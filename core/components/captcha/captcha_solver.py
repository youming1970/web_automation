import base64
import logging
import aiohttp
import asyncio
from typing import Optional, Dict, Any

class CaptchaSolver:
    """
    验证码识别服务基类
    提供不同验证码识别服务的统一接口
    """
    def __init__(self, api_key: Optional[str] = None):
        """
        初始化验证码识别服务
        
        :param api_key: 第三方验证码识别服务的 API Key
        """
        self.api_key = api_key
        self.logger = logging.getLogger(__name__)
        logging.basicConfig(level=logging.INFO)

    async def solve_image_captcha(self, 
                                  image_path: Optional[str] = None, 
                                  image_base64: Optional[str] = None) -> Dict[str, Any]:
        """
        识别图像验证码
        
        :param image_path: 验证码图像文件路径
        :param image_base64: Base64 编码的验证码图像
        :return: 验证码识别结果
        """
        if not image_path and not image_base64:
            raise ValueError("必须提供图像路径或 Base64 编码")
        
        try:
            # 如果提供了文件路径，读取并转换为 Base64
            if image_path:
                with open(image_path, 'rb') as image_file:
                    image_base64 = base64.b64encode(image_file.read()).decode('utf-8')
            
            # 调用具体的验证码识别服务
            result = await self._solve_captcha(image_base64)
            
            return {
                "status": "success",
                "text": result,
                "confidence": result.get('confidence', 0.8)
            }
        
        except Exception as e:
            self.logger.error(f"验证码识别失败: {e}")
            return {
                "status": "error",
                "message": str(e)
            }

    async def _solve_captcha(self, image_base64: str) -> Dict[str, Any]:
        """
        抽象方法：具体的验证码识别逻辑
        子类需要实现此方法
        
        :param image_base64: Base64 编码的验证码图像
        :return: 识别结果
        """
        raise NotImplementedError("子类必须实现 _solve_captcha 方法")

class TwoCaptchaSolver(CaptchaSolver):
    """
    2Captcha 验证码识别服务
    """
    BASE_URL = "https://2captcha.com/in.php"
    RESULT_URL = "https://2captcha.com/res.php"

    async def _solve_captcha(self, image_base64: str) -> Dict[str, Any]:
        """
        使用 2Captcha 识别验证码
        
        :param image_base64: Base64 编码的验证码图像
        :return: 识别结果
        """
        if not self.api_key:
            raise ValueError("未提供 2Captcha API Key")
        
        async with aiohttp.ClientSession() as session:
            # 提交验证码识别请求
            submit_params = {
                'key': self.api_key,
                'method': 'base64',
                'body': image_base64,
                'json': 1
            }
            
            async with session.get(self.BASE_URL, params=submit_params) as response:
                submit_result = await response.json()
                
                if submit_result.get('request') == 'ERROR_ZERO_BALANCE':
                    raise ValueError("2Captcha 余额不足")
                
                captcha_id = submit_result.get('request')
            
            # 等待并获取识别结果
            while True:
                result_params = {
                    'key': self.api_key,
                    'action': 'get',
                    'id': captcha_id,
                    'json': 1
                }
                
                async with session.get(self.RESULT_URL, params=result_params) as response:
                    result = await response.json()
                    
                    if result.get('request') == 'CAPCHA_NOT_READY':
                        await asyncio.sleep(5)  # 等待 5 秒后重试
                        continue
                    
                    if result.get('request') == 'ERROR_CAPTCHA_UNSOLVABLE':
                        raise ValueError("验证码无法识别")
                    
                    return {
                        "text": result.get('request'),
                        "confidence": 0.8
                    }

class AntiCaptchaManager:
    """
    验证码处理管理器
    """
    def __init__(self, solver_type: str = '2captcha', api_key: Optional[str] = None):
        """
        初始化验证码处理管理器
        
        :param solver_type: 验证码识别服务类型
        :param api_key: 第三方服务 API Key
        """
        self.solver_type = solver_type
        self.api_key = api_key
        
        self.solvers = {
            '2captcha': TwoCaptchaSolver
        }
        
        if solver_type not in self.solvers:
            raise ValueError(f"不支持的验证码识别服务: {solver_type}")
        
        self.solver = self.solvers[solver_type](api_key)

    async def solve_captcha(self, 
                             image_path: Optional[str] = None, 
                             image_base64: Optional[str] = None) -> Dict[str, Any]:
        """
        解决验证码
        
        :param image_path: 验证码图像文件路径
        :param image_base64: Base64 编码的验证码图像
        :return: 验证码识别结果
        """
        return await self.solver.solve_image_captcha(image_path, image_base64) 