from typing import List, Dict, Any, Optional, Union
import logging
from playwright.async_api import Page, ElementHandle
from .selector_handlers.base_selector_handler import (
    ElementNotFoundError, 
    InvalidSelectorError, 
    SelectorError
)
from .selector_handlers.css_selector_handler import CSSSelectorHandler
from .selector_handlers.xpath_selector_handler import XPathSelectorHandler
from .selector_handlers.id_selector_handler import IDSelectorHandler
from .selector_handlers.name_selector_handler import NameSelectorHandler
from .selector_handlers.class_selector_handler import ClassSelectorHandler

class BaseSelectorHandler:
    """
    选择器处理器基类
    """
    @staticmethod
    async def find_element(page: Page, selector: str) -> Optional[ElementHandle]:
        """
        在页面中查找单个元素
        
        :param page: Playwright 页面对象
        :param selector: 选择器字符串
        :return: 找到的元素，如果未找到则返回 None
        """
        raise NotImplementedError("子类必须实现 find_element 方法")

    @staticmethod
    async def find_elements(page: Page, selector: str) -> List[ElementHandle]:
        """
        在页面中查找多个元素
        
        :param page: Playwright 页面对象
        :param selector: 选择器字符串
        :return: 找到的元素列表
        """
        raise NotImplementedError("子类必须实现 find_elements 方法")

