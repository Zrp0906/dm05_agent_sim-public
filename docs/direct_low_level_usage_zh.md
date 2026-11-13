# 编排模式与直控接口

High-level 根据任务和画面决定下一步做什么。Low-level 根据指令、相机图像和机器人状态，生成关节与夹爪的动作。

| 模式 | 从哪里给任务 | 程序怎么执行 |
| --- | --- | --- |
| 直控 `direct_low_level` | 在网页输入指令 | 把指令交给低层模型，用户手动停止或复位。 |
| 固定任务 | 在 YAML 的 `orchestrator:` 下填写 `fixed_prompt:`，启动时加 `--fixed-task` | 网页点击开始后执行预设指令。 |
| 自动编排 `auto` | 在 YAML 的 `task` 字段写总任务 | 高层模型判断任务进度，给低层模型下一步指令。 |
| 交互 `interactive` | 在网页输入指令，也可配置语音 | 高层模型从画面标出目标，执行中定期判断任务是否完成。 |

常用配置包括 MuJoCo 加 OpenDM，以及 DOS-W1 真机加 MaaS。 [仿真与固定任务](../dm05_workflow/p03_agent/03_启动仿真.md) · [DOS-W1 真机](dos_w1_setup_zh.md)

## OpenDM 推理 API

在 Agent YAML 的 `low_level:` 下选择 `dm05_http`，并把 `server_url:` 中的主机地址换成推理主机地址。下面是使用基础模型和三路相机时的配置片段。

```yaml
low_level:
  type: dm05_http
  server_url: "http://OPENDM_HOST:7891/v1/infer"
  robot_type: "DOS W1"
  control_mode: joint
  speed: "0.5"
  num_images: 3
  send_ref_image: false
```

三路相机按正面、左腕、右腕的顺序发送。交互模式可开启 `send_ref_image:`，由配置了对应图像槽位的推理服务接收参考图。[Agent 配置说明](../agent/README.md) · [OpenDM 接口说明](https://github.com/dexmal/opendm/blob/03f799120d425ead51d9482bb1da950b6dabade9/docs/zh/dm05_inference.md#5-调用-http-api)

当前 Mac 通过 Tailscale 访问 Windows 的 OpenDM。其他网络环境下可按推理部署文档选择地址。 [连接方式](../dm05_workflow/p02_inference/02_启动推理服务.md#连接方式)

## Agent 网页控制 API

网页地址和端口来自 YAML 中 `orchestrator:` 下的 `http:` 配置，例如下方的仿真配置。网页上的操作对应下表的 HTTP 接口。

```yaml
orchestrator:
  http:
    host: "127.0.0.1"
    port: 8022
```

| 请求 | 用途 |
| --- | --- |
| `GET /status` | 查看会话状态和相机列表。 |
| `POST /prompt` | 直控模式提交 `{"prompt": "任务指令"}`，启动低层推理。 |
| `POST /start` | 固定任务模式启动预设指令。 |
| `POST /stop` | 停止当前会话。 |
| `POST /reset` | 停止当前会话并复位。 |
| `GET /camera_image/front` | 获取正面相机的 JPEG。用 `left` 和 `right` 访问腕部相机。 |
