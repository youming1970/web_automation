import pytest
from unittest.mock import AsyncMock, MagicMock
from playwright.async_api import Page, ElementHandle
from core.components.selector.selector_handlers.id_selector_handler import IDSelectorHandler
from core.components.selector.selector_handlers.name_selector_handler import NameSelectorHandler
from core.components.selector.selector_handlers.base_selector_handler import (
    ElementNotFoundError, 
    InvalidSelectorError
)
from core.components.selector.selector_handlers.class_selector_handler import ClassSelectorHandler

@pytest.fixture
def mock_page():
    """创建模拟的 Playwright Page 对象"""
    mock_page = MagicMock(spec=Page)
    
    # 创建模拟的 query_selector 和 query_selector_all 方法
    mock_page.query_selector = AsyncMock()
    mock_page.query_selector_all = AsyncMock()
    
    return mock_page

@pytest.mark.asyncio
async def test_id_selector_handler_find_element(mock_page):
    """测试 ID 选择器处理器查找单个元素"""
    # 模拟元素查找成功
    mock_element = MagicMock(spec=ElementHandle)
    mock_page.query_selector.return_value = mock_element
    
    id_handler = IDSelectorHandler(mock_page)
    
    # 测试带 '#' 的选择器
    element = await id_handler.find_element('#test-id')
    assert element == mock_element
    mock_page.query_selector.assert_called_once_with('#test-id')
    
    # 测试不带 '#' 的选择器
    mock_page.query_selector.reset_mock()
    element = await id_handler.find_element('test-id')
    assert element == mock_element
    mock_page.query_selector.assert_called_once_with('#test-id')

@pytest.mark.asyncio
async def test_id_selector_handler_element_not_found(mock_page):
    """测试 ID 选择器处理器找不到元素的情况"""
    # 模拟 query_selector 返回 None
    mock_page.query_selector.return_value = None
    
    id_handler = IDSelectorHandler(mock_page)
    
    with pytest.raises(ElementNotFoundError):
        await id_handler.find_element('test-id')

@pytest.mark.asyncio
async def test_id_selector_handler_find_elements(mock_page):
    """测试 ID 选择器处理器查找多个元素"""
    # 模拟多个元素查找成功
    mock_elements = [MagicMock(spec=ElementHandle), MagicMock(spec=ElementHandle)]
    mock_page.query_selector_all.return_value = mock_elements
    
    id_handler = IDSelectorHandler(mock_page)
    
    # 测试带 '#' 的选择器
    elements = await id_handler.find_elements('#test-ids')
    assert elements == mock_elements
    mock_page.query_selector_all.assert_called_once_with('#test-ids')
    
    # 测试不带 '#' 的选择器
    mock_page.query_selector_all.reset_mock()
    elements = await id_handler.find_elements('test-ids')
    assert elements == mock_elements
    mock_page.query_selector_all.assert_called_once_with('#test-ids')

@pytest.mark.asyncio
async def test_id_selector_handler_multiple_elements_not_found(mock_page):
    """测试 ID 选择器处理器找不到多个元素的情况"""
    # 模拟 query_selector_all 返回空列表
    mock_page.query_selector_all.return_value = []
    
    id_handler = IDSelectorHandler(mock_page)
    
    with pytest.raises(ElementNotFoundError):
        await id_handler.find_elements('test-ids')

@pytest.mark.parametrize("invalid_selector", [
    '',
    None,
    123  # 非字符串类型
])
@pytest.mark.asyncio
async def test_id_selector_handler_invalid_selector(mock_page, invalid_selector):
    """测试 ID 选择器处理器的无效选择器处理"""
    id_handler = IDSelectorHandler(mock_page)
    
    with pytest.raises(InvalidSelectorError):
        await id_handler.find_element(invalid_selector)
    
    with pytest.raises(InvalidSelectorError):
        await id_handler.find_elements(invalid_selector)

@pytest.mark.asyncio
async def test_name_selector_handler_find_element(mock_page):
    """测试 Name 选择器处理器的 find_element 方法"""
    # 模拟成功找到元素的场景
    mock_element = MagicMock(spec=ElementHandle)
    mock_page.query_selector.return_value = mock_element
    
    name_handler = NameSelectorHandler(mock_page)
    
    # 测试不同格式的 Name 选择器
    test_selectors = ['test-name', 'name:test-name', '[name="test-name"]']
    
    for selector in test_selectors:
        result = await name_handler.find_element(selector)
        assert result == mock_element
        
        # 根据不同的输入格式，验证正确的查询选择器
        if selector.startswith('name:'):
            mock_page.query_selector.assert_called_with('[name="test-name"]')
        elif not selector.startswith('[name='):
            mock_page.query_selector.assert_called_with('[name="test-name"]')

