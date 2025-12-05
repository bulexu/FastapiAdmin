<template>
    <el-dialog title="版本详情" v-model="visible" width="900px" append-to-body>
        <div>
            <div class="mb10">
                <span class="font-bold">版本号：</span>V{{ detail.version }}
            </div>
            <div class="mb10">
                <span class="font-bold">能力标签：</span>
                <el-tag v-for="(tag, idx) in detail.ability_tags" :key="idx" class="mb5 ml5">{{
                    tag
                }}
                </el-tag>
            </div>
            <div class="mb10">
                <span class="font-bold">内容预览：</span>
                <WangEditor v-model="detail.content" height="400px" :readonly="true" />
            </div>
        </div>
        <template #footer>
            <el-button type="primary" @click="rollbackToVersion" v-if="!detail.is_archived">加载此版本
            </el-button>
            <el-button type="primary" @click="copyContent">复制内容</el-button>
            <el-button @click="visible = false">关闭</el-button>
        </template>
    </el-dialog>
</template>

<script setup lang="ts">
import { computed, getCurrentInstance } from "vue";
import WangEditor from '@/components/WangEditor/index.vue';

const props = defineProps({
    modelValue: {
        type: Boolean,
        default: false
    },
    detail: {
        type: Object,
        default: () => ({
            content: '',
            ability_tags: [],
            version: '',
            is_archived: false
        })
    }
});

const emit = defineEmits(['update:modelValue', 'rollback']);

const { proxy } = getCurrentInstance() as any;

const visible = computed({
    get: () => props.modelValue,
    set: (val) => emit('update:modelValue', val)
});

function rollbackToVersion() {
    emit('rollback', props.detail);
    visible.value = false;
}

function copyContent() {
    const content = props.detail.content;
    if (navigator?.clipboard) {
        navigator.clipboard.writeText(content).then(() => {
            ElMessage.success('内容已复制到剪贴板');
        }, () => {
            ElMessage.error('复制失败');
        });
    } else {
        const textarea = document.createElement('textarea');
        textarea.value = content;
        document.body.appendChild(textarea);
        textarea.select();
        try {
            document.execCommand('copy');
            ElMessage.success('内容已复制到剪贴板');
        } catch (err) {
            ElMessage.error('复制失败');
        }
        document.body.removeChild(textarea);
    }
}
</script>

<style scoped>
.mb10 {
    margin-bottom: 10px;
}

.mb5 {
    margin-bottom: 5px;
}

.ml5 {
    margin-left: 5px;
}

.font-bold {
    font-weight: bold;
}
</style>
