-- 创建默认管理员用户
INSERT INTO `t_user` (`id`, `username`, `name`, `password`, `email`, `mobile`, `status`, `login_time`, `create_time`, `update_time`) VALUES (1, 'admin', 'Admin', 'pbkdf2_sha256$600000$U1OUFyNMdyHlHFfhBkVPr3$Q2OYOUVAh3kU29ENFY1pC1kyQnrommzYodWuoCOHAZw=', 'admin@example.com', '1234567890', 0, '2024-07-29 13:37:05.099571', '2024-07-12 16:19:39.000000', '2024-07-29 13:37:05.099613');

INSERT INTO `turelay`.`t_role` (`id`, `role_name`, `description`, `create_time`, `update_time`) VALUES (1, 'Administrator', '管理员', '2024-07-12 16:19:39.000000', '2024-07-12 16:19:39.000000');
INSERT INTO `turelay`.`t_role` (`id`, `role_name`, `description`, `create_time`, `update_time`) VALUES (2, 'User', '普通用户', '2024-07-12 16:19:39.000000', '2024-07-12 16:19:39.000000');

INSERT INTO `turelay`.`t_user_role` (`id`, `role_id`, `user_id`) VALUES (1, 1, 1);

INSERT INTO `turelay`.`t_permission` (`id`, `name`, `code`, `create_time`, `update_time`) VALUES (1, '全部权限', 'full_access', '2024-07-12 16:19:39.000000', '2024-07-12 16:19:39.000000');
INSERT INTO `turelay`.`t_permission` (`id`, `name`, `code`, `create_time`, `update_time`) VALUES (2, '查看权限', 'view', '2024-07-12 16:19:39.000000', '2024-07-12 16:19:39.000000');


INSERT INTO `turelay`.`t_role_permission` (`id`, `permission_id`, `role_id`) VALUES (1, 1, 1);