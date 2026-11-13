"""
功能：
    按 Agent 配置构建机器人、低层推理客户端和可选高层 VLM，组装所选任务模式的编排器。

输入：
    Agent YAML 解析出的 robot、low_level、orchestrator，以及模式所需的 high_level、task 或语音配置。

输出：
    编排器实例；read_fixed_prompt 返回固定任务文本。

运行：
    作为依赖导入，不单独运行。运行编排器结束后释放 MuJoCo。

参数：
    无

被谁依赖：
    p03_launch.py
    p04_integration.py
    p03_verify_runtime.py
"""

from agent.direct_low_level_orchestrator import DirectLowLevelOrchestrator
from agent.factory import build_high_level, build_low_level, build_robot
from agent.interactive_orchestrator import InteractiveOrchestrator
from agent.orchestrator import AgentOrchestrator


def build_auto(config: dict, log_dir: str) -> AgentOrchestrator:
    high_level = build_high_level(config['high_level'])
    robot = build_robot(config['robot'])
    low_level = build_low_level(config['low_level'], robot=robot)
    robot_config = config.get('robot', {})
    orch_config = config.get('orchestrator', {})
    return AgentOrchestrator(
        high_level=high_level,
        low_level=low_level,
        robot=robot,
        task=config['task'],
        replan_interval=config['high_level'].get('replan_interval', 50),
        action_horizon=robot_config.get('action_horizon', 10),
        control_frequency=robot_config.get('control_frequency', 30),
        max_steps=orch_config.get('max_steps', 2000),
        log_dir=log_dir,
    )


def build_interactive(config: dict, voice_config: dict | None = None) -> InteractiveOrchestrator:
    high_level = build_high_level(config['high_level'])
    robot = build_robot(config['robot'])
    low_level = build_low_level(config['low_level'], robot=robot)
    orch_config = config.get('orchestrator', {})
    http_cfg = orch_config.get('http', {})
    pad_port = http_cfg.get('pad_port')
    low_level_cfg = config.get('low_level', {})
    home_state = orch_config.get('home_state')
    if home_state is None:
        home_state = low_level_cfg.get('executor', {}).get('init_action') or low_level_cfg.get('init_action')
    return InteractiveOrchestrator(
        high_level=high_level,
        low_level=low_level,
        robot=robot,
        main_camera_index=int(orch_config.get('main_camera_index', 0)),
        check_interval_s=float(orch_config.get('check_interval_s', 3.0)),
        home_state=home_state,
        home_threshold_rad=float(orch_config.get('home_threshold_rad', 0.05)),
        home_threshold_m=float(orch_config.get('home_threshold_m', 0.02)),
        auto_reset_on_done=bool(orch_config.get('auto_reset_on_done', True)),
        force_reset=bool(orch_config.get('force_reset', False)),
        home_done_timeout_s=float(orch_config.get('home_done_timeout_s', 0.0)),
        check_max_in_flight=int(orch_config.get('check_max_in_flight', 3)),
        ref_update_iou_threshold=float(orch_config.get('ref_update_iou_threshold', 0.7)),
        ref_update_min_bbox_area=float(orch_config.get('ref_update_min_bbox_area', 0.005)),
        verify_camera_indices=orch_config.get('verify_camera_indices'),
        weighted_done_threshold=float(orch_config.get('weighted_done_threshold', 5.0)),
        weighted_done_window_s=float(orch_config.get('weighted_done_window_s', 15.0)),
        weighted_done_main_done=float(orch_config.get('weighted_done_main_done', 1.0)),
        weighted_done_main_not_done=float(orch_config.get('weighted_done_main_not_done', -2.0)),
        weighted_done_verify_done=float(orch_config.get('weighted_done_verify_done', 5.0)),
        weighted_done_verify_not_done=float(orch_config.get('weighted_done_verify_not_done', -10.0)),
        verify_cooldown_s=float(orch_config.get('verify_cooldown_s', 20.0)),
        ref_update_via_verify=bool(orch_config.get('ref_update_via_verify', True)),
        fix_prompt=low_level_cfg.get('fix_prompt'),
        fix_ref_image_path=low_level_cfg.get('fix_ref_image_path'),
        http_host=str(http_cfg.get('host', '0.0.0.0')),
        http_port=int(http_cfg.get('port', 8010)),
        pad_http_port=int(pad_port) if pad_port is not None else None,
        voice_config=voice_config or {},
    )


def build_direct_low_level(config: dict) -> DirectLowLevelOrchestrator:
    robot = build_robot(config['robot'])
    low_level = build_low_level(config['low_level'], robot=robot)
    http_cfg = config.get('orchestrator', {}).get('http', {})
    return DirectLowLevelOrchestrator(
        low_level=low_level,
        robot=robot,
        http_host=str(http_cfg.get('host', '0.0.0.0')),
        http_port=int(http_cfg.get('port', 8020)),
    )


def read_fixed_prompt(config: dict) -> str:
    orch_config = config.get('orchestrator', {}) or {}
    prompt = str(orch_config.get('fixed_prompt') or '').strip()
    if not prompt:
        raise ValueError('orchestrator.fixed_prompt is empty; fill it in the config before running')
    return prompt


def build_fixed_task(config: dict) -> DirectLowLevelOrchestrator:
    fixed_prompt = read_fixed_prompt(config)
    robot = build_robot(config['robot'])
    low_level = build_low_level(config['low_level'], robot=robot)
    orch_config = config.get('orchestrator', {}) or {}
    http_cfg = orch_config.get('http', {}) or {}
    return DirectLowLevelOrchestrator(
        low_level=low_level,
        robot=robot,
        http_host=str(http_cfg.get('host', '0.0.0.0')),
        http_port=int(http_cfg.get('port', 8022)),
        index_html='fixed_task.html',
        app_title='DexAgent Fixed Task',
        fixed_prompt=fixed_prompt,
        allow_prompt_input=False,
    )


def run_orchestrator(orchestrator, config: dict) -> None:
    try:
        orchestrator.run()
    finally:
        if config['robot'].get('type') == 'mujoco':
            orchestrator.robot.close()
