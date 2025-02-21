import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock
from playwright.async_api import Page, ElementHandle

from core.components.selector.selector_engine import SelectorEngine
from core.components.selector.selector_handlers.base_selector_handler import ElementNotFoundError, InvalidSelectorError

class TestSelectorEngine:
    @pytest.fixture(autouse=True)
    def setup(self, mock_page):
        """
        设置测试环境
        """
        self.mock_page = mock_page
        self.selector_engine = SelectorEngine(self.mock_page)

    @pytest.fixture
    def mock_page(self):
        """创建模拟的 Playwright Page 对象"""
        mock_page = MagicMock(spec=Page)
        
        async def mock_locator(selector):
            # 创建完整的层级结构
            mock_locator = MagicMock()
            mock_element = MagicMock(spec=ElementHandle)
            
            # 正确设置 first 属性和 element_handle 方法
            mock_first = MagicMock()
            mock_first.element_handle = AsyncMock(return_value=mock_element)
            mock_locator.first = AsyncMock(return_value=mock_first)
            
            # 设置 all_element_handles 方法
            mock_locator.all_element_handles = AsyncMock(return_value=[mock_element])
            
            return mock_locator
        
        mock_page.locator = AsyncMock(side_effect=mock_locator)
        return mock_page

    def test_parse_selector(self):
        """
        测试选择器解析方法
        """
        # CSS 选择器
        assert SelectorEngine.parse_selector('div.test') == ('css', 'div.test')
        assert SelectorEngine.parse_selector('css:div.test') == ('css', 'div.test')

        # XPath 选择器
        assert SelectorEngine.parse_selector('xpath://div[@class="test"]') == ('xpath', '//div[@class="test"]')

        # ID 选择器
        assert SelectorEngine.parse_selector('id:test-id') == ('id', 'test-id')
        assert SelectorEngine.parse_selector('#test-id') == ('id', 'test-id')

        # Name 选择器
        assert SelectorEngine.parse_selector('name:username') == ('name', 'username')
        assert SelectorEngine.parse_selector('[name="username"]') == ('name', 'username')

    @pytest.mark.asyncio
    async def test_find_element(self):
        """
        测试使用不同选择器类型查找单个元素
        """
        mock_element = MagicMock(spec=ElementHandle)
        
        # XPath 选择器测试
        mock_locator = MagicMock()
        mock_first = MagicMock()
        mock_first.element_handle = AsyncMock(return_value=mock_element)
        mock_locator.first = AsyncMock(return_value=mock_first)
        self.mock_page.locator = AsyncMock(return_value=mock_locator)
        
        result = await self.selector_engine.find_element('xpath://div[@class="test"]')
        assert result == mock_element

        # CSS 选择器
        self.mock_page.query_selector = AsyncMock(return_value=mock_element)
        result = await self.selector_engine.find_element('div.test')
        assert result == mock_element

        # ID 选择器
        self.mock_page.query_selector = AsyncMock(return_value=mock_element)
        result = await self.selector_engine.find_element('#test-id')
        assert result == mock_element

        # Name 选择器
        self.mock_page.query_selector = AsyncMock(return_value=mock_element)
        result = await self.selector_engine.find_element('name:username')
        assert result == mock_element

        # Class 选择器
        self.mock_page.query_selector = AsyncMock(return_value=mock_element)
        result = await self.selector_engine.find_element('.test-class')
        assert result == mock_element

    @pytest.mark.asyncio
    async def test_find_elements(self):
        """
        测试使用不同选择器类型查找多个元素
        """
        mock_elements = [AsyncMock(spec=ElementHandle), AsyncMock(spec=ElementHandle)]

        # CSS 选择器
        self.mock_page.query_selector_all = AsyncMock(return_value=mock_elements)
        result = await self.selector_engine.find_elements('div.test')
        assert result == mock_elements

        # XPath 选择器
        mock_locator = AsyncMock()
        mock_locator.all_element_handles = AsyncMock(return_value=mock_elements)
        self.mock_page.locator = AsyncMock(return_value=mock_locator)
        result = await self.selector_engine.find_elements('xpath://div[@class="test"]')
        assert result == mock_elements

        # ID 选择器
        self.mock_page.query_selector_all = AsyncMock(return_value=mock_elements)
        result = await self.selector_engine.find_elements('#test-id')
        assert result == mock_elements

        # Name 选择器
        self.mock_page.query_selector_all = AsyncMock(return_value=mock_elements)
        result = await self.selector_engine.find_elements('name:username')
        assert result == mock_elements

        # Class 选择器
        self.mock_page.query_selector_all = AsyncMock(return_value=mock_elements)
        result = await self.selector_engine.find_elements('.test-class')
        assert result == mock_elements

    @pytest.mark.asyncio
    async def test_unsupported_selector(self):
        """
        测试不支持的选择器类型
        """
        with pytest.raises(InvalidSelectorError):
            await self.selector_engine.find_element('invalid:selector')

        with pytest.raises(InvalidSelectorError):
            await self.selector_engine.find_elements('invalid:selector')

    @pytest.mark.asyncio
    async def test_element_not_found(self):
        """
        测试查找不存在的元素
        """
        self.mock_page.query_selector.return_value = None
        self.mock_page.query_selector_all.return_value = []

        with pytest.raises(ElementNotFoundError):
            await self.selector_engine.find_element('div.nonexistent')

        with pytest.raises(ElementNotFoundError):
            await self.selector_engine.find_elements('div.nonexistent') 