<template>
    <div class="evaluation-sidebar">
        <div class="flex-between mb10">
            <h3 style="margin: 0;">评估结果</h3>
            <el-button type="primary" size="small" @click="handleEvaluatePrompt" :loading="evaluating"
                :disabled="!content">
                {{ evaluating ? '评估中...' : '开始评估' }}
            </el-button>
        </div>

        <div v-if="!hasEvaluated && !evaluating" class="text-center text-muted mt100">
            <el-empty description="请先输入提示词内容，然后点击评估按钮" />
        </div>

        <div v-if="evaluating || hasEvaluated" v-loading="evaluating">
            <!-- 评分结果 -->
            <el-card shadow="never" class="mb10">
                <template #header>
                    <div class="card-header">
                        <span>评分结果(仅供参考)</span>
                    </div>
                </template>
                <el-row :gutter="20">
                    <!-- 综合评分 -->
                    <el-col :span="10">
                        <div class="overall-score-section">
                            <div class="section-title">综合评分</div>
                            <div class="text-center mt10">
                                <el-progress type="circle" :percentage="evaluateResult.overall_score || 0"
                                    :color="getScoreColor(evaluateResult.overall_score || 0)" :width="80" />
                                <div class="mt5 font-16 font-bold">
                                    {{ evaluateResult.overall_score || 0 }}/100
                                </div>
                            </div>
                        </div>
                    </el-col>

                    <!-- 维度评分 -->
                    <el-col :span="14">
                        <div class="dimension-score-section">
                            <div class="section-title">维度评分</div>
                            <div class="mt10">
                                <div v-for="(score, dimension) in evaluateResult.dimension_scores" :key="dimension"
                                    class="dimension-row">
                                    <el-tooltip :content="getDimensionDescription(dimension)" placement="left">
                                        <span class="dimension-name">{{ dimension }}</span>
                                    </el-tooltip>
                                    <div class="progress-container">
                                        <el-progress :percentage="score * 10" :show-text="false"
                                            :color="getScoreColor(score * 10)" :stroke-width="8" />
                                    </div>
                                    <span class="dimension-score">{{ score }}/10</span>
                                </div>
                            </div>
                        </div>
                    </el-col>
                </el-row>
            </el-card>

            <!-- 优点、不足、改进建议 -->
            <el-tabs v-model="activeTab" type="border-card">
                <el-tab-pane label="优点" name="strengths">
                    <ul class="evaluation-list">
                        <li v-for="(strength, idx) in evaluateResult.strengths" :key="idx" class="mb5">
                            {{ strength }}
                        </li>
                    </ul>
                </el-tab-pane>
                <el-tab-pane label="不足" name="weaknesses">
                    <ul class="evaluation-list">
                        <li v-for="(weakness, idx) in evaluateResult.weaknesses" :key="idx" class="mb5">
                            {{ weakness }}
                        </li>
                    </ul>
                </el-tab-pane>
                <el-tab-pane label="改进建议" name="suggestions">
                    <div v-if="evaluateResult.improvement_suggestions?.length">
                        <!-- 建议列表区域 -->
                        <div class="suggestions-container">
                            <el-checkbox-group v-model="selectedSuggestions">
                                <div v-for="(suggestion, idx) in evaluateResult.improvement_suggestions" :key="idx"
                                    class="suggestion-item">
                                    <el-checkbox :label="suggestion" class="suggestion-checkbox">
                                        <span class="suggestion-text">{{ suggestion }}</span>
                                    </el-checkbox>
                                </div>
                            </el-checkbox-group>
                        </div>

                        <!-- 操作区域 -->
                        <div class="suggestions-actions">
                            <div class="model-select-row">
                                <span class="model-label">优化模型：</span>
                                <el-select v-model="optimizeModel" placeholder="选择优化模型" class="model-select"
                                    size="small">
                                    <el-option label="Qwen-Turbo (快速)" value="qwen-turbo" />
                                    <el-option label="Qwen-Plus (均衡)" value="qwen-plus" />
                                    <el-option label="Qwen-Max (高质量)" value="qwen-max" />
                                </el-select>
                            </div>
                            <div class="button-row">
                                <el-button size="small" @click="selectAllSuggestions" class="action-btn secondary-btn">
                                    {{
                                        selectedSuggestions.length ===
                                            evaluateResult.improvement_suggestions.length
                                            ? '取消全选' : '全选'
                                    }}
                                </el-button>
                                <el-button type="primary" size="small" @click="optimizePrompt" :loading="optimizing"
                                    class="action-btn primary-btn"
                                    :disabled="!selectedSuggestions.length || !optimizeModel">
                                    {{ optimizing ? '优化中...' : '应用选中建议' }}
                                </el-button>
                            </div>
                        </div>
                    </div>
                    <div v-else class="empty-suggestions">
                        暂无改进建议
                    </div>
                </el-tab-pane>
            </el-tabs>
        </div>
    </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from "vue";
