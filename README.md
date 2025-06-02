# P2P拼车系统 (Peer-to-Peer Carpooling)

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/Python-3.8-green.svg)
![Django](https://img.shields.io/badge/Django-latest-green.svg)

## 项目简介

P2P拼车系统是一个现代化的点对点拼车平台，旨在为用户提供便捷、环保、经济的出行解决方案。通过该平台，车主可以发布行程信息，乘客可以搜索并预订合适的拼车路线，实现资源共享和高效出行。

### 主要特点

- 🚗 智能路线匹配
- 👥 实时用户互动
- 🔐 安全的用户认证系统
- 📱 响应式现代界面设计
- 💰 便捷的在线预订系统
- 🗺️ 直观的行程管理

## 技术栈

- **前端**: HTML5, CSS3, JavaScript
- **后端**: Python, Django
- **数据库**: MySQL
- **开发工具**: VS Code
- **版本控制**: Git

## 功能模块

1. **用户管理**
   - 注册与登录
   - 个人信息管理
   - 密码修改

2. **行程管理**
   - 发布行程
   - 搜索行程
   - 行程预订
   - 行程状态追踪

3. **车辆管理**
   - 添加车辆信息
   - 管理车辆状态
   - 查看所有车辆

4. **预订系统**
   - 在线预订
   - 预订确认
   - 预订历史记录

## 快速开始

### 环境要求

- Python 3.8
- MySQL（最新版本）
- VS Code

### 安装步骤

1. **克隆项目**
   ```bash
   git clone [项目地址]
   cd Peer-to-Peer-Carpooling
   ```

2. **创建并激活虚拟环境**
   ```bash
   python -m venv env
   .\env\Scripts\activate
   ```

3. **安装依赖**
   ```bash
   pip install django
   pip install requests
   pip install cryptography
   pip install mysql-connector-python
   pip install pillow
   pip install pymysql
   ```

4. **配置数据库**
   - 在MySQL中创建数据库
   - 更新 `carpool/carpool/settings.py` 中的数据库配置
   - 更新 `carpool/website/views.py` 中的数据库连接信息

5. **运行数据库迁移**
   ```bash
   cd carpool
   python manage.py makemigrations
   python manage.py migrate
   ```

6. **启动服务器**
   ```bash
   python manage.py runserver
   ```
   访问 http://127.0.0.1:8000/ 即可使用系统

## 项目结构

```
Peer-to-Peer-Carpooling/
├── carpool/
│   ├── website/          # 主应用目录
│   │   ├── static/     # 静态文件
│   │   │   ├── images/ # 图片资源
│   │   │   ├── css/    # 样式文件
│   │   │   └── js/     # JavaScript文件
│   │   └── templates/  # HTML模板
│   └── env/                # 虚拟环境
```

## 注意事项

- 所有上传的车辆图片都保存在 `static/images/cars` 目录下
- 运行服务器时使用 `Ctrl+C` 可以停止服务
- 确保数据库配置正确且MySQL服务正在运行

## 贡献指南

欢迎提交问题和改进建议！如果您想为项目做出贡献，请：

1. Fork 本仓库
2. 创建您的特性分支
3. 提交您的改动
4. 推送到您的分支
5. 创建一个 Pull Request

## 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件
