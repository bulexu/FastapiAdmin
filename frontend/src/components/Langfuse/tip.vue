<template>
  <el-drawer v-model="visible" :title="'Langfuse 使用示例'" size="60%" :with-header="true">
    <div class="langfuse-tip-content">
      <section>
        <h3>Python</h3>
        <CodeBlock :code="pythonCode" language="python" />
      </section>
      <section>
        <h3>JS/TS</h3>
        <CodeBlock :code="jsCode" language="javascript" />
      </section>
      <div class="doc-link">
        <el-link underline="always" type="primary" href="https://langfuse.com/docs/prompt-management/get-started"
          target="_blank">查看官网文档</el-link>
      </div>
    </div>
  </el-drawer>
</template>

<script setup>
import { defineProps, defineEmits, computed } from 'vue'
import CodeBlock from '@/components/Code/index.vue';
const props = defineProps({ modelValue: Boolean })
const emit = defineEmits(['update:modelValue'])
const visible = computed({
  get: () => props.modelValue,
  set: v => emit('update:modelValue', v)
})

const pythonCode = `from langfuse import Langfuse

# Initialize Langfuse client
langfuse = Langfuse()

# Or with configuration
langfuse = Langfuse(
  public_key="langfuse_public_key",
  secret_key="langfuse_secret_key",
  host="langfuse_host"
)

# Get production prompt
prompt = langfuse.get_prompt("dify-workflow-designer")

# Get by label
# You can use as many labels as you'd like to identify different deployment targets
prompt = langfuse.get_prompt("dify-workflow-designer", label="production")
prompt = langfuse.get_prompt("dify-workflow-designer", label="latest")

# Get by version number, usually not recommended as it requires code changes to deploy new prompt versions
langfuse.get_prompt("dify-workflow-designer", version=1)

# Compile the variable and resolve the placeholder with a list of messages.
compiled_prompt = prompt.compile(criticlevel="expert", chat_history=[
  {"role": "user", "content": "I love Ron Fricke movies like Baraka"},
  {"role": "user", "content": "Also, the Korean movie Memories of a Murderer"}
])
`;

const jsCode = `import { LangfuseClient } from "@langfuse/client";

// Initialize the Langfuse client
const langfuse = new LangfuseClient();

// Or with configuration
const langfuse = new LangfuseClient({
  publicKey: "your-public-key",
  secretKey: "your-secret-key",
  baseUrl: "https://cloud.langfuse.com", // or your self-hosted instance
});

// Get production prompt
const prompt = await langfuse.prompt.get("dify-workflow-designer");

// Get by label
// You can use as many labels as you'd like to identify different deployment targets
const prompt = await langfuse.prompt.get("dify-workflow-designer", { label: "production" })
const prompt = await langfuse.prompt.get("dify-workflow-designer", { label: "latest" })

// Get by version number, usually not recommended as it requires code changes to deploy new prompt versions
await langfuse.prompt.get("dify-workflow-designer", { version: 1 })

// Compile the variable and resolve the placeholder with a list of messages.
const compiledPrompt = prompt.compile(
  // variables
  { criticlevel: "expert" },
  // placeholders
  {
    chat_history: [
      { role: "user", content: "I love Ron Fricke movies like Baraka" },
      {
        role: "user",
        content: "Also, the Korean movie Memories of a Murderer",
      },
    ],
  }
);

`;
</script>

<style scoped>
.langfuse-tip-content {
  padding: 16px;
}

section {
  margin-bottom: 24px;
}

.doc-link {
  margin-top: 16px;
  font-size: 14px;
}
</style>
