import pytest
import pytest_asyncio
from core.components.browser.browser_manager import BrowserManager
from playwright.async_api import Page
import asyncio

@pytest_asyncio.fixture
async def browser_manager():
    manager = BrowserManager()
    yield manager
    await manager.close()

@pytest.mark.asyncio
async def test_browser_initialization(browser_manager):
    """测试浏览器初始化"""
    await browser_manager.init()
    assert browser_manager.browser is not None
    
    # 测试创建上下文
    context = await browser_manager.create_context()
    assert context is not None
    assert browser_manager.context is not None
    
    # 测试关闭上下文
    await browser_manager.close_context()
    assert browser_manager.context is None

@pytest.mark.asyncio
async def test_page_creation(browser_manager):
    """测试页面创建"""
    # 创建页面
    page = await browser_manager.create_page()
    assert isinstance(page, Page)
    
    # 测试页面导航
    await browser_manager.navigate(page, "https://example.com")
    current_url = await page.evaluate("window.location.href")
    assert "example.com" in current_url
    
    # 关闭页面
    await page.close()

@pytest.mark.asyncio
async def test_anti_crawler_integration(browser_manager):
    """测试反爬虫集成"""
    # 创建页面（会自动应用User-Agent和代理）
    page = await browser_manager.create_page()
    
    # 验证User-Agent设置
    user_agent = browser_manager.get_current_user_agent()
    assert user_agent is not None
    
    # 验证代理设置（如果启用）
    if browser_manager.proxy_enabled:
        proxy = browser_manager.get_current_proxy()
        assert proxy is not None
        assert "server" in proxy
    
    await page.close()

@pytest.mark.asyncio
async def test_page_retry(browser_manager):
    """测试页面创建重试机制"""
    # 测试正常创建
    page = await browser_manager.new_page_with_retry()
    assert isinstance(page, Page)
    await page.close()
    
    # 测试重试失败
    browser_manager.browser = None  # 模拟浏览器未初始化
    with pytest.raises(Exception):
        await browser_manager.new_page_with_retry(max_retries=0)  # 不允许重试

@pytest.mark.asyncio
async def test_request_delay(browser_manager):
    """测试请求延迟机制"""
    page = await browser_manager.create_page()
    
    # 设置最小延迟时间
    browser_manager.anti_crawler.delay_config["min_delay"] = 0.5
    
    # 记录开始时间
    start_time = asyncio.get_event_loop().time()
    
    # 执行导航
    await browser_manager.navigate(page, "https://example.com")
    
    # 记录结束时间
    end_time = asyncio.get_event_loop().time()
    
    # 验证是否应用了延迟
    elapsed = end_time - start_time
    assert elapsed >= 0.5  # 使用设置的最小延迟时间
    
    await page.close()

@pytest.mark.asyncio
async def test_context_management(browser_manager):
    """测试上下文管理"""
    # 初始化浏览器
    await browser_manager.init()
    assert browser_manager.browser is not None
    
    # 创建上下文
    context = await browser_manager.create_context()
    assert context is not None
    
    # 创建页面
    page = await browser_manager.create_page()
    assert isinstance(page, Page)
    
    # 关闭浏览器
    await browser_manager.close()
    assert browser_manager.browser is None
    assert browser_manager.context is None

@pytest.mark.asyncio
async def test_screenshot(browser_manager):
    """测试截图功能"""
    import os
    
    page = await browser_manager.create_page()
    await browser_manager.navigate(page, "https://example.com")
    
    # 测试截图
    screenshot_path = "test_screenshot.png"
    await page.screenshot(path=screenshot_path)
    
    # 验证截图是否生成
    assert os.path.exists(screenshot_path)
    
    # 清理测试文件
    os.remove(screenshot_path)
    await page.close()

@pytest.mark.asyncio
async def test_page_content(browser_manager):
    """测试获取页面内容"""
    page = await browser_manager.create_page()
    await browser_manager.navigate(page, "https://example.com")
    
    # 获取页面内容
    content = await page.content()
    assert "Example Domain" in content
    
    await page.close()

@pytest.mark.asyncio
async def test_error_handling(browser_manager):
    """测试错误处理"""
    # 测试无效URL
    page = await browser_manager.create_page()
    with pytest.raises(Exception):
        await browser_manager.navigate(page, "invalid-url")
    
    # 测试超时
    with pytest.raises(Exception):
        await browser_manager.navigate(page, "https://example.com", timeout=1)
    
    await page.close() 