import pytest
from core.components.action.handlers.data_processor_handler import DataProcessorHandler

@pytest.fixture
def handler():
    return DataProcessorHandler(None, None)  # 不需要page和selector_engine

@pytest.mark.asyncio
async def test_filter_data(handler):
    """测试数据过滤功能"""
    test_data = [
        {"name": "item1", "price": 100},
        {"name": "item2", "price": 200},
        {"name": "item3", "price": 150}
    ]
    
    # 测试大于条件
    action_data = {
        "data": test_data,
        "rules": [{
            "type": "filter",
            "condition": {
                "field": "price",
                "operator": "greater_than",
                "value": 150
            }
        }]
    }
    
    result = await handler.execute(action_data)
    assert len(result) == 1
    assert result[0]["price"] == 200
    
    # 测试包含条件
    action_data = {
        "data": test_data,
        "rules": [{
            "type": "filter",
            "condition": {
                "field": "name",
                "operator": "contains",
                "value": "item1"
            }
        }]
    }
    
    result = await handler.execute(action_data)
    assert len(result) == 1
    assert result[0]["name"] == "item1"

@pytest.mark.asyncio
async def test_transform_data(handler):
    """测试数据转换功能"""
    # 测试文本替换
    action_data = {
        "data": "Hello World",
        "rules": [{
            "type": "transform",
            "transform_type": "replace",
            "old_value": "World",
            "new_value": "Python"
        }]
    }
    
    result = await handler.execute(action_data)
    assert result == "Hello Python"
    
    # 测试正则提取
    action_data = {
        "data": "Price: $199.99",
        "rules": [{
            "type": "transform",
            "transform_type": "extract",
            "pattern": r"\$\d+\.\d+"
        }]
    }
    
    result = await handler.execute(action_data)
    assert result == "$199.99"
    
    # 测试数字格式化
    action_data = {
        "data": "123.4567",
        "rules": [{
            "type": "transform",
            "transform_type": "format",
            "format_type": "number",
            "decimal_places": 2
        }]
    }
    
    result = await handler.execute(action_data)
    assert result == "123.46"

@pytest.mark.asyncio
async def test_aggregate_data(handler):
    """测试数据聚合功能"""
    test_data = [
        {"name": "item1", "price": 100},
        {"name": "item2", "price": 200},
        {"name": "item3", "price": 150}
    ]
    
    # 测试计数
    action_data = {
        "data": test_data,
        "rules": [{
            "type": "aggregate",
            "aggregate_type": "count",
            "field": "price"
        }]
    }
    
    result = await handler.execute(action_data)
    assert result == 3
    
    # 测试求和
    action_data = {
        "data": test_data,
        "rules": [{
            "type": "aggregate",
            "aggregate_type": "sum",
            "field": "price"
        }]
    }
    
    result = await handler.execute(action_data)
    assert result == 450
    
    # 测试平均值
    action_data = {
        "data": test_data,
        "rules": [{
            "type": "aggregate",
            "aggregate_type": "average",
            "field": "price"
        }]
    }
    
    result = await handler.execute(action_data)
    assert result == 150

@pytest.mark.asyncio
async def test_multiple_rules(handler):
    """测试多规则处理"""
    test_data = [
        {"name": "item1", "price": 100},
        {"name": "item2", "price": 200},
        {"name": "item3", "price": 150}
    ]
    
    action_data = {
        "data": test_data,
        "rules": [
            # 先过滤价格大于100的项目
            {
                "type": "filter",
                "condition": {
                    "field": "price",
                    "operator": "greater_than",
                    "value": 100
                }
            },
            # 然后计算平均价格
            {
                "type": "aggregate",
                "aggregate_type": "average",
                "field": "price"
            }
        ]
    }
    
    result = await handler.execute(action_data)
    assert result == 175  # (200 + 150) / 2

@pytest.mark.asyncio
async def test_error_handling(handler):
    """测试错误处理"""
    # 测试无效的规则类型
    action_data = {
        "data": [],
        "rules": [{
            "type": "invalid_type"
        }]
    }
    
    with pytest.raises(ValueError):
        await handler.execute(action_data)
    
    # 测试无效的数据格式
    action_data = {
        "data": "not a list",
        "rules": [{
            "type": "aggregate",
            "aggregate_type": "sum",
            "field": "price"
        }]
    }
    
    result = await handler.execute(action_data)
    assert result == "not a list"  # 应该返回原数据

@pytest.mark.asyncio
async def test_validation(handler):
    """测试参数验证"""
    # 测试缺少rules参数
    assert not await handler.validate({})
    
    # 测试有rules参数
    assert await handler.validate({"rules": []}) 