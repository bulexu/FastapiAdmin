"""
钉钉服务类，提供钉钉API相关功能
"""
import time

from alibabacloud_tea_openapi import models as open_api_models
from app.config.setting import settings

from .constants import (
    DINGTALK_SDK_PROTOCOL,
    DINGTALK_SDK_REGION_ID
)


class DingTalkClient:
    """钉钉服务类"""
    
    def __init__(self, app_key: str = None, app_secret: str = None):
        """
        初始化钉钉服务
        
        Args:
            app_key: 钉钉应用Key
            app_secret: 钉钉应用Secret
        """
        self.app_key = app_key or settings.DINGTALK_APP_KEY
        self.app_secret = app_secret or settings.DINGTALK_APP_SECRET
        self._access_token = None
        self._token_expires_at = 0
        self._client = None
    
    def _get_access_token(self) -> str:
        """
        获取钉钉访问令牌
        
        Returns:
            str: 访问令牌
        """
        # 如果token还有效，直接返回
        if self._access_token and time.time() < self._token_expires_at:
            return self._access_token
        
        # 使用官方SDK获取token
        try:
            from alibabacloud_dingtalk.oauth2_1_0.client import Client as OAuthClient
            from alibabacloud_dingtalk.oauth2_1_0 import models as oauth_models
            
            config = open_api_models.Config()
            config.protocol = DINGTALK_SDK_PROTOCOL
            config.region_id = DINGTALK_SDK_REGION_ID
            
            oauth_client = OAuthClient(config)
            get_access_token_request = oauth_models.GetAccessTokenRequest()
            get_access_token_request.app_key = self.app_key
            get_access_token_request.app_secret = self.app_secret
            
            response = oauth_client.get_access_token(get_access_token_request)
            
            if response.body.access_token:
                self._access_token = response.body.access_token
                # 设置过期时间（提前5分钟过期）
                self._token_expires_at = time.time() + response.body.expire_in - 300
                return self._access_token
            else:
                raise Exception("获取access_token失败")
                
        except Exception as e:
            raise Exception(f"获取access_token失败: {str(e)}")