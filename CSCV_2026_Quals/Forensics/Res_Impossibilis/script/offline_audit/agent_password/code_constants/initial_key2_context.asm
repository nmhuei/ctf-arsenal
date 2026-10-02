
OFFSET 0xcc51d0c4
cc51d084: 8548fc               test dword ptr [rax - 4], ecx
cc51d087: ff                   .byte 0xff
cc51d088: ff                   .byte 0xff
cc51d089: e8f0e1f7ff           call 0xcc49b27e
cc51d08e: 4889c5               mov rbp, rax
cc51d091: 4885c0               test rax, rax
cc51d094: 0f84b1020000         je 0xcc51d34b
cc51d09a: 4c8d742440           lea r14, [rsp + 0x40]
cc51d09f: be0b000000           mov esi, 0xb
cc51d0a4: 4c89f7               mov rdi, r14
cc51d0a7: e872edf7ff           call 0xcc49be1e
cc51d0ac: 85c0                 test eax, eax
cc51d0ae: 0f856b020000         jne 0xcc51d31f
cc51d0b4: 4889ef               mov rdi, rbp
cc51d0b7: 498d5d50             lea rbx, [r13 + 0x50]
cc51d0bb: e85ed0f7ff           call 0xcc49a11e
cc51d0c0: 41c7455890785634     mov dword ptr [r13 + 0x58], 0x34567890
cc51d0c8: 48b97856341289674523 movabs rcx, 0x2345678912345678
cc51d0d2: 4889442408           mov qword ptr [rsp + 8], rax
cc51d0d7: 49894d50             mov qword ptr [r13 + 0x50], rcx
cc51d0db: 4885c0               test rax, rax
cc51d0de: 0f842c020000         je 0xcc51d310
cc51d0e4: 4989ef               mov r15, rbp
cc51d0e7: 0f1f8000000000       nop dword ptr [rax]
cc51d0ee: 410fb637             movzx esi, byte ptr [r15]
cc51d0f2: 4889df               mov rdi, rbx
cc51d0f5: 4983c701             add r15, 1
cc51d0f9: e81038fcff           call 0xcc4e090e
cc51d0fe: 4889ea               mov rdx, rbp
cc51d101: 4c29fa               sub rdx, r15
cc51d104: 4803542408           add rdx, qword ptr [rsp + 8]
cc51d109: 75e3                 jne 0xcc51d0ee
cc51d10b: 418b5558             mov edx, dword ptr [r13 + 0x58]
cc51d10f: 410fb6455d           movzx eax, byte ptr [r13 + 0x5d]
cc51d114: 4531ff               xor r15d, r15d
cc51d117: 488d6c2460           lea rbp, [rsp + 0x60]
cc51d11c: 8844244b             mov byte ptr [rsp + 0x4b], al
cc51d120: eb08                 jmp 0xcc51d12a
cc51d122: 0f1f4000             nop dword ptr [rax]
cc51d126: 418b5558             mov edx, dword ptr [r13 + 0x58]
cc51d12a: 83ca02               or edx, 2
cc51d12d: 430fb6343e           movzx esi, byte ptr [r14 + r15]
cc51d132: 4889df               mov rdi, rbx
cc51d135: 89d0                 mov eax, edx
cc51d137: 83f001               xor eax, 1
cc51d13a: 0fafc2               imul eax, edx
cc51d13d: c1e808               shr eax, 8
cc51d140: 31f0                 xor eax, esi
cc51d142: 42                   .byte 0x42
cc51d143: 88                   .byte 0x88

OFFSET 0xcc51d311
cc51d2d1: f7ff                 idiv edi
cc51d2d3: 85c0                 test eax, eax
cc51d2d5: 0f8593fdffff         jne 0xcc51d06e
cc51d2db: 498b8510010000       mov rax, qword ptr [r13 + 0x110]
cc51d2e2: 41c685d000000001     mov byte ptr [r13 + 0xd0], 1
cc51d2ea: 41c685c000000001     mov byte ptr [r13 + 0xc0], 1
cc51d2f2: 488d440302           lea rax, [rbx + rax + 2]
cc51d2f7: 49898510010000       mov qword ptr [r13 + 0x110], rax
cc51d2fe: 498b4518             mov rax, qword ptr [r13 + 0x18]
cc51d302: 488d440302           lea rax, [rbx + rax + 2]
cc51d307: 49894518             mov qword ptr [r13 + 0x18], rax
cc51d30b: e9c1f9ffff           jmp 0xcc51ccd1
cc51d310: ba90785634           mov edx, 0x34567890
cc51d315: e9f5fdffff           jmp 0xcc51d10f
cc51d31a: e82fdcf7ff           call 0xcc49af4e
cc51d31f: 31c0                 xor eax, eax
cc51d321: 488d15e6840100       lea rdx, [rip + 0x184e6]
cc51d328: 83ceff               or esi, 0xffffffff
cc51d32b: 4c89e7               mov rdi, r12
cc51d32e: e8bbe3f7ff           call 0xcc49b6ee
cc51d333: b8e2ffffff           mov eax, 0xffffffe2
cc51d338: 4898                 cdqe 
cc51d33a: e91cfbffff           jmp 0xcc51ce5b
cc51d33f: 488d15c8390100       lea rdx, [rip + 0x139c8]
cc51d346: e906fdffff           jmp 0xcc51d051
cc51d34b: 488d153a7f0100       lea rdx, [rip + 0x17f3a]
cc51d352: e9fafcffff           jmp 0xcc51d051
cc51d357: 0f1f8000000000       nop dword ptr [rax]
cc51d35e: 4156                 push r14
cc51d360: 4155                 push r13
cc51d362: 4531ed               xor r13d, r13d
cc51d365: 4154                 push r12
cc51d367: 41bc10000000         mov r12d, 0x10
cc51d36d: 53                   push rbx
cc51d36e: 4881ece8000000       sub rsp, 0xe8
cc51d375: 64488b042528000000   mov rax, qword ptr fs:[0x28]
cc51d37e: 48898424d8000000     mov qword ptr [rsp + 0xd8], rax
cc51d386: 31c0                 xor eax, eax
cc51d388: 83ff02               cmp edi, 2
cc51d38b: 4c8d742470           lea r14, [rsp + 0x70]
cc51d390: b8                   .byte 0xb8

