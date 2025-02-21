from typing import Dict, Any, List
from ..base_action_handler import BaseActionHandler

class DataProcessorHandler(BaseActionHandler):
    """数据处理动作处理器"""
    
    async def execute(self, action_data: Dict[str, Any]) -> Any:
        """
        执行数据处理动作
        
        :param action_data: 动作数据，包含处理规则
        :return: 处理后的数据
        """
        data = action_data.get('data', [])
        rules = action_data.get('rules', [])
        
        processed_data = data
        for rule in rules:
            processed_data = self._apply_rule(processed_data, rule)
            
        return processed_data

    def _apply_rule(self, data: Any, rule: Dict[str, Any]) -> Any:
        """
        应用处理规则
        
        :param data: 待处理数据
        :param rule: 处理规则
        :return: 处理后的数据
        """
        rule_type = rule.get('type')
        
        if rule_type == 'filter':
            return self._filter_data(data, rule)
        elif rule_type == 'transform':
            return self._transform_data(data, rule)
        elif rule_type == 'aggregate':
            return self._aggregate_data(data, rule)
        else:
            raise ValueError(f"未知的处理规则类型: {rule_type}")

    def _filter_data(self, data: List[Any], rule: Dict[str, Any]) -> List[Any]:
        """
        过滤数据
        
        :param data: 数据列表
        :param rule: 过滤规则
        :return: 过滤后的数据
        """
        condition = rule.get('condition', {})
        field = condition.get('field')
        operator = condition.get('operator')
        value = condition.get('value')
        
        if not all([field, operator, value]):
            return data
            
        filtered = []
        for item in data:
            if isinstance(item, dict):
                item_value = item.get(field)
                if self._evaluate_condition(item_value, operator, value):
                    filtered.append(item)
                    
        return filtered

    def _transform_data(self, data: Any, rule: Dict[str, Any]) -> Any:
        """
        转换数据
        
        :param data: 待转换数据
        :param rule: 转换规则
        :return: 转换后的数据
        """
        transform_type = rule.get('transform_type')
        
        if transform_type == 'replace':
            return self._replace_text(data, rule)
        elif transform_type == 'extract':
            return self._extract_pattern(data, rule)
        elif transform_type == 'format':
            return self._format_data(data, rule)
        
        return data

    def _aggregate_data(self, data: List[Any], rule: Dict[str, Any]) -> Any:
        """
        聚合数据
        
        :param data: 数据列表
        :param rule: 聚合规则
        :return: 聚合结果
        """
        agg_type = rule.get('aggregate_type')
        field = rule.get('field')
        
        if not field or not isinstance(data, list):
            return data
            
        values = []
        for item in data:
            if isinstance(item, dict):
                value = item.get(field)
                if value is not None:
                    values.append(value)
        
        if agg_type == 'count':
            return len(values)
        elif agg_type == 'sum':
            return sum(values)
        elif agg_type == 'average':
            return sum(values) / len(values) if values else 0
        elif agg_type == 'max':
            return max(values) if values else None
        elif agg_type == 'min':
            return min(values) if values else None
        
        return data

    def _evaluate_condition(self, value1: Any, operator: str, value2: Any) -> bool:
        """
        评估条件
        
        :param value1: 第一个值
        :param operator: 操作符
        :param value2: 第二个值
        :return: 条件是否成立
        """
        if operator == 'equals':
            return value1 == value2
        elif operator == 'not_equals':
            return value1 != value2
        elif operator == 'contains':
            return value2 in value1 if value1 is not None else False
        elif operator == 'not_contains':
            return value2 not in value1 if value1 is not None else True
        elif operator == 'greater_than':
            return value1 > value2
        elif operator == 'less_than':
            return value1 < value2
        
        return False

    def _replace_text(self, data: str, rule: Dict[str, Any]) -> str:
        """
        替换文本
        
        :param data: 文本数据
        :param rule: 替换规则
        :return: 替换后的文本
        """
        if not isinstance(data, str):
            return data
            
        old_value = rule.get('old_value', '')
        new_value = rule.get('new_value', '')
        return data.replace(old_value, new_value)

    def _extract_pattern(self, data: str, rule: Dict[str, Any]) -> str:
        """
        提取模式
        
        :param data: 文本数据
        :param rule: 提取规则
        :return: 提取的文本
        """
        if not isinstance(data, str):
            return data
            
        import re
        pattern = rule.get('pattern', '')
        try:
            match = re.search(pattern, data)
            return match.group(0) if match else data
        except:
            return data

    def _format_data(self, data: Any, rule: Dict[str, Any]) -> str:
        """
        格式化数据
        
        :param data: 待格式化数据
        :param rule: 格式化规则
        :return: 格式化后的数据
        """
        format_type = rule.get('format_type')
        
        if format_type == 'number':
            try:
                decimal_places = rule.get('decimal_places', 2)
                return format(float(data), f'.{decimal_places}f')
            except:
                return data
        elif format_type == 'date':
            try:
                from datetime import datetime
                input_format = rule.get('input_format', '%Y-%m-%d')
                output_format = rule.get('output_format', '%Y-%m-%d')
                date = datetime.strptime(data, input_format)
                return date.strftime(output_format)
            except:
                return data
        
        return data

    async def validate(self, action_data: Dict[str, Any]) -> bool:
        """
        验证动作参数
        
        :param action_data: 动作数据
        :return: 是否验证通过
        """
        return 'rules' in action_data 