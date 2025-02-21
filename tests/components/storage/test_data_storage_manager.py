import pytest
import os
import json
from datetime import datetime
from core.components.storage.data_storage_manager import DataStorageManager

@pytest.fixture
def storage_manager():
    manager = DataStorageManager()
    yield manager
    # 清理测试数据
    test_files = [
        "test_data.json",
        "test_workflow_data.json",
        "test_export.json"
    ]
    for file in test_files:
        if os.path.exists(file):
            os.remove(file)

def test_data_storage(storage_manager):
    """测试数据存储基本功能"""
    workflow_id = 1  # 使用整数ID
    data = {
        "text": "测试数据",
        "number": 123,
        "timestamp": datetime.now().isoformat()
    }
    
    # 存储数据
    file_path = storage_manager.store_data(workflow_id, data)
    assert os.path.exists(file_path)
    
    # 读取数据
    loaded_data = storage_manager.load_data(file_path)
    assert loaded_data["data"]["text"] == data["text"]
    assert loaded_data["data"]["number"] == data["number"]
    assert "timestamp" in loaded_data["data"]
    assert "workflow_id" in loaded_data

def test_workflow_data_management(storage_manager):
    """测试工作流数据管理"""
    workflow_id = 1  # 使用整数ID
    
    # 清理已有数据
    for file in storage_manager.get_workflow_data_files():
        try:
            os.remove(file)
        except:
            pass

    # 存储多条数据
    data_entries = [
        {"step": "step1", "value": "value1"},
        {"step": "step2", "value": "value2"},
        {"step": "step3", "value": "value3"}
    ]

    file_paths = []
    for data in data_entries:
        file_path = storage_manager.store_data(workflow_id, data)
        file_paths.append(file_path)

    # 获取工作流数据文件列表
    workflow_files = storage_manager.get_workflow_data_files(workflow_id)
    assert len(workflow_files) == len(data_entries)

    # 验证数据内容
    for file_path in workflow_files:
        loaded_data = storage_manager.load_data(file_path)
        assert loaded_data["workflow_id"] == workflow_id
        assert "data" in loaded_data
        assert "timestamp" in loaded_data

def test_data_export(storage_manager):
    """测试数据导出功能"""
    workflow_id = 1  # 使用整数ID
    data = {
        "text": "测试数据",
        "number": 123,
        "nested": {
            "key": "value"
        }
    }

    # 存储数据
    file_path = storage_manager.store_data(workflow_id, data)

    # 导出数据
    export_path = "test_export.json"
    storage_manager.export_data(file_path, export_path)

    # 验证导出文件
    assert os.path.exists(export_path)
    with open(export_path, 'r', encoding='utf-8') as f:
        exported_data = json.load(f)
        assert exported_data["data"] == data
        assert exported_data["workflow_id"] == workflow_id
        assert "timestamp" in exported_data

    # 清理测试文件
    os.remove(export_path)

def test_data_deletion(storage_manager):
    """测试数据删除功能"""
    workflow_id = "test_workflow"
    data = {"test": "data"}
    
    # 存储数据
    file_path = storage_manager.store_data(workflow_id, data)
    assert os.path.exists(file_path)
    
    # 删除数据
    storage_manager.delete_data(file_path)
    assert not os.path.exists(file_path)
    
    # 删除不存在的文件
    with pytest.raises(Exception):
        storage_manager.delete_data("non_existent.json")

def test_data_validation(storage_manager):
    """测试数据验证"""
    workflow_id = "test_workflow"
    
    # 测试无效数据
    invalid_data = "不是字典类型的数据"
    with pytest.raises(Exception):
        storage_manager.store_data(workflow_id, invalid_data)
    
    # 测试空数据
    with pytest.raises(Exception):
        storage_manager.store_data(workflow_id, {})

def test_file_path_generation(storage_manager):
    """测试文件路径生成"""
    workflow_id = "test_workflow"
    
    # 生成多个文件路径
    paths = set()
    for _ in range(5):
        data = {"test": "data"}
        file_path = storage_manager.store_data(workflow_id, data)
        paths.add(file_path)
    
    # 验证路径唯一性
    assert len(paths) == 5

def test_data_search(storage_manager):
    """测试数据搜索功能"""
    workflow_id = 1  # 使用整数ID
    
    # 清理已有数据
    for file in storage_manager.get_workflow_data_files():
        try:
            os.remove(file)
        except:
            pass

    # 存储测试数据
    test_data = [
        {"type": "A", "value": 1},
        {"type": "A", "value": 2},
        {"type": "B", "value": 3},
        {"type": "B", "value": 4}
    ]

    for data in test_data:
        storage_manager.store_data(workflow_id, data)

    # 搜索特定类型的数据
    type_a_files = storage_manager.search_data_files(workflow_id, lambda d: d.get("type") == "A")
    assert len(type_a_files) == 2

    # 验证搜索结果
    for file_path in type_a_files:
        data = storage_manager.load_data(file_path)
        assert data["data"]["type"] == "A"

def test_data_aggregation(storage_manager):
    """测试数据聚合功能"""
    workflow_id = 1  # 使用整数ID
    
    # 清理已有数据
    for file in storage_manager.get_workflow_data_files():
        try:
            os.remove(file)
        except:
            pass

    # 存储测试数据
    test_data = [
        {"type": "A", "value": 10},
        {"type": "A", "value": 20},
        {"type": "B", "value": 30},
        {"type": "B", "value": 40}
    ]

    for data in test_data:
        storage_manager.store_data(workflow_id, data)

    # 计算总和
    total = storage_manager.aggregate_data(
        workflow_id,
        lambda d: d["data"]["value"],
        sum
    )
    assert total == 100

    # 计算平均值
    avg = storage_manager.aggregate_data(
        workflow_id,
        lambda d: d["data"]["value"],
        lambda values: sum(values) / len(values) if values else 0
    )
    assert avg == 25

def test_error_handling(storage_manager):
    """测试错误处理"""
    # 测试加载不存在的文件
    with pytest.raises(Exception):
        storage_manager.load_data("non_existent.json")
    
    # 测试导出不存在的文件
    with pytest.raises(Exception):
        storage_manager.export_data("non_existent.json", "export.json")
    
    # 测试无效的工作流ID
    with pytest.raises(Exception):
        storage_manager.get_workflow_data_files("")
    
    # 测试无效的搜索条件
    with pytest.raises(Exception):
        storage_manager.search_data_files("test_workflow", None) 