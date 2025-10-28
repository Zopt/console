"""Flask application providing a simple server control panel."""
from __future__ import annotations

import subprocess
from typing import List

from flask import Flask, redirect, render_template, request, url_for

from control import ControlService, load_config

app = Flask(__name__)
config = load_config()
service = ControlService(config)


@app.route("/doget", methods=["GET"])
def dashboard() -> str:
    ip_addresses = _get_ip_addresses()
    firewall_status = service.get_firewall_status()
    return render_template(
        "dashboard.html",
        ip_addresses=ip_addresses,
        password=config.server_password or "未设置 (请在 config.yaml 中配置)",
        firewall_status=firewall_status,
        message=request.args.get("message"),
        error=request.args.get("error"),
    )


@app.route("/doget/action", methods=["POST"])
def perform_action():
    action = request.form.get("action", "")
    success, message = service.execute(action)
    query = {"message": message} if success else {"error": message}
    return redirect(url_for("dashboard", **query))


def _get_ip_addresses() -> List[str]:
    """Fetch a list of IP addresses using the hostname command."""
    try:
        output = subprocess.check_output(["hostname", "-I"], text=True)
    except (FileNotFoundError, subprocess.CalledProcessError):
        return ["未知 (无法获取 IP 地址)"]
    addresses = [addr for addr in output.split() if addr.strip()]
    return addresses or ["未知"]


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8888)