@pytest.mark.asyncio
async def test_name_selector_handler_find_elements(mock_page):
    """测试 Name 选择器处理器的 find_elements 方法"""
    # 模拟成功找到多个元素的场景
    mock_elements = [MagicMock(spec=ElementHandle), MagicMock(spec=ElementHandle)]
    mock_page.query_selector_all.return_value = mock_elements
    
    name_handler = NameSelectorHandler(mock_page)
    
    # 测试不同格式的 Name 选择器
    test_selectors = ['test-name', 'name:test-name', '[name="test-name"]']
    
    for selector in test_selectors:
        result = await name_handler.find_elements(selector)
        assert result == mock_elements
        
        # 根据不同的输入格式，验证正确的查询选择器
        if selector.startswith('name:'):
            mock_page.query_selector_all.assert_called_with('[name="test-name"]')
        elif not selector.startswith('[name='):
            mock_page.query_selector_all.assert_called_with('[name="test-name"]')

@pytest.mark.asyncio
async def test_name_selector_handler_element_not_found(mock_page):
    """测试 Name 选择器处理器找不到元素的情况"""
    mock_page.query_selector.return_value = None
    mock_page.query_selector_all.return_value = []
    
    name_handler = NameSelectorHandler(mock_page)
    
    # 测试 find_element
    with pytest.raises(ElementNotFoundError):
        await name_handler.find_element('non-existent-name')
    
    # 测试 find_elements
    with pytest.raises(ElementNotFoundError):
        await name_handler.find_elements('non-existent-name')

@pytest.mark.parametrize("invalid_selector", [
    '', 
    None, 
    123  # 非字符串类型
])
@pytest.mark.asyncio
async def test_name_selector_handler_invalid_selector(mock_page, invalid_selector):
    """测试 Name 选择器处理器的无效选择器处理"""
    name_handler = NameSelectorHandler(mock_page)
    
    with pytest.raises(InvalidSelectorError):
        await name_handler.find_element(invalid_selector)
    
    with pytest.raises(InvalidSelectorError):
        await name_handler.find_elements(invalid_selector)

# Class 选择器处理器测试
@pytest.mark.asyncio
async def test_class_selector_handler_find_element(mock_page):
    """测试 Class 选择器处理器的 find_element 方法"""
    # 模拟成功找到元素的场景
    mock_element = MagicMock(spec=ElementHandle)
    mock_page.query_selector.return_value = mock_element
    
    class_handler = ClassSelectorHandler(mock_page)
    
    # 测试不同格式的 Class 选择器
    test_selectors = ['test-class', 'class:test-class', '.test-class']
    
    for selector in test_selectors:
        result = await class_handler.find_element(selector)
        assert result == mock_element
        
        # 根据不同的输入格式，验证正确的查询选择器
        if selector.startswith('class:'):
            mock_page.query_selector.assert_called_with('.test-class')
        elif not selector.startswith('.'):
            mock_page.query_selector.assert_called_with('.test-class')

@pytest.mark.asyncio
async def test_class_selector_handler_find_elements(mock_page):
    """测试 Class 选择器处理器的 find_elements 方法"""
    # 模拟成功找到多个元素的场景
    mock_elements = [MagicMock(spec=ElementHandle), MagicMock(spec=ElementHandle)]
    mock_page.query_selector_all.return_value = mock_elements
    
    class_handler = ClassSelectorHandler(mock_page)
    
    # 测试不同格式的 Class 选择器
    test_selectors = ['test-class', 'class:test-class', '.test-class']
    
    for selector in test_selectors:
        result = await class_handler.find_elements(selector)
        assert result == mock_elements
        
        # 根据不同的输入格式，验证正确的查询选择器
        if selector.startswith('class:'):
            mock_page.query_selector_all.assert_called_with('.test-class')
        elif not selector.startswith('.'):
            mock_page.query_selector_all.assert_called_with('.test-class')

@pytest.mark.asyncio
async def test_class_selector_handler_element_not_found(mock_page):
    """测试 Class 选择器处理器找不到元素的情况"""
    mock_page.query_selector.return_value = None
    mock_page.query_selector_all.return_value = []
    
    class_handler = ClassSelectorHandler(mock_page)
    
    # 测试 find_element
    with pytest.raises(ElementNotFoundError):
        await class_handler.find_element('non-existent-class')
    
    # 测试 find_elements
    with pytest.raises(ElementNotFoundError):
        await class_handler.find_elements('non-existent-class')

@pytest.mark.parametrize("invalid_selector", [
    '', 
    None, 
    123  # 非字符串类型
])
@pytest.mark.asyncio
async def test_class_selector_handler_invalid_selector(mock_page, invalid_selector):
    """测试 Class 选择器处理器的无效选择器处理"""
    class_handler = ClassSelectorHandler(mock_page)
    
    with pytest.raises(InvalidSelectorError):
        await class_handler.find_element(invalid_selector)
    
    with pytest.raises(InvalidSelectorError):
        await class_handler.find_elements(invalid_selector) 