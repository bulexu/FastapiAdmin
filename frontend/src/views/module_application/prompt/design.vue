<template>
    <div class="app-container">
        <el-row :gutter="20">
            <el-col :span="16">
                <!-- 左侧：提示词设计区域 -->
                <PromptForm v-model="form" :is-edit-mode="isEditMode" @submit="submitForm" />
            </el-col>

            <el-col :span="8">
                <!-- 右侧：评估结果区域 -->
                <PromptEvaluator v-model="form.evaluate_result" v-model:content="form.content" />
            </el-col>
        </el-row>

        <!-- 底部历史版本时间轴 -->
        <PromptVersions ref="versionsRef" :prompt-id="form.prompt_id" :visible="isEditMode"
            @show-detail="showVersionDetail" @rollback="rollbackToVersion" />

        <!-- 版本详情弹窗 -->
        <PromptVersionDetail v-model="versionDetailDialog" :detail="currentVersionDetail"
            @rollback="rollbackToVersion" />

    </div>
</template>
<script setup name="PromptDesign">
import { ref, reactive, toRefs, onMounted, computed } from "vue";
import { useRoute, useRouter } from 'vue-router';
import PromptAPI from '@/api/module_application/prompt';
import PromptForm from './components/PromptForm.vue';
import PromptEvaluator from './components/PromptEvaluator.vue';
import PromptVersions from './components/PromptVersions.vue';
import PromptVersionDetail from './components/PromptVersionDetail.vue';

const route = useRoute();
const router = useRouter();

const versionsRef = ref();
const versionDetailDialog = ref(false);
const currentVersionDetail = ref({
    content: '',
    ability_tags: [],
    version: '',
    is_archived: false
});

const data = reactive({
    form: {
        prompt_id: undefined,
        prompt_code: '',
        prompt_title: '',
        content: '',
        ability_tags: [],
        description: '',
        evaluate_result: {},
        model: 'qwen-plus',
        optimize_model: 'qwen-plus'
    }
});

const { form } = toRefs(data);

// 判断是否为编辑模式
const isEditMode = computed(() => form.value.prompt_id != null && form.value.prompt_id !== '');

// 显示版本详情
function showVersionDetail(version) {
    currentVersionDetail.value = version;
    versionDetailDialog.value = true;
}

// 仅加载指定版本的内容到编辑器
function rollbackToVersion(version) {
    if (!version || !version.content) return;
    form.value.content = version.content;
    form.value.ability_tags = [...(version.ability_tags || [])];
    form.value.description = version.description || '';
    form.value.evaluate_result = {};
    versionDetailDialog.value = false;
    ElMessage.success('已加载到当前编辑器，保存后生效');
}

// 初始化表单数据
async function initFormData() {
    const promptId = route.query.id;
    form.value.prompt_id = promptId;
    if (isEditMode.value && promptId) {
        try {
            // 用获取提示词详情的API
            const res = await PromptAPI.getDetail(promptId);
            Object.assign(form.value, res.data.data);
        } catch (e) {
            ElMessage.error('获取提示词详情失败');
        }
    }
}

// 提交表单
async function submitForm() {
    try {
        const payload = {
            ...form.value
        };

        let res;
        if (isEditMode.value) {
            res = await PromptAPI.update(form.value.prompt_id, payload);
        } else {
            res = await PromptAPI.create(payload);
        }

        if (res.data && res.data.data && res.data.data.id) {
            form.value.prompt_id = res.data.data.id;
            router.replace({ query: { ...route.query, id: res.data.data.id } });
        }

        if (isEditMode.value) {
            if (versionsRef.value) {
                versionsRef.value.loadVersionList(); // 刷新版本列表
            }
        }
    } catch (e) {
        ElMessage.error("保存失败");
    }
}// 页面初始化
onMounted(() => {
    initFormData();
});
</script>

<style scoped>
/* 扩展 ruoyi.scss 中的通用间距样式 */
.p20 {
    padding: 20px;
}
</style>
