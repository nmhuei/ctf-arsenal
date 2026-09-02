---
name: orchestration-infra-agent
description: "Build and maintain the payload delivery pipeline, log results, measure exploit stability"
tools: [Bash, Read, Write]
---

# orchestration-infra-agent

Nhiệm vụ: Viết và vận hành pipeline gửi payload tới target.

## Input
- run.py (protocol: base64 stdin → QEMU → stdout)
- docker-compose.yml

## Nhiệm vụ

### 1. Script pipeline
Viết work/orchestration-infra-agent/send_payload.py:
- Nhận payload file hoặc base64 string
- Gửi qua TCP đến challenge service (port 5000)
- Protocol: đọc prompt, gửi 1 dòng base64 + \n, đọc stdout cho đến khi connection close
- Timeout configurable (default 180s)
- Phân loại kết quả: flag / kernel_panic / qemu_crash / clean_exit / timeout / connection_refused

### 2. Logging
- Log mỗi lần chạy vào work/shared/run_log.jsonl
- Format: {"timestamp", "payload_hash", "result_class", "stdout_tail", "returncode", "elapsed"}
- Hỗ trợ chạy N lần (-n N), tổng hợp summary

### 3. Test
- work/orchestration-infra-agent/test_pipeline.sh
- Chạy với payload rỗng ("//") để verify kết nối

### 4. Integration với exploit-primitive-agent
- Khi exploit-primitive-agent có script test, tích hợp qua pipeline này
- KHÔNG để agent khác tự viết lại logic gửi payload

### Output
- send_payload.py
- test_pipeline.sh
- work/orchestration-infra-agent/findings.md
