from typing import Optional, Dict, Any
from playwright.async_api import async_playwright, Browser, Page, BrowserContext
import asyncio
import logging
import random
from core.components.anti_crawler.anti_crawler_manager import AntiCrawlerManager

class ProxyManager:
    """
    代理管理器
    """
    DEFAULT_PROXIES = [
        # 免费代理示例（仅用于演示，实际使用需要可靠的代理服务）
        {"server": "http://104.236.45.251:8080"},
        {"server": "http://167.71.5.83:8080"},
        {"server": "http://138.197.102.119:80"},
        {"server": "http://45.55.196.74:8080"}
    ]

    @classmethod
    def get_random_proxy(cls, protocol: str = 'http') -> Optional[Dict[str, str]]:
        """
        获取随机代理
        
        :param protocol: 代理协议（http/https）
        :return: 代理配置字典
        """
        if not cls.DEFAULT_PROXIES:
            return None
        
        proxy = random.choice(cls.DEFAULT_PROXIES)
        return {
            "server": proxy['server'],
            "bypass": "localhost,127.0.0.1"
        }

    @classmethod
    def validate_proxy(cls, proxy: Dict[str, str]) -> bool:
        """
        验证代理是否可用
        
        :param proxy: 代理配置
        :return: 是否可用
        """
        # TODO: 实现实际的代理验证逻辑
        return True

