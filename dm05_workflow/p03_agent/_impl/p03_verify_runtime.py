"""
功能：
    检查 CPython 3.11、Python 依赖、Agent 配置和固定任务字段。

输入：
    当前 Python 环境和本次启动使用的 Agent YAML。

输出：
    终端检查结果及失败项；导入日志模块时可产生日志。

运行：
    阶段 03 在启动 Agent 和机械臂服务前调用。

参数：
    --config 指定 Agent YAML；--dos-w1 检查真机依赖；--fixed-task 检查固定任务文本。

被谁依赖：
    p00_cli.py
"""

from __future__ import annotations

import argparse
import importlib
import platform
import sys


EXPECTED_IMPORTS = {
    "yaml": "PyYAML",
    "numpy": "numpy",
    "cv2": "opencv-python-headless",
    "requests": "requests",
    "loguru": "loguru",
    "PIL": "Pillow",
    "fastapi": "fastapi",
    "uvicorn": "uvicorn",
    "websockets": "websockets",
    "scipy": "scipy",
    "pydantic": "pydantic",
}


def main() -> int:
    parser = argparse.ArgumentParser(description='检查阶段 03 的 Python 环境和 Agent YAML')
    parser.add_argument('--config', required=True, help='本次启动使用的 Agent YAML')
    parser.add_argument('--dos-w1', action='store_true', help='检查 DOS-W1 真机环境')
    parser.add_argument('--fixed-task', action='store_true', help='检查 YAML 中的固定任务')
    args = parser.parse_args()

    if platform.python_implementation() != "CPython" or sys.version_info[:2] != (3, 11):
        print(
            "[FAIL] 需要标准 CPython 3.11；"
            f"当前版本为 {sys.version.split()[0]}。",
            file=sys.stderr,
        )
        return 1

    expected_imports = EXPECTED_IMPORTS.copy()
    if args.dos_w1:
        expected_imports.update({'airbot_py.arm': 'airbot_py', 'pyrealsense2': 'pyrealsense2'})
    else:
        expected_imports['mujoco'] = 'mujoco'

    failures = []
    for module_name, package_name in expected_imports.items():
        try:
            importlib.import_module(module_name)
        except Exception as exc:
            failures.append(f"{package_name}: {type(exc).__name__}: {exc}")

    try:
        from .p03_config import load_config

        config = load_config(args.config)
        expected_robot = 'airbot' if args.dos_w1 else 'mujoco'
        if config['robot']['type'] != expected_robot:
            failures.append(f'当前运行方式要求 robot.type 为 {expected_robot}')
        if args.fixed_task or (config.get('orchestrator') or {}).get('mode') == 'fixed_task':
            from .p03_orchestrators import read_fixed_prompt

            read_fixed_prompt(config)
    except Exception as exc:
        failures.append(f"Agent 配置检查失败: {type(exc).__name__}: {exc}")

    if failures:
        print("[FAIL] 运行环境检查未通过:", file=sys.stderr)
        for failure in failures:
            print(f"  - {failure}", file=sys.stderr)
        return 1

    print(
        f"[OK] CPython {sys.version.split()[0]}、依赖和 Agent 配置检查通过。"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
