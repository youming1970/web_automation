import pytest
from unittest.mock import AsyncMock, MagicMock
from playwright.async_api import Page, ElementHandle

from core.components.selector.selector_handlers.name_selector_handler import NameSelectorHandler
from core.components.selector.selector_handlers.base_selector_handler import ElementNotFoundError, InvalidSelectorError

@pytest.mark.asyncio
class TestNameSelectorHandler:
    @pytest.fixture(autouse=True)
    def setup_method(self):
        """
        为每个测试方法设置模拟的 Playwright Page 对象
        """
        self.mock_page = AsyncMock(spec=Page)
        self.name_selector_handler = NameSelectorHandler(self.mock_page)

    async def test_name_selector_handler_find_element(self):
        """
        测试使用 Name 选择器查找单个元素
        """
        mock_element = AsyncMock(spec=ElementHandle)
        self.mock_page.query_selector.return_value = mock_element

        result = await self.name_selector_handler.find_element('username')
        
        self.mock_page.query_selector.assert_called_once_with('[name="username"]')
        assert result == mock_element

    async def test_name_selector_handler_element_not_found(self):
        """
        测试使用 Name 选择器查找单个元素，但未找到
        """
        self.mock_page.query_selector.return_value = None

        with pytest.raises(ElementNotFoundError):
            await self.name_selector_handler.find_element('nonexistent_name')

    async def test_name_selector_handler_find_elements(self):
        """
        测试使用 Name 选择器查找多个元素
        """
        mock_elements = [AsyncMock(spec=ElementHandle), AsyncMock(spec=ElementHandle)]
        self.mock_page.query_selector_all.return_value = mock_elements

        result = await self.name_selector_handler.find_elements('input_fields')
        
        self.mock_page.query_selector_all.assert_called_once_with('[name="input_fields"]')
        assert result == mock_elements

    async def test_name_selector_handler_multiple_elements_not_found(self):
        """
        测试使用 Name 选择器查找多个元素，但未找到
        """
        self.mock_page.query_selector_all.return_value = []

        with pytest.raises(ElementNotFoundError):
            await self.name_selector_handler.find_elements('nonexistent_name')

    async def test_name_selector_handler_invalid_selector(self):
        """
        测试使用无效的 Name 选择器
        """
        with pytest.raises(InvalidSelectorError):
            await self.name_selector_handler.find_element('')

        with pytest.raises(InvalidSelectorError):
            await self.name_selector_handler.find_element(123)

    async def test_name_selector_handler_different_selector_formats(self):
        """
        测试不同格式的 Name 选择器
        """
        mock_element = AsyncMock(spec=ElementHandle)
        self.mock_page.query_selector.return_value = mock_element

        # 测试不同的选择器格式
        await self.name_selector_handler.find_element('username')  # 简单名称
        await self.name_selector_handler.find_element('[name="username"]')  # 完整 name 选择器
        await self.name_selector_handler.find_element('name:username')  # name: 前缀

        # 验证调用了正确的选择器
        assert self.mock_page.query_selector.call_count == 3
        calls = self.mock_page.query_selector.call_args_list
        assert calls[0][0][0] == '[name="username"]'
        assert calls[1][0][0] == '[name="username"]'
        assert calls[2][0][0] == '[name="username"]' 