class SelectorEngine:
    """
    选择器引擎，用于处理不同类型的选择器
    """
    def __init__(self, page: Optional[Page] = None):
        """
        初始化选择器引擎
        
        :param page: Playwright 页面对象，可选
        """
        self.page = page
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # 使用工厂方法创建处理器
        self.handlers = {
            'css': CSSSelectorHandler(page),
            'xpath': XPathSelectorHandler(page),
            'id': IDSelectorHandler(page),
            'name': NameSelectorHandler(page),
            'class': ClassSelectorHandler(page)
        }

    def _create_handler(self, selector_type: str):
        """
        创建选择器处理器的辅助方法
        
        :param selector_type: 选择器类型
        :return: 选择器处理器实例
        """
        handler_class = self.handlers.get(selector_type)
        if not handler_class:
            raise InvalidSelectorError(selector_type, f"找不到选择器类型 '{selector_type}' 的处理器")
        return handler_class

    @classmethod
    def parse_selector(cls, selector: str) -> tuple[str, str]:
        """
        解析选择器，提取选择器类型和值
        
        :param selector: 选择器字符串
        :return: 包含选择器类型和值的元组
        """
        # 处理 None 和空字符串
        if selector is None or selector == '':
            raise InvalidSelectorError(str(selector), "选择器必须是非空字符串")
        
        # 处理特殊前缀选择器
        if selector.startswith('css:'):
            selector_value = selector[4:]
            if not selector_value:
                raise InvalidSelectorError(selector, "选择器值不能为空")
            # 简单的 CSS 选择器语法验证
            if not cls._is_valid_css_selector(selector_value):
                raise InvalidSelectorError(selector, "无效的 CSS 选择器")
            return 'css', selector_value
        elif selector.startswith('xpath:'):
            selector_value = selector[6:]
            if not selector_value:
                raise InvalidSelectorError(selector, "选择器值不能为空")
            # 简单的 XPath 选择器语法验证
            if not cls._is_valid_xpath_selector(selector_value):
                raise InvalidSelectorError(selector, "无效的 XPath 选择器")
            return 'xpath', selector_value
        elif selector.startswith('id:'):
            selector_value = selector[3:]
            if not selector_value:
                raise InvalidSelectorError(selector, "选择器值不能为空")
            return 'id', selector_value
        elif selector.startswith('name:'):
            selector_value = selector[5:]
            if not selector_value:
                raise InvalidSelectorError(selector, "选择器值不能为空")
            return 'name', selector_value
        elif selector.startswith('class:'):
            selector_value = selector[6:]
            if not selector_value:
                raise InvalidSelectorError(selector, "选择器值不能为空")
            return 'class', selector_value
        elif selector.startswith('[name='):
            selector_value = selector[6:-1].strip('"')
            return 'name', selector_value
        elif selector.startswith('#'):
            return 'id', selector[1:]
        elif selector.startswith('.'):
            return 'class', selector[1:]
        elif ':' in selector:
            # 处理未知的选择器类型
            raise InvalidSelectorError(selector, "不支持的选择器类型")
        
        # 默认为 CSS 选择器
        return 'css', selector

    @staticmethod
    def _is_valid_css_selector(selector: str) -> bool:
        """
        简单验证 CSS 选择器的有效性
        
        :param selector: CSS 选择器字符串
        :return: 是否为有效的 CSS 选择器
        """
        try:
            # 检查是否包含基本的 CSS 选择器字符
            if not any(char in selector for char in ['#', '.', '[', ']', ':', '>']):
                return False
            
            # 检查括号是否匹配
            if selector.count('[') != selector.count(']'):
                return False
            
            return True
        except Exception:
            return False

    @staticmethod
    def _is_valid_xpath_selector(selector: str) -> bool:
        """
        简单验证 XPath 选择器的有效性
        
        :param selector: XPath 选择器字符串
        :return: 是否为有效的 XPath 选择器
        """
        try:
            # 检查是否以 // 或 ( 开头
            if not (selector.startswith('//') or selector.startswith('(')):
                return False
            
            # 检查是否包含基本的 XPath 语法元素
            if not any(char in selector for char in ['@', '=', '[', ']']):
                return False
            
            # 检查括号是否匹配
            if selector.count('[') != selector.count(']'):
                return False
            
            return True
        except Exception:
            return False

    async def find_element(self, selector: str) -> Optional[ElementHandle]:
        """
        使用指定选择器查找单个元素
        
        :param selector: 选择器字符串
        :return: 找到的元素
        """
        selector_type, selector_value = self.parse_selector(selector)
        handler = self.handlers.get(selector_type)
        
        if handler is None:
            raise InvalidSelectorError(selector, f"不支持的选择器类型: {selector_type}")
        
        try:
            self.logger.debug(f"使用 {selector_type} 选择器查找元素: {selector_value}")
            element = await handler.find_element(selector_value)

            if element is not None:
                self.logger.info(f"成功找到元素，选择器: {selector}, 类型: {selector_type}")
                return element
            else:
                self.logger.warning(f"未找到元素，选择器: {selector}, 类型: {selector_type}")
                raise ElementNotFoundError(selector)

        except InvalidSelectorError as e:
            self.logger.error(f"无效的选择器: {selector}, 错误信息: {e}")
            raise
        except ElementNotFoundError as e:
            self.logger.warning(f"元素未找到: {selector}, 错误信息: {e}")
            raise
        except Exception as e:
            self.logger.error(f"查找元素时发生未预期的错误，选择器: {selector}, 错误信息: {e}")
            raise SelectorError(f"查找元素时发生未预期的错误: {selector}, {e}") from e

    async def find_elements(self, selector: str) -> List[ElementHandle]:
        """
        使用指定选择器查找多个元素
        
        :param selector: 选择器字符串
        :return: 找到的元素列表
        """
        selector_type, selector_value = self.parse_selector(selector)
        handler = self.handlers.get(selector_type)
        
        if handler is None:
            raise InvalidSelectorError(selector, f"不支持的选择器类型: {selector_type}")
        
        try:
            self.logger.debug(f"使用 {selector_type} 选择器查找多个元素: {selector_value}")
            elements = await handler.find_elements(selector_value)

            if elements and len(elements) > 0:
                self.logger.info(f"成功找到 {len(elements)} 个元素，选择器: {selector}, 类型: {selector_type}")
                return elements
            else:
                self.logger.warning(f"未找到任何元素，选择器: {selector}, 类型: {selector_type}")
                raise ElementNotFoundError(selector)

        except InvalidSelectorError as e:
            self.logger.error(f"无效的选择器: {selector}, 错误信息: {e}")
            raise
        except ElementNotFoundError as e:
            self.logger.warning(f"元素未找到: {selector}, 错误信息: {e}")
            raise
        except Exception as e:
            self.logger.error(f"查找多个元素时发生未预期的错误，选择器: {selector}, 错误信息: {e}")
            raise SelectorError(f"查找多个元素时发生未预期的错误: {selector}, {e}") from e
