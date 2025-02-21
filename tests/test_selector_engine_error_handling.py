import pytest
import logging
from unittest.mock import patch, MagicMock, AsyncMock
from core.components.selector.selector_engine import SelectorEngine
from core.components.selector.selector_handlers.base_selector_handler import (
    InvalidSelectorError, 
    ElementNotFoundError
)
from core.components.selector.selector_handlers.css_selector_handler import CSSSelectorHandler
from core.components.selector.selector_handlers.xpath_selector_handler import XPathSelectorHandler
from playwright.async_api import Page, ElementHandle

@pytest.fixture
def mock_page():
    """创建模拟的 Playwright Page 对象"""
    mock_page = MagicMock(spec=Page)
    
    async def mock_locator(selector):
        mock_locator = MagicMock()
        
        # 模拟元素未找到的情况
        mock_first = MagicMock()
        mock_first.element_handle = AsyncMock(return_value=None)
        mock_locator.first = AsyncMock(return_value=mock_first)
        
        # 模拟空列表返回
        mock_locator.all_element_handles = AsyncMock(return_value=[])
        
        return mock_locator
    
    mock_page.locator = AsyncMock(side_effect=mock_locator)
    return mock_page

@pytest.fixture
def selector_engine(mock_page):
    """创建选择器引擎实例"""
    return SelectorEngine(page=mock_page)

# parse_selector 方法的扩展测试
@pytest.mark.parametrize("invalid_selector,expected_error_msg", [
    ('invalid:selector', '不支持的选择器类型'),
    ('unknown:test', '不支持的选择器类型'),
    ('', '选择器必须是非空字符串'),
    (None, '选择器必须是非空字符串'),
    ('css:invalid selector', '无效的 CSS 选择器'),
    ('xpath:invalid xpath', '无效的 XPath 选择器'),
    ('id:', '选择器值不能为空'),
    ('name:', '选择器值不能为空'),
    ('class:', '选择器值不能为空'),
])
def test_parse_selector_invalid_types(selector_engine, invalid_selector, expected_error_msg):
    """测试解析无效选择器类型"""
    try:
        if invalid_selector is None or invalid_selector == '':
            with pytest.raises(InvalidSelectorError) as excinfo:
                selector_engine.parse_selector(invalid_selector)
            assert '选择器必须是非空字符串' in str(excinfo.value)
        elif invalid_selector.endswith(':'):
            with pytest.raises(InvalidSelectorError) as excinfo:
                selector_engine.parse_selector(invalid_selector)
            assert '选择器值不能为空' in str(excinfo.value)
        else:
            with pytest.raises(InvalidSelectorError) as excinfo:
                selector_engine.parse_selector(invalid_selector)
            assert expected_error_msg in str(excinfo.value)
    except Exception as e:
        pytest.fail(f"测试失败：{e}")

# CSS 选择器处理器的错误处理测试
@pytest.mark.asyncio
async def test_css_selector_handler_element_not_found(mock_page):
    """测试 CSS 选择器处理器找不到元素的情况"""
    # 模拟 Playwright 的 query_selector 返回 None
    mock_page.query_selector.return_value = None
    
    css_handler = CSSSelectorHandler(mock_page)
    
    with pytest.raises(ElementNotFoundError) as excinfo:
        await css_handler.find_element('#non-existent')
    
    assert '#non-existent' in str(excinfo.value)

# XPath 选择器处理器的错误处理测试
@pytest.mark.asyncio
async def test_xpath_selector_handler_element_not_found(mock_page):
    """测试 XPath 选择器处理器找不到元素的情况"""
    # 模拟 Playwright 的 locator 返回空列表
    mock_page.locator.return_value.first.element_handle.return_value = None
    
    xpath_handler = XPathSelectorHandler(mock_page)
    
    with pytest.raises(ElementNotFoundError) as excinfo:
        await xpath_handler.find_element('//div[@class="non-existent"]')
    
    assert '//div[@class="non-existent"]' in str(excinfo.value)

# 日志记录测试
@pytest.mark.asyncio
@patch('logging.Logger.warning')
async def test_css_selector_handler_log_warning(mock_log_warning, mock_page):
    """测试 CSS 选择器处理器的警告日志"""
    mock_page.query_selector.return_value = None
    
    css_handler = CSSSelectorHandler(mock_page)
    
    with pytest.raises(ElementNotFoundError):
        await css_handler.find_element('#non-existent')
    
    mock_log_warning.assert_called_once()
    assert '未找到匹配 CSS 选择器的元素' in str(mock_log_warning.call_args[0][0])

@pytest.mark.asyncio
@patch('logging.Logger.warning')
async def test_xpath_selector_handler_log_warning(mock_log_warning, mock_page):
    """测试 XPath 选择器处理器的警告日志"""
    mock_page.locator.return_value.first.element_handle.return_value = None
    
    xpath_handler = XPathSelectorHandler(mock_page)
    
    with pytest.raises(ElementNotFoundError):
        await xpath_handler.find_element('//div[@class="non-existent"]')
    
    mock_log_warning.assert_called_once()
    assert '未找到匹配 XPath 选择器的元素' in str(mock_log_warning.call_args[0][0])

