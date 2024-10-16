# WebTerminal堡垒机

这是一个基于Django和Vue 3的WebTerminal堡垒机系统,支持SSH和RDP远程连接,提供用户管理和多连接管理功能。

## 功能特性

- 用户管理：支持用户列表查看、添加、编辑和删除
- SSH远程连接：使用Paramiko库实现安全的SSH连接
- RDP远程桌面连接：通过Guacamole协议实现RDP功能
- 基于浏览器的WebTerminal：使用xterm.js实现在线终端
- 多连接管理：支持同时管理多个远程连接
- 审计日志：记录用户操作和连接历史

## 技术栈

### 后端
- Python 3.x
- Django 3.x
- Paramiko (SSH连接)
- Guacamole协议 (RDP连接)
- Django Channels (WebSocket支持)

### 前端
- Vue 3
- Ant Design Vue
- xterm.js (WebTerminal)
- axios (HTTP请求)

## 安装

(这里添加安装说明)

## 使用

(这里添加使用说明)

## 开发

### 后端开发
1. 进入backend目录
2. 安装依赖: `pip install -r requirements.txt`
3. 运行开发服务器: `python manage.py runserver`

### 前端开发
1. 进入web目录
2. 安装依赖: `npm install`
3. 运行开发服务器: `npm run serve`

## 贡献

欢迎提交问题和拉取请求。对于重大更改,请先开issue讨论您想要更改的内容。

## 许可证

[MIT](https://choosealicense.com/licenses/mit/)

## 项目结构
