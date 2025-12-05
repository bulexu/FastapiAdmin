<template>
    <div class="mt40 mb20" v-loading="loading" v-if="visible">
        <!-- 底部历史版本时间轴 -->
        <el-divider content-position="left">
            <h4>历史版本</h4>
        </el-divider>

        <el-empty v-if="!versionList.length && !loading" description="暂无历史版本" />

        <el-timeline v-if="versionList.length">
            <el-timeline-item v-for="item in versionList" :key="item.id" :timestamp="parseTime(item.created_time)"
                :color="item.is_archived ? '#909399' : '#67c23a'" placement="top">
                <el-card shadow="hover">
                    <div class="flex-between">
                        <div>
                            <h4>V{{ item.version }}</h4>
                            <p>{{ item.description || '无备注' }}</p>
                        </div>
                        <div>
                            <el-button size="small" @click="showVersionDetail(item)">查看</el-button>
                            <el-button size="small" type="primary" @click="rollbackToVersion(item)"
                                v-if="!item.is_archived">加载此版本
                            </el-button>
                        </div>
                    </div>
                </el-card>
            </el-timeline-item>
        </el-timeline>
    </div>
</template>

<script setup lang="ts">
import { ref, watch } from "vue";
import PromptAPI, { type PromptVersionTable } from "@/api/module_application/prompt";

const props = defineProps({
    promptId: {
        type: Number,
        default: undefined
    },
    visible: {
        type: Boolean,
        default: false
    }
});

const emit = defineEmits(['show-detail', 'rollback']);

const loading = ref(false);
const versionList = ref<PromptVersionTable[]>([]);

watch([() => props.promptId, () => props.visible], ([newId, newVisible]) => {
    if (newId && newVisible) {
        loadVersionList();
    }
}, { immediate: true });

// 获取版本列表
async function loadVersionList() {
    if (!props.promptId) return;

    loading.value = true;
    try {
        const res = await PromptAPI.getVersionList(props.promptId);
        versionList.value = res.data.data;
    } catch (e) {
        versionList.value = [];
    }
    loading.value = false;
}

function showVersionDetail(item: any) {
    emit('show-detail', item);
}

function rollbackToVersion(item: any) {
    emit('rollback', item);
}

function parseTime(time?: string) {
    if (!time) return '';
    return time.replace('T', ' ');
}

defineExpose({
    loadVersionList
});
</script>

<style scoped>
.mt40 {
    margin-top: 40px;
}

.mb20 {
    margin-bottom: 20px;
}

.flex-between {
    display: flex;
    justify-content: space-between;
    align-items: center;
}
</style>
