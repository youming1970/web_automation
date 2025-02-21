from typing import Dict, Any, Optional
from ..base_action_handler import BaseActionHandler

class ExtractTextHandler(BaseActionHandler):
    """提取元素文本内容的处理器"""
    
    async def execute(self, action_data: Dict[str, Any]) -> str:
        """
        执行文本提取动作
        
        :param action_data: 动作数据，包含选择器信息
        :return: 提取的文本内容
        """
        element = await self.selector_engine.find_element(action_data['selector'])
        return await element.text_content()

    async def validate(self, action_data: Dict[str, Any]) -> bool:
        """
        验证动作参数
        
        :param action_data: 动作数据
        :return: 是否验证通过
        """
        return 'selector' in action_data

class ExtractAttributeHandler(BaseActionHandler):
    """提取元素属性值的处理器"""
    
    async def execute(self, action_data: Dict[str, Any]) -> str:
        """
        执行属性提取动作
        
        :param action_data: 动作数据，包含选择器信息和属性名
        :return: 提取的属性值
        """
        element = await self.selector_engine.find_element(action_data['selector'])
        attribute = action_data.get('attribute', 'value')  # 默认提取value属性
        return await element.get_attribute(attribute)

    async def validate(self, action_data: Dict[str, Any]) -> bool:
        """
        验证动作参数
        
        :param action_data: 动作数据
        :return: 是否验证通过
        """
        return 'selector' in action_data

class ExtractHtmlHandler(BaseActionHandler):
    """提取元素HTML内容的处理器"""
    
    async def execute(self, action_data: Dict[str, Any]) -> str:
        """
        执行HTML提取动作
        
        :param action_data: 动作数据，包含选择器信息
        :return: 提取的HTML内容
        """
        element = await self.selector_engine.find_element(action_data['selector'])
        return await element.inner_html()

    async def validate(self, action_data: Dict[str, Any]) -> bool:
        """
        验证动作参数
        
        :param action_data: 动作数据
        :return: 是否验证通过
        """
        return 'selector' in action_data

class ExtractUrlHandler(BaseActionHandler):
    """提取当前页面URL的处理器"""
    
    async def execute(self, action_data: Dict[str, Any]) -> str:
        """
        执行URL提取动作
        
        :param action_data: 动作数据（不需要选择器）
        :return: 当前页面URL
        """
        return self.page.url

    async def validate(self, action_data: Dict[str, Any]) -> bool:
        """
        验证动作参数
        
        :param action_data: 动作数据
        :return: 是否验证通过
        """
        return True  # URL提取不需要额外参数

class ExtractMultipleHandler(BaseActionHandler):
    """提取多个元素内容的处理器"""
    
    async def execute(self, action_data: Dict[str, Any]) -> list:
        """
        执行多元素提取动作
        
        :param action_data: 动作数据，包含选择器信息和提取类型
        :return: 提取的内容列表
        """
        elements = await self.selector_engine.find_elements(action_data['selector'])
        extract_type = action_data.get('extract_type', 'text')  # 默认提取文本
        
        results = []
        for element in elements:
            if extract_type == 'text':
                content = await element.text_content()
            elif extract_type == 'html':
                content = await element.inner_html()
            elif extract_type == 'attribute':
                attribute = action_data.get('attribute', 'value')
                content = await element.get_attribute(attribute)
            else:
                raise ValueError(f"Unknown extract type: {extract_type}")
                
            results.append(content)
            
        return results

    async def validate(self, action_data: Dict[str, Any]) -> bool:
        """
        验证动作参数
        
        :param action_data: 动作数据
        :return: 是否验证通过
        """
        if 'selector' not in action_data:
            return False
            
        extract_type = action_data.get('extract_type', 'text')
        return extract_type in ['text', 'html', 'attribute'] 