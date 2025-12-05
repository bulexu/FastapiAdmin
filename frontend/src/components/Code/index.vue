<template>
  <div class="code-block-wrapper">
    <el-tooltip content="复制" placement="top">
      <el-button class="copy-btn" size="small" icon="CopyDocument" @click="copyCode" circle>
      </el-button>
    </el-tooltip>
    <pre v-html="highlightedCode" class="code-block"></pre>
  </div>
</template>

<script setup>
import { ref, watch, defineProps } from 'vue';
import hljs from 'highlight.js/lib/core';
import python from 'highlight.js/lib/languages/python';
import javascript from 'highlight.js/lib/languages/javascript';
import 'highlight.js/styles/github.css';
import { ElMessage } from 'element-plus';

hljs.registerLanguage('python', python);
hljs.registerLanguage('javascript', javascript);

const props = defineProps({
  code: String,
  language: String
});

const highlightedCode = ref('');

watch(() => props.code, (newCode) => {
  highlightedCode.value = hljs.highlight(newCode, { language: props.language }).value;
}, { immediate: true });

function copyCode() {
  navigator.clipboard.writeText(props.code).then(() => {
    ElMessage.success('复制成功');
  });
}
</script>

<style scoped>
.code-block-wrapper {
  position: relative;
  background: #f6f8fa;
  border-radius: 6px;
  padding: 16px 16px 8px 16px;
  margin-top: 8px;
}
.copy-btn {
  position: absolute;
  top: 8px;
  right: 8px;
  z-index: 2;
}
.code-block {
  font-size: 14px;
  font-family: 'Fira Mono', 'Consolas', 'Menlo', monospace;
  white-space: pre;
  overflow-x: auto;
  margin: 0;
}
</style>