OFFSET 0xcc7ad083
cc7ad043: 0000                 add byte ptr [rax], al
cc7ad045: 0000                 add byte ptr [rax], al
cc7ad047: 0000                 add byte ptr [rax], al
cc7ad049: 0000                 add byte ptr [rax], al
cc7ad04b: 0000                 add byte ptr [rax], al
cc7ad04d: 0000                 add byte ptr [rax], al
cc7ad04f: 0000                 add byte ptr [rax], al
cc7ad051: 0000                 add byte ptr [rax], al
cc7ad053: 0000                 add byte ptr [rax], al
cc7ad055: 0000                 add byte ptr [rax], al
cc7ad057: 0000                 add byte ptr [rax], al
cc7ad059: 0000                 add byte ptr [rax], al
cc7ad05b: 0000                 add byte ptr [rax], al
cc7ad05d: 0000                 add byte ptr [rax], al
cc7ad05f: 0000                 add byte ptr [rax], al
cc7ad061: 0000                 add byte ptr [rax], al
cc7ad063: 0000                 add byte ptr [rax], al
cc7ad065: 0000                 add byte ptr [rax], al
cc7ad067: 0000                 add byte ptr [rax], al
cc7ad069: 0000                 add byte ptr [rax], al
cc7ad06b: 0000                 add byte ptr [rax], al
cc7ad06d: 0000                 add byte ptr [rax], al
cc7ad06f: 0000                 add byte ptr [rax], al
cc7ad071: 0000                 add byte ptr [rax], al
cc7ad073: 0000                 add byte ptr [rax], al
cc7ad075: 0000                 add byte ptr [rax], al
cc7ad077: 0000                 add byte ptr [rax], al
cc7ad079: 0000                 add byte ptr [rax], al
cc7ad07b: 0000                 add byte ptr [rax], al
cc7ad07d: 0028                 add byte ptr [rax], ch
cc7ad07f: 88f7                 mov bh, dh
cc7ad081: e6d5                 out 0xd5, al
cc7ad083: 90                   nop 
cc7ad084: 7856                 js 0xcc7ad0dc
cc7ad086: 3492                 xor al, 0x92
cc7ad088: 20de                 and dh, bl
cc7ad08a: 9b                   wait 
cc7ad08b: 57                   push rdi
cc7ad08c: 43e259               loop 0xcc7ad0e8
cc7ad08f: d108                 ror dword ptr [rax], 1
cc7ad091: c7                   .byte 0xc7
cc7ad092: 7bf3                 jnp 0xcc7ad087
cc7ad094: 6a48                 push 0x48
cc7ad096: 3c2b                 cmp al, 0x2b
cc7ad098: 1a4110               sbb al, byte ptr [rcx + 0x10]
cc7ad09b: ef                   out dx, eax
cc7ad09c: cdab                 int 0xab
cc7ad09e: 21f1                 and ecx, esi
cc7ad0a0: ac                   lodsb al, byte ptr [rsi]
cc7ad0a1: 68e440bc37           push 0x37bc40e4
cc7ad0a6: af                   scasd eax, dword ptr [rdi]
cc7ad0a7: 86c4                 xchg ah, al
cc7ad0a9: b3a2                 mov bl, 0xa2
cc7ad0ab: 1103                 adc dword ptr [rbx], eax
cc7ad0ad: f1                   int1 
cc7ad0ae: debc1a12cf8a46       fidivr word ptr [rdx + rbx + 0x468acf12]
cc7ad0b5: 0ac4                 or al, ah
cc7ad0b7: 7bf3                 jnp 0xcc7ad0ac
cc7ad0b9: 6a48                 push 0x48
cc7ad0bb: 3c2b                 cmp al, 0x2b
cc7ad0bd: 1a21                 sbb ah, byte ptr [rcx]
cc7ad0bf: 10ef                 adc bh, ch
cc7ad0c1: cdab                 int 0xab
cc7ad0c3: 21f1                 and ecx, esi
cc7ad0c5: ac                   lodsb al, byte ptr [rsi]
cc7ad0c6: 686440bc37           push 0x37bc4064
cc7ad0cb: af                   scasd eax, dword ptr [rdi]
cc7ad0cc: 86c4                 xchg ah, al
cc7ad0ce: b3a2                 mov bl, 0xa2
cc7ad0d0: 1101                 adc dword ptr [rcx], eax
cc7ad0d2: f1                   int1 
cc7ad0d3: debc1a12cf8a46       fidivr word ptr [rdx + rbx + 0x468acf12]
cc7ad0da: 02c4                 add al, ah
cc7ad0dc: 7bf3                 jnp 0xcc7ad0d1
cc7ad0de: 6a48                 push 0x48
cc7ad0e0: 3c2b                 cmp al, 0x2b
cc7ad0e2: 1a01                 sbb al, byte ptr [rcx]
cc7ad0e4: 10ef                 adc bh, ch
cc7ad0e6: cdab                 int 0xab
cc7ad0e8: 21f1                 and ecx, esi
cc7ad0ea: ac                   lodsb al, byte ptr [rsi]
cc7ad0eb: 68e420de9b           push -0x6421df1c
cc7ad0f0: 57                   push rdi
cc7ad0f1: 43e259               loop 0xcc7ad14d
cc7ad0f4: d18841bc37af         ror dword ptr [rax - 0x50c843bf], 1
cc7ad0fa: 06                   .byte 0x06
cc7ad0fb: 80fca8               cmp ah, 0xa8
cc7ad0fe: 30fa                 xor dl, bh
cc7ad100: f0                   .byte 0xf0
cc7ad101: 0d                   .byte 0x0d
cc7ad102: 50                   push rax

