"""
功能：
    检查阶段文档、编号入口和实现模块的文件名，核对入口集合并解析 Python 语法。

输入：
    dm05_workflow/、configs/standard.json、p00_cli.py 中的 STAGES。

输出：
    终端输出阶段和入口数量，或定位配置和文件布局问题。

运行：
    由 00_01_check_structure.py 导入并调用 main。

参数：
    无

被谁依赖：
    00_01_check_structure.py
"""

import argparse
import ast

from .p00_cli import STAGES
from .p00_common import DEFAULT_CONFIG, ROOT, load_workflow_config


def main() -> None:
    argparse.ArgumentParser(description=__doc__).parse_args()
    workflow = ROOT / 'dm05_workflow'
    load_workflow_config(DEFAULT_CONFIG)
    expected_entries = {
        'p00_pipeline/00_02_run_pipeline.py',
        *(entry for _, entries in STAGES.values() for entry in entries),
    }
    actual_entries = set()
    for stage_dir in sorted(workflow.glob('p[0-9][0-9]_*')):
        stage = stage_dir.name[1:3]
        if len(list(stage_dir.glob(f'{stage}_*.md'))) != 1:
            raise ValueError(f'{stage_dir.name} 应有一份对应的阶段说明')
        entries = sorted(path for path in stage_dir.glob('*.py') if path.name != '__init__.py')
        for number, entry in enumerate(entries, start=1):
            if not entry.name.startswith(f'{stage}_{number:02d}_'):
                raise ValueError(f'入口编号不连续: {entry.name}')
            actual_entries.add(entry.relative_to(workflow).as_posix())
        for source in (stage_dir / '_impl').glob('*.py'):
            if source.name != '__init__.py' and not source.name.startswith(f'p{stage}_'):
                raise ValueError(f'实现文件的阶段编号有误: {source.name}')

    if actual_entries != expected_entries:
        raise ValueError(f'调度表与入口不一致: {sorted(actual_entries ^ expected_entries)}')
    for source in workflow.rglob('*.py'):
        ast.parse(source.read_text(encoding='utf-8'), filename=str(source))
    print(f'[OK] {len(STAGES)} 个阶段，{len(actual_entries)} 个编号入口，配置与调度表通过检查。')
