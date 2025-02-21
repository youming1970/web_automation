import pytest
import os
import sys

def main():
    """
    运行所有测试用例
    """
    # 添加项目根目录到Python路径
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, project_root)
    
    # 运行测试
    args = [
        # 测试目录
        "tests",
        # 显示详细输出
        "-v",
        # 显示测试进度
        "-s",
        # 显示测试覆盖率报告
        "--cov=core",
        "--cov-report=term-missing",
        # 失败时显示完整的traceback
        "--tb=long",
        # 禁用警告
        "-p", "no:warnings"
    ]
    
    pytest.main(args)

if __name__ == "__main__":
    main() 