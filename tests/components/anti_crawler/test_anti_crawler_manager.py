import pytest
import os
import json
from core.components.anti_crawler.anti_crawler_manager import AntiCrawlerManager
from datetime import datetime, timedelta

@pytest.fixture
def manager():
    # 创建测试配置目录
    os.makedirs("config", exist_ok=True)
    return AntiCrawlerManager()

@pytest.fixture
def cleanup():
    yield
    # 清理测试配置文件
    config_files = [
        "config/user_agents.json",
        "config/proxies.json",
        "config/delay_config.json"
    ]
    for file in config_files:
        if os.path.exists(file):
            os.remove(file)

def test_user_agent_management(manager, cleanup):
    """测试User-Agent管理"""
    # 测试默认User-Agent列表
    assert len(manager.user_agents) > 0
    
    # 测试添加新的User-Agent
    new_ua = "Mozilla/5.0 Test User Agent"
    manager.add_user_agent(new_ua)
    assert new_ua in manager.user_agents
    
    # 测试移除User-Agent
    manager.remove_user_agent(new_ua)
    assert new_ua not in manager.user_agents
    
    # 测试随机获取User-Agent
    ua = manager.get_random_user_agent()
    assert ua in manager.user_agents
    
    # 测试保存和加载User-Agent
    manager.save_user_agents(["test_ua_1", "test_ua_2"])
    new_manager = AntiCrawlerManager()
    assert "test_ua_1" in new_manager.user_agents
    assert "test_ua_2" in new_manager.user_agents

def test_proxy_management(manager, cleanup):
    """测试代理管理"""
    # 测试默认代理列表
    assert isinstance(manager.proxies, list)
    
    # 测试添加新代理
    test_proxy = {
        "http": "http://127.0.0.1:8080",
        "https": "http://127.0.0.1:8080"
    }
    
    # 注：实际添加代理时会进行验证，这里我们模拟验证通过
    manager.proxies.append(test_proxy)
    manager.save_proxies(manager.proxies)
    
    # 测试获取随机代理
    proxy = manager.get_random_proxy()
    assert proxy is not None
    assert "http" in proxy
    assert "https" in proxy
    
    # 测试移除代理
    manager.remove_proxy(test_proxy)
    assert test_proxy not in manager.proxies

def test_delay_management(manager, cleanup):
    """测试延迟管理"""
    # 测试默认延迟配置
    assert "min_delay" in manager.delay_config
    assert "max_delay" in manager.delay_config
    assert "random_delay" in manager.delay_config
    
    # 测试更新延迟配置
    manager.update_delay_config(2.0, 5.0, True)
    assert manager.delay_config["min_delay"] == 2.0
    assert manager.delay_config["max_delay"] == 5.0
    assert manager.delay_config["random_delay"] is True
    
    # 测试获取延迟时间
    delay = manager.get_delay_time()
    assert 2.0 <= delay <= 5.0
    
    # 测试固定延迟
    manager.update_delay_config(3.0, 3.0, False)
    delay = manager.get_delay_time()
    assert delay == 3.0

def test_delay_timing(manager, cleanup):
    """测试延迟时间控制"""
    # 设置固定延迟
    manager.update_delay_config(2.0, 2.0, False)
    
    # 初始状态不需要延迟
    assert not manager.should_delay()
    
    # 更新请求时间
    manager.update_last_request_time()
    
    # 立即检查应该需要延迟
    assert manager.should_delay()
    
    # 等待足够时间后不需要延迟
    manager.last_request_time = datetime.now() - timedelta(seconds=3)
    assert not manager.should_delay()

@pytest.mark.asyncio
async def test_proxy_validation(manager, cleanup):
    """测试代理验证"""
    test_proxy = {
        "http": "http://invalid.proxy:8080",
        "https": "http://invalid.proxy:8080"
    }
    
    # 测试同步验证
    assert not manager.validate_proxy(test_proxy)
    
    # 测试异步验证
    assert not await manager.validate_proxy_async(test_proxy)

def test_config_persistence(manager, cleanup):
    """测试配置持久化"""
    # 测试User-Agent配置
    test_uas = ["test_ua_1", "test_ua_2"]
    manager.save_user_agents(test_uas)
    assert os.path.exists("config/user_agents.json")
    
    with open("config/user_agents.json", 'r') as f:
        saved_uas = json.load(f)
    assert saved_uas == test_uas
    
    # 测试代理配置
    test_proxies = [{
        "http": "http://test.proxy:8080",
        "https": "http://test.proxy:8080"
    }]
    manager.save_proxies(test_proxies)
    assert os.path.exists("config/proxies.json")
    
    with open("config/proxies.json", 'r') as f:
        saved_proxies = json.load(f)
    assert saved_proxies == test_proxies
    
    # 测试延迟配置
    test_delay = {
        "min_delay": 1.5,
        "max_delay": 3.5,
        "random_delay": True
    }
    manager.save_delay_config(test_delay)
    assert os.path.exists("config/delay_config.json")
    
    with open("config/delay_config.json", 'r') as f:
        saved_delay = json.load(f)
    assert saved_delay == test_delay 