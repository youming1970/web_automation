from typing import List, Dict, Any, Optional
from core.components.browser.browser_manager import BrowserManager
import json
import logging
import re
import asyncio
import random

class SelectorEngine:
    """
    选择器引擎，支持多种选择器类型
    """
    @staticmethod
    def parse_selector(selector: str) -> Dict[str, str]:
        """
        解析选择器字符串
        支持的格式：
        - css:#id
        - xpath://div[@class='example']
        - id:example
        - name:username
        - class:btn-primary
        
        :param selector: 选择器字符串
        :return: 解析后的选择器字典
        """
        selector_types = {
            'css': lambda s: s,
            'xpath': lambda s: s,
            'id': lambda s: f'#{s}',
            'name': lambda s: f'[name="{s}"]',
            'class': lambda s: f'.{s}'
        }
        
        # 默认使用 CSS 选择器
        if ':' not in selector:
            return {'type': 'css', 'value': selector}
        
        type_part, value_part = selector.split(':', 1)
        type_part = type_part.lower()
        
        if type_part not in selector_types:
            raise ValueError(f"不支持的选择器类型: {type_part}")
        
        return {
            'type': type_part,
            'value': selector_types[type_part](value_part)
        }

class AntiCrawlerManager:
    """
    反爬虫策略管理器
    """
    USER_AGENTS = [
        # Windows Chrome
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        
        # Windows Firefox
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
        
        # macOS Safari
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15",
        
        # macOS Chrome
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36",
        
        # Linux Chrome
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36"
    ]

    @classmethod
    def get_random_user_agent(cls) -> str:
        """
        获取随机 User-Agent
        
        :return: 随机 User-Agent 字符串
        """
        return random.choice(cls.USER_AGENTS)

    @staticmethod
    async def random_delay(min_delay: float = 1.0, max_delay: float = 3.0):
        """
        随机延迟
        
        :param min_delay: 最小延迟时间（秒）
        :param max_delay: 最大延迟时间（秒）
        """
        delay = random.uniform(min_delay, max_delay)
        await asyncio.sleep(delay)

class ActionExecutor:
    def __init__(self, 
                 browser_manager: Optional[BrowserManager] = None, 
                 anti_crawler_enabled: bool = True,
                 min_delay: float = 1.0, 
                 max_delay: float = 3.0):
        """
        初始化动作执行器
        
        :param browser_manager: 可选的浏览器管理器实例
        :param anti_crawler_enabled: 是否启用反爬虫策略
        :param min_delay: 最小请求延迟
        :param max_delay: 最大请求延迟
        """
        self.browser_manager = browser_manager or BrowserManager()
        self.logger = logging.getLogger(__name__)
        logging.basicConfig(level=logging.INFO)
        
        # 反爬虫配置
        self.anti_crawler_enabled = anti_crawler_enabled
        self.min_delay = min_delay
        self.max_delay = max_delay
        
        # 支持的动作类型
        self.supported_actions = [
            'goto', 'click', 'input', 'select', 
            'radio', 'checkbox', 'wait'
        ]
        
        # 选择器引擎
        self.selector_engine = SelectorEngine()
        self.anti_crawler_manager = AntiCrawlerManager()

    async def execute_action(self, action: Dict[str, Any], page=None) -> Dict[str, Any]:
        """
        执行单个动作
        
        :param action: 动作配置字典
        :param page: 可选的浏览器页面对象
        :return: 动作执行结果
        """
        # 反爬虫策略：随机延迟
        if self.anti_crawler_enabled:
            await self.anti_crawler_manager.random_delay(
                self.min_delay, 
                self.max_delay
            )
        
        action_type = action.get('type')
        selector_str = action.get('selector')
        value = action.get('value')
        
        # 如果没有提供页面，创建新页面
        if page is None:
            await self.browser_manager.launch()
            await self.browser_manager.create_context()
            page = await self.browser_manager.new_page()
            
            # 反爬虫策略：随机 User-Agent
            if self.anti_crawler_enabled:
                user_agent = self.anti_crawler_manager.get_random_user_agent()
                await page.context.set_extra_http_headers({
                    'User-Agent': user_agent
                })
        
        try:
            # 解析选择器
            if selector_str:
                selector_info = self.selector_engine.parse_selector(selector_str)
                selector = selector_info['value']
                selector_type = selector_info['type']
            else:
                selector = None
                selector_type = None
            
            if action_type == 'goto':
                await page.goto(value)
                return {
                    "status": "success", 
                    "message": f"跳转到 {value}", 
                    "url": page.url
                }
            
            elif action_type == 'click':
                if selector_type == 'xpath':
                    await page.click(f'xpath:{selector}')
                else:
                    await page.click(selector)
                return {
                    "status": "success", 
                    "message": f"点击 {selector}"
                }
            
            elif action_type == 'input':
                if selector_type == 'xpath':
                    await page.fill(f'xpath:{selector}', value)
                else:
                    await page.fill(selector, value)
                return {
                    "status": "success", 
                    "message": f"在 {selector} 输入 {value}"
                }
            
            elif action_type == 'select':
                if selector_type == 'xpath':
                    await page.select_option(f'xpath:{selector}', value)
                else:
                    await page.select_option(selector, value)
                return {
                    "status": "success", 
                    "message": f"在 {selector} 选择 {value}"
                }
            
            elif action_type == 'radio':
                if selector_type == 'xpath':
                    await page.check(f'xpath:{selector}')
                else:
                    await page.check(selector)
                return {
                    "status": "success", 
                    "message": f"选择单选框 {selector}"
                }
            
            elif action_type == 'checkbox':
                if selector_type == 'xpath':
                    await page.check(f'xpath:{selector}')
                else:
                    await page.check(selector)
                return {
                    "status": "success", 
                    "message": f"选择复选框 {selector}"
                }
            
            elif action_type == 'wait':
                if selector_type == 'xpath':
                    await page.wait_for_selector(f'xpath:{selector}', state='visible')
                else:
                    await page.wait_for_selector(selector, state='visible')
                return {
                    "status": "success", 
                    "message": f"等待 {selector} 可见"
                }
            
            else:
                raise ValueError(f"不支持的动作类型: {action_type}")
        
        except Exception as e:
            self.logger.error(f"执行动作 {action_type} 时发生错误: {e}")
            return {
                "status": "error", 
                "message": str(e)
            }

    async def execute_workflow(self, workflow: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        执行完整的工作流
        
        :param workflow: 工作流动作列表
        :return: 工作流执行结果列表
        """
        results = []
        
        try:
            await self.browser_manager.launch()
            await self.browser_manager.create_context()
            page = await self.browser_manager.new_page()
            
            for action in workflow:
                result = await self.execute_action(action, page)
                results.append(result)
                
                # 如果某个动作执行失败，停止工作流
                if result['status'] == 'error':
                    break
        
        except Exception as e:
            self.logger.error(f"执行工作流时发生错误: {e}")
            results.append({
                "status": "error", 
                "message": str(e)
            })
        
        finally:
            await self.browser_manager.close()
        
        return results

    def add_action_type(self, action_type: str):
        """
        添加新的动作类型
        
        :param action_type: 新的动作类型
        """
        if action_type not in self.supported_actions:
            self.supported_actions.append(action_type)
            self.logger.info(f"添加新的动作类型: {action_type}")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        async def close_resources():
            await self.browser_manager.close()
        
        import asyncio
        asyncio.run(close_resources())

    async def __aenter__(self):
        """
        异步上下文管理器入口
        """
        await self.browser_manager.launch()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """
        异步上下文管理器出口
        """
        await self.browser_manager.close()
