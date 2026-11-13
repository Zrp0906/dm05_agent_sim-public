# DOS-W1 真机与 MaaS

[项目入口](../README.md)

执行真机流程前，需要取得授权提供的 Agent 源码和真机配置。[Agent 目录说明](../agent/README.md)

在 Linux 准备 CPython 3.11 的 `dos-w1` Conda 环境、Agent 使用的 `airbot_py` 和 `pyrealsense2`、`tmux`，以及装有 `airbot_server` 的 `airbot` Conda 环境。

在项目根目录检查交付文件、安装依赖并复制真机配置。

```bash
conda activate dos-w1
python dm05_workflow/p00_pipeline/00_02_run_pipeline.py --from-stage 0
python -m pip install -r requirements.txt
cp -n agent/config/direct_maas_config.yaml agent/config/direct_maas.local.yaml
```

在 `agent/config/direct_maas.local.yaml` 中填写有权限使用的 MaaS 模型 ID，将三路相机的序列号占位符替换为实际值，并按现场设备设置机械臂端口。确认 CAN 设备名及端口与启动脚本一致。[真机启动脚本](../dm05_workflow/p03_agent/_impl/p03_start_dos_w1.sh) · [MaaS 平台](https://maas.dexmal.com/)

用总入口选择阶段 03 的真机分支。它先检查 Python 环境、真机依赖和 YAML，然后在 `airbot_servers` 会话中启动四个机械臂服务，等待端口就绪后启动 Agent。

| CAN 设备 | 端口 |
| --- | --- |
| `can_left_lead` | 50050 |
| `can_left` | 50051 |
| `can_right_lead` | 50052 |
| `can_right` | 50053 |

在终端启动真机流程，密钥通过环境变量传入。

```bash
conda activate dos-w1
export DEXOS_API_KEY="客户自己的 MaaS API Key"
python dm05_workflow/p00_pipeline/00_02_run_pipeline.py --from-stage 3 --dos-w1 \
  --agent-config agent/config/direct_maas.local.yaml
```

在 YAML 的 `orchestrator:` 下找到 `http:`，按其中的 `port:` 打开网页，确认三路相机刷新。控制真机前清空机械臂工作区，确认急停可用，首次运行时降低速度。异常动作时使用物理急停。

另开终端运行 `tmux attach -t airbot_servers` 可查看机械臂服务。用 `Ctrl+C` 停止 Agent。结束使用时执行 `tmux kill-session -t airbot_servers` 停止机械臂服务。
