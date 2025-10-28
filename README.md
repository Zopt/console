# 云服务器控制面板

该项目提供一个简单的 Web 控制面板，可用于在服务器上查看基础信息并执行常用的控制命令。应用默认监听 `8888` 端口，通过访问 `http://<服务器 IP>:8888/doget` 即可打开面板。

## 功能特性

- 显示服务器当前 IP 地址
- 显示配置中的服务器密码/登录信息
- 查询 `ufw` 防火墙状态
- 一键执行重启、关机、防火墙开关等命令

## 安装部署

1. **克隆仓库并安装依赖**

   ```bash
   git clone <your-repo-url>
   cd console
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

2. **配置命令和密码**

   ```bash
   cp config.example.yaml config.yaml
   # 编辑 config.yaml，将命令和密码替换为适合当前服务器的设置
   ```

   - `server_password` 字段用于在页面上展示的密码或其他登录提示。
   - `commands` 字段中可以自定义不同操作对应的命令。命令既可以使用列表（逐个参数）也可以使用字符串（会按空格拆分）。确保运行服务的用户具备执行这些命令的权限，如果需要 `sudo` 请配置免密码或者调整命令。

3. **启动控制面板**

   ```bash
   FLASK_APP=app.py flask run --host=0.0.0.0 --port=8888
   ```

   或者直接使用：

   ```bash
   python app.py
   ```

4. **访问面板**

   在浏览器打开 `http://<服务器 IP>:8888/doget`，即可进入操作页面。

## 安全提示

- 运行该面板的用户将获得执行控制命令的能力，请务必限制访问来源或加上额外的身份验证机制。
- 示例命令使用 `sudo`，建议在生产环境配置免密码 `sudo` 或者改为使用 systemd/API 等更安全的方法。
- 如果服务器不使用 `ufw`，可以在 `commands` 中移除防火墙相关项，并忽略防火墙状态显示。

## 许可证

MIT
