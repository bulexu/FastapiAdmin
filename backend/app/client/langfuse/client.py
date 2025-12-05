import logging
from typing import Optional
from langfuse import Langfuse
from app.config.setting import settings


class LangfuseClient:
    _instance = None
    _client: Optional[Langfuse] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(LangfuseClient, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        if settings.LANGFUSE_ENABLED:
            try:
                self._client = Langfuse(
                    public_key=settings.LANGFUSE_PUBLIC_KEY,
                    secret_key=settings.LANGFUSE_SECRET_KEY,
                    host=settings.LANGFUSE_HOST
                )
                logging.info("Langfuse client initialized successfully.")
            except Exception as e:
                logging.error(f"Failed to initialize Langfuse client: {e}")
        else:
            logging.info("Langfuse 未启用，未实例化 langfuse 对象。")

    @property
    def client(self) -> Optional[Langfuse]:
        return self._client


# 创建单例实例
langfuse_client = LangfuseClient()
# 导出 langfuse 实例，保持原有引用方式
langfuse = langfuse_client.client
