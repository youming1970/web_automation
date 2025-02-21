from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QTextEdit, QLabel, QSpinBox, QDoubleSpinBox,
    QCheckBox, QGroupBox, QMessageBox, QListWidget,
    QListWidgetItem, QInputDialog, QDialog, QFormLayout,
    QLineEdit
)
from PyQt5.QtCore import Qt
from core.components.anti_crawler.anti_crawler_manager import AntiCrawlerManager

class ProxyDialog(QDialog):
    """代理配置对话框"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("添加代理")
        self.setup_ui()

    def setup_ui(self):
        """设置UI布局"""
        layout = QFormLayout(self)
        
        self.http_proxy = QLineEdit()
        layout.addRow("HTTP代理:", self.http_proxy)
        
        self.https_proxy = QLineEdit()
        layout.addRow("HTTPS代理:", self.https_proxy)
        
        # 按钮
        button_layout = QHBoxLayout()
        
        ok_button = QPushButton("确定")
        ok_button.clicked.connect(self.accept)
        button_layout.addWidget(ok_button)
        
        cancel_button = QPushButton("取消")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)
        
        layout.addRow(button_layout)

    def get_proxy(self) -> dict:
        """获取代理配置"""
        return {
            "http": self.http_proxy.text(),
            "https": self.https_proxy.text()
        }

class AntiCrawlerConfigWidget(QWidget):
    """反爬虫配置组件"""

    def __init__(self):
        super().__init__()
        self.anti_crawler = AntiCrawlerManager()
        self.setup_ui()
        self.load_config()

    def setup_ui(self):
        """设置UI布局"""
        layout = QVBoxLayout(self)
        
        # User-Agent 配置
        ua_group = QGroupBox("User-Agent 配置")
        ua_layout = QVBoxLayout(ua_group)
        
        self.ua_list = QListWidget()
        ua_layout.addWidget(self.ua_list)
        
        ua_buttons = QHBoxLayout()
        
        add_ua_button = QPushButton("添加")
        add_ua_button.clicked.connect(self.add_user_agent)
        ua_buttons.addWidget(add_ua_button)
        
        remove_ua_button = QPushButton("删除")
        remove_ua_button.clicked.connect(self.remove_user_agent)
        ua_buttons.addWidget(remove_ua_button)
        
        ua_layout.addLayout(ua_buttons)
        layout.addWidget(ua_group)
        
        # 代理配置
        proxy_group = QGroupBox("代理配置")
        proxy_layout = QVBoxLayout(proxy_group)
        
        self.proxy_list = QListWidget()
        proxy_layout.addWidget(self.proxy_list)
        
        proxy_buttons = QHBoxLayout()
        
        add_proxy_button = QPushButton("添加")
        add_proxy_button.clicked.connect(self.add_proxy)
        proxy_buttons.addWidget(add_proxy_button)
        
        remove_proxy_button = QPushButton("删除")
        remove_proxy_button.clicked.connect(self.remove_proxy)
        proxy_buttons.addWidget(remove_proxy_button)
        
        test_proxy_button = QPushButton("测试")
        test_proxy_button.clicked.connect(self.test_proxy)
        proxy_buttons.addWidget(test_proxy_button)
        
        proxy_layout.addLayout(proxy_buttons)
        layout.addWidget(proxy_group)
        
        # 延迟配置
        delay_group = QGroupBox("延迟配置")
        delay_layout = QFormLayout(delay_group)
        
        self.min_delay = QDoubleSpinBox()
        self.min_delay.setRange(0, 60)
        self.min_delay.setDecimals(1)
        self.min_delay.setSingleStep(0.1)
        delay_layout.addRow("最小延迟(秒):", self.min_delay)
        
        self.max_delay = QDoubleSpinBox()
        self.max_delay.setRange(0, 60)
        self.max_delay.setDecimals(1)
        self.max_delay.setSingleStep(0.1)
        delay_layout.addRow("最大延迟(秒):", self.max_delay)
        
        self.random_delay = QCheckBox("使用随机延迟")
        delay_layout.addRow(self.random_delay)
        
        layout.addWidget(delay_group)
        
        # 保存按钮
        save_button = QPushButton("保存配置")
        save_button.clicked.connect(self.save_config)
        layout.addWidget(save_button)

    def load_config(self):
        """加载配置"""
        # 加载 User-Agent
        self.ua_list.clear()
        for ua in self.anti_crawler.user_agents:
            self.ua_list.addItem(ua)
        
        # 加载代理
        self.proxy_list.clear()
        for proxy in self.anti_crawler.proxies:
            self.proxy_list.addItem(
                f"HTTP: {proxy['http']}, HTTPS: {proxy['https']}"
            )
        
        # 加载延迟配置
        self.min_delay.setValue(self.anti_crawler.delay_config["min_delay"])
        self.max_delay.setValue(self.anti_crawler.delay_config["max_delay"])
        self.random_delay.setChecked(self.anti_crawler.delay_config["random_delay"])

    def add_user_agent(self):
        """添加 User-Agent"""
        ua, ok = QInputDialog.getText(
            self,
            "添加 User-Agent",
            "请输入 User-Agent:"
        )
        if ok and ua:
            self.anti_crawler.add_user_agent(ua)
            self.ua_list.addItem(ua)

    def remove_user_agent(self):
        """删除 User-Agent"""
        current_item = self.ua_list.currentItem()
        if not current_item:
            return
            
        reply = QMessageBox.question(
            self,
            "确认删除",
            "确定要删除选中的 User-Agent 吗？",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            ua = current_item.text()
            self.anti_crawler.remove_user_agent(ua)
            self.ua_list.takeItem(self.ua_list.row(current_item))

    def add_proxy(self):
        """添加代理"""
        dialog = ProxyDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            proxy = dialog.get_proxy()
            if self.anti_crawler.add_proxy(proxy):
                self.proxy_list.addItem(
                    f"HTTP: {proxy['http']}, HTTPS: {proxy['https']}"
                )
                QMessageBox.information(self, "成功", "代理添加成功")
            else:
                QMessageBox.warning(self, "失败", "代理验证失败，请检查代理配置")

    def remove_proxy(self):
        """删除代理"""
        current_item = self.proxy_list.currentItem()
        if not current_item:
            return
            
        reply = QMessageBox.question(
            self,
            "确认删除",
            "确定要删除选中的代理吗？",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            proxy_text = current_item.text()
            # 解析代理文本
            http = proxy_text.split("HTTP: ")[1].split(",")[0].strip()
            https = proxy_text.split("HTTPS: ")[1].strip()
            proxy = {"http": http, "https": https}
            
            self.anti_crawler.remove_proxy(proxy)
            self.proxy_list.takeItem(self.proxy_list.row(current_item))

    def test_proxy(self):
        """测试代理"""
        current_item = self.proxy_list.currentItem()
        if not current_item:
            return
            
        proxy_text = current_item.text()
        # 解析代理文本
        http = proxy_text.split("HTTP: ")[1].split(",")[0].strip()
        https = proxy_text.split("HTTPS: ")[1].strip()
        proxy = {"http": http, "https": https}
        
        if self.anti_crawler.validate_proxy(proxy):
            QMessageBox.information(self, "测试结果", "代理可用")
        else:
            QMessageBox.warning(self, "测试结果", "代理不可用")

    def save_config(self):
        """保存配置"""
        # 保存延迟配置
        self.anti_crawler.update_delay_config(
            min_delay=self.min_delay.value(),
            max_delay=self.max_delay.value(),
            random_delay=self.random_delay.isChecked()
        )
        
        QMessageBox.information(self, "成功", "配置保存成功") 