OFFSET 0x10b90ee8e
10b90ee4e: e8db95ffff           call 0x10b90842e
10b90ee53: e960faffff           jmp 0x10b90e8b8
10b90ee58: 8b83c8000000         mov eax, dword ptr [rbx + 0xc8]
10b90ee5e: 8902                 mov dword ptr [rdx], eax
10b90ee60: e95ffeffff           jmp 0x10b90ecc4
10b90ee65: e8f430a705           call 0x111381f5e
10b90ee6a: 48898370010100       mov qword ptr [rbx + 0x10170], rax
10b90ee71: 48c7835801010078563412 mov qword ptr [rbx + 0x10158], 0x12345678
10b90ee7c: 48c7836001010089674523 mov qword ptr [rbx + 0x10160], 0x23456789
10b90ee87: 48c7836801010090785634 mov qword ptr [rbx + 0x10168], 0x34567890
10b90ee92: 488b4db0             mov rcx, qword ptr [rbp - 0x50]
10b90ee96: 408a39               mov dil, byte ptr [rcx]
10b90ee99: 4084ff               test dil, dil
10b90ee9c: 7478                 je 0x10b90ef16
10b90ee9e: 48ff45b0             inc qword ptr [rbp - 0x50]
10b90eea2: b978563412           mov ecx, 0x12345678
10b90eea7: be89674523           mov esi, 0x23456789
10b90eeac: ba90785634           mov edx, 0x34567890
10b90eeb1: 4189c8               mov r8d, ecx
10b90eeb4: 4130f8               xor r8b, dil
10b90eeb7: 410fb6f8             movzx edi, r8b
10b90eebb: 8b3cb8               mov edi, dword ptr [rax + rdi*4]
10b90eebe: 48c1e908             shr rcx, 8
10b90eec2: 4831f9               xor rcx, rdi
10b90eec5: 48898b58010100       mov qword ptr [rbx + 0x10158], rcx
10b90eecc: 0fb6f9               movzx edi, cl
10b90eecf: 4801f7               add rdi, rsi
10b90eed2: 4869f705840808       imul rsi, rdi, 0x8088405
10b90eed9: 48ffc6               inc rsi
10b90eedc: 4889b360010100       mov qword ptr [rbx + 0x10160], rsi
10b90eee3: 89f7                 mov edi, esi
10b90eee5: c1ef18               shr edi, 0x18
10b90eee8: 4189d0               mov r8d, edx
10b90eeeb: 4131f8               xor r8d, edi
10b90eeee: 410fb6f8             movzx edi, r8b
10b90eef2: 8b3cb8               mov edi, dword ptr [rax + rdi*4]
10b90eef5: 48c1ea08             shr rdx, 8
10b90eef9: 4831fa               xor rdx, rdi
10b90eefc: 48899368010100       mov qword ptr [rbx + 0x10168], rdx
10b90ef03: 4c8b45b0             mov r8, qword ptr [rbp - 0x50]
10b90ef07: 418a38               mov dil, byte ptr [r8]
10b90ef0a: 49ffc0               inc r8
10b90ef0d: 4c                   .byte 0x4c

