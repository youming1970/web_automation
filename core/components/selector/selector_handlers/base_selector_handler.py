from abc import ABC, abstractmethod
import logging
from typing import List, Optional
from playwright.async_api import Page, ElementHandle

class SelectorError(Exception):
    """
    选择器基础异常类
    """
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)

class InvalidSelectorError(SelectorError):
    """
    无效选择器异常
    当选择器语法或类型不正确时抛出
    """
    def __init__(self, selector: str, reason: str = "无效的选择器"):
        self.selector = selector
        super().__init__(f"{reason}: {selector}")

class ElementNotFoundError(SelectorError):
    """
    元素未找到异常
    当使用选择器无法找到元素时抛出
    """
    def __init__(self, selector: str, message: str = "未找到指定元素"):
        self.selector = selector
        super().__init__(f"{message}: {selector}")

class BaseSelectorHandler(ABC):
    """
    选择器处理器抽象基类
    定义选择器处理的标准接口
    """
    def __init__(self, page: Optional[Page] = None):
        """
        初始化选择器处理器
        
        :param page: Playwright 页面对象，可选
        """
        self.page = page
        self.logger = logging.getLogger(self.__class__.__name__)

    @abstractmethod
    async def find_element(self, selector_value: str) -> Optional[ElementHandle]:
        """
        查找单个元素
        
        :param selector_value: 选择器值
        :return: 找到的元素，未找到返回 None
        :raises ElementNotFoundError: 当无法找到元素时
        :raises InvalidSelectorError: 当选择器无效时
        """
        pass

    @abstractmethod
    async def find_elements(self, selector_value: str) -> List[ElementHandle]:
        """
        查找多个元素
        
        :param selector_value: 选择器值
        :return: 找到的元素列表
        :raises ElementNotFoundError: 当无法找到元素时
        :raises InvalidSelectorError: 当选择器无效时
        """
        pass
