"""
功能：
    构建 MuJoCo 和 DM0.5 客户端，核对观测与动作维度，提交首个动作并释放资源。

输入：
    工作流 JSON；Agent YAML 中的 mujoco、dm05_http 和推理地址。
    三路仿真图像、14 维状态及任务文本。

输出：
    JSON 记录，包含 UTC 时间、相机数、状态维度、动作形状和提交结果。

运行：
    由 04_01_check_integration.py 导入并调用 main。

参数：
    无独立命令行参数；见 04_01_check_integration.py。

被谁依赖：
    04_01_check_integration.py
"""

import argparse
from datetime import datetime, timezone
import json

from agent.factory import build_low_level, build_robot
from dm05_workflow.p00_pipeline._impl.p00_common import add_config_argument, load_workflow_config
from dm05_workflow.p03_agent._impl.p03_config import load_config
from dm05_workflow.p03_agent._impl.p03_orchestrators import read_fixed_prompt


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    add_config_argument(parser)
    parser.add_argument('--task', help='推理指令，默认使用 Agent YAML 的固定任务')
    args = parser.parse_args()
    workflow = load_workflow_config(args.config)
    config = load_config(str(workflow.agent_config))
    if config['robot']['type'] != 'mujoco':
        parser.error('联调需要 robot.type 为 mujoco')
    low_level_config = config['low_level']
    if low_level_config.get('type', 'dm05_http') != 'dm05_http':
        parser.error('联调需要 low_level.type 为 dm05_http')
    task = args.task or read_fixed_prompt(config)

    robot = build_robot(config['robot'])
    try:
        client = build_low_level(low_level_config, robot=robot)
        try:
            observation = robot.get_observation()
            images = observation['images']
            state = observation['state']
            if len(images) != 3 or state.shape != (14,):
                raise ValueError('联调需要三路相机和 14 维机器人状态')
            actions = client.predict(images, state, task)
            if actions.shape[1] != 14:
                raise ValueError(f'OpenDM 返回的动作不符合 [T, 14]: {actions.shape}')
            robot.execute_action(actions[0])
        finally:
            client.close()
    finally:
        robot.close()

    report = {
        'recorded_at': datetime.now(timezone.utc).isoformat(),
        'camera_count': len(images),
        'state_dimension': int(state.size),
        'action_shape': list(actions.shape),
        'first_action_submitted_to_simulator': True,
    }
    report_path = workflow.integration_report
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(f'[OK] OpenDM 返回 {actions.shape[0]} 个动作，首个动作已提交给 MuJoCo。')
    print(f'联调记录: {report_path}')