import PromptAPI from '@/api/module_application/prompt';

const props = defineProps({
    modelValue: {
        type: Object,
        required: true
    },
    content: {
        type: String,
        default: ''
    }
});

const emit = defineEmits(['update:modelValue', 'update:content']);

const evaluateResult = computed({
    get: () => props.modelValue,
    set: (val) => emit('update:modelValue', val)
});

const evaluating = ref(false);
const hasEvaluated = ref(false);
const activeTab = ref('strengths');
const optimizing = ref(false);
const selectedSuggestions = ref<string[]>([]);
const optimizeModel = ref('qwen-plus');

watch(() => props.modelValue, (val) => {
    if (val && val.overall_score !== undefined) {
        hasEvaluated.value = true;
    }
}, { immediate: true, deep: true });

// 评估提示词
async function handleEvaluatePrompt() {
    const editorText = props.content;
    if (!editorText || !/[a-zA-Z\u4e00-\u9fa5]/.test(editorText)) {
        ElMessage.warning('请先输入包含正文的提示词内容');
        return;
    }

    evaluating.value = true;
    resetEvaluateResult();

    try {
        const res = await PromptAPI.evaluatePrompt({ prompt: editorText });
        if (res.data) {
            evaluateResult.value = res.data.data;
            hasEvaluated.value = true;
        }
    } catch (e) {
        ElMessage.error('评估失败');
    }
    evaluating.value = false;
}

function resetEvaluateResult() {
    hasEvaluated.value = false;
    evaluateResult.value = {
        overall_score: 0,
        dimension_scores: {},
        strengths: [],
        weaknesses: [],
        improvement_suggestions: []
    };
    selectedSuggestions.value = [];
}

// 全选/取消全选改进建议
function selectAllSuggestions() {
    if (selectedSuggestions.value.length === evaluateResult.value.improvement_suggestions.length) {
        selectedSuggestions.value = [];
    } else {
        selectedSuggestions.value = [...evaluateResult.value.improvement_suggestions];
    }
}

// 应用选中的改进建议优化提示词
async function optimizePrompt() {
    if (!selectedSuggestions.value.length) {
        ElMessage.warning('请选择要应用的改进建议');
        return;
    }

    let content = props.content;
    if (!content) {
        ElMessage.warning('请先输入提示词内容');
        return;
    }

    content = content.trim().replace(/[\r\n]/g, '');
    if (content.length > 50000 || content.length < 20) {
        ElMessage.warning('提示词内容长度应在20-50000字符之间');
        return;
    }

    optimizing.value = true;
    let optimizedContent = '';

    try {
        PromptAPI.optimizePromptWithSuggestions(
            {
                content: content,
                suggestions: selectedSuggestions.value,
                model: optimizeModel.value
            },
            (event: any) => {
                // 处理流式响应数据
                try {
                    const chunk = JSON.parse(event.data);
                    // 兼容不同格式的 chunk
                    const content = chunk.content || chunk.kwargs?.content || '';
                    if (content) {
                        optimizedContent += content;
                        emit('update:content', optimizedContent);
                    }
                } catch (e) {
                    // 忽略解析异常
                }
            },
            () => {
                // 流式响应结束
                optimizing.value = false;
                resetEvaluateResult();
            },
            () => {
                // 发生错误
                optimizing.value = false;
                ElMessage.error('优化失败，请重试');
                // 恢复原始内容
                emit('update:content', content);
            }
        );
    } catch (e) {
        ElMessage.error('优化失败，请重试');
        optimizing.value = false;
    }
}

// 获取分数颜色
function getScoreColor(score: number) {
    if (score >= 80) return '#67c23a';
    if (score >= 60) return '#e6a23c';
    if (score >= 40) return '#f56c6c';
    return '#909399';
}

// 维度描述
const dimensionDescriptions: any = {
    '清晰性': '提示词是否语义明确、无歧义，指令易于理解。',
    '具体性': '是否包含足够的上下文、约束条件（如格式、长度、语气、角色、受众等）和任务细节。',
    '相关性': '提示词内容是否紧密围绕目标任务，避免无关或冗余信息。',
    '可执行性': '模型是否能根据提示可靠地生成符合预期的输出，指令是否可操作。',
    '一致性': '在相同条件下多次运行是否产生语义和结构稳定的结果。',
    '效率性': '是否以简洁、最小化的语言达成目标，避免冗长或浪费 token。',
    '鲁棒性': '对措辞微调、同义替换或输入扰动是否保持输出质量稳定。',
    '目标对齐度': '生成结果是否真正满足用户意图、业务场景及伦理合规要求。',
    '可扩展性': '提示词是否具备模板化潜力，可泛化至类似任务或领域。',
    '用户友好性': '非技术用户是否能轻松理解并有效使用该提示词。'
};

