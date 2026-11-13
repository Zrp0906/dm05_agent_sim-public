"""
功能：
    读取准备和导出参数，调用 p01_prepare_opendm.sh。打包后通过 docker save 写入同目录临时文件，再替换目标归档。

输入：
    工作流 JSON 的 prepare_dir 和 image_archive。
    构建使用固定版本的镜像与源码；导出使用本机程序镜像和已校验权重。

输出：
    程序镜像、权重目录、带权重的镜像及 Docker 归档，具体产物由所选入口决定。

运行：
    由编号入口导入并调用 prepare_main 或 export_main。

参数：
    无独立命令行参数；见 01_01_prepare_opendm.py 和 01_02_export_image.py。

被谁依赖：
    01_01_prepare_opendm.py
    01_02_export_image.py
"""

import argparse
import subprocess
from pathlib import Path
from tempfile import TemporaryDirectory

from dm05_workflow.p00_pipeline._impl.p00_common import add_config_argument, load_workflow_config


PREPARE_SCRIPT = Path(__file__).with_name('p01_prepare_opendm.sh')


def prepare_main() -> None:
    parser = argparse.ArgumentParser(description='构建 OpenDM 程序镜像并下载权重')
    add_config_argument(parser)
    parser.add_argument('--download-weights', action='store_true', help='只下载和校验权重')
    args = parser.parse_args()
    config = load_workflow_config(args.config)
    mode = 'download' if args.download_weights else 'prepare'
    subprocess.run(['bash', str(PREPARE_SCRIPT), mode, str(config.prepare_dir)], check=True)


def export_main() -> None:
    parser = argparse.ArgumentParser(description='将已准备的程序和权重打包为 Docker 归档')
    add_config_argument(parser)
    args = parser.parse_args()
    config = load_workflow_config(args.config)
    archive = config.image_archive
    if not archive.parent.is_dir():
        parser.error(f'归档目录不存在: {archive.parent}')

    subprocess.run(['bash', str(PREPARE_SCRIPT), 'bundle', str(config.prepare_dir)], check=True)
    with TemporaryDirectory(prefix='.opendm-export-', dir=archive.parent) as directory:
        temporary = Path(directory) / archive.name
        subprocess.run(['docker', 'save', '-o', str(temporary), 'opendm-dm05:with-weights'], check=True)
        temporary.replace(archive)
    print(f'归档: {archive}')
