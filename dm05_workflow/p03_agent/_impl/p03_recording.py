"""
功能：
    把直控录制配置传给低层轨迹记录器，按需安装正面相机录制扩展。

输入：
    Agent 配置中的 orchestrator.recording。

输出：
    更新 low_level.trajectory_recording，安装相机录制扩展；录制文件由运行中的会话生成。

运行：
    在直控编排器构建前由 p03_launch.py 调用。

参数：
    无

被谁依赖：
    p03_launch.py
"""

from agent.log import get_logger


logger = get_logger('main')


def _recording_config(config: dict) -> dict:
    orch_config = config.get('orchestrator', {}) or {}
    raw = orch_config.get('recording')
    if raw is None:
        return {}
    if not isinstance(raw, dict):
        raise ValueError('orchestrator.recording must be a dict when provided')
    return dict(raw)


def _recording_options(recording_config: dict, name: str) -> dict:
    raw = recording_config.get(name, {})
    if raw is None:
        raw = {}
    if not isinstance(raw, dict):
        raise ValueError(f'orchestrator.recording.{name} must be a dict')
    options = dict(raw)
    if 'output_dir' in recording_config and 'output_dir' not in options:
        options['output_dir'] = recording_config['output_dir']
    return options


def apply_trajectory_recording(config: dict) -> None:
    low_level_cfg = config.setdefault('low_level', {})
    if not isinstance(low_level_cfg, dict):
        return
    recording_cfg = _recording_config(config)
    if recording_cfg.get('enabled', False):
        options = _recording_options(recording_cfg, 'trajectory')
        options['enabled'] = bool(options.get('enabled', True))
        options['_runtime_enabled'] = True
        low_level_cfg['trajectory_recording'] = options
        return
    options = low_level_cfg.get('trajectory_recording')
    if isinstance(options, dict):
        options['_runtime_enabled'] = False


def install_front_recording(config: dict) -> None:
    try:
        from agent.extensions.direct_front_recording import install
    except Exception as exc:
        logger.warning(f'front-camera recording extension unavailable: {type(exc).__name__}: {exc}')
        return
    try:
        recording_cfg = _recording_config(config)
        installed = install(
            config=_recording_options(recording_cfg, 'front_camera'),
            enabled=bool(recording_cfg.get('enabled', False)),
        )
        if installed:
            logger.info('front-camera recording extension installed')
    except Exception as exc:
        logger.warning(f'front-camera recording extension disabled: {type(exc).__name__}: {exc}')
