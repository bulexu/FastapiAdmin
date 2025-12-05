<template>
    <div>
        <el-form ref="promptRef" :model="form" :rules="rules" label-width="120px">
            <div class="mb20" style="padding-left: 120px;">
                <el-button @click="loadExample" :icon="Refresh" v-if="!isEditMode">载入示例</el-button>
                <el-button :icon="MagicStick" type="warning" @click="handleDesignByDialog" :loading="testLoading"
                    class="ml5">设计
                </el-button>
                <el-button type="warning" @click="handlePromptTest" :disabled="!form.content" :loading="testLoading"
                    class="ml5">调试
                </el-button>
            </div>

            <el-form-item prop="prompt_title">
                <template #label>
                    <el-text>
                        <span>
                            <el-tooltip content="智能体的核心定义，指导生成提示词" placement="top">
                                <el-icon>
                                    <QuestionFilled />
                                </el-icon>
                            </el-tooltip>
                            标题
                        </span>
                    </el-text>
                </template>
                <el-input v-model="form.prompt_title" placeholder="请输入提示词标题"></el-input>
            </el-form-item>

            <el-form-item prop="prompt_code">
                <template #label>
                    <el-text>
                        <span>
                            <el-tooltip content="唯一编码" placement="top">
                                <el-icon>
                                    <QuestionFilled />
                                </el-icon>
                            </el-tooltip>
                            编码
                        </span>
                    </el-text>
                </template>
                <el-input v-model="form.prompt_code" placeholder="请输入提示词编码"></el-input>
            </el-form-item>

            <el-form-item prop="ability_tags">
                <template #label>
                    <el-text>
                        <span>
                            <el-tooltip content="智能体拥有的核心能力" placement="top">
                                <el-icon>
                                    <QuestionFilled />
                                </el-icon>
                            </el-tooltip>能力标签
                        </span>
                    </el-text>
                </template>
                <div>
                    <div>
                        <el-tag v-for="(tag, idx) in form.ability_tags" :key="idx" closable
                            @close="removeAbilityTag(idx)" class="mb5 ml1">{{ tag }}
                        </el-tag>
                    </div>
                    <div>
                        <el-input v-model="abilityTagInput" placeholder="添加能力标签 (最多10个)" class="w-400"
                            @keyup.enter="addAbilityTag" :disabled="form.ability_tags.length >= tagLimit">
                            <template #append>
                                <el-button @click="addAbilityTag"
                                    :disabled="!abilityTagInput || form.ability_tags.length >= tagLimit">添加
                                </el-button>
                            </template>
                        </el-input>
                    </div>
                </div>
            </el-form-item>

            <el-form-item label="内容" prop="content">
                <WangEditor v-model="form.content" ref="editorRef" height="400px" />
            </el-form-item>

            <el-form-item label="备注" prop="description">
                <el-input type="textarea" v-model="form.description" placeholder="请输入备注" :rows="2" />
            </el-form-item>

            <!-- 底部操作按钮 -->
            <div class="mt20" style="display: flex; justify-content: flex-end;">
                <el-button type="primary" @click="submitForm">保存</el-button>
            </div>
        </el-form>

        <!-- 调试抽屉 -->
        <el-drawer title="提示词调试" v-model="testDialogVisible" direction="rtl" size="60%" :close-on-click-modal="false">
            <div class="debug-container">
                <iframe :src="debugIframeUrl"
                    style="width: 100%; height: 100%; min-height: 700px; border: none; display: block; overflow: hidden;"
                    frameborder="0" scrolling="no" allow="microphone">
                </iframe>
            </div>
        </el-drawer>

        <!-- 对话设计抽屉 -->
        <el-drawer v-model="chatbotDrawerVisible" title="对话设计助手" direction="rtl" size="60%"
            :close-on-click-modal="false">
            <div class="chatbot-container">
                <iframe :src="designerIframeUrl"
                    style="width: 100%; height: 100%; border: none; display: block; overflow: hidden;" frameborder="0"
                    scrolling="no" allow="microphone">
                </iframe>
            </div>
        </el-drawer>
    </div>
</template>

<script setup lang="ts">
import { ref, computed, getCurrentInstance } from "vue";
import { Refresh, QuestionFilled, MagicStick } from '@element-plus/icons-vue';
import WangEditor from '@/components/WangEditor/index.vue';
import { parseParams } from '@/utils/common';
const props = defineProps({
    modelValue: {
        type: Object,
        required: true
    },
    isEditMode: {
        type: Boolean,
        default: false
    }
});

const emit = defineEmits(['update:modelValue', 'submit']);

const { proxy } = getCurrentInstance() as any;
const form = computed({
    get: () => props.modelValue,
    set: (val) => emit('update:modelValue', val)
});

const rules = {
    prompt_code: [{ required: true, message: "提示词编码不能为空", trigger: "blur" }],
    prompt_title: [{ required: true, message: "提示词标题不能为空", trigger: "blur" }],
    content: [{ required: true, message: "内容不能为空", trigger: "blur" }],
};

const editorRef = ref();
const tagLimit = 10;
const abilityTagInput = ref("");

