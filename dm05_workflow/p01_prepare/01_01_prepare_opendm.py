"""
功能：
    构建 OpenDM 程序镜像，下载并校验 DM0.5 权重。也可只下载权重。

输入：
    工作流 JSON 的 prepare_dir。
    默认使用固定版本的 OpenDM 基础镜像和源码；两种模式都获取 DM0.5 权重。

输出：
    opendm-dm05:prepared（默认模式）。
    prepare_dir/checkpoints/DM05 中的权重、模型配置和处理器文件。

运行：
    在 WSL Ubuntu 独立运行，也可由 00_02_run_pipeline.py 调度。
    仅下载权重时可在 Mac 运行，prepare_dir 可指向移动硬盘。

参数：
    --config：工作流 JSON，默认 configs/standard.json。
    --download-weights：只下载和校验权重。

被谁依赖：
    00_02_run_pipeline.py
"""

import sys
from pathlib import Path


if __name__ == '__main__':
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
    from dm05_workflow.p01_prepare._impl.p01_prepare import prepare_main

    prepare_main()