function getDimensionDescription(dimension: string | number) {
    const key = String(dimension);
    return dimensionDescriptions[key] || '暂无说明';
}
</script>

<style scoped>
.evaluation-sidebar {
    border-left: 1px solid #e4e7ed;
    padding-left: 20px;
}

.flex-between {
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.mb10 {
    margin-bottom: 10px;
}

.mt100 {
    margin-top: 100px;
}

.text-center {
    text-align: center;
}

.text-muted {
    color: #909399;
}

.overall-score-section,
.dimension-score-section {
    display: flex;
    flex-direction: column;
    height: 100%;
}

.section-title {
    font-size: 14px;
    font-weight: 600;
    color: #303133;
    margin-bottom: 8px;
    text-align: center;
}

.mt10 {
    margin-top: 10px;
}

.mt5 {
    margin-top: 5px;
}

.font-16 {
    font-size: 16px;
}

.font-bold {
    font-weight: bold;
}

.dimension-row {
    display: flex;
    align-items: center;
    margin-bottom: 8px;
    gap: 8px;
}

.dimension-name {
    width: 70px;
    min-width: 70px;
    max-width: 70px;
    font-size: 12px;
    cursor: help;
    border-bottom: 1px dotted #999;
    flex-shrink: 0;
    text-align: left;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}

.progress-container {
    flex: 1;
    min-width: 80px;
}

.dimension-score {
    width: 40px;
    min-width: 40px;
    max-width: 40px;
    font-size: 12px;
    text-align: right;
    flex-shrink: 0;
}

.evaluation-list {
    margin: 0;
    padding-left: 16px;
    font-size: 13px;
}

.mb5 {
    margin-bottom: 5px;
}

.suggestions-container {
    margin-bottom: 16px;
    padding-right: 0;
}

.suggestion-item {
    margin-bottom: 8px;
    padding: 6px;
    border-radius: 4px;
    transition: background-color 0.2s;
}

.suggestion-item:hover {
    background-color: #f5f7fa;
}

.suggestion-checkbox {
    width: 100%;
    align-items: flex-start !important;
    line-height: 1.5;
}

.suggestion-text {
    font-size: 13px;
    line-height: 1.6;
    word-break: break-word;
    white-space: normal;
    display: block;
    margin-top: 1px;
    padding-left: 4px;
}

.suggestions-actions {
    display: flex;
    flex-direction: column;
    gap: 12px;
    padding: 16px;
    background: linear-gradient(135deg, #f8f9fa 0%, #f1f3f4 100%);
    border-radius: 8px;
    border: 1px solid #e1e4e8;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.model-select-row {
    display: flex;
    align-items: center;
    gap: 12px;
}

.model-label {
    font-size: 13px;
    font-weight: 600;
    color: #24292e;
    white-space: nowrap;
    min-width: 70px;
}

.model-select {
    flex: 1;
    max-width: 220px;
}

.button-row {
    display: flex;
    gap: 10px;
    justify-content: flex-end;
}

.action-btn {
    font-size: 12px;
    border-radius: 6px;
    font-weight: 500;
    transition: all 0.2s ease;
    min-width: 90px;
}

.secondary-btn {
    background-color: #ffffff;
    border-color: #d0d7de;
    color: #656d76;
}

.secondary-btn:hover {
    background-color: #f3f4f6;
    border-color: #8c959f;
    color: #24292e;
}

.primary-btn {
    background: linear-gradient(135deg, #0969da 0%, #0550ae 100%);
    border-color: #0969da;
    box-shadow: 0 1px 2px rgba(9, 105, 218, 0.2);
}

.primary-btn:hover {
    background: linear-gradient(135deg, #0550ae 0%, #033d8b 100%);
    border-color: #0550ae;
    box-shadow: 0 2px 4px rgba(9, 105, 218, 0.3);
    transform: translateY(-1px);
}

.primary-btn:disabled {
    background: #8c959f;
    border-color: #8c959f;
    transform: none;
    box-shadow: none;
}

.empty-suggestions {
    text-align: center;
    color: #909399;
    padding: 40px 20px;
    font-size: 14px;
}

:deep(.el-progress-bar__outer) {
    height: 8px !important;
}

:deep(.el-progress-bar__inner) {
    height: 8px !important;
}

:deep(.el-checkbox) {
    align-items: flex-start;
    margin-bottom: 4px;
}

:deep(.el-checkbox__input) {
    margin-top: 2px;
}

:deep(.el-checkbox__label) {
    line-height: 1.4;
    white-space: normal;
    word-break: break-word;
}

:deep(.el-tabs__content) {
    overflow: visible;
}

:deep(.el-tab-pane) {
    overflow: visible;
}
</style>
