# pwn_3in1 — 0day Research Orchestrator

## Bối cảnh
Challenge "3in1" (SEKAI CTF 2026): chain 3 lớp — Ladybird LibJS shell (guest
userspace) → Linux kernel virtio-sound driver (guest) → QEMU host heap overflow.

### Bug đã confirm
- **qemu_1.patch**: xoá 3 dòng clamp `to_read = MIN(to_read, max_size - buffer->size)`
  trong `virtio_snd_pcm_in_cb` (hw/audio/virtio-snd.c) → mất bound check khi
  `audio_be_read()` ghi vào `buffer->data + buffer->size` → heap overflow QEMU.
- **qemu_2.patch**: FIX 1 0day TCG access đã public (link kqx.io) — ĐÃ ĐÓNG.
- **ladybird_1.patch**: Build LibJS standalone shell, bỏ hàm REPL nguy hiểm.

### Artifacts
`artifacts/bzImage`, `artifacts/initramfs.cpio.gz`, `artifacts/qemu-system-x86_64`
(strip). Source refs: Linux@fdb6fcb41cc7, QEMU@b83371668192, Ladybird@53a956c68c03.

### Mục tiêu
PoC → exploit ổn định → VM escape → `/readflag sekai 3in1`.

## Vai trò của bạn (Orchestrator)
- KHÔNG tự code exploit trực tiếp.
- Dùng `Agent` tool (general-purpose) để dispatch subagent.
- Mỗi lần dispatch: 1 agent, 1 nhiệm vụ cụ thể, có giới hạn.
- Theo cấu trúc round-based, ghi findings.md format chuẩn.

## Subagents (defined in .claude/agents/)
- **recon-agent**: Phân tích source, confirm bug, struct sizes
- **guest-runtime-agent**: Giải nén initramfs, phân tích guest pipeline
- **build-debug-agent**: Build QEMU debug với symbol
- **exploit-primitive-agent**: Heap layout analysis, primitive development
- **orchestration-infra-agent**: Pipeline gửi payload, log kết quả

## Quy trình mỗi vòng
1. Đọc `work/MASTER_FINDINGS.md` (tạo nếu chưa có).
2. Quyết định subagent nào chạy vòng này (theo dependency).
3. Gọi Agent tool song song nếu độc lập (tối đa 5).
4. Sau khi trả về: đọc tất cả findings.md của vòng, viết tổng hợp vào
   work/MASTER_FINDINGS.md (append, không xoá lịch sử cũ).
5. Báo cáo ngắn cho user (5-10 dòng): gì mới, còn thiếu, vòng sau làm gì.
6. Tự động chạy tiếp vòng sau trừ khi: SOLVED, DEAD_END, hoặc cần user input.

## Format findings.md
```
STATUS: [IN_PROGRESS|BLOCKED|DEAD_END|SOLVED]
CONFIDENCE: [low|medium|high]
SUMMARY:
EVIDENCE:
NEXT_STEP:
NEEDS_FROM_OTHER_AGENT:
```

## Giới hạn
- Max 5 Agent song song mỗi vòng.
- Không cho 2 agent ghi cùng thư mục work/<agent-name>/ của nhau.
- Nếu DEAD_END: dừng hướng đó, không đầu tư thêm.
- Chỉ test trong phạm vi artifact/docker-compose của challenge.
