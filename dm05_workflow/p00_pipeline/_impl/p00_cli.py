"""
功能：
    维护阶段、执行机器和脚本的对应关系。读取配置，生成参数并按顺序启动子进程。

输入：
    工作流 JSON、阶段范围、预览开关。
    阶段 03 使用 Agent YAML 和 JSON 的 fixed_task，可显式选择 DOS-W1 真机。

输出：
    打印执行机器和命令；实际运行时等待子进程，失败后停止。

运行：
    由 00_02_run_pipeline.py 导入；结构检查读取 STAGES。

参数：
    无独立命令行参数；总入口参数见 00_02_run_pipeline.py。

被谁依赖：
    00_02_run_pipeline.py
    p00_structure.py
"""

from __future__ import annotations

import argparse
from pathlib import Path
import shlex
import subprocess
import sys

from .p00_common import ROOT, WorkflowConfig, add_config_argument, load_workflow_config


DOS_W1_CONFIG = ROOT / 'agent/config/direct_maas.local.yaml'
DOS_W1_START = ROOT / 'dm05_workflow/p03_agent/_impl/p03_start_dos_w1.sh'

# 每个阶段列出操作机器和可独立运行的入口。
STAGES = {
    0: ('任意机器', ('p00_pipeline/00_01_check_structure.py',)),
    1: ('WSL Ubuntu', (
        'p01_prepare/01_01_prepare_opendm.py',
        'p01_prepare/01_02_export_image.py',
    )),
    2: ('GPU Ubuntu', (
        'p02_inference/02_01_import_image.py',
        'p02_inference/02_02_start_inference.py',
    )),
    3: ('Mac', ('p03_agent/03_01_start_agent.py',)),
    4: ('Mac', ('p04_integration/04_01_check_integration.py',)),
}


def commands_for_stage(
    stage: int,
    config_path: Path,
    config: WorkflowConfig,
    *,
    dos_w1: bool = False,
    agent_config: Path | None = None,
) -> list[list[str]]:
    _, entries = STAGES[stage]
    if stage == 0:
        return [[sys.executable, str(ROOT / 'dm05_workflow' / entries[0])]]
    if stage == 3:
        selected_config = agent_config or (DOS_W1_CONFIG if dos_w1 else config.agent_config)
        options = ['--config', str((ROOT / selected_config.expanduser()).resolve())]
        if config.fixed_task:
            options.append('--fixed-task')
        verify = [sys.executable, '-m', 'dm05_workflow.p03_agent._impl.p03_verify_runtime', *options]
        launch = [sys.executable, str(ROOT / 'dm05_workflow' / entries[0]), *options]
        if dos_w1:
            verify.append('--dos-w1')
            return [verify, ['bash', str(DOS_W1_START)], launch]
        return [verify, launch]

    commands = []
    for entry in entries:
        command = [sys.executable, str(ROOT / 'dm05_workflow' / entry)]
        if entry != 'p02_inference/02_02_start_inference.py':
            command.extend(['--config', str(config_path)])
        commands.append(command)
    return commands


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    add_config_argument(parser)
    parser.add_argument('--from-stage', type=int, choices=STAGES)
    parser.add_argument('--to-stage', type=int, choices=STAGES)
    parser.add_argument('--dry-run', action='store_true', help='只列出命令和操作机器')
    parser.add_argument('--dos-w1', action='store_true', help='阶段 03 使用 DOS-W1 真机并启动本机机械臂服务')
    parser.add_argument('--agent-config', type=Path, help='阶段 03 使用的 Agent YAML')
    args = parser.parse_args()
    bounds = [stage for stage in (args.from_stage, args.to_stage) if stage is not None]
    first, last = (bounds[0], bounds[-1]) if bounds else (min(STAGES), max(STAGES))
    if first > last:
        parser.error('--from-stage 必须小于或等于 --to-stage')
    if not args.dry_run and first != last:
        parser.error('请选择一个阶段执行，例如 --from-stage 1 --to-stage 1；完整路线用 --dry-run')
    if (args.dos_w1 or args.agent_config is not None) and (first, last) != (3, 3):
        parser.error('--dos-w1 和 --agent-config 用于单独执行或预览第 03 阶段')

    config_path = args.config.resolve()
    config = load_workflow_config(config_path)
    for stage in range(first, last + 1):
        machine, _ = STAGES[stage]
        if stage == 3 and args.dos_w1:
            machine = 'Linux · DOS-W1'
        print(f'[{stage:02d} · {machine}]', flush=True)
        commands = commands_for_stage(stage, config_path, config, dos_w1=args.dos_w1, agent_config=args.agent_config)
        for command in commands:
            print(shlex.join(command), flush=True)
            if not args.dry_run:
                result = subprocess.run(command, cwd=ROOT)
                if result.returncode:
                    raise SystemExit(result.returncode)
