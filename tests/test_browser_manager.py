import unittest
import asyncio
from core.components.browser.browser_manager import BrowserManager, ProxyManager

class TestBrowserManager(unittest.TestCase):
    def setUp(self):
        """
        每个测试前初始化 BrowserManager
        """
        self.browser_manager = BrowserManager(headless=True)

    def test_proxy_manager(self):
        """测试代理管理器"""
        # 测试随机代理获取
        proxy = ProxyManager.get_random_proxy()
        self.assertIsNotNone(proxy)
        self.assertIn('server', proxy)
        self.assertIn('bypass', proxy)
        
        # 测试代理验证
        self.assertTrue(ProxyManager.validate_proxy(proxy))

    async def test_proxy_launch(self):
        """测试使用代理启动浏览器"""
        # 启用代理
        browser_manager_with_proxy = BrowserManager(
            headless=True, 
            proxy_enabled=True
        )
        
        try:
            browser = await browser_manager_with_proxy.launch()
            self.assertIsNotNone(browser)
        finally:
            await browser_manager_with_proxy.close()

    async def test_custom_proxy(self):
        """测试自定义代理"""
        custom_proxy = {
            "server": "http://custom-proxy.example.com:8080",
            "bypass": "localhost,127.0.0.1"
        }
        
        browser_manager_custom_proxy = BrowserManager(
            headless=True, 
            proxy_enabled=True,
            proxy=custom_proxy
        )
        
        try:
            browser = await browser_manager_custom_proxy.launch()
            self.assertIsNotNone(browser)
            
            # 验证使用了自定义代理
            self.assertEqual(
                browser_manager_custom_proxy.custom_proxy, 
                custom_proxy
            )
        finally:
            await browser_manager_custom_proxy.close()

    async def test_proxy_context(self):
        """测试代理上下文"""
        browser_manager_proxy = BrowserManager(
            headless=True, 
            proxy_enabled=True
        )
        
        try:
            await browser_manager_proxy.launch()
            context = await browser_manager_proxy.create_context()
            self.assertIsNotNone(context)
        finally:
            await browser_manager_proxy.close()

    async def test_browser_launch(self):
        """测试浏览器启动"""
        try:
            browser = await self.browser_manager.launch()
            self.assertIsNotNone(browser)
        finally:
            await self.browser_manager.close()

    async def test_create_context(self):
        """测试创建浏览器上下文"""
        try:
            await self.browser_manager.launch()
            context = await self.browser_manager.create_context(
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                viewport={'width': 1280, 'height': 720}
            )
            self.assertIsNotNone(context)
        finally:
            await self.browser_manager.close()

    async def test_new_page(self):
        """测试创建新页面"""
        try:
            await self.browser_manager.launch()
            await self.browser_manager.create_context()
            page = await self.browser_manager.new_page('https://example.com')
            self.assertIsNotNone(page)
            
            # 验证页面是否成功加载
            title = await page.title()
            self.assertIsNotNone(title)
        finally:
            await self.browser_manager.close()

    async def test_screenshot(self):
        """测试页面截图"""
        try:
            await self.browser_manager.launch()
            await self.browser_manager.create_context()
            page = await self.browser_manager.new_page('https://example.com')
            
            screenshot_path = await self.browser_manager.take_screenshot('test_screenshot.png')
            self.assertTrue(screenshot_path.endswith('test_screenshot.png'))
        finally:
            await self.browser_manager.close()

    def test_browser_manager_async_context(self):
        """测试异步上下文管理器"""
        async def test_context():
            async with BrowserManager(headless=True) as browser_manager:
                page = await browser_manager.new_page('https://example.com')
                title = await page.title()
                self.assertIsNotNone(title)
        
        asyncio.run(test_context())

    def tearDown(self):
        """
        每个测试后关闭浏览器资源
        """
        async def close_resources():
            await self.browser_manager.close()
        
        asyncio.run(close_resources())

def run_async_tests(test_case):
    """
    运行异步测试的辅助函数
    """
    loop = asyncio.get_event_loop()
    test_methods = [method for method in dir(test_case) 
                    if method.startswith('test_') and asyncio.iscoroutinefunction(getattr(test_case, method))]
    
    for method_name in test_methods:
        method = getattr(test_case, method_name)
        loop.run_until_complete(method)

if __name__ == '__main__':
    unittest.main() 