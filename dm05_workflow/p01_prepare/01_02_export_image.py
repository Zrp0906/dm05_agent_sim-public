"""
功能：
    把校验通过的 DM0.5 权重装进程序镜像，导出可迁移的 Docker 归档。

输入：
    本机镜像 opendm-dm05:prepared。
    prepare_dir/checkpoints/DM05。
    工作流 JSON 的 image_archive，父目录须已存在。

输出：
    opendm-dm05:with-weights，镜像内的模型目录为 /checkpoint。
    image_archive 指定的 .tar 文件。

运行：
    在有程序镜像和权重的 WSL Ubuntu 上独立运行，也可由 00_02_run_pipeline.py 调度。

参数：
    --config：工作流 JSON，默认 configs/standard.json。

被谁依赖：
    00_02_run_pipeline.py
"""

import sys
from pathlib import Path


if __name__ == '__main__':
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
    from dm05_workflow.p01_prepare._impl.p01_prepare import export_main

    export_main()
