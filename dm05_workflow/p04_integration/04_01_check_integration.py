"""
功能：
    用三路 MuJoCo 图像和 14 维状态向 OpenDM 请求一次推理，并把首个动作提交给仿真。

输入：
    工作流 JSON、其中指定的 Agent YAML，以及可用的 OpenDM 服务。

输出：
    integration_report 指定的 JSON，默认 outputs/integration.json。

运行：
    在 Mac 独立运行，也可由 00_02_run_pipeline.py 调度。

参数：
    --config：工作流 JSON，默认 configs/standard.json。
    --task：推理指令，默认读取 Agent YAML 的 orchestrator.fixed_prompt。

被谁依赖：
    00_02_run_pipeline.py
"""

import sys
from pathlib import Path


if __name__ == '__main__':
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
    from dm05_workflow.p04_integration._impl.p04_integration import main

    main()
