"""
功能：
    读取发布清单，逐个校验文件的 SHA-256。

输入：
    MANIFEST.sha256 和其中列出的文件。

输出：
    终端完整性检查结果；缺失或哈希不符时返回失败状态。

运行：
    由 00_01_check_structure.py 在阶段 00 调用。

参数：
    无

被谁依赖：
    00_01_check_structure.py
"""

from __future__ import annotations

import hashlib

from .p00_common import ROOT


def main() -> int:
    manifest = ROOT / "MANIFEST.sha256"
    failures = []

    for line in manifest.read_text(encoding="utf-8").splitlines():
        expected, relative = line.split("  ", 1)
        path = ROOT / relative
        if not path.is_file():
            failures.append(f"缺少文件: {relative}")
            continue
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        if actual != expected:
            failures.append(f"文件已变化: {relative}")

    if failures:
        print("[FAIL] 完整性检查未通过:")
        for failure in failures:
            print(f"  - {failure}")
        return 1

    print("[OK] 交付包完整性检查通过。")
    return 0
