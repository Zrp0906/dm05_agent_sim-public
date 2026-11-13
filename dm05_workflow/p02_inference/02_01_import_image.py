"""
功能：
    将含 OpenDM 程序、环境和权重的 Docker 归档导入目标主机。

输入：
    工作流 JSON 的 image_archive 指向的 .tar 文件。

输出：
    本机 Docker 镜像 opendm-dm05:with-weights。

运行：
    在 GPU Ubuntu 主机独立运行，也可由 00_02_run_pipeline.py 调度。

参数：
    --config：工作流 JSON，默认 configs/standard.json。

被谁依赖：
    00_02_run_pipeline.py
"""

import sys
from pathlib import Path


if __name__ == '__main__':
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
    from dm05_workflow.p02_inference._impl.p02_inference import import_main

    import_main()