# 无效 XPath 选择器语法测试
@pytest.mark.parametrize("invalid_xpath", [
    'div[@class="test"]',  # 不以 // 或 ( 开头
    '',  # 空字符串
    None  # None 值
])
@pytest.mark.asyncio
async def test_xpath_selector_invalid_syntax(mock_page, invalid_xpath):
    """测试 XPath 选择器的语法验证"""
    xpath_handler = XPathSelectorHandler(mock_page)

    with pytest.raises(InvalidSelectorError) as excinfo:
        await xpath_handler.find_element(invalid_xpath)

    # 根据不同的输入，检查不同的错误消息
    if invalid_xpath is None or invalid_xpath == '':
        assert '选择器必须是非空字符串' in str(excinfo.value)
    else:
        assert '必须以 \'//\' 或 \'(\'' in str(excinfo.value)

# 边界情况测试：多个元素查找
@pytest.mark.asyncio
async def test_css_selector_handler_multiple_elements(mock_page):
    """测试 CSS 选择器处理器查找多个元素的情况"""
    # 模拟返回空列表
    mock_page.query_selector_all.return_value = []
    
    css_handler = CSSSelectorHandler(mock_page)
    
    with pytest.raises(ElementNotFoundError):
        await css_handler.find_elements('.non-existent-class')

@pytest.mark.asyncio
async def test_xpath_selector_handler_multiple_elements(mock_page):
    """测试 XPath 选择器处理器查找多个元素的情况"""
    # 模拟返回空列表
    mock_page.locator.return_value.all_element_handles.return_value = []
    
    xpath_handler = XPathSelectorHandler(mock_page)
    
    with pytest.raises(ElementNotFoundError):
        await xpath_handler.find_elements('//div[@class="non-existent"]')

# 新增的测试用例：parse_selector 方法的更多边界测试
@pytest.mark.parametrize("invalid_selector,expected_error_msg", [
    ('invalid:selector', '不支持的选择器类型'),
    ('unknown:test', '不支持的选择器类型'),
    ('', '选择器必须是非空字符串'),
    (None, '选择器必须是非空字符串'),
    ('css:invalid selector', '无效的 CSS 选择器'),
    ('xpath:invalid xpath', '无效的 XPath 选择器'),
    ('id:', '选择器值不能为空'),
    ('name:', '选择器值不能为空'),
    ('class:', '选择器值不能为空'),
])
def test_parse_selector_additional_invalid_types(selector_engine, invalid_selector, expected_error_msg):
    """测试解析更多无效选择器类型"""
    try:
        if invalid_selector is None or invalid_selector == '':
            with pytest.raises(InvalidSelectorError) as excinfo:
                selector_engine.parse_selector(invalid_selector)
            assert '选择器必须是非空字符串' in str(excinfo.value)
        elif invalid_selector.endswith(':'):
            with pytest.raises(InvalidSelectorError) as excinfo:
                selector_engine.parse_selector(invalid_selector)
            assert '选择器值不能为空' in str(excinfo.value)
        else:
            with pytest.raises(InvalidSelectorError) as excinfo:
                selector_engine.parse_selector(invalid_selector)
            assert expected_error_msg in str(excinfo.value)
    except Exception as e:
        pytest.fail(f"测试失败：{e}")

# 日志详细验证测试
@pytest.mark.asyncio
@patch('logging.Logger.debug')
@patch('logging.Logger.warning')
@patch('logging.Logger.error')
@patch('logging.Logger.info')
async def test_css_selector_handler_detailed_logging(
    mock_log_info, mock_log_error, mock_log_warning, mock_log_debug, mock_page
):
    """详细测试 CSS 选择器处理器的日志记录"""
    # 模拟查找元素失败的场景
    mock_page.query_selector.return_value = None
    
    css_handler = CSSSelectorHandler(mock_page)
    
    with pytest.raises(ElementNotFoundError):
        await css_handler.find_element('#non-existent')
    
    # 验证日志调用
    mock_log_debug.assert_called_once()
    mock_log_warning.assert_called_once()
    mock_log_info.assert_not_called()
    mock_log_error.assert_not_called()
    
    # 检查日志内容
    assert 'CSS 选择器查找单个元素' in mock_log_debug.call_args[0][0]
    assert '未找到匹配 CSS 选择器的元素' in mock_log_warning.call_args[0][0]

