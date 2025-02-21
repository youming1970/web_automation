from typing import List, Optional
from playwright.async_api import Page, ElementHandle
from .base_selector_handler import BaseSelectorHandler, ElementNotFoundError, InvalidSelectorError, SelectorError

class XPathSelectorHandler(BaseSelectorHandler):
    """
    XPath 选择器处理器
    实现 XPath 选择器的元素查找功能
    """
    def __init__(self, page: Optional[Page] = None):
        """
        初始化 XPath 选择器处理器
        
        :param page: Playwright 页面对象，可选
        """
        super().__init__(page)

    async def find_element(self, selector: str) -> Optional[ElementHandle]:
        """
        使用 XPath 选择器查找单个元素

        :param selector: XPath 选择器字符串
        :return: 找到的元素句柄，如果未找到则返回 None
        """
        if selector is None or not selector:
            raise InvalidSelectorError(str(selector), "选择器必须是非空字符串")
        
        if not (selector.startswith('//') or selector.startswith('(')):
            raise InvalidSelectorError(selector, "XPath 选择器必须以 '//' 或 '(' 开头")

        self.logger.debug(f"XPath 选择器查找单个元素: {selector}")
        
        try:
            locator = await self.page.locator(selector)
            first = await locator.first()
            if first:
                element = await first.element_handle()
                if element is not None:
                    self.logger.info(f"成功找到 XPath 元素: {selector}")
                    return element
            
            self.logger.warning(f"未找到匹配 XPath 选择器的元素: {selector}")
            raise ElementNotFoundError(selector)
            
        except ElementNotFoundError:
            raise
        except Exception as e:
            self.logger.warning(f"未找到匹配 XPath 选择器的元素: {selector}")
            raise ElementNotFoundError(selector) from e

    async def find_elements(self, selector: str) -> List[ElementHandle]:
        """
        使用 XPath 选择器查找多个元素

        :param selector: XPath 选择器字符串
        :return: 找到的元素句柄列表
        """
        # 验证 XPath 选择器语法
        if selector is None or not selector:
            raise InvalidSelectorError(str(selector), "选择器必须是非空字符串")
        
        if not (selector.startswith('//') or selector.startswith('(')):
            raise InvalidSelectorError(selector, "XPath 选择器必须以 '//' 或 '(' 开头")

        self.logger.debug(f"XPath 选择器查找多个元素: {selector}")
        
        try:
            # 使用 locator 方法查找元素
            locator = await self.page.locator(selector)
            
            # 获取所有元素句柄
            elements = await locator.all_element_handles()

            if elements and len(elements) > 0:
                self.logger.info(f"成功找到 {len(elements)} 个 XPath 元素: {selector}")
                return elements
            else:
                self.logger.warning(f"未找到匹配 XPath 选择器的元素: {selector}")
                raise ElementNotFoundError(selector)

        except Exception as e:
            self.logger.warning(f"未找到匹配 XPath 选择器的元素: {selector}")
            raise ElementNotFoundError(selector) from e 