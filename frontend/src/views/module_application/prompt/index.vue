<!-- 提示词管理 -->
<template>
    <div class="app-container">
        <!-- 搜索区域 -->
        <div v-show="visible" class="search-container">
            <el-form ref="queryFormRef" :model="queryFormData" label-suffix=":" :inline="true"
                @submit.prevent="handleQuery">
                <el-form-item prop="prompt_title" label="标题">
                    <el-input v-model="queryFormData.prompt_title" placeholder="请输入标题" clearable />
                </el-form-item>
                <el-form-item prop="prompt_code" label="编码">
                    <el-input v-model="queryFormData.prompt_code" placeholder="请输入编码" clearable />
                </el-form-item>
                <el-form-item prop="is_publish" label="发布状态">
                    <el-select v-model="queryFormData.is_publish" placeholder="请选择状态" style="width: 170px" clearable>
                        <el-option :value="1" label="已发布" />
                        <el-option :value="0" label="未发布" />
                    </el-select>
                </el-form-item>

                <!-- 查询、重置按钮 -->
                <el-form-item>
                    <el-button v-hasPerm="['module_application:prompt:query']" type="primary" icon="search"
                        @click="handleQuery">
                        查询
                    </el-button>
                    <el-button v-hasPerm="['module_application:prompt:query']" icon="refresh" @click="handleResetQuery">
                        重置
                    </el-button>
                </el-form-item>
            </el-form>
        </div>

        <!-- 内容区域 -->
        <el-card class="data-table">
            <template #header>
                <div class="card-header">
                    <span>
                        提示词列表
                        <el-tooltip content="提示词列表">
                            <QuestionFilled class="w-4 h-4 mx-1" />
                        </el-tooltip>
                    </span>
                </div>
            </template>

            <!-- 功能区域 -->
            <div class="data-table__toolbar">
                <div class="data-table__toolbar--left">
                    <el-row :gutter="10">
                        <el-col :span="1.5">
                            <el-button v-hasPerm="['module_application:prompt:create']" type="success" icon="plus"
                                @click="handleAdd">
                                新增
                            </el-button>
                        </el-col>
                        <el-col :span="1.5">
                            <el-button v-hasPerm="['module_application:prompt:delete']" type="danger" icon="delete"
                                :disabled="selectIds.length === 0" @click="handleDelete(selectIds)">
                                批量删除
                            </el-button>
                        </el-col>
                        <el-col :span="1.5">
                            <el-tooltip class="item" content="如何使用提示词" placement="top">
                                <el-button circle icon="Warning" @click="showLangfuseTip = true" />
                            </el-tooltip>
                        </el-col>
                    </el-row>
                </div>
                <div class="data-table__toolbar--right">
                    <el-row :gutter="10">
                        <el-col :span="1.5">
                            <el-tooltip content="搜索显示/隐藏">
                                <el-button v-hasPerm="['*:*:*']" type="info" icon="search" circle
                                    @click="visible = !visible" />
                            </el-tooltip>
                        </el-col>
                        <el-col :span="1.5">
                            <el-tooltip content="刷新">
                                <el-button v-hasPerm="['module_application:prompt:query']" type="primary" icon="refresh"
                                    circle @click="handleRefresh" />
                            </el-tooltip>
                        </el-col>
                        <el-col :span="1.5">
                            <el-popover placement="bottom" trigger="click">
                                <template #reference>
                                    <el-button type="danger" icon="operation" circle></el-button>
                                </template>
                                <el-scrollbar max-height="350px">
                                    <template v-for="column in tableColumns" :key="column.prop">
                                        <el-checkbox v-if="column.prop" v-model="column.show" :label="column.label" />
                                    </template>
                                </el-scrollbar>
                            </el-popover>
                        </el-col>
                    </el-row>
                </div>
            </div>

            <!-- 表格区域 -->
            <el-table ref="tableRef" v-loading="loading" :data="pageTableData" highlight-current-row
                class="data-table__content" :height="450" border stripe @selection-change="handleSelectionChange">
                <template #empty>
                    <el-empty :image-size="80" description="暂无数据" />
                </template>
                <el-table-column v-if="tableColumns.find((col) => col.prop === 'selection')?.show" type="selection"
                    min-width="55" align="center" />
                <el-table-column v-if="tableColumns.find((col) => col.prop === 'index')?.show" fixed label="序号"
                    min-width="60">
                    <template #default="scope">
                        {{ (queryFormData.page_no - 1) * queryFormData.page_size + scope.$index + 1 }}
                    </template>
                </el-table-column>
                <el-table-column v-if="tableColumns.find((col) => col.prop === 'prompt_code')?.show" label="编码"
                    prop="prompt_code" min-width="140" />
                <el-table-column v-if="tableColumns.find((col) => col.prop === 'prompt_title')?.show" label="标题"
                    prop="prompt_title" min-width="140" />
                <el-table-column v-if="tableColumns.find((col) => col.prop === 'version_id')?.show" label="当前版本"
                    prop="version_id" min-width="100" align="center">
                    <template #default="scope">
                        <el-tag type="info">V{{ scope.row.version_id }}</el-tag>
                    </template>
                </el-table-column>
                <el-table-column v-if="tableColumns.find((col) => col.prop === 'ability_tags')?.show" label="能力标签"
                    prop="ability_tags" min-width="200">
                    <template #default="scope">
                        <el-tag v-for="(tag, idx) in scope.row.ability_tags" :key="idx" style="margin:2px;">{{ tag
                            }}</el-tag>
                    </template>
                </el-table-column>
                <el-table-column v-if="tableColumns.find((col) => col.prop === 'is_publish')?.show" label="发布状态"
                    prop="is_publish" min-width="100" align="center">
                    <template #default="scope">
                        <el-tag :type="scope.row.is_publish === 1 ? 'success' : 'info'">
                            {{ scope.row.is_publish === 1 ? "已发布" : "未发布" }}
                        </el-tag>
                    </template>
                </el-table-column>
                <el-table-column v-if="tableColumns.find((col) => col.prop === 'updated_time')?.show" label="更新时间"
                    prop="updated_time" min-width="180" />
                <el-table-column v-if="tableColumns.find((col) => col.prop === 'operation')?.show" fixed="right"
                    label="操作" align="center" min-width="250">
                    <template #default="scope">
                        <el-tooltip content="编辑" placement="top">
                            <el-button v-hasPerm="['module_application:prompt:update']" type="primary" size="small" link
                                icon="edit" @click="handleUpdate(scope.row.id)" />
                        </el-tooltip>
                        <el-tooltip content="复制" placement="top">
                            <el-button v-hasPerm="['module_application:prompt:create']" type="primary" size="small" link
                                icon="CopyDocument" @click="handleCopy(scope.row)" />
                        </el-tooltip>
                        <el-tooltip content="推送" placement="top">
                            <el-button v-hasPerm="['module_application:prompt:push']"
                                :type="scope.row.is_publish === 1 ? 'success' : 'info'" size="small" link icon="Flag"
                                @click="handlePublish(scope.row)" />
                        </el-tooltip>
                        <el-tooltip content="删除" placement="top">
                            <el-button v-hasPerm="['module_application:prompt:delete']" type="danger" size="small" link
                                icon="delete" @click="handleDelete([scope.row.id])" />
                        </el-tooltip>
                    </template>
                </el-table-column>
            </el-table>

            <!-- 分页区域 -->
            <template #footer>
                <pagination v-model:total="total" v-model:page="queryFormData.page_no"
                    v-model:limit="queryFormData.page_size" @pagination="loadingData" />
            </template>
        </el-card>

        <!-- 如何使用弹窗 -->
        <LangfuseTipDrawer v-model="showLangfuseTip" />
    </div>