OFFSET 0x10b90eead
10b90ee6d: 7001                 jo 0x10b90ee70
10b90ee6f: 0100                 add dword ptr [rax], eax
10b90ee71: 48c7835801010078563412 mov qword ptr [rbx + 0x10158], 0x12345678
10b90ee7c: 48c7836001010089674523 mov qword ptr [rbx + 0x10160], 0x23456789
10b90ee87: 48c7836801010090785634 mov qword ptr [rbx + 0x10168], 0x34567890
10b90ee92: 488b4db0             mov rcx, qword ptr [rbp - 0x50]
10b90ee96: 408a39               mov dil, byte ptr [rcx]
10b90ee99: 4084ff               test dil, dil
10b90ee9c: 7478                 je 0x10b90ef16
10b90ee9e: 48ff45b0             inc qword ptr [rbp - 0x50]
10b90eea2: b978563412           mov ecx, 0x12345678
10b90eea7: be89674523           mov esi, 0x23456789
10b90eeac: ba90785634           mov edx, 0x34567890
10b90eeb1: 4189c8               mov r8d, ecx
10b90eeb4: 4130f8               xor r8b, dil
10b90eeb7: 410fb6f8             movzx edi, r8b
10b90eebb: 8b3cb8               mov edi, dword ptr [rax + rdi*4]
10b90eebe: 48c1e908             shr rcx, 8
10b90eec2: 4831f9               xor rcx, rdi
10b90eec5: 48898b58010100       mov qword ptr [rbx + 0x10158], rcx
10b90eecc: 0fb6f9               movzx edi, cl
10b90eecf: 4801f7               add rdi, rsi
10b90eed2: 4869f705840808       imul rsi, rdi, 0x8088405
10b90eed9: 48ffc6               inc rsi
10b90eedc: 4889b360010100       mov qword ptr [rbx + 0x10160], rsi
10b90eee3: 89f7                 mov edi, esi
10b90eee5: c1ef18               shr edi, 0x18
10b90eee8: 4189d0               mov r8d, edx
10b90eeeb: 4131f8               xor r8d, edi
10b90eeee: 410fb6f8             movzx edi, r8b
10b90eef2: 8b3cb8               mov edi, dword ptr [rax + rdi*4]
10b90eef5: 48c1ea08             shr rdx, 8
10b90eef9: 4831fa               xor rdx, rdi
10b90eefc: 48899368010100       mov qword ptr [rbx + 0x10168], rdx
10b90ef03: 4c8b45b0             mov r8, qword ptr [rbp - 0x50]
10b90ef07: 418a38               mov dil, byte ptr [r8]
10b90ef0a: 49ffc0               inc r8
10b90ef0d: 4c8945b0             mov qword ptr [rbp - 0x50], r8
10b90ef11: 4084ff               test dil, dil
10b90ef14: 759b                 jne 0x10b90eeb1
10b90ef16: 488b7360             mov rsi, qword ptr [rbx + 0x60]
10b90ef1a: 488b8348010100       mov rax, qword ptr [rbx + 0x10148]
10b90ef21: 488b9030010000       mov rdx, qword ptr [rax + 0x130]
10b90ef28: 48035078             add rdx, qword ptr [rax + 0x78]
10b90ef2c: 48                   .byte 0x48

OFFSET 0x12585e281
12585e241: 3b35eba32173         cmp esi, dword ptr [rip + 0x7321a3eb]
12585e247: bae1ed28a6           mov edx, 0xa628ede1
12585e24c: a081caac222b13f43a   movabs al, byte ptr [0x3af4132b22acca81]
12585e255: 9a                   .byte 0x9a
12585e256: 52                   push rdx
12585e257: 12a0f703c679         adc ah, byte ptr [rax + 0x79c603f7]
12585e25d: 9d                   popfq 
12585e25e: 59                   pop rcx
12585e25f: ea                   .byte 0xea
12585e260: 7acc                 jp 0x12585e22e
12585e262: a2281c6fa5412448c2   movabs byte ptr [0xc2482441a56f1c28], al
12585e26b: ea                   .byte 0xea
12585e26c: 59                   pop rcx
12585e26d: 5f                   pop rdi
12585e26e: dfea                 fucompi st(2)
12585e270: d6                   .byte 0xd6
12585e271: 98                   cwde 
12585e272: b9abb3ba84           mov ecx, 0x84bab3ab
12585e277: 93                   xchg ebx, eax
12585e278: ba9a3e65bc           mov edx, 0xbc653e9a
12585e27d: c897c71b             enter -0x3869, 0x1b
12585e281: 90                   nop 
12585e282: 7856                 js 0x12585e2da
12585e284: 341b                 xor al, 0x1b
12585e286: ed                   in eax, dx
12585e287: 19c4                 sbb esp, eax
12585e289: 4ee399               jrcxz 0x12585e225
12585e28c: 860e                 xchg byte ptr [rsi], cl
12585e28e: 52                   push rdx
12585e28f: c6                   .byte 0xc6
12585e290: e2b0                 loop 0x12585e242
12585e292: e86275f007           call 0x12d7657f9
12585e297: 57                   push rdi
12585e298: 4731bef9cec3fd       xor dword ptr [r14 - 0x23c3107], r15d
12585e29f: 5f                   pop rdi
12585e2a0: 9d                   popfq 
12585e2a1: 62                   .byte 0x62
12585e2a2: 804d1b5d             or byte ptr [rbp + 0x1b], 0x5d
12585e2a6: 83df5d               sbb edi, 0x5d
12585e2a9: d6                   .byte 0xd6
12585e2aa: 17                   .byte 0x17
12585e2ab: 5e                   pop rsi
12585e2ac: daad1ad8cb64         fisubr dword ptr [rbp + 0x64cbd81a]
12585e2b2: f1                   int1 
12585e2b3: be94eb4055           mov esi, 0x5540eb94
12585e2b8: af                   scasd eax, dword ptr [rdi]
12585e2b9: 432df06cd5f4         sub eax, 0xf4d56cf0
12585e2bf: 4b8af1               mov sil, r9b
12585e2c2: 96                   xchg esi, eax
12585e2c3: 27                   .byte 0x27
12585e2c4: 8177eb3605d512       xor dword ptr [rdi - 0x15], 0x12d50536
12585e2cb: 227d81               and bh, byte ptr [rbp - 0x7f]
12585e2ce: e3e8                 jrcxz 0x12585e2b8
12585e2d0: b77e                 mov bh, 0x7e
12585e2d2: 68f5321320           push 0x201332f5
12585e2d7: 6aa2                 push -0x5e
12585e2d9: 010441               add dword ptr [rcx + rax*2], eax
12585e2dc: 9b                   wait 
12585e2dd: 82                   .byte 0x82
12585e2de: e912f88195           jmp 0xbb07daf5
12585e2e3: 0a99617a085c         or bl, byte ptr [rcx + 0x5c087a61]
12585e2e9: 13c3                 adc eax, ebx
12585e2eb: 8f                   .byte 0x8f
12585e2ec: fb                   sti 
12585e2ed: 0aa5c64fa3f4         or ah, byte ptr [rbp - 0xb5cb03a]
12585e2f3: 719e                 jno 0x12585e293
12585e2f5: 35e8329293           xor eax, 0x939232e8
12585e2fa: f5                   cmc 
12585e2fb: 6580c927             or cl, 0x27
12585e2ff: f6fe                 idiv dh

