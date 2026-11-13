"""
功能：
    用 docker load 导入归档；启动时运行容器，从 /checkpoint 加载模型并配置三路相机和 14 维动作。

输入：
    导入读取工作流 JSON 的 image_archive。
    启动使用本机 opendm-dm05:with-weights 镜像和 NVIDIA GPU。

输出：
    导入后的本机镜像；启动后在 7891 端口提供推理接口。

运行：
    由编号入口导入并调用 import_main 或 start_main。

参数：
    无独立命令行参数；导入参数见 02_01_import_image.py。

被谁依赖：
    02_01_import_image.py
    02_02_start_inference.py
"""

import argparse
import os
import subprocess

from dm05_workflow.p00_pipeline._impl.p00_common import add_config_argument, load_workflow_config


def import_main() -> None:
    parser = argparse.ArgumentParser(description='导入 OpenDM Docker 镜像归档')
    add_config_argument(parser)
    args = parser.parse_args()
    archive = load_workflow_config(args.config).image_archive
    subprocess.run(['docker', 'load', '-i', str(archive)], check=True)


def start_main() -> None:
    argparse.ArgumentParser(description='在 GPU 主机启动 DM0.5 HTTP 服务').parse_args()
    os.execvp('docker', [
        'docker', 'run', '--rm', '-it', '--pull=never', '--gpus', 'all', '--shm-size=16g',
        '-p', '7891:7891', '--workdir', '/opt/opendm', 'opendm-dm05:with-weights',
        '/opt/conda/bin/conda', 'run', '--no-capture-output', '-n', 'opendm',
        'bash', 'script/dm05_launcher.sh', '--exp', 'opendm/exp/dm05_exp.py',
        '--task', 'inference',
        '--model-config.model-name-or-path', '/checkpoint',
        '--model-config.chunk-size', '50',
        '--inference-config.output-action-dim', '14',
        '--inference-config.image-prompts', 'Head', 'Left wrist', 'Right wrist',
        '--inference-config.port', '7891',
    ])
