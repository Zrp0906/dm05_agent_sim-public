#!/usr/bin/env bash
set -euo pipefail

if [[ $# != 2 || ! "$1" =~ ^(prepare|download|bundle)$ ]]; then
  printf 'Expected prepare, download or bundle and a destination directory.\n' >&2
  exit 2
fi

mode="$1"
prepare_dir="$2"
checkpoint_dir="$prepare_dir/checkpoints/DM05"

opendm_revision=03f799120d425ead51d9482bb1da950b6dabade9
model_revision=5cd18734814abb075a9ccfd9ad6d16777b5cf10e
model_sha256=b7da77f516ebd0c0c68faed2f0cfe1c68985b7b874e49dda4292d8d286de20dd
model_bytes=11658431136
checkpoint_files=(
  model.safetensors config.json generation_config.json norm_stats.json
  tokenizer.json tokenizer_config.json chat_template.jinja
  preprocessor_config.json processor_config.json
)
prepared_image=opendm-dm05:prepared
platform=linux/amd64

verify_checkpoint() (
  cd -- "$checkpoint_dir"
  model_file="${1:-model.safetensors}"
  for file in "${checkpoint_files[@]:1}" "$model_file"; do
    if [[ ! -s "$file" ]]; then
      printf 'Missing checkpoint file: %s/%s\n' "$checkpoint_dir" "$file" >&2
      exit 1
    fi
  done
  checksum=(sha256sum --check -)
  if ! command -v sha256sum >/dev/null; then
    checksum=(shasum -a 256 --check -)
  fi
  printf '%s  %s\n' "$model_sha256" "$model_file" | "${checksum[@]}"
)

if [[ "$mode" == download ]]; then
  mkdir -p -- "$checkpoint_dir"
  checkpoint_dir="$(cd -- "$checkpoint_dir" && pwd -P)"
  (
    cd -- "$checkpoint_dir"
    checkpoint_url="https://huggingface.co/Dexmal/DM05/resolve/$model_revision"
    curl_options=(--fail --location --connect-timeout 15 --retry 3)
    for file in "${checkpoint_files[@]:1}"; do
      if [[ ! -s "$file" ]]; then
        curl "${curl_options[@]}" --output "$file.part" "$checkpoint_url/$file"
        mv -- "$file.part" "$file"
      fi
    done

    if [[ -s model.safetensors ]]; then
      verify_checkpoint
    else
      partial_file=model.safetensors.part
      touch -- "$partial_file"
      partial_size="$(wc -c < "$partial_file")"
      if (( partial_size > model_bytes )); then
        printf 'Partial weight file exceeds expected size: %s/%s\n' "$checkpoint_dir" "$partial_file" >&2
        exit 1
      fi
      if (( partial_size < model_bytes )); then
        curl "${curl_options[@]}" --continue-at - --output "$partial_file" \
          "$checkpoint_url/model.safetensors"
      fi
      verify_checkpoint "$partial_file"
      mv -- "$partial_file" model.safetensors
    fi
  )
  printf 'Checkpoint: %s\n' "$checkpoint_dir"
  exit 0
fi

if [[ "$mode" == bundle ]]; then
  verify_checkpoint
  bundled_image=opendm-dm05:with-weights
  container_id="$(docker create --pull=never --platform "$platform" "$prepared_image")"
  trap 'docker rm "$container_id" >/dev/null' EXIT

  tar_options=(--format=posix --transform='s,^,checkpoint/,')
  if [[ "$(uname -s)" == Darwin ]]; then
    tar_options=(--format=pax -s ',^,checkpoint/,')
  fi
  (
    cd -- "$checkpoint_dir"
    COPYFILE_DISABLE=1 tar "${tar_options[@]}" -chf - -- "${checkpoint_files[@]}"
  ) | docker cp - "$container_id:/"

  docker commit "$container_id" "$bundled_image"
  printf 'Image with weights: %s\nCheckpoint in image: /checkpoint\n' "$bundled_image"
  exit 0
fi

mkdir -p -- "$checkpoint_dir"
checkpoint_dir="$(cd -- "$checkpoint_dir" && pwd -P)"

build_context="$(mktemp -d)"
trap 'rm -rf -- "$build_context"' EXIT
if [[ -n "${OPENDM_SOURCE_ARCHIVE:-}" ]]; then
  source_dir="opendm-$opendm_revision"
  tar -xzf "$OPENDM_SOURCE_ARCHIVE" -C "$build_context" "$source_dir"
  source_step="COPY $source_dir/ ."
else
  source_step='RUN git init . \
    && git fetch --depth 1 https://github.com/dexmal/opendm.git "$OPENDM_REVISION" \
    && git checkout --detach FETCH_HEAD'
fi

docker build --platform "$platform" --tag "$prepared_image" \
  --build-arg "OPENDM_REVISION=$opendm_revision" --file - "$build_context" <<DOCKERFILE
FROM dexmal/opendm@sha256:60a754dce047fbef40ab7d3a160fd82ccfbf5fa0509d862b6702311499dfbd4d
ARG OPENDM_REVISION
WORKDIR /opt/opendm
$source_step
RUN conda run -n opendm python -m pip install --no-build-isolation -e .
DOCKERFILE

docker run --platform "$platform" --rm -i --user "$(id -u):$(id -g)" \
  --env HF_HOME=/tmp/opendm-hf \
  --env NVIDIA_VISIBLE_DEVICES=void \
  --mount "type=bind,source=$checkpoint_dir,target=/checkpoint" \
  --entrypoint /opt/conda/envs/opendm/bin/python \
  "$prepared_image" - "$model_revision" <<'PYTHON'
from importlib.metadata import version
from pathlib import Path
import sys

from huggingface_hub import snapshot_download

if not Path("script/dm05_launcher.sh").is_file():
    raise SystemExit("OpenDM launcher is missing in the prepared image")
print(f"OpenDM installed: {version('opendm')}", flush=True)
snapshot_download("Dexmal/DM05", revision=sys.argv[1], local_dir="/checkpoint")
PYTHON

verify_checkpoint
printf 'Prepared image: %s\nCheckpoint: %s\n' "$prepared_image" "$checkpoint_dir"
