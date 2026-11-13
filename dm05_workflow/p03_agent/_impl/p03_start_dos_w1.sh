#!/usr/bin/env bash
# 启动 DOS-W1 的四个 airbot_server，等端口就绪后返回。
set -euo pipefail

session=airbot_servers
interfaces=(can_left_lead can_left can_right_lead can_right)
ports=(50050 50051 50052 50053)

if [[ $(uname -s) != Linux ]]; then
    printf '[FAIL] DOS-W1 机械臂服务需要 Linux。\n' >&2
    exit 1
fi
if ! conda_bin=$(command -v conda) || ! command -v tmux >/dev/null || ! command -v timeout >/dev/null; then
    printf '[FAIL] 请先准备 Conda、tmux 和 timeout。\n' >&2
    exit 1
fi

port_ready() {
    timeout 1 bash -c ': > "/dev/tcp/127.0.0.1/$1"' _ "$1" 2>/dev/null
}

all_ports_ready() {
    local port
    for port in "${ports[@]}"; do
        port_ready "$port" || return 1
    done
}

target="=$session"
if ! tmux has-session -t "$target" 2>/dev/null; then
    for port in "${ports[@]}"; do
        if port_ready "$port"; then
            printf '[FAIL] 机械臂服务端口 %s 已被占用。\n' "$port" >&2
            exit 1
        fi
    done

    printf -v server_command '%q run --no-capture-output -n airbot airbot_server' "$conda_bin"
    target=$(tmux new-session -d -P -F '#{session_id}' -s "$session" -n airbots \
        "$server_command -i ${interfaces[0]} -p ${ports[0]}")
    trap 'tmux kill-session -t "$target" 2>/dev/null || true' EXIT
    for ((index = 1; index < ${#ports[@]}; index++)); do
        tmux split-window -d -t "$target:airbots" "$server_command -i ${interfaces[index]} -p ${ports[index]}"
    done
    tmux select-layout -t "$target:airbots" tiled >/dev/null
fi

for ((attempt = 0; attempt < 30; attempt++)); do
    if ! tmux has-session -t "$target" 2>/dev/null; then
        break
    fi
    if all_ports_ready; then
        trap - EXIT
        printf '[OK] DOS-W1 四个机械臂服务已就绪。用 tmux attach -t %s 查看。\n' "$session"
        exit 0
    fi
    sleep 1
done

printf '[FAIL] DOS-W1 机械臂服务未就绪，请检查 airbot 环境和 CAN 设备。\n' >&2
exit 1