</template>

<script setup lang="ts">
defineOptions({
    name: "Prompt",
    inheritAttrs: false,
});

import { ref, reactive, onMounted, getCurrentInstance } from "vue";
import { useRouter } from "vue-router";
import { ElMessage, ElMessageBox } from "element-plus";
import PromptAPI, { PromptTable, PromptForm, PromptPageQuery } from "@/api/module_application/prompt";
import { QuestionFilled } from "@element-plus/icons-vue";
import LangfuseTipDrawer from '@/components/Langfuse/tip.vue';

const { proxy } = getCurrentInstance() as any;
const router = useRouter();

const visible = ref(true);
const queryFormRef = ref();
const total = ref(0);
const selectIds = ref<number[]>([]);
const loading = ref(false);
const showLangfuseTip = ref(false);

// 分页表单
const pageTableData = ref<PromptTable[]>([]);

// 表格列配置
const tableColumns = ref([
    { prop: "selection", label: "选择框", show: true },
    { prop: "index", label: "序号", show: true },
    { prop: "prompt_code", label: "编码", show: true },
    { prop: "prompt_title", label: "标题", show: true },
    { prop: "version_id", label: "当前版本", show: true },
    { prop: "ability_tags", label: "能力标签", show: true },
    { prop: "is_publish", label: "发布状态", show: true },
    { prop: "updated_time", label: "更新时间", show: true },
    { prop: "operation", label: "操作", show: true },
]);