@pytest.mark.asyncio
@patch('logging.Logger.debug')
@patch('logging.Logger.warning')
@patch('logging.Logger.error')
@patch('logging.Logger.info')
async def test_xpath_selector_handler_detailed_logging(
    mock_log_info, mock_log_error, mock_log_warning, mock_log_debug, mock_page
):
    """详细测试 XPath 选择器处理器的日志记录"""
    # 模拟查找元素失败的场景
    mock_page.locator.return_value.first.element_handle.return_value = None
    
    xpath_handler = XPathSelectorHandler(mock_page)
    
    with pytest.raises(ElementNotFoundError):
        await xpath_handler.find_element('//div[@class="non-existent"]')
    
    # 验证日志调用
    mock_log_debug.assert_called_once()
    mock_log_warning.assert_called_once()
    mock_log_info.assert_not_called()
    mock_log_error.assert_not_called()
    
    # 检查日志内容
    assert 'XPath 选择器查找单个元素' in mock_log_debug.call_args[0][0]
    assert '未找到匹配 XPath 选择器的元素' in mock_log_warning.call_args[0][0]

# 异常处理边界测试
@pytest.mark.asyncio
async def test_css_selector_handler_extreme_edge_cases(mock_page):
    """测试 CSS 选择器处理器的极端边界情况"""
    css_handler = CSSSelectorHandler(mock_page)
    
    # 测试非常复杂或特殊的选择器
    complex_selectors = [
        'div[data-test="very-long-attribute-name-with-special-chars-@#$%^&*()"]',
        'input:not([type="text"])',
        'div > p + span',
        'div:nth-child(2n+1)'
    ]
    
    for selector in complex_selectors:
        mock_page.query_selector.return_value = None
        
        with pytest.raises(ElementNotFoundError):
            await css_handler.find_element(selector)

@pytest.mark.asyncio
async def test_xpath_selector_handler_extreme_edge_cases(mock_page):
    """测试 XPath 选择器处理器的极端边界情况"""
    xpath_handler = XPathSelectorHandler(mock_page)
    
    # 测试复杂的 XPath 选择器
    complex_selectors = [
        '//div[@data-test="very-long-attribute-name-with-special-chars-@#$%^&*()"]',
        '//input[not(@type="text")]',
        '//div/p[last()]',
        '//div[contains(@class, "test-class")]'
    ]
    
    for selector in complex_selectors:
        mock_page.locator.return_value.first.element_handle.return_value = None
        
        with pytest.raises(ElementNotFoundError):
            await xpath_handler.find_element(selector)

# 性能和异常处理测试
@pytest.mark.asyncio
async def test_selector_handlers_performance_and_error_handling(mock_page):
    """测试选择器处理器的性能和错误处理"""
    css_handler = CSSSelectorHandler(mock_page)
    xpath_handler = XPathSelectorHandler(mock_page)
    
    # 模拟大量查找操作
    for _ in range(100):
        mock_page.query_selector.return_value = None
        mock_page.locator.return_value.first.element_handle.return_value = None
        
        with pytest.raises(ElementNotFoundError):
            await css_handler.find_element('#repeated-non-existent')
        
        with pytest.raises(ElementNotFoundError):
            await xpath_handler.find_element('//div[@repeated="non-existent"]')

@pytest.mark.asyncio
async def test_find_element_not_found_css(selector_engine, mock_page):
    """
    测试 CSS 选择器在未找到元素时抛出 ElementNotFoundError
    """
    mock_page.query_selector.return_value = None  # 模拟 CSS 选择器未找到元素
    with pytest.raises(ElementNotFoundError):
        await selector_engine.find_element('css:div.nonexistent')

@pytest.mark.asyncio
async def test_find_element_not_found_xpath(selector_engine, mock_page):
    """测试 XPath 选择器在未找到元素时抛出 ElementNotFoundError"""
    with pytest.raises(ElementNotFoundError):
        await selector_engine.find_element('xpath://div[@class="nonexistent"]')

@pytest.mark.asyncio
async def test_find_element_not_found_id(selector_engine, mock_page):
    """
    测试 ID 选择器在未找到元素时抛出 ElementNotFoundError
    """
    mock_page.query_selector.return_value = None  # 模拟 ID 选择器未找到元素
    with pytest.raises(ElementNotFoundError):
        await selector_engine.find_element('id:nonexistent-id')

@pytest.mark.asyncio
async def test_find_element_not_found_name(selector_engine, mock_page):
    """
    测试 Name 选择器在未找到元素时抛出 ElementNotFoundError
    """
    mock_page.query_selector.return_value = None  # 模拟 Name 选择器未找到元素
    with pytest.raises(ElementNotFoundError):
        await selector_engine.find_element('name:nonexistent-name')

@pytest.mark.asyncio
async def test_find_element_not_found_class(selector_engine, mock_page):
    """
    测试 Class 选择器在未找到元素时抛出 ElementNotFoundError
    """
    mock_page.query_selector.return_value = None  # 模拟 Class 选择器未找到元素
    with pytest.raises(ElementNotFoundError):
        await selector_engine.find_element('class:nonexistent-class') 