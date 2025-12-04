<!-- 数据集检索 -->
<template>
    <div class="app-container">
        <!-- 搜索区域 -->
        <div class="search-container">
            <el-form ref="queryFormRef" :model="queryFormData" :inline="true" label-suffix=":">
                <!-- 数据源选择 -->
                <el-form-item label="数据源" prop="table_id">
                    <el-select v-model="selectedTableId" placeholder="请选择数据源" filterable style="width: 200px"
                        @change="handleTableChange">
                        <el-option v-for="item in tableList" :key="item.id"
                            :label="item.table_comment || item.table_name" :value="item.id" />
                    </el-select>
                </el-form-item>

                <!-- 动态搜索字段 -->
                <template v-if="selectedTableId">
                    <!-- 其他筛选字段 (非LIKE) -->
                    <template v-for="field in visibleQueryFields" :key="field.column_name">
                        <el-form-item :label="field.column_comment || field.column_name" :prop="field.column_name">
                            <!-- 字典选择 -->
                            <el-select v-if="field.dict_type" v-model="queryFormData[field.column_name]"
                                :placeholder="'请选择' + (field.column_comment || field.column_name)" clearable
                                style="width: 200px">
                                <el-option v-for="dict in dictOptionsMap[field.dict_type] || []" :key="dict.value"
                                    :label="dict.dict_label" :value="dict.dict_value" />
                            </el-select>
                            <!-- 日期时间 -->
                            <el-date-picker v-else-if="isDateField(field)" v-model="queryFormData[field.column_name]"
                                type="datetimerange" value-format="YYYY-MM-DD HH:mm:ss" range-separator="至"
                                start-placeholder="开始时间" end-placeholder="结束时间" style="width: 340px" />
                            <!-- 普通输入框 -->
                            <el-input v-else v-model="queryFormData[field.column_name]"
                                :placeholder="'请输入' + (field.column_comment || field.column_name)" clearable
                                style="width: 200px" />
                        </el-form-item>
                    </template>

                    <!-- 查询按钮组 -->
                    <el-form-item>
                        <el-button type="primary" icon="Search" @click="handleQuery">查询</el-button>
                        <el-button icon="Refresh" @click="handleResetQuery">重置</el-button>
                        <!-- 展开/收起 -->
                        <template v-if="queryFields.length > 3">
                            <el-link class="ml-3" type="primary" underline="never" @click="isExpand = !isExpand">
                                {{ isExpand ? "收起" : "展开" }}
                                <el-icon>
                                    <component :is="isExpand ? 'ArrowUp' : 'ArrowDown'" />
                                </el-icon>
                            </el-link>
                        </template>
                    </el-form-item>
                </template>
            </el-form>
        </div>

        <!-- 内容区域 -->
        <el-card class="data-table">
            <template #header>
                <div class="card-header">
                    <span>
                        {{ currentTableName || '数据集' }}列表
                        <el-tooltip content="数据集检索列表">
                            <el-icon class="w-4 h-4 mx-1">
                                <QuestionFilled />
                            </el-icon>
                        </el-tooltip>
                    </span>
                </div>
            </template>

            <!-- 功能区域 -->
            <div class="data-table__toolbar">
                <div class="data-table__toolbar--left">

                </div>
                <div class="data-table__toolbar--right">
                    <el-row :gutter="10">
                        <el-col :span="1.5">
                            <el-tooltip content="导出">
                                <el-button v-hasPerm="['module_dataset:dataset:export']" type="warning" icon="download"
                                    :disabled="!selectedTableId" circle @click="handleOpenExportsModal" />
                            </el-tooltip>
                        </el-col>
                        <el-col :span="1.5">
                            <el-tooltip content="刷新">
                                <el-button type="primary" icon="Refresh" :disabled="!selectedTableId" circle
                                    @click="handleRefresh" />
                            </el-tooltip>
                        </el-col>
                        <el-col :span="1.5">
                            <el-popover placement="bottom" trigger="click">
                                <template #reference>
                                    <el-button type="danger" icon="Operation" :disabled="!selectedTableId" circle />
                                </template>
                                <el-scrollbar max-height="350px">
                                    <template v-for="column in tableFields" :key="column.column_name">
                                        <el-checkbox v-if="column.is_list === true" v-model="column.show"
                                            :label="column.column_comment || column.column_name" />
                                    </template>
                                </el-scrollbar>
                            </el-popover>
                        </el-col>
                    </el-row>
                </div>
            </div>

            <!-- 表格区域 -->
            <el-table v-loading="loading" :data="tableData" border stripe highlight-current-row height="450"
                class="data-table__content" @selection-change="handleSelectionChange">
                <template #empty>
                    <el-empty :image-size="80" description="暂无数据" />
                </template>

                <el-table-column type="selection" width="55" align="center" />
                <el-table-column type="index" label="序号" width="60" align="center">
                    <template #default="scope">
                        {{ (pageParams.page_no - 1) * pageParams.page_size + scope.$index + 1 }}
                    </template>
                </el-table-column>

                <template v-for="field in listFields" :key="field.column_name">
                    <el-table-column :prop="field.column_name" :label="field.column_comment || field.column_name"
                        min-width="150" show-overflow-tooltip>
                        <template #default="{ row }">
                            <template v-if="field.dict_type">
                                <el-tag :type="getDictTagType(field.dict_type, row[field.column_name])">
                                    {{ getDictLabel(field.dict_type, row[field.column_name]) }}
                                </el-tag>
                            </template>
                            <template v-else>
                                {{ row[field.column_name] }}
                            </template>
                        </template>
                    </el-table-column>
                </template>
            </el-table>

            <!-- 分页区域 -->
            <template #footer>
                <pagination v-if="total > 0" v-model:total="total" v-model:page="pageParams.page_no"
                    v-model:limit="pageParams.page_size" @pagination="loadingData" />
            </template>
        </el-card>

        <!-- 导出弹窗 -->
        <ExportModal v-model="exportsDialogVisible" :content-config="curdContentConfig" :query-params="queryFormData"
            :page-data="tableData" :selection-data="selectionRows" />
    </div>
