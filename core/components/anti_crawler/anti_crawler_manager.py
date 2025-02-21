import random
import json
import os
from typing import Dict, List, Optional
from datetime import datetime, timedelta

class AntiCrawlerManager:
    """反爬虫管理器"""

    def __init__(self):
        self.user_agents = self._load_user_agents()
        self.proxies = self._load_proxies()
        self.delay_config = self._load_delay_config()
        self.last_request_time = None

    def _load_user_agents(self) -> List[str]:
        """加载 User-Agent 列表"""
        default_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 Edg/91.0.864.59",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        ]
        
        try:
            config_path = os.path.join("config", "user_agents.json")
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return default_agents
        except Exception:
            return default_agents

    def _load_proxies(self) -> List[Dict[str, str]]:
        """加载代理配置"""
        try:
            config_path = os.path.join("config", "proxies.json")
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return []
        except Exception:
            return []

    def _load_delay_config(self) -> Dict[str, float]:
        """加载延迟配置"""
        default_config = {
            "min_delay": 1.0,  # 最小延迟（秒）
            "max_delay": 3.0,  # 最大延迟（秒）
            "random_delay": True  # 是否使用随机延迟
        }
        
        try:
            config_path = os.path.join("config", "delay_config.json")
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return default_config
        except Exception:
            return default_config

    def get_random_user_agent(self) -> str:
        """获取随机 User-Agent"""
        return random.choice(self.user_agents)

    def get_random_proxy(self) -> Optional[Dict[str, str]]:
        """获取随机代理"""
        return random.choice(self.proxies) if self.proxies else None

    def get_delay_time(self) -> float:
        """获取延迟时间"""
        if self.delay_config["random_delay"]:
            return random.uniform(
                self.delay_config["min_delay"],
                self.delay_config["max_delay"]
            )
        return self.delay_config["min_delay"]

    def should_delay(self) -> bool:
        """判断是否需要延迟"""
        if not self.last_request_time:
            return False
            
        elapsed = datetime.now() - self.last_request_time
        return elapsed.total_seconds() < self.delay_config["min_delay"]

    def update_last_request_time(self):
        """更新最后请求时间"""
        self.last_request_time = datetime.now()

    def save_user_agents(self, user_agents: List[str]):
        """保存 User-Agent 列表"""
        config_dir = "config"
        if not os.path.exists(config_dir):
            os.makedirs(config_dir)
            
        config_path = os.path.join(config_dir, "user_agents.json")
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(user_agents, f, ensure_ascii=False, indent=2)
        self.user_agents = user_agents

    def save_proxies(self, proxies: List[Dict[str, str]]):
        """保存代理配置"""
        config_dir = "config"
        if not os.path.exists(config_dir):
            os.makedirs(config_dir)
            
        config_path = os.path.join(config_dir, "proxies.json")
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(proxies, f, ensure_ascii=False, indent=2)
        self.proxies = proxies

    def save_delay_config(self, config: Dict[str, float]):
        """保存延迟配置"""
        config_dir = "config"
        if not os.path.exists(config_dir):
            os.makedirs(config_dir)
            
        config_path = os.path.join(config_dir, "delay_config.json")
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        self.delay_config = config

    def validate_proxy(self, proxy: Dict[str, str]) -> bool:
        """验证代理是否可用"""
        import requests
        import asyncio
        from playwright.async_api import async_playwright
        
        # 同步验证
        try:
            response = requests.get(
                "http://www.google.com",
                proxies={
                    "http": proxy["http"],
                    "https": proxy["https"]
                },
                timeout=5
            )
            return response.status_code == 200
        except Exception:
            return False

    async def validate_proxy_async(self, proxy: Dict[str, str]) -> bool:
        """异步验证代理是否可用"""
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(proxy=proxy)
                page = await browser.new_page()
                await page.goto("http://www.google.com", timeout=5000)
                await browser.close()
                return True
        except Exception:
            return False

    def add_proxy(self, proxy: Dict[str, str]) -> bool:
        """添加新代理"""
        if self.validate_proxy(proxy):
            self.proxies.append(proxy)
            self.save_proxies(self.proxies)
            return True
        return False

    def remove_proxy(self, proxy: Dict[str, str]):
        """移除代理"""
        if proxy in self.proxies:
            self.proxies.remove(proxy)
            self.save_proxies(self.proxies)

    def add_user_agent(self, user_agent: str):
        """添加新的 User-Agent"""
        if user_agent not in self.user_agents:
            self.user_agents.append(user_agent)
            self.save_user_agents(self.user_agents)

    def remove_user_agent(self, user_agent: str):
        """移除 User-Agent"""
        if user_agent in self.user_agents:
            self.user_agents.remove(user_agent)
            self.save_user_agents(self.user_agents)

    def update_delay_config(self, min_delay: float, max_delay: float, random_delay: bool):
        """更新延迟配置"""
        config = {
            "min_delay": min_delay,
            "max_delay": max_delay,
            "random_delay": random_delay
        }
        self.save_delay_config(config) 