from database.crud_manager import CRUDManager

def test_database_connection():
    """测试数据库连接和基本查询"""
    try:
        crud = CRUDManager()
        
        # 测试获取所有网站
        print("\n获取所有网站:")
        websites = crud.get_all_websites()
        for website in websites:
            print(f"网站: {website['name']} ({website['url']})")

        # 测试获取所有用户
        print("\n获取所有用户:")
        users = crud.get_all_users()
        for user in users:
            print(f"用户: {user['username']} ({user['email']})")

        # 测试获取用户工作流
        print("\n获取用户1的工作流:")
        workflows = crud.get_user_workflows(1)
        for workflow in workflows:
            print(f"工作流: {workflow['workflow_name']}")

        crud.close()
        print("\n测试完成！")

    except Exception as e:
        print(f"测试失败: {str(e)}")

if __name__ == "__main__":
    test_database_connection()
