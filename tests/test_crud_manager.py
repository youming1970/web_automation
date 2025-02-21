import unittest
from database.crud_manager import CRUDManager

class TestCRUDManager(unittest.TestCase):
    def setUp(self):
        """
        每个测试前初始化 CRUDManager
        """
        self.crud = CRUDManager()

    def test_user_crud(self):
        """测试用户的 CRUD 操作"""
        # 创建用户
        user = self.crud.create_user(
            username='testuser', 
            email='test@example.com', 
            password_hash='hashed_password'
        )
        self.assertIsNotNone(user)
        self.assertEqual(user['username'], 'testuser')
        
        # 获取用户
        retrieved_user = self.crud.get_user(user['id'])
        self.assertEqual(retrieved_user['username'], 'testuser')
        
        # 更新用户
        updated_user = self.crud.update_user(
            user['id'], 
            username='updateduser', 
            email='updated@example.com'
        )
        self.assertEqual(updated_user['username'], 'updateduser')
        
        # 删除用户
        delete_result = self.crud.delete_user(user['id'])
        self.assertTrue(delete_result)

    def test_action_crud(self):
        """测试动作的 CRUD 操作"""
        # 首先创建一个网站
        website = self.crud.create_website(
            name='Test Website', 
            url='https://example.com'
        )
        
        # 创建动作
        action = self.crud.create_action(
            website_id=website['id'], 
            name='测试点击', 
            action_type='click',
            selector_id=None
        )
        self.assertIsNotNone(action)
        self.assertEqual(action['action_type'], 'click')
        
        # 获取动作
        retrieved_action = self.crud.get_action(action['id'])
        self.assertEqual(retrieved_action['action_type'], 'click')
        
        # 获取网站动作
        website_actions = self.crud.get_website_actions(website['id'])
        self.assertTrue(len(website_actions) > 0)

    def test_user_preference_crud(self):
        """测试用户偏好的 CRUD 操作"""
        # 创建用户和网站
        user = self.crud.create_user(
            username='prefuser', 
            email='pref@example.com', 
            password_hash='hashed_password'
        )
        website = self.crud.create_website(
            name='Preference Website', 
            url='https://pref.example.com'
        )
        
        # 创建用户偏好
        preference = self.crud.create_user_preference(
            user_id=user['id'], 
            website_id=website['id'], 
            preference_key='theme', 
            preference_value='{"value": "dark"}'
        )
        self.assertIsNotNone(preference)
        self.assertEqual(preference['preference_value']['value'], 'dark')
        
        # 获取用户偏好
        retrieved_preference = self.crud.get_user_preference(preference['id'])
        self.assertEqual(retrieved_preference['preference_value']['value'], 'dark')
        
        # 获取用户网站偏好
        user_website_preferences = self.crud.get_user_website_preferences(
            user['id'], website['id']
        )
        self.assertTrue(len(user_website_preferences) > 0)

    def tearDown(self):
        """
        每个测试后关闭数据库连接
        """
        self.crud.close()

if __name__ == '__main__':
    unittest.main() 