// 分页查询参数
const queryFormData = reactive<PromptPageQuery>({
    page_no: 1,
    page_size: 10,
    prompt_title: undefined,
    prompt_code: undefined,
    is_publish: undefined,
});

// 编辑表单
const formData = reactive<PromptForm>({
    id: undefined,
    prompt_code: "",
    prompt_title: "",
    content: "",
    ability_tags: [],
    description: "",
});

// 弹窗状态
const dialogVisible = reactive({
    title: "",
    visible: false,
    type: "create" as "create" | "update" | "detail",
});


// 列表刷新
async function handleRefresh() {
    await loadingData();
}

// 加载表格数据
async function loadingData() {
    loading.value = true;
    try {
        const response = await PromptAPI.getPage(queryFormData);
        pageTableData.value = response.data.data.items;
        total.value = response.data.data.total;
    } catch (error: any) {
        console.error(error);
    } finally {
        loading.value = false;
    }
}

// 查询
async function handleQuery() {
    queryFormData.page_no = 1;
    loadingData();
}

// 重置查询
async function handleResetQuery() {
    queryFormRef.value.resetFields();
    queryFormData.page_no = 1;
    loadingData();
}

// 行复选框选中项变化
async function handleSelectionChange(selection: any) {
    selectIds.value = selection.map((item: any) => item.id);
}

/** 新增按钮操作 */
function handleAdd() {
    router.push('/application/prompt/design');
}

/** 修改按钮操作 */
function handleUpdate(promptId: number) {
    router.push({ path: '/application/prompt/design', query: { id: promptId } });
}

// 删除
async function handleDelete(ids: number[]) {
    ElMessageBox.confirm("确认删除该项数据?", "警告", {
        confirmButtonText: "确定",
        cancelButtonText: "取消",
        type: "warning",
    })
        .then(async () => {
            try {
                loading.value = true;
                await PromptAPI.delete(ids);
                handleResetQuery();
            } catch (error: any) {
                console.error(error);
            } finally {
                loading.value = false;
            }
        })
        .catch(() => {
            ElMessageBox.close();
        });
}

// 复制
async function handleCopy(row: PromptTable) {
    ElMessageBox.confirm(`确认复制提示词 "${row.prompt_title}"?`, "提示", {
        confirmButtonText: "确定",
        cancelButtonText: "取消",
        type: "info",
    }).then(async () => {
        // 获取详情
        const response = await PromptAPI.getDetail(row.id!);
        const data = response.data.data;

        // 填充表单，清除ID和Code
        Object.assign(formData, data);
        formData.id = undefined;
        formData.prompt_code = `${data.prompt_code}_copy_${new Date().getTime()}`; // 自动生成唯一Code
        formData.prompt_title = `${data.prompt_title} (副本)`;

        dialogVisible.type = "create";
        dialogVisible.title = "复制提示词";
        dialogVisible.visible = true;
    });
}

// 推送
async function handlePublish(row: PromptTable) {
    ElMessageBox.confirm(`确认推送提示词 "${row.prompt_title}" 到生产环境?`, "提示", {
        confirmButtonText: "确定",
        cancelButtonText: "取消",
        type: "warning",
    }).then(async () => {
        try {
            loading.value = true;
            await PromptAPI.pushToProduction(row.id!);
            ElMessage.success("推送成功");
            handleRefresh();
        } catch (error: any) {
            console.error(error);
        } finally {
            loading.value = false;
        }
    });
}

onMounted(() => {
    loadingData();
});
</script>

<style lang="scss" scoped></style>
