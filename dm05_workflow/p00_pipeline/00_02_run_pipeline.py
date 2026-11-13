"""
功能：
    预览完整的部署路线，或用子进程运行当前机器负责的一个阶段。

输入：
    工作流 JSON，默认 configs/standard.json。

输出：
    打印每个阶段的执行机器和命令；执行时由各编号脚本生成产物。

运行：
    在项目根目录独立运行。实际执行时选定一个阶段。

参数：
    --config：工作流 JSON，默认 configs/standard.json。
    --from-stage、--to-stage：阶段范围，取值 0–4。只给一个边界时执行或预览该阶段。
    --dry-run：只打印命令。省略范围时预览 00–04。
    --dos-w1：阶段 03 使用 DOS-W1 真机并启动本机机械臂服务。
    --agent-config：指定阶段 03 使用的 Agent YAML。

被谁依赖：
    无
"""

import sys
from pathlib import Path


if __name__ == '__main__':
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
    from dm05_workflow.p00_pipeline._impl.p00_cli import main

    main()
