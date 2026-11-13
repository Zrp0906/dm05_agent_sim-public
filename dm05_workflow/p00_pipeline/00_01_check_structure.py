"""
功能：
    检查阶段说明、入口编号、实现文件命名和调度表，解析工作流源码并核对文件哈希。

输入：
    dm05_workflow/ 下的阶段目录、Markdown 和 Python 源码。
    configs/standard.json、p00_cli.py 的阶段调度表和 MANIFEST.sha256。

输出：
    终端检查结果；失败时报告缺少或不一致的条目。

运行：
    在项目根目录独立运行。

参数：
    无

被谁依赖：
    00_02_run_pipeline.py
"""

import sys
from pathlib import Path


if __name__ == '__main__':
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
    from dm05_workflow.p00_pipeline._impl.p00_structure import main
    from dm05_workflow.p00_pipeline._impl.p00_verify_integrity import main as verify_integrity

    main()
    raise SystemExit(verify_integrity())
