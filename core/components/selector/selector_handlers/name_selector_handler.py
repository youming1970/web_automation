from typing import List, Optional
from playwright.async_api import Page, ElementHandle
from .base_selector_handler import BaseSelectorHandler, ElementNotFoundError, InvalidSelectorError

class NameSelectorHandler(BaseSelectorHandler):
    """
    Name 选择器处理器
    实现 Name 选择器的元素查找功能
    """
    def __init__(self, page: Optional[Page] = None):
        """
        初始化 Name 选择器处理器
        
        :param page: Playwright 页面对象，可选
        """
        super().__init__(page)

    async def find_element(self, selector_value: str) -> Optional[ElementHandle]:
        """
        使用 Name 选择器查找单个元素
        
        :param selector_value: Name 选择器值
        :return: 找到的元素，未找到返回 None
        :raises ElementNotFoundError: 当无法找到元素时
        :raises InvalidSelectorError: 当选择器无效时
        """
        try:
            # 验证选择器的基本语法
            if not selector_value or not isinstance(selector_value, str):
                raise InvalidSelectorError(selector_value, "Name 选择器必须是非空字符串")
            
            # 确保 Name 选择器以 '[name=""]' 格式
            if not selector_value.startswith('[name="') and not selector_value.startswith('name:'):
                selector_value = f'[name="{selector_value}"]'
            elif selector_value.startswith('name:'):
                selector_value = f'[name="{selector_value.split(":", 1)[1]}"]'
            
            self.logger.debug(f"Name 选择器查找单个元素 - 选择器: {selector_value}, 页面: {self.page}")
            
            element = await self.page.query_selector(selector_value)
            
            if element is None:
                self.logger.warning(f"未找到匹配 Name 选择器的元素 - 选择器: {selector_value}")
                raise ElementNotFoundError(selector_value)
            
            self.logger.info(f"成功使用 Name 选择器找到元素 - 选择器: {selector_value}")
            return element
        
        except InvalidSelectorError:
            raise
        
        except ElementNotFoundError:
            raise
        
        except Exception as e:
            self.logger.error(f"使用 Name 选择器查找元素时发生错误 - 选择器: {selector_value}, 错误: {e}")
            raise ElementNotFoundError(selector_value) from e

    async def find_elements(self, selector_value: str) -> List[ElementHandle]:
        """
        使用 Name 选择器查找多个元素
        
        :param selector_value: Name 选择器值
        :return: 找到的元素列表
        :raises ElementNotFoundError: 当无法找到元素时
        :raises InvalidSelectorError: 当选择器无效时
        """
        try:
            # 验证选择器的基本语法
            if not selector_value or not isinstance(selector_value, str):
                raise InvalidSelectorError(selector_value, "Name 选择器必须是非空字符串")
            
            # 确保 Name 选择器以 '[name=""]' 格式
            if not selector_value.startswith('[name="') and not selector_value.startswith('name:'):
                selector_value = f'[name="{selector_value}"]'
            elif selector_value.startswith('name:'):
                selector_value = f'[name="{selector_value.split(":", 1)[1]}"]'
            
            self.logger.debug(f"Name 选择器查找多个元素 - 选择器: {selector_value}, 页面: {self.page}")
            
            elements = await self.page.query_selector_all(selector_value)
            
            if not elements:
                self.logger.warning(f"未找到匹配 Name 选择器的元素 - 选择器: {selector_value}")
                raise ElementNotFoundError(selector_value)
            
            self.logger.info(f"成功使用 Name 选择器找到 {len(elements)} 个元素 - 选择器: {selector_value}")
            return elements
        
        except InvalidSelectorError:
            raise
        
        except ElementNotFoundError:
            raise
        
        except Exception as e:
            self.logger.error(f"使用 Name 选择器查找多个元素时发生错误 - 选择器: {selector_value}, 错误: {e}")
            raise ElementNotFoundError(selector_value) from e 