from typing import List, Optional
from playwright.async_api import Page, ElementHandle
import logging
from .base_selector_handler import BaseSelectorHandler, ElementNotFoundError, InvalidSelectorError, SelectorError

class CSSSelectorHandler(BaseSelectorHandler):
    """
    CSS 选择器处理器
    实现 CSS 选择器的元素查找功能
    """
    def __init__(self, page: Optional[Page] = None):
        """
        初始化 CSS 选择器处理器
        
        :param page: Playwright 页面对象，可选
        """
        super().__init__(page)

    async def find_element(self, selector: str) -> Optional[ElementHandle]:
        """
        使用 CSS 选择器查找单个元素

        :param selector: CSS 选择器字符串
        :return: 找到的元素句柄，如果未找到则返回 None
        """
        # 验证 CSS 选择器语法
        if selector is None:
            raise InvalidSelectorError(str(selector), "选择器必须是非空字符串")
        
        if not selector or not selector.strip():
            raise InvalidSelectorError(selector, "CSS 选择器必须是非空字符串")

        try:
            self.logger.debug(f"CSS 选择器查找单个元素: {selector}")
            
            # 使用 query_selector 方法查找元素
            element = await self.page.query_selector(selector)

            if element:
                self.logger.info(f"成功找到 CSS 元素: {selector}")
                return element
            else:
                self.logger.warning(f"未找到匹配 CSS 选择器的元素: {selector}")
                raise ElementNotFoundError(selector)

        except ElementNotFoundError:
            raise
        except Exception as e:
            self.logger.error(f"CSS 选择器查找元素时发生错误: {selector}, 错误信息: {e}")
            raise ElementNotFoundError(selector) from e

    async def find_elements(self, selector: str) -> List[ElementHandle]:
        """
        使用 CSS 选择器查找多个元素

        :param selector: CSS 选择器字符串
        :return: 找到的元素句柄列表
        """
        # 验证 CSS 选择器语法
        if selector is None:
            raise InvalidSelectorError(str(selector), "选择器必须是非空字符串")
        
        if not selector or not selector.strip():
            raise InvalidSelectorError(selector, "CSS 选择器必须是非空字符串")

        try:
            self.logger.debug(f"CSS 选择器查找多个元素: {selector}")
            
            # 使用 query_selector_all 方法查找元素
            elements = await self.page.query_selector_all(selector)

            if elements:
                self.logger.info(f"成功找到 {len(elements)} 个 CSS 元素: {selector}")
                return elements
            else:
                self.logger.warning(f"未找到匹配 CSS 选择器的元素: {selector}")
                raise ElementNotFoundError(selector)

        except ElementNotFoundError:
            raise
        except Exception as e:
            self.logger.error(f"CSS 选择器查找多个元素时发生错误: {selector}, 错误信息: {e}")
            raise ElementNotFoundError(selector) from e 