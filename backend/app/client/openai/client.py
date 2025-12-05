import logging
from app.config.setting import settings
from typing import Any, Iterator, AsyncIterator
import json_repair
from langchain_openai import ChatOpenAI
from langchain_core.messages import BaseMessageChunk


class AIClient:
	def __init__(self):
		self.model = settings.OPENAI_MODEL
		self.api_key = settings.OPENAI_API_KEY
		self.base_url = settings.OPENAI_BASE_URL
		self.llm = ChatOpenAI(
			model=self.model,
			openai_api_key=self.api_key,
			openai_api_base=self.base_url,
			temperature=0.7,
		)

	def get_llm(self, model: str, json_format: bool, temperature: float = 0.7) -> ChatOpenAI:
		llm = self.llm
		kwargs = {"temperature": temperature}
		if model != self.model:
			kwargs["model"] = model
		if json_format:
			kwargs["response_format"] = {"type": "json_object"}
		
		if kwargs:
			return llm.bind(**kwargs)
		return llm

	def chat(self, messages: list, model: str = "qwen-plus", json_format: bool = False) -> Any:
		"""
		通用对话接口，自动适配不同 LLM 服务商，支持 messages 参数
		"""
		try:
			llm = self.get_llm(model, json_format)
			response = llm.invoke(messages)
			content = response.content
			if json_format:
				return json_repair.loads(content)
			return content
		except Exception as e:
			logging.error(f"AI请求失败: {e}")
			return {} if json_format else ""

	async def achat(self, messages: list, model: str = "qwen-plus", json_format: bool = False) -> Any:
		"""
		通用对话接口，自动适配不同 LLM 服务商，支持 messages 参数
		"""
		try:
			llm = self.get_llm(model, json_format)
			response = await llm.ainvoke(messages)
			content = response.content
			if json_format:
				return json_repair.loads(content)
			return content
		except Exception as e:
			logging.error(f"AI请求失败: {e}")
			return {} if json_format else ""

	def chat_stream(self, messages: list, model: str = "qwen-plus") -> Iterator[BaseMessageChunk]:
		"""
		流式响应，返回生成内容的迭代器
		"""
		llm = self.get_llm(model, False)
		for chunk in llm.stream(messages):
			yield chunk
			

	async def achat_stream(self, messages: list, model: str = "qwen-plus") -> AsyncIterator[BaseMessageChunk]:
		"""
		流式响应，返回生成内容的异步迭代器
		"""
		llm = self.get_llm(model, False)
		async for chunk in llm.astream(messages):
			yield chunk


# 单例
ai_client = AIClient()