class BrowserManager:
    """浏览器管理器"""

    def __init__(self, headless: bool = True, browser_type: str = 'chromium'):
        """
        初始化浏览器管理器
        
        :param headless: 是否使用无头模式
        :param browser_type: 浏览器类型（chromium/firefox/webkit）
        """
        self.browser = None
        self.context = None
        self.anti_crawler = AntiCrawlerManager()
        self.headless = headless
        self.browser_type = browser_type
        self.proxy_enabled = False
        self.custom_proxy = None
        self.proxy_manager = None
        self.logger = logging.getLogger(__name__)
        
        # 配置日志
        self.logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        ))
        self.logger.addHandler(handler)

    async def init(self):
        """初始化浏览器"""
        if not self.browser:
            try:
                self.playwright = await async_playwright().start()
                self.browser = await self.playwright.chromium.launch(headless=self.headless)
                self.logger.info(f"已启动 {self.browser_type} 浏览器")
            except Exception as e:
                self.logger.error(f"初始化浏览器失败: {e}")
                raise

    async def create_context(self, user_agent: Optional[str] = None, viewport: Optional[Dict[str, int]] = None):
        """
        创建浏览器上下文
        
        :param user_agent: 自定义用户代理
        :param viewport: 视窗大小
        :return: 浏览器上下文
        """
        if not self.browser:
            await self.init()
            
        try:
            # 获取随机 User-Agent
            self.current_user_agent = user_agent or self.anti_crawler.get_random_user_agent()
            
            # 获取随机代理
            proxy = None
            if self.proxy_enabled:
                proxy = self.custom_proxy or self.anti_crawler.get_random_proxy()
            
            # 创建上下文
            context_options = {
                'user_agent': self.current_user_agent
            }
            
            if viewport:
                context_options['viewport'] = viewport
                
            if proxy:
                context_options['proxy'] = proxy
                self.logger.info(f"使用代理: {proxy.get('server', '')}")
            
            self.context = await self.browser.new_context(**context_options)
            self.logger.info("创建新的浏览器上下文")
            return self.context
            
        except Exception as e:
            self.logger.error(f"创建浏览器上下文失败: {e}")
            raise

    async def create_page(self) -> Page:
        """创建新页面"""
        if not self.context:
            await self.create_context()
            
        try:
            page = await self.context.new_page()
            self.logger.info("创建新页面")
            return page
        except Exception as e:
            self.logger.error(f"创建页面失败: {e}")
            raise

    async def _setup_request_handlers(self, page: Page):
        """设置请求处理器"""
        async def handle_request(request):
            # 检查是否需要延迟
            if self.anti_crawler.should_delay():
                delay = self.anti_crawler.get_delay_time()
                await asyncio.sleep(delay)
            
            # 更新最后请求时间
            self.anti_crawler.update_last_request_time()
            
            # 继续请求
            await request.continue_()
            
        # 启用请求拦截
        await page.route("**/*", handle_request)

    async def close_context(self):
        """关闭当前上下文"""
        if self.context:
            await self.context.close()
            self.context = None

    async def close(self):
        """关闭浏览器"""
        try:
            if self.context:
                await self.close_context()
            if self.browser:
                await self.browser.close()
                self.browser = None
                self.logger.info("关闭浏览器")
        except Exception as e:
            self.logger.error(f"关闭浏览器失败: {e}")
            raise

    async def new_page_with_retry(self, max_retries: int = 3) -> Optional[Page]:
        """创建新页面（带重试）"""
        if not self.browser:
            if max_retries <= 0:
                raise Exception("浏览器未初始化且不允许重试")
            try:
                await self.init()
            except Exception as e:
                self.logger.error(f"初始化浏览器失败: {e}")
                raise
        
        for attempt in range(max_retries):
            try:
                return await self.create_page()
            except Exception as e:
                if attempt == max_retries - 1:
                    raise
                self.logger.warning(f"创建页面失败，尝试重试: {e}")
                await asyncio.sleep(1)
                await self.close_context()  # 关闭当前上下文，使用新的代理重试

    async def navigate(self, page: Page, url: str, timeout: int = 30000):
        """
        导航到指定URL
        
        :param page: 页面对象
        :param url: 目标URL
        :param timeout: 超时时间（毫秒）
        """
        try:
            # 应用延迟
            if self.anti_crawler.should_delay():
                delay = self.anti_crawler.get_delay_time()
                await asyncio.sleep(delay)
                self.logger.info(f"应用延迟: {delay}秒")
            
            # 更新最后请求时间
            self.anti_crawler.update_last_request_time()
            
            # 执行导航
            self.logger.info(f"导航到: {url}")
            await page.goto(url, timeout=timeout)
            
        except Exception as e:
            self.logger.error(f"导航失败: {e}")
            raise

    def get_current_user_agent(self) -> str:
        """获取当前使用的 User-Agent"""
        if not self.context:
            return None
        return self.current_user_agent

    def get_current_proxy(self) -> Optional[Dict[str, str]]:
        """获取当前使用的代理"""
        return self.context.proxy if self.context else None

    async def launch(self, proxy: Optional[Dict[str, str]] = None) -> Browser:
        """
        启动浏览器
        
        :param proxy: 可选的代理服务器配置
        :return: Playwright 浏览器对象
        """
        try:
            self.playwright = await async_playwright().start()
            
            browser_launch_options = {
                'headless': self.headless
            }
            
            # 处理代理配置
            if self.proxy_enabled:
                if self.custom_proxy:
                    proxy = self.custom_proxy
                else:
                    proxy = self.proxy_manager.get_random_proxy()
                
                if proxy and self.proxy_manager.validate_proxy(proxy):
                    browser_launch_options['proxy'] = proxy
                    self.logger.info(f"使用代理: {proxy['server']}")
            
            if self.browser_type == 'chromium':
                self.browser = await self.playwright.chromium.launch(**browser_launch_options)
            elif self.browser_type == 'firefox':
                self.browser = await self.playwright.firefox.launch(**browser_launch_options)
            elif self.browser_type == 'webkit':
                self.browser = await self.playwright.webkit.launch(**browser_launch_options)
            else:
                raise ValueError(f"不支持的浏览器类型: {self.browser_type}")
            
            self.logger.info(f"已启动 {self.browser_type} 浏览器")
            return self.browser
        
        except Exception as e:
            self.logger.error(f"启动浏览器失败: {e}")
            raise

    async def new_page(self, url: Optional[str] = None) -> Page:
        """
        创建新页面
        
        :param url: 可选的初始 URL
        :return: Playwright 页面对象
        """
        if not self.context:
            await self.create_context()
        
        self.page = await self.context.new_page()
        
        if url:
            await self.page.goto(url)
        
        self.logger.info(f"创建新页面 {f'并导航到 {url}' if url else ''}")
        return self.page

    async def __aenter__(self):
        """
        异步上下文管理器入口
        """
        await self.launch()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """
        异步上下文管理器出口
        """
        await self.close()

    # 辅助方法
    async def take_screenshot(self, path: str = 'screenshot.png') -> str:
        """
        对当前页面截图
        
        :param path: 保存路径
        :return: 截图保存路径
        """
        if not self.page:
            raise RuntimeError("未创建页面")
        
        await self.page.screenshot(path=path)
        self.logger.info(f"页面截图已保存到 {path}")
        return path

    async def get_page_source(self) -> str:
        """
        获取当前页面源代码
        
        :return: 页面 HTML 源代码
        """
        if not self.page:
            raise RuntimeError("未创建页面")
        
        return await self.page.content()
