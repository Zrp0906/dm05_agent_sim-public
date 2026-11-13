"""
功能：
    用已导入的镜像和本机 NVIDIA GPU 启动 OpenDM。

输入：
    opendm-dm05:with-weights 及镜像内 /checkpoint 的权重。
    Docker GPU 支持和可用的 7891 端口。

输出：
    前台 OpenDM 服务，提供 POST /v1/infer。

运行：
    在 GPU Ubuntu 主机独立运行，也可由 00_02_run_pipeline.py 调度。

参数：
    无

被谁依赖：
    00_02_run_pipeline.py
"""

import sys
from pathlib import Path


if __name__ == '__main__':
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
    from dm05_workflow.p02_inference._impl.p02_inference import start_main

    start_main()
