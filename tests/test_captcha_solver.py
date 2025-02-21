import unittest
import asyncio
import os
import base64
from core.components.captcha.captcha_solver import CaptchaSolver, TwoCaptchaSolver, AntiCaptchaManager

class TestCaptchaSolver(unittest.TestCase):
    def setUp(self):
        """
        初始化测试环境
        """
        # 注意：实际测试需要替换为真实的 API Key
        self.api_key = os.environ.get('TWO_CAPTCHA_API_KEY', 'test_api_key')
        self.anti_captcha_manager = AntiCaptchaManager(
            solver_type='2captcha', 
            api_key=self.api_key
        )

    def test_base_captcha_solver(self):
        """测试基础验证码解决器"""
        with self.assertRaises(NotImplementedError):
            async def test():
                solver = CaptchaSolver()
                await solver._solve_captcha('base64_image')
            
            asyncio.run(test())

    def test_anti_captcha_manager_initialization(self):
        """测试验证码管理器初始化"""
        # 测试默认初始化
        manager = AntiCaptchaManager(api_key=self.api_key)
        self.assertEqual(manager.solver_type, '2captcha')
        
        # 测试不支持的服务类型
        with self.assertRaises(ValueError):
            AntiCaptchaManager(solver_type='unsupported_service')

    def test_two_captcha_solver_validation(self):
        """测试 2Captcha 验证码解决器的验证"""
        # 测试未提供 API Key
        with self.assertRaises(ValueError):
            async def test():
                solver = TwoCaptchaSolver()
                await solver._solve_captcha('base64_image')
            
            asyncio.run(test())

    async def test_solve_image_captcha_base64(self):
        """
        测试 Base64 图像验证码识别
        注意：这是一个模拟测试，实际需要真实的验证码图像和有效的 API Key
        """
        # 创建一个简单的 Base64 编码图像
        test_image_base64 = base64.b64encode(b'test_image_data').decode('utf-8')
        
        # 模拟验证码识别
        result = await self.anti_captcha_manager.solve_captcha(image_base64=test_image_base64)
        
        # 验证结果结构
        self.assertIn('status', result)
        self.assertIn('text', result)
        self.assertIn('confidence', result)

    def test_solve_image_captcha_file(self):
        """
        测试文件路径验证码识别
        注意：需要在测试目录准备一个测试验证码图像
        """
        async def test_file_captcha():
            # 假设有一个测试验证码图像
            test_image_path = 'test_captcha.png'
            
            # 如果测试图像不存在，跳过测试
            if not os.path.exists(test_image_path):
                self.skipTest("测试验证码图像不存在")
            
            result = await self.anti_captcha_manager.solve_captcha(image_path=test_image_path)
            
            # 验证结果结构
            self.assertIn('status', result)
            self.assertIn('text', result)
            self.assertIn('confidence', result)
        
        # 运行异步测试
        asyncio.run(test_file_captcha())

    def test_invalid_captcha_input(self):
        """测试无效的验证码输入"""
        async def test_invalid_input():
            with self.assertRaises(ValueError):
                await self.anti_captcha_manager.solve_captcha()
        
        asyncio.run(test_invalid_input())

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

 