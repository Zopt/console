# 云服务器控制面板

该项目提供一个简单的 Web 控制面板，可用于在服务器上查看基础信息并执行常用的控制命令。应用默认监听 `8888` 端口，通过访问 `http://<服务器 IP>:8888/doget` 即可打开面板。

## 功能特性

- 显示服务器当前 IP 地址
- 显示配置中的服务器密码/登录信息
- 查询防火墙状态（默认调用 `ufw status`，可自定义）
- 一键执行重启、关机、防火墙开关等自定义命令
- 按钮支持自定义名称、样式及确认提示

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

   配置文件支持以下字段：

   | 字段 | 类型 | 说明 |
   | --- | --- | --- |
   | `server_password` | `string` | 页面上显示的密码或登录提示信息 |
   | `ip_command` | `string`/`string[]` | 获取 IP 地址的命令，默认 `hostname -I` |
   | `firewall_status_command` | `string`/`string[]` | 查询防火墙状态的命令，默认 `sudo ufw status` |
   | `actions` | `array`/`object` | 自定义按钮。每个按钮包含 `name`、`label`、`command`、可选 `style`(`primary`/`secondary`/`danger`/`warning`) 与 `confirm` 字段 |

   命令字段可使用字符串（将按 shell 规则拆分）或字符串数组（逐个参数）。确保运行服务的用户具备执行这些命令的权限，如果需要 `sudo` 请配置免密码或者调整命令。

3. **启动控制面板**

   ```bash
   FLASK_APP=app.py flask run --host=0.0.0.0 --port=8888
   ```

   或者直接使用：

   ```bash
   python app.py
   ```

   可通过设置环境变量 `CONTROL_CONFIG` 指定其他配置文件路径。

4. **访问面板**

   在浏览器打开 `http://<服务器 IP>:8888/doget`，即可进入操作页面。

## 安全提示

- 运行该面板的用户将获得执行控制命令的能力，请务必限制访问来源或加上额外的身份验证机制。
- 示例命令使用 `sudo`，建议在生产环境配置免密码 `sudo` 或者改为使用 systemd/API 等更安全的方法。
- 如果服务器不使用 `ufw`，可以在 `actions` 中移除防火墙相关项，或修改 `firewall_status_command`。
- 如需自动拉起服务，可结合 systemd/pm2/docker 等方式部署。

## 许可证

MIT
