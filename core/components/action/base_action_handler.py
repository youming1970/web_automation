from typing import Dict, Any
from playwright.async_api import Page
from core.components.selector.selector_engine import SelectorEngine

class BaseActionHandler:
    """动作处理器基类"""
    
    def __init__(self, page: Page, selector_engine: SelectorEngine):
        """
        初始化处理器
        
        :param page: Playwright页面对象
        :param selector_engine: 选择器引擎
        """
        self.page = page
        self.selector_engine = selector_engine

    async def execute(self, action_data: Dict[str, Any]) -> Any:
        """
        执行动作
        
        :param action_data: 动作数据
        :return: 执行结果
        """
        raise NotImplementedError("子类必须实现execute方法")

    async def validate(self, action_data: Dict[str, Any]) -> bool:
        """
        验证动作参数
        
        :param action_data: 动作数据
        :return: 是否验证通过
        """
        raise NotImplementedError("子类必须实现validate方法") 