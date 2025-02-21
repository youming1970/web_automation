from typing import Optional
import logging

class XPathSelectorHandler:
    def __init__(self, page: Optional[Page] = None):
        """
        初始化 XPath 选择器处理器

        :param page: Playwright 的 Page 对象，用于元素定位
        :raises ValueError: 如果未提供 page 对象
        """
        if page is None:
            raise ValueError("必须提供 Page 对象")
        
        self.page = page
        self.logger = logging.getLogger(self.__class__.__name__) 