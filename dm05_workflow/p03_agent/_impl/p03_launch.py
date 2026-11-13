"""
功能：
    读取启动参数和 YAML，设置日志，构建所选编排器并启动。直控分支按配置启用录制。

输入：
    --config 指定的 Agent YAML；交互分支可读取语音配置。

输出：
    任务控制循环或前台网页服务，以及配置指定的日志。

运行：
    由 03_01_start_agent.py 导入并调用 main。

参数：
    无独立命令行参数；见 03_01_start_agent.py。

被谁依赖：
    03_01_start_agent.py
"""

import argparse

from agent.log import get_logger, setup_logging

from .p03_config import load_config, load_voice_config
from .p03_orchestrators import (
    build_auto,
    build_direct_low_level,
    build_fixed_task,
    build_interactive,
    run_orchestrator,
)
from .p03_recording import apply_trajectory_recording, install_front_recording


logger = get_logger('agent')


def main() -> None:
    parser = argparse.ArgumentParser(description='启动 Agent 网页')
    parser.add_argument('--config', required=True, help='Agent YAML 配置文件')
    parser.add_argument('--fixed-task', action='store_true', help='使用 YAML 中的固定任务')
    args = parser.parse_args()
    config = load_config(args.config)
    orch_config = config.get('orchestrator') or {}
    log_dir = orch_config.get('log_dir', './logs')
    setup_logging(log_dir=log_dir)
    logger.info(f'Loaded config from {args.config}')

    mode = 'fixed_task' if args.fixed_task else orch_config.get('mode', 'auto')
    if mode == 'fixed_task':
        logger.info('Orchestrator mode: fixed_task')
        orchestrator = build_fixed_task(config)
    elif mode == 'interactive':
        logger.info('Orchestrator mode: interactive')
        orchestrator = build_interactive(config, voice_config=load_voice_config(config, args.config))
    elif mode == 'direct_low_level':
        logger.info('Orchestrator mode: direct_low_level')
        apply_trajectory_recording(config)
        install_front_recording(config)
        orchestrator = build_direct_low_level(config)
    elif mode == 'auto':
        logger.info(f'Orchestrator mode: auto, task={config.get("task")!r}')
        orchestrator = build_auto(config, log_dir=log_dir)
    else:
        raise ValueError(f'Unknown orchestrator.mode: {mode}')

    run_orchestrator(orchestrator, config)
