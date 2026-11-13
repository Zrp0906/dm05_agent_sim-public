"""
功能：
    读取 Agent YAML；解析场景和语音配置的路径，并检查 MuJoCo 的动作类型。

输入：
    Agent YAML；可选的 robot.physics_scene 和 voice_config。

输出：
    Agent 配置字典；交互模式可另取语音配置字典。

运行：
    作为依赖导入，不单独运行。相对文件先查 Agent YAML 所在目录，再查项目根目录。

参数：
    无

被谁依赖：
    p03_launch.py
    p04_integration.py
    p03_verify_runtime.py
"""

import os
from pathlib import Path

import yaml


PROJECT_ROOT = str(Path(__file__).resolve().parents[3])


def load_config(config_path: str) -> dict:
    with open(config_path) as file:
        config = yaml.safe_load(file)
    if not isinstance(config, dict):
        raise ValueError(f'Agent YAML 必须是映射: {config_path}')
    if config['robot']['type'] == 'mujoco':
        if str((config.get('low_level') or {}).get('action_type', 'JOINT')).upper() != 'JOINT':
            raise ValueError('MuJoCo simulation requires a JOINT low-level model.')
        scene = config['robot'].get('physics_scene')
        if scene:
            config['robot']['physics_scene'] = _resolve_config_path(scene, config_path)
    return config


def _resolve_config_path(path: str, base_config_path: str) -> str:
    if os.path.isabs(path):
        return path
    candidate = os.path.join(os.path.dirname(os.path.abspath(base_config_path)), path)
    if os.path.isfile(candidate):
        return candidate
    return os.path.join(PROJECT_ROOT, path)


def load_voice_config(config: dict, config_path: str) -> dict:
    raw_path = str(config.get('voice_config') or '').strip()
    if not raw_path:
        return {}
    voice_path = _resolve_config_path(raw_path, config_path)
    if not os.path.isfile(voice_path):
        raise FileNotFoundError(f'voice_config not found: {voice_path}')
    with open(voice_path) as file:
        data = yaml.safe_load(file) or {}
    return data.get('voice', data) or {}
