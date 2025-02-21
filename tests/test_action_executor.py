import unittest
import asyncio
from core.components.action.action_executor import ActionExecutor
from core.components.browser.browser_manager import BrowserManager

class TestActionExecutor(unittest.TestCase):
    def setUp(self):
        """
        每个测试前初始化 ActionExecutor
        """
        self.browser_manager = BrowserManager(headless=True)
        self.action_executor = ActionExecutor(self.browser_manager)

    async def test_goto_action(self):
        """测试 goto 动作"""
        action = {
            'type': 'goto',
            'value': 'https://example.com'
        }
        
        result = await self.action_executor.execute_action(action)
        self.assertEqual(result['status'], 'success')
        self.assertTrue('https://example.com' in result['url'])

    async def test_input_action(self):
        """测试 input 动作"""
        workflow = [
            {'type': 'goto', 'value': 'https://example.com'},
            {'type': 'input', 'selector': 'id:search', 'value': 'test query'},
            {'type': 'input', 'selector': 'xpath://input[@name="q"]', 'value': 'xpath query'}
        ]
        
        results = await self.action_executor.execute_workflow(workflow)
        self.assertEqual(len(results), 3)
        self.assertEqual(results[0]['status'], 'success')
        self.assertEqual(results[1]['status'], 'success')
        self.assertEqual(results[2]['status'], 'success')

    async def test_click_action(self):
        """测试 click 动作"""
        workflow = [
            {'type': 'goto', 'value': 'https://example.com'},
            {'type': 'click', 'selector': 'class:submit-button'},
            {'type': 'click', 'selector': 'xpath://button[@type="submit"]'}
        ]
        
        results = await self.action_executor.execute_workflow(workflow)
        self.assertEqual(len(results), 3)
        self.assertEqual(results[0]['status'], 'success')
        self.assertEqual(results[1]['status'], 'success')
        self.assertEqual(results[2]['status'], 'success')

    def test_add_action_type(self):
        """测试添加新的动作类型"""
        original_actions = len(self.action_executor.supported_actions)
        self.action_executor.add_action_type('custom_action')
        self.assertEqual(len(self.action_executor.supported_actions), original_actions + 1)
        self.assertIn('custom_action', self.action_executor.supported_actions)

    async def test_unsupported_action(self):
        """测试不支持的动作类型"""
        action = {
            'type': 'unsupported_action',
            'value': 'test'
        }
        
        result = await self.action_executor.execute_action(action)
        self.assertEqual(result['status'], 'error')
        self.assertTrue('不支持的动作类型' in result['message'])

    def test_async_context_manager(self):
        """测试异步上下文管理器"""
        async def test_context():
            async with ActionExecutor() as executor:
                action = {'type': 'goto', 'value': 'https://example.com'}
                result = await executor.execute_action(action)
                self.assertEqual(result['status'], 'success')
        
        asyncio.run(test_context())

    def test_selector_parsing(self):
        """测试选择器解析"""
        selector_engine = self.action_executor.selector_engine
        
        # CSS 选择器
        css_selector = selector_engine.parse_selector('#test-id')
        self.assertEqual(css_selector['type'], 'css')
        self.assertEqual(css_selector['value'], '#test-id')
        
        # ID 选择器
        id_selector = selector_engine.parse_selector('id:test-id')
        self.assertEqual(id_selector['type'], 'id')
        self.assertEqual(id_selector['value'], '#test-id')
        
        # Name 选择器
        name_selector = selector_engine.parse_selector('name:username')
        self.assertEqual(name_selector['type'], 'name')
        self.assertEqual(name_selector['value'], '[name="username"]')
        
        # Class 选择器
        class_selector = selector_engine.parse_selector('class:btn-primary')
        self.assertEqual(class_selector['type'], 'class')
        self.assertEqual(class_selector['value'], '.btn-primary')
        
        # XPath 选择器
        xpath_selector = selector_engine.parse_selector('xpath://div[@class="example"]')
        self.assertEqual(xpath_selector['type'], 'xpath')
        self.assertEqual(xpath_selector['value'], '//div[@class="example"]')

    def test_anti_crawler_settings(self):
        """测试反爬虫设置"""
        # 禁用反爬虫策略
        executor_no_anti_crawler = ActionExecutor(anti_crawler_enabled=False)
        self.assertFalse(executor_no_anti_crawler.anti_crawler_enabled)
        
        # 自定义延迟
        executor_custom_delay = ActionExecutor(
            min_delay=0.5, 
            max_delay=1.5
        )
        self.assertEqual(executor_custom_delay.min_delay, 0.5)
        self.assertEqual(executor_custom_delay.max_delay, 1.5)
        
        # 测试随机 User-Agent
        user_agents = set()
        for _ in range(10):
            user_agent = executor_custom_delay.anti_crawler_manager.get_random_user_agent()
            user_agents.add(user_agent)
        
        # 确保有多个不同的 User-Agent
        self.assertTrue(len(user_agents) > 1)

    async def test_anti_crawler_workflow(self):
        """测试反爬虫策略的工作流"""
        import time
        
        start_time = time.time()
        workflow = [
            {'type': 'goto', 'value': 'https://example.com'},
            {'type': 'input', 'selector': 'id:search', 'value': 'test query'}
        ]
        
        # 使用较长的延迟以确保可测量
        executor = ActionExecutor(min_delay=1.0, max_delay=2.0)
        results = await executor.execute_workflow(workflow)
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        self.assertEqual(len(results), 2)
        self.assertTrue(execution_time >= 1.0)  # 确保有延迟
        for result in results:
            self.assertEqual(result['status'], 'success')

    def tearDown(self):
        """
        每个测试后关闭资源
        """
        async def close_resources():
            await self.action_executor.browser_manager.close()
        
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