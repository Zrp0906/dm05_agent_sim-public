"""
功能：
    提供项目根目录和默认配置路径，读取并校验工作流 JSON。

输入：
    configs/standard.json 或自定义工作流 JSON。
    配置字段 prepare_dir、image_archive、agent_config、fixed_task、integration_report。

输出：
    WorkflowConfig，路径按项目根目录解析，支持 ~ 表示用户目录。

运行：
    作为依赖导入，不单独运行。

参数：
    无

被谁依赖：
    p00_cli.py
    p00_structure.py
    p01_prepare.py
    p02_inference.py
    p04_integration.py
"""

import argparse
from dataclasses import dataclass
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
DEFAULT_CONFIG = ROOT / 'configs/standard.json'


@dataclass(frozen=True)
class WorkflowConfig:
    prepare_dir: Path
    image_archive: Path
    agent_config: Path
    fixed_task: bool
    integration_report: Path


def add_config_argument(parser: argparse.ArgumentParser) -> None:
    parser.add_argument('--config', type=Path, default=DEFAULT_CONFIG, help='工作流 JSON 配置')


def load_workflow_config(path: Path) -> WorkflowConfig:
    data = json.loads(path.read_text(encoding='utf-8'))

    def project_path(key: str) -> Path:
        value = data[key]
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f'{key} 必须是非空路径')
        return (ROOT / Path(value).expanduser()).resolve()

    fixed_task = data['fixed_task']
    if not isinstance(fixed_task, bool):
        raise ValueError('fixed_task 必须是布尔值')
    return WorkflowConfig(
        prepare_dir=project_path('prepare_dir'),
        image_archive=project_path('image_archive'),
        agent_config=project_path('agent_config'),
        fixed_task=fixed_task,
        integration_report=project_path('integration_report'),
    )
