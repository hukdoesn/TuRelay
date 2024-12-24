/*
 Navicat Premium Data Transfer

 Source Server         : Turelay
 Source Server Type    : MySQL
 Source Server Version : 80040 (8.0.40)
 Source Host           : 117.72.35.106:3307
 Source Schema         : turelay

 Target Server Type    : MySQL
 Target Server Version : 80040 (8.0.40)
 File Encoding         : 65001

 Date: 24/12/2024 16:01:39
*/

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
INSERT INTO `t_alert_contacts` (`id`, `name`, `creator`, `notify_type`, `webhook`, `create_time`) VALUES (7, '钉钉告警测试', 'Admin', '钉钉', 'https://oapi.dingtalk.com/robot/send?access_token=1df380996baf0d171cf5dd03b30f51e9720252419464336c98e0467c564a2508', '2024-10-17 15:35:56.744647');
INSERT INTO `t_alert_contacts` (`id`, `name`, `creator`, `notify_type`, `webhook`, `create_time`) VALUES (9, '企业微信告警测试', 'Admin', '企微', 'https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=b6fd730d-fa51-4abf-ad48-a999cfc6a89b', '2024-10-28 13:36:18.070762');
INSERT INTO `t_alert_contacts` (`id`, `name`, `creator`, `notify_type`, `webhook`, `create_time`) VALUES (10, '飞书告警测试', 'Admin', '飞书', 'https://open.feishu.cn/open-apis/bot/v2/hook/ea6d19ed-6679-4650-9e54-4275b5b0ed6b', '2024-10-28 15:41:35.933120');
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
INSERT INTO `t_command_alert` (`id`, `name`, `command_rule`, `is_active`, `create_time`, `alert_contacts`, `hosts`, `match_type`) VALUES (27, '测试', '[\"ls\", \"ps\"]', 0, '2024-12-18 09:18:03.620002', '7', '9bfef5a1-ee1d-4054-be97-27934ad112ed,ec4ce326-2f74-4854-ab70-a00d78326a7d', 'exact');
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
) ENGINE=InnoDB AUTO_INCREMENT=919 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;

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
) ENGINE=InnoDB AUTO_INCREMENT=17 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;

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
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;

-- ----------------------------
-- Records of t_domain_monitor
-- ----------------------------
BEGIN;
INSERT INTO `t_domain_monitor` (`id`, `name`, `domain`, `connectivity`, `status_code`, `redirection`, `time_consumption`, `tls_version`, `http_version`, `certificate_days`, `enable`, `alert`, `monitor_frequency`, `create_time`) VALUES (5, '博客', 'https://ext4.cn', 1, 200, 'True', 0.422152, 'TLSv1.2', '1.1', 65, 1, 0, 15, '2024-12-05 14:06:04.581398');
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
) ENGINE=InnoDB AUTO_INCREMENT=15 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;

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
INSERT INTO `t_node` (`id`, `name`, `create_time`, `parent_id`) VALUES ('3794c6aed0b14e2097b0f1baf5f2baa2', 'test', '2024-11-04 11:44:20.406723', '0af379a2fb0f4a4dba855e7b25f6f270');
INSERT INTO `t_node` (`id`, `name`, `create_time`, `parent_id`) VALUES ('6554e0e0d53741618c0cafd5d38ad208', '阿里云', '2024-09-05 00:00:00.000000', '0af379a2fb0f4a4dba855e7b25f6f270');
INSERT INTO `t_node` (`id`, `name`, `create_time`, `parent_id`) VALUES ('a502be3619654c01bd9cf30fb6e0f582', '啊啊啊', '2024-12-17 17:00:05.304181', '0af379a2fb0f4a4dba855e7b25f6f270');
INSERT INTO `t_node` (`id`, `name`, `create_time`, `parent_id`) VALUES ('ed3e5decb7a84328832f90344bfecaef', 'blog', '2024-11-04 11:44:27.166401', '3794c6aed0b14e2097b0f1baf5f2baa2');
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
) ENGINE=InnoDB AUTO_INCREMENT=12 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;

