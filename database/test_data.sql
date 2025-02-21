-- 插入测试网站
INSERT INTO websites (name, url) VALUES 
('测试网站1', 'https://example1.com'),
('测试网站2', 'https://example2.com');

-- 插入测试用户
INSERT INTO users (username, email, password_hash) VALUES 
('testuser1', 'test1@example.com', 'hashed_password_1'),
('testuser2', 'test2@example.com', 'hashed_password_2');

-- 插入选择器
INSERT INTO selectors (website_id, name, selector_type, selector_value) VALUES 
(1, '登录按钮', 'CSS', '#login-button'),
(1, '用户名输入框', 'CSS', '#username-input');

-- 插入动作
INSERT INTO actions (website_id, name, action_type, selector_id, parameters) VALUES 
(1, '点击登录', 'click', 1, '{}'),
(1, '输入用户名', 'input', 2, '{"value": "testuser"}');
