-- 工作流程详情视图
CREATE VIEW workflow_details AS
SELECT 
    w.id as workflow_id,
    w.name as workflow_name,
    u.username,
    ws.name as website_name,
    ws.url as website_url,
    array_agg(a.name ORDER BY ws.step_order) as action_sequence
FROM workflows w
JOIN users u ON w.user_id = u.id
JOIN websites ws ON w.website_id = ws.id
JOIN workflow_steps ws ON w.id = ws.workflow_id
JOIN actions a ON ws.action_id = a.id
GROUP BY w.id, w.name, u.username, ws.name, ws.url;

-- 用户活动视图
CREATE VIEW user_activities AS
SELECT 
    u.username,
    count(DISTINCT w.id) as workflow_count,
    count(DISTINCT wp.website_id) as website_count,
    max(w.created_at) as last_activity
FROM users u
LEFT JOIN workflows w ON u.id = w.user_id
LEFT JOIN user_preferences wp ON u.id = wp.user_id
GROUP BY u.id, u.username;