</template>

<script setup lang="ts">
import { useDictStore } from "@/store/index";
const dictStore = useDictStore();

defineOptions({
    name: "Dataset",
    inheritAttrs: false,
});

import { ref, reactive, computed, onMounted } from "vue";
import DatasetAPI from "@/api/module_dataset/dataset";
import { QuestionFilled } from "@element-plus/icons-vue";
import ExportModal from "@/components/CURD/ExportModal.vue";
import type { IContentConfig } from "@/components/CURD/types";

// 状态变量
const loading = ref(false);
const isExpand = ref(false);
const selectedTableId = ref<number | undefined>(undefined);
const currentTableName = ref("");
const tableList = ref<any[]>([]);
const tableFields = ref<any[]>([]);
const tableData = ref<any[]>([]);
const total = ref(0);
const dictOptionsMap = ref<Record<string, any[]>>({});
const exportsDialogVisible = ref(false);
const selectionRows = ref<any[]>([]);

// 查询参数
const queryFormRef = ref();
const queryFormData = ref<Record<string, any>>({});
const pageParams = reactive({
    page_no: 1,
    page_size: 10,
});

// 计算属性：所有可查询字段
const queryFields = computed(() => {
    return tableFields.value.filter(f => (f.is_query === true || f.is_query === '1'));
});

// 计算属性：可见的查询字段（根据展开状态）
const visibleQueryFields = computed(() => {
    if (isExpand.value) {
        return queryFields.value;
    }
    return queryFields.value.slice(0, 3);
});

// 计算属性：列表显示字段
const listFields = computed(() => {
    return tableFields.value.filter(f => (f.is_list === true));
});

// 导出配置
const curdContentConfig = computed(() => ({
    permPrefix: "module_dataset:dataset",
    cols: tableFields.value
        .filter((f) => f.is_list === true)
        .map((f) => ({
            prop: f.column_name,
            label: f.column_comment || f.column_name,
        })) as any,
    exportsAction: async (params: any) => {
        if (!selectedTableId.value) return [];
        const query = { ...params };
        query.page_no = 1;
        query.page_size = -1;
        const res = await DatasetAPI.getDatasetTableData(selectedTableId.value, query);
        return res.data.data.items || [];
    },
}));