OFFSET 0x14fbf43b7
14fbf4377: d1d1                 rcl ecx, 1
14fbf4379: d1e1                 shl ecx, 1
14fbf437b: bfa3a3a3a3           mov edi, 0xa3a3a3a3
14fbf4380: a3a3a3e3a7b210efcd   movabs dword ptr [0xcdef10b2a7e3a3a3], eax
14fbf4389: ab                   stosd dword ptr [rdi], eax
14fbf438a: 43e259               loop 0x14fbf43e6
14fbf438d: d18842bc37af         ror dword ptr [rax - 0x50c843be], 1
14fbf4393: 0e                   .byte 0x0e
14fbf4394: 896745               mov dword ptr [rdi + 0x45], esp
14fbf4397: 23ef                 and ebp, edi
14fbf4399: cdab                 int 0xab
14fbf439b: 43e259               loop 0x14fbf43f7
14fbf439e: d14842               ror dword ptr [rax + 0x42], 1
14fbf43a1: bc37af0e89           mov esp, 0x890eaf37
14fbf43a6: 67452308             and r9d, dword ptr [r8d]
14fbf43aa: f1                   int1 
14fbf43ab: debc3a249e158d       fidivr word ptr [rdx + rdi - 0x72ea61dc]
14fbf43b2: 1cc4                 sbb al, 0xc4
14fbf43b4: 7bf3                 jnp 0x14fbf43a9
14fbf43b6: ea                   .byte 0xea
14fbf43b7: 90                   nop 
14fbf43b8: 7856                 js 0x14fbf4410
14fbf43ba: 3462                 xor al, 0x62
14fbf43bc: 10ef                 adc bh, ch
14fbf43be: cdab                 int 0xab
14fbf43c0: 43e259               loop 0x14fbf441c
14fbf43c3: d14841               ror dword ptr [rax + 0x41], 1
14fbf43c6: bc37af0e89           mov esp, 0x890eaf37
14fbf43cb: 67452304f1           and r8d, dword ptr [r9d + esi*8]
14fbf43d0: debc3a249e158d       fidivr word ptr [rdx + rdi - 0x72ea61dc]
14fbf43d7: 0cc4                 or al, 0xc4
14fbf43d9: 7bf3                 jnp 0x14fbf43ce
14fbf43db: ea                   .byte 0xea
14fbf43dc: 90                   nop 
14fbf43dd: 7856                 js 0x14fbf4435
14fbf43df: 3422                 xor al, 0x22
14fbf43e1: 10ef                 adc bh, ch
14fbf43e3: cdab                 int 0xab
14fbf43e5: 43e259               loop 0x14fbf4441
14fbf43e8: d14840               ror dword ptr [rax + 0x40], 1
14fbf43eb: bc37af0e89           mov esp, 0x890eaf37
14fbf43f0: 67452300             and r8d, dword ptr [r8d]
14fbf43f4: f1                   int1 
14fbf43f5: debc1a80c9a820       fidivr word ptr [rdx + rbx + 0x20a8c980]
14fbf43fc: fc                   cld 
14fbf43fd: e0d7                 loopne 0x14fbf43d6
14fbf43ff: 2042e3               and byte ptr [rdx - 0x1d], al
14fbf4402: 0311                 add edx, dword ptr [rcx]
14fbf4404: 8d1b                 lea ebx, [rbx]
14fbf4406: 1921                 sbb dword ptr [rcx], esp
14fbf4408: 1dd0b5da86           sbb eax, 0x86dab5d0
14fbf440d: 9b                   wait 
14fbf440e: 8c68dc               mov word ptr [rax - 0x24], gs
14fbf4411: c848c34d             enter -0x3cb8, 0x4d
14fbf4415: 8c                   .byte 0x8c
14fbf4416: 346e                 xor al, 0x6e
14fbf4418: 6424e3               and al, 0xe3
14fbf441b: 46690cbc1100240f     imul r9d, dword ptr [rsp + r15*4], 0xf240011
14fbf4423: 2030                 and byte ptr [rax], dh
14fbf4425: 4050                 push rax
14fbf4427: 60                   .byte 0x60
14fbf4428: 7080                 jo 0x14fbf43aa
14fbf442a: 90                   nop 
14fbf442b: a0b0c0d0e0f000f310   movabs al, byte ptr [0x10f300f0e0d0c0b0]
14fbf4434: 2030                 and byte ptr [rax], dh
14fbf4436: 40                   .byte 0x40

