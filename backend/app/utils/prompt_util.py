# -*- coding: utf-8 -*-

import yaml
from typing import Optional, Dict, Any
from app.core.logger import log
from app.config.path_conf import STATIC_DIR

class PromptUtil:
    """提示词工具类，用于管理和获取提示词内容"""
    
    _cache: Dict[str, str] = {}
    _yaml_path = STATIC_DIR / "assets" / "prompt.yaml"
    
    @classmethod
    def _load_prompts(cls) -> Dict[str, Any]:
        """加载提示词YAML文件"""
        try:
            if cls._yaml_path.exists():
                with open(cls._yaml_path, 'r', encoding='utf-8') as file:
                    return yaml.safe_load(file) or {}
            else:
                log.warning(f"提示词文件不存在: {cls._yaml_path}")
                return {}
        except Exception as e:
            log.error(f"加载提示词文件失败: {e}")
            return {}
    
    @classmethod
    def get_prompt(cls, key: str) -> Optional[str]:
        """
        获取指定的提示词内容
        :param key: 提示词键名
        :return: 提示词内容，如果不存在返回None
        """
        if key in cls._cache:
            return cls._cache[key]
        
        prompts = cls._load_prompts()
        if key in prompts and 'content' in prompts[key]:
            content = prompts[key]['content'].strip()
            cls._cache[key] = content
            return content
        
        log.warning(f"提示词不存在: {key}")
        return None
    
    @classmethod
    def get_prompt_generator(cls) -> Optional[str]:
        """获取提示词生成器提示词"""
        return cls.get_prompt('prompt_generator')
    
    @classmethod
    def get_prompt_evaluator(cls) -> Optional[str]:
        """获取提示词评估专家提示词"""
        return cls.get_prompt('prompt_evaluator')
    
    @classmethod
    def get_prompt_optimizer(cls) -> Optional[str]:
        """获取提示词优化专家提示词"""
        return cls.get_prompt('prompt_optimizer')
    
    @classmethod
    def refresh_cache(cls):
        """刷新缓存"""
        cls._cache.clear()
    
    @classmethod
    def get_all_prompts(cls) -> Dict[str, str]:
        """获取所有提示词"""
        prompts = cls._load_prompts()
        result = {}
        for key, value in prompts.items():
            if 'content' in value:
                result[key] = value['content'].strip()
        return result
    
    @classmethod
    def get_prompt_info(cls, key: str) -> Optional[Dict[str, Any]]:
        """
        获取提示词的完整信息（包括标题和内容）
        :param key: 提示词键名
        :return: 提示词信息字典
        """
        prompts = cls._load_prompts()
        return prompts.get(key)
    
    @classmethod
    def validate_yaml(cls) -> bool:
        """验证YAML文件格式是否正确"""
        try:
            prompts = cls._load_prompts()
            required_keys = ['prompt_generator', 'prompt_evaluator', 'prompt_optimizer']
            
            for key in required_keys:
                if key not in prompts:
                    log.error(f"缺少必需的提示词配置: {key}")
                    return False
                
                if 'content' not in prompts[key]:
                    log.error(f"提示词配置缺少content字段: {key}")
                    return False
            
            return True
        except Exception as e:
            log.error(f"验证YAML文件失败: {e}")
            return False
