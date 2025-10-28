"""Utility helpers for executing server control actions."""
from __future__ import annotations

import os
import subprocess
from dataclasses import dataclass, field
from typing import Dict, List, Tuple

import yaml

DEFAULT_CONFIG_PATH = "config.yaml"

DEFAULT_COMMANDS = {
    "restart": ["sudo", "reboot"],
    "shutdown": ["sudo", "shutdown", "-h", "now"],
    "firewall_enable": ["sudo", "ufw", "enable"],
    "firewall_disable": ["sudo", "ufw", "disable"],
}


@dataclass
class ControlConfig:
    """Configuration container for the control panel."""

    commands: Dict[str, List[str]] = field(default_factory=lambda: DEFAULT_COMMANDS.copy())
    server_password: str = ""

    @classmethod
    def from_dict(cls, data: Dict[str, object]) -> "ControlConfig":
        commands = DEFAULT_COMMANDS.copy()
        user_commands = data.get("commands") or {}
        for key, value in user_commands.items():
            if isinstance(value, list):
                commands[key] = [str(part) for part in value]
            elif isinstance(value, str):
                commands[key] = value.split()
        password = str(data.get("server_password", ""))
        return cls(commands=commands, server_password=password)


class ControlService:
    """Service wrapper that runs configured system commands."""

    def __init__(self, config: ControlConfig | None = None) -> None:
        self.config = config or load_config()

    def execute(self, action: str) -> Tuple[bool, str]:
        """Execute an action and return the status and message."""
        command = self.config.commands.get(action)
        if not command:
            return False, f"未知的操作: {action}"
        try:
            subprocess.run(command, check=True)
        except FileNotFoundError:
            return False, "命令不存在，请检查配置。"
        except subprocess.CalledProcessError as exc:  # pragma: no cover - requires system commands
            return False, f"执行失败 (退出码 {exc.returncode})。"
        return True, "操作执行成功。"

    def get_firewall_status(self) -> str:
        """Return the firewall status using ufw when available."""
        try:
            result = subprocess.check_output(["sudo", "ufw", "status"], text=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            return "未知 (无法查询 ufw 状态)"
        return result.strip() or "未知"


def load_config(path: str = DEFAULT_CONFIG_PATH) -> ControlConfig:
    """Load configuration from YAML if available."""
    if not os.path.exists(path):
        return ControlConfig()
    with open(path, "r", encoding="utf-8") as fp:
        data = yaml.safe_load(fp) or {}
    if not isinstance(data, dict):
        raise ValueError("配置文件格式必须是映射 (YAML 对象)。")
    return ControlConfig.from_dict(data)
