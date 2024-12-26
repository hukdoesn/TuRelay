

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for t_alert_contacts
-- ----------------------------
DROP TABLE IF EXISTS `t_alert_contacts`;
CREATE TABLE `t_alert_contacts` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `name` varchar(150) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  `creator` varchar(150) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  `notify_type` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  `webhook` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  `create_time` datetime(6) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `t_alert_contacts_name_b9888fa6_uniq` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;

-- ----------------------------
-- Records of t_alert_contacts
-- ----------------------------
BEGIN;
COMMIT;

-- ----------------------------
-- Table structure for t_alert_history_log
-- ----------------------------
DROP TABLE IF EXISTS `t_alert_history_log`;
CREATE TABLE `t_alert_history_log` (
  `id` int NOT NULL AUTO_INCREMENT,
  `alert_rule` varchar(150) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL,
  `command` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin,
  `create_time` datetime(6) DEFAULT NULL,
  `hostname` varchar(150) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL,
  `match_type` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL,
  `username` varchar(150) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;

-- ----------------------------
-- Records of t_alert_history_log
-- ----------------------------
BEGIN;
COMMIT;

-- ----------------------------
-- Table structure for t_command_alert
-- ----------------------------
DROP TABLE IF EXISTS `t_command_alert`;
CREATE TABLE `t_command_alert` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `name` varchar(150) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  `command_rule` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin,
  `is_active` tinyint(1) DEFAULT NULL,
  `create_time` datetime(6) NOT NULL,
  `alert_contacts` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin,
  `hosts` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin,
  `match_type` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=28 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;

-- ----------------------------
-- Records of t_command_alert
-- ----------------------------
BEGIN;
COMMIT;

-- ----------------------------
-- Table structure for t_command_log
-- ----------------------------
DROP TABLE IF EXISTS `t_command_log`;
CREATE TABLE `t_command_log` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `username` varchar(150) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  `command` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  `hosts` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  `credential` varchar(150) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  `create_time` datetime(6) NOT NULL,
  `network` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=928 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;

-- ----------------------------
-- Records of t_command_log
-- ----------------------------
BEGIN;
COMMIT;

-- ----------------------------
-- Table structure for t_credential
-- ----------------------------
DROP TABLE IF EXISTS `t_credential`;
CREATE TABLE `t_credential` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(150) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  `type` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  `account` varchar(150) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL,
  `password` varchar(128) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL,
  `key` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin,
  `key_password` varchar(128) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL,
  `KeyId` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL,
  `KeySecret` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL,
  `notes` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin,
  `create_time` datetime(6) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=19 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;

-- ----------------------------
-- Records of t_credential
-- ----------------------------
BEGIN;
COMMIT;

-- ----------------------------
-- Table structure for t_domain_monitor
-- ----------------------------
DROP TABLE IF EXISTS `t_domain_monitor`;
CREATE TABLE `t_domain_monitor` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `name` varchar(150) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  `domain` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  `connectivity` tinyint(1) NOT NULL,
  `status_code` int DEFAULT NULL,
  `redirection` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL,
  `time_consumption` double DEFAULT NULL,
  `tls_version` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL,
  `http_version` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL,
  `certificate_days` int DEFAULT NULL,
  `enable` tinyint(1) NOT NULL,
  `alert` tinyint(1) NOT NULL,
  `monitor_frequency` int NOT NULL,
  `create_time` datetime(6) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;

-- ----------------------------
-- Records of t_domain_monitor
-- ----------------------------
BEGIN;
COMMIT;

-- ----------------------------
-- Table structure for t_host
-- ----------------------------
DROP TABLE IF EXISTS `t_host`;
CREATE TABLE `t_host` (
  `id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  `name` varchar(150) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  `status` tinyint(1) NOT NULL,
  `operating_system` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  `network` char(39) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  `protocol` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  `port` int NOT NULL,
  `remarks` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin,
  `create_time` datetime(6) NOT NULL,
  `account_type_id` int DEFAULT NULL,
  `node_id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `t_host_account_type_id_e1167e0f_fk_t_credential_id` (`account_type_id`),
  KEY `t_host_node_id_c8076110_fk_t_node_id` (`node_id`),
  CONSTRAINT `t_host_account_type_id_e1167e0f_fk_t_credential_id` FOREIGN KEY (`account_type_id`) REFERENCES `t_credential` (`id`),
  CONSTRAINT `t_host_node_id_c8076110_fk_t_node_id` FOREIGN KEY (`node_id`) REFERENCES `t_node` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;

-- ----------------------------
-- Records of t_host
-- ----------------------------
BEGIN;
COMMIT;

-- ----------------------------
-- Table structure for t_login_log
-- ----------------------------
DROP TABLE IF EXISTS `t_login_log`;
CREATE TABLE `t_login_log` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `username` varchar(150) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  `client_ip` char(39) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  `login_status` tinyint(1) NOT NULL,
  `reason` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL,
  `browser_info` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  `os_info` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL,
  `login_time` datetime(6) NOT NULL,
  `user_id` bigint DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `t_login_log_user_id_3f17b1b0_fk_t_user_id` (`user_id`),
  CONSTRAINT `t_login_log_user_id_3f17b1b0_fk_t_user_id` FOREIGN KEY (`user_id`) REFERENCES `t_user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=44 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;

-- ----------------------------
-- Records of t_login_log
-- ----------------------------
BEGIN;
COMMIT;

-- ----------------------------
-- Table structure for t_node
-- ----------------------------
DROP TABLE IF EXISTS `t_node`;
CREATE TABLE `t_node` (
  `id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  `name` varchar(150) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  `create_time` datetime(6) NOT NULL,
  `parent_id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `t_node_parent_id_7e9cba0e_fk_t_node_id` (`parent_id`),
  CONSTRAINT `t_node_parent_id_7e9cba0e_fk_t_node_id` FOREIGN KEY (`parent_id`) REFERENCES `t_node` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;

-- ----------------------------
-- Records of t_node
-- ----------------------------
BEGIN;
INSERT INTO `t_node` (`id`, `name`, `create_time`, `parent_id`) VALUES ('0af379a2fb0f4a4dba855e7b25f6f270', 'Default', '2024-09-05 00:00:00.000000', NULL);
INSERT INTO `t_node` (`id`, `name`, `create_time`, `parent_id`) VALUES ('9783b8684c5540fbaa1d8e1730397cbf', '演示', '2024-12-24 16:29:15.278109', '0af379a2fb0f4a4dba855e7b25f6f270');
COMMIT;

-- ----------------------------
-- Table structure for t_operation_log
-- ----------------------------
DROP TABLE IF EXISTS `t_operation_log`;
CREATE TABLE `t_operation_log` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `module` varchar(150) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  `request_interface` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  `request_method` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  `ip_address` char(39) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  `before_change` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin,
  `after_change` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin,
  `create_time` datetime(6) NOT NULL,
  `user_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  KEY `t_operation_log_user_id_15f36343_fk_t_user_id` (`user_id`),
  CONSTRAINT `t_operation_log_user_id_15f36343_fk_t_user_id` FOREIGN KEY (`user_id`) REFERENCES `t_user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=40 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;

-- ----------------------------
-- Records of t_operation_log
-- ----------------------------
BEGIN;
COMMIT;

-- ----------------------------
-- Table structure for t_permission
-- ----------------------------
DROP TABLE IF EXISTS `t_permission`;
CREATE TABLE `t_permission` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `name` varchar(150) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  `code` varchar(150) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  `create_time` datetime(6) NOT NULL,
  `update_time` datetime(6) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`),
  UNIQUE KEY `code` (`code`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;

-- ----------------------------
-- Records of t_permission
-- ----------------------------
BEGIN;
INSERT INTO `t_permission` (`id`, `name`, `code`, `create_time`, `update_time`) VALUES (1, '全部权限', 'full_access', '2024-07-12 16:19:39.000000', '2024-07-12 16:19:39.000000');
INSERT INTO `t_permission` (`id`, `name`, `code`, `create_time`, `update_time`) VALUES (2, '查看权限', 'view', '2024-07-12 16:19:39.000000', '2024-07-12 16:19:39.000000');
COMMIT;

-- ----------------------------
-- Table structure for t_role
-- ----------------------------
DROP TABLE IF EXISTS `t_role`;
CREATE TABLE `t_role` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `role_name` varchar(150) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  `description` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  `create_time` datetime(6) NOT NULL,
  `update_time` datetime(6) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `role_name` (`role_name`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;

-- ----------------------------
-- Records of t_role
-- ----------------------------
BEGIN;
INSERT INTO `t_role` (`id`, `role_name`, `description`, `create_time`, `update_time`) VALUES (1, 'Administrator', '管理员', '2024-07-12 16:19:39.000000', '2024-07-12 16:19:39.000000');
INSERT INTO `t_role` (`id`, `role_name`, `description`, `create_time`, `update_time`) VALUES (2, 'User', '普通用户', '2024-07-12 16:19:39.000000', '2024-07-12 16:19:39.000000');
COMMIT;

-- ----------------------------
-- Table structure for t_role_permission
-- ----------------------------
DROP TABLE IF EXISTS `t_role_permission`;
CREATE TABLE `t_role_permission` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `permission_id` bigint NOT NULL,
  `role_id` bigint NOT NULL,
  `user_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `t_role_permission_user_id_role_id_permission_id_d671940e_uniq` (`user_id`,`role_id`,`permission_id`),
  KEY `t_role_permission_permission_id_f4ba5100_fk_t_permission_id` (`permission_id`),
  KEY `t_role_permission_role_id_d111be47_fk_t_role_id` (`role_id`),
  CONSTRAINT `t_role_permission_permission_id_f4ba5100_fk_t_permission_id` FOREIGN KEY (`permission_id`) REFERENCES `t_permission` (`id`),
  CONSTRAINT `t_role_permission_role_id_d111be47_fk_t_role_id` FOREIGN KEY (`role_id`) REFERENCES `t_role` (`id`),
  CONSTRAINT `t_role_permission_user_id_fbdafe01_fk_t_user_id` FOREIGN KEY (`user_id`) REFERENCES `t_user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=42 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;

-- ----------------------------
-- Records of t_role_permission
-- ----------------------------
BEGIN;
INSERT INTO `t_role_permission` (`id`, `permission_id`, `role_id`, `user_id`) VALUES (39, 1, 1, 1);
COMMIT;

-- ----------------------------
-- Table structure for t_system_settings
-- ----------------------------
DROP TABLE IF EXISTS `t_system_settings`;
CREATE TABLE `t_system_settings` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `watermark_enabled` tinyint(1) NOT NULL,
  `ip_whitelist` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin,
  `ip_blacklist` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin,
  `update_time` datetime(6) NOT NULL,
  `multi_login_account` varchar(150) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;

-- ----------------------------
-- Records of t_system_settings
-- ----------------------------
BEGIN;
INSERT INTO `t_system_settings` (`id`, `watermark_enabled`, `ip_whitelist`, `ip_blacklist`, `update_time`, `multi_login_account`) VALUES (2, 0, '', '', '2024-12-24 17:47:18.188700', 'admin');
COMMIT;

-- ----------------------------
-- Table structure for t_token
-- ----------------------------
DROP TABLE IF EXISTS `t_token`;
CREATE TABLE `t_token` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `token` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  `create_time` datetime(6) NOT NULL,
  `user_id` bigint NOT NULL,
  `last_activity` datetime(6) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `t_token_token_34abd9a6_uniq` (`token`),
  KEY `t_token_user_id_e8393728` (`user_id`)
) ENGINE=InnoDB AUTO_INCREMENT=241 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;

-- ----------------------------
-- Table structure for t_user
-- ----------------------------
DROP TABLE IF EXISTS `t_user`;
CREATE TABLE `t_user` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `username` varchar(150) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  `name` varchar(150) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  `password` varchar(128) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  `email` varchar(254) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  `mobile` varchar(15) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  `status` tinyint(1) NOT NULL,
  `login_time` datetime(6) DEFAULT NULL,
  `create_time` datetime(6) NOT NULL,
  `update_time` datetime(6) NOT NULL,
  `mfa_level` int NOT NULL,
  `otp_secret_key` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`),
  UNIQUE KEY `email` (`email`)
) ENGINE=InnoDB AUTO_INCREMENT=16 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;

-- ----------------------------
-- Records of t_user
-- ----------------------------
BEGIN;
INSERT INTO `t_user` (`id`, `username`, `name`, `password`, `email`, `mobile`, `status`, `login_time`, `create_time`, `update_time`, `mfa_level`, `otp_secret_key`) VALUES (1, 'admin', 'Admin', 'pbkdf2_sha256$600000$oHrGCP0PXFDV7mZYvC9Ci1$ZdH0cnifW94GlsCVdHG9MUApvvbTLRCxzPxtncwNDBw=', 'admin@example.com', '1234567890', 0, '2024-12-25 13:03:09.118481', '2024-07-12 16:19:39.000000', '2024-12-25 13:03:09.118651', 0, NULL);
COMMIT;

-- ----------------------------
-- Table structure for t_user_lock
-- ----------------------------
DROP TABLE IF EXISTS `t_user_lock`;
CREATE TABLE `t_user_lock` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `login_count` int NOT NULL,
  `lock_count` int NOT NULL,
  `last_attempt_time` datetime(6) DEFAULT NULL,
  `user_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `user_id` (`user_id`),
  CONSTRAINT `t_user_lock_user_id_6af3000e_fk_t_user_id` FOREIGN KEY (`user_id`) REFERENCES `t_user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;

-- ----------------------------
-- Records of t_user_lock
-- ----------------------------
BEGIN;
INSERT INTO `t_user_lock` (`id`, `login_count`, `lock_count`, `last_attempt_time`, `user_id`) VALUES (1, 0, 0, '2024-12-25 09:19:58.826978', 1);
COMMIT;

SET FOREIGN_KEY_CHECKS = 1;
