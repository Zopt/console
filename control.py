"""Utility helpers for executing server control actions."""
from __future__ import annotations

import os
import shlex
import subprocess
from dataclasses import dataclass, field
from typing import Dict, List, Sequence, Tuple

import yaml

DEFAULT_CONFIG_PATH = "config.yaml"


@dataclass
class ActionConfig:
    """Definition of a button/action that can be triggered from the UI."""

    name: str
    label: str
    command: List[str]
    style: str = "primary"
    confirm: str | None = None


def _default_actions() -> List[ActionConfig]:
    return [
        ActionConfig(
            name="restart",
            label="重启服务器",
            command=["sudo", "reboot"],
            style="primary",
            confirm="确定要重启服务器吗？",
        ),
        ActionConfig(
            name="shutdown",
            label="关闭服务器",
            command=["sudo", "shutdown", "-h", "now"],
            style="danger",
            confirm="确定要立即关闭服务器吗？",
        ),
        ActionConfig(
            name="firewall_enable",
            label="开启防火墙",
            command=["sudo", "ufw", "enable"],
            style="secondary",
        ),
        ActionConfig(
            name="firewall_disable",
            label="关闭防火墙",
            command=["sudo", "ufw", "disable"],
            style="danger",
        ),
    ]


@dataclass
class ControlConfig:
    """Configuration container for the control panel."""

    actions: List[ActionConfig] = field(default_factory=_default_actions)
    server_password: str = ""
    ip_command: List[str] = field(default_factory=lambda: ["hostname", "-I"])
    firewall_status_command: List[str] = field(
        default_factory=lambda: ["sudo", "ufw", "status"]
    )

    @classmethod
    def from_dict(cls, data: Dict[str, object]) -> "ControlConfig":
        password = str(data.get("server_password", ""))
        ip_command = _normalise_command(
            data.get("ip_command"), default=["hostname", "-I"]
        )
        firewall_cmd = _normalise_command(
            data.get("firewall_status_command"), default=["sudo", "ufw", "status"]
        )
        actions = _parse_actions(data.get("actions"))
        return cls(
            actions=actions if actions is not None else _default_actions(),
            server_password=password,
            ip_command=ip_command,
            firewall_status_command=firewall_cmd,
        )


class ControlService:
    """Service wrapper that runs configured system commands."""

    def __init__(self, config: ControlConfig | None = None) -> None:
        self.config = config or load_config()

    def execute(self, action: str) -> Tuple[bool, str]:
        """Execute an action and return the status and message."""
        action_config = self.get_action(action)
        if not action_config:
            return False, f"未知的操作: {action}"
        try:
            subprocess.run(action_config.command, check=True)
        except FileNotFoundError:
            return False, "命令不存在，请检查配置。"
        except subprocess.CalledProcessError as exc:  # pragma: no cover - requires system commands
            return False, f"执行失败 (退出码 {exc.returncode})。"
        return True, "操作执行成功。"

    def get_firewall_status(self) -> str:
        """Return the firewall status using the configured firewall command."""
        try:
            result = subprocess.check_output(
                self.config.firewall_status_command, text=True
            )
        except (subprocess.CalledProcessError, FileNotFoundError):
            return "未知 (无法查询防火墙状态)"
        return result.strip() or "未知"

    def get_action(self, action_name: str) -> ActionConfig | None:
        """Return the configuration for a specific action."""
        for action in self.config.actions:
            if action.name == action_name:
                return action
        return None


def load_config(path: str = DEFAULT_CONFIG_PATH) -> ControlConfig:
    """Load configuration from YAML if available."""
    custom_path = os.getenv("CONTROL_CONFIG")
    if custom_path:
        path = custom_path
    if not os.path.exists(path):
        return ControlConfig()
    with open(path, "r", encoding="utf-8") as fp:
        data = yaml.safe_load(fp) or {}
    if not isinstance(data, dict):
        raise ValueError("配置文件格式必须是映射 (YAML 对象)。")
    return ControlConfig.from_dict(data)


def _normalise_command(value: object, default: Sequence[str]) -> List[str]:
    if not value:
        return list(default)
    if isinstance(value, list):
        return [str(part) for part in value]
    if isinstance(value, str):
        return shlex.split(value)
    raise TypeError("命令配置必须是字符串或字符串数组。")


def _parse_actions(value: object) -> List[ActionConfig] | None:
    if value is None:
        return None
    if isinstance(value, list):
        return [_parse_action_dict(item) for item in value]
    if isinstance(value, dict):
        actions: List[ActionConfig] = []
        for name, cfg in value.items():
            merged = {"name": name}
            if isinstance(cfg, dict):
                merged.update(cfg)
            else:
                merged["command"] = cfg
            actions.append(_parse_action_dict(merged))
        return actions
    raise TypeError("actions 配置必须是数组或映射。")


def _parse_action_dict(raw: object) -> ActionConfig:
    if not isinstance(raw, dict):
        raise TypeError("每个 action 必须是对象类型。")
    if "name" not in raw:
        raise ValueError("action 配置缺少 name 字段。")
    if "command" not in raw:
        raise ValueError("action 配置缺少 command 字段。")
    command = _normalise_command(raw.get("command"), default=[])
    if not command:
        raise ValueError("action command 不能为空。")
    label = str(raw.get("label") or raw["name"])
    style = str(raw.get("style") or "primary")
    confirm = raw.get("confirm")
    if confirm is not None:
        confirm = str(confirm)
    return ActionConfig(
        name=str(raw["name"]),
        label=label,
        command=command,
        style=style,
        confirm=confirm,
    )
