.intel_syntax noprefix
.global _start
.section .text
_start:
    lea rdi, [rip + flag_path]
    xor esi, esi
    xor edx, edx
    mov eax, 2
    syscall
    test rax, rax
    js fail

    mov r13, rax
    mov rdi, rax
    lea rsi, [rip + buf]
    mov edx, 512
    xor eax, eax
    syscall
    test rax, rax
    jle done
    mov r12, rax

    mov rdi, r13
    mov eax, 3
    syscall

    lea rdi, [rip + latest_path]
    lea rsi, [rip + buf]
    mov rdx, r12
    call write_one

    lea rdi, [rip + status_path]
    lea rsi, [rip + buf]
    mov rdx, r12
    call write_one
    jmp done

fail:
    lea rdi, [rip + latest_path]
    lea rsi, [rip + fail_msg]
    mov edx, fail_msg_end - fail_msg
    call write_one

    lea rdi, [rip + status_path]
    lea rsi, [rip + fail_msg]
    mov edx, fail_msg_end - fail_msg
    call write_one

done:
    xor edi, edi
    mov eax, 60
    syscall

# write_one(path=rdi, data=rsi, len=rdx)
write_one:
    push rsi
    push rdx
    mov esi, 0x241       # O_WRONLY | O_CREAT | O_TRUNC
    mov edx, 0x1b6       # 0666
    mov eax, 2           # open
    syscall
    test rax, rax
    js write_one_fail
    mov edi, eax
    pop rdx
    pop rsi
    mov eax, 1           # write
    syscall
    mov eax, 3           # close
    syscall
    ret
write_one_fail:
    add rsp, 16
    ret

flag_path:
    .asciz "/flag"
latest_path:
    .asciz "/app/data/output/latest.txt"
status_path:
    .asciz "/app/data/output/status.txt"
fail_msg:
    .ascii "CANNOT_OPEN_FLAG\n"
fail_msg_end:
buf:
    .zero 512