-- ----------------------------
-- Records of t_operation_log
-- ----------------------------
BEGIN;
INSERT INTO `t_operation_log` (`id`, `module`, `request_interface`, `request_method`, `ip_address`, `before_change`, `after_change`, `create_time`, `user_id`) VALUES (1, '站点监控', '/api/monitor_domains/1/delete/', 'DELETE', '172.20.0.1', '{\"id\": 1, \"name\": \"百度\", \"domain\": \"https://www.baidu.com\", \"connectivity\": false, \"status_code\": null, \"redirection\": null, \"time_consumption\": null, \"tls_version\": null, \"http_version\": null, \"certificate_days\": null, \"enable\": false, \"alert\": false, \"monitor_frequency\": 15}', '{}', '2024-12-24 14:11:17.304125', 1);
INSERT INTO `t_operation_log` (`id`, `module`, `request_interface`, `request_method`, `ip_address`, `before_change`, `after_change`, `create_time`, `user_id`) VALUES (2, '站点监控', '/api/monitor_domains/2/delete/', 'DELETE', '172.20.0.1', '{\"id\": 2, \"name\": \"京东\", \"domain\": \"https://jd.com\", \"connectivity\": false, \"status_code\": null, \"redirection\": null, \"time_consumption\": null, \"tls_version\": null, \"http_version\": null, \"certificate_days\": null, \"enable\": false, \"alert\": false, \"monitor_frequency\": 15}', '{}', '2024-12-24 14:11:19.126928', 1);
INSERT INTO `t_operation_log` (`id`, `module`, `request_interface`, `request_method`, `ip_address`, `before_change`, `after_change`, `create_time`, `user_id`) VALUES (3, '站点监控', '/api/monitor_domains/3/delete/', 'DELETE', '172.20.0.1', '{\"id\": 3, \"name\": \"QQ\", \"domain\": \"https://www.qq.com\", \"connectivity\": false, \"status_code\": null, \"redirection\": null, \"time_consumption\": null, \"tls_version\": null, \"http_version\": null, \"certificate_days\": null, \"enable\": false, \"alert\": true, \"monitor_frequency\": 15}', '{}', '2024-12-24 14:11:20.931095', 1);
INSERT INTO `t_operation_log` (`id`, `module`, `request_interface`, `request_method`, `ip_address`, `before_change`, `after_change`, `create_time`, `user_id`) VALUES (4, '站点监控', '/api/monitor_domains/6/delete/', 'DELETE', '172.20.0.1', '{\"id\": 6, \"name\": \"test\", \"domain\": \"https://www.ext4.cn\", \"connectivity\": false, \"status_code\": null, \"redirection\": null, \"time_consumption\": null, \"tls_version\": null, \"http_version\": null, \"certificate_days\": null, \"enable\": false, \"alert\": false, \"monitor_frequency\": 15}', '{}', '2024-12-24 14:11:22.802712', 1);
INSERT INTO `t_operation_log` (`id`, `module`, `request_interface`, `request_method`, `ip_address`, `before_change`, `after_change`, `create_time`, `user_id`) VALUES (5, '用户列表', '/api/users/demo/delete/', 'DELETE', '172.20.0.1', '{\"id\": 14, \"username\": \"demo\", \"name\": \"演示用户\", \"password\": \"***\", \"email\": \"demo@163.com\", \"mobile\": \"19512141234\", \"status\": false, \"login_time\": \"2024-12-18T14:20:24.047238\", \"otp_secret_key\": null, \"mfa_level\": 0}', '{}', '2024-12-24 14:11:35.004852', 1);
INSERT INTO `t_operation_log` (`id`, `module`, `request_interface`, `request_method`, `ip_address`, `before_change`, `after_change`, `create_time`, `user_id`) VALUES (6, '用户列表', '/api/users/test/delete/', 'DELETE', '172.20.0.1', '{\"id\": 13, \"username\": \"test\", \"name\": \"测试\", \"password\": \"***\", \"email\": \"hukdoesn@163.com\", \"mobile\": \"12345678910\", \"status\": false, \"login_time\": null, \"otp_secret_key\": null, \"mfa_level\": 0}', '{}', '2024-12-24 14:11:37.058263', 1);
INSERT INTO `t_operation_log` (`id`, `module`, `request_interface`, `request_method`, `ip_address`, `before_change`, `after_change`, `create_time`, `user_id`) VALUES (7, '凭据管理', '/api/credentials/16/delete/', 'DELETE', '172.20.0.1', '{\"id\": 16, \"name\": \"测试demo\", \"type\": \"密码\", \"account\": \"root\", \"password\": \"***\", \"key\": \"***\", \"key_password\": \"***\", \"KeyId\": \"\", \"KeySecret\": \"***\", \"notes\": \"\"}', '{}', '2024-12-24 14:11:45.740053', 1);
INSERT INTO `t_operation_log` (`id`, `module`, `request_interface`, `request_method`, `ip_address`, `before_change`, `after_change`, `create_time`, `user_id`) VALUES (8, '凭据管理', '/api/credentials/7/delete/', 'DELETE', '172.20.0.1', '{\"id\": 7, \"name\": \"bc\", \"type\": \"密钥\", \"account\": \"root\", \"password\": \"***\", \"key\": \"***\", \"key_password\": \"***\", \"KeyId\": \"\", \"KeySecret\": \"***\", \"notes\": \"\"}', '{}', '2024-12-24 14:11:47.373818', 1);
INSERT INTO `t_operation_log` (`id`, `module`, `request_interface`, `request_method`, `ip_address`, `before_change`, `after_change`, `create_time`, `user_id`) VALUES (9, '凭据管理', '/api/credentials/1/delete/', 'DELETE', '172.20.0.1', '{\"id\": 1, \"name\": \"blog\", \"type\": \"密钥\", \"account\": \"root\", \"password\": \"***\", \"key\": \"***\", \"key_password\": \"***\", \"KeyId\": \"\", \"KeySecret\": \"***\", \"notes\": \"博客\"}', '{}', '2024-12-24 14:11:49.495917', 1);
INSERT INTO `t_operation_log` (`id`, `module`, `request_interface`, `request_method`, `ip_address`, `before_change`, `after_change`, `create_time`, `user_id`) VALUES (10, '凭据管理', '/api/credentials/12/delete/', 'DELETE', '172.20.0.1', '{\"id\": 12, \"name\": \"testaskey\", \"type\": \"AccessKey\", \"account\": \"root\", \"password\": \"***\", \"key\": \"***\", \"key_password\": \"***\", \"KeyId\": \"sadadsadsadsa\", \"KeySecret\": \"***\", \"notes\": \"\"}', '{}', '2024-12-24 14:12:04.549018', 1);
INSERT INTO `t_operation_log` (`id`, `module`, `request_interface`, `request_method`, `ip_address`, `before_change`, `after_change`, `create_time`, `user_id`) VALUES (11, '用户列表', '/api/users/admin/reset_password/', 'POST', '172.20.0.1', '{\"id\": 1, \"username\": \"admin\", \"name\": \"Admin\", \"password\": \"***\", \"email\": \"admin@example.com\", \"mobile\": \"1234567890\", \"status\": false, \"login_time\": \"2024-12-24T15:40:05.340430\", \"otp_secret_key\": null, \"mfa_level\": 0}', '{\"detail\": \"密码重置成功\", \"is_self_update\": true}', '2024-12-24 15:41:57.475090', 1);
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
) ENGINE=InnoDB AUTO_INCREMENT=41 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;

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
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;