// 调试 & 设计
const testDialogVisible = ref(false);
const testLoading = ref(false);
const chatbotDrawerVisible = ref(false);

// Dify API
const difyApiUrl = import.meta.env.VITE_APP_DIFY_API_URL;
const difyPromptDesignerToken = import.meta.env.VITE_APP_DIFY_PROMPT_DESIGNER_TOKEN;
const difyPromptDebugToken = import.meta.env.VITE_APP_DIFY_PROMPT_DEBUG_TOKEN;

// 标签操作
function addAbilityTag() {
    if (abilityTagInput.value && form.value.ability_tags.length < tagLimit) {
        form.value.ability_tags.push(abilityTagInput.value);
        abilityTagInput.value = "";
    }
}

function removeAbilityTag(idx: number) {
    form.value.ability_tags.splice(idx, 1);
}

// 载入示例
function loadExample() {
    const examples = [
        {
            prompt_code: "market_analysis_assistant" + Date.now(),
            prompt_title: "市场分析助手",
            ability_tags: ["数据分析", "趋势预测", "竞品调研", "报告生成", "Excel"],
        },
        {
            prompt_code: "product_manager_assistant" + Date.now(),
            prompt_title: "产品经理助手",
            ability_tags: ["需求分析", "PRD撰写", "用户故事", "敏捷开发", "竞品分析"],
        },
        {
            prompt_code: "ui_design_assistant" + Date.now(),
            prompt_title: "UI设计助手",
            ability_tags: ["Figma", "配色方案", "界面规范", "交互设计", "图标设计"],
        },
        {
            prompt_code: "frontend_dev_assistant" + Date.now(),
            prompt_title: "前端开发助手",
            ability_tags: ["Vue3", "TypeScript", "Vite", "组件化", "性能优化"],
        },
        {
            prompt_code: "backend_dev_assistant" + Date.now(),
            prompt_title: "后端开发助手",
            ability_tags: ["Python", "FastAPI", "PostgreSQL", "Redis", "Docker"],
        },
        {
            prompt_code: "hr_management_assistant" + Date.now(),
            prompt_title: "人事管理助手",
            ability_tags: ["招聘", "绩效考核", "员工关系", "薪酬管理", "培训发展"],
        },
        {
            prompt_code: "copywriting_assistant" + Date.now(),
            prompt_title: "文案写作助手",
            ability_tags: ["短视频脚本", "广告文案", "品牌故事", "SEO优化", "创意写作"],
        },
        {
            prompt_code: "operation_assistant" + Date.now(),
            prompt_title: "运营助手",
            ability_tags: ["活动策划", "用户增长", "数据分析", "内容运营", "社群管理"],
        }
    ];
    const pick = examples[Math.floor(Math.random() * examples.length)];
    Object.assign(form.value, {
        prompt_code: pick.prompt_code,
        prompt_title: pick.prompt_title,
        ability_tags: [...pick.ability_tags],
        description: ''
    });
    abilityTagInput.value = "";
}

// 调试
function handlePromptTest() {
    testDialogVisible.value = true;
}

const debugIframeUrl = computed(() => {
    const inputs = {
        title: form.value.prompt_title,
        prompt: form.value.content,
        "sys.user_id": `debug-${Date.now()}`
    };
    const baseUrl = `${difyApiUrl}/chatbot/${difyPromptDebugToken}`;
    return `${baseUrl}?${parseParams(inputs)}`;
});

// 设计
function handleDesignByDialog() {
    chatbotDrawerVisible.value = true;
}

const designerIframeUrl = computed(() => {
    const inputs = {
        "sys.user_id": `debug-${Date.now()}`
    };
    const baseUrl = `${difyApiUrl}/chatbot/${difyPromptDesignerToken}`;
    return `${baseUrl}?${parseParams(inputs)}`;
});

// 提交
function submitForm() {
    proxy.$refs.promptRef.validate((valid: boolean) => {
        if (valid) {
            emit('submit');
        }
    });
}
</script>

<style scoped>
.w-200 {
    width: 200px;
}

.w-400 {
    width: 400px;
}

.mb5 {
    margin-bottom: 5px;
}

.mb20 {
    margin-bottom: 20px;
}

.mt20 {
    margin-top: 20px;
}

.ml1 {
    margin-left: 10px;
}

.ml5 {
    margin-left: 5px;
}

.model-selector {
    display: flex;
    align-items: center;
}

.action-buttons {
    display: flex;
    align-items: center;
}

.flex-between {
    display: flex;
    justify-content: space-between;
    align-items: center;
}

/* 对话设计抽屉样式 */
.chatbot-container {
    height: calc(100vh - 120px);
    overflow: hidden;
    padding: 0;
    margin: 0;
}

.chatbot-container iframe {
    border-radius: 8px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    overflow: hidden;
}

/* 调试弹窗样式 */
.debug-container {
    height: 700px;
    overflow: hidden;
    padding: 0;
    margin: 0;
}

.debug-container iframe {
    border-radius: 8px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    overflow: hidden;
}
</style>
