"""
功能：
    读取 Agent YAML，按配置启动直控、交互或自动编排，也可启动固定任务。

输入：
    Agent YAML，包含 robot.type、推理服务和编排设置。
    固定任务读取 orchestrator.fixed_prompt。

输出：
    直控、交互或固定任务模式提供网页；自动编排运行任务控制循环。

运行：
    可在项目根目录独立运行；Mac 仿真可由 00_02_run_pipeline.py 调度。

参数：
    --config：Agent YAML，必填。
    --fixed-task：以预设指令启动固定任务网页。

被谁依赖：
    00_02_run_pipeline.py
"""

import sys
from pathlib import Path


if __name__ == '__main__':
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
    from dm05_workflow.p03_agent._impl.p03_launch import main

    main()