OFFSET 0x14fbf43dc
14fbf439c: e259                 loop 0x14fbf43f7
14fbf439e: d14842               ror dword ptr [rax + 0x42], 1
14fbf43a1: bc37af0e89           mov esp, 0x890eaf37
14fbf43a6: 67452308             and r9d, dword ptr [r8d]
14fbf43aa: f1                   int1 
14fbf43ab: debc3a249e158d       fidivr word ptr [rdx + rdi - 0x72ea61dc]
14fbf43b2: 1cc4                 sbb al, 0xc4
14fbf43b4: 7bf3                 jnp 0x14fbf43a9
14fbf43b6: ea                   .byte 0xea
14fbf43b7: 90                   nop 
14fbf43b8: 7856                 js 0x14fbf4410
14fbf43ba: 3462                 xor al, 0x62
14fbf43bc: 10ef                 adc bh, ch
14fbf43be: cdab                 int 0xab
14fbf43c0: 43e259               loop 0x14fbf441c
14fbf43c3: d14841               ror dword ptr [rax + 0x41], 1
14fbf43c6: bc37af0e89           mov esp, 0x890eaf37
14fbf43cb: 67452304f1           and r8d, dword ptr [r9d + esi*8]
14fbf43d0: debc3a249e158d       fidivr word ptr [rdx + rdi - 0x72ea61dc]
14fbf43d7: 0cc4                 or al, 0xc4
14fbf43d9: 7bf3                 jnp 0x14fbf43ce
14fbf43db: ea                   .byte 0xea
14fbf43dc: 90                   nop 
14fbf43dd: 7856                 js 0x14fbf4435
14fbf43df: 3422                 xor al, 0x22
14fbf43e1: 10ef                 adc bh, ch
14fbf43e3: cdab                 int 0xab
14fbf43e5: 43e259               loop 0x14fbf4441
14fbf43e8: d14840               ror dword ptr [rax + 0x40], 1
14fbf43eb: bc37af0e89           mov esp, 0x890eaf37
14fbf43f0: 67452300             and r8d, dword ptr [r8d]
14fbf43f4: f1                   int1 
14fbf43f5: debc1a80c9a820       fidivr word ptr [rdx + rbx + 0x20a8c980]
14fbf43fc: fc                   cld 
14fbf43fd: e0d7                 loopne 0x14fbf43d6
14fbf43ff: 2042e3               and byte ptr [rdx - 0x1d], al
14fbf4402: 0311                 add edx, dword ptr [rcx]
14fbf4404: 8d1b                 lea ebx, [rbx]
14fbf4406: 1921                 sbb dword ptr [rcx], esp
14fbf4408: 1dd0b5da86           sbb eax, 0x86dab5d0
14fbf440d: 9b                   wait 
14fbf440e: 8c68dc               mov word ptr [rax - 0x24], gs
14fbf4411: c848c34d             enter -0x3cb8, 0x4d
14fbf4415: 8c                   .byte 0x8c
14fbf4416: 346e                 xor al, 0x6e
14fbf4418: 6424e3               and al, 0xe3
14fbf441b: 46690cbc1100240f     imul r9d, dword ptr [rsp + r15*4], 0xf240011
14fbf4423: 2030                 and byte ptr [rax], dh
14fbf4425: 4050                 push rax
14fbf4427: 60                   .byte 0x60
14fbf4428: 7080                 jo 0x14fbf43aa
14fbf442a: 90                   nop 
14fbf442b: a0b0c0d0e0f000f310   movabs al, byte ptr [0x10f300f0e0d0c0b0]
14fbf4434: 2030                 and byte ptr [rax], dh
14fbf4436: 4050                 push rax
14fbf4438: 60                   .byte 0x60
14fbf4439: 7080                 jo 0x14fbf43bb
14fbf443b: 90                   nop 
14fbf443c: a0b0c0d0e0f000f410   movabs al, byte ptr [0x10f400f0e0d0c0b0]
14fbf4445: 2030                 and byte ptr [rax], dh
14fbf4447: 4050                 push rax
14fbf4449: 60                   .byte 0x60
14fbf444a: 7080                 jo 0x14fbf43cc
14fbf444c: f4                   hlt 
14fbf444d: 50                   push rax
14fbf444e: ff01                 inc dword ptr [rcx]
14fbf4450: 5a                   pop rdx
14fbf4451: a2d69f63b059aea36c   movabs byte ptr [0x6ca3ae59b0639fd6], al
14fbf445a: c0                   .byte 0xc0
14fbf445b: 5a                   pop rdx