// 初始化
onMounted(async () => {
    getTableList();
});

// 获取数据源列表
async function getTableList() {
    try {
        const res = await DatasetAPI.getDatasetTableList();
        tableList.value = res.data.data || [];
    } catch (error) {
        console.error(error);
    }
}

// 切换数据源
async function handleTableChange(val: number) {
    if (!val) return;

    const table = tableList.value.find(t => t.id === val);
    currentTableName.value = table ? (table.table_comment || table.table_name) : "";

    loading.value = true;
    try {
        // 获取表结构
        const res = await DatasetAPI.getDatasetTableDetail(val);
        const fields = res.data.data || [];

        // 初始化字段显示状态
        fields.forEach((f: any) => {
            f.show = true;
        });
        tableFields.value = fields;

        // 加载字典
        await loadDictOptions(fields);

        // 重置查询表单
        handleResetQuery();
    } catch (error) {
        console.error(error);
    } finally {
        loading.value = false;
    }
}

// 加载字典数据
async function loadDictOptions(fields: any[]) {
    const dictTypes = new Set<string>();
    fields.forEach(f => {
        if (f.dict_type) dictTypes.add(f.dict_type);
    });

    const types = Array.from(dictTypes);
    if (types.length > 0) {
        await dictStore.getDict(types);
    }

    for (const type of types) {
        if (!dictOptionsMap.value[type]) {
            console.log("加载字典：", type);
            console.log(dictStore.getDictArray(type));
            console.log(dictStore.getDictArray('sys_notice_type'));
            dictOptionsMap.value[type] = dictStore.getDictArray(type) || [];
        }
    }
}

// 加载数据
async function loadingData() {
    if (!selectedTableId.value) return;

    loading.value = true;
    try {
        const params = {
            ...pageParams,
            ...queryFormData.value
        };

        const res = await DatasetAPI.getDatasetTableData(selectedTableId.value, params);
        tableData.value = res.data.data.items || [];
        total.value = res.data.data.total || 0;
    } catch (error) {
        console.error(error);
    } finally {
        loading.value = false;
    }
}

// 查询
function handleQuery() {
    pageParams.page_no = 1;
    loadingData();
}

// 重置
function handleResetQuery() {
    if (queryFormRef.value) {
        queryFormRef.value.resetFields();
    }
    queryFormData.value = {};
    pageParams.page_no = 1;
    loadingData();
}

// 刷新
function handleRefresh() {
    loadingData();
}

// 选中项发生变化
function handleSelectionChange(selection: any[]) {
    selectionRows.value = selection;
}

// 打开导出弹窗
function handleOpenExportsModal() {
    if (!selectedTableId.value) return;
    exportsDialogVisible.value = true;
}

// 辅助函数：判断是否为日期字段
function isDateField(field: any) {
    const type = (field.column_name || "").toLowerCase();
    return type.includes("date") || type.includes("time");
}

// 辅助函数：获取字典标签
function getDictLabel(dictType: string, value: any) {
    const options = dictOptionsMap.value[dictType] || [];
    const option = options.find(opt => opt.dict_value == value.toString()); // 使用 == 兼容字符串和数字
    return option ? option.dict_label : value;
}

// 辅助函数：获取字典Tag类型
function getDictTagType(dictType: string, value: any) {
    const options = dictOptionsMap.value[dictType] || [];
    const option = options.find(opt => opt.dict_value == value.toString());
    // 假设字典数据中有 el_tag_type 或 listClass 属性，如果没有则默认
    return option?.list_class || 'primary';
}
</script>

<style lang="scss" scoped>
.search-container {
    padding: 18px 18px 0;
    margin-bottom: 10px;
    background-color: var(--el-bg-color);
    border-radius: 4px;
    box-shadow: var(--el-box-shadow-light);
}
</style>
