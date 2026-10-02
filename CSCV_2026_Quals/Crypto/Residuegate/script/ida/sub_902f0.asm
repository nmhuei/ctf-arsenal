                rol     ax, 8
                xor     edx, edx
                jmp     loc_8D577
; ---------------------------------------------------------------------------

loc_8D473:                              ; CODE XREF: sub_8CB70+8CB↑j
                call    cs:__errno_location_ptr
                mov     r12d, [rax]
                shl     r12, 20h
                or      r12, 2
                mov     rdi, r12
                call    sub_5BBB0
                cmp     al, 0Dh
                jnz     loc_8D5F4

loc_8D494:                              ; CODE XREF: sub_8CB70+A7E↓j
                mov     r8, [rsp+0C58h+var_C58]
                mov     rax, [r8+128h]
                mov     rcx, [r8+148h]
                movzx   edx, byte ptr [r8+150h]
                mov     rsi, [rax+10h]
                and     ecx, 33h
                mov     rax, [rsi+90h]
                xor     rcx, 0FF003Fh
                db      66h, 66h, 66h, 66h, 2Eh
                nop     word ptr [rax+rax+00000000h]

loc_8D4D0:                              ; CODE XREF: sub_8CB70+977↓j
                mov     edi, eax
                shr     edi, 10h
                cmp     dl, dil
                jnz     short loc_8D4E9
                mov     edi, eax
                and     edi, ecx
                lock cmpxchg [rsi+90h], rdi
                jnz     short loc_8D4D0

loc_8D4E9:                              ; CODE XREF: sub_8CB70+968↑j
                test    bl, bl
                mov     rsi, 7FFFFFFFFFFFFFFFh
                jz      short loc_8D512
                movzx   eax, byte ptr fs:0FFFFFFFFFFFFFF58h
                cmp     eax, 1
                jz      loc_8FEB2
                cmp     eax, 2
                jnz     loc_8FE8C

loc_8D512:                              ; CODE XREF: sub_8CB70+985↑j
                mov     eax, r12d
                and     eax, 3
                cmp     eax, 1
                jnz     loc_8FF11
                jmp     loc_8FECE
; ---------------------------------------------------------------------------

loc_8D526:                              ; CODE XREF: sub_8CB70+8DA↑j
                movzx   ebx, word ptr [rsp+0C58h+addr.sa_data]
                rol     bx, 8
                mov     eax, dword ptr [rsp+0C58h+addr.sa_data+2]
                mov     dword ptr [rsp+0C58h+var_BE8], eax
                mov     eax, dword ptr [rsp+0C58h+var_7E0]
                mov     dword ptr [rsp+0C58h+var_C08], eax
                mov     ecx, dword ptr [rsp+0C58h+addr.sa_data+6]
                shl     ecx, 10h
                movzx   eax, word ptr [rsp+0C58h+addr.sa_data+8]
                mov     rdx, qword ptr [rsp+0C58h+addr.sa_data+0Ah]
                mov     [rsp+0C58h+var_BE0], rdx
                mov     edx, 1
                mov     esi, [rsp+0C58h+var_7E4]
                mov     dword ptr [rsp+0C58h+var_C40], esi

loc_8D577:                              ; CODE XREF: sub_8CB70+8FE↑j
                mov     rsi, 7FFFFFFFFFFFFFFFh
                mov     ecx, ecx
                shl     rcx, 10h
                or      rcx, rdx
                movzx   r14d, ax
                shl     r14, 30h
                or      r14, rcx
                mov     byte ptr [r13+0], 1
                movzx   ecx, byte ptr fs:0FFFFFFFFFFFFFF58h
                cmp     ecx, 1
                jz      loc_8F9AB
                mov     al, 1
                cmp     ecx, 2
                jnz     loc_8F989
                mov     byte ptr [rsp+0C58h+addr.sa_family], al
                lea     rsi, off_210E7070 ; "/home/aothuatgiadp/.cargo/registry/src/"...
                lea     rdi, [rsp+0C58h+addr]
                call    sub_558F0
; ---------------------------------------------------------------------------

loc_8D5D2:                              ; CODE XREF: sub_8CB70+8E3↑j
                mov     edi, ebp        ; fd
                call    cs:close_ptr
                mov     r12, 1400000003h
                mov     rdi, r12
                call    sub_5BBB0
                cmp     al, 0Dh
                jz      loc_8D494

loc_8D5F4:                              ; CODE XREF: sub_8CB70+91E↑j
                mov     rcx, [rsp+0C58h+var_C58]

loc_8D5F8:                              ; CODE XREF: sub_8CB70+79D↑j
                mov     rdi, [rsp+0C58h+var_B58]
                movzx   r8d, [rsp+0C58h+var_C2A]
                mov     r9d, [rsp+0C58h+var_BCC]
                mov     r10d, [rsp+0C58h+var_BD0]
                mov     r11d, [rsp+0C58h+var_BD4]
                mov     byte ptr [r13+0], 1
                mov     r13d, 2

loc_8D629:                              ; CODE XREF: sub_8CB70+35E4↓j
                mov     rax, [rsp+0C58h+var_B40]
                mov     ebp, [rsp+0C58h+var_B9C]

loc_8D638:                              ; CODE XREF: sub_8CB70+317B↓j
                mov     byte ptr [rcx+1B8h], 1
                mov     [rcx+0C0h], r13
                mov     [rcx+0C8h], r12
                mov     [rcx+0D0h], rdi
                mov     [rsp+0C58h+var_B9C], ebp
                mov     [rcx+0D8h], ebp
                mov     [rcx+0E0h], r14
                mov     [rsp+0C58h+var_B40], rax
                mov     [rcx+0E8h], rax
                mov     [rcx+0F0h], r11d
                mov     [rcx+0F4h], r10d
                mov     [rcx+0F8h], r9d
                mov     [rcx+0FCh], r8w
                cmp     r13, 2
                mov     [rsp+0C58h+var_B58], rdi
; END OF FUNCTION CHUNK FOR sub_8CB70
; ---------------------------------------------------------------------------
                db 66h, 44h, 89h
; ---------------------------------------------------------------------------
; START OF FUNCTION CHUNK FOR sub_8CB70
                and     al, 2Eh
                mov     [rsp+0C58h+var_BCC], r9d
                mov     [rsp+0C58h+var_BD0], r10d
                mov     [rsp+0C58h+var_BD4], r11d
                jnz     short near ptr loc_8D732+1
                mov     rax, [rsp+0C58h+var_C48]
                mov     [rax], r12
                mov     eax, r12d
                and     eax, 3
                mov     ecx, 10h
                lea     rdx, jpt_8D6E1  ; "|�\b�w�\b�\x04�\b�)�\b�"
                movsxd  rsi, dword ptr ds:(jpt_8D6E1 - 1002B6Ch)[rdx+rax*4] ; switch 4 cases
                add     rsi, rdx
                jmp     rsi             ; switch jump
; ---------------------------------------------------------------------------

loc_8D6E3:                              ; CODE XREF: sub_8CB70+B71↑j
                mov     ecx, 0Fh        ; jumptable 000000000008D6E1 case 1

loc_8D6E8:                              ; CODE XREF: sub_8CB70+B71↑j
                movzx   ecx, byte ptr [r12+rcx] ; jumptable 000000000008D6E1 case 0
                cmp     ecx, 6
                ja      loc_8D7A7
                mov     edx, 4Ch ; 'L'
                bt      edx, ecx
                jnb     loc_8D7A7
                mov     r13d, 2
                cmp     eax, 1
                jnz     loc_8E027
                lea     r14, [r12-1]
                mov     r15, [r12-1]
                mov     rbx, [r12+7]
                mov     rax, [rbx]
                test    rax, rax
                jnz     loc_8E009
; END OF FUNCTION CHUNK FOR sub_8CB70
; ---------------------------------------------------------------------------
                dw 0DBE9h
; ---------------------------------------------------------------------------
; START OF FUNCTION CHUNK FOR sub_8CB70
                or      [rax], al

loc_8D732:                              ; CODE XREF: sub_8CB70+B4E↑j
                add     [rax-73h], cl
                or      eax, 48000000h
                mov     ecx, [rax+30h]
                mov     [rsp+0C58h+var_338], rcx
                movdqu  xmm0, xmmword ptr [rax]
                movups  xmm1, xmmword ptr [rax+10h]
                movups  xmm2, xmmword ptr [rax+20h]
                movaps  [rsp+0C58h+src], xmm2
                movaps  [rsp+0C58h+var_358], xmm1
                movdqa  [rsp+0C58h+var_368], xmm0
                jmp     loc_8E027
; ---------------------------------------------------------------------------

loc_8D770:                              ; CODE XREF: sub_8CB70+B71↑j
                shr     r12, 20h        ; jumptable 000000000008D6E1 case 2
                add     r12d, 0FFFFFF99h
                cmp     r12d, 8
                ja      short loc_8D7A7
                mov     r13d, 2
                mov     eax, 103h
                bt      eax, r12d
                jb      loc_8E027
                jmp     short loc_8D7A7
; ---------------------------------------------------------------------------

loc_8D795:                              ; CODE XREF: sub_8CB70+B71↑j
                shr     r12, 20h        ; jumptable 000000000008D6E1 case 3
                lea     eax, [r12-7]
                cmp     eax, 23h ; '#'
                jnb     loc_8D900

loc_8D7A7:                              ; CODE XREF: sub_8CB70+B80↑j
                                        ; sub_8CB70+B8E↑j ...
                mov     edi, 1
                call    sub_FE82F0
                inc     rax
                jo      short loc_8D7D9
                cmp     edx, 3B9ACA00h
                jb      short loc_8D806
                inc     rax
                seto    cl
                add     edx, 0C4653600h
                cmp     edx, 3B9ACA00h
                setz    sil
                or      sil, cl
                jz      short loc_8D806

loc_8D7D9:                              ; CODE XREF: sub_8CB70+C44↑j
                mov     edi, 1
                call    sub_FE82F0
                add     rax, 38640900h
                jo      loc_8F8CE
                cmp     edx, 3B9ACA00h
                jb      short loc_8D806
                inc     rax
                jo      loc_8F8CE
                add     edx, 0C4653600h

loc_8D806:                              ; CODE XREF: sub_8CB70+C4C↑j
                                        ; sub_8CB70+C67↑j ...
                lea     rdi, [rsp+0C58h+addr]
                mov     rsi, rax
                call    sub_FFED60
                movups  xmm0, [rsp+0C58h+var_798]
                mov     r8, [rsp+0C58h+var_C58]
                movups  xmmword ptr [r8+170h], xmm0
                movups  xmm0, [rsp+0C58h+var_7A8]
                movups  xmmword ptr [r8+160h], xmm0
                movups  xmm0, [rsp+0C58h+var_7B8]
                movups  xmmword ptr [r8+150h], xmm0
                movdqu  xmm0, xmmword ptr [rsp+0C58h+addr.sa_family]
                movups  xmm1, xmmword ptr [rsp+470h]
                movups  xmm2, [rsp+0C58h+var_7D8]
                movups  xmm3, xmmword ptr [rsp+0C58h+var_7C8]
                movups  xmmword ptr [r8+140h], xmm3
                movups  xmmword ptr [r8+130h], xmm2
                movups  xmmword ptr [r8+120h], xmm1
                movdqu  xmmword ptr [r8+110h], xmm0

loc_8D88C:                              ; CODE XREF: sub_8CB70:loc_8CC5B↑j
                lea     r12, [r8+110h]
                mov     rax, [rsp+0C58h+var_B50]
                mov     rax, [rax]
                mov     [rsp+0C58h+var_C08], rax
                lea     rbp, [r8+120h]
                mov     rax, fs:0
                lea     rax, [rax-0F0h]
                mov     [rsp+0C58h+var_C40], rax
                movzx   eax, byte ptr fs:0FFFFFFFFFFFFFF58h
                cmp     eax, 1
                mov     [rsp+0C58h+var_BE0], r12
                jz      loc_8D982
                xor     r13d, r13d
                mov     r15d, 0
                mov     ecx, 0
                cmp     eax, 2
                jnz     short loc_8D964
                mov     dword ptr [rsp+0C58h+var_C28], ecx
                mov     rax, [rbp+0]
                cmp     rax, 2
                jz      loc_8D9C9
                jmp     loc_8DEC0
; ---------------------------------------------------------------------------

loc_8D900:                              ; CODE XREF: sub_8CB70+C31↑j
                mov     r13d, 2
                mov     eax, 33h ; '3'
                bt      eax, r12d
                jb      loc_8D7A7
                jmp     loc_8E027
; ---------------------------------------------------------------------------

loc_8D91A:                              ; CODE XREF: sub_8CB70+87E↑j
                mov     rax, [rsp+0C58h+var_B50]
                mov     rax, [rax]
                mov     rdi, [rax]
                mov     rsi, [rax+8]
                call    sub_FF2660
                mov     r8, [rsp+0C58h+var_C58]
                mov     al, 4
                jmp     loc_8D221
; ---------------------------------------------------------------------------

loc_8D93C:                              ; CODE XREF: sub_8CB70+40D↑j
                mov     qword ptr [rsp+0C58h+addr.sa_family], 0
                add     r12, 20h ; ' '
                lea     rsi, [rsp+0C58h+addr_len]
                lea     rdx, [rsp+0C58h+addr]
                mov     rdi, r12
                call    sub_550B8
; ---------------------------------------------------------------------------

loc_8D964:                              ; CODE XREF: sub_8CB70+D77↑j
                lea     rsi, sub_5BC70
                mov     rdi, [rsp+0C58h+var_C40]
                call    sub_FE1FB0
                mov     byte ptr fs:0FFFFFFFFFFFFFF58h, 1
                mov     r8, [rsp+0C58h+var_C58]

loc_8D982:                              ; CODE XREF: sub_8CB70+D60↑j
                movzx   r15d, byte ptr fs:0FFFFFFFFFFFFFF54h
                movzx   r13d, byte ptr fs:0FFFFFFFFFFFFFF55h
                mov     eax, r13d
                cmp     r15b, 1
                jnz     short loc_8D9AC
                test    r13b, r13b
                jz      loc_8E845
                lea     eax, [r13-1]

loc_8D9AC:                              ; CODE XREF: sub_8CB70+E2D↑j
                mov     fs:0FFFFFFFFFFFFFF55h, al
                mov     ecx, r15d
                mov     dword ptr [rsp+0C58h+var_C28], ecx
                mov     rax, [rbp+0]
                cmp     rax, 2
                jnz     loc_8DEC0

loc_8D9C9:                              ; CODE XREF: sub_8CB70+D85↑j
                mov     ecx, [r8+110h]
                mov     rbx, [r8+118h]
                mov     r14d, 1
                mov     eax, 1
                lock xadd [rbx], rax
                cmp     ecx, 1
                jz      short loc_8D9EF
                xor     r14d, r14d

loc_8D9EF:                              ; CODE XREF: sub_8CB70+E7A↑j
                test    rax, rax
                js      loc_9019F       ; jumptable 000000000008CBAF cases 1,2
                                        ; jumptable 000000000008CC33 case 2
                                        ; jumptable 000000000008CCAA case 2
                cmp     dword ptr [rbp+0], 2
                jz      short loc_8DA66
                mov     rdi, rbp
                call    sub_FFEED0
                mov     r8, [rsp+0C58h+var_C58]
                test    byte ptr [r8+120h], 1
                jz      short loc_8DA2F
                mov     rax, [r8+128h]
                lock dec qword ptr [rax]
                jnz     short loc_8DA4C
                mov     rdi, [r8+128h]  ; ptr
                call    sub_FEDCC0
                jmp     short loc_8DA48
; ---------------------------------------------------------------------------

loc_8DA2F:                              ; CODE XREF: sub_8CB70+EA2↑j
                mov     rax, [r8+128h]
                lock dec qword ptr [rax]
                jnz     short loc_8DA4C
                mov     rdi, [r8+128h]  ; ptr
                call    sub_FEDB50

loc_8DA48:                              ; CODE XREF: sub_8CB70+EBD↑j
                mov     r8, [rsp+0C58h+var_C58]

loc_8DA4C:                              ; CODE XREF: sub_8CB70+EAF↑j
                                        ; sub_8CB70+ECA↑j
                mov     rax, [r8+150h]
                test    rax, rax
                jz      short loc_8DA66
                mov     rdi, [r8+158h]
                call    qword ptr [rax+18h]
                mov     r8, [rsp+0C58h+var_C58]

loc_8DA66:                              ; CODE XREF: sub_8CB70+E8C↑j
                                        ; sub_8CB70+EE6↑j
                mov     [r8+120h], r14
                mov     [r8+128h], rbx
                pxor    xmm0, xmm0
                movdqu  xmmword ptr [r8+130h], xmm0
                mov     qword ptr [r8+140h], 0
                mov     qword ptr [r8+148h], 0FFFFFFFFFFFFFFFFh
                mov     qword ptr [r8+150h], 0
                mov     qword ptr [r8+160h], 0
                mov     byte ptr [r8+168h], 0
                mov     eax, [rsp+0C58h+addr_len]
                mov     ecx, [rsp+0C58h+addr_len+3]
                mov     [r8+169h], eax
                mov     [r8+16Ch], ecx
                test    r14, r14
                mov     eax, 160h
                mov     ecx, 230h
                cmovnz  rcx, rax
                mov     eax, [rbx+rcx+88h]
                cmp     eax, 3B9ACA00h
                jz      loc_8E861
                mov     dword ptr [rsp+0C58h+var_BE8], r15d
                lea     r15, [r8+130h]
                mov     esi, [r8+178h]
                mov     rdx, [r8+170h]
                mov     rcx, [rbx+rcx+80h]
                lea     edi, [rsi+0F423Fh]
                cmp     esi, 3B8B87C1h
                mov     [rsp+0C58h+var_C50], r13
                jb      short loc_8DB3A
                inc     rdx
                jo      loc_8F8CE
                add     esi, 0C474783Fh
                mov     edi, esi

loc_8DB3A:                              ; CODE XREF: sub_8CB70+FB7↑j
                mov     qword ptr [rsp+0C58h+var_B98], rdx
                mov     dword ptr [rsp+0C58h+var_B98+8], edi
                mov     qword ptr [rsp+0C58h+dest], rcx
                mov     dword ptr [rsp+0C58h+dest+8], eax
                lea     rdi, [rsp+0C58h+addr_len]
                lea     rsi, [rsp+0C58h+var_B98]
                lea     rdx, [rsp+0C58h+dest]
                call    sub_FE83C0
                mov     r8, [rsp+0C58h+var_C58]
                mov     r13, [r8+128h]
                cmp     byte ptr [r8+120h], 0
                mov     eax, 160h
                mov     ecx, 230h
                cmovnz  rcx, rax
                cmp     dword ptr [r13+rcx+88h], 3B9ACA00h
                jz      loc_8E861
                mov     rax, [rsp+0C58h+var_AE8]
                add     r13, rcx
                mov     ecx, 3E8h
                mul     rcx
                mov     ecx, dword ptr [rsp+0C58h+var_AE0]
                imul    rbx, rcx, 431BDE83h
                shr     rbx, 32h
                add     rbx, rax
                adc     rdx, 0
                xor     eax, eax
                cmp     qword ptr [rsp+0C58h+addr_len], 0
                cmovnz  rdx, rax
                cmovnz  rbx, rax
                cmp     rbx, 0FFFFFFFFFFFFFFFDh
                mov     rax, 0FFFFFFFFFFFFFFFDh
                cmovnb  rbx, rax
                test    rdx, rdx
                cmovnz  rbx, rax
                lea     r14, [r13+48h]
                mov     ecx, 1
                xor     eax, eax
                lock cmpxchg [r13+48h], ecx
                jnz     loc_8F805

loc_8DC14:                              ; CODE XREF: sub_8CB70+2CA1↓j
                mov     rax, cs:qword_210E9B20
                xor     r12d, r12d
                mov     rcx, 7FFFFFFFFFFFFFFFh
                test    rax, rcx
                jnz     loc_8F816
                movzx   eax, byte ptr [r13+4Ch]
                mov     rax, [r8+148h]
                cmp     rax, 0FFFFFFFFFFFFFFFFh
                jz      short loc_8DC53

loc_8DC43:                              ; CODE XREF: sub_8CB70+2CC6↓j
                lea     rdi, [r13+50h]
                mov     rsi, r15
                call    sub_FFF070
                mov     r8, [rsp+0C58h+var_C58]

loc_8DC53:                              ; CODE XREF: sub_8CB70+10D1↑j
                                        ; sub_8CB70+2CCC↓j
                movzx   eax, byte ptr [r13+78h]
                test    al, al
                jz      short loc_8DCB7
                mov     rax, [r8+148h]
                xor     ebx, ebx
                cmp     rax, 0FFFFFFFFFFFFFFFFh
                mov     rdx, 7FFFFFFFFFFFFFFFh
                jz      loc_8DE7B
                mov     byte ptr [r8+168h], 1
                mov     qword ptr [r8+148h], 0FFFFFFFFFFFFFFFFh
                mov     rax, [r8+160h]
                db      66h, 66h, 66h, 66h, 2Eh
                nop     word ptr [rax+rax+00000000h]

loc_8DCA0:                              ; CODE XREF: sub_8CB70+1140↓j
                mov     rcx, rax
                or      rcx, 2
                lock cmpxchg [r8+160h], rcx
                jnz     short loc_8DCA0
                jmp     loc_8DE52
; ---------------------------------------------------------------------------

loc_8DCB7:                              ; CODE XREF: sub_8CB70+10EA↑j
                mov     [r8+148h], rbx
                mov     [r8+140h], rbx
                mov     rdx, [r8+148h]
                cmp     rdx, 0FFFFFFFFFFFFFFFFh
                jz      loc_8FBFF
                mov     [r8+140h], rdx
                mov     rax, [r13+58h]
                cmp     rdx, rax
                jbe     loc_8DE09
                xor     rax, rdx
                or      rax, 3Fh
                mov     rcx, 0FFFFFFFFEh
                cmp     rax, rcx
                cmovnb  rax, rcx
                bsr     rax, rax
                xor     al, 1
                movzx   eax, al
                imul    edi, eax, 2Bh ; '+'
                shr     edi, 8
                cmp     al, 23h ; '#'
                ja      loc_902D7
                mov     rsi, [r13+50h]
                imul    rdi, 410h
                mov     rax, [r8+140h]
                mov     ecx, [rsi+rdi+400h]
                add     ecx, ecx
                lea     ecx, [rcx+rcx*2]
                shr     rax, cl
                add     rsi, rdi
                and     eax, 3Fh
                mov     ecx, eax
                shl     ecx, 4
                lea     rdi, [rsi+rcx]
                mov     qword ptr [rsp+0C58h+dest], r15
                mov     rcx, [rcx+rsi]
                cmp     rcx, r15
                jz      loc_90025
                mov     [r8+138h], rcx
                mov     qword ptr [r8+130h], 0
                test    rcx, rcx
                jz      short loc_8DD78
                mov     [rcx], r15

loc_8DD78:                              ; CODE XREF: sub_8CB70+1203↑j
                mov     [rdi], r15
                cmp     qword ptr [rdi+8], 0
                jnz     short loc_8DD86
                mov     [rdi+8], r15

loc_8DD86:                              ; CODE XREF: sub_8CB70+1210↑j
                mov     edi, 1
                mov     ecx, eax
                shl     rdi, cl
                or      [rsi+408h], rdi
                mov     rax, [r13+70h]
                dec     rax
                xor     ebx, ebx
                cmp     rax, rdx
                mov     rdx, 7FFFFFFFFFFFFFFFh
                jb      loc_8DE7B
                mov     edi, [r13+44h]
                cmp     edi, 0FFFFFFFFh
                jz      loc_8E81E
                call    sub_EE780
                xor     ebx, ebx
                test    rax, rax
                mov     rdx, 7FFFFFFFFFFFFFFFh
                jz      loc_8DE7B
                mov     qword ptr [rsp+0C58h+addr_len], rax
                lea     rdi, aFailedToWakeIO ; "failed to wake I/O driver"
                lea     rcx, off_210E6D08
                lea     r8, off_210E79D8 ; "/home/aothuatgiadp/.cargo/registry/src/"...
                lea     rdx, [rsp+0C58h+addr_len]
                mov     esi, 19h
                call    sub_4AA30
; ---------------------------------------------------------------------------

loc_8DE09:                              ; CODE XREF: sub_8CB70+1174↑j
                mov     rax, [r8+148h]
                xor     ebx, ebx
                cmp     rax, 0FFFFFFFFFFFFFFFFh
                mov     rdx, 7FFFFFFFFFFFFFFFh
                jz      short loc_8DE7B
                mov     byte ptr [r8+168h], 0
                mov     qword ptr [r8+148h], 0FFFFFFFFFFFFFFFFh
                mov     rax, [r8+160h]
                nop     dword ptr [rax+00h]

loc_8DE40:                              ; CODE XREF: sub_8CB70+12E0↓j
                mov     rcx, rax
                or      rcx, 2
                lock cmpxchg [r8+160h], rcx
                jnz     short loc_8DE40

loc_8DE52:                              ; CODE XREF: sub_8CB70+1142↑j
                xor     ebx, ebx
                test    rax, rax
                jnz     short loc_8DE7B
                mov     rbx, [r8+150h]
                mov     r15, [r8+158h]
                mov     qword ptr [r8+150h], 0
                xor     eax, eax
                xchg    rax, [r8+160h]

loc_8DE7B:                              ; CODE XREF: sub_8CB70+1103↑j
                                        ; sub_8CB70+123D↑j ...
                test    r12b, r12b
                jnz     short loc_8DE90

loc_8DE80:                              ; CODE XREF: sub_8CB70+1CCA↓j
                mov     rax, cs:qword_210E9B20
                test    rax, rdx
                jnz     loc_8F972

loc_8DE90:                              ; CODE XREF: sub_8CB70+130E↑j
                                        ; sub_8CB70+1CD0↓j ...
                xor     eax, eax
                xchg    eax, [r14]
                cmp     eax, 2
                mov     r12, [rsp+0C58h+var_BE0]
                jz      loc_8F841
                test    rbx, rbx
                mov     r13, [rsp+0C58h+var_C50]
                jz      short loc_8DEB3

loc_8DEAD:                              ; CODE XREF: sub_8CB70+2CF3↓j
                mov     rdi, r15
                call    qword ptr [rbx+8]

loc_8DEB3:                              ; CODE XREF: sub_8CB70+133B↑j
                                        ; sub_8CB70+2CF9↓j
                mov     rax, [rbp+0]
                mov     r8, [rsp+0C58h+var_C58]
                mov     r15d, dword ptr [rsp+0C58h+var_BE8]

loc_8DEC0:                              ; CODE XREF: sub_8CB70+D8B↑j
                                        ; sub_8CB70+E53↑j
                mov     rcx, [r8+128h]
                test    al, 1
                mov     edx, 160h
                mov     eax, 230h
                cmovnz  rax, rdx
                cmp     dword ptr [rcx+rax+88h], 3B9ACA00h
                jz      loc_8E861
                movzx   eax, byte ptr [rcx+rax+78h]
                test    al, al
                jnz     loc_8EEAE
                mov     ecx, 1
                xor     eax, eax
                lock cmpxchg [r8+160h], rcx
                cmp     rax, 2
                jz      short loc_8DF5E
                test    rax, rax
                jnz     loc_8DFB2
                mov     rcx, [rsp+0C58h+var_C08]
                mov     rax, [rcx]
                mov     rdi, [rcx+8]
                call    qword ptr [rax]
                mov     r8, [rsp+0C58h+var_C58]
                mov     rcx, [r8+150h]
                mov     rdi, [r8+158h]
                mov     [r8+150h], rax
                mov     [r8+158h], rdx
                xor     edx, edx
                mov     eax, 1
                lock cmpxchg [r8+160h], rdx
                jnz     short loc_8DF75
                test    rcx, rcx
                jz      short loc_8DFB2
                call    qword ptr [rcx+18h]
                jmp     short loc_8DFAE
; ---------------------------------------------------------------------------

loc_8DF5E:                              ; CODE XREF: sub_8CB70+1399↑j
                mov     rcx, [rsp+0C58h+var_C08]
                mov     rax, [rcx]
                mov     rdi, [rcx+8]
                call    qword ptr [rax+10h]
                mov     r8, [rsp+0C58h+var_C58]
                pause
                jmp     short loc_8DFB2
; ---------------------------------------------------------------------------

loc_8DF75:                              ; CODE XREF: sub_8CB70+13E2↑j
                mov     rbx, [r8+150h]
                mov     r14, [r8+158h]
                mov     qword ptr [r8+150h], 0
                xor     eax, eax
                xchg    rax, [r8+160h]
                test    rcx, rcx
                jz      short loc_8DFA3
                call    qword ptr [rcx+8]
                mov     r8, [rsp+0C58h+var_C58]

loc_8DFA3:                              ; CODE XREF: sub_8CB70+142A↑j
                test    rbx, rbx
                jz      short loc_8DFB2
                mov     rdi, r14
                call    qword ptr [rbx+8]

loc_8DFAE:                              ; CODE XREF: sub_8CB70+13EC↑j
                mov     r8, [rsp+0C58h+var_C58]

loc_8DFB2:                              ; CODE XREF: sub_8CB70+139E↑j
                                        ; sub_8CB70+13E7↑j ...
                mov     rax, [r8+148h]
                cmp     rax, 0FFFFFFFFFFFFFFFFh
                jnz     loc_8E7CD
                movzx   eax, byte ptr [r8+168h]
                test    al, al
                jnz     loc_901A1
                mov     rbx, r8
                mov     rdi, r12
                call    sub_64A80
                mov     rax, [rbx+108h]
                mov     ecx, eax
                and     ecx, 3
                mov     r13d, 2
                cmp     ecx, 1
                jnz     short loc_8E027
                lea     r14, [rax-1]
                mov     r15, [rax-1]
                mov     rbx, [rax+7]
                mov     rax, [rbx]
                test    rax, rax
                jz      short loc_8E00E

loc_8E009:                              ; CODE XREF: sub_8CB70+BB8↑j
                mov     rdi, r15
                call    rax

loc_8E00E:                              ; CODE XREF: sub_8CB70+1497↑j
                cmp     qword ptr [rbx+8], 0
                jz      short loc_8E01E
                mov     rdi, r15        ; ptr
                call    cs:free_ptr

loc_8E01E:                              ; CODE XREF: sub_8CB70+14A3↑j
                mov     rdi, r14        ; ptr
                call    cs:free_ptr

loc_8E027:                              ; CODE XREF: sub_8CB70+B9D↑j
                                        ; sub_8CB70+BFB↑j ...
                mov     rcx, [rsp+0C58h+var_BF8]
                mov     rax, [rsp+0C58h+var_338]
                mov     [rsp+0C58h+var_938], rax
                movaps  xmm0, [rsp+0C58h+var_368]
                movaps  xmm1, [rsp+0C58h+var_358]
                movaps  xmm2, [rsp+0C58h+src]
                movaps  [rsp+0C58h+var_948], xmm2
                movaps  [rsp+0C58h+var_958], xmm1
                movaps  [rsp+0C58h+var_968], xmm0
                mov     byte ptr [rcx], 1
                movdqa  xmm0, [rsp+0C58h+var_968]
                movaps  xmm1, [rsp+0C58h+var_958]
                movaps  xmm2, [rsp+0C58h+var_948]
                movdqa  [rsp+0C58h+var_9A8], xmm0
                movaps  [rsp+0C58h+var_998], xmm1
                movaps  [rsp+0C58h+var_988], xmm2
                mov     rax, [rsp+0C58h+var_938]
                mov     [rsp+0C58h+var_978], rax
                mov     rdi, [rsp+0C58h+var_BC0]
                call    sub_66130
                cmp     r13d, 2
                jz      loc_8F749
                mov     r8, [rsp+0C58h+var_C58]
                lea     rbx, [r8+50h]
                mov     [r8+50h], r13
                movaps  xmm0, [rsp+0C58h+var_9A8]
                movups  xmmword ptr [r8+58h], xmm0
                mov     rax, qword ptr [rsp+0C58h+var_998]
                mov     [r8+68h], rax
                movdqu  xmm0, [rsp+0C58h+var_998+8]
                movups  xmm1, [rsp+0C58h+var_988+8]
                movdqu  xmmword ptr [r8+70h], xmm0
                movups  xmmword ptr [r8+80h], xmm1
                movzx   eax, byte ptr [r8+0B2h]
                cmp     eax, 2
                jz      short loc_8E15D
                mov     edi, [r8+68h]   ; fd
                cmp     edi, 0FFFFFFFFh
                jz      loc_8E879
                and     eax, 1
                mov     dword ptr [rsp+0C58h+addr.sa_family], eax
                lea     rcx, [rsp+0C58h+addr] ; optval
                mov     esi, 6          ; level
                mov     edx, 1          ; optname
                mov     r8d, 4          ; optlen
                call    cs:setsockopt_ptr
                cmp     eax, 0FFFFFFFFh
                jnz     short loc_8E159
                call    cs:__errno_location_ptr

loc_8E159:                              ; CODE XREF: sub_8CB70+15E1↑j
                mov     r8, [rsp+0C58h+var_C58]

loc_8E15D:                              ; CODE XREF: sub_8CB70+15A7↑j
                movdqu  xmm0, xmmword ptr [rbx]
                movups  xmm1, xmmword ptr [rbx+10h]
                movups  xmmword ptr [r8+0A0h], xmm1
                movdqu  xmmword ptr [r8+90h], xmm0
                lea     rax, [r8+48h]
                mov     [r8+0B8h], rax
                mov     rdi, [r8+48h]   ; ptr
                lock inc qword ptr [rdi]
                jle     loc_9019F       ; jumptable 000000000008CBAF cases 1,2
                                        ; jumptable 000000000008CC33 case 2
                                        ; jumptable 000000000008CCAA case 2

loc_8E18F:                              ; CODE XREF: sub_8CB70+E0↑j
                xor     ecx, ecx
                mov     eax, 1
                lock cmpxchg [rdi], rcx
                jnz     loc_8E260
                mov     r8, [rdi+10h]
                mov     r15, [rdi+18h]
                mov     rax, [rdi+20h]
                mov     [rsp+0C58h+var_C50], rax
                mov     rax, [rdi+28h]
                mov     qword ptr [rsp+0C58h+var_C28], rax
                mov     rsi, [rdi+30h]
                mov     r11, [rdi+38h]
                mov     rbx, [rdi+48h]
                mov     rax, [rdi+60h]
                mov     [rsp+0C58h+var_BF8], rax
                mov     eax, [rdi+68h]
                mov     dword ptr [rsp+0C58h+var_BC0], eax
                mov     r9, [rdi+70h]
                mov     r14, [rdi+78h]
                mov     r10, [rdi+88h]
                mov     rax, [rdi+0A0h]
                mov     [rsp+0C58h+var_BE8], rax
                mov     eax, [rdi+0A8h]
                mov     dword ptr [rsp+0C58h+var_C08], eax
                movzx   eax, byte ptr [rdi+0B0h]
                mov     byte ptr [rsp+0C58h+var_BE0], al
                cmp     rdi, 0FFFFFFFFFFFFFFFFh
                jz      short loc_8E255
                lock dec qword ptr [rdi+8]
                jnz     short loc_8E255
                mov     [rsp+0C58h+var_C48], r14
                mov     r14, r8
                mov     r13, r9
                mov     rbp, r15
                mov     r15, r10
                mov     [rsp+0C58h+var_C40], rbx
                mov     rbx, r11
                mov     r12, rsi
                call    cs:free_ptr
                mov     rsi, r12
                mov     r11, rbx
                mov     rbx, [rsp+0C58h+var_C40]
                mov     r10, r15
                mov     r15, rbp
                mov     r9, r13
                mov     r8, r14
                mov     r14, [rsp+0C58h+var_C48]

loc_8E255:                              ; CODE XREF: sub_8CB70+169E↑j
                                        ; sub_8CB70+16A5↑j
                cmp     r8, 3
                jz      short loc_8E263
                jmp     loc_8E3A3
; ---------------------------------------------------------------------------

loc_8E260:                              ; CODE XREF: sub_8CB70+162B↑j
                mov     r15, rdi

loc_8E263:                              ; CODE XREF: sub_8CB70+16E9↑j
                lea     rsi, [r15+30h]
                lea     rdi, [rsp+0C58h+addr]
                call    sub_B89A0
                mov     r12, [r15+60h]
                lock inc qword ptr [r12]
                jle     loc_9019F       ; jumptable 000000000008CBAF cases 1,2
                                        ; jumptable 000000000008CC33 case 2
                                        ; jumptable 000000000008CCAA case 2
                mov     ebx, [r15+68h]
                mov     rax, qword ptr [rsp+0C58h+addr.sa_family]
                mov     [rsp+0C58h+var_C10], rax
                mov     rax, qword ptr [rsp+0C58h+addr.sa_data+6]
                mov     [rsp+0C58h+var_C38], rax
                mov     rax, [rsp+0C58h+var_7E0]
                mov     [rsp+0C58h+var_C40], rax
                lea     rsi, [r15+70h]
                lea     rdi, [rsp+0C58h+addr]
                call    sub_B89A0
                mov     rax, [r15+0A0h]
                lock inc qword ptr [rax]
                jle     loc_9019F       ; jumptable 000000000008CBAF cases 1,2
                                        ; jumptable 000000000008CC33 case 2
                                        ; jumptable 000000000008CCAA case 2
                mov     ecx, [r15+0A8h]
                mov     dword ptr [rsp+0C58h+var_C08], ecx
                mov     r13, qword ptr [rsp+0C58h+addr.sa_family]
                mov     rcx, qword ptr [rsp+0C58h+addr.sa_data+6]
                mov     [rsp+0C58h+var_C48], rcx
                mov     rdx, r15
                mov     r15, [rsp+0C58h+var_7E0]
                movzx   ecx, byte ptr [rdx+0B0h]
                mov     byte ptr [rsp+0C58h+var_BE0], cl
                mov     r14, [rdx+10h]
                mov     rbp, rdx
                lea     rsi, [rdx+18h]
                lea     rdi, [rsp+0C58h+addr.sa_data+6]
                cmp     r14, 2
                mov     dword ptr [rsp+0C58h+var_BC0], ebx
                mov     [rsp+0C58h+var_BE8], rax
                jz      short loc_8E33A
                cmp     r14d, 1
                jnz     short loc_8E341
                lea     rdx, off_210C96B8 ; "/home/aothuatgiadp/.cargo/registry/src/"...
                jmp     short loc_8E348
; ---------------------------------------------------------------------------

loc_8E33A:                              ; CODE XREF: sub_8CB70+17B9↑j
                call    sub_B6940
                jmp     short loc_8E34D
; ---------------------------------------------------------------------------

loc_8E341:                              ; CODE XREF: sub_8CB70+17BF↑j
                lea     rdx, off_210C96A0 ; "/home/aothuatgiadp/.cargo/registry/src/"...

loc_8E348:                              ; CODE XREF: sub_8CB70+17C8↑j
                call    sub_B6810

loc_8E34D:                              ; CODE XREF: sub_8CB70+17CF↑j
                mov     rbx, qword ptr [rsp+0C58h+addr.sa_data+6]
                mov     rax, [rsp+470h]
                mov     [rsp+0C58h+var_C50], rax
                mov     rax, [rsp+0C58h+var_7E0]
                mov     qword ptr [rsp+0C58h+var_C28], rax
                lock dec qword ptr [rbp+0]
                mov     [rsp+0C58h+var_BF8], r12
                jnz     short loc_8E383
                mov     rdi, rbp        ; ptr
                call    sub_B40E0

loc_8E383:                              ; CODE XREF: sub_8CB70+1809↑j
                mov     r8, r14
                mov     r14, [rsp+0C58h+var_C48]
                mov     r9, r13
                mov     r10, r15
                mov     r15, rbx
                mov     r11, [rsp+0C58h+var_C38]
                mov     rsi, [rsp+0C58h+var_C10]
                mov     rbx, [rsp+0C58h+var_C40]

loc_8E3A3:                              ; CODE XREF: sub_8CB70+16EB↑j
                movdqa  xmm0, xmmword ptr [rsi]
                imul    rax, r11, 0FFFFFFFFFFFFFE90h
                lea     rdi, [rsi+rax]
                add     rdi, 0FFFFFFFFFFFFFE90h ; ptr
                lea     r13, [rsi+10h]
                pmovmskb r12d, xmm0
                not     r12d
                cmp     byte ptr fs:0FFFFFFFFFFFFFFF8h, 1
                jnz     loc_8E885
                mov     rax, fs:0FFFFFFFFFFFFFFE8h
                mov     rcx, fs:0FFFFFFFFFFFFFFF0h

loc_8E3E6:                              ; CODE XREF: sub_8CB70+1D85↓j
                lea     rdx, [rax+1]
                mov     fs:0FFFFFFFFFFFFFFE8h, rdx
                movups  xmm1, xmmword ptr cs:off_210E6EA0
                movaps  [rsp+0C58h+var_B38], xmm1
                movups  xmm2, cs:xmmword_210E6EB0
                movaps  [rsp+0C58h+var_B28], xmm2
                mov     qword ptr [rsp+0C58h+var_B18], rax
                mov     qword ptr [rsp+0C58h+var_B18+8], rcx
                test    rbx, rbx
                jnz     loc_8E8FA

loc_8E42A:                              ; CODE XREF: sub_8CB70+1E27↓j
                                        ; sub_8CB70+234B↓j ...
                mov     rbx, 0B19AB5C45606EFh
                test    r11, r11
                jz      short loc_8E470
                cmp     r11, rbx
                jz      short loc_8E470
                mov     r12, r14
                mov     r14, r8
                mov     rbp, r9
                mov     r13, r15
                mov     r15, r10
                call    cs:free_ptr
                movups  xmm2, cs:xmmword_210E6EB0
                movups  xmm1, xmmword ptr cs:off_210E6EA0
                mov     r10, r15
                mov     r15, r13
                mov     r9, rbp
                mov     r8, r14
                mov     r14, r12

loc_8E470:                              ; CODE XREF: sub_8CB70+18C7↑j
                                        ; sub_8CB70+18CC↑j
                movdqa  xmm0, xmmword ptr [r9]
                imul    rax, r14, 0FFFFFFFFFFFFFE90h
                lea     rdi, [r9+rax]
                add     rdi, 0FFFFFFFFFFFFFE90h ; ptr
                lea     r12, [r9+10h]
                pmovmskb ebp, xmm0
                not     ebp
                cmp     byte ptr fs:0FFFFFFFFFFFFFFF8h, 1
                jnz     loc_8EBBE
                mov     rax, fs:0FFFFFFFFFFFFFFE8h
                mov     rcx, fs:0FFFFFFFFFFFFFFF0h

loc_8E4B2:                              ; CODE XREF: sub_8CB70+20AC↓j
                lea     rdx, [rax+1]
                mov     fs:0FFFFFFFFFFFFFFE8h, rdx
                movaps  [rsp+0C58h+var_B98], xmm1
                movaps  [rsp+0C58h+var_B88], xmm2
                mov     qword ptr [rsp+0C58h+var_B78], rax
                mov     qword ptr [rsp+0C58h+var_B78+8], rcx
                test    r10, r10
                jnz     loc_8EC21

loc_8E4E8:                              ; CODE XREF: sub_8CB70+211E↓j
                                        ; sub_8CB70+2442↓j
                test    r14, r14
                jz      short loc_8E4FE
                cmp     r14, rbx
                jz      short loc_8E4FE
                mov     r14, r8
                call    cs:free_ptr
                mov     r8, r14

loc_8E4FE:                              ; CODE XREF: sub_8CB70+197B↑j
                                        ; sub_8CB70+1980↑j
                test    r8, r8
                jz      short loc_8E52D
                cmp     r8, 1
                jnz     short loc_8E553
                mov     qword ptr [rsp+0C58h+var_368+8], r15
                mov     rax, [rsp+0C58h+var_C50]
                mov     qword ptr [rsp+0C58h+var_358], rax
                mov     rax, qword ptr [rsp+0C58h+var_C28]
                mov     qword ptr [rsp+0C58h+var_358+8], rax
                jmp     short loc_8E575
; ---------------------------------------------------------------------------

loc_8E52D:                              ; CODE XREF: sub_8CB70+1991↑j
                mov     qword ptr [rsp+0C58h+var_368+8], r15
                mov     rax, [rsp+0C58h+var_C50]
                mov     qword ptr [rsp+0C58h+var_358], rax
                mov     rax, qword ptr [rsp+0C58h+var_C28]
                mov     qword ptr [rsp+0C58h+var_358+8], rax
                xor     eax, eax
                jmp     short loc_8E57A
; ---------------------------------------------------------------------------

loc_8E553:                              ; CODE XREF: sub_8CB70+1997↑j
                shr     r15, 20h
                test    r15b, r15b
                jnz     loc_8F88D
                lea     rdi, [rsp+0C58h+var_368+8]
                mov     rsi, [rsp+0C58h+var_C50]
                mov     rax, qword ptr [rsp+0C58h+var_C28]
                call    qword ptr [rax+20h]

loc_8E575:                              ; CODE XREF: sub_8CB70+19BB↑j
                mov     eax, 1

loc_8E57A:                              ; CODE XREF: sub_8CB70+19E1↑j
                mov     qword ptr [rsp+0C58h+var_368], rax
                movaps  xmm0, [rsp+0C58h+var_B38]
                movaps  xmm1, [rsp+0C58h+var_B28]
                movaps  xmm2, [rsp+0C58h+var_B18]
                movaps  [rsp+0C58h+var_7D8], xmm0
                movaps  xmmword ptr [rsp+0C58h+var_7C8], xmm1
                movaps  [rsp+0C58h+var_7B8], xmm2
                mov     rax, qword ptr [rsp+0C58h+var_358]
                mov     [rsp+470h], rax
                mov     rax, qword ptr [rsp+0C58h+var_358+8]
                mov     [rsp+0C58h+var_7E0], rax
                mov     rax, qword ptr [rsp+0C58h+var_368]
                mov     qword ptr [rsp+0C58h+addr.sa_family], rax
                mov     rax, qword ptr [rsp+0C58h+var_368+8]
                mov     qword ptr [rsp+0C58h+addr.sa_data+6], rax
                mov     edi, 0B8h       ; size
                call    cs:malloc_ptr
                test    rax, rax
                jz      loc_8EE9F
                mov     r12, rax
                mov     qword ptr [rax], 1
                mov     qword ptr [rax+8], 1
                movaps  xmm0, xmmword ptr [rsp+0C58h+addr.sa_family]
                movaps  xmm1, xmmword ptr [rsp+470h]
                movaps  xmm2, [rsp+0C58h+var_7D8]
                movaps  xmm3, xmmword ptr [rsp+0C58h+var_7C8]
                movups  xmmword ptr [rax+10h], xmm0
                movups  xmmword ptr [rax+20h], xmm1
                movups  xmmword ptr [rax+30h], xmm2
                movups  xmmword ptr [rax+40h], xmm3
                movaps  xmm0, [rsp+0C58h+var_7B8]
                movups  xmmword ptr [rax+50h], xmm0
                mov     rax, [rsp+0C58h+var_BF8]
                mov     [r12+60h], rax
                mov     eax, dword ptr [rsp+0C58h+var_BC0]
                mov     [r12+68h], eax
                movaps  xmm0, [rsp+0C58h+var_B98]
                movaps  xmm1, [rsp+0C58h+var_B88]
                movaps  xmm2, [rsp+0C58h+var_B78]
                movups  xmmword ptr [r12+70h], xmm0
                movups  xmmword ptr [r12+80h], xmm1
                movups  xmmword ptr [r12+90h], xmm2
                mov     rax, [rsp+0C58h+var_BE8]
                mov     [r12+0A0h], rax
                mov     eax, dword ptr [rsp+0C58h+var_C08]
                mov     [r12+0A8h], eax
                movzx   eax, byte ptr [rsp+0C58h+var_BE0]
                mov     [r12+0B0h], al
                mov     r8, [rsp+0C58h+var_C58]
                mov     qword ptr [r8+0B8h], 0
                mov     rsi, 7FFFFFFFFFFFFFFFh

loc_8E6D9:                              ; CODE XREF: sub_8CB70+8D↑j
                lea     rax, [r8+90h]
                movdqu  xmm0, xmmword ptr [r8+90h]
                movups  xmm1, xmmword ptr [r8+0A0h]
                movaps  [rsp+0C58h+var_4A8], xmm1
                movdqa  [rsp+0C58h+dest], xmm0
                db      66h, 66h, 66h, 66h, 2Eh
                nop     word ptr [rax+rax+00000000h]

loc_8E710:                              ; CODE XREF: sub_8CB70+1BB1↓j
                mov     ecx, 1
                lock xadd cs:qword_210E99B8, rcx
                test    rcx, rcx
                jz      short loc_8E710
                mov     qword ptr [rsp+0C58h+var_BB8], rcx
                lea     rcx, [rsp+0C58h+var_BB8]
                mov     qword ptr [rsp+0C58h+var_368], rcx
                lea     rcx, [rsp+0C58h+var_B08]
                mov     qword ptr [rsp+0C58h+var_368+8], rcx
                movdqu  xmm0, xmmword ptr [rax]
                movups  xmm1, xmmword ptr [rax+10h]
                movdqu  [rsp+0C58h+var_358], xmm0
                movups  [rsp+0C58h+src], xmm1
                mov     [rsp+0C58h+var_338], r12
                mov     [rsp+0C58h+var_38], 0
                movzx   eax, byte ptr fs:0FFFFFFFFFFFFFF58h
                cmp     eax, 1
                jz      loc_8F015
                cmp     eax, 2
                jnz     loc_8EFE6
                lea     rdi, [rsp+0C58h+var_358]
                call    sub_67390
                mov     rax, [rsp+0C58h+var_338]
                lock dec qword ptr [rax]
                mov     bl, 1
                jnz     short loc_8E7B9
                mov     rdi, [rsp+0C58h+var_338] ; ptr
                call    sub_B40E0

loc_8E7B9:                              ; CODE XREF: sub_8CB70+1C3A↑j
                mov     byte ptr [rsp+0C58h+addr.sa_family], bl
                lea     rdi, [rsp+0C58h+addr]
                call    sub_46D20
; ---------------------------------------------------------------------------

loc_8E7CD:                              ; CODE XREF: sub_8CB70+144D↑j
                cmp     byte ptr [rsp+0C58h+var_C28], 0
                jz      short loc_8E817
                movzx   eax, byte ptr fs:0FFFFFFFFFFFFFF58h
                cmp     eax, 1
                jz      short loc_8E805
                cmp     eax, 2
                jz      short loc_8E817
                lea     rsi, sub_5BC70
                mov     rdi, [rsp+0C58h+var_C40]
                call    sub_FE1FB0
                mov     byte ptr fs:0FFFFFFFFFFFFFF58h, 1
                mov     r8, [rsp+0C58h+var_C58]

loc_8E805:                              ; CODE XREF: sub_8CB70+1C70↑j
                mov     fs:0FFFFFFFFFFFFFF54h, r15b
                mov     fs:0FFFFFFFFFFFFFF55h, r13b

loc_8E817:                              ; CODE XREF: sub_8CB70+1C62↑j
                                        ; sub_8CB70+1C75↑j
                mov     al, 4
                jmp     loc_8D22F
; ---------------------------------------------------------------------------

loc_8E81E:                              ; CODE XREF: sub_8CB70+124A↑j
                mov     rdi, [r13+0]
                add     rdi, 10h
                call    sub_FF32F0
                xor     ebx, ebx
                mov     rdx, 7FFFFFFFFFFFFFFFh
                test    r12b, r12b
                jz      loc_8DE80
                jmp     loc_8DE90
; ---------------------------------------------------------------------------

loc_8E845:                              ; CODE XREF: sub_8CB70+E32↑j
                mov     rax, [rsp+0C58h+var_C08]
                mov     rdi, [rax]
                mov     rsi, [rax+8]
                call    sub_FF2660
                mov     r8, [rsp+0C58h+var_C58]
                mov     al, 4
                jmp     loc_8D22F
; ---------------------------------------------------------------------------

loc_8E861:                              ; CODE XREF: sub_8CB70+F7E↑j
                                        ; sub_8CB70+1032↑j ...
                lea     rdi, aATokio1XContex_0 ; "A Tokio 1.x context was found, but time"...
                lea     rdx, off_210E7AB8 ; "/home/aothuatgiadp/.cargo/registry/src/"...
                mov     esi, 73h ; 's'
                call    sub_4AAB0
; ---------------------------------------------------------------------------

loc_8E879:                              ; CODE XREF: sub_8CB70+89D↑j
                                        ; sub_8CB70+15B0↑j
                lea     rdi, off_210E7058 ; "/home/aothuatgiadp/.cargo/registry/src/"...
                call    sub_4A8E0
; ---------------------------------------------------------------------------

loc_8E885:                              ; CODE XREF: sub_8CB70+185E↑j
                mov     [rsp+0C58h+var_C48], r14
                mov     r14, r8
                mov     [rsp+0C58h+var_BC8], r13
                mov     r13, r9
                mov     [rsp+0C58h+var_C38], r15
                mov     [rsp+0C58h+var_BF0], r10
                mov     [rsp+0C58h+var_C40], rbx
                mov     rbx, r11
                mov     rbp, rsi
                mov     r15, rdi
                call    sub_FEC4C0
                mov     rdi, r15
                mov     rsi, rbp
                mov     r11, rbx
                mov     rbx, [rsp+0C58h+var_C40]
                mov     r10, [rsp+0C58h+var_BF0]
                mov     r15, [rsp+0C58h+var_C38]
                mov     r9, r13
                mov     r13, [rsp+0C58h+var_BC8]
                mov     r8, r14
                mov     r14, [rsp+0C58h+var_C48]
                mov     rcx, rdx
                mov     fs:0FFFFFFFFFFFFFFF0h, rdx
                mov     byte ptr fs:0FFFFFFFFFFFFFFF8h, 1
                jmp     loc_8E3E6
; ---------------------------------------------------------------------------

loc_8E8FA:                              ; CODE XREF: sub_8CB70+18B4↑j
                mov     [rsp+0C58h+var_BC8], r13
                mov     [rsp+0C58h+var_C10], rsi
                lea     rdx, [rsp+0C58h+var_B38]
                mov     [rsp+0C58h+var_B60], rdi
                mov     rdi, rdx
                mov     rsi, rbx
                mov     rdx, rax
                mov     [rsp+0C58h+var_C00], r8
                mov     [rsp+0C58h+var_C48], r9
                mov     [rsp+0C58h+var_BF0], r10
                mov     [rsp+0C58h+var_C38], r11
                call    sub_49A40
                mov     rdi, [rsp+0C58h+var_B60]
                movups  xmm2, cs:xmmword_210E6EB0
                movups  xmm1, xmmword ptr cs:off_210E6EA0
                mov     r11, [rsp+0C58h+var_C38]
                mov     r10, [rsp+0C58h+var_BF0]
                mov     r9, [rsp+0C58h+var_C48]
                mov     r8, [rsp+0C58h+var_C00]
                jmp     short loc_8E99D
; ---------------------------------------------------------------------------

loc_8E965:                              ; CODE XREF: sub_8CB70+203B↓j
                                        ; sub_8CB70+2049↓j
                mov     rbx, [rsp+0C58h+var_C40]
                test    rbx, rbx
                mov     r8, [rsp+0C58h+var_C00]
                mov     r9, [rsp+0C58h+var_C48]
                mov     r10, [rsp+0C58h+var_BF0]
                mov     r11, [rsp+0C58h+var_C38]
                movups  xmm1, xmmword ptr cs:off_210E6EA0
                movups  xmm2, cs:xmmword_210E6EB0
                mov     rdi, [rsp+0C58h+var_B60]
                jz      loc_8E42A

loc_8E99D:                              ; CODE XREF: sub_8CB70+1DF3↑j
                test    r12w, r12w
                mov     rbp, [rsp+0C58h+var_C10]
                mov     rax, [rsp+0C58h+var_BC8]
                jnz     short loc_8E9D0

loc_8E9B0:                              ; CODE XREF: sub_8CB70+1E5B↓j
                movdqa  xmm0, xmmword ptr [rax]
                pmovmskb r12d, xmm0
                add     rbp, 0FFFFFFFFFFFFE900h
                add     rax, 10h
                cmp     r12d, 0FFFFh
                jz      short loc_8E9B0
                not     r12d

loc_8E9D0:                              ; CODE XREF: sub_8CB70+1E3E↑j
                mov     [rsp+0C58h+var_BC8], rax
                lea     eax, [r12-1]
                tzcnt   ecx, r12d
                and     eax, r12d
                mov     r12d, eax
                neg     rcx
                mov     rdx, rbp
                imul    rsi, rcx, 170h
                dec     rbx
                mov     [rsp+0C58h+var_C40], rbx
                mov     ecx, [rbp+rsi-170h]
                mov     rbx, [rbp+rsi-168h]
                mov     rax, [rbp+rsi-150h]
                mov     [rsp+0C58h+var_BA8], rax
                movdqu  xmm0, xmmword ptr [rbp+rsi-160h]
                movdqa  [rsp+0C58h+var_BB8], xmm0
                cmp     rbx, 4
                jz      loc_8EEB3
                mov     [rsp+0C58h+var_B44], ecx
                mov     [rsp+0C58h+var_C10], rdx
                add     rsi, rdx
                add     rsi, 0FFFFFFFFFFFFFEB8h ; src
                mov     edx, 148h       ; n
                lea     rbp, [rsp+0C58h+dest]
                mov     rdi, rbp        ; dest
                call    cs:memmove_ptr
                cmp     rbx, 3
                jnz     short loc_8EAA3
                mov     rax, [rsp+0C58h+var_BA8]
                mov     qword ptr [rsp+0C58h+var_B88], rax
                movaps  xmm0, [rsp+0C58h+var_BB8]
                movaps  [rsp+0C58h+var_B98], xmm0
                mov     ebx, 3
                lea     rsi, [rsp+0C58h+addr_len]
                mov     r13, cs:memcpy_ptr
                jmp     loc_8EB3E
; ---------------------------------------------------------------------------

loc_8EAA3:                              ; CODE XREF: sub_8CB70+1EF8↑j
                mov     qword ptr [rsp+0C58h+var_968], rbx
                mov     rax, [rsp+0C58h+var_BA8]
                lea     rcx, [rsp+0C58h+var_968+8]
                mov     [rcx+10h], rax
                movaps  xmm0, [rsp+0C58h+var_BB8]
                movups  xmmword ptr [rcx], xmm0
                mov     edx, 148h       ; n
                lea     rdi, [rsp+0C58h+var_948] ; dest
                mov     rsi, rbp        ; src
                mov     r13, cs:memcpy_ptr
                call    r13 ; memcpy
                lea     rdi, [rsp+0C58h+var_368]
                lea     rsi, [rsp+0C58h+var_968]
                call    sub_B6160
                mov     rbx, qword ptr [rsp+0C58h+var_368]
                lea     rax, [rsp+0C58h+var_368+8]
                movups  xmm0, xmmword ptr [rax]
                movaps  [rsp+0C58h+var_B98], xmm0
                mov     rax, [rax+10h]
                mov     qword ptr [rsp+0C58h+var_B88], rax
                mov     edx, 148h       ; n
                lea     rbp, [rsp+0C58h+addr_len]
                mov     rdi, rbp        ; dest
                lea     rsi, [rsp+0C58h+src] ; src
                call    r13 ; memcpy
                mov     rsi, rbp        ; src

loc_8EB3E:                              ; CODE XREF: sub_8CB70+1F2E↑j
                mov     ebp, [rsp+0C58h+var_B44]
                mov     dword ptr [rsp+0C58h+addr.sa_family], ebp
                mov     qword ptr [rsp+0C58h+addr.sa_data+6], rbx
                mov     rax, qword ptr [rsp+0C58h+var_B88]
                lea     rbx, [rsp+0C58h+addr.sa_data+6]
                mov     [rbx+18h], rax
                movdqa  xmm0, [rsp+0C58h+var_B98]
                movdqu  xmmword ptr [rbx+8], xmm0
                mov     edx, 148h       ; n
                lea     rdi, [rsp+0C58h+var_7D8+8] ; dest
                call    r13 ; memcpy
                lea     r13, [rsp+0C58h+var_368]
                mov     rdi, r13        ; dest
                lea     rsi, [rsp+0C58h+var_B38]
                mov     edx, ebp
                mov     rcx, rbx
                call    sub_B9160
                cmp     dword ptr [rsp+0C58h+var_368], 4
                jz      loc_8E965
                mov     rdi, r13
                call    sub_B4300
                jmp     loc_8E965
; ---------------------------------------------------------------------------

loc_8EBBE:                              ; CODE XREF: sub_8CB70+192A↑j
                mov     rbx, rdi
                mov     [rsp+0C58h+var_C48], r14
                mov     [rsp+0C58h+var_C00], r8
                mov     r14, r9
                mov     r13, r15
                mov     r15, r10
                call    sub_FEC4C0
                movups  xmm2, cs:xmmword_210E6EB0
                movups  xmm1, xmmword ptr cs:off_210E6EA0
                mov     r10, r15
                mov     r15, r13
                mov     r9, r14
                mov     r8, [rsp+0C58h+var_C00]
                mov     r14, [rsp+0C58h+var_C48]
                mov     rdi, rbx
                mov     rbx, 0B19AB5C45606EFh
                mov     rcx, rdx
                mov     fs:0FFFFFFFFFFFFFFF0h, rdx
                mov     byte ptr fs:0FFFFFFFFFFFFFFF8h, 1
                jmp     loc_8E4B2
; ---------------------------------------------------------------------------

loc_8EC21:                              ; CODE XREF: sub_8CB70+1972↑j
                mov     [rsp+0C58h+var_C48], r9
                lea     rdx, [rsp+0C58h+var_B98]
                mov     [rsp+0C58h+var_C10], rdi
                mov     rdi, rdx
                mov     rsi, r10
                mov     rdx, rax
                mov     [rsp+0C58h+var_C00], r8
                mov     [rsp+0C58h+var_C38], r15
                mov     r15, r10
                call    sub_49A40
                mov     r9, r15
                mov     r15, [rsp+0C58h+var_C38]
                mov     r8, [rsp+0C58h+var_C00]
                mov     rdi, [rsp+0C58h+var_C10]
                lea     r13, [rsp+0C58h+dest]
                jmp     short loc_8EC94
; ---------------------------------------------------------------------------

loc_8EC6A:                              ; CODE XREF: sub_8CB70+231C↓j
                                        ; sub_8CB70+232A↓j
                mov     r9, [rsp+0C58h+var_BF0]
                test    r9, r9
                mov     rdi, [rsp+0C58h+var_C10]
                mov     r8, [rsp+0C58h+var_C00]
                mov     rbx, 0B19AB5C45606EFh
                lea     r13, [rsp+0C58h+dest]
                jz      loc_8E4E8

loc_8EC94:                              ; CODE XREF: sub_8CB70+20F8↑j
                test    bp, bp
                mov     rdx, [rsp+0C58h+var_C48]
                jnz     short loc_8ECBD

loc_8EC9E:                              ; CODE XREF: sub_8CB70+2149↓j
                movdqa  xmm0, xmmword ptr [r12]
                pmovmskb ebp, xmm0
                add     rdx, 0FFFFFFFFFFFFE900h
                add     r12, 10h
                cmp     ebp, 0FFFFh
                jz      short loc_8EC9E
                not     ebp

loc_8ECBD:                              ; CODE XREF: sub_8CB70+212C↑j
                lea     eax, [rbp-1]
                tzcnt   ecx, ebp
                and     eax, ebp
                mov     ebp, eax
                neg     rcx
                imul    rsi, rcx, 170h
                dec     r9
                mov     ecx, [rdx+rsi-170h]
                mov     rbx, [rdx+rsi-168h]
                mov     rax, [rdx+rsi-150h]
                mov     [rsp+0C58h+var_AF8], rax
                movdqu  xmm0, xmmword ptr [rdx+rsi-160h]
                movdqa  [rsp+0C58h+var_B08], xmm0
                cmp     rbx, 4
                mov     [rsp+0C58h+var_C48], rdx
                jz      loc_8EF64
                mov     dword ptr [rsp+0C58h+var_C40], ecx
                mov     [rsp+0C58h+var_BF0], r9
                add     rsi, rdx
                add     rsi, 0FFFFFFFFFFFFFEB8h ; src
                mov     edx, 148h       ; n
                mov     rdi, r13        ; dest
                call    cs:memmove_ptr
                cmp     rbx, 3
                jnz     short loc_8ED75
                mov     rax, [rsp+0C58h+var_AF8]
                mov     [rsp+0C58h+var_BA8], rax
                movaps  xmm0, [rsp+0C58h+var_B08]
                movaps  [rsp+0C58h+var_BB8], xmm0
                mov     ebx, 3
                lea     rsi, [rsp+0C58h+addr_len]
                mov     rcx, cs:memcpy_ptr
                jmp     loc_8EE1B
; ---------------------------------------------------------------------------

loc_8ED75:                              ; CODE XREF: sub_8CB70+21CA↑j
                mov     qword ptr [rsp+0C58h+var_968], rbx
                mov     rax, [rsp+0C58h+var_AF8]
                lea     rcx, [rsp+0C58h+var_968+8]
                mov     [rcx+10h], rax
                movaps  xmm0, [rsp+0C58h+var_B08]
                movups  xmmword ptr [rcx], xmm0
                mov     edx, 148h       ; n
                lea     rdi, [rsp+0C58h+var_948] ; dest
                mov     rsi, r13        ; src
                mov     rax, cs:memcpy_ptr
                call    rax ; memcpy
                lea     rdi, [rsp+0C58h+var_368]
                lea     rsi, [rsp+0C58h+var_968]
                call    sub_B6160
                mov     rbx, qword ptr [rsp+0C58h+var_368]
                lea     rax, [rsp+0C58h+var_368+8]
                movups  xmm0, xmmword ptr [rax]
                movaps  [rsp+0C58h+var_BB8], xmm0
                mov     rax, [rax+10h]
                mov     [rsp+0C58h+var_BA8], rax
                mov     edx, 148h       ; n
                lea     rdi, [rsp+0C58h+addr_len] ; dest
                lea     rsi, [rsp+0C58h+src] ; src
                mov     r13, cs:memcpy_ptr
                call    r13 ; memcpy
                lea     rsi, [rsp+0C58h+addr_len] ; src
                mov     rcx, r13

loc_8EE1B:                              ; CODE XREF: sub_8CB70+2200↑j
                mov     r13d, dword ptr [rsp+0C58h+var_C40]
                mov     dword ptr [rsp+0C58h+addr.sa_family], r13d
                mov     qword ptr [rsp+0C58h+addr.sa_data+6], rbx
                mov     rax, [rsp+0C58h+var_BA8]
                lea     rbx, [rsp+0C58h+addr.sa_data+6]
                mov     [rbx+18h], rax
                movdqa  xmm0, [rsp+0C58h+var_BB8]
                movdqu  xmmword ptr [rbx+8], xmm0
                mov     edx, 148h       ; n
                lea     rdi, [rsp+0C58h+var_7D8+8] ; dest
                call    rcx ; memcpy
                lea     rbx, [rsp+0C58h+var_368]
                mov     rdi, rbx        ; dest
                lea     rsi, [rsp+0C58h+var_B98]
                mov     edx, r13d
                lea     rcx, [rsp+0C58h+addr.sa_data+6]
                call    sub_B9160
                cmp     dword ptr [rsp+0C58h+var_368], 4
                jz      loc_8EC6A
                mov     rdi, rbx
                call    sub_B4300
                jmp     loc_8EC6A
; ---------------------------------------------------------------------------

loc_8EE9F:                              ; CODE XREF: sub_8CB70+1A90↑j
                mov     edi, 8
                mov     esi, 0B8h
                call    sub_497D5
; ---------------------------------------------------------------------------

loc_8EEAE:                              ; CODE XREF: sub_8CB70+137F↑j
                call    sub_55A70
; ---------------------------------------------------------------------------

loc_8EEB3:                              ; CODE XREF: sub_8CB70+1EC2↑j
                mov     r13, [rsp+0C58h+var_C40]
                test    r13, r13
                jz      loc_8E42A
                mov     rbp, rdx
                jmp     short loc_8EF2E
; ---------------------------------------------------------------------------

loc_8EEC6:                              ; CODE XREF: sub_8CB70+23CD↓j
                                        ; sub_8CB70+23EF↓j
                mov     [rsp+0C58h+var_BC8], rax
                lea     ebx, [r12-1]
                tzcnt   eax, r12d
                and     ebx, r12d
                neg     rax
                imul    rax, 170h
                mov     rbp, rcx
                lea     rdi, [rcx+rax]
                add     rdi, 0FFFFFFFFFFFFFE98h
                call    sub_B4300
                mov     r12d, ebx
                dec     r13
                mov     r8, [rsp+0C58h+var_C00]
                mov     r9, [rsp+0C58h+var_C48]
                mov     r10, [rsp+0C58h+var_BF0]
                mov     r11, [rsp+0C58h+var_C38]
                movups  xmm1, xmmword ptr cs:off_210E6EA0
                movups  xmm2, cs:xmmword_210E6EB0
                mov     rdi, [rsp+0C58h+var_B60]
                jz      loc_8E42A

loc_8EF2E:                              ; CODE XREF: sub_8CB70+2354↑j
                test    r12w, r12w
                mov     rcx, rbp
                mov     rax, [rsp+0C58h+var_BC8]
                jnz     short loc_8EEC6

loc_8EF3F:                              ; CODE XREF: sub_8CB70+23EA↓j
                movdqa  xmm0, xmmword ptr [rax]
                pmovmskb r12d, xmm0
                add     rcx, 0FFFFFFFFFFFFE900h
                add     rax, 10h
                cmp     r12d, 0FFFFh
                jz      short loc_8EF3F
                not     r12d
                jmp     loc_8EEC6
; ---------------------------------------------------------------------------

loc_8EF64:                              ; CODE XREF: sub_8CB70+219F↑j
                test    r9, r9
                jmp     short loc_8EFA8
; ---------------------------------------------------------------------------

loc_8EF69:                              ; CODE XREF: sub_8CB70+2453↓j
                                        ; sub_8CB70+2474↓j
                lea     ebx, [rbp-1]
                tzcnt   eax, ebp
                and     ebx, ebp
                neg     rax
                imul    rax, 170h
                mov     [rsp+0C58h+var_C48], rcx
                lea     rdi, [rcx+rax]
                add     rdi, 0FFFFFFFFFFFFFE98h
                call    sub_B4300
                mov     ebp, ebx
                mov     r9, r15
                dec     r9
                mov     rdi, [rsp+0C58h+var_C10]
                mov     r8, [rsp+0C58h+var_C00]
                mov     r15, [rsp+0C58h+var_C38]

loc_8EFA8:                              ; CODE XREF: sub_8CB70+23F7↑j
                mov     rbx, 0B19AB5C45606EFh
                jz      loc_8E4E8
                mov     r15, r9
                test    bp, bp
                mov     rcx, [rsp+0C58h+var_C48]
                jnz     short loc_8EF69

loc_8EFC5:                              ; CODE XREF: sub_8CB70+2470↓j
                movdqa  xmm0, xmmword ptr [r12]
                pmovmskb ebp, xmm0
                add     rcx, 0FFFFFFFFFFFFE900h
                add     r12, 10h
                cmp     ebp, 0FFFFh
                jz      short loc_8EFC5
                not     ebp
                jmp     short loc_8EF69
; ---------------------------------------------------------------------------

loc_8EFE6:                              ; CODE XREF: sub_8CB70+1C19↑j
                mov     rax, fs:0
                lea     rdi, [rax-0F0h]
                lea     rsi, sub_5BC70
                call    sub_FE1FB0
                mov     byte ptr fs:0FFFFFFFFFFFFFF58h, 1
                mov     rsi, 7FFFFFFFFFFFFFFFh

loc_8F015:                              ; CODE XREF: sub_8CB70+1C10↑j
                mov     rax, fs:0FFFFFFFFFFFFFF10h
                cmp     rax, rsi
                jnb     loc_8FAD1
                inc     rax
                mov     fs:0FFFFFFFFFFFFFF10h, rax
                mov     rbx, fs:0FFFFFFFFFFFFFF18h
                lea     rdi, [rsp+0C58h+addr] ; dest
                lea     rsi, [rsp+0C58h+var_368] ; src
                mov     edx, 338h       ; n
                call    cs:memcpy_ptr
                cmp     rbx, 2
                jz      loc_9021E
                mov     rax, qword ptr [rsp+0C58h+addr.sa_family]
                mov     r13, [rax]
                test    bl, 1
                jz      loc_8F2ED
                mov     r14, fs:0FFFFFFFFFFFFFF20h
                lock inc qword ptr [r14]
                jle     loc_9019F       ; jumptable 000000000008CBAF cases 1,2
                                        ; jumptable 000000000008CC33 case 2
                                        ; jumptable 000000000008CCAA case 2
                mov     rax, [r14+218h]
                pxor    xmm0, xmm0
                test    rax, rax
                jz      short loc_8F0AB
                lock inc qword ptr [rax]
                jle     loc_9019F       ; jumptable 000000000008CBAF cases 1,2
                                        ; jumptable 000000000008CC33 case 2
                                        ; jumptable 000000000008CCAA case 2
                movdqu  xmm0, xmmword ptr [r14+218h]

loc_8F0AB:                              ; CODE XREF: sub_8CB70+2526↑j
                movdqa  [rsp+0C58h+var_C28], xmm0
                movaps  xmm0, [rsp+0C58h+dest]
                movaps  xmm1, [rsp+0C58h+var_4A8]
                movups  [rsp+0C58h+var_958+4], xmm1
                movups  [rsp+0C58h+var_968+4], xmm0
                mov     qword ptr [rsp+0C58h+addr_len], 0
                lea     rdi, [rsp+0C58h+addr_len] ; memptr
                mov     esi, 80h        ; alignment
                mov     edx, 400h       ; size
                call    cs:posix_memalign_ptr
                xor     r15d, r15d
                test    eax, eax
                jnz     short loc_8F104
                mov     r15, qword ptr [rsp+0C58h+addr_len]

loc_8F104:                              ; CODE XREF: sub_8CB70+258A↑j
                test    r15, r15
                mov     rdi, 7FFFFFFFFFFFFFFFh
                jz      loc_8F7F6
                mov     qword ptr [r15], 0CCh
                mov     qword ptr [r15+8], 0
                lea     rax, off_210C82C0
                mov     [r15+10h], rax
                mov     [r15+20h], r14
                mov     [r15+28h], r13
                mov     dword ptr [r15+30h], 0
                movups  xmm0, [rsp+0C58h+var_968]
                movups  xmm1, [rsp+0C58h+var_958]
                movups  xmmword ptr [r15+34h], xmm0
                movups  xmmword ptr [r15+44h], xmm1
                mov     eax, dword ptr [rsp+0C58h+var_948]
                mov     [r15+54h], eax
                mov     [r15+58h], r12
                mov     byte ptr [r15+358h], 0
                xorps   xmm0, xmm0
                movaps  xmmword ptr [r15+360h], xmm0
                mov     qword ptr [r15+370h], 0
                movdqa  xmm0, [rsp+0C58h+var_C28]
                movdqa  xmmword ptr [r15+380h], xmm0
                mov     rax, [r14+0D0h]
                mov     [r15+18h], rax
                mov     rcx, [r14+0A8h]
                mov     rax, [r14+0C8h]
                and     rax, r13
                lea     rdx, [rax+rax*2]
                lea     r12, [rcx+rdx*8]
                mov     esi, 1
                xor     eax, eax
                lock cmpxchg [rcx+rdx*8], esi
                jnz     loc_8F8FE
                mov     rcx, cs:qword_210E9B20
                xor     eax, eax
                test    rcx, rdi
                jnz     loc_8F922

loc_8F1DF:                              ; CODE XREF: sub_8CB70+2DAC↓j
                                        ; sub_8CB70+2DC3↓j
                movzx   ecx, byte ptr [r12+4]
                lea     rcx, [r14+0B8h]
                lea     rdx, [r14+0C0h]
                mov     [rsp+0C58h+var_AD8], r12
                mov     byte ptr [rsp+0C58h+var_AD0], al
                mov     [rsp+0C58h+var_AE8], rcx
                mov     [rsp+0C58h+var_AE0], rdx
                mov     qword ptr [rsp+0C58h+addr_len], r13
                movzx   eax, byte ptr [r14+0D8h]
                test    al, al
                jz      loc_8F546
                mov     r12, [rsp+0C58h+var_AD8]
                test    byte ptr [rsp+0C58h+var_AD0], 1
                jnz     short loc_8F24C
                mov     rax, cs:qword_210E9B20
                test    rax, rdi
                jnz     loc_8FE5D

loc_8F24C:                              ; CODE XREF: sub_8CB70+26CA↑j
                                        ; sub_8CB70+32F4↓j ...
                xor     eax, eax
                xchg    eax, [r12]
                cmp     eax, 2
                jz      loc_8FC17

loc_8F25B:                              ; CODE XREF: sub_8CB70+30C1↓j
                mov     rax, [r15+10h]
                mov     rdi, r15
                call    qword ptr [rax+30h]
                mov     rax, 0FFFFFFFFFFFFFFC0h
                lock xadd [r15], rax
                cmp     rax, 3Fh ; '?'
                jbe     loc_8F8E6
                and     rax, 0FFFFFFFFFFFFFFC0h
                xor     r12d, r12d
                cmp     rax, 40h ; '@'
                jnz     short loc_8F295
                mov     rax, [r15+10h]
                mov     rdi, r15
                call    qword ptr [rax+10h]
                xor     r12d, r12d

loc_8F295:                              ; CODE XREF: sub_8CB70+2716↑j
                mov     qword ptr [rsp+0C58h+var_968], r13
                mov     rax, [r14+208h]
                test    rax, rax
                jz      short loc_8F2CE

loc_8F2A9:                              ; CODE XREF: sub_8CB70+2AA8↓j
                mov     rcx, [r14+210h]
                mov     rdx, [rcx+10h]
                dec     rdx
                and     rdx, 0FFFFFFFFFFFFFFF0h
                lea     rdi, [rax+rdx]
                add     rdi, 10h
                lea     rsi, [rsp+0C58h+var_968]
                call    qword ptr [rcx+28h]

loc_8F2CE:                              ; CODE XREF: sub_8CB70+2737↑j
                                        ; sub_8CB70+2AAE↓j
                test    r12, r12
                jz      loc_8F725
                add     r14, 10h
                mov     rdi, r14
                mov     rsi, r12
                xor     edx, edx
                call    sub_FF58B0
                jmp     loc_8F725
; ---------------------------------------------------------------------------

loc_8F2ED:                              ; CODE XREF: sub_8CB70+24FF↑j
                mov     rbp, fs:0FFFFFFFFFFFFFF20h
                lock inc qword ptr [rbp+0]
                jle     loc_9019F       ; jumptable 000000000008CBAF cases 1,2
                                        ; jumptable 000000000008CC33 case 2
                                        ; jumptable 000000000008CCAA case 2
                mov     rax, [rbp+210h]
                pxor    xmm0, xmm0
                test    rax, rax
                jz      short loc_8F323
                lock inc qword ptr [rax]
                jle     loc_9019F       ; jumptable 000000000008CBAF cases 1,2
                                        ; jumptable 000000000008CC33 case 2
                                        ; jumptable 000000000008CCAA case 2
                movdqa  xmm0, xmmword ptr [rbp+210h]

loc_8F323:                              ; CODE XREF: sub_8CB70+279F↑j
                movdqa  [rsp+0C58h+var_C28], xmm0
                movaps  xmm0, [rsp+0C58h+dest]
                movaps  xmm1, [rsp+0C58h+var_4A8]
                movups  [rsp+0C58h+var_958+4], xmm1
                movups  [rsp+0C58h+var_968+4], xmm0
                mov     qword ptr [rsp+0C58h+addr_len], 0
                lea     rdi, [rsp+0C58h+addr_len] ; memptr
                mov     esi, 80h        ; alignment
                mov     edx, 400h       ; size
                call    cs:posix_memalign_ptr
                xor     r15d, r15d
                test    eax, eax
                jnz     short loc_8F37C
                mov     r15, qword ptr [rsp+0C58h+addr_len]

loc_8F37C:                              ; CODE XREF: sub_8CB70+2802↑j
                test    r15, r15
                mov     rdi, 7FFFFFFFFFFFFFFFh
                jz      loc_8F7F6
                mov     qword ptr [r15], 0CCh
                mov     qword ptr [r15+8], 0
                lea     rax, off_210C8270
                mov     [r15+10h], rax
                mov     [r15+20h], rbp
                mov     [r15+28h], r13
                mov     dword ptr [r15+30h], 0
                movups  xmm0, [rsp+0C58h+var_968]
                movups  xmm1, [rsp+0C58h+var_958]
                movups  xmmword ptr [r15+34h], xmm0
                movups  xmmword ptr [r15+44h], xmm1
                mov     eax, dword ptr [rsp+0C58h+var_948]
                mov     [r15+54h], eax
                mov     [r15+58h], r12
                mov     byte ptr [r15+358h], 0
                xorps   xmm0, xmm0
                movaps  xmmword ptr [r15+360h], xmm0
                mov     qword ptr [r15+370h], 0
                movdqa  xmm0, [rsp+0C58h+var_C28]
                movdqa  xmmword ptr [r15+380h], xmm0
                mov     rax, [rbp+198h]
                mov     [r15+18h], rax
                mov     rcx, [rbp+170h]
                mov     rax, [rbp+190h]
                and     rax, r13
                lea     rdx, [rax+rax*2]
                lea     r14, [rcx+rdx*8]
                mov     esi, 1
                xor     eax, eax
                lock cmpxchg [rcx+rdx*8], esi
                jnz     loc_8F938
                mov     rcx, cs:qword_210E9B20
                xor     eax, eax
                test    rcx, rdi
                jnz     loc_8F95C

loc_8F457:                              ; CODE XREF: sub_8CB70+2DE6↓j
                                        ; sub_8CB70+2DFD↓j
                movzx   ecx, byte ptr [r14+4]
                lea     rcx, [rbp+180h]
                lea     rdx, [rbp+188h]
                mov     [rsp+0C58h+var_AD8], r14
                mov     byte ptr [rsp+0C58h+var_AD0], al
                mov     [rsp+0C58h+var_AE8], rcx
                mov     [rsp+0C58h+var_AE0], rdx
                mov     qword ptr [rsp+0C58h+addr_len], r13
                movzx   eax, byte ptr [rbp+1A0h]
                test    al, al
                jz      loc_8F623
                mov     r14, [rsp+0C58h+var_AD8]
                test    byte ptr [rsp+0C58h+var_AD0], 1
                jnz     short loc_8F4C2
                mov     rax, cs:qword_210E9B20
                test    rax, rdi
                jnz     loc_8FE75

loc_8F4C2:                              ; CODE XREF: sub_8CB70+2940↑j
                                        ; sub_8CB70+330C↓j ...
                xor     eax, eax
                xchg    eax, [r14]
                cmp     eax, 2
                jz      loc_8FC36

loc_8F4D0:                              ; CODE XREF: sub_8CB70+30E0↓j
                mov     rax, [r15+10h]
                mov     rdi, r15
                call    qword ptr [rax+30h]
                mov     rax, 0FFFFFFFFFFFFFFC0h
                lock xadd [r15], rax
                cmp     rax, 3Fh ; '?'
                jbe     loc_8F8E6
                and     rax, 0FFFFFFFFFFFFFFC0h
                cmp     rax, 40h ; '@'
                jnz     short loc_8F504
                mov     rax, [r15+10h]
                mov     rdi, r15
                call    qword ptr [rax+10h]

loc_8F504:                              ; CODE XREF: sub_8CB70+2988↑j
                mov     qword ptr [rsp+0C58h+var_968], r13
                mov     rax, [rbp+200h]
                test    rax, rax
                jz      loc_8F725
                mov     rcx, [rbp+208h]
                mov     rdx, [rcx+10h]
                dec     rdx
                and     rdx, 0FFFFFFFFFFFFFFF0h
                lea     rdi, [rax+rdx]
                add     rdi, 10h
                lea     rsi, [rsp+0C58h+var_968]
                call    qword ptr [rcx+28h]
                jmp     loc_8F725
; ---------------------------------------------------------------------------

loc_8F546:                              ; CODE XREF: sub_8CB70+26B4↑j
                mov     rcx, [r15+10h]
                mov     rax, [rcx+48h]
                mov     rax, [r15+rax]
                mov     qword ptr [rsp+0C58h+var_B38], rax
                cmp     rax, qword ptr [rsp+0C58h+addr_len]
                jnz     loc_8FBCD
                mov     r12, [rsp+0C58h+var_AD8]
                mov     qword ptr [rsp+0C58h+var_B98], r15
                mov     rax, [r12+8]
                cmp     rax, r15
                jz      loc_8FFA6
                mov     rcx, [rcx+38h]
                mov     [r15+rcx+8], rax
                mov     rcx, [r15+10h]
                mov     rcx, [rcx+38h]
                mov     qword ptr [r15+rcx], 0
                test    rax, rax
                jz      short loc_8F5B0
                mov     rcx, [rax+10h]
                mov     rcx, [rcx+38h]
                mov     [rax+rcx], r15

loc_8F5B0:                              ; CODE XREF: sub_8CB70+2A32↑j
                mov     [r12+8], r15
                cmp     qword ptr [r12+10h], 0
                jnz     short loc_8F5C2
                mov     [r12+10h], r15

loc_8F5C2:                              ; CODE XREF: sub_8CB70+2A4B↑j
                mov     rax, [rsp+0C58h+var_AE8]
                lock inc qword ptr [rax]
                mov     rax, [rsp+0C58h+var_AE0]
                lock inc qword ptr [rax]
                cmp     byte ptr [rsp+0C58h+var_AD0], 0
                jnz     short loc_8F5F4
                mov     rax, cs:qword_210E9B20
                test    rax, rdi
                jnz     loc_8FFF6

loc_8F5F4:                              ; CODE XREF: sub_8CB70+2A72↑j
                                        ; sub_8CB70+348D↓j ...
                xor     eax, eax
                xchg    eax, [r12]
                cmp     eax, 2
                jz      loc_8FE07

loc_8F603:                              ; CODE XREF: sub_8CB70+32B1↓j
                mov     r12, r15
                mov     qword ptr [rsp+0C58h+var_968], r13
                mov     rax, [r14+208h]
                test    rax, rax
                jnz     loc_8F2A9
                jmp     loc_8F2CE
; ---------------------------------------------------------------------------

loc_8F623:                              ; CODE XREF: sub_8CB70+292A↑j
                mov     rcx, [r15+10h]
                mov     rax, [rcx+48h]
                mov     rax, [r15+rax]
                mov     qword ptr [rsp+0C58h+var_B38], rax
                cmp     rax, qword ptr [rsp+0C58h+addr_len]
                jnz     loc_8FBCD
                mov     r14, [rsp+0C58h+var_AD8]
                mov     qword ptr [rsp+0C58h+var_B98], r15
                mov     rax, [r14+8]
                cmp     rax, r15
                jz      loc_8FFCE
                mov     rcx, [rcx+38h]
                mov     [r15+rcx+8], rax
                mov     rcx, [r15+10h]
                mov     rcx, [rcx+38h]
                mov     qword ptr [r15+rcx], 0
                test    rax, rax
                jz      short loc_8F68C
                mov     rcx, [rax+10h]
                mov     rcx, [rcx+38h]
                mov     [rax+rcx], r15

loc_8F68C:                              ; CODE XREF: sub_8CB70+2B0E↑j
                mov     [r14+8], r15
                cmp     qword ptr [r14+10h], 0
                jnz     short loc_8F69B
                mov     [r14+10h], r15

loc_8F69B:                              ; CODE XREF: sub_8CB70+2B25↑j
                mov     rax, [rsp+0C58h+var_AE8]
                lock inc qword ptr [rax]
                mov     rax, [rsp+0C58h+var_AE0]
                lock inc qword ptr [rax]
                cmp     byte ptr [rsp+0C58h+var_AD0], 0
                jnz     short loc_8F6CD
                mov     rax, cs:qword_210E9B20
                test    rax, rdi
                jnz     loc_9000E

loc_8F6CD:                              ; CODE XREF: sub_8CB70+2B4B↑j
                                        ; sub_8CB70+34A5↓j ...
                xor     eax, eax
                xchg    eax, [r14]
                cmp     eax, 2
                jz      loc_8FE26
                mov     qword ptr [rsp+0C58h+var_968], r13
                mov     rax, [rbp+200h]
                test    rax, rax
                jz      short loc_8F714

loc_8F6EF:                              ; CODE XREF: sub_8CB70+32E2↓j
                mov     rcx, [rbp+208h]
                mov     rdx, [rcx+10h]
                dec     rdx
                and     rdx, 0FFFFFFFFFFFFFFF0h
                lea     rdi, [rax+rdx]
                add     rdi, 10h
                lea     rsi, [rsp+0C58h+var_968]
                call    qword ptr [rcx+28h]

loc_8F714:                              ; CODE XREF: sub_8CB70+2B7D↑j
                                        ; sub_8CB70+32E8↓j
                mov     rdi, fs:0FFFFFFFFFFFFFF20h
                mov     rsi, r15
                call    sub_FF5240

loc_8F725:                              ; CODE XREF: sub_8CB70+2761↑j
                                        ; sub_8CB70+2778↑j ...
                dec     qword ptr fs:0FFFFFFFFFFFFFF10h
                mov     ecx, 84h
                mov     eax, 0CCh
                lock cmpxchg [r15], rcx
                jz      short loc_8F749
                mov     rax, [r15+10h]
                mov     rdi, r15
                call    qword ptr [rax+20h]

loc_8F749:                              ; CODE XREF: sub_8CB70+1552↑j
                                        ; sub_8CB70+2BCD↑j
                mov     r8, [rsp+0C58h+var_C58]
                mov     rsi, 7FFFFFFFFFFFFFFFh

loc_8F757:                              ; CODE XREF: sub_8CB70+6D↑j
                lea     rcx, [r8+28h]
                lea     rax, [r8+0B8h]
                mov     [r8+0B8h], rcx
                lea     rdx, [r8+100h]
                mov     [rsp+0C58h+var_BF8], rdx
                mov     byte ptr [r8+100h], 0

loc_8F77D:                              ; CODE XREF: sub_8CB70+D3↑j
                mov     [rsp+0C58h+var_BC0], rax
                lea     rax, [r8+108h]
                mov     [rsp+0C58h+var_C48], rax
                mov     [r8+108h], rcx
                lea     rdx, [r8+1B8h]
                mov     byte ptr [r8+1B8h], 0

loc_8F7A7:                              ; CODE XREF: sub_8CB70+159↑j
                mov     [rsp+0C58h+var_C10], rdx
                mov     [r8+110h], rcx
                mov     [r8+118h], rcx
                mov     qword ptr [r8+120h], 1
                lea     r13, [r8+140h]
                mov     byte ptr [r8+140h], 0
                mov     eax, 1
                mov     rdx, rcx

loc_8F7DC:                              ; CODE XREF: sub_8CB70+151↑j
                mov     [r8+128h], rdx
                mov     [r8+130h], rax
                mov     [r8+138h], rcx
                jmp     loc_8FF1F
; ---------------------------------------------------------------------------

loc_8F7F6:                              ; CODE XREF: sub_8CB70+25A1↑j
                                        ; sub_8CB70+2819↑j
                mov     edi, 80h
                mov     esi, 400h
                call    sub_497D5
; ---------------------------------------------------------------------------

loc_8F805:                              ; CODE XREF: sub_8CB70+109E↑j
                mov     rdi, r14
                call    sub_4FAB0
                mov     r8, [rsp+0C58h+var_C58]
                jmp     loc_8DC14
; ---------------------------------------------------------------------------

loc_8F816:                              ; CODE XREF: sub_8CB70+10BB↑j
                call    sub_4FBB0
                mov     r8, [rsp+0C58h+var_C58]
                mov     r12d, eax
                xor     r12b, 1
                movzx   eax, byte ptr [r13+4Ch]
                mov     rax, [r8+148h]
                cmp     rax, 0FFFFFFFFFFFFFFFFh
                jnz     loc_8DC43
                jmp     loc_8DC53
; ---------------------------------------------------------------------------

loc_8F841:                              ; CODE XREF: sub_8CB70+132D↑j
                mov     edi, 0CAh       ; sysno
                mov     rsi, r14
                mov     edx, 81h
                mov     ecx, 1
                xor     eax, eax
                call    cs:syscall_ptr
                test    rbx, rbx
                mov     r13, [rsp+0C58h+var_C50]
                jnz     loc_8DEAD
                jmp     loc_8DEB3
; ---------------------------------------------------------------------------

loc_8F86E:                              ; CODE XREF: sub_8CB70+719↑j
                mov     edi, 0CAh       ; sysno
                mov     rsi, r9
                mov     edx, 81h
                mov     ecx, 1
                xor     eax, eax
                call    cs:syscall_ptr
                jmp     loc_8D28F
; ---------------------------------------------------------------------------

loc_8F88D:                              ; CODE XREF: sub_8CB70+19EA↑j
                mov     rax, [rsp+0C58h+var_C50]
                mov     qword ptr [rsp+0C58h+addr.sa_family], rax
                mov     rax, qword ptr [rsp+0C58h+var_C28]
                mov     qword ptr [rsp+0C58h+addr.sa_data+6], rax
                lea     rdi, aCalledResultUn ; "called `Result::unwrap()` on an `Err` v"...
                lea     rcx, off_210C9398
                lea     r8, off_210C95D8 ; "/home/aothuatgiadp/.cargo/registry/src/"...
                lea     rdx, [rsp+0C58h+addr]
                mov     esi, 2Bh ; '+'
                call    sub_4AA30
; ---------------------------------------------------------------------------

loc_8F8CE:                              ; CODE XREF: sub_8CB70+C79↑j
                                        ; sub_8CB70+C8A↑j ...
                lea     rdi, aOverflowWhenAd ; "overflow when adding duration to instan"...
                lea     rdx, off_210E6250 ; "library/std/src/time.rs"
                mov     esi, 28h ; '('
                call    sub_4AAB0
; ---------------------------------------------------------------------------

loc_8F8E6:                              ; CODE XREF: sub_8CB70+2705↑j
                                        ; sub_8CB70+297A↑j
                lea     rdi, aAssertionFaile_44 ; "assertion failed: prev.ref_count() >= 1"
                lea     rdx, off_210E7EB0 ; "/home/aothuatgiadp/.cargo/registry/src/"...
                mov     esi, 27h ; '''
                call    sub_4A710
; ---------------------------------------------------------------------------

loc_8F8FE:                              ; CODE XREF: sub_8CB70+2657↑j
                mov     rdi, r12
                call    sub_4FAB0
                mov     rdi, 7FFFFFFFFFFFFFFFh
                mov     rcx, cs:qword_210E9B20
                xor     eax, eax
                test    rcx, rdi
                jz      loc_8F1DF

loc_8F922:                              ; CODE XREF: sub_8CB70+2669↑j
                call    sub_4FBB0
                mov     rdi, 7FFFFFFFFFFFFFFFh
                xor     al, 1
                jmp     loc_8F1DF
; ---------------------------------------------------------------------------

loc_8F938:                              ; CODE XREF: sub_8CB70+28CF↑j
                mov     rdi, r14
                call    sub_4FAB0
                mov     rdi, 7FFFFFFFFFFFFFFFh
                mov     rcx, cs:qword_210E9B20
                xor     eax, eax
                test    rcx, rdi
                jz      loc_8F457

loc_8F95C:                              ; CODE XREF: sub_8CB70+28E1↑j
                call    sub_4FBB0
                mov     rdi, 7FFFFFFFFFFFFFFFh
                xor     al, 1
                jmp     loc_8F457
; ---------------------------------------------------------------------------

loc_8F972:                              ; CODE XREF: sub_8CB70+131A↑j
                call    sub_4FBB0
                test    al, al
                jnz     loc_8DE90
                mov     byte ptr [r13+4Ch], 1
                jmp     loc_8DE90
; ---------------------------------------------------------------------------

loc_8F989:                              ; CODE XREF: sub_8CB70+A41↑j
                lea     rsi, sub_5BC70
                mov     rdi, r15
                call    sub_FE1FB0
                mov     byte ptr fs:0FFFFFFFFFFFFFF58h, 1
                mov     rsi, 7FFFFFFFFFFFFFFFh

loc_8F9AB:                              ; CODE XREF: sub_8CB70+A36↑j
                mov     rax, fs:0FFFFFFFFFFFFFF10h
                cmp     rax, rsi
                jnb     loc_8FAD1
                mov     word ptr [rsp+0C58h+var_C10], bx
                lea     rcx, [rax+1]
                mov     fs:0FFFFFFFFFFFFFF10h, rcx
                mov     r12, fs:0FFFFFFFFFFFFFF18h
                cmp     r12, 2
                jz      loc_9025D
                mov     rbx, fs:0FFFFFFFFFFFFFF20h
                mov     r13d, 1
                mov     eax, 1
                lock xadd [rbx], rax
                test    r12b, 1
                jnz     short loc_8FA04
                xor     r13d, r13d

loc_8FA04:                              ; CODE XREF: sub_8CB70+2E8F↑j
                test    rax, rax
                js      loc_9019F       ; jumptable 000000000008CBAF cases 1,2
                                        ; jumptable 000000000008CC33 case 2
                                        ; jumptable 000000000008CCAA case 2
                dec     qword ptr fs:0FFFFFFFFFFFFFF10h
                lea     r15, [rbx+230h]
                lea     rax, [rbx+160h]
                test    r13, r13
                cmovnz  r15, rax
                cmp     dword ptr [r15+44h], 0FFFFFFFFh
                jz      loc_8FADD
                lea     rax, [r15+8]
                mov     qword ptr [rsp+0C58h+var_C28], rax
                mov     ecx, 1
                xor     eax, eax
                lock cmpxchg [r15+8], ecx
                jnz     loc_8FAF5
                mov     [rsp+0C58h+var_C50], r12
                mov     rax, cs:qword_210E9B20
                test    rax, rsi
                jnz     loc_8FB1E

loc_8FA67:                              ; CODE XREF: sub_8CB70+2FA8↓j
                lea     rax, [r15+0Ch]
                mov     [rsp+0C58h+var_C38], rax
                movzx   eax, byte ptr [r15+0Ch]
                lea     rdi, [r15+10h]
                call    sub_FF2BE0
                mov     r12, rdx
                test    al, 1
                mov     rcx, 7FFFFFFFFFFFFFFFh
                mov     rsi, qword ptr [rsp+0C58h+var_C28]
                jz      loc_8FC6B

loc_8FA98:                              ; CODE XREF: sub_8CB70+2FED↓j
                mov     rax, cs:qword_210E9B20
                test    rax, rcx
                jnz     loc_8FDB0

loc_8FAA8:                              ; CODE XREF: sub_8CB70+2FF3↓j
                                        ; sub_8CB70+3256↓j
                xor     eax, eax
                xchg    eax, [rsi]
                cmp     eax, 2
                jnz     loc_900F4
                mov     edi, 0CAh       ; sysno
                mov     edx, 81h
                mov     ecx, 1
                xor     eax, eax
                call    cs:syscall_ptr
                jmp     loc_900F4
; ---------------------------------------------------------------------------

loc_8FAD1:                              ; CODE XREF: sub_8CB70+24B1↑j
                                        ; sub_8CB70+2E47↑j
                lea     rdi, off_210E71A8 ; "/home/aothuatgiadp/.cargo/registry/src/"...
                call    sub_4A9D0
; ---------------------------------------------------------------------------

loc_8FADD:                              ; CODE XREF: sub_8CB70+2EC0↑j
                lea     rdi, aATokio1XContex ; "A Tokio 1.x context was found, but IO i"...
                lea     rdx, off_210E7070 ; "/home/aothuatgiadp/.cargo/registry/src/"...
                mov     esi, 68h ; 'h'
                call    sub_4AAB0
; ---------------------------------------------------------------------------

loc_8FAF5:                              ; CODE XREF: sub_8CB70+2EDC↑j
                mov     rdi, qword ptr [rsp+0C58h+var_C28]
                call    sub_4FAB0
                mov     rsi, 7FFFFFFFFFFFFFFFh
                mov     [rsp+0C58h+var_C50], r12
                mov     rax, cs:qword_210E9B20
                test    rax, rsi
                jz      loc_8FA67

loc_8FB1E:                              ; CODE XREF: sub_8CB70+2EF1↑j
                call    sub_4FBB0
                mov     byte ptr [rsp+0C58h+var_C00], al
                lea     rax, [r15+0Ch]
                mov     [rsp+0C58h+var_C38], rax
                movzx   eax, byte ptr [r15+0Ch]
                lea     rdi, [r15+10h]
                call    sub_FF2BE0
                mov     r12, rdx
                test    al, 1
                jz      loc_8FC55
                cmp     byte ptr [rsp+0C58h+var_C00], 0
                mov     rcx, 7FFFFFFFFFFFFFFFh
                mov     rsi, qword ptr [rsp+0C58h+var_C28]
                jnz     loc_8FA98
                jmp     loc_8FAA8
; ---------------------------------------------------------------------------

loc_8FB68:                              ; CODE XREF: sub_8CB70+4F4↑j
                xor     bpl, 1
                mov     r9, [rsp+0C58h+var_C50]
                mov     rbx, [r8+180h]
                test    rbx, rbx
                jnz     loc_8D194

loc_8FB81:                              ; CODE XREF: sub_8CB70+61E↑j
                lea     rdi, off_210E7A38 ; "/home/aothuatgiadp/.cargo/registry/src/"...
                call    sub_4A8E0
; ---------------------------------------------------------------------------

loc_8FB8D:                              ; CODE XREF: sub_8CB70+699↑j
                mov     edi, 0CAh       ; sysno
                mov     rsi, r9
                mov     edx, 81h
                mov     ecx, 1
                xor     eax, eax
                call    cs:syscall_ptr
                mov     r8, [rsp+0C58h+var_C58]
                jmp     loc_8D20F
; ---------------------------------------------------------------------------

loc_8FBB0:                              ; CODE XREF: sub_8CB70+70B↑j
                call    sub_4FBB0
                mov     r9, [rsp+0C58h+var_C50]
                test    al, al
                jnz     loc_8D281
                mov     byte ptr [r12+1Ch], 1
                jmp     loc_8D281
; ---------------------------------------------------------------------------

loc_8FBCD:                              ; CODE XREF: sub_8CB70+29F2↑j
                                        ; sub_8CB70+2ACF↑j
                mov     qword ptr [rsp+0C58h+var_968], 0
                lea     r8, off_210C8210 ; "/home/aothuatgiadp/.cargo/registry/src/"...
                lea     rsi, [rsp+0C58h+var_B38]
                lea     rdx, [rsp+0C58h+addr_len]
                lea     rcx, [rsp+0C58h+var_968]
                xor     edi, edi
                call    sub_4AC82
; ---------------------------------------------------------------------------

loc_8FBFF:                              ; CODE XREF: sub_8CB70+1160↑j
                lea     rdi, aTimerAlreadyFi ; "Timer already fired"
                lea     rdx, off_210E7A78 ; "/home/aothuatgiadp/.cargo/registry/src/"...
                mov     esi, 13h
                call    sub_4AAB0
; ---------------------------------------------------------------------------

loc_8FC17:                              ; CODE XREF: sub_8CB70+26E5↑j
                mov     edi, 0CAh       ; sysno
                mov     rsi, r12
                mov     edx, 81h
                mov     ecx, 1
                xor     eax, eax
                call    cs:syscall_ptr
                jmp     loc_8F25B
; ---------------------------------------------------------------------------

loc_8FC36:                              ; CODE XREF: sub_8CB70+295A↑j
                mov     edi, 0CAh       ; sysno
                mov     rsi, r14
                mov     edx, 81h
                mov     ecx, 1
                xor     eax, eax
                call    cs:syscall_ptr
                jmp     loc_8F4D0
; ---------------------------------------------------------------------------

loc_8FC55:                              ; CODE XREF: sub_8CB70+2FD3↑j
                cmp     byte ptr [rsp+0C58h+var_C00], 0
                mov     rcx, 7FFFFFFFFFFFFFFFh
                mov     rsi, qword ptr [rsp+0C58h+var_C28]
                jz      short loc_8FC7B

loc_8FC6B:                              ; CODE XREF: sub_8CB70+2F22↑j
                mov     rax, cs:qword_210E9B20
                test    rax, rcx
                jnz     loc_8FDCB

loc_8FC7B:                              ; CODE XREF: sub_8CB70+30F9↑j
                                        ; sub_8CB70+3271↓j
                mov     [rsp+0C58h+var_BF0], rbx
                xor     eax, eax
                xchg    eax, [rsi]
                cmp     eax, 2
                jz      loc_8FD8F

loc_8FC8D:                              ; CODE XREF: sub_8CB70+323B↓j
                lea     rbx, [r12+80h]
                mov     edi, [r15+40h]  ; epfd
                mov     dword ptr [rsp+0C58h+addr.sa_family], 80002005h
                mov     qword ptr [rsp+0C58h+addr.sa_data+2], rbx
                lea     rcx, [rsp+0C58h+addr] ; event
                mov     esi, 1          ; op
                mov     edx, ebp        ; fd
                call    cs:epoll_ctl_ptr
                test    eax, eax
                js      short loc_8FCF0
                mov     rdi, r12
                movzx   r8d, word ptr [rsp+0C58h+var_C10]
                mov     r9d, dword ptr [rsp+0C58h+var_C08]
                mov     r10d, dword ptr [rsp+0C58h+var_BE8]
                mov     r11d, dword ptr [rsp+0C58h+var_C40]
                mov     rax, [rsp+0C58h+var_BE0]
                mov     r12, [rsp+0C58h+var_BF0]
                mov     rcx, [rsp+0C58h+var_C58]
                jmp     loc_8D638
; ---------------------------------------------------------------------------

loc_8FCF0:                              ; CODE XREF: sub_8CB70+3153↑j
                call    cs:__errno_location_ptr
                mov     r14d, [rax]
                shl     r14, 20h
                or      r14, 2
                xor     eax, eax
                mov     rsi, qword ptr [rsp+0C58h+var_C28]
                mov     ecx, 1
                lock cmpxchg [rsi], ecx
                jnz     loc_90046

loc_8FD17:                              ; CODE XREF: sub_8CB70+34E3↓j
                mov     rax, cs:qword_210E9B20
                xor     r13d, r13d
                mov     rdx, 7FFFFFFFFFFFFFFFh
                test    rax, rdx
                jnz     loc_90058
                movzx   eax, byte ptr [r15+0Ch]
                mov     rcx, [rbx]
                test    rcx, rcx
                jz      loc_90084

loc_8FD45:                              ; CODE XREF: sub_8CB70+350E↓j
                mov     rax, [r12+88h]
                mov     [rcx+8], rax
                test    rax, rax
                jz      loc_9009F

loc_8FD5A:                              ; CODE XREF: sub_8CB70+3529↓j
                mov     rcx, [rbx]
                mov     [rax], rcx
                pxor    xmm0, xmm0
                movdqu  xmmword ptr [rbx], xmm0
                lock dec qword ptr [r12]
                jnz     loc_900BF

loc_8FD73:                              ; CODE XREF: sub_8CB70+3549↓j
                mov     rdi, r12        ; ptr
                call    sub_FEE4D0
                mov     rsi, qword ptr [rsp+0C58h+var_C28]
                mov     rdx, 7FFFFFFFFFFFFFFFh
                jmp     loc_900BF
; ---------------------------------------------------------------------------

loc_8FD8F:                              ; CODE XREF: sub_8CB70+3117↑j
                mov     edi, 0CAh       ; sysno
                mov     rsi, qword ptr [rsp+0C58h+var_C28]
                mov     edx, 81h
                mov     ecx, 1
                xor     eax, eax
                call    cs:syscall_ptr
                jmp     loc_8FC8D
; ---------------------------------------------------------------------------

loc_8FDB0:                              ; CODE XREF: sub_8CB70+2F32↑j
                call    sub_4FBB0
                test    al, al
                jnz     short loc_8FDC1
                mov     rax, [rsp+0C58h+var_C38]
                mov     byte ptr [rax], 1

loc_8FDC1:                              ; CODE XREF: sub_8CB70+3247↑j
                mov     rsi, qword ptr [rsp+0C58h+var_C28]
                jmp     loc_8FAA8
; ---------------------------------------------------------------------------

loc_8FDCB:                              ; CODE XREF: sub_8CB70+3105↑j
                call    sub_4FBB0
                test    al, al
                jnz     short loc_8FDDC
                mov     rax, [rsp+0C58h+var_C38]
                mov     byte ptr [rax], 1

loc_8FDDC:                              ; CODE XREF: sub_8CB70+3262↑j
                mov     rsi, qword ptr [rsp+0C58h+var_C28]
                jmp     loc_8FC7B
; ---------------------------------------------------------------------------

loc_8FDE6:                              ; CODE XREF: sub_8CB70+68B↑j
                call    sub_4FBB0
                mov     r9, [rsp+0C58h+var_C50]
                mov     r8, [rsp+0C58h+var_C58]
                test    al, al
                jnz     loc_8D201
                mov     byte ptr [r12+1Ch], 1
                jmp     loc_8D201
; ---------------------------------------------------------------------------

loc_8FE07:                              ; CODE XREF: sub_8CB70+2A8D↑j
                mov     edi, 0CAh       ; sysno
                mov     rsi, r12
                mov     edx, 81h
                mov     ecx, 1
                xor     eax, eax
                call    cs:syscall_ptr
                jmp     loc_8F603
; ---------------------------------------------------------------------------

loc_8FE26:                              ; CODE XREF: sub_8CB70+2B65↑j
                mov     edi, 0CAh       ; sysno
                mov     rsi, r14
                mov     edx, 81h
                mov     ecx, 1
                xor     eax, eax
                call    cs:syscall_ptr
                mov     qword ptr [rsp+0C58h+var_968], r13
                mov     rax, [rbp+200h]
                test    rax, rax
                jnz     loc_8F6EF
                jmp     loc_8F714
; ---------------------------------------------------------------------------

loc_8FE5D:                              ; CODE XREF: sub_8CB70+26D6↑j
                call    sub_4FBB0
                test    al, al
                jnz     loc_8F24C
                mov     byte ptr [r12+4], 1
                jmp     loc_8F24C
; ---------------------------------------------------------------------------

loc_8FE75:                              ; CODE XREF: sub_8CB70+294C↑j
                call    sub_4FBB0
                test    al, al
                jnz     loc_8F4C2
                mov     byte ptr [r14+4], 1
                jmp     loc_8F4C2
; ---------------------------------------------------------------------------

loc_8FE8C:                              ; CODE XREF: sub_8CB70+99C↑j
                lea     rsi, sub_5BC70
                mov     rdi, r15
                call    sub_FE1FB0
                mov     byte ptr fs:0FFFFFFFFFFFFFF58h, 1
                mov     r8, [rsp+0C58h+var_C58]
                mov     rsi, 7FFFFFFFFFFFFFFFh

loc_8FEB2:                              ; CODE XREF: sub_8CB70+993↑j
                mov     fs:0FFFFFFFFFFFFFF54h, bl
                mov     fs:0FFFFFFFFFFFFFF55h, r14b
                mov     eax, r12d
                and     eax, 3
                cmp     eax, 1
                jnz     short loc_8FF11

loc_8FECE:                              ; CODE XREF: sub_8CB70+9B1↑j
                lea     r14, [r12-1]
                mov     r15, [r12-1]
                mov     rbx, [r12+7]
                mov     rax, [rbx]
                test    rax, rax
                jz      short loc_8FEEA
                mov     rdi, r15
                call    rax

loc_8FEEA:                              ; CODE XREF: sub_8CB70+3373↑j
                cmp     qword ptr [rbx+8], 0
                jz      short loc_8FEFA
                mov     rdi, r15        ; ptr
                call    cs:free_ptr

loc_8FEFA:                              ; CODE XREF: sub_8CB70+337F↑j
                mov     rdi, r14        ; ptr
                call    cs:free_ptr
                mov     r8, [rsp+0C58h+var_C58]
                mov     rsi, 7FFFFFFFFFFFFFFFh

loc_8FF11:                              ; CODE XREF: sub_8CB70+9AB↑j
                                        ; sub_8CB70+335C↑j
                mov     rdx, [r8+128h]
                mov     rax, [r8+130h]

loc_8FF1F:                              ; CODE XREF: sub_8CB70+2C81↑j
                mov     [r8+148h], rdx
                mov     [r8+150h], rax
                lea     rdi, [r8+1B0h]
                mov     byte ptr [r8+1B0h], 0

loc_8FF3C:                              ; CODE XREF: sub_8CB70+1B8↑j
                mov     [rsp+0C58h+var_C40], rdi
                mov     r12, [rdx+10h]
                sub     r12, 0FFFFFFFFFFFFFF80h
                mov     [r8+158h], r12
                mov     [r8+160h], rax
                lea     rcx, [r8+1A8h]
                mov     [rsp+0C58h+var_BE8], rcx
                mov     byte ptr [r8+1A8h], 0

loc_8FF6B:                              ; CODE XREF: sub_8CB70+1CB↑j
                mov     [r8+168h], r12
                pxor    xmm0, xmm0
                movdqu  xmmword ptr [r8+170h], xmm0
                mov     qword ptr [r8+180h], 0
                mov     [r8+190h], rax
                mov     byte ptr [r8+198h], 0
                mov     byte ptr [r8+1A0h], 0
                jmp     loc_8CD94
; ---------------------------------------------------------------------------

loc_8FFA6:                              ; CODE XREF: sub_8CB70+2A10↑j
                mov     qword ptr [rsp+0C58h+var_968], 0
                add     r12, 8
                lea     rsi, [rsp+0C58h+var_B98]
                lea     rdx, [rsp+0C58h+var_968]
                mov     rdi, r12
                call    sub_46BFC
; ---------------------------------------------------------------------------

loc_8FFCE:                              ; CODE XREF: sub_8CB70+2AEC↑j
                mov     qword ptr [rsp+0C58h+var_968], 0
                add     r14, 8
                lea     rsi, [rsp+0C58h+var_B98]
                lea     rdx, [rsp+0C58h+var_968]
                mov     rdi, r14
                call    sub_46BFC
; ---------------------------------------------------------------------------

loc_8FFF6:                              ; CODE XREF: sub_8CB70+2A7E↑j
                call    sub_4FBB0
                test    al, al
                jnz     loc_8F5F4
                mov     byte ptr [r12+4], 1
                jmp     loc_8F5F4
; ---------------------------------------------------------------------------

loc_9000E:                              ; CODE XREF: sub_8CB70+2B57↑j
                call    sub_4FBB0
                test    al, al
                jnz     loc_8F6CD
                mov     byte ptr [r14+4], 1
                jmp     loc_8F6CD
; ---------------------------------------------------------------------------

loc_90025:                              ; CODE XREF: sub_8CB70+11E8↑j
                mov     qword ptr [rsp+0C58h+addr_len], 0
                lea     rsi, [rsp+0C58h+dest]
                lea     rdx, [rsp+0C58h+addr_len]
                call    sub_5515C
; ---------------------------------------------------------------------------

loc_90046:                              ; CODE XREF: sub_8CB70+31A1↑j
                mov     rdi, rsi
                call    sub_4FAB0
                mov     rsi, qword ptr [rsp+0C58h+var_C28]
                jmp     loc_8FD17
; ---------------------------------------------------------------------------

loc_90058:                              ; CODE XREF: sub_8CB70+31BE↑j
                call    sub_4FBB0
                mov     rsi, qword ptr [rsp+0C58h+var_C28]
                mov     rdx, 7FFFFFFFFFFFFFFFh
                mov     r13d, eax
                xor     r13b, 1
                movzx   eax, byte ptr [r15+0Ch]
                mov     rcx, [rbx]
                test    rcx, rcx
                jnz     loc_8FD45

loc_90084:                              ; CODE XREF: sub_8CB70+31CF↑j
                cmp     [r15+28h], rbx
                jnz     short loc_900BF
                mov     rax, [r12+88h]
                mov     [r15+28h], rax
                test    rax, rax
                jnz     loc_8FD5A

loc_9009F:                              ; CODE XREF: sub_8CB70+31E4↑j
                cmp     [r15+30h], rbx
                jnz     short loc_900BF
                mov     rax, [rbx]
                mov     [r15+30h], rax
                pxor    xmm0, xmm0
                movdqu  xmmword ptr [rbx], xmm0
                lock dec qword ptr [r12]
                jz      loc_8FD73

loc_900BF:                              ; CODE XREF: sub_8CB70+31FD↑j
                                        ; sub_8CB70+321A↑j ...
                test    r13b, r13b
                jnz     short loc_900D4
                mov     rax, cs:qword_210E9B20
                test    rax, rdx
                jnz     loc_90180

loc_900D4:                              ; CODE XREF: sub_8CB70+3552↑j
                                        ; sub_8CB70+361C↓j ...
                xor     eax, eax
                xchg    eax, [rsi]
                cmp     eax, 2
                mov     rbx, [rsp+0C58h+var_BF0]
                jz      short loc_90159
                lock dec qword ptr [r12]
                jnz     short loc_900F1

loc_900E9:                              ; CODE XREF: sub_8CB70+3605↓j
                mov     rdi, r12        ; ptr
                call    sub_FEE4D0

loc_900F1:                              ; CODE XREF: sub_8CB70+3577↑j
                                        ; sub_8CB70+360B↓j
                mov     r12, r14

loc_900F4:                              ; CODE XREF: sub_8CB70+2F3F↑j
                                        ; sub_8CB70+2F5C↑j
                lock dec qword ptr [rbx]
                setz    al
                test    byte ptr [rsp+0C58h+var_C50], 1
                jz      short loc_90110
                test    al, al
                jz      short loc_9011C
                mov     rdi, rbx        ; ptr
                call    sub_FEDCC0
                jmp     short loc_9011C
; ---------------------------------------------------------------------------

loc_90110:                              ; CODE XREF: sub_8CB70+3590↑j
                test    al, al
                jz      short loc_9011C
                mov     rdi, rbx        ; ptr
                call    sub_FEDB50

loc_9011C:                              ; CODE XREF: sub_8CB70+3594↑j
                                        ; sub_8CB70+359E↑j ...
                mov     edi, ebp        ; fd
                call    cs:close_ptr
                mov     r13d, 2
                mov     rcx, [rsp+0C58h+var_C58]
                mov     rdi, [rsp+0C58h+var_B58]
                movzx   r8d, [rsp+0C58h+var_C2A]
                mov     r9d, [rsp+0C58h+var_BCC]
                mov     r10d, [rsp+0C58h+var_BD0]
                mov     r11d, [rsp+0C58h+var_BD4]
                jmp     loc_8D629
; ---------------------------------------------------------------------------

loc_90159:                              ; CODE XREF: sub_8CB70+3570↑j
                mov     edi, 0CAh       ; sysno
                mov     edx, 81h
                mov     ecx, 1
                xor     eax, eax
                call    cs:syscall_ptr
                lock dec qword ptr [r12]
                jz      loc_900E9
                jmp     loc_900F1
; ---------------------------------------------------------------------------

loc_90180:                              ; CODE XREF: sub_8CB70+355E↑j
                call    sub_4FBB0
                mov     rsi, qword ptr [rsp+0C58h+var_C28]
                test    al, al
                jnz     loc_900D4
                mov     rax, [rsp+0C58h+var_C38]
                mov     byte ptr [rax], 1
                jmp     loc_900D4
; ---------------------------------------------------------------------------

loc_9019F:                              ; CODE XREF: sub_8CB70+3F↑j
                                        ; sub_8CB70+C3↑j ...
                ud2                     ; jumptable 000000000008CBAF cases 1,2
                                        ; jumptable 000000000008CC33 case 2
                                        ; jumptable 000000000008CCAA case 2
; ---------------------------------------------------------------------------

loc_901A1:                              ; CODE XREF: sub_8CB70+145D↑j
                mov     byte ptr [rsp+0C58h+var_B98], al
                lea     rax, [rsp+0C58h+var_B98]
                mov     qword ptr [rsp+0C58h+dest], rax
                lea     rax, sub_FFECD0
                mov     qword ptr [rsp+0C58h+dest+8], rax
                lea     rax, off_210E8160 ; "timer error: "
                mov     qword ptr [rsp+0C58h+addr_len], rax
                mov     [rsp+0C58h+var_AE8], 1
                mov     [rsp+0C58h+var_AD0], 0
                lea     rax, [rsp+0C58h+dest]
                mov     [rsp+0C58h+var_AE0], rax
                mov     [rsp+0C58h+var_AD8], 1
                lea     rsi, off_210E8170 ; "/home/aothuatgiadp/.cargo/registry/src/"...
                lea     rdi, [rsp+0C58h+addr_len]
                call    sub_4A5F0
; ---------------------------------------------------------------------------

loc_9021E:                              ; CODE XREF: sub_8CB70+24EB↑j
                movzx   eax, [rsp+0C58h+var_4C8]
                cmp     eax, 3
                jz      short loc_90283
                test    eax, eax
                jnz     loc_902B8
                lea     rdi, [rsp+0C58h+var_7E8]
                call    sub_67390
                mov     rax, [rsp+0C58h+var_7C8]
                lock dec qword ptr [rax]
                jnz     short loc_902B8
                mov     rdi, [rsp+0C58h+var_7C8] ; ptr
                call    sub_B40E0
                jmp     short loc_902B8
; ---------------------------------------------------------------------------

loc_9025D:                              ; CODE XREF: sub_8CB70+2E6C↑j
                mov     fs:0FFFFFFFFFFFFFF10h, rax
                xor     eax, eax
                mov     byte ptr [rsp+0C58h+addr.sa_family], al
                lea     rsi, off_210E7070 ; "/home/aothuatgiadp/.cargo/registry/src/"...
                lea     rdi, [rsp+0C58h+addr]
                call    sub_558F0
; ---------------------------------------------------------------------------

loc_90283:                              ; CODE XREF: sub_8CB70+36B9↑j
                lea     rdi, [rsp+0C58h+var_760]
                call    sub_64F20
                mov     rax, [rsp+0C58h+ptr]
                test    rax, rax
                jz      short loc_902B8
                lock dec qword ptr [rax]
                jnz     short loc_902B8
                mov     rdi, [rsp+0C58h+ptr] ; ptr
                mov     rsi, [rsp+0C58h+var_780]
                call    sub_6D5C0

loc_902B8:                              ; CODE XREF: sub_8CB70+36BD↑j
                                        ; sub_8CB70+36DC↑j ...
                dec     qword ptr fs:0FFFFFFFFFFFFFF10h
                xor     ebx, ebx
                mov     byte ptr [rsp+0C58h+addr.sa_family], bl
                lea     rdi, [rsp+0C58h+addr]
                call    sub_46D20
; ---------------------------------------------------------------------------

loc_902D7:                              ; CODE XREF: sub_8CB70+11A3↑j
                lea     rdx, off_210E7B18 ; "/home/aothuatgiadp/.cargo/registry/src/"...
                mov     esi, 6
                call    sub_4A595
; } // starts at 8CB70
; END OF FUNCTION CHUNK FOR sub_8CB70
; ---------------------------------------------------------------------------
                align 10h

; =============== S U B R O U T I N E =======================================


sub_902F0       proc near               ; CODE XREF: sub_797F0+20E↑p
                                        ; sub_79DC0+20E↑p

var_BB8         = qword ptr -0BB8h
var_BB0         = qword ptr -0BB0h
var_BA8         = qword ptr -0BA8h
var_B99         = byte ptr -0B99h
var_B98         = qword ptr -0B98h
var_B90         = qword ptr -0B90h
var_B88         = qword ptr -0B88h
src             = qword ptr -0B80h
var_B78         = qword ptr -0B78h
var_B70         = qword ptr -0B70h
var_B68         = xmmword ptr -0B68h
var_B50         = qword ptr -0B50h
var_B48         = qword ptr -0B48h
var_B40         = qword ptr -0B40h
var_B38         = qword ptr -0B38h
var_B2C         = dword ptr -0B2Ch
var_B28         = qword ptr -0B28h
var_B18         = xmmword ptr -0B18h
var_B08         = qword ptr -0B08h
var_AF8         = qword ptr -0AF8h
var_AF0         = qword ptr -0AF0h
var_AE8         = qword ptr -0AE8h
var_AE0         = qword ptr -0AE0h
var_AD8         = xmmword ptr -0AD8h
var_AC8         = xmmword ptr -0AC8h
var_AB8         = qword ptr -0AB8h
var_AB0         = byte ptr -0AB0h
var_AA8         = xmmword ptr -0AA8h
var_A98         = qword ptr -0A98h
var_A90         = qword ptr -0A90h
var_A88         = qword ptr -0A88h
var_A80         = qword ptr -0A80h
var_A78         = qword ptr -0A78h
var_A70         = qword ptr -0A70h
var_A68         = qword ptr -0A68h
var_A60         = qword ptr -0A60h
var_A58         = xmmword ptr -0A58h
var_A48         = xmmword ptr -0A48h
var_A38         = xmmword ptr -0A38h
var_A28         = xmmword ptr -0A28h
var_A18         = xmmword ptr -0A18h
var_A08         = qword ptr -0A08h
var_A00         = qword ptr -0A00h
var_9F8         = xmmword ptr -9F8h
var_998         = xmmword ptr -998h
var_988         = xmmword ptr -988h
var_978         = xmmword ptr -978h
var_968         = xmmword ptr -968h
var_958         = xmmword ptr -958h
var_948         = xmmword ptr -948h
var_8E0         = qword ptr -8E0h
var_8D8         = qword ptr -8D8h
var_8D0         = qword ptr -8D0h
var_8C8         = qword ptr -8C8h
var_8B8         = qword ptr -8B8h
var_8B0         = qword ptr -8B0h
var_8A8         = qword ptr -8A8h
var_8A0         = qword ptr -8A0h
var_898         = qword ptr -898h
var_890         = qword ptr -890h
var_888         = qword ptr -888h
var_880         = qword ptr -880h
dest            = xmmword ptr -878h
n               = qword ptr -868h
var_858         = xmmword ptr -858h
var_840         = qword ptr -840h
var_838         = qword ptr -838h
var_830         = qword ptr -830h
var_828         = qword ptr -828h
var_820         = word ptr -820h
var_818         = qword ptr -818h
var_810         = word ptr -810h
var_80E         = byte ptr -80Eh
var_7A8         = qword ptr -7A8h
var_7A0         = qword ptr -7A0h
var_798         = qword ptr -798h
var_790         = qword ptr -790h
var_788         = qword ptr -788h
var_780         = qword ptr -780h
var_628         = byte ptr -628h
var_608         = byte ptr -608h
var_600         = xmmword ptr -600h
ptr             = qword ptr -5F0h
var_5D8         = xmmword ptr -5D8h
var_5C8         = xmmword ptr -5C8h
var_5B8         = xmmword ptr -5B8h
var_5A8         = xmmword ptr -5A8h
var_598         = xmmword ptr -598h
var_588         = xmmword ptr -588h
var_578         = xmmword ptr -578h
var_568         = xmmword ptr -568h
var_558         = xmmword ptr -558h
var_548         = xmmword ptr -548h
var_538         = qword ptr -538h
var_530         = qword ptr -530h
var_528         = qword ptr -528h
var_520         = word ptr -520h
var_4A8         = qword ptr -4A8h
var_4A0         = qword ptr -4A0h
var_498         = qword ptr -498h
var_490         = byte ptr -490h
var_48F         = byte ptr -48Fh
var_48E         = byte ptr -48Eh
var_328         = xmmword ptr -328h
var_318         = xmmword ptr -318h
var_308         = xmmword ptr -308h
var_2F8         = qword ptr -2F8h
var_2E8         = qword ptr -2E8h
var_2E0         = qword ptr -2E0h
var_2D8         = qword ptr -2D8h
var_2D0         = qword ptr -2D0h
var_288         = xmmword ptr -288h
var_278         = xmmword ptr -278h
var_268         = xmmword ptr -268h
var_258         = xmmword ptr -258h
var_248         = qword ptr -248h
var_238         = qword ptr -238h
var_230         = qword ptr -230h
var_210         = qword ptr -210h
var_1F8         = qword ptr -1F8h
var_1F0         = byte ptr -1F0h
var_1E8         = qword ptr -1E8h
var_1E0         = qword ptr -1E0h
var_1D8         = byte ptr -1D8h
var_1D0         = qword ptr -1D0h
var_1C8         = byte ptr -1C8h
var_1B8         = qword ptr -1B8h
var_1B0         = word ptr -1B0h
var_1A8         = qword ptr -1A8h
var_1A0         = qword ptr -1A0h
var_198         = qword ptr -198h
var_188         = qword ptr -188h
var_128         = qword ptr -128h
var_C0          = qword ptr -0C0h
var_A0          = qword ptr -0A0h
var_98          = dword ptr -98h
var_90          = byte ptr -90h
var_60          = qword ptr -60h
var_58          = qword ptr -58h
var_50          = byte ptr -50h
var_47          = byte ptr -47h
var_46          = byte ptr -46h
var_45          = byte ptr -45h
var_41          = word ptr -41h

; __unwind {
                push    rbp
                push    r15
                push    r14
                push    r13
                push    r12
                push    rbx
                sub     rsp, 0B88h
                mov     [rsp+0BB8h+var_BA8], rsi
                mov     rbx, rdi
                movzx   eax, byte ptr [rdi+320h]
                test    eax, eax
                jz      short loc_90329
                cmp     eax, 3
                jz      loc_9040D
                lea     rdi, off_210C8948 ; "/home/aothuatgiadp/.cargo/registry/src/"...
                call    sub_4AE10
; ---------------------------------------------------------------------------

loc_90329:                              ; CODE XREF: sub_902F0+22↑j
                lea     rax, [rbx+28h]
                mov     qword ptr [rbx+28h], 0
                mov     qword ptr [rbx+38h], 0
                mov     qword ptr [rbx+40h], 1Eh
                mov     dword ptr [rbx+48h], 0
                mov     qword ptr [rbx+50h], 0
                mov     qword ptr [rbx+60h], 0
                mov     qword ptr [rbx+70h], 0
                mov     dword ptr [rbx+78h], 1
                mov     word ptr [rbx+7Ch], 201h
                mov     byte ptr [rbx+80h], 2
                movups  xmm0, xmmword ptr [rbx]
                movups  xmm1, xmmword ptr [rbx+10h]
                movaps  [rsp+0BB8h+var_318], xmm1
                movaps  [rsp+0BB8h+var_328], xmm0
                mov     rcx, [rbx+20h]
                mov     qword ptr [rbx+88h], 3
                movdqa  xmm0, [rsp+0BB8h+var_328]
                movdqa  xmm1, [rsp+0BB8h+var_318]
                movdqa  xmm2, [rsp+0BB8h+var_308]
                movdqu  xmmword ptr [rbx+90h], xmm0
                movdqu  xmmword ptr [rbx+0A0h], xmm1
                movdqu  xmmword ptr [rbx+0B0h], xmm2
                mov     rdx, [rsp+0BB8h+var_2F8]
                mov     [rbx+0C0h], rdx
                mov     qword ptr [rbx+0C8h], 0
                mov     word ptr [rbx+0D0h], 1
                mov     qword ptr [rbx+0D8h], 2
                mov     [rbx+0E0h], rax
                mov     [rbx+138h], rcx

loc_9040D:                              ; CODE XREF: sub_902F0+27↑j
                lea     r13, [rbx+88h]
                lea     rax, [rbx+90h]
                mov     [rsp+0BB8h+var_AF0], rax
                lea     rax, [rbx+0D8h]
                mov     [rsp+0BB8h+var_B90], rax
                lea     rax, [rbx+0B0h]
                mov     [rsp+0BB8h+src], rax
                lea     rax, [rbx+98h]
                mov     qword ptr [rsp+0BB8h+var_B68], rax
                lea     rax, [rbx+2F9h]
                mov     [rsp+0BB8h+var_AE8], rax
                lea     rdx, [rbx+319h]
                mov     esi, 1
                lea     r12, aPriHttp20Sm ; "PRI * HTTP/2.0\r\n\r\nSM\r\n\r\n"
                mov     [rsp+0BB8h+var_BB8], rbx
                mov     [rsp+0BB8h+var_B98], r13

loc_90472:                              ; CODE XREF: sub_902F0+85D↓j
                mov     rax, [r13+0]
                lea     rcx, [rax-3]
                cmp     rcx, 3
                cmovnb  rcx, rsi
                test    rcx, rcx
                jnz     loc_90BCA
                cmp     byte ptr [rbx+0D1h], 0
                mov     r13, [rsp+0BB8h+var_BA8]
                jnz     loc_93AFB
                mov     [rsp+0BB8h+var_B38], rdx
                mov     r15, [rbx+0C8h]
                nop     dword ptr [rax+00h]

loc_904B0:                              ; CODE XREF: sub_902F0+293↓j
                cmp     r15, 19h
                jnb     loc_9436E
                mov     rax, [rsp+0BB8h+var_AF0]
                mov     rbp, [rax]
                cmp     r15, 18h
                jz      loc_9058B
                cmp     rbp, 2
                jz      loc_94382
                mov     eax, 18h
                sub     rax, r15
                mov     rcx, [rsp+0BB8h+src]
                lea     rbp, [rcx+r15]
                mov     qword ptr [rsp+0BB8h+dest], rbp
                mov     qword ptr [rsp+0BB8h+dest+8], rax
                lea     rax, [rsp+0BB8h+n]
                pxor    xmm0, xmm0
                movdqu  xmmword ptr [rax], xmm0
                mov     rsi, [r13+0]
                mov     rdi, [rsp+0BB8h+var_AF0]
                lea     rdx, [rsp+0BB8h+dest]
                call    sub_FF2D10
                test    al, 1
                jnz     loc_905C8
                test    rdx, rdx
                jnz     loc_905C8
                mov     rsi, qword ptr [rsp+0BB8h+dest+8]
                mov     rdx, [rsp+0BB8h+n] ; n
                cmp     rdx, rsi
                ja      loc_9438E
                mov     r14, r15
                add     r14, rdx
                jb      loc_943A0
                cmp     r14, 19h
                jnb     loc_93EF1
                mov     [rbx+0C8h], r14
                test    rdx, rdx
                jz      short loc_905E0
                add     r15, r12
                mov     rdi, rbp        ; s1
                mov     rsi, r15        ; s2
                call    cs:bcmp_ptr
                mov     r15, r14
                test    eax, eax
                jz      loc_904B0
                jmp     short loc_905E3
; ---------------------------------------------------------------------------

loc_9058B:                              ; CODE XREF: sub_902F0+1D9↑j
                mov     rax, [rsp+0BB8h+var_AF0]
                mov     qword ptr [rax], 2
                cmp     rbp, 2
                jz      loc_944BA
                mov     rcx, qword ptr [rsp+0BB8h+var_B68]
                mov     rax, [rcx+10h]
                mov     qword ptr [rsp+0BB8h+var_568], rax
                movups  xmm0, xmmword ptr [rcx]
                movaps  [rsp+0BB8h+var_578], xmm0
                mov     r14d, 18h
                jmp     short loc_90627
; ---------------------------------------------------------------------------

loc_905C8:                              ; CODE XREF: sub_902F0+235↑j
                                        ; sub_902F0+23E↑j
                test    al, 1
                jnz     loc_93ADD
                test    rdx, rdx
                jnz     loc_93ED5
                mov     [rbx+0C8h], r15

loc_905E0:                              ; CODE XREF: sub_902F0+27D↑j
                mov     r14, r15

loc_905E3:                              ; CODE XREF: sub_902F0+299↑j
                mov     byte ptr [rbx+0D0h], 0
                mov     rbp, [rbx+90h]
                mov     qword ptr [rbx+90h], 2
                cmp     rbp, 2
                jz      loc_944BA
                mov     rcx, qword ptr [rsp+0BB8h+var_B68]
                mov     rax, [rcx+10h]
                mov     qword ptr [rsp+0BB8h+var_568], rax
                movups  xmm0, xmmword ptr [rcx]
                movaps  [rsp+0BB8h+var_578], xmm0
                test    r14, r14
                jz      short loc_9067D

loc_90627:                              ; CODE XREF: sub_902F0+2D6↑j
                mov     r13, 7FFFFFFFFFFFFFFDh
                mov     rdi, r14        ; size
                call    cs:malloc_ptr
                test    rax, rax
                jz      loc_948D9
                mov     r15, rax
                mov     rdi, rax        ; dest
                mov     rsi, [rsp+0BB8h+src] ; src
                mov     rdx, r14        ; n
                call    cs:memcpy_ptr
                movzx   eax, byte ptr [rbx+0D0h]
                mov     rcx, r15
                test    r15b, 1
                jnz     short loc_90674
                or      rcx, 1
                lea     rdx, off_210CC730
                jmp     short loc_906A0
; ---------------------------------------------------------------------------

loc_90674:                              ; CODE XREF: sub_902F0+375↑j
                lea     rdx, off_210CC758
                jmp     short loc_906A0
; ---------------------------------------------------------------------------

loc_9067D:                              ; CODE XREF: sub_902F0+335↑j
                movzx   eax, byte ptr [rbx+0D0h]
                mov     r15d, 1
                xor     r14d, r14d
                xor     ecx, ecx
                lea     rdx, off_210C9908
                mov     r13, 7FFFFFFFFFFFFFFDh

loc_906A0:                              ; CODE XREF: sub_902F0+382↑j
                                        ; sub_902F0+38B↑j
                mov     rsi, qword ptr [rsp+0BB8h+var_568]
                lea     r8, [rsp+0BB8h+var_998+8]
                mov     [r8+10h], rsi
                movaps  xmm0, [rsp+0BB8h+var_578]
                movups  xmmword ptr [r8], xmm0
                cmp     rbp, 3
                jz      loc_93ADD
                mov     rsi, [r8+10h]
                lea     rdi, [rsp+0BB8h+var_578+8]
                mov     [rdi+10h], rsi
                movups  xmm0, xmmword ptr [r8]
                movups  xmmword ptr [rdi], xmm0
                mov     qword ptr [rsp+0BB8h+var_558], rdx
                mov     qword ptr [rsp+0BB8h+var_558+8], r15
                mov     qword ptr [rsp+0BB8h+var_548], r14
                mov     qword ptr [rsp+0BB8h+var_548+8], rcx
                mov     qword ptr [rsp+0BB8h+var_578], rbp
                mov     rbp, [rbx+138h]
                mov     qword ptr [rbx+138h], 0
                test    rbp, rbp
                jz      loc_944C6
                test    al, al
                jnz     loc_93B3A
                mov     r15, [rsp+0BB8h+var_B90]
                cmp     dword ptr [r15], 2
                jnz     short loc_9073E
                mov     r15, [rbx+0E0h]

loc_9073E:                              ; CODE XREF: sub_902F0+445↑j
                mov     edi, 2000h      ; size
                call    cs:malloc_ptr
                test    rax, rax
                jz      loc_948CA
                lea     rdx, [rsp+0BB8h+var_1C8]
                pxor    xmm4, xmm4
                movdqu  xmmword ptr [rdx], xmm4
                movdqu  xmmword ptr [rdx-60h], xmm4
                mov     qword ptr [rdx-50h], 0
                movdqu  xmmword ptr [rdx-40h], xmm4
                movdqu  xmm0, [rsp+0BB8h+var_578]
                movdqu  xmm1, [rsp+0BB8h+var_568]
                movdqu  xmm2, [rsp+0BB8h+var_558]
                movdqu  xmm3, [rsp+0BB8h+var_548]
                movdqa  [rsp+0BB8h+var_258], xmm3
                movdqa  [rsp+0BB8h+var_268], xmm2
                movdqa  [rsp+0BB8h+var_278], xmm1
                movdqa  [rsp+0BB8h+var_288], xmm0
                mov     [rsp+0BB8h+var_248], 0
                mov     [rsp+0BB8h+var_238], 2000h
                mov     [rsp+0BB8h+var_230], rax
                mov     [rsp+0BB8h+var_210], 8
                mov     [rsp+0BB8h+var_1F8], 66000h
                mov     [rsp+0BB8h+var_1F0], 1
                mov     [rsp+0BB8h+var_1E8], 2000h
                mov     [rsp+0BB8h+var_1E0], 66000h
                mov     [rsp+0BB8h+var_1D8], 0
                mov     [rsp+0BB8h+var_1D0], 1
                mov     [rsp+0BB8h+var_1B8], 1
                mov     [rsp+0BB8h+var_1B0], 0
                mov     [rsp+0BB8h+var_1A8], 0
                mov     [rsp+0BB8h+var_198], 0
                mov     [rsp+0BB8h+var_188], 3
                mov     [rsp+0BB8h+var_128], 0
                lea     rax, [r13+6]
                mov     [rsp+0BB8h+var_C0], rax
                mov     [rsp+0BB8h+var_98], 3B9ACA00h
                mov     [rsp+0BB8h+var_90], 0Ch
                mov     [rsp+0BB8h+var_60], 0
                movdqu  xmmword ptr [rdx+150h], xmm4
                mov     byte ptr [rdx+180h], 0
                mov     qword ptr [rdx+178h], 0
                mov     [rsp+0BB8h+var_47], 1
                mov     byte ptr [rdx+186h], 0
                mov     dword ptr [rdx+182h], 0
                mov     [rsp+0BB8h+var_41], 201h
                mov     eax, [r15+48h]
                mov     ecx, [r15+4Bh]
                mov     [rdx+17Ch], ecx
                mov     [rdx+179h], eax
                mov     rax, [r15+38h]
                test    rax, rax
                mov     r12, cs:malloc_ptr
                jz      short loc_90908
                lock inc qword ptr [rax]
                jle     loc_948A1
                mov     rcx, [r15+40h]

loc_90908:                              ; CODE XREF: sub_902F0+608↑j
                mov     [rsp+0BB8h+var_60], rax
                mov     [rsp+0BB8h+var_58], rcx
                cmp     byte ptr [r15+50h], 1
                jnz     short loc_90950
                cmp     byte ptr [r15+4Fh], 0
                jz      short loc_9095F

loc_90926:                              ; CODE XREF: sub_902F0+66D↓j
                mov     [rsp+0BB8h+var_50], 1
                cmp     byte ptr [r15+51h], 0
                jnz     short loc_90966

loc_90935:                              ; CODE XREF: sub_902F0+674↓j
                cmp     byte ptr [r15+52h], 0
                jz      short loc_90975

loc_9093C:                              ; CODE XREF: sub_902F0+683↓j
                mov     [rsp+0BB8h+var_46], 1
                mov     rax, [r15]
                test    rax, rax
                jnz     short loc_9097D
                jmp     short loc_90991
; ---------------------------------------------------------------------------
                align 10h

loc_90950:                              ; CODE XREF: sub_902F0+62D↑j
                mov     byte ptr [rsp+0BB8h+var_41], 2
                cmp     byte ptr [r15+4Fh], 0
                jnz     short loc_90926

loc_9095F:                              ; CODE XREF: sub_902F0+634↑j
                cmp     byte ptr [r15+51h], 0
                jz      short loc_90935

loc_90966:                              ; CODE XREF: sub_902F0+643↑j
                mov     [rsp+0BB8h+var_45], 1
                cmp     byte ptr [r15+52h], 0
                jnz     short loc_9093C

loc_90975:                              ; CODE XREF: sub_902F0+64A↑j
                mov     rax, [r15]
                test    rax, rax
                jz      short loc_90991

loc_9097D:                              ; CODE XREF: sub_902F0+65A↑j
                mov     rcx, [r15+8]
                mov     [rsp+0BB8h+var_1A8], rax
                mov     [rsp+0BB8h+var_1A0], rcx

loc_90991:                              ; CODE XREF: sub_902F0+65C↑j
                                        ; sub_902F0+68B↑j
                mov     rcx, [r15+38h]
                lea     rax, aHeaderReadTime ; "header_read_timeout"
                mov     qword ptr [rsp+0BB8h+var_A58], rax
                mov     qword ptr [rsp+0BB8h+var_A58+8], 13h
                mov     eax, [r15+20h]
                cmp     dword ptr [r15+10h], 1
                jnz     short loc_909D0
                cmp     eax, 3B9ACA00h
                jz      short loc_909F5
                test    rcx, rcx
                jnz     short loc_909E2
                jmp     loc_94700
; ---------------------------------------------------------------------------
                align 10h

loc_909D0:                              ; CODE XREF: sub_902F0+6C9↑j
                cmp     eax, 3B9ACA00h
                setz    dl
                test    rcx, rcx
                setz    cl
                or      cl, dl
                jnz     short loc_909F5

loc_909E2:                              ; CODE XREF: sub_902F0+6D5↑j
                mov     rcx, [r15+18h]
                mov     [rsp+0BB8h+var_A0], rcx
                mov     [rsp+0BB8h+var_98], eax

loc_909F5:                              ; CODE XREF: sub_902F0+6D0↑j
                                        ; sub_902F0+6F0↑j
                movzx   eax, byte ptr [r15+55h]
                cmp     al, 2
                jnz     loc_90B60
                movzx   eax, byte ptr [r15+53h]
                mov     byte ptr [rsp+0BB8h+var_1B0], al
                test    al, al
                jz      loc_90B7B

loc_90A16:                              ; CODE XREF: sub_902F0+885↓j
                mov     [rsp+0BB8h+var_1F0], 0
                test    byte ptr [r15+28h], 1
                jnz     loc_90B86

loc_90A29:                              ; CODE XREF: sub_902F0+890↓j
                cmp     byte ptr [r15+54h], 0
                jnz     short loc_90A38

loc_90A30:                              ; CODE XREF: sub_902F0+8CF↓j
                mov     [rsp+0BB8h+var_47], 0

loc_90A38:                              ; CODE XREF: sub_902F0+73E↑j
                                        ; sub_902F0+8D5↓j
                mov     edi, 128h       ; size
                call    r12 ; malloc
                test    rax, rax
                jz      loc_944D2
                mov     r15, rax
                mov     r14, rbp
                mov     qword ptr [rax], 0Ah
                mov     edi, 10h        ; size
                call    r12 ; malloc
                test    rax, rax
                jz      loc_9446C
                mov     rbp, rax
                mov     qword ptr [rax], 0
                mov     edx, 250h       ; n
                lea     rdi, [rsp+0BB8h+dest] ; dest
                lea     rsi, [rsp+0BB8h+var_288] ; src
                mov     r12, cs:memcpy_ptr
                call    r12 ; memcpy
                mov     eax, dword ptr [rsp+0BB8h+var_2E8]
                mov     ecx, dword ptr [rsp+0BB8h+var_2E8+3]
                mov     dword ptr [rsp+0BB8h+var_998+3], ecx
                mov     [rsp+220h], eax
                mov     eax, dword ptr [rsp+0BB8h+var_5D8]
                mov     ecx, dword ptr [rsp+0BB8h+var_5D8+3]
                mov     dword ptr [rsp+0BB8h+var_A58+3], ecx
                mov     dword ptr [rsp+0BB8h+var_A58], eax
                mov     r13, [rsp+0BB8h+var_B98]
                mov     rdi, r13
                call    sub_64F20
                mov     edx, 270h       ; n
                mov     rdi, r13        ; dest
                lea     rsi, [rsp+0BB8h+dest] ; src
                call    r12 ; memcpy
                lea     r12, aPriHttp20Sm ; "PRI * HTTP/2.0\r\n\r\nSM\r\n\r\n"
                mov     byte ptr [rbx+2F8h], 3
                mov     eax, [rsp+220h]
                mov     ecx, dword ptr [rsp+0BB8h+var_998+3]
                mov     rdx, [rsp+0BB8h+var_AE8]
                mov     [rdx+3], ecx
                mov     [rdx], eax
                mov     [rbx+300h], r15
                mov     [rbx+308h], r14
                mov     [rbx+310h], rbp
                mov     byte ptr [rbx+318h], 0
                mov     eax, dword ptr [rsp+0BB8h+var_A58]
                mov     ecx, dword ptr [rsp+0BB8h+var_A58+3]
                mov     rdx, [rsp+0BB8h+var_B38]
                mov     [rdx], eax
                mov     [rdx+3], ecx
                mov     esi, 1
                jmp     loc_90472
; ---------------------------------------------------------------------------
                align 20h

loc_90B60:                              ; CODE XREF: sub_902F0+70C↑j
                mov     [rsp+0BB8h+var_1F0], al
                movzx   eax, byte ptr [r15+53h]
                mov     byte ptr [rsp+0BB8h+var_1B0], al
                test    al, al
                jnz     loc_90A16

loc_90B7B:                              ; CODE XREF: sub_902F0+720↑j
                test    byte ptr [r15+28h], 1
                jz      loc_90A29

loc_90B86:                              ; CODE XREF: sub_902F0+733↑j
                mov     rax, [r15+30h]
                cmp     rax, 1FFFh
                jbe     loc_94612
                mov     [rsp+0BB8h+var_1E8], 2000h
                mov     [rsp+0BB8h+var_1E0], rax
                mov     [rsp+0BB8h+var_1D8], 0
                mov     [rsp+0BB8h+var_1F8], rax
                cmp     byte ptr [r15+54h], 0
                jz      loc_90A30
                jmp     loc_90A38
; ---------------------------------------------------------------------------

loc_90BCA:                              ; CODE XREF: sub_902F0+195↑j
                cmp     rcx, 1
                mov     r13, [rsp+0BB8h+var_BA8]
                jnz     loc_944A2
                cmp     eax, 2
                jnz     short loc_90C15

loc_90BDE:                              ; CODE XREF: sub_902F0+3C5A↓j
                                        ; sub_902F0+3D98↓j ...
                mov     rdi, [rsp+0BB8h+var_B98]
                call    sub_64F20

loc_90BE8:                              ; CODE XREF: sub_902F0+3DE2↓j
                                        ; sub_902F0+3DF1↓j
                mov     rax, [rbx+60h]
                mov     bpl, 1
                test    rax, rax
                jz      short loc_90C0E
                lock dec qword ptr [rax]
                jnz     short loc_90C0E
                mov     rdi, [rbx+60h]  ; ptr
                mov     rsi, [rbx+68h]
                call    sub_6D5C0
                xor     eax, eax
                jmp     loc_93AE2
; ---------------------------------------------------------------------------

loc_90C0E:                              ; CODE XREF: sub_902F0+902↑j
                                        ; sub_902F0+908↑j
                xor     eax, eax
                jmp     loc_93AE2
; ---------------------------------------------------------------------------

loc_90C15:                              ; CODE XREF: sub_902F0+8EC↑j
                mov     rbx, fs:0
                cmp     byte ptr fs:0FFFFFFFFFFFFFFA0h, 0
                jz      loc_9458C
                cmp     qword ptr fs:0FFFFFFFFFFFFFF60h, 0
                jnz     loc_945B1

loc_90C3D:                              ; CODE XREF: sub_902F0+42BB↓j
                mov     qword ptr fs:0FFFFFFFFFFFFFF60h, 0FFFFFFFFFFFFFFFFh
                xor     edi, edi
                call    sub_FE82F0
                mov     r14, rax
                mov     ebp, edx
                cmp     rax, fs:0FFFFFFFFFFFFFF68h
                jnz     short loc_90C70
                cmp     ebp, fs:0FFFFFFFFFFFFFF70h
                ja      short loc_90C76
                jmp     loc_90DA7
; ---------------------------------------------------------------------------

loc_90C70:                              ; CODE XREF: sub_902F0+96F↑j
                jle     loc_90DA7

loc_90C76:                              ; CODE XREF: sub_902F0+979↑j
                lea     r15, [rbx-0A0h]
                add     r15, 8
                mov     [rsp+220h], r14
                mov     dword ptr [rsp+0BB8h+var_998+8], ebp
                mov     qword ptr [rsp+0BB8h+var_578], 0
                mov     dword ptr [rsp+0BB8h+var_578+8], 0
                lea     rdi, [rsp+0BB8h+dest]
                lea     rsi, [rsp+0BB8h+var_998]
                lea     r12, [rsp+0BB8h+var_578]
                mov     rdx, r12
                call    sub_FE83C0
                mov     r13, qword ptr [rsp+0BB8h+dest]
                mov     ebx, dword ptr [rsp+0BB8h+n]
                mov     qword ptr fs:0FFFFFFFFFFFFFF78h, 0
                mov     rdi, r14
                mov     esi, ebp
                call    sub_D4B80
                mov     qword ptr [rsp+0BB8h+var_A58], rax
                lea     rax, [rsp+0BB8h+var_A58]
                mov     qword ptr [rsp+0BB8h+var_578], rax
                lea     rax, sub_D4F90
                mov     qword ptr [rsp+0BB8h+var_578+8], rax
                lea     rax, asc_1000010 ; "\x01"
                mov     qword ptr [rsp+0BB8h+dest], rax
                mov     qword ptr [rsp+0BB8h+dest+8], 1
                mov     qword ptr [rsp+0BB8h+var_858], 0
                mov     [rsp+0BB8h+n], r12
                mov     [rsp+0BB8h+n+8], 1
                lea     rsi, qword_210CD080
                lea     rdx, [rsp+0BB8h+dest]
                mov     rdi, r15
                call    sub_BCC60
                inc     r14
                jo      loc_946E8
                xor     eax, eax
                test    r13, r13
                cmovnz  ebx, eax
                sub     ebp, ebx
                js      short loc_90D82
                mov     r13, [rsp+0BB8h+var_BA8]
                jmp     short loc_90D96
; ---------------------------------------------------------------------------

loc_90D82:                              ; CODE XREF: sub_902F0+A89↑j
                dec     r14
                mov     r13, [rsp+0BB8h+var_BA8]
                jo      loc_9478E
                add     ebp, 3B9ACA00h

loc_90D96:                              ; CODE XREF: sub_902F0+A90↑j
                mov     fs:0FFFFFFFFFFFFFF68h, r14
                mov     fs:0FFFFFFFFFFFFFF70h, ebp

loc_90DA7:                              ; CODE XREF: sub_902F0+97B↑j
                                        ; sub_902F0:loc_90C70↑j
                inc     qword ptr fs:0FFFFFFFFFFFFFF60h
                mov     rbx, [rsp+0BB8h+var_BB8]
                lea     rax, [rbx+168h]
                mov     [rsp+0BB8h+var_B48], rax
                lea     rax, [rbx+2D8h]
                mov     [rsp+0BB8h+var_B90], rax
                lea     rax, [rbx+210h]
                mov     [rsp+0BB8h+var_A80], rax
                lea     rax, [rbx+249h]
                mov     [rsp+0BB8h+var_B70], rax
                lea     rax, [rbx+2A0h]
                mov     [rsp+0BB8h+var_A78], rax
                lea     rax, [rbx+188h]
                mov     [rsp+0BB8h+var_A60], rax
                lea     rax, [rbx+280h]
                mov     [rsp+0BB8h+var_8A0], rax
                lea     rax, [rbx+2C1h]
                mov     [rsp+0BB8h+var_8A8], rax
                lea     rax, [rbx+140h]
                mov     [rsp+0BB8h+src], rax
                mov     [rsp+0BB8h+var_B2C], 1
                mov     dword ptr [rsp+0BB8h+var_B38], eax
                jmp     short loc_90E59
; ---------------------------------------------------------------------------

loc_90E43:                              ; CODE XREF: sub_902F0+24F0↓j
                                        ; sub_902F0+2511↓j ...
                mov     rdi, r12        ; ptr
                call    cs:free_ptr

loc_90E4C:                              ; CODE XREF: sub_902F0+BFE↓j
                                        ; sub_902F0+19B0↓j ...
                lea     rdi, [rsp+0BB8h+var_B28] ; jumptable 0000000000091CA0 case 5
                call    sub_64B90

loc_90E59:                              ; CODE XREF: sub_902F0+B51↑j
                                        ; sub_902F0+1B57↓j ...
                cmp     byte ptr [rbx+318h], 0
                jnz     loc_91D30
                mov     rax, [rbx+1E8h]
                test    rax, rax
                jz      loc_90F70
                mov     rdx, [rsp+0BB8h+var_B90]
                mov     rcx, [rdx+20h]
                mov     [rsp+0BB8h+var_AB8], rcx
                movdqu  xmm0, xmmword ptr [rdx]
                movdqu  xmm1, xmmword ptr [rdx+10h]
                movdqa  [rsp+0BB8h+var_AC8], xmm1
                movdqa  [rsp+0BB8h+var_AD8], xmm0
                mov     byte ptr [rbx+2F8h], 3
                cmp     byte ptr [rsp+0BB8h+var_AB8], 3
                jz      loc_91BE0
                mov     rcx, [rsp+0BB8h+var_AB8]
                mov     [rsp+0BB8h+var_B08], rcx
                movdqa  xmm0, [rsp+0BB8h+var_AD8]
                movdqa  xmm1, [rsp+0BB8h+var_AC8]
                movdqa  [rsp+0BB8h+var_B18], xmm1
                movdqa  xmmword ptr [rsp+0BB8h+var_B28], xmm0
                cmp     eax, 3
                jnb     loc_90E4C       ; jumptable 0000000000091CA0 case 5
                mov     r12, [rsp+0BB8h+var_B28+8]
                mov     rcx, [r13+0]
                xor     eax, eax
                mov     edx, 1
                lock cmpxchg [r12+28h], rdx
                cmp     rax, 2
                jz      loc_90FDB
                test    rax, rax
                jnz     loc_91050
                mov     rdx, [r12+18h]
                mov     rax, [rcx]
                test    rdx, rdx
                jz      loc_90FE7
                mov     rdi, [rcx+8]
                mov     rcx, [r12+20h]
                xor     rcx, rdi
                xor     rdx, rax
                or      rdx, rcx
                jnz     loc_90FEB
                mov     eax, 1
                xor     ecx, ecx
                lock cmpxchg [r12+28h], rcx
                jnz     loc_9101F
                jmp     loc_91050
; ---------------------------------------------------------------------------
                align 10h

loc_90F70:                              ; CODE XREF: sub_902F0+B80↑j
                mov     rax, [rbx+300h]
                cmp     dword ptr [rax], 0Ah
                jnz     loc_91D30
                cmp     byte ptr [rbx+2C8h], 0
                jnz     loc_912A0
                mov     ebp, [rbx+278h]
                cmp     ebp, 3B9ACA00h
                jz      loc_912A0
                mov     rcx, rbx
                mov     rbx, [rbx+270h]
                mov     rax, [rcx+2B0h]
                test    rax, rax
                jz      loc_9119A
                mov     rcx, [rcx+2B8h]
                mov     rdx, [rcx+10h]
                dec     rdx
                and     rdx, 0FFFFFFFFFFFFFFF0h
                lea     rdi, [rax+rdx]
                add     rdi, 10h
                call    qword ptr [rcx+28h]
                jmp     loc_911A4
; ---------------------------------------------------------------------------

loc_90FDB:                              ; CODE XREF: sub_902F0+C22↑j
                mov     rax, [rcx]
                mov     rdi, [rcx+8]
                call    qword ptr [rax+10h]
                jmp     short loc_91050
; ---------------------------------------------------------------------------

loc_90FE7:                              ; CODE XREF: sub_902F0+C3C↑j
                mov     rdi, [rcx+8]

loc_90FEB:                              ; CODE XREF: sub_902F0+C54↑j
                call    qword ptr [rax]
                mov     r14, rax
                mov     r15, rdx
                mov     rax, [r12+18h]
                test    rax, rax
                jz      short loc_91005
                mov     rdi, [r12+20h]
                call    qword ptr [rax+18h]

loc_91005:                              ; CODE XREF: sub_902F0+D0B↑j
                mov     [r12+18h], r14
                mov     [r12+20h], r15
                mov     eax, 1
                xor     ecx, ecx
                lock cmpxchg [r12+28h], rcx
                jz      short loc_91050

loc_9101F:                              ; CODE XREF: sub_902F0+C68↑j
                mov     rax, [r12+18h]
                mov     rdi, [r12+20h]
                mov     qword ptr [r12+18h], 0
                test    rax, rax
                jz      loc_94687
                xor     ecx, ecx
                xchg    rcx, [r12+28h]
                call    qword ptr [rax+8]
                db      66h, 66h, 2Eh
                nop     word ptr [rax+rax+00000000h]

loc_91050:                              ; CODE XREF: sub_902F0+C2B↑j
                                        ; sub_902F0+C6E↑j ...
                mov     rax, [r12+10h]
                test    rax, rax
                jz      short loc_9108D
                cmp     rax, 1
                jz      loc_91CD8       ; jumptable 0000000000091CA0 case 6
                cmp     rax, 2
                jnz     loc_944E1
                cmp     byte ptr [rsp+0BB8h+var_B08], 2
                jz      short loc_9108D
                mov     rax, qword ptr [rsp+0BB8h+var_B18]
                mov     rax, [rax+38h]
                test    rax, rax
                js      loc_91C53

loc_9108D:                              ; CODE XREF: sub_902F0+D68↑j
                                        ; sub_902F0+D86↑j
                mov     edi, 18h        ; size
                call    cs:malloc_ptr
                test    rax, rax
                jz      loc_943B8
                mov     r12, rax
                mov     qword ptr [rax], 0
                mov     byte ptr [rax+10h], 5
                cmp     dword ptr [rbx+1E8h], 1
                movdqa  xmm0, [rsp+0BB8h+var_AA8]
                jnz     loc_9277A
                mov     r13, [rbx+1F0h]
                lea     rax, [r13-2]
                cmp     rax, 3
                setb    al
                cmp     r13, 3
                setnz   cl
                test    cl, al
                jnz     short loc_9113C
                movzx   esi, byte ptr [rbx+248h]
                movdqu  xmm1, xmmword ptr [rbx+210h]
                mov     rbp, [rbx+220h]
                test    rbp, rbp
                jz      loc_92466
                mov     r15, [rbx+228h]
                test    r15, r15
                js      loc_948FA
                movdqa  [rsp+0BB8h+var_B68], xmm1
                mov     byte ptr [rsp+0BB8h+var_BB0], sil
                jz      loc_9253A
                mov     rdi, r15        ; size
                call    cs:malloc_ptr
                test    rax, rax
                jz      loc_94906
                mov     r14, rax
                jmp     loc_92540
; ---------------------------------------------------------------------------

loc_9113C:                              ; CODE XREF: sub_902F0+DF0↑j
                mov     r9, [rbx+1F8h]
                mov     r10, [rbx+200h]
                mov     rbp, [rbx+208h]
                movdqu  xmm1, xmmword ptr [rbx+210h]
                mov     r14, [rbx+220h]
                mov     r8, [rbx+240h]
                movzx   esi, byte ptr [rbx+248h]
                mov     rdx, [rsp+0BB8h+var_B70]
                mov     eax, [rdx]
                mov     ecx, [rdx+3]
                mov     dword ptr [rsp+0BB8h+var_578+3], ecx
                mov     dword ptr [rsp+0BB8h+var_578], eax
                movdqu  xmm0, xmmword ptr [rbx+228h]
                mov     rcx, [rbx+238h]
                jmp     loc_92701
; ---------------------------------------------------------------------------

loc_9119A:                              ; CODE XREF: sub_902F0+CC3↑j
                mov     edi, 1
                call    sub_FE82F0

loc_911A4:                              ; CODE XREF: sub_902F0+CE6↑j
                add     rax, rbx
                seto    cl
                test    rbx, rbx
                sets    sil
                xor     sil, cl
                mov     rbx, [rsp+0BB8h+var_BB8]
                jnz     loc_9447B
                add     ebp, edx
                cmp     ebp, 3B9ACA00h
                jb      short loc_911D7
                inc     rax
                jo      loc_9447B
                add     ebp, 0C4653600h

loc_911D7:                              ; CODE XREF: sub_902F0+ED6↑j
                mov     byte ptr [rbx+2C8h], 1
                cmp     qword ptr [rbx+2A0h], 0
                mov     rcx, [rbx+2B0h]
                jz      short loc_91225
                test    rcx, rcx
                jz      loc_945CC
                mov     r8, [rbx+2B8h]
                mov     rdx, [r8+10h]
                dec     rdx
                and     rdx, 0FFFFFFFFFFFFFFF0h
                lea     rdi, [rcx+rdx]
                add     rdi, 10h
                mov     rsi, [rsp+0BB8h+var_A78]
                mov     rdx, rax
                mov     ecx, ebp
                call    qword ptr [r8+30h]
                jmp     short loc_912A0
; ---------------------------------------------------------------------------

loc_91225:                              ; CODE XREF: sub_902F0+EFD↑j
                test    rcx, rcx
                jz      loc_946A2
                mov     r8, [rbx+2B8h]
                mov     rdx, [r8+10h]
                dec     rdx
                and     rdx, 0FFFFFFFFFFFFFFF0h
                lea     rdi, [rcx+rdx]
                add     rdi, 10h
                mov     rsi, rax
                mov     edx, ebp
                call    qword ptr [r8+20h]
                mov     r14, rax
                mov     r15, rdx
                mov     r12, [rbx+2A0h]
                test    r12, r12
                jz      short loc_9128B
                mov     rbx, [rbx+2A8h]
                mov     rax, [rbx]
                test    rax, rax
                jz      short loc_91277
                mov     rdi, r12
                call    rax

loc_91277:                              ; CODE XREF: sub_902F0+F80↑j
                cmp     qword ptr [rbx+8], 0
                mov     rbx, [rsp+0BB8h+var_BB8]
                jz      short loc_9128B
                mov     rdi, r12        ; ptr
                call    cs:free_ptr

loc_9128B:                              ; CODE XREF: sub_902F0+F71↑j
                                        ; sub_902F0+F90↑j
                mov     [rbx+2A0h], r14
                mov     [rbx+2A8h], r15
                nop     dword ptr [rax+00000000h]

loc_912A0:                              ; CODE XREF: sub_902F0+C97↑j
                                        ; sub_902F0+CA9↑j ...
                mov     rcx, [rsp+0BB8h+var_8A8]
                mov     eax, [rcx]
                mov     ecx, [rcx+3]
                lea     rdx, [rsp+0BB8h+var_AB8]
                mov     [rdx+3], ecx
                mov     [rdx], eax
                movzx   eax, byte ptr [rbx+2CAh]
                movzx   ecx, byte ptr [rbx+2CCh]
                mov     rdx, [rsp+0BB8h+var_A60]
                mov     qword ptr [rsp+0BB8h+var_AC8], rdx
                mov     rdx, [rsp+0BB8h+var_8A0]
                mov     qword ptr [rsp+0BB8h+var_AC8+8], rdx
                movdqu  xmm0, xmmword ptr [rbx+168h]
                movdqa  [rsp+0BB8h+var_AD8], xmm0
                mov     byte ptr [rsp+0BB8h+var_AB8+7], al
                mov     [rsp+0BB8h+var_AB0], cl
                nop     word ptr [rax+rax+00000000h]

loc_91310:                              ; CODE XREF: sub_902F0+1421↓j
                mov     r14, [rbx+148h]
                test    r14, r14
                jz      loc_9149D
                cmp     qword ptr [rbx+0C8h], 0
                jz      loc_91420
                mov     rcx, [rbx+0D0h]
                mov     rax, rcx
                sub     rax, 3
                mov     edi, 0
                cmovnb  rdi, rax
                cmp     r14, rdi
                jb      loc_94350
                mov     rsi, r14
                sub     rsi, rdi
                jz      loc_9149D
                mov     rax, [rsp+0BB8h+src]
                add     rdi, [rax]
                mov     rdx, rcx
                sub     rdx, r14
                cmp     rcx, 3
                mov     eax, 3
                cmovb   rax, rcx
                sub     rdx, rax
                not     rcx
                add     rcx, r14
                add     rcx, rax
                mov     eax, 1
                jmp     short loc_913A7
; ---------------------------------------------------------------------------
                align 10h

loc_91390:                              ; CODE XREF: sub_902F0+10C7↓j
                                        ; sub_902F0+10D6↓j ...
                lea     r8, [rdx+rax]
                inc     r8
                inc     rax
                dec     rcx
                cmp     r8, 1
                jz      loc_9149D

loc_913A7:                              ; CODE XREF: sub_902F0+1096↑j
                movzx   r8d, byte ptr [rdi+rax-1]
                cmp     r8d, 0Ah
                jz      short loc_913F0
                cmp     r8d, 0Dh
                jnz     short loc_91390
                cmp     rax, rsi
                ja      loc_93C3F
                cmp     rcx, 2
                jbe     short loc_91390
                movzx   r8d, word ptr [rdi+rax]
                xor     r8d, 0D0Ah
                movzx   r9d, byte ptr [rdi+rax+2]
                xor     r9d, 0Ah
                or      r9w, r8w
                jnz     short loc_91390
                jmp     short loc_91420
; ---------------------------------------------------------------------------
                align 10h

loc_913F0:                              ; CODE XREF: sub_902F0+10C1↑j
                cmp     rax, rsi
                jnb     short loc_913FB
                cmp     byte ptr [rdi+rax], 0Ah
                jz      short loc_91420

loc_913FB:                              ; CODE XREF: sub_902F0+1103↑j
                cmp     rax, rsi
                ja      loc_93C4E
                cmp     rcx, 1
                jbe     short loc_91390
                cmp     word ptr [rdi+rax], 0A0Dh
                jnz     loc_91390
                db      2Eh
                nop     word ptr [rax+rax+00000000h]

loc_91420:                              ; CODE XREF: sub_902F0+1038↑j
                                        ; sub_902F0+10F4↑j ...
                lea     rdi, [rsp+0BB8h+dest]
                mov     rsi, [rsp+0BB8h+src]
                lea     rdx, [rsp+0BB8h+var_AD8]
                call    sub_DAF00
                mov     r14, qword ptr [rsp+0BB8h+dest]
                movzx   ebx, byte ptr [rsp+0BB8h+dest+8]
                cmp     r14, 4
                jz      loc_91756
                movzx   ebp, byte ptr [rsp+0BB8h+dest+0Fh]
                movzx   r12d, word ptr [rsp+0BB8h+dest+0Dh]
                mov     r15d, dword ptr [rsp+0BB8h+dest+9]
                mov     edx, 0E0h       ; n
                lea     rdi, [rsp+0BB8h+var_998] ; dest
                lea     rsi, [rsp+0BB8h+n] ; src
                call    cs:memcpy_ptr
                cmp     r14, 3
                jnz     loc_9184C
                mov     rbx, [rsp+0BB8h+var_BB8]
                mov     r14, [rbx+148h]

loc_9149D:                              ; CODE XREF: sub_902F0+102A↑j
                                        ; sub_902F0+1064↑j ...
                mov     rax, [rbx+130h]
                cmp     r14, rax
                jnb     loc_9173B
                test    r14, r14
                jz      short loc_914C0
                mov     [rbx+0D0h], r14
                mov     ecx, 1
                jmp     short loc_914C2
; ---------------------------------------------------------------------------

loc_914C0:                              ; CODE XREF: sub_902F0+11C0↑j
                xor     ecx, ecx

loc_914C2:                              ; CODE XREF: sub_902F0+11CE↑j
                mov     [rbx+0C8h], rcx
                mov     byte ptr [rbx+161h], 0
                sub     rax, r14
                mov     esi, 0
                cmovnb  rsi, rax
                mov     rax, [rbx+128h]
                cmp     rsi, rax
                cmovnb  rsi, rax
                mov     rbp, [rbx+150h]
                mov     rax, rbp
                sub     rax, r14
                cmp     rax, rsi
                jnb     short loc_91514
                mov     rdi, [rsp+0BB8h+src]
                call    sub_BBC20
                mov     r14, [rbx+148h]
                mov     rbp, [rbx+150h]

loc_91514:                              ; CODE XREF: sub_902F0+120A↑j
                cmp     rbp, r14
                jnz     short loc_91536
                mov     esi, 40h ; '@'
                mov     rdi, [rsp+0BB8h+src]
                call    sub_BBC20
                mov     r14, [rbx+148h]
                mov     rbp, [rbx+150h]

loc_91536:                              ; CODE XREF: sub_902F0+1227↑j
                sub     rbp, r14
                add     r14, [rbx+140h]
                mov     rax, rbx
                mov     rbx, [rbx+0A8h]
                mov     r15, [rax+0B0h]
                mov     r12, [rax+0B8h]
                mov     rdi, [rax+0C0h]
                mov     qword ptr [rax+0A8h], 0
                test    rbx, rbx
                jz      short loc_915D8
                test    r12, r12
                jz      short loc_915D0
                mov     qword ptr [rsp+0BB8h+var_B68], rdi
                cmp     rbp, r12
                mov     r13, r12
                cmovb   r13, rbp
                mov     rdi, r14        ; dest
                mov     rsi, r15        ; src
                mov     rdx, r13        ; n
                call    cs:memcpy_ptr
                mov     rdx, r12
                sub     rdx, r13
                add     r15, r13
                cmp     r12, rbp
                jbe     loc_91667
                mov     rax, [rsp+0BB8h+var_BB8]
                mov     [rax+0A8h], rbx
                mov     rbx, rax
                mov     [rax+0B0h], r15
                mov     [rax+0B8h], rdx
                jmp     loc_91676
; ---------------------------------------------------------------------------
                align 10h

loc_915D0:                              ; CODE XREF: sub_902F0+1282↑j
                mov     rsi, r15
                xor     edx, edx
                call    qword ptr [rbx+20h]

loc_915D8:                              ; CODE XREF: sub_902F0+127D↑j
                mov     qword ptr [rsp+0BB8h+dest], r14
                mov     qword ptr [rsp+0BB8h+dest+8], rbp
                lea     rax, [rsp+0BB8h+n]
                pxor    xmm0, xmm0
                movdqu  xmmword ptr [rax], xmm0
                mov     rsi, [r13+0]
                mov     rdi, [rsp+0BB8h+var_B98]
                lea     rdx, [rsp+0BB8h+dest]
                call    sub_FF2D10
                test    rdx, rdx
                setnz   cl
                or      cl, al
                test    cl, 1
                jz      short loc_91640
                test    al, 1
                mov     rbx, [rsp+0BB8h+var_BB8]
                jnz     loc_91B2D
                test    rdx, rdx
                jnz     loc_91B95
                mov     rax, [rbx+148h]
                xor     r13d, r13d
                jmp     short loc_91690
; ---------------------------------------------------------------------------
                align 20h

loc_91640:                              ; CODE XREF: sub_902F0+1329↑j
                mov     rsi, qword ptr [rsp+0BB8h+dest+8]
                mov     r13, [rsp+0BB8h+n]
                cmp     r13, rsi
                mov     rbx, [rsp+0BB8h+var_BB8]
                ja      loc_9435F
                cmp     r13, rbp
                jbe     short loc_91676
                jmp     loc_93C5D
; ---------------------------------------------------------------------------

loc_91667:                              ; CODE XREF: sub_902F0+12AE↑j
                mov     rdi, qword ptr [rsp+0BB8h+var_B68]
                mov     rsi, r15
                call    qword ptr [rbx+20h]
                mov     rbx, [rsp+0BB8h+var_BB8]

loc_91676:                              ; CODE XREF: sub_902F0+12D0↑j
                                        ; sub_902F0+1370↑j
                mov     rax, [rbx+148h]
                mov     rcx, [rbx+150h]
                sub     rcx, rax
                cmp     r13, rcx
                ja      loc_93C6F

loc_91690:                              ; CODE XREF: sub_902F0+134A↑j
                add     rax, r13
                mov     [rbx+148h], rax
                mov     rcx, [rbx+128h]
                cmp     r13, rcx
                jnb     short loc_916E0
                bsr     rcx, rcx
                not     ecx
                add     cl, 2
                mov     rax, 0FFFFFFFFFFFFFFFFh
                shr     rax, cl
                inc     rax
                cmp     r13, rax
                jnb     short loc_91701
                mov     cl, 1
                cmp     byte ptr [rbx+138h], 1
                jnz     short loc_91703
                cmp     rax, 2001h
                mov     ecx, 2000h
                cmovb   rax, rcx
                jmp     short loc_916FA
; ---------------------------------------------------------------------------
                align 20h

loc_916E0:                              ; CODE XREF: sub_902F0+13B4↑j
                lea     rdx, [rcx+rcx]
                mov     rax, [rbx+130h]
                cmp     rax, rdx
                cmovb   rdx, rax
                test    rcx, rcx
                js      short loc_916FA
                mov     rax, rdx

loc_916FA:                              ; CODE XREF: sub_902F0+13EB↑j
                                        ; sub_902F0+1405↑j
                mov     [rbx+128h], rax

loc_91701:                              ; CODE XREF: sub_902F0+13CF↑j
                xor     ecx, ecx

loc_91703:                              ; CODE XREF: sub_902F0+13DA↑j
                mov     [rbx+138h], cl
                test    r13, r13
                mov     r13, [rsp+0BB8h+var_BA8]
                jnz     loc_91310
                mov     edi, 18h        ; size
                call    cs:malloc_ptr
                test    rax, rax
                jz      loc_943B8
                mov     r12, rax
                mov     qword ptr [rax], 0
                mov     byte ptr [rax+10h], 2
                jmp     short loc_91784
; ---------------------------------------------------------------------------

loc_9173B:                              ; CODE XREF: sub_902F0+11B7↑j
                mov     edi, 18h        ; size
                call    cs:malloc_ptr
                test    rax, rax
                jz      loc_943B8
                mov     r12, rax
                mov     bl, 0Ah
                jmp     short loc_9176D
; ---------------------------------------------------------------------------

loc_91756:                              ; CODE XREF: sub_902F0+115E↑j
                mov     edi, 18h        ; size
                call    cs:malloc_ptr
                mov     r12, rax
                test    rax, rax
                jz      loc_943B8

loc_9176D:                              ; CODE XREF: sub_902F0+1464↑j
                mov     qword ptr [r12], 0
                mov     byte ptr [r12+10h], 0
                mov     [r12+11h], bl

loc_91780:                              ; CODE XREF: sub_902F0+18EB↓j
                mov     rbx, [rsp+0BB8h+var_BB8]

loc_91784:                              ; CODE XREF: sub_902F0+1449↑j
                mov     rdi, [rsp+0BB8h+var_B48]
                call    sub_D9250
                mov     r14, [rbx+148h]
                test    r14, r14
                jz      loc_91836
                mov     rax, [rsp+0BB8h+src]
                mov     r13, [rax]
                xor     r15d, r15d
                jmp     short loc_917B8
; ---------------------------------------------------------------------------
                align 10h

loc_917B0:                              ; CODE XREF: sub_902F0+14D1↓j
                                        ; sub_902F0+14D6↓j
                inc     r15
                cmp     r14, r15
                jz      short loc_917F4

loc_917B8:                              ; CODE XREF: sub_902F0+14B9↑j
                movzx   eax, byte ptr [r13+r15+0]
                cmp     eax, 0Dh
                jz      short loc_917B0
                cmp     eax, 0Ah
                jz      short loc_917B0
                mov     [rsp+0BB8h+var_898], r15
                cmp     r15, r14
                ja      loc_943D6
                test    r15, r15
                jz      loc_919F3
                mov     rbp, [rbx+158h]
                test    bpl, 1
                jnz     short loc_91808
                jmp     loc_919CF
; ---------------------------------------------------------------------------

loc_917F4:                              ; CODE XREF: sub_902F0+14C6↑j
                mov     r15, r14
                mov     rbp, [rbx+158h]
                test    bpl, 1
                jz      loc_919CF

loc_91808:                              ; CODE XREF: sub_902F0+14FD↑j
                mov     rbx, rbp
                shr     rbx, 5
                lea     rax, [rbx+r15]
                mov     rcx, rax
                shr     rcx, 3Bh
                jnz     loc_9197F
                shl     rax, 5
                and     ebp, 1Fh
                or      rbp, rax
                mov     rax, rbp
                mov     rsi, [rsp+0BB8h+var_BB8]
                jmp     loc_919C5
; ---------------------------------------------------------------------------

loc_91836:                              ; CODE XREF: sub_902F0+14A8↑j
                xor     r14d, r14d
                movzx   eax, byte ptr [r12+10h]
                test    al, al
                jnz     loc_91A06
                jmp     loc_91A97
; ---------------------------------------------------------------------------

loc_9184C:                              ; CODE XREF: sub_902F0+119C↑j
                movzx   eax, bl
                shl     ebp, 10h
                or      r12d, ebp
                shl     r12, 20h
                or      r15, r12
                shl     r15, 8
                or      r15, rax
                mov     edx, 0E0h       ; n
                lea     rdi, [rsp+0BB8h+var_568] ; dest
                lea     rsi, [rsp+0BB8h+var_998] ; src
                call    cs:memcpy_ptr
                mov     rbx, [rsp+0BB8h+var_BB8]
                mov     qword ptr [rbx+0C8h], 0
                mov     qword ptr [rsp+0BB8h+var_578], r14
                mov     qword ptr [rsp+0BB8h+var_578+8], r15
                mov     byte ptr [rbx+2C8h], 0
                mov     r14, [rbx+2A0h]
                test    r14, r14
                jz      short loc_918D8
                mov     rbx, [rbx+2A8h]
                mov     rax, [rbx]
                test    rax, rax
                jz      short loc_918C4
                mov     rdi, r14
                call    rax

loc_918C4:                              ; CODE XREF: sub_902F0+15CD↑j
                cmp     qword ptr [rbx+8], 0
                mov     rbx, [rsp+0BB8h+var_BB8]
                jz      short loc_918D8
                mov     rdi, r14        ; ptr
                call    cs:free_ptr

loc_918D8:                              ; CODE XREF: sub_902F0+15BE↑j
                                        ; sub_902F0+15DD↑j
                mov     qword ptr [rbx+2A0h], 0
                mov     byte ptr [rbx+2CCh], 0
                cmp     byte ptr [rbx+2CFh], 2
                jz      short loc_918FA
                mov     byte ptr [rbx+2CFh], 1

loc_918FA:                              ; CODE XREF: sub_902F0+1601↑j
                cmp     [rsp+0BB8h+var_48F], 0
                jnz     short loc_9190B
                mov     byte ptr [rbx+2CFh], 2

loc_9190B:                              ; CODE XREF: sub_902F0+1612↑j
                movzx   eax, byte ptr [rsp+0BB8h+var_4A0]
                mov     [rbx+2D0h], al
                movzx   esi, [rsp+0BB8h+var_48E]
                add     sil, sil
                mov     r12, [rsp+0BB8h+var_498]
                test    r12, r12
                mov     [rsp+0BB8h+var_BB0], r12
                jz      loc_92498
                cmp     al, 2
                setnb   al
                test    [rsp+0BB8h+var_490], al
                jz      loc_92507
                cmp     r12, 0FFFFFFFFFFFFFFFEh
                jz      loc_92B4A
                cmp     r12, 0FFFFFFFFFFFFFFFFh
                jnz     loc_92B99
                mov     r15d, 4
                xor     r12d, r12d
                mov     rax, [rbx+1E8h]
                cmp     rax, 1
                jnz     loc_92BB3
                jmp     loc_92BBC
; ---------------------------------------------------------------------------

loc_9197F:                              ; CODE XREF: sub_902F0+152A↑j
                mov     edi, 28h ; '('  ; size
                call    cs:malloc_ptr
                test    rax, rax
                jz      loc_94693
                shr     ebp, 2
                and     ebp, 7
                mov     rcx, r13
                sub     rcx, rbx
                lea     rdx, [r14+rbx]
                mov     rsi, [rsp+0BB8h+var_BB8]
                add     rbx, [rsi+150h]
                mov     [rax], rbx
                mov     [rax+8], rcx
                mov     [rax+10h], rdx
                mov     [rax+18h], rbp
                mov     qword ptr [rax+20h], 1

loc_919C5:                              ; CODE XREF: sub_902F0+1541↑j
                mov     [rsi+158h], rax
                mov     rbx, rsi

loc_919CF:                              ; CODE XREF: sub_902F0+14FF↑j
                                        ; sub_902F0+1512↑j
                add     r13, r15
                mov     [rbx+140h], r13
                sub     r14, r15
                mov     eax, 0
                cmovb   r14, rax
                mov     [rbx+148h], r14
                sub     [rbx+150h], r15

loc_919F3:                              ; CODE XREF: sub_902F0+14EC↑j
                mov     r13, [rsp+0BB8h+var_BA8]
                movzx   eax, byte ptr [r12+10h]
                test    al, al
                jz      loc_91A97

loc_91A06:                              ; CODE XREF: sub_902F0+1551↑j
                test    r14, r14
                jnz     loc_91A97
                mov     r15, [rbx+250h]
                mov     rbp, 7FFFFFFFFFFFFFFDh
                lea     rax, [r15+rbp]
                cmp     rax, 4
                jb      loc_91E9D
                lea     rax, [rbp+4]
                cmp     r15, rax
                jnb     loc_91E9D
                lea     rax, [rbp+3]
                cmp     r15, rax
                jz      loc_91E9D
                mov     r14, [rbx+258h]
                mov     rbx, [rbx+260h]
                test    rbx, rbx
                jz      loc_91E7C
                lea     r13, [r14+18h]
                jmp     short loc_91A7D
; ---------------------------------------------------------------------------
                align 10h

loc_91A70:                              ; CODE XREF: sub_902F0+1794↓j
                                        ; sub_902F0+17A5↓j
                add     r13, 20h ; ' '
                dec     rbx
                jz      loc_91E7C

loc_91A7D:                              ; CODE XREF: sub_902F0+1773↑j
                mov     rax, [r13-18h]
                test    rax, rax
                jz      short loc_91A70
                mov     rdi, [r13+0]
                mov     rsi, [r13-10h]
                mov     rdx, [r13-8]
                call    qword ptr [rax+20h]
                jmp     short loc_91A70
; ---------------------------------------------------------------------------

loc_91A97:                              ; CODE XREF: sub_902F0+1557↑j
                                        ; sub_902F0+1710↑j ...
                mov     rcx, [rbx+250h]
                mov     rdx, 7FFFFFFFFFFFFFFDh
                add     rcx, rdx
                jnz     short loc_91B16
                cmp     r14, 18h
                jb      short loc_91AE8
                mov     rcx, [rsp+0BB8h+src]
                mov     rcx, [rcx]
                movdqu  xmm0, xmmword ptr [rcx]
                pcmpeqb xmm0, cs:xmmword_10001C0
                movq    xmm1, qword ptr [rcx+10h]
                pcmpeqb xmm1, cs:xmmword_10001B0
                pand    xmm1, xmm0
                pmovmskb ecx, xmm1
                cmp     ecx, 0FFFFh
                jz      loc_925FD

loc_91AE8:                              ; CODE XREF: sub_902F0+17C1↑j
                test    al, al
                jnz     short loc_91B16
                movzx   eax, byte ptr [r12+11h]
                add     al, 0FCh
                cmp     al, 9
                movzx   eax, al
                mov     ecx, 5
                cmovnb  eax, ecx
                cmp     al, 6
                ja      short loc_91B16
                movzx   eax, al
                mov     ecx, 7Bh ; '{'
                bt      ecx, eax
                jb      loc_938F0

loc_91B16:                              ; CODE XREF: sub_902F0+17BB↑j
                                        ; sub_902F0+17FA↑j ...
                mov     r14, r12

loc_91B19:                              ; CODE XREF: sub_902F0+18A3↓j
                                        ; sub_902F0+236C↓j
                mov     ebp, 3
                cmp     rbp, 3
                jnz     loc_91EF6
                jmp     loc_93707
; ---------------------------------------------------------------------------

loc_91B2D:                              ; CODE XREF: sub_902F0+1331↑j
                mov     byte ptr [rbx+161h], 1
                cmp     byte ptr [rbx+2C8h], 0
                jz      loc_91D30
                mov     rax, [rsp+0BB8h+var_A78]
                mov     rdi, [rax]
                test    rdi, rdi
                jz      loc_91D30
                mov     rax, [rbx+2A8h]
                mov     rsi, r13
                call    qword ptr [rax+18h]
                test    al, al
                jnz     loc_91D30
                mov     byte ptr [rbx+2C8h], 0
                mov     edi, 18h        ; size
                call    cs:malloc_ptr
                test    rax, rax
                jz      loc_943B8
                mov     r14, rax
                mov     qword ptr [rax], 0
                mov     byte ptr [rax+10h], 7
                jmp     short loc_91B19
; ---------------------------------------------------------------------------

loc_91B95:                              ; CODE XREF: sub_902F0+133A↑j
                mov     rbx, rdx
                mov     edi, 18h        ; size
                mov     r14, cs:malloc_ptr
                call    r14 ; malloc
                test    rax, rax
                jz      loc_943B8
                mov     r12, rax
                mov     byte ptr [rax+10h], 6
                mov     edi, 8          ; size
                call    r14 ; malloc
                test    rax, rax
                jz      loc_94493
                mov     [rax], rbx
                mov     [r12], rax
                lea     rax, off_210CCF28
                mov     [r12+8], rax
                jmp     loc_91780
; ---------------------------------------------------------------------------

loc_91BE0:                              ; CODE XREF: sub_902F0+BC1↑j
                mov     bpl, 1
                cmp     eax, 4
                jz      loc_91D1A
                cmp     byte ptr [rbx+2C0h], 0
                jnz     loc_91D1A
                cmp     qword ptr [rbx+148h], 0
                jnz     loc_91D1A
                mov     rdi, [rsp+0BB8h+var_B98]
                mov     rsi, r13
                call    sub_6E8E0
                mov     r14, rdx
                cmp     rax, 2
                jz      loc_91D1A
                test    al, 1
                jz      loc_92FFB
                mov     rdi, [rsp+0BB8h+var_B48]
                call    sub_D9100
                mov     rdi, r14
                call    sub_D6E10
                mov     rdx, rax
                cmp     byte ptr [rsp+0BB8h+var_AB8], 3
                jnz     loc_93804
                xor     ebp, ebp
                jmp     loc_91D1A
; ---------------------------------------------------------------------------

loc_91C53:                              ; CODE XREF: sub_902F0+D97↑j
                lea     rdi, [rsp+0BB8h+var_B18]
                mov     rsi, r13
                call    sub_D5DC0
                test    al, al
                jnz     short loc_91CD8 ; jumptable 0000000000091CA0 case 6
                lea     rdi, [rsp+0BB8h+var_578]
                mov     rsi, [rsp+0BB8h+var_B98]
                mov     rdx, r13
                call    sub_724E0
                mov     r15, qword ptr [rsp+0BB8h+var_578]
                lea     rax, [r15-3]    ; switch 4 cases
                cmp     rax, 3
                ja      def_91CA0       ; jumptable 0000000000091CA0 default case
                lea     rcx, jpt_91CA0
                movsxd  rax, ds:(jpt_91CA0 - 1002B7Ch)[rcx+rax*4]
                add     rax, rcx
                jmp     rax             ; switch jump
; ---------------------------------------------------------------------------

loc_91CA2:                              ; CODE XREF: sub_902F0+19B0↑j
                                        ; DATA XREF: .rodata:jpt_91CA0↓o
                cmp     byte ptr [rsp+0BB8h+var_B08], 2 ; jumptable 0000000000091CA0 case 3
                jnz     loc_92CFB
                lea     rax, [rsp+0BB8h+var_578+8]
                movdqu  xmm0, xmmword ptr [rax]
                movdqu  xmm1, xmmword ptr [rax+10h]
                movdqa  xmmword ptr [rsp+0BB8h+n], xmm1
                movdqa  [rsp+0BB8h+dest], xmm0
                jmp     loc_92D26
; ---------------------------------------------------------------------------

loc_91CD8:                              ; CODE XREF: sub_902F0+D6E↑j
                                        ; sub_902F0+1975↑j ...
                cmp     byte ptr [rbx+2F8h], 3 ; jumptable 0000000000091CA0 case 6
                jz      short loc_91CEB
                mov     rdi, [rsp+0BB8h+var_B90]
                call    sub_DAA80

loc_91CEB:                              ; CODE XREF: sub_902F0+19EF↑j
                mov     rax, [rsp+0BB8h+var_B08]
                mov     rcx, [rsp+0BB8h+var_B90]
                mov     [rcx+20h], rax
                movdqa  xmm0, xmmword ptr [rsp+0BB8h+var_B28]
                movdqa  xmm1, [rsp+0BB8h+var_B18]
                movdqu  xmmword ptr [rcx+10h], xmm1
                movdqu  xmmword ptr [rcx], xmm0
                mov     bpl, 1

loc_91D1A:                              ; CODE XREF: sub_902F0+18F6↑j
                                        ; sub_902F0+1903↑j ...
                test    bpl, bpl
                jnz     short loc_91D30
                test    rdx, rdx
                jnz     loc_93F50
                nop     dword ptr [rax+rax+00000000h]

loc_91D30:                              ; CODE XREF: sub_902F0+B70↑j
                                        ; sub_902F0+C8A↑j ...
                mov     r15, [rsp+0BB8h+var_B98]
                mov     rdi, r15
                mov     rsi, r13
                call    sub_741F0
                mov     r14, rax
                test    rdx, rdx
                setz    al
                or      al, r14b
                test    al, 1
                jz      loc_93F50
                mov     rdi, r15
                mov     rsi, r13
                call    sub_74140
                test    rdx, rdx
                setz    cl
                mov     edi, dword ptr [rsp+0BB8h+var_B38]
                movzx   edi, dil
                mov     esi, 0
                cmovz   edi, esi
                test    al, 1
                mov     esi, 1
                cmovnz  edi, esi
                mov     dword ptr [rsp+0BB8h+var_B38], edi
                or      cl, al
                test    cl, 1
                jz      loc_93F50
                cmp     byte ptr [rbx+318h], 0
                jnz     short loc_91DF0
                mov     rax, [rbx+310h]
                cmp     qword ptr [rax], 0
                jz      short loc_91DF0
                mov     rax, [rbx+250h]
                mov     rdx, 7FFFFFFFFFFFFFFDh
                lea     rcx, [rax+rdx]
                cmp     rcx, 4
                setb    cl
                add     rdx, 7
                cmp     rax, rdx
                setnz   al
                test    al, cl
                jnz     short loc_91DF0
                test    r14b, 1
                jnz     short loc_91E52
                movzx   ecx, byte ptr [rbx+2CDh]
                mov     byte ptr [rbx+2CDh], 0
                mov     al, 1
                test    cl, cl
                jz      short loc_91E0C
                jmp     short loc_91E2E
; ---------------------------------------------------------------------------

loc_91DF0:                              ; CODE XREF: sub_902F0+1AAB↑j
                                        ; sub_902F0+1AB8↑j ...
                movzx   ecx, byte ptr [rbx+2CDh]
                mov     byte ptr [rbx+2CDh], 0
                test    cl, cl
                jz      loc_93D0D
                xor     eax, eax
                test    cl, cl
                jnz     short loc_91E2E

loc_91E0C:                              ; CODE XREF: sub_902F0+1AFC↑j
                                        ; sub_902F0+1B88↓j
                test    al, al
                jz      short loc_91E2E
                mov     rdi, [rsp+0BB8h+var_B98]
                mov     rsi, r13
                call    sub_741F0
                test    al, 1
                jnz     loc_93BF3
                test    rdx, rdx
                jnz     loc_93F50

loc_91E2E:                              ; CODE XREF: sub_902F0+1AFE↑j
                                        ; sub_902F0+1B1A↑j ...
                mov     ecx, [rsp+0BB8h+var_B2C]
                cmp     ecx, 10h
                mov     eax, ecx
                adc     eax, 0
                cmp     ecx, 10h
                mov     [rsp+0BB8h+var_B2C], eax
                jb      loc_90E59
                jmp     loc_93ACF
; ---------------------------------------------------------------------------

loc_91E52:                              ; CODE XREF: sub_902F0+1AE8↑j
                mov     eax, dword ptr [rsp+0BB8h+var_B38]
                and     al, 1
                setz    dl
                movzx   ecx, byte ptr [rbx+2CDh]
                mov     byte ptr [rbx+2CDh], 0
                or      dl, cl
                jz      loc_93D0D
                xor     al, 1
                test    cl, cl
                jz      short loc_91E0C
                jmp     short loc_91E2E
; ---------------------------------------------------------------------------

loc_91E7C:                              ; CODE XREF: sub_902F0+1769↑j
                                        ; sub_902F0+1787↑j
                test    r15, r15
                mov     rbx, [rsp+0BB8h+var_BB8]
                mov     r13, [rsp+0BB8h+var_BA8]
                mov     rbp, 7FFFFFFFFFFFFFFDh
                jz      short loc_91E9D
                mov     rdi, r14        ; ptr
                call    cs:free_ptr

loc_91E9D:                              ; CODE XREF: sub_902F0+1738↑j
                                        ; sub_902F0+1745↑j ...
                lea     rax, [rbp+9]
                mov     [rbx+250h], rax
                mov     byte ptr [rbx+2CFh], 2
                mov     r14, [r12]
                test    r14, r14
                jz      short loc_91EDE
                mov     rbx, [r12+8]
                mov     rax, [rbx]
                test    rax, rax
                jz      short loc_91ECA
                mov     rdi, r14
                call    rax

loc_91ECA:                              ; CODE XREF: sub_902F0+1BD3↑j
                cmp     qword ptr [rbx+8], 0
                mov     rbx, [rsp+0BB8h+var_BB8]
                jz      short loc_91EDE
                mov     rdi, r14        ; ptr
                call    cs:free_ptr

loc_91EDE:                              ; CODE XREF: sub_902F0+1BC6↑j
                                        ; sub_902F0+1BE3↑j
                mov     rdi, r12        ; ptr
                call    cs:free_ptr
                mov     ebp, 4
                cmp     rbp, 3
                jz      loc_93707

loc_91EF6:                              ; CODE XREF: sub_902F0+1832↑j
                                        ; sub_902F0+3411↓j
                cmp     rbp, 4
                jnz     short loc_91F1F
                mov     rax, [rbx+250h]
                mov     rcx, 7FFFFFFFFFFFFFFDh
                add     rax, rcx
                cmp     rax, 3
                jnz     loc_90E59
                jmp     loc_9373F
; ---------------------------------------------------------------------------

loc_91F1F:                              ; CODE XREF: sub_902F0+1C0A↑j
                mov     [rsp+0BB8h+var_B88], r14
                mov     edx, 0C0h       ; n
                lea     rdi, [rsp+0BB8h+var_578] ; dest
                lea     rsi, [rsp+0BB8h+var_A58] ; src
                call    cs:memcpy_ptr
                test    r12, r12
                jz      loc_920EE
                mov     edi, 30h ; '0'  ; size
                call    cs:malloc_ptr
                test    rax, rax
                jz      loc_943C7
                mov     r14, rax
                mov     qword ptr [rax], 0
                mov     qword ptr [rax+28h], 0
                mov     edi, 1          ; nmemb
                mov     esi, 10h        ; size
                call    cs:calloc_ptr
                test    rax, rax
                jz      loc_9446C
                mov     r15, rax
                mov     edi, 60h ; '`'  ; size
                call    cs:malloc_ptr
                test    rax, rax
                jz      loc_9456E
                mov     rcx, rax
                mov     qword ptr [rax], 1
                mov     qword ptr [rax+8], 1
                mov     [rax+10h], r14
                mov     [rax+18h], r14
                mov     [rax+20h], r15
                mov     [rax+28h], r15
                mov     qword ptr [rax+30h], 0
                mov     rax, 7FFFFFFFFFFFFFFDh
                add     rax, 3
                mov     [rcx+38h], rax
                mov     qword ptr [rcx+40h], 1
                mov     qword ptr [rcx+48h], 0
                mov     qword ptr [rcx+58h], 0
                mov     [rsp+0BB8h+var_AF8], rcx
                lock inc qword ptr [rcx]
                jle     loc_948A1
                mov     edi, 30h ; '0'  ; size
                mov     r14, cs:malloc_ptr
                call    r14 ; malloc
                test    rax, rax
                jz      loc_943C7
                mov     r15, rax
                mov     qword ptr [rax], 1
                mov     qword ptr [rax+8], 1
                mov     dword ptr [rax+10h], 0
                mov     byte ptr [rax+14h], 0
                mov     qword ptr [rax+18h], 0
                mov     byte ptr [rax+28h], 0
                mov     edi, 0B0h       ; size
                call    r14 ; malloc
                test    rax, rax
                jz      loc_9457D
                mov     qword ptr [rax], 1
                mov     qword ptr [rax+8], 1
                mov     qword ptr [rax+10h], 3
                mov     byte ptr [rax+70h], 0
                mov     qword ptr [rax+78h], 0
                mov     byte ptr [rax+88h], 0
                mov     qword ptr [rax+90h], 0
                mov     byte ptr [rax+0A0h], 0
                mov     byte ptr [rax+0A8h], 0
                mov     [rsp+0BB8h+var_A68], rax
                lock inc qword ptr [rax]
                jle     loc_948A1
                mov     edi, 30h ; '0'  ; size
                call    cs:malloc_ptr
                mov     r14, rax
                movzx   esi, byte ptr [rsp+0BB8h+var_B50]
                test    sil, 1
                jnz     short loc_9210D
                test    r14, r14
                mov     rax, [rsp+0BB8h+var_AF8]
                jz      loc_943C7
                mov     qword ptr [r14], 1
                mov     qword ptr [r14+8], 1
                mov     qword ptr [r14+10h], 2
                jmp     short loc_92135
; ---------------------------------------------------------------------------

loc_920EE:                              ; CODE XREF: sub_902F0+1C52↑j
                mov     r12, [rsp+0BB8h+var_A70]
                xor     r14d, r14d
                movzx   esi, byte ptr [rsp+0BB8h+var_B50]
                test    sil, 2
                jnz     loc_921BF
                jmp     loc_923BB
; ---------------------------------------------------------------------------

loc_9210D:                              ; CODE XREF: sub_902F0+1DD2↑j
                test    r14, r14
                mov     rax, [rsp+0BB8h+var_AF8]
                jz      loc_943C7
                mov     qword ptr [r14], 1
                mov     qword ptr [r14+8], 1
                mov     qword ptr [r14+10h], 1

loc_92135:                              ; CODE XREF: sub_902F0+1DFC↑j
                mov     qword ptr [r14+18h], 0
                mov     qword ptr [r14+28h], 0
                lock inc qword ptr [r14]
                jle     loc_948A1
                cmp     byte ptr [rbx+2F8h], 3
                jz      short loc_9216F
                mov     rdi, [rsp+0BB8h+var_B90]
                call    sub_DAA80
                movzx   esi, byte ptr [rsp+0BB8h+var_B50]
                mov     rax, [rsp+0BB8h+var_AF8]

loc_9216F:                              ; CODE XREF: sub_902F0+1E66↑j
                mov     rcx, [rsp+0BB8h+var_A68]
                mov     [rbx+2D8h], rcx
                mov     [rbx+2E0h], r14
                mov     [rbx+2E8h], rax
                mov     [rbx+2F0h], r15
                mov     byte ptr [rbx+2F8h], 0
                mov     eax, dword ptr [rsp+0BB8h+var_AE0]
                mov     ecx, dword ptr [rsp+0BB8h+var_AE0+3]
                mov     rdx, [rsp+0BB8h+var_AE8]
                mov     [rdx+3], ecx
                mov     [rdx], eax
                test    sil, 2
                jz      loc_923BB

loc_921BF:                              ; CODE XREF: sub_902F0+1E12↑j
                mov     [rsp+0BB8h+var_BB0], r12
                mov     edi, 70h ; 'p'  ; size
                mov     r15, cs:malloc_ptr
                call    r15 ; malloc
                test    rax, rax
                jz      loc_945BD
                mov     r12, rax
                mov     qword ptr [rax], 1
                mov     qword ptr [rax+8], 1
                pxor    xmm0, xmm0
                movdqu  xmmword ptr [rax+30h], xmm0
                lock inc qword ptr [rax]
                jle     loc_948A1
                mov     edi, 20h ; ' '  ; size
                call    r15 ; malloc
                test    rax, rax
                jz      loc_9455F
                mov     r15, rax
                mov     qword ptr [rax], 1
                mov     qword ptr [rax+8], 1
                mov     qword ptr [rax+10h], 0
                mov     [rax+18h], r12
                cmp     qword ptr [rbx+178h], 0
                mov     r13, rbx
                jz      short loc_92293
                mov     rbx, [r13+180h]
                test    rbx, rbx
                jz      short loc_92293
                mov     rax, [rbx+30h]
                nop     dword ptr [rax]

loc_92250:                              ; CODE XREF: sub_902F0+1F78↓j
                mov     rcx, rax
                test    cl, 4
                jnz     short loc_9226A
                mov     rdx, rcx
                or      rdx, 2
                mov     rax, rcx
                lock cmpxchg [rbx+30h], rdx
                jnz     short loc_92250

loc_9226A:                              ; CODE XREF: sub_902F0+1F66↑j
                and     ecx, 5
                cmp     ecx, 1
                jnz     short loc_9227D
                mov     rax, [rbx+20h]
                mov     rdi, [rbx+28h]
                call    qword ptr [rax+10h]

loc_9227D:                              ; CODE XREF: sub_902F0+1F80↑j
                lock dec qword ptr [rbx]
                mov     r13, [rsp+0BB8h+var_BB8]
                jnz     short loc_92293
                mov     rdi, [r13+180h] ; ptr
                call    sub_D5470

loc_92293:                              ; CODE XREF: sub_902F0+1F4B↑j
                                        ; sub_902F0+1F57↑j ...
                mov     qword ptr [r13+178h], 1
                mov     [r13+180h], r12
                mov     rax, qword ptr [rsp+0BB8h+var_B68]
                test    rax, rax
                mov     rbx, r13
                mov     r12, cs:malloc_ptr
                mov     r13, 0A4B9F50F0C6047C5h
                jnz     short loc_922EB
                mov     edi, 20h ; ' '  ; size
                call    r12 ; malloc
                test    rax, rax
                jz      loc_9455F
                movups  xmm0, cs:xmmword_210E6EB0
                movups  xmmword ptr [rax+10h], xmm0
                movdqu  xmm0, xmmword ptr cs:off_210E6EA0
                movdqu  xmmword ptr [rax], xmm0

loc_922EB:                              ; CODE XREF: sub_902F0+1FD1↑j
                mov     qword ptr [rsp+0BB8h+var_B68], rax
                mov     edi, 8          ; size
                call    r12 ; malloc
                test    rax, rax
                jz      loc_94493
                mov     [rax], r15
                mov     rdi, qword ptr [rsp+0BB8h+var_B68]
                mov     rsi, r13
                mov     r13, 6661BE1274C6C1E8h
                mov     rdx, r13
                mov     rcx, rax
                lea     r8, off_210C7408
                call    sub_9F040
                test    rax, rax
                jz      loc_923B1
                mov     rdi, rax
                call    qword ptr [rdx+38h]
                mov     r15, rax
                mov     r12, rdx
                mov     rdi, rax
                call    qword ptr [rdx+18h]
                mov     rcx, 0A4B9F50F0C6047C5h
                xor     rax, rcx
                xor     rdx, r13
                or      rdx, rax
                setz    al
                cmovz   r12, r15
                mov     r13, [r12]
                test    r15, r15
                jz      short loc_92388
                test    al, al
                jnz     short loc_92388
                test    r13, r13
                jz      short loc_92375
                mov     rdi, r15
                call    r13

loc_92375:                              ; CODE XREF: sub_902F0+207D↑j
                cmp     qword ptr [r12+8], 0
                jz      short loc_923B1
                mov     rdi, r15        ; ptr
                call    cs:free_ptr
                jmp     short loc_923B1
; ---------------------------------------------------------------------------

loc_92388:                              ; CODE XREF: sub_902F0+2074↑j
                                        ; sub_902F0+2078↑j
                mov     rdi, r12        ; ptr
                call    cs:free_ptr
                test    r13, r13
                jz      short loc_923B1
                lock dec qword ptr [r13+0]
                mov     r12, [rsp+0BB8h+var_BB0]
                jnz     short loc_923AA
                mov     rdi, r13        ; ptr
                call    sub_6D470

loc_923AA:                              ; CODE XREF: sub_902F0+20B0↑j
                mov     r13, [rsp+0BB8h+var_BA8]
                jmp     short loc_923BB
; ---------------------------------------------------------------------------

loc_923B1:                              ; CODE XREF: sub_902F0+203B↑j
                                        ; sub_902F0+208B↑j ...
                mov     r13, [rsp+0BB8h+var_BA8]
                mov     r12, [rsp+0BB8h+var_BB0]

loc_923BB:                              ; CODE XREF: sub_902F0+1E18↑j
                                        ; sub_902F0+1EC9↑j ...
                mov     edx, 0C0h       ; n
                lea     rdi, [rsp+0BB8h+n] ; dest
                lea     rsi, [rsp+0BB8h+var_578] ; src
                call    cs:memcpy_ptr
                mov     rax, [rsp+0BB8h+var_A68]
                mov     [rsp+0BB8h+var_790], rax
                mov     [rsp+0BB8h+var_788], r12
                mov     rax, [rsp+0BB8h+var_AF8]
                mov     [rsp+0BB8h+var_780], rax
                mov     qword ptr [rsp+0BB8h+dest], rbp
                mov     rax, [rsp+0BB8h+var_B88]
                mov     qword ptr [rsp+0BB8h+dest+8], rax
                mov     rax, qword ptr [rsp+0BB8h+var_B68]
                mov     [rsp+0BB8h+var_7A8], rax
                mov     rax, [rsp+0BB8h+var_B40]
                mov     [rsp+0BB8h+var_7A0], rax
                mov     [rsp+0BB8h+var_798], r14
                mov     rdi, [rbx+300h]
                mov     rsi, [rbx+308h]
                lea     rdx, [rsp+0BB8h+dest]
                call    sub_59A00
                test    rax, rax
                jnz     loc_92C91
                mov     [rsp+0BB8h+var_A70], r12
                jmp     loc_90E59
; ---------------------------------------------------------------------------

loc_92466:                              ; CODE XREF: sub_902F0+E0B↑j
                mov     r8, [rbx+240h]
                mov     r9, [rbx+1F8h]
                mov     r10, [rbx+200h]
                and     r13d, 1
                mov     rbp, [rbx+208h]
                xor     r14d, r14d

loc_92489:                              ; CODE XREF: sub_902F0+25D0↓j
                mov     rdx, [rsp+0BB8h+var_B70]
                mov     rcx, [rsp+0BB8h+var_B78]
                jmp     loc_92701
; ---------------------------------------------------------------------------

loc_92498:                              ; CODE XREF: sub_902F0+1644↑j
                mov     rax, [rbx+1E8h]
                cmp     rax, 1
                jz      short loc_924AE
                cmp     eax, 2
                jnz     loc_92CD5

loc_924AE:                              ; CODE XREF: sub_902F0+21B3↑j
                mov     rcx, [rbx+1F0h]
                mov     rax, [rbx+220h]
                add     rcx, 0FFFFFFFFFFFFFFFEh
                cmp     rcx, 3
                setb    cl
                test    rax, rax
                setz    dl
                or      dl, cl
                jnz     loc_92CD5
                mov     rdi, [rbx+238h]
                test    dil, 1
                jz      loc_92CA3
                shr     rdi, 5
                mov     rcx, [rbx+230h]
                add     rcx, rdi
                jz      loc_92CD5
                mov     ebp, esi
                sub     rax, rdi
                mov     rdi, rax
                jmp     loc_92CCD
; ---------------------------------------------------------------------------

loc_92507:                              ; CODE XREF: sub_902F0+1656↑j
                cmp     r12, 0FFFFFFFFFFFFFFFEh
                jz      loc_92B6E
                cmp     r12, 0FFFFFFFFFFFFFFFFh
                jnz     loc_92C15
                mov     r15d, 4
                xor     r12d, r12d
                mov     rax, [rbx+1E8h]
                cmp     rax, 1
                jnz     loc_92C2F
                jmp     loc_92C38
; ---------------------------------------------------------------------------

loc_9253A:                              ; CODE XREF: sub_902F0+E2C↑j
                mov     r14d, 1

loc_92540:                              ; CODE XREF: sub_902F0+E47↑j
                mov     rdi, r14        ; dest
                mov     rsi, rbp        ; src
                mov     rdx, r15        ; n
                call    cs:memcpy_ptr
                mov     rax, r15
                shr     rax, 0Ah
                mov     ecx, 7Fh
                bsr     rcx, rax
                xor     rcx, 0FFFFFFFFFFFFFFC0h
                add     rcx, 41h ; 'A'
                cmp     rcx, 7
                mov     eax, 7
                cmovnb  rcx, rax
                mov     eax, ecx
                lea     rcx, ds:1[rax*4]
                mov     r8, [rbx+240h]
                mov     rax, [rbx+1E8h]
                mov     r9, [rbx+1F8h]
                and     r13d, 1
                mov     r10, [rbx+200h]
                mov     rbp, [rbx+208h]
                movq    xmm0, r15
                pshufd  xmm0, xmm0, 44h ; 'D'
                cmp     rax, 1
                jz      loc_92661
                cmp     rax, 2
                movdqa  xmm1, [rsp+0BB8h+var_B68]
                jnz     loc_926F7
                mov     [rsp+0BB8h+var_B78], rcx
                mov     rax, [rbx+1F0h]
                mov     rdi, [rbx+220h]
                add     rax, 0FFFFFFFFFFFFFFFEh
                cmp     rax, 3
                setb    al
                test    rdi, rdi
                setz    cl
                or      cl, al
                cmp     cl, 1
                jnz     loc_9268F
                jmp     loc_926EB
; ---------------------------------------------------------------------------

loc_925FD:                              ; CODE XREF: sub_902F0+17F2↑j
                mov     edi, 18h        ; size
                call    cs:malloc_ptr
                test    rax, rax
                jz      loc_943B8
                mov     qword ptr [rax], 0
                mov     r15, rax
                mov     word ptr [rax+10h], 600h
                mov     r14, [r12]
                test    r14, r14
                jz      short loc_92650
                mov     rbx, [r12+8]
                mov     rax, [rbx]
                test    rax, rax
                jz      short loc_9263C
                mov     rdi, r14
                call    rax

loc_9263C:                              ; CODE XREF: sub_902F0+2345↑j
                cmp     qword ptr [rbx+8], 0
                mov     rbx, [rsp+0BB8h+var_BB8]
                jz      short loc_92650
                mov     rdi, r14        ; ptr
                call    cs:free_ptr

loc_92650:                              ; CODE XREF: sub_902F0+2338↑j
                                        ; sub_902F0+2355↑j
                mov     rdi, r12        ; ptr
                call    cs:free_ptr
                mov     r14, r15
                jmp     loc_91B19
; ---------------------------------------------------------------------------

loc_92661:                              ; CODE XREF: sub_902F0+22C3↑j
                mov     [rsp+0BB8h+var_B78], rcx
                mov     rax, [rbx+1F0h]
                mov     rdi, [rbx+220h]
                add     rax, 0FFFFFFFFFFFFFFFEh
                cmp     rax, 3
                setb    al
                test    rdi, rdi
                setz    cl
                or      cl, al
                movdqa  xmm1, [rsp+0BB8h+var_B68]
                jnz     short loc_926EB

loc_9268F:                              ; CODE XREF: sub_902F0+2302↑j
                mov     r15, [rbx+238h]
                test    r15b, 1
                jz      loc_928B6
                shr     r15, 5
                mov     rax, [rbx+230h]
                add     rax, r15
                jz      short loc_926EB
                sub     rdi, r15        ; ptr
                movdqa  [rsp+0BB8h+var_AA8], xmm0
                mov     [rsp+0BB8h+var_B88], r8
                mov     r15, r9
                mov     [rsp+0BB8h+var_B50], r10
                call    cs:free_ptr
                mov     r10, [rsp+0BB8h+var_B50]
                mov     r9, r15
                mov     r8, [rsp+0BB8h+var_B88]
                movdqa  xmm1, [rsp+0BB8h+var_B68]
                movdqa  xmm0, [rsp+0BB8h+var_AA8]

loc_926EB:                              ; CODE XREF: sub_902F0+2308↑j
                                        ; sub_902F0+239D↑j ...
                mov     rdx, [rsp+0BB8h+var_B70]
                mov     rcx, [rsp+0BB8h+var_B78]
                jmp     short loc_926FC
; ---------------------------------------------------------------------------

loc_926F7:                              ; CODE XREF: sub_902F0+22D3↑j
                mov     rdx, [rsp+0BB8h+var_B70]

loc_926FC:                              ; CODE XREF: sub_902F0+2405↑j
                movzx   esi, byte ptr [rsp+0BB8h+var_BB0]

loc_92701:                              ; CODE XREF: sub_902F0+EA5↑j
                                        ; sub_902F0+21A3↑j ...
                mov     qword ptr [rbx+1E8h], 2
                mov     [rbx+1F0h], r13
                mov     [rbx+1F8h], r9
                mov     [rbx+200h], r10
                mov     [rbx+208h], rbp
                movdqu  xmmword ptr [rbx+210h], xmm1
                mov     [rbx+220h], r14
                movdqa  [rsp+0BB8h+var_AA8], xmm0
                movdqu  xmmword ptr [rbx+228h], xmm0
                mov     [rsp+0BB8h+var_B78], rcx
                mov     [rbx+238h], rcx
                mov     [rbx+240h], r8
                mov     [rbx+248h], sil
                mov     eax, dword ptr [rsp+0BB8h+var_578]
                mov     ecx, dword ptr [rsp+0BB8h+var_578+3]
                mov     [rdx+3], ecx
                mov     [rdx], eax
                mov     r13, [rsp+0BB8h+var_BA8]

loc_9277A:                              ; CODE XREF: sub_902F0+DCF↑j
                lea     rdi, [rsp+0BB8h+dest]
                mov     rsi, [rsp+0BB8h+var_B98]
                mov     rdx, r13
                call    sub_724E0
                mov     rax, qword ptr [rsp+0BB8h+dest]
                cmp     rax, 6
                jz      short loc_927BE
                cmp     eax, 5
                jz      short loc_927BE
                cmp     eax, 4
                jnz     short loc_92815
                mov     r14, qword ptr [rsp+0BB8h+dest+8]
                mov     eax, r14d
                and     eax, 3
                cmp     eax, 1
                jz      loc_9286D

loc_927BE:                              ; CODE XREF: sub_902F0+24AB↑j
                                        ; sub_902F0+24B0↑j
                mov     rax, [rbx+1E8h]
                test    rax, rax
                jz      short loc_927D9

loc_927CA:                              ; CODE XREF: sub_902F0+2557↓j
                                        ; sub_902F0+2572↓j ...
                cmp     eax, 3
                jz      short loc_927D9
                mov     rdi, [rsp+0BB8h+var_B48]
                call    sub_D9250

loc_927D9:                              ; CODE XREF: sub_902F0+24D8↑j
                                        ; sub_902F0+24DD↑j ...
                mov     r14, [r12]
                test    r14, r14
                jz      loc_90E43
                mov     rbx, [r12+8]
                mov     rax, [rbx]
                test    rax, rax
                jz      short loc_927F8
                mov     rdi, r14
                call    rax

loc_927F8:                              ; CODE XREF: sub_902F0+2501↑j
                cmp     qword ptr [rbx+8], 0
                mov     rbx, [rsp+0BB8h+var_BB8]
                jz      loc_90E43
                mov     rdi, r14        ; ptr
                call    cs:free_ptr
                jmp     loc_90E43
; ---------------------------------------------------------------------------

loc_92815:                              ; CODE XREF: sub_902F0+24B5↑j
                cmp     eax, 3
                jnz     short loc_9284B
                mov     rdi, qword ptr [rsp+0BB8h+var_858]
                mov     rax, qword ptr [rsp+0BB8h+dest+8]
                mov     rsi, [rsp+0BB8h+n]
                mov     rdx, [rsp+0BB8h+n+8]
                call    qword ptr [rax+20h]
                mov     rax, [rbx+1E8h]
                test    rax, rax
                jnz     short loc_927CA
                jmp     short loc_927D9
; ---------------------------------------------------------------------------

loc_9284B:                              ; CODE XREF: sub_902F0+2528↑j
                lea     rdi, [rsp+0BB8h+dest]
                call    sub_D55E0
                mov     rax, [rbx+1E8h]
                test    rax, rax
                jnz     loc_927CA
                jmp     loc_927D9
; ---------------------------------------------------------------------------

loc_9286D:                              ; CODE XREF: sub_902F0+24C8↑j
                mov     r15, [r14-1]
                mov     rbx, [r14+7]
                mov     rax, [rbx]
                test    rax, rax
                jz      short loc_92882
                mov     rdi, r15
                call    rax

loc_92882:                              ; CODE XREF: sub_902F0+258B↑j
                cmp     qword ptr [rbx+8], 0
                mov     rbx, cs:free_ptr
                jz      short loc_92895
                mov     rdi, r15        ; ptr
                call    rbx ; __imp_free

loc_92895:                              ; CODE XREF: sub_902F0+259E↑j
                dec     r14
                mov     rdi, r14        ; ptr
                call    rbx ; __imp_free
                mov     rbx, [rsp+0BB8h+var_BB8]
                mov     rax, [rbx+1E8h]
                test    rax, rax
                jnz     loc_927CA
                jmp     loc_927D9
; ---------------------------------------------------------------------------

loc_928B6:                              ; CODE XREF: sub_902F0+23AA↑j
                lock dec qword ptr [r15+20h]
                movzx   esi, byte ptr [rsp+0BB8h+var_BB0]
                jnz     loc_92489
                mov     [rsp+0BB8h+var_B50], r10
                mov     [rsp+0BB8h+var_B40], r9
                mov     [rsp+0BB8h+var_B88], r8
                movdqa  [rsp+0BB8h+var_AA8], xmm0
                mov     rax, [r15+20h]
                cmp     qword ptr [r15], 0
                mov     rax, cs:free_ptr
                jz      short loc_92900
                mov     rdi, [r15+8]    ; ptr
                call    cs:free_ptr
                mov     rax, cs:free_ptr

loc_92900:                              ; CODE XREF: sub_902F0+25FD↑j
                mov     rdi, r15        ; ptr
                call    rax ; __imp_free
                mov     rdx, [rsp+0BB8h+var_B70]
                movdqa  xmm0, [rsp+0BB8h+var_AA8]
                mov     rcx, [rsp+0BB8h+var_B78]
                movzx   esi, byte ptr [rsp+0BB8h+var_BB0]
                movdqa  xmm1, [rsp+0BB8h+var_B68]
                mov     r8, [rsp+0BB8h+var_B88]
                mov     r9, [rsp+0BB8h+var_B40]
                mov     r10, [rsp+0BB8h+var_B50]
                jmp     loc_92701
; ---------------------------------------------------------------------------

loc_92937:                              ; CODE XREF: sub_902F0+19B0↑j
                                        ; DATA XREF: .rodata:jpt_91CA0↓o
                mov     rbx, qword ptr [rsp+0BB8h+var_578+8] ; jumptable 0000000000091CA0 case 4
                mov     edi, 18h        ; size
                mov     r15, cs:malloc_ptr
                call    r15 ; malloc
                test    rax, rax
                jz      loc_943B8
                mov     r14, rax
                mov     qword ptr [rax], 0
                mov     byte ptr [rax+10h], 8
                mov     edi, 8          ; size
                call    r15 ; malloc
                test    rax, rax
                jz      loc_94493
                mov     [rax], rbx
                mov     [r14], rax
                lea     rax, off_210C6F30
                mov     [r14+8], rax
                mov     rdi, qword ptr [rsp+0BB8h+var_B18]
                mov     esi, dword ptr [rsp+0BB8h+var_B08]
                mov     rdx, r14
                call    sub_D6A30
                mov     rbx, [rsp+0BB8h+var_BB8]
                jmp     loc_90E4C       ; jumptable 0000000000091CA0 case 5
; ---------------------------------------------------------------------------

def_91CA0:                              ; CODE XREF: sub_902F0+199C↑j
                lea     rcx, [rsp+0BB8h+var_578+8] ; jumptable 0000000000091CA0 default case
                mov     rax, [rcx+50h]
                lea     rdx, [rsp+0BB8h+var_2E0]
                mov     [rdx+50h], rax
                movups  xmm0, xmmword ptr [rcx+40h]
                movups  xmmword ptr [rdx+40h], xmm0
                movdqu  xmm0, xmmword ptr [rcx]
                movdqu  xmm1, xmmword ptr [rcx+10h]
                movdqu  xmm2, xmmword ptr [rcx+20h]
                movdqu  xmm3, xmmword ptr [rcx+30h]
                movdqu  xmmword ptr [rdx+30h], xmm3
                movdqu  xmmword ptr [rdx+20h], xmm2
                movdqu  xmmword ptr [rdx+10h], xmm1
                movdqu  xmmword ptr [rdx], xmm0
                mov     [rsp+0BB8h+var_2E8], r15
                mov     r14, [rsp+0BB8h+var_B28]
                mov     [rsp+0BB8h+var_B28], 0
                test    r14, r14
                jz      loc_92FDD
                mov     rax, [rcx+50h]
                mov     qword ptr [rsp+0BB8h+var_948], rax
                movups  xmm0, xmmword ptr [rcx+40h]
                movaps  [rsp+0BB8h+var_958], xmm0
                movups  xmm0, xmmword ptr [rcx]
                movups  xmm1, xmmword ptr [rcx+10h]
                movups  xmm2, xmmword ptr [rcx+20h]
                movups  xmm3, xmmword ptr [rcx+30h]
                movaps  [rsp+0BB8h+var_968], xmm3
                movaps  [rsp+0BB8h+var_978], xmm2
                movaps  [rsp+0BB8h+var_988], xmm1
                movaps  [rsp+0BB8h+var_998], xmm0
                movzx   eax, byte ptr [r14+0A8h]
                test    al, al
                jnz     short loc_92A73
                mov     al, 1
                xchg    al, [r14+70h]
                test    al, al
                jz      loc_9383B

loc_92A73:                              ; CODE XREF: sub_902F0+2773↑j
                mov     rax, qword ptr [rsp+0BB8h+var_948]
                mov     [rsp+0BB8h+var_A08], rax
                movaps  xmm0, [rsp+0BB8h+var_958]
                movaps  [rsp+0BB8h+var_A18], xmm0
                movdqa  xmm0, [rsp+0BB8h+var_998]
                movdqa  xmm1, [rsp+0BB8h+var_988]
                movdqa  xmm2, [rsp+0BB8h+var_978]
                movdqa  xmm3, [rsp+0BB8h+var_968]
                movdqa  [rsp+0BB8h+var_A28], xmm3
                movdqa  [rsp+0BB8h+var_A38], xmm2
                movdqa  [rsp+0BB8h+var_A48], xmm1
                movdqa  [rsp+0BB8h+var_A58], xmm0

loc_92ADB:                              ; CODE XREF: sub_902F0+35C5↓j
                                        ; sub_902F0+35D3↓j ...
                mov     al, 1
                xchg    al, [r14+0A8h]
                mov     al, 1
                xchg    al, [r14+88h]
                test    al, al
                jnz     short loc_92B18
                mov     rax, [r14+78h]
                mov     rdi, [r14+80h]
                mov     qword ptr [r14+78h], 0
                mov     ecx, 0
                xchg    cl, [r14+88h]
                test    rax, rax
                jz      short loc_92B18
                call    qword ptr [rax+8]

loc_92B18:                              ; CODE XREF: sub_902F0+27FF↑j
                                        ; sub_902F0+2823↑j
                mov     al, 1
                xchg    al, [r14+0A0h]
                test    al, al
                jz      loc_9300D
                lock dec qword ptr [r14]
                jnz     loc_93041

loc_92B33:                              ; CODE XREF: sub_902F0+2D4B↓j
                mov     rdi, r14        ; ptr
                call    sub_D5580
                cmp     r15, 3
                jz      loc_930AD
                jmp     loc_93047
; ---------------------------------------------------------------------------

loc_92B4A:                              ; CODE XREF: sub_902F0+1660↑j
                mov     r15, [rbx+168h]
                mov     r12, [rbx+170h]
                mov     r14, r12
                shr     r14, 8
                mov     rax, [rbx+1E8h]
                cmp     rax, 1
                jnz     short loc_92BB3
                jmp     short loc_92BBC
; ---------------------------------------------------------------------------

loc_92B6E:                              ; CODE XREF: sub_902F0+221B↑j
                mov     r15, [rbx+168h]
                mov     r12, [rbx+170h]
                mov     r14, r12
                shr     r14, 8
                mov     rax, [rbx+1E8h]
                cmp     rax, 1
                jnz     loc_92C2F
                jmp     loc_92C38
; ---------------------------------------------------------------------------

loc_92B99:                              ; CODE XREF: sub_902F0+166A↑j
                mov     r14, r12
                shr     r14, 8
                mov     r15d, 2
                mov     rax, [rbx+1E8h]
                cmp     rax, 1
                jz      short loc_92BBC

loc_92BB3:                              ; CODE XREF: sub_902F0+1684↑j
                                        ; sub_902F0+287A↑j
                cmp     eax, 2
                jnz     loc_92DB4

loc_92BBC:                              ; CODE XREF: sub_902F0+168A↑j
                                        ; sub_902F0+287C↑j ...
                mov     rcx, [rbx+1F0h]
                mov     rax, [rbx+220h]
                add     rcx, 0FFFFFFFFFFFFFFFEh
                cmp     rcx, 3
                setb    cl
                test    rax, rax
                setz    dl
                or      dl, cl
                jnz     loc_92DB4
                mov     rdi, [rbx+238h]
                test    dil, 1
                jz      loc_92D82
                shr     rdi, 5
                mov     rcx, [rbx+230h]
                add     rcx, rdi
                jz      loc_92DB4
                mov     ebp, esi
                sub     rax, rdi
                mov     rdi, rax
                jmp     loc_92DAC
; ---------------------------------------------------------------------------

loc_92C15:                              ; CODE XREF: sub_902F0+2225↑j
                mov     r14, r12
                shr     r14, 8
                mov     r15d, 2
                mov     rax, [rbx+1E8h]
                cmp     rax, 1
                jz      short loc_92C38

loc_92C2F:                              ; CODE XREF: sub_902F0+223F↑j
                                        ; sub_902F0+289E↑j
                cmp     eax, 2
                jnz     loc_92E5D

loc_92C38:                              ; CODE XREF: sub_902F0+2245↑j
                                        ; sub_902F0+28A4↑j ...
                mov     rcx, [rbx+1F0h]
                mov     rax, [rbx+220h]
                add     rcx, 0FFFFFFFFFFFFFFFEh
                cmp     rcx, 3
                setb    cl
                test    rax, rax
                setz    dl
                or      dl, cl
                jnz     loc_92E5D
                mov     rdi, [rbx+238h]
                test    dil, 1
                jz      loc_92E2B
                shr     rdi, 5
                mov     rcx, [rbx+230h]
                add     rcx, rdi
                jz      loc_92E5D
                mov     ebp, esi
                sub     rax, rdi
                mov     rdi, rax
                jmp     loc_92E55
; ---------------------------------------------------------------------------

loc_92C91:                              ; CODE XREF: sub_902F0+2163↑j
                mov     rdx, rax
                xor     ebp, ebp
                mov     [rsp+0BB8h+var_A70], r12
                jmp     loc_91D1A
; ---------------------------------------------------------------------------

loc_92CA3:                              ; CODE XREF: sub_902F0+21F0↑j
                lock dec qword ptr [rdi+20h]
                jnz     short loc_92CD5
                mov     ebp, esi
                mov     rax, [rdi+20h]
                cmp     qword ptr [rdi], 0
                jz      short loc_92CCD
                mov     rax, [rdi+8]
                mov     rbx, rdi
                mov     rdi, rax        ; ptr
                call    cs:free_ptr
                mov     rdi, rbx        ; ptr
                mov     rbx, [rsp+0BB8h+var_BB8]

loc_92CCD:                              ; CODE XREF: sub_902F0+2212↑j
                                        ; sub_902F0+29C4↑j
                call    cs:free_ptr
                mov     esi, ebp

loc_92CD5:                              ; CODE XREF: sub_902F0+21B8↑j
                                        ; sub_902F0+21DF↑j ...
                mov     qword ptr [rbx+1E8h], 3
                mov     byte ptr [rsp+0BB8h+var_B50], sil
                mov     r14, qword ptr [rsp+0BB8h+var_558+8]
                test    r14, r14
                jnz     loc_92EE6
                jmp     loc_936A6
; ---------------------------------------------------------------------------

loc_92CFB:                              ; CODE XREF: sub_902F0+19BA↑j
                lea     rdi, [rsp+0BB8h+dest]
                lea     rsi, [rsp+0BB8h+var_B18]
                lea     rdx, [rsp+0BB8h+var_578+8]
                call    sub_D5FB0
                cmp     byte ptr [rsp+0BB8h+var_858], 2
                jz      loc_930AD

loc_92D26:                              ; CODE XREF: sub_902F0+19E3↑j
                mov     rbx, qword ptr [rsp+0BB8h+dest]
                mov     r14, qword ptr [rsp+0BB8h+dest+8]
                test    rbx, rbx
                jz      loc_947A6
                mov     r15, [rsp+0BB8h+n]
                mov     r12, [rsp+0BB8h+n+8]
                mov     rax, [rsp+0BB8h+var_BB8]
                mov     rax, [rax+1E8h]
                dec     rax
                cmp     rax, 2
                jnb     short loc_92D6D
                mov     rdi, [rsp+0BB8h+var_B48]
                call    sub_D9250

loc_92D6D:                              ; CODE XREF: sub_902F0+2A71↑j
                mov     rdi, r12
                mov     rsi, r14
                mov     rdx, r15
                call    qword ptr [rbx+20h]
                mov     rbx, [rsp+0BB8h+var_BB8]
                jmp     loc_90E4C       ; jumptable 0000000000091CA0 case 5
; ---------------------------------------------------------------------------

loc_92D82:                              ; CODE XREF: sub_902F0+28FE↑j
                lock dec qword ptr [rdi+20h]
                jnz     short loc_92DB4
                mov     ebp, esi
                mov     rax, [rdi+20h]
                cmp     qword ptr [rdi], 0
                jz      short loc_92DAC
                mov     rax, [rdi+8]
                mov     rbx, rdi
                mov     rdi, rax        ; ptr
                call    cs:free_ptr
                mov     rdi, rbx        ; ptr
                mov     rbx, [rsp+0BB8h+var_BB8]

loc_92DAC:                              ; CODE XREF: sub_902F0+2920↑j
                                        ; sub_902F0+2AA3↑j
                call    cs:free_ptr
                mov     esi, ebp

loc_92DB4:                              ; CODE XREF: sub_902F0+28C6↑j
                                        ; sub_902F0+28ED↑j ...
                mov     qword ptr [rbx+1E8h], 1
                mov     [rbx+1F0h], r15
                mov     [rbx+1F8h], r12b
                mov     [rbx+1F9h], r14d
                mov     rax, r14
                shr     rax, 30h
                mov     [rbx+1FFh], al
                shr     r14, 20h
                mov     [rbx+1FDh], r14w
                mov     qword ptr [rbx+200h], 0
                mov     rax, [rsp+0BB8h+var_A80]
                pxor    xmm0, xmm0
                movdqu  xmmword ptr [rax], xmm0
                mov     qword ptr [rax+10h], 0
                mov     qword ptr [rbx+240h], 0
                mov     byte ptr [rbx+248h], 0
                or      sil, 1
                jmp     loc_92ECB
; ---------------------------------------------------------------------------

loc_92E2B:                              ; CODE XREF: sub_902F0+297A↑j
                lock dec qword ptr [rdi+20h]
                jnz     short loc_92E5D
                mov     ebp, esi
                mov     rax, [rdi+20h]
                cmp     qword ptr [rdi], 0
                jz      short loc_92E55
                mov     rax, [rdi+8]
                mov     rbx, rdi
                mov     rdi, rax        ; ptr
                call    cs:free_ptr
                mov     rdi, rbx        ; ptr
                mov     rbx, [rsp+0BB8h+var_BB8]

loc_92E55:                              ; CODE XREF: sub_902F0+299C↑j
                                        ; sub_902F0+2B4C↑j
                call    cs:free_ptr
                mov     esi, ebp

loc_92E5D:                              ; CODE XREF: sub_902F0+2942↑j
                                        ; sub_902F0+2969↑j ...
                mov     qword ptr [rbx+1E8h], 2
                mov     [rbx+1F0h], r15
                mov     [rbx+1F8h], r12b
                mov     [rbx+1F9h], r14d
                mov     rax, r14
                shr     rax, 30h
                mov     [rbx+1FFh], al
                shr     r14, 20h
                mov     [rbx+1FDh], r14w
                mov     qword ptr [rbx+200h], 0
                mov     rax, [rsp+0BB8h+var_A80]
                pxor    xmm0, xmm0
                movdqu  xmmword ptr [rax], xmm0
                mov     qword ptr [rax+10h], 0
                mov     qword ptr [rbx+240h], 0
                mov     byte ptr [rbx+248h], 0

loc_92ECB:                              ; CODE XREF: sub_902F0+2B36↑j
                mov     r12, [rsp+0BB8h+var_BB0]
                mov     byte ptr [rsp+0BB8h+var_B50], sil
                mov     r14, qword ptr [rsp+0BB8h+var_558+8]
                test    r14, r14
                jz      loc_936A6

loc_92EE6:                              ; CODE XREF: sub_902F0+2A00↑j
                lea     rdi, [rsp+0BB8h+var_578]
                lea     rsi, qword_10037A0
                call    sub_D70F0
                movzx   edx, ax
                movzx   ecx, [rsp+0BB8h+var_520]
                and     edx, ecx
                mov     r8, [rsp+0BB8h+var_528]
                mov     rsi, qword ptr [rsp+0BB8h+var_558]
                mov     r9, [rsp+0BB8h+var_530]
                xor     r10d, r10d
                jmp     short loc_92F36
; ---------------------------------------------------------------------------
                align 10h

loc_92F30:                              ; CODE XREF: sub_902F0+2C8C↓j
                                        ; sub_902F0+2CA1↓j ...
                inc     r10
                inc     rdx

loc_92F36:                              ; CODE XREF: sub_902F0+2C32↑j
                mov     rdi, rdx
                nop     dword ptr [rax+00000000h]

loc_92F40:                              ; CODE XREF: sub_902F0+2C5B↓j
                mov     rdx, rdi
                mov     edi, 0
                cmp     rdx, r8
                jnb     short loc_92F40
                movzx   edi, word ptr [r9+rdx*4]
                cmp     rdi, 0FFFFh
                jz      short loc_92FD2
                movzx   r11d, word ptr [r9+rdx*4+2]
                mov     ebx, r11d
                and     ebx, ecx
                mov     r15d, edx
                sub     r15d, ebx
                and     r15d, ecx
                cmp     r10, r15
                ja      short loc_92FD2
                cmp     r11w, ax
                mov     rbx, [rsp+0BB8h+var_BB8]
                jnz     short loc_92F30
                cmp     r14, rdi
                jbe     loc_948BB
                imul    rdi, 68h ; 'h'
                cmp     qword ptr [rsi+rdi+40h], 0
                jnz     short loc_92F30
                lea     r11, [rsi+rdi]
                add     r11, 40h ; '@'
                cmp     byte ptr [r11+8], 43h ; 'C'
                jnz     short loc_92F30
                lea     rax, [rsi+rdi]
                movzx   ecx, byte ptr [rsi+rdi]
                mov     [rsp+0BB8h+var_B99], cl
                test    cl, 1
                jz      loc_93126
                mov     rcx, [rax+10h]
                mov     [rsp+0BB8h+var_A88], rcx
                mov     ecx, 1
                mov     [rsp+0BB8h+var_B88], rcx
                jmp     loc_9312F
; ---------------------------------------------------------------------------

loc_92FD2:                              ; CODE XREF: sub_902F0+2C69↑j
                                        ; sub_902F0+2C82↑j
                xor     eax, eax
                mov     rbx, [rsp+0BB8h+var_BB8]
                jmp     loc_936A8
; ---------------------------------------------------------------------------

loc_92FDD:                              ; CODE XREF: sub_902F0+271C↑j
                mov     qword ptr [rsp+0BB8h+dest], 3
                lea     rdi, [rsp+0BB8h+var_2E8]
                call    sub_D55E0
                jmp     loc_930F1
; ---------------------------------------------------------------------------

loc_92FFB:                              ; CODE XREF: sub_902F0+1933↑j
                test    r14, r14
                jz      loc_93822
                xor     edx, edx
                xor     ebp, ebp
                jmp     loc_91D1A
; ---------------------------------------------------------------------------

loc_9300D:                              ; CODE XREF: sub_902F0+2833↑j
                mov     rax, [r14+90h]
                mov     rdi, [r14+98h]
                mov     qword ptr [r14+90h], 0
                test    rax, rax
                jz      short loc_9302E
                call    qword ptr [rax+18h]

loc_9302E:                              ; CODE XREF: sub_902F0+2D39↑j
                xor     eax, eax
                xchg    al, [r14+0A0h]
                lock dec qword ptr [r14]
                jz      loc_92B33

loc_93041:                              ; CODE XREF: sub_902F0+283D↑j
                cmp     r15, 3
                jz      short loc_930AD

loc_93047:                              ; CODE XREF: sub_902F0+2855↑j
                mov     rax, [rsp+0BB8h+var_A08]
                lea     rcx, [rsp+0BB8h+n]
                mov     [rcx+48h], rax
                movaps  xmm0, [rsp+0BB8h+var_A18]
                movups  xmmword ptr [rcx+38h], xmm0
                movdqa  xmm0, [rsp+0BB8h+var_A58]
                movdqa  xmm1, [rsp+0BB8h+var_A48]
                movdqa  xmm2, [rsp+0BB8h+var_A38]
                movdqa  xmm3, [rsp+0BB8h+var_A28]
                movdqu  xmmword ptr [rcx+28h], xmm3
                movdqu  xmmword ptr [rcx+18h], xmm2
                movdqu  xmmword ptr [rcx+8], xmm1
                movdqu  xmmword ptr [rcx-8], xmm0
                mov     qword ptr [rsp+0BB8h+dest], r15
                cmp     r15, 4
                jnz     short loc_930F1

loc_930AD:                              ; CODE XREF: sub_902F0+284F↑j
                                        ; sub_902F0+2A30↑j ...
                cmp     byte ptr [rbx+2F8h], 3
                jz      short loc_930C0
                mov     rdi, [rsp+0BB8h+var_B90]
                call    sub_DAA80

loc_930C0:                              ; CODE XREF: sub_902F0+2DC4↑j
                mov     rax, [rsp+0BB8h+var_B08]
                mov     rcx, [rsp+0BB8h+var_B90]
                mov     [rcx+20h], rax
                movdqa  xmm0, xmmword ptr [rsp+0BB8h+var_B28]
                movdqa  xmm1, [rsp+0BB8h+var_B18]
                movdqu  xmmword ptr [rcx+10h], xmm1
                movdqu  xmmword ptr [rcx], xmm0
                jmp     loc_90E59
; ---------------------------------------------------------------------------

loc_930F1:                              ; CODE XREF: sub_902F0+2D06↑j
                                        ; sub_902F0+2DBB↑j
                mov     rax, [rbx+1E8h]
                dec     rax
                cmp     rax, 1
                ja      short loc_9310B
                mov     rdi, [rsp+0BB8h+var_B48]
                call    sub_D9250

loc_9310B:                              ; CODE XREF: sub_902F0+2E0F↑j
                test    r14, r14
                jz      loc_90E4C       ; jumptable 0000000000091CA0 case 5
                lea     rdi, [rsp+0BB8h+dest]
                call    sub_D55E0
                jmp     loc_90E4C       ; jumptable 0000000000091CA0 case 5
; ---------------------------------------------------------------------------

loc_93126:                              ; CODE XREF: sub_902F0+2CC1↑j
                mov     [rsp+0BB8h+var_B88], 0

loc_9312F:                              ; CODE XREF: sub_902F0+2CDD↑j
                mov     [rsp+0BB8h+var_8B8], rax
                add     rax, 18h
                mov     [rsp+0BB8h+var_A98], rax
                mov     rax, qword ptr [rsp+0BB8h+var_548+8]
                mov     [rsp+0BB8h+var_8B0], rax
                mov     rax, [rsp+0BB8h+var_538]
                mov     [rsp+0BB8h+var_A90], rax
                xor     ecx, ecx
                jmp     short loc_9318A
; ---------------------------------------------------------------------------
                align 10h

loc_93170:                              ; CODE XREF: sub_902F0+30F7↓j
                                        ; sub_902F0+3113↓j
                mov     ecx, 1
                cmp     byte ptr [rsp+0BB8h+var_B68], 0
                mov     r13, [rsp+0BB8h+var_BA8]
                mov     r12, [rsp+0BB8h+var_BB0]
                jnz     loc_936A6

loc_9318A:                              ; CODE XREF: sub_902F0+2E75↑j
                test    cl, 1
                jz      short loc_931E0
                mov     rdi, [rsp+0BB8h+var_B40]
                cmp     rdi, [rsp+0BB8h+var_A90]
                jnb     loc_948E6
                lea     rax, [rdi+rdi*8]
                mov     rdx, [rsp+0BB8h+var_8B0]
                lea     rax, [rdx+rax*8]
                mov     dl, 1
                cmp     rcx, [rsp+0BB8h+var_B88]
                jnz     short loc_9320E
                cmp     rdi, [rsp+0BB8h+var_A88]
                jnz     short loc_9320E
                mov     ecx, 2
                mov     [rsp+0BB8h+var_B88], rcx
                mov     rdi, [rsp+0BB8h+var_A88]
                jmp     short loc_9321A
; ---------------------------------------------------------------------------
                align 20h

loc_931E0:                              ; CODE XREF: sub_902F0+2E9D↑j
                cmp     [rsp+0BB8h+var_B88], 0
                jz      short loc_93239
                test    [rsp+0BB8h+var_B99], 1
                mov     rax, [rsp+0BB8h+var_8B8]
                jz      loc_94776
                mov     rax, [rax+8]
                mov     [rsp+0BB8h+var_B40], rax
                mov     dword ptr [rsp+0BB8h+var_B68], 0
                jmp     short loc_93249
; ---------------------------------------------------------------------------

loc_9320E:                              ; CODE XREF: sub_902F0+2EC9↑j
                                        ; sub_902F0+2ED3↑j
                cmp     dword ptr [rax+10h], 1
                jnz     short loc_9321A
                mov     rdi, [rax+18h]
                xor     edx, edx

loc_9321A:                              ; CODE XREF: sub_902F0+2EE7↑j
                                        ; sub_902F0+2F22↑j
                mov     dword ptr [rsp+0BB8h+var_B68], edx
                mov     [rsp+0BB8h+var_B40], rdi
                add     rax, 20h ; ' '
                mov     rbp, [rax+8]
                mov     r14, [rax+10h]
                test    r14, r14
                jnz     short loc_93262
                jmp     loc_933ED
; ---------------------------------------------------------------------------

loc_93239:                              ; CODE XREF: sub_902F0+2EF6↑j
                mov     al, 1
                mov     dword ptr [rsp+0BB8h+var_B68], eax
                mov     eax, 2
                mov     [rsp+0BB8h+var_B88], rax

loc_93249:                              ; CODE XREF: sub_902F0+2F1C↑j
                mov     rax, [rsp+0BB8h+var_A98]
                mov     rbp, [rax+8]
                mov     r14, [rax+10h]
                test    r14, r14
                jz      loc_933ED

loc_93262:                              ; CODE XREF: sub_902F0+2F42↑j
                cmp     r14, 8
                jnb     short loc_93272
                xor     edx, edx
                mov     rcx, rbp
                jmp     loc_933B5
; ---------------------------------------------------------------------------

loc_93272:                              ; CODE XREF: sub_902F0+2F76↑j
                cmp     r14, 20h ; ' '
                jnb     short loc_93281
                xor     eax, eax
                xor     edx, edx
                jmp     loc_9332E
; ---------------------------------------------------------------------------

loc_93281:                              ; CODE XREF: sub_902F0+2F86↑j
                mov     rax, r14
                and     rax, 0FFFFFFFFFFFFFFE0h
                pxor    xmm0, xmm0
                xor     ecx, ecx
                pxor    xmm1, xmm1
                movdqa  xmm7, cs:xmmword_1000150
                movdqa  xmm8, cs:xmmword_1000160
                movdqa  xmm9, cs:xmmword_10000E0
                nop     dword ptr [rax+00h]

loc_932B0:                              ; CODE XREF: sub_902F0+3017↓j
                movdqu  xmm2, xmmword ptr [rbp+rcx+0]
                movdqu  xmm3, xmmword ptr [rbp+rcx+10h]
                movdqa  xmm4, xmm2
                paddb   xmm4, xmm7
                movdqa  xmm5, xmm3
                paddb   xmm5, xmm7
                movdqa  xmm6, xmm4
                pminub  xmm6, xmm8
                pcmpeqb xmm6, xmm4
                movdqa  xmm4, xmm5
                pminub  xmm4, xmm8
                pcmpeqb xmm4, xmm5
                pcmpeqb xmm2, xmm9
                pandn   xmm2, xmm6
                por     xmm0, xmm2
                pcmpeqb xmm3, xmm9
                pandn   xmm3, xmm4
                por     xmm1, xmm3
                add     rcx, 20h ; ' '
                cmp     rax, rcx
                jnz     short loc_932B0
                por     xmm1, xmm0
                psllw   xmm1, 7
                pmovmskb ecx, xmm1
                test    ecx, ecx
                setnz   dl
                cmp     r14, rax
                jz      loc_933E4
                test    r14b, 18h
                jz      loc_933AF

loc_9332E:                              ; CODE XREF: sub_902F0+2F8C↑j
                mov     rsi, r14
                and     rsi, 0FFFFFFFFFFFFFFF8h
                lea     rcx, [rsi+rbp]
                movzx   edx, dl
                movd    xmm0, edx
                movdqa  xmm4, cs:xmmword_1000170
                movdqa  xmm5, cs:xmmword_1000180
                movdqa  xmm6, cs:xmmword_1000110
                pcmpeqd xmm7, xmm7
                nop     dword ptr [rax+00h]

loc_93360:                              ; CODE XREF: sub_902F0+30A5↓j
                movq    xmm1, qword ptr [rbp+rax+0]
                movdqa  xmm2, xmm1
                paddb   xmm2, xmm4
                movdqa  xmm3, xmm2
                pmaxub  xmm3, xmm5
                pcmpeqb xmm3, xmm2
                pcmpeqb xmm1, xmm6
                por     xmm1, xmm3
                punpcklbw xmm1, xmm1
                pxor    xmm1, xmm7
                por     xmm0, xmm1
                add     rax, 8
                cmp     rsi, rax
                jnz     short loc_93360
                psllw   xmm0, 7
                pmovmskb eax, xmm0
                test    eax, 5555h
                setnz   dl
                cmp     r14, rsi
                jnz     short loc_933B5
                jmp     short loc_933E4
; ---------------------------------------------------------------------------

loc_933AF:                              ; CODE XREF: sub_902F0+3038↑j
                add     rax, rbp
                mov     rcx, rax

loc_933B5:                              ; CODE XREF: sub_902F0+2F7D↑j
                                        ; sub_902F0+30BB↑j
                lea     rax, [r14+rbp]
                nop     dword ptr [rax+00000000h]

loc_933C0:                              ; CODE XREF: sub_902F0+30F2↓j
                movzx   esi, byte ptr [rcx]
                inc     rcx
                lea     edi, [rsi-7Fh]
                cmp     dil, 0A1h
                setb    dil
                cmp     sil, 9
                setnz   sil
                and     sil, dil
                or      dl, sil
                cmp     rcx, rax
                jnz     short loc_933C0

loc_933E4:                              ; CODE XREF: sub_902F0+302E↑j
                                        ; sub_902F0+30BD↑j
                test    dl, 1
                jnz     loc_93170

loc_933ED:                              ; CODE XREF: sub_902F0+2F44↑j
                                        ; sub_902F0+2F6C↑j
                xor     r15d, r15d
                xor     r12d, r12d
                jmp     short loc_93409
; ---------------------------------------------------------------------------
                align 20h

loc_93400:                              ; CODE XREF: sub_902F0+32B8↓j
                                        ; sub_902F0+32D2↓j ...
                test    r13b, r13b
                jnz     loc_93170

loc_93409:                              ; CODE XREF: sub_902F0+3103↑j
                mov     rdi, r12
                mov     r13b, 1
                cmp     r14, r15
                jnb     short loc_9342C
                mov     r12, rdi
                jmp     loc_93596
; ---------------------------------------------------------------------------
                align 20h

loc_93420:                              ; CODE XREF: sub_902F0+3260↓j
                                        ; sub_902F0+3278↓j ...
                mov     r15, rax
                cmp     rax, r14
                ja      loc_9368A

loc_9342C:                              ; CODE XREF: sub_902F0+3122↑j
                mov     rcx, r14
                sub     rcx, r15
                lea     rax, [r15+rbp]
                cmp     rcx, 0Fh
                ja      short loc_93470
                cmp     r14, r15
                jz      loc_93590
                xor     esi, esi
                nop     word ptr [rax+rax+00000000h]

loc_93450:                              ; CODE XREF: sub_902F0+3170↓j
                cmp     byte ptr [rax+rsi], 2Ch ; ','
                jz      loc_93543
                inc     rsi
                cmp     rcx, rsi
                jnz     short loc_93450
                jmp     loc_93590
; ---------------------------------------------------------------------------
                align 10h

loc_93470:                              ; CODE XREF: sub_902F0+314A↑j
                lea     r8, [rax+7]
                and     r8, 0FFFFFFFFFFFFFFF8h
                mov     rdx, r8
                sub     rdx, rax
                jz      short loc_934AD
                xor     esi, esi
                db      66h, 66h, 66h, 66h, 2Eh
                nop     word ptr [rax+rax+00000000h]

loc_93490:                              ; CODE XREF: sub_902F0+31B0↓j
                cmp     byte ptr [rax+rsi], 2Ch ; ','
                jz      loc_93558
                inc     rsi
                cmp     rdx, rsi
                jnz     short loc_93490
                lea     rsi, [rcx-10h]
                cmp     rdx, rsi
                jbe     short loc_934B3
                jmp     short loc_93515
; ---------------------------------------------------------------------------

loc_934AD:                              ; CODE XREF: sub_902F0+318E↑j
                lea     rsi, [rcx-10h]
                xor     edx, edx

loc_934B3:                              ; CODE XREF: sub_902F0+31B9↑j
                mov     r9d, 8
                add     r8, r9
                nop     dword ptr [rax+00h]

loc_934C0:                              ; CODE XREF: sub_902F0+3223↓j
                mov     r9, [r8-8]
                mov     r10, r9
                mov     r12, 2C2C2C2C2C2C2C2Ch
                xor     r10, r12
                mov     r13, 101010101010100h
                mov     r11, r13
                sub     r11, r10
                or      r11, r9
                mov     r9, [r8]
                xor     r9, r12
                sub     r13, r9
                or      r13, r9
                mov     r9, 8080808080808080h
                and     r11, r9
                and     r11, r13
                cmp     r11, r9
                jnz     short loc_93515
                add     rdx, 10h
                add     r8, 10h
                cmp     rdx, rsi
                jbe     short loc_934C0

loc_93515:                              ; CODE XREF: sub_902F0+31BB↑j
                                        ; sub_902F0+3216↑j
                cmp     rcx, rdx
                jz      loc_93695
                add     rax, rdx
                mov     rcx, r14
                sub     rcx, rdx
                sub     rcx, r15
                xor     esi, esi
                mov     r13b, 1
                nop

loc_93530:                              ; CODE XREF: sub_902F0+324C↓j
                cmp     byte ptr [rax+rsi], 2Ch ; ','
                jz      short loc_93540
                inc     rsi
                cmp     rcx, rsi
                jnz     short loc_93530
                jmp     short loc_93590
; ---------------------------------------------------------------------------

loc_93540:                              ; CODE XREF: sub_902F0+3244↑j
                add     rsi, rdx

loc_93543:                              ; CODE XREF: sub_902F0+3164↑j
                lea     rax, [rsi+r15]
                inc     rax
                add     rsi, r15
                cmp     rsi, r14
                jnb     loc_93420
                jmp     short loc_9356E
; ---------------------------------------------------------------------------

loc_93558:                              ; CODE XREF: sub_902F0+31A4↑j
                mov     r13b, 1
                lea     rax, [rsi+r15]
                inc     rax
                add     rsi, r15
                cmp     rsi, r14
                jnb     loc_93420

loc_9356E:                              ; CODE XREF: sub_902F0+3266↑j
                cmp     byte ptr [rbp+rsi+0], 2Ch ; ','
                jnz     loc_93420
                xor     r13d, r13d
                mov     r12, rax
                mov     r15, rax
                jmp     short loc_93599
; ---------------------------------------------------------------------------
                align 10h

loc_93590:                              ; CODE XREF: sub_902F0+314F↑j
                                        ; sub_902F0+3172↑j ...
                mov     r12, rdi
                mov     r15, r14

loc_93596:                              ; CODE XREF: sub_902F0+3127↑j
                                        ; sub_902F0+33A0↓j
                mov     rsi, r14

loc_93599:                              ; CODE XREF: sub_902F0+3292↑j
                                        ; sub_902F0+33B1↓j
                sub     rsi, rdi
                add     rdi, rbp
                call    sub_D7B40
                cmp     rdx, 8
                jnz     loc_93400
                movzx   ecx, byte ptr [rax]
                lea     edx, [rcx-41h]
                cmp     dl, 1Ah
                setb    dl
                shl     dl, 5
                or      dl, cl
                cmp     dl, 74h ; 't'
                jnz     loc_93400
                movzx   ecx, byte ptr [rax+1]
                lea     edx, [rcx-41h]
                cmp     dl, 1Ah
                setb    dl
                shl     dl, 5
                or      dl, cl
                cmp     dl, 72h ; 'r'
                jnz     loc_93400
                movzx   ecx, byte ptr [rax+2]
                lea     edx, [rcx-41h]
                cmp     dl, 1Ah
                setb    dl
                shl     dl, 5
                or      dl, cl
                cmp     dl, 61h ; 'a'
                jnz     loc_93400
                movzx   ecx, byte ptr [rax+3]
                lea     edx, [rcx-41h]
                cmp     dl, 1Ah
                setb    dl
                shl     dl, 5
                or      dl, cl
                cmp     dl, 69h ; 'i'
                jnz     loc_93400
                movzx   ecx, byte ptr [rax+4]
                lea     edx, [rcx-41h]
                cmp     dl, 1Ah
                setb    dl
                shl     dl, 5
                or      dl, cl
                cmp     dl, 6Ch ; 'l'
                jnz     loc_93400
                movzx   ecx, byte ptr [rax+5]
                lea     edx, [rcx-41h]
                cmp     dl, 1Ah
                setb    dl
                shl     dl, 5
                or      dl, cl
                cmp     dl, 65h ; 'e'
                jnz     loc_93400
                movzx   ecx, byte ptr [rax+6]
                lea     edx, [rcx-41h]
                cmp     dl, 1Ah
                setb    dl
                shl     dl, 5
                or      dl, cl
                cmp     dl, 72h ; 'r'
                jnz     loc_93400
                movzx   eax, byte ptr [rax+7]
                lea     ecx, [rax-41h]
                cmp     cl, 1Ah
                setb    cl
                shl     cl, 5
                or      cl, al
                cmp     cl, 73h ; 's'
                jnz     loc_93400
                jmp     loc_93A60
; ---------------------------------------------------------------------------

loc_9368A:                              ; CODE XREF: sub_902F0+3136↑j
                mov     r12, rdi
                mov     r15, rax
                jmp     loc_93596
; ---------------------------------------------------------------------------

loc_93695:                              ; CODE XREF: sub_902F0+3228↑j
                mov     r12, rdi
                mov     r15, r14
                mov     rsi, r14
                mov     r13b, 1
                jmp     loc_93599
; ---------------------------------------------------------------------------

loc_936A6:                              ; CODE XREF: sub_902F0+2A06↑j
                                        ; sub_902F0+2BF0↑j ...
                xor     eax, eax

loc_936A8:                              ; CODE XREF: sub_902F0+2CE8↑j
                                        ; sub_902F0+377C↓j
                mov     [rbx+2CEh], al
                mov     rbp, qword ptr [rsp+0BB8h+var_578]
                mov     r14, qword ptr [rsp+0BB8h+var_578+8]
                mov     edx, 0C0h       ; n
                lea     rdi, [rsp+0BB8h+var_A58] ; dest
                lea     rsi, [rsp+0BB8h+var_568] ; src
                call    cs:memcpy_ptr
                cmp     rbp, 5
                jz      loc_91D30
                mov     rax, [rsp+0BB8h+var_4A8]
                mov     qword ptr [rsp+0BB8h+var_B68], rax
                mov     rax, [rsp+0BB8h+var_4A0]
                mov     [rsp+0BB8h+var_B40], rax
                cmp     rbp, 3
                jnz     loc_91EF6

loc_93707:                              ; CODE XREF: sub_902F0+1838↑j
                                        ; sub_902F0+1C00↑j
                mov     qword ptr [rsp+0BB8h+dest+8], r14
                mov     qword ptr [rsp+0BB8h+dest], 3
                mov     rdi, [rbx+300h]
                mov     rsi, [rbx+308h]
                lea     rdx, [rsp+0BB8h+dest]
                call    sub_59A00
                test    rax, rax
                jnz     loc_937FA

loc_9373F:                              ; CODE XREF: sub_902F0+1C2A↑j
                mov     byte ptr [rbx+318h], 1
                mov     rdi, [rsp+0BB8h+var_B48]
                call    sub_D9250
                mov     r15, [rbx+250h]
                mov     r12, 7FFFFFFFFFFFFFFDh
                lea     rax, [r15+r12]
                cmp     rax, 4
                jb      short loc_937E2
                lea     rax, [r12+4]
                cmp     r15, rax
                jnb     short loc_937E2
                lea     rax, [r12+3]
                cmp     r15, rax
                jz      short loc_937E2
                mov     r14, [rbx+258h]
                mov     rbx, [rbx+260h]
                test    rbx, rbx
                jz      short loc_937C6
                lea     r12, [r14+18h]
                jmp     short loc_937A9
; ---------------------------------------------------------------------------
                align 20h

loc_937A0:                              ; CODE XREF: sub_902F0+34C1↓j
                                        ; sub_902F0+34D4↓j
                add     r12, 20h ; ' '
                dec     rbx
                jz      short loc_937C6

loc_937A9:                              ; CODE XREF: sub_902F0+34A6↑j
                mov     rax, [r12-18h]
                test    rax, rax
                jz      short loc_937A0
                mov     rdi, [r12]
                mov     rsi, [r12-10h]
                mov     rdx, [r12-8]
                call    qword ptr [rax+20h]
                jmp     short loc_937A0
; ---------------------------------------------------------------------------

loc_937C6:                              ; CODE XREF: sub_902F0+34A0↑j
                                        ; sub_902F0+34B7↑j
                test    r15, r15
                mov     rbx, [rsp+0BB8h+var_BB8]
                mov     r12, 7FFFFFFFFFFFFFFDh
                jz      short loc_937E2
                mov     rdi, r14        ; ptr
                call    cs:free_ptr

loc_937E2:                              ; CODE XREF: sub_902F0+3479↑j
                                        ; sub_902F0+3483↑j ...
                lea     rax, [r12+9]
                mov     [rbx+250h], rax
                mov     byte ptr [rbx+2CFh], 2
                jmp     loc_90E59
; ---------------------------------------------------------------------------

loc_937FA:                              ; CODE XREF: sub_902F0+3449↑j
                mov     rdx, rax
                xor     ebp, ebp
                jmp     loc_91D1A
; ---------------------------------------------------------------------------

loc_93804:                              ; CODE XREF: sub_902F0+1956↑j
                lea     rdi, [rsp+0BB8h+var_AD8]
                mov     rbx, rdx
                call    sub_64B90
                mov     rdx, rbx
                mov     rbx, [rsp+0BB8h+var_BB8]
                xor     ebp, ebp
                jmp     loc_91D1A
; ---------------------------------------------------------------------------

loc_93822:                              ; CODE XREF: sub_902F0+2D0E↑j
                mov     rdi, [rsp+0BB8h+var_B48]
                call    sub_D9250
                xor     ebp, ebp
                call    sub_D6DE0
                mov     rdx, rax
                jmp     loc_91D1A
; ---------------------------------------------------------------------------

loc_9383B:                              ; CODE XREF: sub_902F0+277D↑j
                cmp     dword ptr [r14+10h], 3
                jnz     loc_948A3
                mov     [r14+10h], r15
                movaps  xmm0, [rsp+0BB8h+var_998]
                movdqa  xmm1, [rsp+0BB8h+var_988]
                movdqa  xmm2, [rsp+0BB8h+var_978]
                movdqa  xmm3, [rsp+0BB8h+var_968]
                movups  xmmword ptr [r14+18h], xmm0
                movdqu  xmmword ptr [r14+28h], xmm1
                movdqu  xmmword ptr [r14+38h], xmm2
                movdqu  xmmword ptr [r14+48h], xmm3
                movdqa  xmm0, [rsp+0BB8h+var_958]
                movdqu  xmmword ptr [r14+58h], xmm0
                mov     rax, qword ptr [rsp+0BB8h+var_948]
                mov     [r14+68h], rax
                xor     eax, eax
                xchg    al, [r14+70h]
                movzx   eax, byte ptr [r14+0A8h]
                mov     r15d, 3
                test    al, al
                jz      loc_92ADB
                mov     al, 1
                xchg    al, [r14+70h]
                test    al, al
                jnz     loc_92ADB
                mov     r15, [r14+10h]
                mov     qword ptr [r14+10h], 3
                cmp     r15, 3
                jnz     loc_93A71
                xor     eax, eax
                xchg    al, [r14+70h]
                mov     r15d, 3
                jmp     loc_92ADB
; ---------------------------------------------------------------------------

loc_938F0:                              ; CODE XREF: sub_902F0+1820↑j
                lea     rcx, qword_21072BB0
                movzx   eax, word ptr [rcx+rax*2]
                mov     qword ptr [rsp+0BB8h+dest], 0
                mov     [rsp+0BB8h+n+8], 0
                mov     qword ptr [rsp+0BB8h+var_858], 8
                lea     rcx, [rsp+0BB8h+n]
                pxor    xmm0, xmm0
                movdqu  xmmword ptr [rcx+18h], xmm0
                mov     [rsp+0BB8h+var_840], 8
                mov     [rsp+0BB8h+var_838], 0
                mov     [rsp+0BB8h+var_830], 2
                mov     [rsp+0BB8h+var_828], 0
                mov     [rsp+0BB8h+var_820], 0
                mov     [rsp+0BB8h+var_818], 0
                mov     [rsp+0BB8h+var_810], ax
                mov     [rsp+0BB8h+var_80E], 2
                mov     rax, [rsp+0BB8h+var_A60]
                movups  xmm0, xmmword ptr [rax+50h]
                movaps  [rsp+0BB8h+var_948], xmm0
                movups  xmm0, xmmword ptr [rax+40h]
                movaps  [rsp+0BB8h+var_958], xmm0
                movdqu  xmm0, xmmword ptr [rax]
                movdqu  xmm1, xmmword ptr [rax+10h]
                movdqu  xmm2, xmmword ptr [rax+20h]
                movdqu  xmm3, xmmword ptr [rax+30h]
                movdqa  [rsp+0BB8h+var_968], xmm3
                movdqa  [rsp+0BB8h+var_978], xmm2
                movdqa  [rsp+0BB8h+var_988], xmm1
                movdqa  [rsp+0BB8h+var_998], xmm0
                mov     qword ptr [rax], 3
                cmp     dword ptr [rsp+0BB8h+var_998], 3
                jz      short loc_939FB
                lea     rdi, [rsp+0BB8h+var_998]
                call    sub_D55E0

loc_939FB:                              ; CODE XREF: sub_902F0+36FC↑j
                mov     edx, 2
                mov     rdi, [rsp+0BB8h+var_B98]
                lea     rsi, [rsp+0BB8h+dest]
                call    sub_6EA90
                mov     r14, [rbx+298h]
                test    r14, r14
                jz      short loc_93A54
                mov     r15, [r14]
                test    r15, r15
                jz      short loc_93A4B
                mov     rbx, [r14+8]
                mov     rax, [rbx]
                test    rax, rax
                jz      short loc_93A37
                mov     rdi, r15
                call    rax

loc_93A37:                              ; CODE XREF: sub_902F0+3740↑j
                cmp     qword ptr [rbx+8], 0
                mov     rbx, [rsp+0BB8h+var_BB8]
                jz      short loc_93A4B
                mov     rdi, r15        ; ptr
                call    cs:free_ptr

loc_93A4B:                              ; CODE XREF: sub_902F0+3734↑j
                                        ; sub_902F0+3750↑j
                mov     rdi, r14        ; ptr
                call    cs:free_ptr

loc_93A54:                              ; CODE XREF: sub_902F0+372C↑j
                mov     [rbx+298h], r12
                jmp     loc_91D30
; ---------------------------------------------------------------------------

loc_93A60:                              ; CODE XREF: sub_902F0+3395↑j
                mov     al, 1
                mov     r13, [rsp+0BB8h+var_BA8]
                mov     r12, [rsp+0BB8h+var_BB0]
                jmp     loc_936A8
; ---------------------------------------------------------------------------

loc_93A71:                              ; CODE XREF: sub_902F0+35E9↑j
                lea     rax, [r14+18h]
                mov     rcx, [rax+50h]
                mov     [rsp+0BB8h+var_A08], rcx
                movups  xmm0, xmmword ptr [rax+40h]
                movaps  [rsp+0BB8h+var_A18], xmm0
                movdqu  xmm0, xmmword ptr [rax]
                movdqu  xmm1, xmmword ptr [rax+10h]
                movdqu  xmm2, xmmword ptr [rax+20h]
                movdqu  xmm3, xmmword ptr [rax+30h]
                movdqa  [rsp+0BB8h+var_A28], xmm3
                movdqa  [rsp+0BB8h+var_A38], xmm2
                movdqa  [rsp+0BB8h+var_A48], xmm1
                movdqa  [rsp+0BB8h+var_A58], xmm0
                xor     eax, eax
                xchg    al, [r14+70h]
                jmp     loc_92ADB
; ---------------------------------------------------------------------------

loc_93ACF:                              ; CODE XREF: sub_902F0+1B5D↑j
                mov     rax, [r13+0]
                mov     rcx, [rax]
                mov     rdi, [rax+8]
                call    qword ptr [rcx+10h]

loc_93ADD:                              ; CODE XREF: sub_902F0+2DA↑j
                                        ; sub_902F0+3D4↑j ...
                mov     bpl, 3
                mov     al, 1

loc_93AE2:                              ; CODE XREF: sub_902F0+919↑j
                                        ; sub_902F0+920↑j
                mov     [rbx+320h], bpl
                add     rsp, 0B88h
                pop     rbx
                pop     r12
                pop     r13
                pop     r14
                pop     r15
                pop     rbp
                retn
; ---------------------------------------------------------------------------

loc_93AFB:                              ; CODE XREF: sub_902F0+1A7↑j
                lea     rsi, aCancelled ; "Cancelled"
                mov     edx, 9
                mov     edi, 23h ; '#'
                call    sub_FEA910
                mov     r14, rax
                mov     edi, 8          ; size
                call    cs:malloc_ptr
                test    rax, rax
                jz      loc_94493

loc_93B28:                              ; CODE XREF: sub_902F0+3BF6↓j
                mov     r15, rax
                mov     [rax], r14
                lea     rbx, off_210C6F30
                jmp     loc_940B2
; ---------------------------------------------------------------------------

loc_93B3A:                              ; CODE XREF: sub_902F0+436↑j
                mov     edi, 17h        ; size
                call    cs:malloc_ptr
                test    rax, rax
                jz      loc_947D5
                mov     r12, rax
                movdqu  xmm0, xmmword ptr cs:unk_10340BF
                movdqu  xmmword ptr [rax], xmm0
                mov     rax, 646574726F707075h
                mov     [r12+0Fh], rax
                mov     edi, 18h        ; size
                call    cs:malloc_ptr
                test    rax, rax
                mov     rbx, [rsp+0BB8h+var_B98]
                jz      loc_943B8
                mov     r15, rax
                mov     qword ptr [rax], 17h
                mov     [rax+8], r12
                mov     qword ptr [rax+10h], 17h
                lock dec qword ptr [rbp+0]
                jnz     short loc_93BAA
                mov     rdi, rbp        ; ptr
                call    sub_B40E0

loc_93BAA:                              ; CODE XREF: sub_902F0+38B0↑j
                mov     rax, qword ptr [rsp+0BB8h+var_558]
                test    rax, rax
                jz      short loc_93BD2
                mov     rdi, qword ptr [rsp+0BB8h+var_548+8]
                mov     rsi, qword ptr [rsp+0BB8h+var_558+8]
                mov     rdx, qword ptr [rsp+0BB8h+var_548]
                call    qword ptr [rax+20h]

loc_93BD2:                              ; CODE XREF: sub_902F0+38C5↑j
                lea     rdi, [rsp+0BB8h+var_578]
                call    sub_67390
                mov     rdi, rbx
                call    sub_64F20
                lea     rbx, off_210CD628
                jmp     loc_940BC
; ---------------------------------------------------------------------------

loc_93BF3:                              ; CODE XREF: sub_902F0+1B2F↑j
                mov     r14, [rbx+0E8h]
                mov     rax, [rbx+0F0h]
                mov     rdi, [rbx+110h]
                test    rdi, rdi
                jz      short loc_93C8C
                mov     rdx, [rbx+0F8h]
                mov     rcx, [rbx+108h]
                xor     esi, esi
                cmp     rcx, rdx
                cmovnb  rsi, rdx
                sub     rcx, rsi
                mov     r8, rdx
                sub     r8, rcx
                mov     rsi, rdi
                sub     rsi, r8
                ja      short loc_93C92
                add     rdi, rcx
                xor     esi, esi
                mov     rdx, rdi
                jmp     short loc_93C92
; ---------------------------------------------------------------------------

loc_93C3F:                              ; CODE XREF: sub_902F0+10CC↑j
                lea     rdx, off_210CD418 ; "/home/aothuatgiadp/.cargo/registry/src/"...
                mov     rdi, rax
                call    sub_4A610
; ---------------------------------------------------------------------------

loc_93C4E:                              ; CODE XREF: sub_902F0+110E↑j
                lea     rdx, off_210CD430 ; "/home/aothuatgiadp/.cargo/registry/src/"...
                mov     rdi, rax
                call    sub_4A610
; ---------------------------------------------------------------------------

loc_93C5D:                              ; CODE XREF: sub_902F0+1372↑j
                lea     rdx, off_210C6CB8 ; "/home/aothuatgiadp/.cargo/registry/src/"...
                mov     rdi, r13
                mov     rsi, rbp
                call    sub_4A690
; ---------------------------------------------------------------------------

loc_93C6F:                              ; CODE XREF: sub_902F0+139A↑j
                mov     qword ptr [rsp+0BB8h+dest], r13
                mov     qword ptr [rsp+0BB8h+dest+8], rcx
                lea     rdi, [rsp+0BB8h+dest]
                call    sub_4A530
; ---------------------------------------------------------------------------

loc_93C8C:                              ; CODE XREF: sub_902F0+391B↑j
                xor     ecx, ecx
                xor     edx, edx
                xor     esi, esi

loc_93C92:                              ; CODE XREF: sub_902F0+3943↑j
                                        ; sub_902F0+394D↑j
                sub     r14, rax
                mov     rax, [rbx+100h]
                lea     rcx, [rcx+rcx*4]
                shl     rcx, 4
                add     rcx, rax
                lea     rdx, [rdx+rdx*4]
                shl     rdx, 4
                add     rdx, rax
                lea     rsi, [rsi+rsi*4]
                shl     rsi, 4
                add     rsi, rax
                mov     qword ptr [rsp+0BB8h+dest], rcx
                mov     qword ptr [rsp+0BB8h+dest+8], rdx
                mov     [rsp+0BB8h+n], rax
                mov     [rsp+0BB8h+n+8], rsi
                lea     rdi, [rsp+0BB8h+dest]
                call    sub_57510
                add     rax, r14
                jz      short loc_93D0D
                mov     rdi, [rsp+0BB8h+var_B98]
                mov     rsi, r13
                call    sub_74140
                test    rdx, rdx
                setz    cl
                or      cl, al
                test    cl, 1
                jz      loc_93F50

loc_93D0D:                              ; CODE XREF: sub_902F0+1B10↑j
                                        ; sub_902F0+1B7E↑j ...
                cmp     byte ptr [rbx+318h], 0
                jnz     short loc_93D65
                mov     rax, [rbx+1E8h]
                mov     rdx, 7FFFFFFFFFFFFFFDh
                add     rdx, [rbx+250h]
                mov     cl, 1
                cmp     rdx, 3
                jz      short loc_93D54
                mov     rcx, [rbx+300h]
                cmp     dword ptr [rcx], 0Ah
                jnz     loc_93ADD
                mov     rcx, [rbx+310h]
                cmp     qword ptr [rcx], 0
                setz    cl

loc_93D54:                              ; CODE XREF: sub_902F0+3A44↑j
                cmp     eax, 4
                jnz     loc_93ADD
                test    cl, cl
                jz      loc_93ADD

loc_93D65:                              ; CODE XREF: sub_902F0+3A24↑j
                mov     r14, [rbx+178h]
                mov     r12, [rbx+180h]
                mov     qword ptr [rbx+178h], 0
                cmp     r14, 1
                jnz     loc_93E0D
                mov     rdx, [rbx+298h]
                mov     qword ptr [rbx+298h], 0
                test    rdx, rdx
                jz      loc_93E39
                test    r12, r12
                jz      loc_93F50
                mov     rax, [r12+30h]

loc_93DB1:                              ; CODE XREF: sub_902F0+3ADA↓j
                mov     rcx, rax
                test    cl, 4
                jnz     short loc_93DCC
                mov     rsi, rcx
                or      rsi, 2
                mov     rax, rcx
                lock cmpxchg [r12+30h], rsi
                jnz     short loc_93DB1

loc_93DCC:                              ; CODE XREF: sub_902F0+3AC7↑j
                and     ecx, 5
                cmp     ecx, 1
                jnz     short loc_93DEB
                mov     rax, [r12+20h]
                mov     rdi, [r12+28h]
                mov     rbx, rdx
                call    qword ptr [rax+10h]
                mov     rdx, rbx
                mov     rbx, [rsp+0BB8h+var_BB8]

loc_93DEB:                              ; CODE XREF: sub_902F0+3AE2↑j
                lock dec qword ptr [r12]
                jnz     loc_93F50
                mov     rdi, r12        ; ptr
                mov     rbx, rdx
                call    sub_D5470
                mov     rdx, rbx
                mov     rbx, [rsp+0BB8h+var_BB8]
                jmp     loc_93F50
; ---------------------------------------------------------------------------

loc_93E0D:                              ; CODE XREF: sub_902F0+3A92↑j
                mov     rsi, [r13+0]
                mov     rdi, [rsp+0BB8h+var_B98]
                call    sub_6E010
                test    al, 1
                jz      short loc_93E29
                mov     eax, 1
                jmp     loc_93F10
; ---------------------------------------------------------------------------

loc_93E29:                              ; CODE XREF: sub_902F0+3B2D↑j
                test    rdx, rdx
                jz      loc_93F05
                xor     eax, eax
                jmp     loc_93F10
; ---------------------------------------------------------------------------

loc_93E39:                              ; CODE XREF: sub_902F0+3AAD↑j
                mov     rax, [rsp+0BB8h+var_B98]
                mov     rbx, [rax]
                mov     qword ptr [rax], 2
                cmp     rbx, 2
                jz      loc_947E4
                lea     rdi, [rsp+0BB8h+dest+8] ; dest
                mov     edx, 290h       ; n
                mov     rsi, [rsp+0BB8h+var_AF0] ; src
                mov     r15, cs:memcpy_ptr
                call    r15 ; memcpy
                mov     qword ptr [rsp+0BB8h+dest], rbx
                lea     rdi, [rsp+0BB8h+var_578] ; dest
                lea     r14, [rsp+0BB8h+dest]
                mov     edx, 250h       ; n
                mov     rsi, r14        ; src
                call    r15 ; memcpy
                lea     rdi, [rsp+0BB8h+var_998] ; dest
                mov     edx, 0E0h       ; n
                mov     rsi, r14        ; src
                call    r15 ; memcpy
                mov     r13, [rsp+0BB8h+var_8E0]
                mov     r15, [rsp+0BB8h+var_8D8]
                mov     r14, [rsp+0BB8h+var_8C8]
                test    r14b, 1
                jnz     loc_940E6
                lea     rbx, off_210CE518
                jmp     loc_9415F
; ---------------------------------------------------------------------------

loc_93ED5:                              ; CODE XREF: sub_902F0+2E3↑j
                mov     r14, rdx
                mov     edi, 8          ; size
                call    cs:malloc_ptr
                test    rax, rax
                jnz     loc_93B28
                jmp     loc_94493
; ---------------------------------------------------------------------------

loc_93EF1:                              ; CODE XREF: sub_902F0+26D↑j
                lea     rdx, off_210C6CB8 ; "/home/aothuatgiadp/.cargo/registry/src/"...
                mov     esi, 18h
                mov     rdi, r14
                call    sub_4A690
; ---------------------------------------------------------------------------

loc_93F05:                              ; CODE XREF: sub_902F0+3B3C↑j
                mov     edi, [rbx+0A0h]
                call    sub_FF3230

loc_93F10:                              ; CODE XREF: sub_902F0+3B34↑j
                                        ; sub_902F0+3B44↑j
                test    al, 1
                jnz     loc_93ADD
                test    rdx, rdx
                jz      short loc_93F2A
                mov     rdi, rdx
                call    sub_D6F00
                mov     rdx, rax
                jmp     short loc_93F50
; ---------------------------------------------------------------------------

loc_93F2A:                              ; CODE XREF: sub_902F0+3C2B↑j
                mov     rdi, r14
                mov     rsi, r12
                call    sub_65FD0
                mov     rdx, [rbx+298h]
                mov     qword ptr [rbx+298h], 0
                test    rdx, rdx
                jz      loc_90BDE

loc_93F50:                              ; CODE XREF: sub_902F0+1A32↑j
                                        ; sub_902F0+1A5E↑j ...
                mov     r14, [rbx+300h]
                mov     r15, [rbx+308h]
                movzx   ebp, byte ptr [rbx+2F8h]
                mov     byte ptr [rbx+2F8h], 3
                cmp     bpl, 3
                jz      loc_9405E
                mov     [rsp+0BB8h+src], rdx
                mov     rax, [rsp+0BB8h+var_B90]
                movups  xmm0, xmmword ptr [rax]
                movdqu  xmm1, xmmword ptr [rax+10h]
                movdqa  xmmword ptr [rsp+0BB8h+n], xmm1
                movaps  [rsp+0BB8h+dest], xmm0
                mov     byte ptr [rsp+0BB8h+var_858], bpl
                mov     rcx, [rsp+0BB8h+var_AE8]
                mov     eax, [rcx]
                mov     ecx, [rcx+3]
                mov     dword ptr [rsp+0BB8h+var_858+1], eax
                mov     dword ptr [rsp+0BB8h+var_858+4], ecx
                mov     edi, 18h        ; size
                call    cs:malloc_ptr
                test    rax, rax
                jz      loc_943B8
                mov     r12, rax
                mov     qword ptr [rax], 0
                mov     byte ptr [rax+10h], 8
                mov     edi, 10h        ; size
                call    cs:malloc_ptr
                test    rax, rax
                jz      loc_94913
                mov     r13, rax
                movdqu  xmm0, cs:xmmword_1000D60
                movdqu  xmmword ptr [rax], xmm0
                mov     edi, 18h        ; size
                call    cs:malloc_ptr
                test    rax, rax
                jz      loc_943B8
                mov     qword ptr [rax], 10h
                mov     [rax+8], r13
                mov     qword ptr [rax+10h], 10h
                mov     [r12], rax
                lea     rax, off_210C7FA8
                mov     [r12+8], rax
                mov     rdi, [rsp+0BB8h+n]
                movzx   esi, bpl
                mov     rdx, r12
                call    sub_D6A30
                lea     rdi, [rsp+0BB8h+dest]
                call    sub_64B90
                mov     rdx, [rsp+0BB8h+src]

loc_9405E:                              ; CODE XREF: sub_902F0+3C80↑j
                mov     qword ptr [rsp+0BB8h+dest+8], rdx
                mov     qword ptr [rsp+0BB8h+dest], 3
                lea     rdx, [rsp+0BB8h+dest]
                mov     rdi, r14
                mov     rsi, r15
                call    sub_59A00
                test    rax, rax
                jz      loc_90BDE
                mov     r14, rax
                mov     edi, 8          ; size
                call    cs:malloc_ptr
                test    rax, rax
                jz      loc_94493
                mov     r15, rax
                mov     [rax], r14
                lea     rbx, off_210C6FA8

loc_940B2:                              ; CODE XREF: sub_902F0+3845↑j
                mov     rdi, [rsp+0BB8h+var_B98]
                call    sub_64F20

loc_940BC:                              ; CODE XREF: sub_902F0+38FE↑j
                mov     rax, [rbx]
                test    rax, rax
                jz      short loc_940C9
                mov     rdi, r15
                call    rax

loc_940C9:                              ; CODE XREF: sub_902F0+3DD2↑j
                cmp     qword ptr [rbx+8], 0
                mov     rbx, [rsp+0BB8h+var_BB8]
                jz      loc_90BE8
                mov     rdi, r15        ; ptr
                call    cs:free_ptr
                jmp     loc_90BE8
; ---------------------------------------------------------------------------

loc_940E6:                              ; CODE XREF: sub_902F0+3BD3↑j
                shr     r14, 5
                sub     r13, r14
                add     r15, r14
                mov     rax, [rsp+0BB8h+var_8D0]
                add     rax, r14
                mov     [rsp+0BB8h+var_898], rax
                mov     [rsp+0BB8h+var_890], r13
                mov     [rsp+0BB8h+var_888], r15
                lea     rdi, [rsp+0BB8h+var_AD8]
                lea     rsi, [rsp+0BB8h+var_898]
                call    sub_BB950
                mov     [rsp+0BB8h+var_880], r14
                mov     rax, qword ptr [rsp+0BB8h+var_AC8]
                mov     r15, rax
                sub     r15, r14
                jb      loc_9480B
                mov     r13, r14
                add     r13, qword ptr [rsp+0BB8h+var_AD8+8]
                mov     rbx, qword ptr [rsp+0BB8h+var_AD8]
                mov     r14, qword ptr [rsp+0BB8h+var_AC8+8]

loc_9415F:                              ; CODE XREF: sub_902F0+3BE0↑j
                movups  xmm0, [rsp+0BB8h+dest]
                movups  xmm1, xmmword ptr [rsp+0BB8h+n]
                movups  xmm2, [rsp+0BB8h+var_858]
                movups  xmm3, xmmword ptr [rsp+370h]
                movaps  [rsp+0BB8h+var_A58], xmm0
                movaps  [rsp+0BB8h+var_A48], xmm1
                movaps  [rsp+0BB8h+var_A38], xmm2
                movaps  [rsp+0BB8h+var_A28], xmm3
                lea     rdi, [rsp+0BB8h+var_948]
                call    sub_63200
                lea     rdi, [rsp+0BB8h+var_498]
                call    sub_64CE0
                mov     qword ptr [rsp+0BB8h+var_A18], rbx
                mov     qword ptr [rsp+0BB8h+var_A18+8], r13
                mov     [rsp+0BB8h+var_A08], r15
                mov     [rsp+0BB8h+var_A00], r14
                movups  xmm0, [rsp+0BB8h+var_600]
                movaps  [rsp+0BB8h+var_9F8], xmm0
                lea     r14, [rsp+0BB8h+var_628]
                mov     rdi, r14
                call    sub_DABC0
                cmp     [rsp+0BB8h+var_608], 3
                jz      short loc_9420B
                mov     rdi, r14
                call    sub_64B90

loc_9420B:                              ; CODE XREF: sub_902F0+3F11↑j
                lea     rbx, [rsp+0BB8h+var_A18]
                lea     r14, [rsp+0BB8h+var_9F8]
                mov     r15, [rsp+0BB8h+ptr]
                mov     r13, [r15]
                test    r13, r13
                jz      short loc_9424D
                mov     rbp, [r15+8]
                mov     rax, [rbp+0]
                test    rax, rax
                jz      short loc_9423D
                mov     rdi, r13
                call    rax

loc_9423D:                              ; CODE XREF: sub_902F0+3F46↑j
                cmp     qword ptr [rbp+8], 0
                jz      short loc_9424D
                mov     rdi, r13        ; ptr
                call    cs:free_ptr

loc_9424D:                              ; CODE XREF: sub_902F0+3F39↑j
                                        ; sub_902F0+3F52↑j
                mov     rdi, r15        ; ptr
                call    cs:free_ptr
                movaps  xmm0, [rsp+0BB8h+var_A58]
                movaps  xmm1, [rsp+0BB8h+var_A48]
                movaps  xmm2, [rsp+0BB8h+var_A38]
                movaps  xmm3, [rsp+0BB8h+var_A28]
                movaps  [rsp+0BB8h+var_5D8], xmm0
                movaps  [rsp+0BB8h+var_5C8], xmm1
                movaps  [rsp+0BB8h+var_5B8], xmm2
                movaps  [rsp+0BB8h+var_5A8], xmm3
                movups  xmm0, xmmword ptr [rbx]
                movups  xmm1, xmmword ptr [rbx+10h]
                movaps  [rsp+0BB8h+var_598], xmm0
                movaps  [rsp+0BB8h+var_588], xmm1
                mov     rdi, r14
                call    sub_64250
                mov     edi, 40h ; '@'  ; size
                call    cs:malloc_ptr
                test    rax, rax
                jz      loc_947FC
                movaps  xmm0, [rsp+0BB8h+var_5D8]
                movaps  xmm1, [rsp+0BB8h+var_5C8]
                movdqa  xmm2, [rsp+0BB8h+var_5B8]
                movdqa  xmm3, [rsp+0BB8h+var_5A8]
                movdqu  xmmword ptr [rax+30h], xmm3
                movdqu  xmmword ptr [rax+20h], xmm2
                movups  xmmword ptr [rax+10h], xmm1
                movups  xmmword ptr [rax], xmm0
                movdqa  xmm0, [rsp+0BB8h+var_598]
                movdqa  xmm1, [rsp+0BB8h+var_588]
                movdqu  xmmword ptr [rsp+0BB8h+n], xmm0
                movdqu  [rsp+0BB8h+var_858], xmm1
                mov     qword ptr [rsp+0BB8h+dest], rax
                lea     rax, off_210C6EA0
                mov     qword ptr [rsp+0BB8h+dest+8], rax
                lea     rsi, [rsp+0BB8h+dest]
                mov     rdi, r12        ; ptr
                call    sub_D73B0
                mov     rbx, [rsp+0BB8h+var_BB8]
                jmp     loc_90BDE
; ---------------------------------------------------------------------------

loc_94350:                              ; CODE XREF: sub_902F0+1058↑j
                lea     rdx, off_210CD448 ; "/home/aothuatgiadp/.cargo/registry/src/"...
                mov     rsi, r14
                call    sub_4A610
; ---------------------------------------------------------------------------

loc_9435F:                              ; CODE XREF: sub_902F0+1367↑j
                lea     rdx, off_210C85C0 ; "/home/aothuatgiadp/.cargo/registry/src/"...
                mov     rdi, r13
                call    sub_4A690
; ---------------------------------------------------------------------------

loc_9436E:                              ; CODE XREF: sub_902F0+1C4↑j
                lea     rdx, off_210C6CB8 ; "/home/aothuatgiadp/.cargo/registry/src/"...
                mov     esi, 18h
                mov     rdi, r15
                call    sub_4A690
; ---------------------------------------------------------------------------

loc_94382:                              ; CODE XREF: sub_902F0+1E3↑j
                lea     rdi, off_210C6CD0 ; "/home/aothuatgiadp/.cargo/registry/src/"...
                call    sub_4A8E0
; ---------------------------------------------------------------------------

loc_9438E:                              ; CODE XREF: sub_902F0+257↑j
                lea     rax, off_210C85C0 ; "/home/aothuatgiadp/.cargo/registry/src/"...
                mov     rdi, rdx
                mov     rdx, rax
                call    sub_4A690
; ---------------------------------------------------------------------------

loc_943A0:                              ; CODE XREF: sub_902F0+263↑j
                lea     rdi, aOverflow  ; "overflow"
                lea     rdx, off_210C8000 ; "/home/aothuatgiadp/.cargo/registry/src/"...
                mov     esi, 8
                call    sub_4AAB0
; ---------------------------------------------------------------------------

loc_943B8:                              ; CODE XREF: sub_902F0+DAB↑j
                                        ; sub_902F0+1435↑j ...
                mov     edi, 8
                mov     esi, 18h
                call    sub_497D5
; ---------------------------------------------------------------------------

loc_943C7:                              ; CODE XREF: sub_902F0+1C66↑j
                                        ; sub_902F0+1D26↑j ...
                mov     edi, 8
                mov     esi, 30h ; '0'
                call    sub_497D5
; ---------------------------------------------------------------------------

loc_943D6:                              ; CODE XREF: sub_902F0+14E3↑j
                mov     qword ptr [rsp+0BB8h+var_AD8], r14
                lea     rax, [rsp+0BB8h+var_898]
                mov     qword ptr [rsp+0BB8h+var_998], rax
                lea     rax, sub_625B0
                mov     qword ptr [rsp+0BB8h+var_998+8], rax
                lea     rcx, [rsp+0BB8h+var_AD8]
                mov     qword ptr [rsp+0BB8h+var_988], rcx
                mov     qword ptr [rsp+0BB8h+var_988+8], rax
                lea     rax, off_210CE540 ; "cannot advance past `remaining`: "
                mov     qword ptr [rsp+0BB8h+dest], rax
                mov     qword ptr [rsp+0BB8h+dest+8], 2
                mov     qword ptr [rsp+0BB8h+var_858], 0
                lea     rax, [rsp+0BB8h+var_998]
                mov     [rsp+0BB8h+n], rax
                mov     [rsp+0BB8h+n+8], 2
                lea     rsi, off_210CE608 ; "/home/aothuatgiadp/.cargo/registry/src/"...
                lea     rdi, [rsp+0BB8h+dest]
                call    sub_4A5F0
; ---------------------------------------------------------------------------

loc_9446C:                              ; CODE XREF: sub_902F0+771↑j
                                        ; sub_902F0+1C91↑j
                mov     edi, 8
                mov     esi, 10h
                call    sub_497D5
; ---------------------------------------------------------------------------

loc_9447B:                              ; CODE XREF: sub_902F0+EC8↑j
                                        ; sub_902F0+EDB↑j
                lea     rdi, aOverflowWhenAd ; "overflow when adding duration to instan"...
                lea     rdx, off_210E6250 ; "library/std/src/time.rs"
                mov     esi, 28h ; '('
                call    sub_4AAB0
; ---------------------------------------------------------------------------

loc_94493:                              ; CODE XREF: sub_902F0+18D2↑j
                                        ; sub_902F0+200B↑j ...
                mov     edi, 8
                mov     esi, 8
                call    sub_497D5
; ---------------------------------------------------------------------------

loc_944A2:                              ; CODE XREF: sub_902F0+8E3↑j
                lea     rdi, aInternalErrorE_9 ; "internal error: entered unreachable cod"...
                lea     rdx, off_210C7000 ; "/home/aothuatgiadp/.cargo/registry/src/"...
                mov     esi, 28h ; '('
                call    sub_4A710
; ---------------------------------------------------------------------------

loc_944BA:                              ; CODE XREF: sub_902F0+2AE↑j
                                        ; sub_902F0+310↑j
                lea     rdi, off_210C6CE8 ; "/home/aothuatgiadp/.cargo/registry/src/"...
                call    sub_4A8E0
; ---------------------------------------------------------------------------

loc_944C6:                              ; CODE XREF: sub_902F0+42E↑j
                lea     rdi, off_210C6EF8 ; "/home/aothuatgiadp/.cargo/registry/src/"...
                call    sub_4A8E0
; ---------------------------------------------------------------------------

loc_944D2:                              ; CODE XREF: sub_902F0+753↑j
                mov     edi, 8
                mov     esi, 128h
                call    sub_497D5
; ---------------------------------------------------------------------------

loc_944E1:                              ; CODE XREF: sub_902F0+D78↑j
                mov     qword ptr [rsp+0BB8h+var_998], rax
                lea     rax, [rsp+0BB8h+var_998]
                mov     qword ptr [rsp+0BB8h+var_578], rax
                lea     rax, sub_BCE70
                mov     qword ptr [rsp+0BB8h+var_578+8], rax
                lea     rax, off_210CD200 ; "internal error: entered unreachable cod"...
                mov     qword ptr [rsp+0BB8h+dest], rax
                mov     qword ptr [rsp+0BB8h+dest+8], 1
                mov     qword ptr [rsp+0BB8h+var_858], 0
                lea     rax, [rsp+0BB8h+var_578]
                mov     [rsp+0BB8h+n], rax
                mov     [rsp+0BB8h+n+8], 1
                lea     rsi, off_210CD210 ; "/home/aothuatgiadp/.cargo/registry/src/"...
                lea     rdi, [rsp+0BB8h+dest]
                call    sub_4A5F0
; ---------------------------------------------------------------------------

loc_9455F:                              ; CODE XREF: sub_902F0+1F1C↑j
                                        ; sub_902F0+1FDE↑j
                mov     edi, 8
                mov     esi, 20h ; ' '
                call    sub_497D5
; ---------------------------------------------------------------------------

loc_9456E:                              ; CODE XREF: sub_902F0+1CA8↑j
                mov     edi, 8
                mov     esi, 60h ; '`'
                call    sub_497D5
; ---------------------------------------------------------------------------

loc_9457D:                              ; CODE XREF: sub_902F0+1D60↑j
                mov     edi, 8
                mov     esi, 0B0h
                call    sub_497D5
; ---------------------------------------------------------------------------

loc_9458C:                              ; CODE XREF: sub_902F0+937↑j
                mov     rax, fs:0
                lea     rdi, [rax-0A0h]
                call    sub_4DD60
                cmp     qword ptr fs:0FFFFFFFFFFFFFF60h, 0
                jz      loc_90C3D

loc_945B1:                              ; CODE XREF: sub_902F0+947↑j
                lea     rdi, off_210CD278 ; "/home/aothuatgiadp/.cargo/registry/src/"...
                call    sub_4A970
; ---------------------------------------------------------------------------

loc_945BD:                              ; CODE XREF: sub_902F0+1EE6↑j
                mov     edi, 8
                mov     esi, 70h ; 'p'
                call    sub_497D5
; ---------------------------------------------------------------------------

loc_945CC:                              ; CODE XREF: sub_902F0+F02↑j
                lea     rax, off_210CD2A8 ; "You must supply a timer."
                mov     qword ptr [rsp+0BB8h+dest], rax
                mov     qword ptr [rsp+0BB8h+dest+8], 1
                mov     [rsp+0BB8h+n], 8
                xorps   xmm0, xmm0
                movups  xmmword ptr [rsp+0BB8h+n+8], xmm0
                lea     rsi, off_210CD2D0 ; "/home/aothuatgiadp/.cargo/registry/src/"...
                lea     rdi, [rsp+0BB8h+dest]
                call    sub_4A5F0
; ---------------------------------------------------------------------------

loc_94612:                              ; CODE XREF: sub_902F0+8A0↑j
                lea     rax, qword_10016F8
                mov     qword ptr [rsp+0BB8h+var_998], rax
                lea     rax, sub_BCE70
                mov     qword ptr [rsp+0BB8h+var_998+8], rax
                lea     rax, off_210C8060 ; "The max_buf_size cannot be smaller than"...
                mov     qword ptr [rsp+0BB8h+dest], rax
                mov     qword ptr [rsp+0BB8h+dest+8], 2
                mov     qword ptr [rsp+0BB8h+var_858], 0
                lea     rax, [rsp+0BB8h+var_998]
                mov     [rsp+0BB8h+n], rax
                mov     [rsp+0BB8h+n+8], 1
                lea     rsi, off_210C8080 ; "/home/aothuatgiadp/.cargo/registry/src/"...
                lea     rdi, [rsp+0BB8h+dest]
                call    sub_4A5F0
; ---------------------------------------------------------------------------

loc_94687:                              ; CODE XREF: sub_902F0+D45↑j
                lea     rdi, off_210C91B0 ; "/home/aothuatgiadp/.cargo/registry/src/"...
                call    sub_4A8E0
; ---------------------------------------------------------------------------

loc_94693:                              ; CODE XREF: sub_902F0+169D↑j
                mov     edi, 8
                mov     esi, 28h ; '('
                call    sub_497D5
; ---------------------------------------------------------------------------

loc_946A2:                              ; CODE XREF: sub_902F0+F38↑j
                lea     rax, off_210CD2A8 ; "You must supply a timer."
                mov     qword ptr [rsp+0BB8h+dest], rax
                mov     qword ptr [rsp+0BB8h+dest+8], 1
                mov     [rsp+0BB8h+n], 8
                xorps   xmm0, xmm0
                movups  xmmword ptr [rsp+0BB8h+n+8], xmm0
                lea     rsi, off_210CD2B8 ; "/home/aothuatgiadp/.cargo/registry/src/"...
                lea     rdi, [rsp+0BB8h+dest]
                call    sub_4A5F0
; ---------------------------------------------------------------------------

loc_946E8:                              ; CODE XREF: sub_902F0+A79↑j
                lea     rdi, aOverflowWhenAd ; "overflow when adding duration to instan"...
                lea     rdx, off_210E6268 ; "library/std/src/time.rs"
                mov     esi, 28h ; '('
                call    sub_4AAB0
; ---------------------------------------------------------------------------

loc_94700:                              ; CODE XREF: sub_902F0+6D7↑j
                lea     rax, [rsp+0BB8h+var_A58]
                mov     qword ptr [rsp+0BB8h+var_998], rax
                lea     rax, sub_D6DC0
                mov     qword ptr [rsp+0BB8h+var_998+8], rax
                lea     rax, off_210CD2E8 ; "timeout `"
                mov     qword ptr [rsp+0BB8h+dest], rax
                mov     qword ptr [rsp+0BB8h+dest+8], 2
                mov     qword ptr [rsp+0BB8h+var_858], 0
                lea     rax, [rsp+0BB8h+var_998]
                mov     [rsp+0BB8h+n], rax
                mov     [rsp+0BB8h+n+8], 1
                lea     rsi, off_210CD308 ; "/home/aothuatgiadp/.cargo/registry/src/"...
                lea     rdi, [rsp+0BB8h+dest]
                call    sub_4A5F0
; ---------------------------------------------------------------------------

loc_94776:                              ; CODE XREF: sub_902F0+2F05↑j
                lea     rdi, aInternalErrorE_9 ; "internal error: entered unreachable cod"...
                lea     rdx, off_210CD1D0 ; "/home/aothuatgiadp/.cargo/registry/src/"...
                mov     esi, 28h ; '('
                call    sub_4A710
; ---------------------------------------------------------------------------

loc_9478E:                              ; CODE XREF: sub_902F0+A9A↑j
                lea     rdi, aOverflowWhenSu ; "overflow when subtracting duration from"...
                lea     rdx, off_210E6280 ; "library/std/src/time.rs"
                mov     esi, 2Fh ; '/'
                call    sub_4AAB0
; ---------------------------------------------------------------------------

loc_947A6:                              ; CODE XREF: sub_902F0+2A49↑j
                mov     qword ptr [rsp+0BB8h+var_998], r14
                lea     rdi, aJustSentOk ; "just sent Ok"
                lea     rcx, off_210CCD18
                lea     r8, off_210CD228 ; "/home/aothuatgiadp/.cargo/registry/src/"...
                lea     rdx, [rsp+0BB8h+var_998]
                mov     esi, 0Ch
                call    sub_4AA30
; ---------------------------------------------------------------------------

loc_947D5:                              ; CODE XREF: sub_902F0+3858↑j
                mov     edi, 1
                mov     esi, 17h
                call    sub_497D5
; ---------------------------------------------------------------------------

loc_947E4:                              ; CODE XREF: sub_902F0+3B5C↑j
                lea     rdi, aUpgradeableSer ; "upgradeable server connection missing a"...
                lea     rdx, off_210C6E48 ; "/home/aothuatgiadp/.cargo/registry/src/"...
                mov     esi, 33h ; '3'
                call    sub_4AAB0
; ---------------------------------------------------------------------------

loc_947FC:                              ; CODE XREF: sub_902F0+3FD3↑j
                mov     edi, 8
                mov     esi, 40h ; '@'
                call    sub_497D5
; ---------------------------------------------------------------------------

loc_9480B:                              ; CODE XREF: sub_902F0+3E4E↑j
                mov     [rsp+0BB8h+var_AE0], rax
                lea     rax, [rsp+0BB8h+var_880]
                mov     [rsp+0BB8h+var_2E8], rax
                lea     rax, sub_625B0
                mov     [rsp+0BB8h+var_2E0], rax
                lea     rcx, [rsp+0BB8h+var_AE0]
                mov     [rsp+0BB8h+var_2D8], rcx
                mov     [rsp+0BB8h+var_2D0], rax
                lea     rax, off_210CE540 ; "cannot advance past `remaining`: "
                mov     qword ptr [rsp+0BB8h+var_A58], rax
                mov     qword ptr [rsp+0BB8h+var_A58+8], 2
                mov     qword ptr [rsp+0BB8h+var_A38], 0
                lea     rax, [rsp+0BB8h+var_2E8]
                mov     qword ptr [rsp+0BB8h+var_A48], rax
                mov     qword ptr [rsp+0BB8h+var_A48+8], 2
                lea     rsi, off_210CE560 ; "/home/aothuatgiadp/.cargo/registry/src/"...
                lea     rdi, [rsp+0BB8h+var_A58]
                call    sub_4A5F0
; ---------------------------------------------------------------------------

loc_948A1:                              ; CODE XREF: sub_902F0+60E↑j
                                        ; sub_902F0+1D0E↑j ...
                ud2
; ---------------------------------------------------------------------------

loc_948A3:                              ; CODE XREF: sub_902F0+3550↑j
                lea     rdi, aAssertionFaile_1 ; "assertion failed: slot.is_none()"
                lea     rdx, off_210CCC58 ; "/home/aothuatgiadp/.cargo/registry/src/"...
                mov     esi, 20h ; ' '
                call    sub_4A710
; ---------------------------------------------------------------------------

loc_948BB:                              ; CODE XREF: sub_902F0+2C91↑j
                lea     rdx, off_210CE338 ; "/home/aothuatgiadp/.cargo/registry/src/"...
                mov     rsi, r14
                call    sub_4A595
; ---------------------------------------------------------------------------

loc_948CA:                              ; CODE XREF: sub_902F0+45C↑j
                mov     edi, 1
                mov     esi, 2000h
                call    sub_497D5
; ---------------------------------------------------------------------------

loc_948D9:                              ; CODE XREF: sub_902F0+34D↑j
                mov     edi, 1
                mov     rsi, r14
                call    sub_497D5
; ---------------------------------------------------------------------------

loc_948E6:                              ; CODE XREF: sub_902F0+2EAC↑j
                lea     rdx, off_210CD1E8 ; "/home/aothuatgiadp/.cargo/registry/src/"...
                mov     rsi, [rsp+0BB8h+var_A90]
                call    sub_4A595
; ---------------------------------------------------------------------------

loc_948FA:                              ; CODE XREF: sub_902F0+E1B↑j
                lea     rdi, off_210E6E88 ; "/home/aothuatgiadp/.rustup/toolchains/s"...
                call    sub_497F0
; ---------------------------------------------------------------------------

loc_94906:                              ; CODE XREF: sub_902F0+E3E↑j
                mov     edi, 1
                mov     rsi, r15
                call    sub_497D5
; ---------------------------------------------------------------------------

loc_94913:                              ; CODE XREF: sub_902F0+3CFC↑j
                mov     edi, 1
                mov     esi, 10h
                call    sub_497D5
; } // starts at 902F0
sub_902F0       endp

; ---------------------------------------------------------------------------
                align 10h

; =============== S U B R O U T I N E =======================================


sub_94930       proc near               ; CODE XREF: sub_9B0E0+CC7↓p

ptr             = qword ptr -90h
var_88          = qword ptr -88h
var_80          = qword ptr -80h
var_78          = qword ptr -78h
var_70          = qword ptr -70h
var_68          = qword ptr -68h
var_60          = qword ptr -60h
var_58          = qword ptr -58h
var_50          = xmmword ptr -50h
var_40          = xmmword ptr -40h

; __unwind {
                push    rbp
                push    r15
                push    r14
                push    r13
                push    r12
                push    rbx
                sub     rsp, 68h
                mov     rbx, rdi
                mov     r14, [rsi+28h]
                mov     r12, [rsi]
                mov     r10, [rsi+8]
                mov     rax, [rsi+10h]
                mov     rcx, 8000000000000000h
                mov     [rsi], rcx
                mov     rcx, r12
                neg     rcx
                mov     edx, 8
                mov     ecx, 2
                cmovo   rcx, rdx
                mov     r15, [rsi+30h]
                mov     rdx, [rsi+18h]
                mov     rbp, [rdx+18h]
                mov     rsi, [rdx+20h]
                mov     r13, [rdx+28h]
                cmp     r13, rsi
                jnb     loc_94A38
                lea     rdi, [rdx+18h]
                mov     r8, 100002600h

loc_9499C:                              ; CODE XREF: sub_94930+8C↓j
                movzx   r9d, byte ptr [rbp+r13+0]
                cmp     r9, 3Ah ; ':'
                ja      loc_94ACA
                bt      r8, r9
                jnb     short loc_949C8
                inc     r13
                mov     [rdx+28h], r13
                cmp     rsi, r13
                jnz     short loc_9499C
                mov     [rsp+98h+ptr], r10
                mov     r13, rsi
                jmp     short loc_94A3D
; ---------------------------------------------------------------------------

loc_949C8:                              ; CODE XREF: sub_94930+80↑j
                cmp     r9, 3Ah ; ':'
                jnz     loc_94ACA
                inc     r13
                mov     [rdx+28h], r13
                mov     [rsp+98h+var_80], rcx
                mov     [rsp+98h+var_78], r14
                mov     [rsp+98h+var_70], r12
                mov     [rsp+98h+var_68], r10
                mov     [rsp+98h+var_60], rax
                mov     [rsp+98h+var_58], r15
                lea     rdi, [rsp+98h+var_50]
                lea     rsi, [rsp+98h+var_80]
                call    sub_99E00
                cmp     byte ptr [rsp+98h+var_50], 6
                jnz     short loc_94A18

loc_94A0D:                              ; CODE XREF: sub_94930+189↓j
                                        ; sub_94930+195↓j
                mov     rdi, r15
                mov     rsi, r14
                call    sub_FB90C0

loc_94A18:                              ; CODE XREF: sub_94930+DB↑j
                movups  xmm0, [rsp+98h+var_50]
                movups  xmm1, [rsp+98h+var_40]
                movups  xmmword ptr [rbx+10h], xmm1
                movups  xmmword ptr [rbx], xmm0
                add     rsp, 68h
                pop     rbx
                pop     r12
                pop     r13
                pop     r14
                pop     r15
                pop     rbp
                retn
; ---------------------------------------------------------------------------

loc_94A38:                              ; CODE XREF: sub_94930+58↑j
                mov     [rsp+98h+ptr], r10

loc_94A3D:                              ; CODE XREF: sub_94930+96↑j
                mov     [rsp+98h+var_80], 3
                inc     r13
                cmp     r13, rsi
                cmovnb  r13, rsi
                mov     rdx, rbp
                add     rdx, r13
                mov     rax, cs:off_210E9038
                mov     edi, 0Ah
                mov     rsi, rbp
                call    rax ; sub_E7740
                test    al, 1
                jz      short loc_94A73
                sub     rdx, rbp
                inc     rdx
                jmp     short loc_94A75
; ---------------------------------------------------------------------------

loc_94A73:                              ; CODE XREF: sub_94930+139↑j
                xor     edx, edx

loc_94A75:                              ; CODE XREF: sub_94930+141↑j
                mov     [rsp+98h+var_88], rdx
                add     rdx, rbp
                mov     rax, cs:off_210E9040
                mov     edi, 0Ah
                mov     rsi, rbp
                call    rax ; sub_E8110
                lea     rsi, [rax+1]
                sub     r13, [rsp+98h+var_88]
                lea     rdi, [rsp+98h+var_80]
                mov     rdx, r13

loc_94A9F:                              ; CODE XREF: sub_94930+1B5↓j
                call    sub_4F030
                mov     qword ptr [rsp+98h+var_50+8], rax
                mov     byte ptr [rsp+98h+var_50], 6
                shl     r12, 1
                test    r12, r12
                mov     rdi, [rsp+98h+ptr] ; ptr
                jz      loc_94A0D
                call    cs:free_ptr
                jmp     loc_94A0D
; ---------------------------------------------------------------------------

loc_94ACA:                              ; CODE XREF: sub_94930+76↑j
                                        ; sub_94930+9C↑j
                mov     [rsp+98h+ptr], r10
                mov     [rsp+98h+var_80], 6
                call    sub_FB8860
                lea     rdi, [rsp+98h+var_80]
                mov     rsi, rax
                jmp     short loc_94A9F
; } // starts at 94930
sub_94930       endp

; ---------------------------------------------------------------------------
                align 10h

; =============== S U B R O U T I N E =======================================


sub_94AF0       proc near               ; CODE XREF: sub_57110+3D↑p
                                        ; sub_741F0+2E1F↑p

var_1F8         = byte ptr -1F8h
var_1E9         = byte ptr -1E9h
var_1E8         = xmmword ptr -1E8h
var_1D8         = xmmword ptr -1D8h
var_1C8         = qword ptr -1C8h
var_1B8         = xmmword ptr -1B8h
var_1A0         = xmmword ptr -1A0h
var_190         = xmmword ptr -190h
var_180         = xmmword ptr -180h
var_170         = xmmword ptr -170h
var_160         = xmmword ptr -160h
ptr             = qword ptr -150h
var_140         = qword ptr -140h
var_138         = dword ptr -138h
var_130         = qword ptr -130h
var_128         = qword ptr -128h
var_120         = qword ptr -120h
dest            = xmmword ptr -118h
var_108         = xmmword ptr -108h
var_F8          = xmmword ptr -0F8h
var_E8          = xmmword ptr -0E8h
var_D8          = xmmword ptr -0D8h
var_C8          = xmmword ptr -0C8h
var_B8          = xmmword ptr -0B8h
var_A8          = qword ptr -0A8h

; __unwind {
                push    rbp
                push    r15
                push    r14
                push    r13
                push    r12
                push    rbx
                sub     rsp, 1C8h
                mov     r14, rsi
                mov     rbx, rdi
                mov     r12, [rsi]
                cmp     r12, 6
                jnz     loc_94BA8
                mov     rax, [r14+8]
                mov     qword ptr [r14+8], 3
                cmp     rax, 3
                jz      loc_95321
                mov     qword ptr [rsp+1F8h+var_1B8], rax
                movups  xmm0, xmmword ptr [r14+10h]
                movdqu  xmm1, xmmword ptr [r14+20h]
                movdqu  xmm2, xmmword ptr [r14+30h]
                movdqu  xmm3, xmmword ptr [r14+40h]
                movups  [rsp+1F8h+var_1B8+8], xmm0
                movdqu  [rsp+1F8h+var_1A0], xmm1
                movdqu  [rsp+1F8h+var_190], xmm2
                movdqu  [rsp+1F8h+var_180], xmm3
                movups  xmm0, xmmword ptr [r14+50h]
                movups  [rsp+1F8h+var_170], xmm0
                movups  xmm0, xmmword ptr [r14+60h]
                movups  [rsp+1F8h+var_160], xmm0
                movdqu  xmm0, xmmword ptr [r14+70h]
                movdqu  xmmword ptr [rsp+1F8h+ptr], xmm0
                mov     rax, [r14+80h]
                mov     [rsp+1F8h+var_140], rax
                cmp     byte ptr [r14+121h], 0
                jnz     loc_94D18
                jmp     loc_95009
; ---------------------------------------------------------------------------

loc_94BA8:                              ; CODE XREF: sub_94AF0+1E↑j
                mov     ecx, r12d
                and     ecx, 0FFFFFFFEh
                lea     rsi, [r12-3]
                xor     eax, eax
                cmp     ecx, 4
                cmovz   rax, rsi
                test    rax, rax
                jz      short loc_94BD5
                cmp     rax, 1
                jnz     loc_95339
                mov     rsi, [r14+8]
                mov     r15, [r14+10h]
                jmp     short loc_94C54
; ---------------------------------------------------------------------------

loc_94BD5:                              ; CODE XREF: sub_94AF0+CF↑j
                mov     r15, [r14+0F0h]
                mov     rbp, [r14+0F8h]
                mov     rdi, r15
                mov     r13, rdx
                mov     rsi, rdx
                call    qword ptr [rbp+18h]
                test    al, al
                jnz     short loc_94C6E
                mov     qword ptr [r14], 3
                cmp     r12d, 3
                jz      loc_95375
                lea     rsi, [r14+8]    ; src
                lea     rdi, [rsp+1F8h+dest] ; dest
                mov     [rsp+1F8h+var_120], r12
                mov     edx, 0E8h       ; n
                call    cs:memcpy_ptr
                lea     rsi, [rsp+1F8h+var_120]
                mov     rdi, r15
                call    qword ptr [rbp+20h]
                mov     r12, rax
                mov     r15, rdx
                mov     rdi, r14
                call    sub_63B00
                mov     rsi, r12
                mov     qword ptr [r14], 4
                mov     [r14+8], r12
                mov     [r14+10h], r15
                mov     rdx, r13

loc_94C54:                              ; CODE XREF: sub_94AF0+E3↑j
                lea     rdi, [rsp+1F8h+var_120]
                call    qword ptr [r15+18h]
                mov     r15, [rsp+1F8h+var_120]
                cmp     r15, 3
                jnz     short loc_94C7A

loc_94C6E:                              ; CODE XREF: sub_94AF0+101↑j
                mov     qword ptr [rbx], 3
                jmp     loc_95068
; ---------------------------------------------------------------------------

loc_94C7A:                              ; CODE XREF: sub_94AF0+17C↑j
                mov     rax, [rsp+1F8h+var_A8]
                mov     [rsp+1F8h+var_140], rax
                movups  xmm0, [rsp+1F8h+var_B8]
                movups  xmmword ptr [rsp+1F8h+ptr], xmm0
                movups  xmm0, [rsp+1F8h+var_C8]
                movups  [rsp+1F8h+var_160], xmm0
                movups  xmm0, [rsp+1F8h+var_D8]
                movups  [rsp+1F8h+var_170], xmm0
                movdqu  xmm0, [rsp+1F8h+dest]
                movdqu  xmm1, [rsp+1F8h+var_108]
                movdqu  xmm2, [rsp+1F8h+var_F8]
                movdqu  xmm3, [rsp+1F8h+var_E8]
                movdqu  [rsp+1F8h+var_180], xmm3
                movdqu  [rsp+1F8h+var_190], xmm2
                movdqu  [rsp+1F8h+var_1A0], xmm1
                movdqu  [rsp+1F8h+var_1B8+8], xmm0
                mov     rdi, r14
                call    sub_63B00
                mov     qword ptr [r14], 5
                mov     qword ptr [rsp+1F8h+var_1B8], r15
                cmp     byte ptr [r14+121h], 0
                jz      loc_95009

loc_94D18:                              ; CODE XREF: sub_94AF0+AD↑j
                mov     rbp, [r14+100h]
                mov     r12, [r14+108h]
                mov     r15, [r14+110h]
                mov     r13, [r14+118h]
                mov     qword ptr [r14+100h], 0
                test    rbp, rbp
                jz      loc_94F83
                lea     rsi, qword_1003660
                lea     rdi, [rsp+1F8h+var_1B8]
                call    sub_B79E0
                test    al, al
                jz      short loc_94D6E
                mov     rdi, r13
                mov     rsi, r12
                mov     rdx, r15
                call    qword ptr [rbp+20h]
                jmp     loc_94F83
; ---------------------------------------------------------------------------

loc_94D6E:                              ; CODE XREF: sub_94AF0+26B↑j
                test    r15, r15
                jz      loc_94F15
                cmp     r15, 8
                jnb     short loc_94D87
                xor     edx, edx
                mov     rcx, r12
                jmp     loc_94ED9
; ---------------------------------------------------------------------------

loc_94D87:                              ; CODE XREF: sub_94AF0+28B↑j
                cmp     r15, 20h ; ' '
                jnb     short loc_94D96
                xor     eax, eax
                xor     edx, edx
                jmp     loc_94E4B
; ---------------------------------------------------------------------------

loc_94D96:                              ; CODE XREF: sub_94AF0+29B↑j
                mov     rax, r15
                and     rax, 0FFFFFFFFFFFFFFE0h
                pxor    xmm0, xmm0
                xor     ecx, ecx
                movdqa  xmm2, cs:xmmword_10000C0
                movdqa  xmm3, cs:xmmword_10000D0
                movdqa  xmm4, cs:xmmword_10000E0
                pxor    xmm1, xmm1
                nop

loc_94DC0:                              ; CODE XREF: sub_94AF0+334↓j
                movdqu  xmm5, xmmword ptr [r12+rcx]
                movdqu  xmm6, xmmword ptr [r12+rcx+10h]
                movdqa  xmm7, xmm5
                pminub  xmm7, xmm2
                pcmpeqb xmm7, xmm5
                movdqa  xmm8, xmm6
                pminub  xmm8, xmm2
                pcmpeqb xmm8, xmm6
                movdqa  xmm9, xmm5
                pcmpeqb xmm9, xmm3
                por     xmm9, xmm7
                movdqa  xmm7, xmm6
                pcmpeqb xmm7, xmm3
                por     xmm7, xmm8
                pcmpeqb xmm5, xmm4
                pandn   xmm5, xmm9
                por     xmm0, xmm5
                pcmpeqb xmm6, xmm4
                pandn   xmm6, xmm7
                por     xmm1, xmm6
                add     rcx, 20h ; ' '
                cmp     rax, rcx
                jnz     short loc_94DC0
                por     xmm1, xmm0
                psllw   xmm1, 7
                pmovmskb ecx, xmm1
                test    ecx, ecx
                setnz   dl
                cmp     r15, rax
                jz      loc_94F0C
                test    r15b, 18h
                jz      loc_94ED3

loc_94E4B:                              ; CODE XREF: sub_94AF0+2A1↑j
                mov     rsi, r15
                and     rsi, 0FFFFFFFFFFFFFFF8h
                lea     rcx, [r12+rsi]
                movzx   edx, dl
                movd    xmm0, edx
                movdqa  xmm1, cs:xmmword_10000F0
                pcmpeqd xmm2, xmm2
                movdqa  xmm3, cs:xmmword_1000100
                movdqa  xmm4, cs:xmmword_1000110
                nop     dword ptr [rax+00000000h]

loc_94E80:                              ; CODE XREF: sub_94AF0+3C9↓j
                movq    xmm5, qword ptr [r12+rax]
                movdqa  xmm6, xmm5
                pmaxub  xmm6, xmm1
                pcmpeqb xmm6, xmm5
                pxor    xmm6, xmm2
                movdqa  xmm7, xmm5
                pcmpeqb xmm7, xmm3
                por     xmm7, xmm6
                pcmpeqb xmm5, xmm4
                pandn   xmm5, xmm7
                punpcklbw xmm5, xmm5
                por     xmm0, xmm5
                add     rax, 8
                cmp     rsi, rax
                jnz     short loc_94E80
                psllw   xmm0, 7
                pmovmskb eax, xmm0
                test    eax, 5555h
                setnz   dl
                cmp     r15, rsi
                jnz     short loc_94ED9
                jmp     short loc_94F0C
; ---------------------------------------------------------------------------

loc_94ED3:                              ; CODE XREF: sub_94AF0+355↑j
                add     rax, r12
                mov     rcx, rax

loc_94ED9:                              ; CODE XREF: sub_94AF0+292↑j
                                        ; sub_94AF0+3DF↑j
                lea     rax, [r12+r15]
                nop     dword ptr [rax]

loc_94EE0:                              ; CODE XREF: sub_94AF0+41A↓j
                movzx   esi, byte ptr [rcx]
                inc     rcx
                cmp     sil, 20h ; ' '
                setb    dil
                cmp     sil, 7Fh
                setz    r8b
                or      r8b, dil
                cmp     sil, 9
                setnz   sil
                and     sil, r8b
                or      dl, sil
                cmp     rcx, rax
                jnz     short loc_94EE0

loc_94F0C:                              ; CODE XREF: sub_94AF0+34B↑j
                                        ; sub_94AF0+3E1↑j
                test    dl, 1
                jnz     loc_9538D

loc_94F15:                              ; CODE XREF: sub_94AF0+281↑j
                mov     qword ptr [rsp+1F8h+var_1E8], rbp
                mov     qword ptr [rsp+1F8h+var_1E8+8], r12
                mov     qword ptr [rsp+1F8h+var_1D8], r15
                mov     qword ptr [rsp+1F8h+var_1D8+8], r13
                mov     byte ptr [rsp+1F8h+var_1C8], 0
                lea     rdx, qword_1003660
                lea     rdi, [rsp+1F8h+var_120]
                lea     rsi, [rsp+1F8h+var_1B8]
                lea     rcx, [rsp+1F8h+var_1E8]
                call    sub_B51F0
                movzx   eax, byte ptr [rsp+1F8h+var_108+8]
                cmp     al, 3
                jz      loc_95351
                cmp     al, 2
                jz      short loc_94F83
                mov     rax, [rsp+1F8h+var_120]
                mov     rsi, qword ptr [rsp+1F8h+dest]
                mov     rdx, qword ptr [rsp+1F8h+dest+8]
                mov     rdi, qword ptr [rsp+1F8h+var_108]
                call    qword ptr [rax+20h]

loc_94F83:                              ; CODE XREF: sub_94AF0+252↑j
                                        ; sub_94AF0+279↑j ...
                mov     rsi, [rsp+1F8h+ptr+8]
                mov     rax, [rsp+1F8h+var_140]
                lea     rdi, [rsp+1F8h+var_138]
                call    qword ptr [rax+28h]
                lea     rsi, xmmword_10037C0
                lea     rdi, [rsp+1F8h+var_1B8]
                call    sub_B79E0
                test    al, al
                jz      loc_9507A

loc_94FB7:                              ; CODE XREF: sub_94AF0+592↓j
                                        ; sub_94AF0+5A8↓j ...
                cmp     byte ptr [r14+120h], 1
                jnz     short loc_95009
                mov     r14, [rsp+1F8h+ptr+8]
                mov     r15, [rsp+1F8h+var_140]
                mov     rax, [r15]
                test    rax, rax
                jz      short loc_94FDE
                mov     rdi, r14
                call    rax

loc_94FDE:                              ; CODE XREF: sub_94AF0+4E7↑j
                cmp     qword ptr [r15+8], 0
                jz      short loc_94FEE
                mov     rdi, r14        ; ptr
                call    cs:free_ptr

loc_94FEE:                              ; CODE XREF: sub_94AF0+4F3↑j
                mov     [rsp+1F8h+ptr+8], 1
                lea     rax, qword_210C9878
                mov     [rsp+1F8h+var_140], rax

loc_95009:                              ; CODE XREF: sub_94AF0+B3↑j
                                        ; sub_94AF0+222↑j ...
                mov     rax, [rsp+1F8h+ptr+8]
                mov     [rbx+70h], rax
                mov     rax, [rsp+1F8h+var_140]
                mov     [rbx+78h], rax
                movups  xmm0, [rsp+1F8h+var_160+8]
                movups  xmmword ptr [rbx+60h], xmm0
                movups  xmm0, [rsp+1F8h+var_170+8]
                movups  xmmword ptr [rbx+50h], xmm0
                movups  xmm0, [rsp+1F8h+var_180+8]
                movups  xmmword ptr [rbx+40h], xmm0
                movups  xmm0, [rsp+1F8h+var_1B8]
                movups  xmm1, xmmword ptr [rsp+50h]
                movups  xmm2, [rsp+1F8h+var_1A0+8]
                movups  xmm3, [rsp+1F8h+var_190+8]
                movups  xmmword ptr [rbx+30h], xmm3
                movups  xmmword ptr [rbx+20h], xmm2
                movups  xmmword ptr [rbx+10h], xmm1
                movups  xmmword ptr [rbx], xmm0

loc_95068:                              ; CODE XREF: sub_94AF0+185↑j
                add     rsp, 1C8h
                pop     rbx
                pop     r12
                pop     r13
                pop     r14
                pop     r15
                pop     rbp
                retn
; ---------------------------------------------------------------------------

loc_9507A:                              ; CODE XREF: sub_94AF0+4C1↑j
                cmp     [rsp+1F8h+var_138], 1
                jnz     loc_94FB7
                mov     rdi, [rsp+1F8h+var_128]
                cmp     rdi, [rsp+1F8h+var_130]
                jnz     loc_94FB7
                test    rdi, rdi
                jz      short loc_950D0
                lea     rsi, [rsp+1F8h+var_120]
                call    sub_E6490
                mov     r15, rax
                sub     r15, 14h
                jnz     short loc_950F9
                xor     eax, eax
                lea     rcx, off_210C9908
                mov     r13d, 1
                xor     r15d, r15d
                jmp     loc_952AE
; ---------------------------------------------------------------------------

loc_950D0:                              ; CODE XREF: sub_94AF0+5B1↑j
                mov     rax, cs:qword_210C9658
                mov     [rsp+1F8h+var_1C8], rax
                movups  xmm0, xmmword ptr cs:qword_210C9648
                movaps  [rsp+1F8h+var_1D8], xmm0
                movups  xmm0, xmmword ptr cs:off_210C9638
                movaps  [rsp+1F8h+var_1E8], xmm0
                jmp     loc_952C7
; ---------------------------------------------------------------------------

loc_950F9:                              ; CODE XREF: sub_94AF0+5C7↑j
                lea     r12, [rsp+rax+1F8h+var_1F8]
                add     r12, 0D8h
                cmp     rax, 10h
                jbe     short loc_95111
                xor     esi, esi
                jmp     loc_95230
; ---------------------------------------------------------------------------

loc_95111:                              ; CODE XREF: sub_94AF0+618↑j
                mov     ecx, 14h
                sub     rcx, rax
                cmp     eax, 4
                jbe     short loc_95124
                xor     edx, edx
                xor     esi, esi
                jmp     short loc_951A3
; ---------------------------------------------------------------------------

loc_95124:                              ; CODE XREF: sub_94AF0+62C↑j
                mov     edx, ecx
                and     edx, 0FFFFFFF0h
                pxor    xmm0, xmm0
                xor     esi, esi
                movdqa  xmm1, cs:xmmword_10000C0
                movdqa  xmm2, cs:xmmword_10000D0
                movdqa  xmm3, cs:xmmword_10000E0
                nop     word ptr [rax+rax+00000000h]