OFFSET 0x185043fd4
185043f94: f4                   hlt 
185043f95: 833ab2               cmp dword ptr [rdx], -0x4e
185043f98: f5                   cmc 
185043f99: 07                   .byte 0x07
185043f9a: 92                   xchg edx, eax
185043f9b: b31a                 mov bl, 0x1a
185043f9d: 55                   push rbp
185043f9e: c3                   ret 
185043f9f: 02753f               add dh, byte ptr [rbp + 0x3f]
185043fa2: 93                   xchg ebx, eax
185043fa3: 43                   .byte 0x43
185043fa4: ea                   .byte 0xea
185043fa5: 0e                   .byte 0x0e
185043fa6: 22f4                 and dh, ah
185043fa8: 3ed0c9               ror cl, 1
185043fab: d6                   .byte 0xd6
185043fac: 3030                 xor byte ptr [rax], dh
185043fae: 0b77f0               or esi, dword ptr [rdi - 0x10]
185043fb1: cc                   int3 
185043fb2: 6809d0e83a           push 0x3ae8d009
185043fb7: f5                   cmc 
185043fb8: bab7aff252           mov edx, 0x52f2afb7
185043fbd: 5c                   pop rsp
185043fbe: 036e88               add ebp, dword ptr [rsi - 0x78]
185043fc1: a00f4b46b61cb646b6   movabs al, byte ptr [0xb646b61cb6464b0f]
185043fca: ff6870               jmp ptr [rax + 0x70]
185043fcd: 019682ddd9bd         add dword ptr [rsi - 0x4226227e], edx
185043fd3: 19907856342f         sbb dword ptr [rax + 0x2f345678], edx
185043fd9: 8c                   .byte 0x8c
185043fda: 388f05a96025         cmp byte ptr [rdi + 0x2560a905], cl
185043fe0: dd4715               fld qword ptr [rdi + 0x15]
185043fe3: 3147a0               xor dword ptr [rdi - 0x60], eax
185043fe6: f4                   hlt 
185043fe7: 59                   pop rcx
185043fe8: 27                   .byte 0x27
185043fe9: 5b                   pop rbx
185043fea: a7                   cmpsd dword ptr [rsi], dword ptr [rdi]
185043feb: 3a79fe               cmp bh, byte ptr [rcx - 2]
185043fee: b1d9                 mov cl, 0xd9
185043ff0: 75eb                 jne 0x185043fdd
185043ff2: 2f                   .byte 0x2f
185043ff3: 7014                 jo 0x185044009
185043ff5: 27                   .byte 0x27
185043ff6: 4a4ff8               clc 
185043ff9: 639d03c714af         movsxd ebx, dword ptr [rbp - 0x50eb38fd]
185043fff: e0dc                 loopne 0x185043fdd
185044001: 1d119dd6ab           sbb eax, 0xabd69d11
185044006: 16                   .byte 0x16
185044007: 2e687e51c738         push 0x38c7517e
18504400d: 3c42                 cmp al, 0x42
18504400f: 60                   .byte 0x60
185044010: 885401b3             mov byte ptr [rcx + rax - 0x4d], dl
185044014: 41d1b25e132ced       sal dword ptr [r10 - 0x12d3eca2], 1
18504401b: 840c76               test byte ptr [rsi + rsi*2], cl
18504401e: d95dcd               fstp dword ptr [rbp - 0x33]
185044021: 05355de387           add eax, 0x87e35d35
185044026: f9                   stc 
185044027: 88db                 mov bl, bl
185044029: bcee0adb25           mov esp, 0x25db0aee
18504402e: 46eb34               jmp 0x185044065
185044031: 8a23                 mov ah, byte ptr [rbx]
185044033: 06                   .byte 0x06
185044034: b512                 mov ch, 0x12
185044036: 8e28                 mov gs, word ptr [rax]
185044038: d04064               rol byte ptr [rax + 0x64], 1
18504403b: 8db9378e3590         lea edi, [rcx - 0x6fca71c9]
185044041: 1592e5b026           adc eax, 0x26b0e592
185044046: e9a73da96f           jmp 0x1f4ad7df2
18504404b: f1                   int1 
18504404c: 491cb3               sbb al, 0xb3
18504404f: 708f                 jo 0x185043fe0
185044051: c8                   .byte 0xc8
185044052: 17                   .byte 0x17
185044053: 02                   .byte 0x02

