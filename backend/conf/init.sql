-- 创建默认管理员用户
INSERT INTO t_user (username, name, password, email, mobile, status, login_time, create_time, update_time)
VALUES ('admin', 'Admin', '8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918
', 'admin@example.com', '1234567890', 0, NULL, NOW(), NOW());

-- 创建角色
INSERT INTO t_role (role_name, description, create_time, update_time) VALUES
('Administrator', '管理员', NOW(), NOW()),
('User', '普通用户', NOW(), NOW()),
('Guest', 'Guest', NOW(), NOW());

-- 获取管理员用户和角色的ID
SET @admin_user_id = (SELECT id FROM t_user WHERE username='admin');
SET @admin_role_id = (SELECT id FROM t_role WHERE role_name='Administrator');

-- 关联用户和角色
INSERT INTO t_user_role (user_id, role_id)
VALUES (@admin_user_id, @admin_role_id);

-- 创建权限
INSERT INTO t_permission (name, code, create_time, update_time) VALUES 
('全部权限', 'full_access', NOW(), NOW()),
('查看权限', 'view', NOW(), NOW()),
('编辑权限', 'edit', NOW(), NOW());

-- 获取权限ID
SET @full_access_permission_id = (SELECT id FROM t_permission WHERE code='full_access');

-- 关联角色和权限
INSERT INTO t_role_permission (role_id, permission_id)
VALUES (@admin_role_id, @full_access_permission_id);

-- -- 创建初始Token
-- INSERT INTO t_token (user_id, token, create_time)
-- VALUES (@admin_user_id, UUID(), NOW());