-- ----------------------------
-- Records of t_system_settings
-- ----------------------------
BEGIN;
INSERT INTO `t_system_settings` (`id`, `watermark_enabled`, `ip_whitelist`, `ip_blacklist`, `update_time`, `multi_login_account`) VALUES (1, 0, '', '', '2024-12-18 15:01:15.387180', 'admin,demo');
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
) ENGINE=InnoDB AUTO_INCREMENT=216 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;

-- ----------------------------
-- Records of t_token
-- ----------------------------
BEGIN;
INSERT INTO `t_token` (`id`, `token`, `create_time`, `user_id`, `last_activity`) VALUES (215, 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzM1MDMzMzI5LCJpYXQiOjE3MzUwMjYxMjksImp0aSI6ImZiNjFmNjE5ODJiYjQzMmViNmY4NjUxYzVkODlhNDFlIiwidXNlcl9pZCI6MSwiaXNfcmVhZF9vbmx5IjpmYWxzZX0.QUtivhEBbWOe8NPpvV-tk9BBoODlab3bwyW03NZpDD8', '2024-12-24 15:42:09.255626', 1, '2024-12-24 15:42:09.255666');
COMMIT;

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
) ENGINE=InnoDB AUTO_INCREMENT=15 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;

-- ----------------------------
-- Records of t_user
-- ----------------------------
BEGIN;
INSERT INTO `t_user` (`id`, `username`, `name`, `password`, `email`, `mobile`, `status`, `login_time`, `create_time`, `update_time`, `mfa_level`, `otp_secret_key`) VALUES (1, 'admin', 'Admin', 'pbkdf2_sha256$600000$s17MLssMUxQl04t6Es1HsJ$Ow8h2Zr/lflRTqJ6l8YiiSeegWS0ewWIpfD7uZwkZh0=', 'admin@example.com', '1234567890', 0, '2024-12-24 15:42:09.359044', '2024-07-12 16:19:39.000000', '2024-12-24 15:42:09.359180', 0, NULL);
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
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;

-- ----------------------------
-- Records of t_user_lock
-- ----------------------------
BEGIN;
INSERT INTO `t_user_lock` (`id`, `login_count`, `lock_count`, `last_attempt_time`, `user_id`) VALUES (1, 0, 0, '2024-12-24 15:42:05.932071', 1);
COMMIT;

SET FOREIGN_KEY_CHECKS = 1;