OFFSET 0x19af16c11
19af16bd1: 89c1                 mov ecx, eax
19af16bd3: 31c0                 xor eax, eax
19af16bd5: f7d9                 neg ecx
19af16bd7: 19c0                 sbb eax, eax
19af16bd9: eb09                 jmp 0x19af16be4
19af16bdb: 0fb645e7             movzx eax, byte ptr [rbp - 0x19]
19af16bdf: 418907               mov dword ptr [r15], eax
19af16be2: 31c0                 xor eax, eax
19af16be4: 4883c408             add rsp, 8
19af16be8: 5b                   pop rbx
19af16be9: 415e                 pop r14
19af16beb: 415f                 pop r15
19af16bed: 5d                   pop rbp
19af16bee: c3                   ret 
19af16bef: 670fb9               ud1 
19af16bf2: 4002670f             add spl, byte ptr [rdi + 0xf]
19af16bf6: b94002cccc           mov ecx, 0xcccc0240
19af16bfb: cc                   int3 
19af16bfc: cc                   int3 
19af16bfd: cc                   int3 
19af16bfe: 48c70678563412       mov qword ptr [rsi], 0x12345678
19af16c05: 48c7460889674523     mov qword ptr [rsi + 8], 0x23456789
19af16c0d: 48c7461090785634     mov qword ptr [rsi + 0x10], 0x34567890
19af16c15: 448a0f               mov r9b, byte ptr [rdi]
19af16c18: 4584c9               test r9b, r9b
19af16c1b: 7470                 je 0x19af16c8d
19af16c1d: 55                   push rbp
19af16c1e: 4889e5               mov rbp, rsp
19af16c21: 48ffc7               inc rdi
19af16c24: b878563412           mov eax, 0x12345678
19af16c29: 41b889674523         mov r8d, 0x23456789
19af16c2f: b990785634           mov ecx, 0x34567890
19af16c34: 4189c2               mov r10d, eax
19af16c37: 4530ca               xor r10b, r9b
19af16c3a: 450fb6ca             movzx r9d, r10b
19af16c3e: 468b0c8a             mov r9d, dword ptr [rdx + r9*4]
19af16c42: 48c1e808             shr rax, 8
19af16c46: 4c31c8               xor rax, r9
19af16c49: 488906               mov qword ptr [rsi], rax
19af16c4c: 440fb6c8             movzx r9d, al
19af16c50: 4d01c1               add r9, r8
19af16c53: 4d69c105840808       imul r8, r9, 0x8088405
19af16c5a: 49ffc0               inc r8
19af16c5d: 4c894608             mov qword ptr [rsi + 8], r8
19af16c61: 4589c1               mov r9d, r8d
19af16c64: 41c1e918             shr r9d, 0x18
19af16c68: 4189ca               mov r10d, ecx
19af16c6b: 4531ca               xor r10d, r9d
19af16c6e: 450fb6ca             movzx r9d, r10b
19af16c72: 468b0c8a             mov r9d, dword ptr [rdx + r9*4]
19af16c76: 48c1e908             shr rcx, 8
19af16c7a: 4c31c9               xor rcx, r9
19af16c7d: 48894e10             mov qword ptr [rsi + 0x10], rcx
19af16c81: 448a0f               mov r9b, byte ptr [rdi]
19af16c84: 48ffc7               inc rdi
19af16c87: 4584c9               test r9b, r9b
19af16c8a: 75a8                 jne 0x19af16c34
19af16c8c: 5d                   pop rbp
19af16c8d: c3                   ret 
19af16c8e: 55                   push rbp
19af16c8f: 48                   .byte 0x48
19af16c90: 89                   .byte 0x89

OFFSET 0x19af16c30
19af16bf0: 0fb9                 ud1 
19af16bf2: 4002670f             add spl, byte ptr [rdi + 0xf]
19af16bf6: b94002cccc           mov ecx, 0xcccc0240
19af16bfb: cc                   int3 
19af16bfc: cc                   int3 
19af16bfd: cc                   int3 
19af16bfe: 48c70678563412       mov qword ptr [rsi], 0x12345678
19af16c05: 48c7460889674523     mov qword ptr [rsi + 8], 0x23456789
19af16c0d: 48c7461090785634     mov qword ptr [rsi + 0x10], 0x34567890
19af16c15: 448a0f               mov r9b, byte ptr [rdi]
19af16c18: 4584c9               test r9b, r9b
19af16c1b: 7470                 je 0x19af16c8d
19af16c1d: 55                   push rbp
19af16c1e: 4889e5               mov rbp, rsp
19af16c21: 48ffc7               inc rdi
19af16c24: b878563412           mov eax, 0x12345678
19af16c29: 41b889674523         mov r8d, 0x23456789
19af16c2f: b990785634           mov ecx, 0x34567890
19af16c34: 4189c2               mov r10d, eax
19af16c37: 4530ca               xor r10b, r9b
19af16c3a: 450fb6ca             movzx r9d, r10b
19af16c3e: 468b0c8a             mov r9d, dword ptr [rdx + r9*4]
19af16c42: 48c1e808             shr rax, 8
19af16c46: 4c31c8               xor rax, r9
19af16c49: 488906               mov qword ptr [rsi], rax
19af16c4c: 440fb6c8             movzx r9d, al
19af16c50: 4d01c1               add r9, r8
19af16c53: 4d69c105840808       imul r8, r9, 0x8088405
19af16c5a: 49ffc0               inc r8
19af16c5d: 4c894608             mov qword ptr [rsi + 8], r8
19af16c61: 4589c1               mov r9d, r8d
19af16c64: 41c1e918             shr r9d, 0x18
19af16c68: 4189ca               mov r10d, ecx
19af16c6b: 4531ca               xor r10d, r9d
19af16c6e: 450fb6ca             movzx r9d, r10b
19af16c72: 468b0c8a             mov r9d, dword ptr [rdx + r9*4]
19af16c76: 48c1e908             shr rcx, 8
19af16c7a: 4c31c9               xor rcx, r9
19af16c7d: 48894e10             mov qword ptr [rsi + 0x10], rcx
19af16c81: 448a0f               mov r9b, byte ptr [rdi]
19af16c84: 48ffc7               inc rdi
19af16c87: 4584c9               test r9b, r9b
19af16c8a: 75a8                 jne 0x19af16c34
19af16c8c: 5d                   pop rbp
19af16c8d: c3                   ret 
19af16c8e: 55                   push rbp
19af16c8f: 4889e5               mov rbp, rsp
19af16c92: 53                   push rbx
19af16c93: 50                   push rax
19af16c94: 48837f2800           cmp qword ptr [rdi + 0x28], 0
19af16c99: 740e                 je 0x19af16ca9
19af16c9b: 4889fb               mov rbx, rdi
19af16c9e: e8dbce5ff6           call 0x191513b7e
19af16ca3: 48394338             cmp qword ptr [rbx + 0x38], rax
19af16ca7: 7e07                 jle 0x19af16cb0
19af16ca9: 4883c408             add rsp, 8
19af16cad: 5b                   pop rbx
19af16cae: 5d                   pop rbp
19af16caf: c3                   ret 
