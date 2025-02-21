import unittest
import asyncio
from database.crud_manager import CRUDManager
from core.components.action.action_executor import ActionExecutor

class TestWorkflow(unittest.TestCase):
    def setUp(self):
        """
        初始化测试资源
        """
        self.crud = CRUDManager()
        self.action_executor = ActionExecutor()

    async def test_simple_workflow(self):
        """
        测试简单的工作流执行
        """
        # 创建测试网站
        website = self.crud.create_website(
            name='测试网站', 
            url='https://example.com'
        )
        
        # 创建测试用户
        user = self.crud.create_user(
            username='workflow_tester', 
            email='tester@example.com', 
            password_hash='hashed_password'
        )
        
        # 创建工作流
        workflow_data = self.crud.create_workflow(
            name='简单测试工作流', 
            user_id=user['id'], 
            website_id=website['id']
        )
        
        # 添加工作流步骤
        workflow_steps = [
            self.crud.add_workflow_step(
                workflow_id=workflow_data['id'], 
                step_order=1, 
                action_type='goto', 
                value=website['url']
            ),
            self.crud.add_workflow_step(
                workflow_id=workflow_data['id'], 
                step_order=2, 
                action_type='input', 
                selector='#search', 
                value='测试查询'
            )
        ]
        
        # 获取工作流步骤
        steps = self.crud.get_workflow_steps(workflow_data['id'])
        
        # 转换为动作执行器可用的格式
        workflow_actions = [
            {'type': step['action_type'], 
             'value': step['value'], 
             'selector': step['selector_id']} 
            for step in steps
        ]
        
        # 执行工作流
        results = await self.action_executor.execute_workflow(workflow_actions)
        
        # 验证工作流执行结果
        self.assertEqual(len(results), len(workflow_actions))
        for result in results:
            self.assertEqual(result['status'], 'success')

    def tearDown(self):
        """
        清理测试资源
        """
        async def close_resources():
            await self.action_executor.browser_manager.close()
            self.crud.close()
        
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