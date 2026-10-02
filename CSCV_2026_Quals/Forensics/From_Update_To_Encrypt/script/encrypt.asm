            ; CALL XREF from fcn.00405c90 @ 0x405ddc(x)
┌ 2993: fcn.00404fa0 ();
│ afv: vars(61:sp[0x10..0x25c])
│           0x00404fa0      55             push ebp
│           0x00404fa1      8bec           mov ebp, esp
│           0x00404fa3      6aff           push 0xffffffffffffffff
│           0x00404fa5      68cdd84100     push 0x41d8cd
│           0x00404faa      64a100000000   mov eax, dword fs:[0]
│           0x00404fb0      50             push eax
│           0x00404fb1      81ec18010000   sub esp, 0x118
│           0x00404fb7      a108804200     mov eax, dword [0x428008]   ; [0x428008:4]=0xbb40e64e
│           0x00404fbc      33c5           xor eax, ebp
│           0x00404fbe      8945ec         mov dword [var_14h], eax
│           0x00404fc1      53             push ebx
│           0x00404fc2      56             push esi
│           0x00404fc3      57             push edi
│           0x00404fc4      50             push eax
│           0x00404fc5      8d45f4         lea eax, [var_ch]
│           0x00404fc8      64a300000000   mov dword fs:[0], eax
│           0x00404fce      8965f0         mov dword [var_10h], esp
│           0x00404fd1      899504ffffff   mov dword [var_fch], edx
│           0x00404fd7      8b4508         mov eax, dword [var_8h]
│           0x00404fda      0f57c0         xorps xmm0, xmm0
│           0x00404fdd      8985dcfeffff   mov dword [pbSecret], eax
│           0x00404fe3      8b450c         mov eax, dword [var_ch_2]
│           0x00404fe6      660fd645b0     movq qword [var_50h], xmm0
│           0x00404feb      c745b80000..   mov dword [var_48h], 0
│           0x00404ff2      898508ffffff   mov dword [var_f8h], eax
│           0x00404ff8      c78558ffff..   mov dword [hObject], 0xffffffff ; -1
│           0x00405002      c78564ffff..   mov dword [hFile], 0xffffffff ; -1
│           0x0040500c      c78560ffff..   mov dword [lpBuffer], 0
│           0x00405016      c78550ffff..   mov dword [var_b0h], 0
│           0x00405020      c745b00000..   mov dword [var_50h], 0
│           0x00405027      c745b40000..   mov dword [cbInput], 0
│           0x0040502e      c745b80000..   mov dword [var_48h], 0
│           0x00405035      c745fc0000..   mov dword [var_4h], 0
│           0x0040503c      660fd645c8     movq qword [var_38h], xmm0
│           0x00405041      c745d00000..   mov dword [var_30h], 0
│           0x00405048      c7855cffff..   mov dword [phAlgorithm], 0
│           0x00405052      c78554ffff..   mov dword [phKey], 0
│           0x0040505c      c745c80000..   mov dword [var_38h], 0
│           0x00405063      c745cc0000..   mov dword [var_34h], 0
│           0x0040506a      c745d00000..   mov dword [var_30h], 0
│           0x00405071      c645fc01       mov byte [var_4h], 1
│           0x00405075      8d8560ffffff   lea eax, [lpBuffer]
│           0x0040507b      83791408       cmp dword [ecx + 0x14], 8
│           0x0040507f      8985e0feffff   mov dword [var_120h], eax
│           0x00405085      8d8550ffffff   lea eax, [var_b0h]
│           0x0040508b      8985e4feffff   mov dword [var_11ch], eax
│           0x00405091      8d45b0         lea eax, [var_50h]
│           0x00405094      8985e8feffff   mov dword [var_118h], eax
│           0x0040509a      8d8554ffffff   lea eax, [phKey]
│           0x004050a0      8985ecfeffff   mov dword [var_114h], eax
│           0x004050a6      8d855cffffff   lea eax, [phAlgorithm]
│           0x004050ac      8985f0feffff   mov dword [var_110h], eax
│           0x004050b2      8d45c8         lea eax, [var_38h]
│           0x004050b5      8985f4feffff   mov dword [var_10ch], eax
│           0x004050bb      8d8558ffffff   lea eax, [hObject]
│           0x004050c1      8985f8feffff   mov dword [var_108h], eax
│           0x004050c7      8d8564ffffff   lea eax, [hFile]
│           0x004050cd      8985fcfeffff   mov dword [var_104h], eax
│           0x004050d3      8d4584         lea eax, [var_7ch]
│           0x004050d6      0f114584       movups xmmword [var_7ch], xmm0
│           0x004050da      898500ffffff   mov dword [var_100h], eax
│       ┌─< 0x004050e0      7202           jb 0x4050e4
│       │   0x004050e2      8b09           mov ecx, dword [ecx]
│       │   ; CODE XREF from fcn.00404fa0 @ 0x4050e0(x)
│       └─> 0x004050e4      6a00           push 0
│           0x004050e6      6800000028     push 0x28000000
│           0x004050eb      6a03           push 3                      ; 3
│           0x004050ed      6a00           push 0
│           0x004050ef      6a01           push 1                      ; 1 ; DWORD dwShareMode
│           0x004050f1      6800000080     push 0x80000000             ; DWORD dwDesiredAccess
│           0x004050f6      51             push ecx                    ; LPCWSTR lpFileName
│           0x004050f7      ff1518e04100   call dword [sym.imp.KERNEL32.dll_CreateFileW] ; 0x41e018 ; "Zi\x02" ; HANDLE CreateFileW(LPCWSTR lpFileName, DWORD dwDesiredAccess, DWORD dwShareMode, LPSECURITY_ATTRIBUTES lpSecurityAttributes, DWORD dwCreationDisposition, DWORD dwFlagsAndAttributes, HANDLE hTemplateFile)
│           0x004050fd      898558ffffff   mov dword [hObject], eax
│           0x00405103      83f8ff         cmp eax, 0xffffffff
│       ┌─< 0x00405106      751a           jne 0x405122
│       │   0x00405108      68a8464200     push str.____CreateFile_input_failed_n ; 0x4246a8 ; "[-] CreateFile input failed\n"
│       │   0x0040510d      6a02           push 2                      ; 2
│       │   0x0040510f      e827890000     call fcn.0040da3b
│       │   0x00405114      83c404         add esp, 4
│       │   0x00405117      50             push eax
│       │   0x00405118      e803bfffff     call fcn.00401020
│      ┌──< 0x0040511d      e972060000     jmp 0x405794
│      ││   ; CODE XREF from fcn.00404fa0 @ 0x405106(x)
│      │└─> 0x00405122      6a1c           push 0x1c                   ; 28 ; DWORD dwBufferSize
│      │    0x00405124      8d8d68ffffff   lea ecx, [lpFileInformation]
│      │    0x0040512a      c745800000..   mov dword [var_80h], 0
│      │    0x00405131      51             push ecx                    ; LPVOID lpFileInformation
│      │    0x00405132      0f57c0         xorps xmm0, xmm0
│      │    0x00405135      6a10           push 0x10                   ; 16 ; FILE_INFO_BY_HANDLE_CLASS FileInformationClass
│      │    0x00405137      50             push eax                    ; HANDLE hFile
│      │    0x00405138      0f118568ff..   movups xmmword [lpFileInformation], xmm0
│      │    0x0040513f      660fd68578..   movq qword [var_88h], xmm0
│      │    0x00405147      ff1504e04100   call dword [sym.imp.KERNEL32.dll_GetFileInformationByHandleEx] ; 0x41e004 ; BOOL GetFileInformationByHandleEx(HANDLE hFile, FILE_INFO_BY_HANDLE_CLASS FileInformationClass, LPVOID lpFileInformation, DWORD dwBufferSize)
│      │    0x0040514d      85c0           test eax, eax
│      │┌─< 0x0040514f      0f84c0090000   je 0x405b15
│      ││   0x00405155      8bb568ffffff   mov esi, dword [lpFileInformation]
│      ││   0x0040515b      8d46ff         lea eax, [esi - 1]
│      ││   0x0040515e      3dffff0000     cmp eax, 0xffff
│     ┌───< 0x00405163      0f87ac090000   ja 0x405b15
│     │││   0x00405169      85f6           test esi, esi
│    ┌────< 0x0040516b      0f84a4090000   je 0x405b15
│    ││││   0x00405171      8d4594         lea eax, [lpFileSize]
│    ││││   0x00405174      0f57c0         xorps xmm0, xmm0
│    ││││   0x00405177      50             push eax                    ; PLARGE_INTEGER lpFileSize
│    ││││   0x00405178      ffb558ffffff   push dword [hObject]        ; HANDLE hFile
│    ││││   0x0040517e      660f134594     movlpd qword [lpFileSize], xmm0
│    ││││   0x00405183      ff1508e04100   call dword [sym.imp.KERNEL32.dll_GetFileSizeEx] ; 0x41e008 ; " i\x02" ; BOOL GetFileSizeEx(HANDLE hFile, PLARGE_INTEGER lpFileSize)
│    ││││   0x00405189      85c0           test eax, eax
│   ┌─────< 0x0040518b      750a           jne 0x405197
│   │││││   0x0040518d      68e4464200     push str.____GetFileSizeEx_failed_n ; 0x4246e4 ; "[-] GetFileSizeEx failed\n"
│  ┌──────< 0x00405192      e95b090000     jmp 0x405af2
│  ││││││   ; CODE XREF from fcn.00404fa0 @ 0x40518b(x)
│  │└─────> 0x00405197      8b7d94         mov edi, dword [lpFileSize]
│  │ ││││   0x0040519a      8bcf           mov ecx, edi
│  │ ││││   0x0040519c      8b4598         mov eax, dword [var_68h]
│  │ ││││   0x0040519f      83c1ff         add ecx, 0xffffffff
│  │ ││││   0x004051a2      83d0ff         adc eax, 0xffffffff
│  │ ││││   0x004051a5      85c0           test eax, eax
│  │┌─────< 0x004051a7      0f8740090000   ja 0x405aed
│ ┌───────< 0x004051ad      7209           jb 0x4051b8
│ │││││││   0x004051af      83f9fe         cmp ecx, 0xfffffffe
│ ────────< 0x004051b2      0f8735090000   ja 0x405aed
│ │││││││   ; CODE XREF from fcn.00404fa0 @ 0x4051ad(x)
│ └───────> 0x004051b8      8d8effff0000   lea ecx, [esi + 0xffff]
│  ││││││   0x004051be      89bd0cffffff   mov dword [var_f4h], edi
│  ││││││   0x004051c4      8bc1           mov eax, ecx
│  ││││││   0x004051c6      33d2           xor edx, edx
│  ││││││   0x004051c8      f7f6           div esi
│  ││││││   0x004051ca      6a04           push 4                      ; 4
│  ││││││   0x004051cc      2bca           sub ecx, edx
│  ││││││   0x004051ce      6800300000     push 0x3000
│  ││││││   0x004051d3      51             push ecx
│  ││││││   0x004051d4      6a00           push 0
│  ││││││   0x004051d6      898d50ffffff   mov dword [var_b0h], ecx
│  ││││││   0x004051dc      ff1514e04100   call dword [sym.imp.KERNEL32.dll_VirtualAlloc] ; 0x41e014 ; "Ji\x02" ; LPVOID VirtualAlloc(LPVOID lpAddress, SIZE_T dwSize, DWORD flAllocationType, DWORD flProtect)
│  ││││││   0x004051e2      898560ffffff   mov dword [lpBuffer], eax
│  ││││││   0x004051e8      85c0           test eax, eax
│ ┌───────< 0x004051ea      750a           jne 0x4051f6
│ │││││││   0x004051ec      6818474200     push str.____VirtualAlloc_read__failed_n ; 0x424718 ; "[-] VirtualAlloc(read) failed\n"
│ ────────< 0x004051f1      e9fc080000     jmp 0x405af2
│ │││││││   ; CODE XREF from fcn.00404fa0 @ 0x4051ea(x)
│ └───────> 0x004051f6      c645fc02       mov byte [var_4h], 2
│  ││││││   0x004051fa      8b45b8         mov eax, dword [var_48h]
│  ││││││   0x004051fd      2b45b0         sub eax, dword [var_50h]
│  ││││││   0x00405200      3bf8           cmp edi, eax
│ ┌───────< 0x00405202      7615           jbe 0x405219
│ │││││││   0x00405204      81ffffffff7f   cmp edi, 0x7fffffff
│ ────────< 0x0040520a      0f875b090000   ja 0x405b6b
│ │││││││   0x00405210      57             push edi
│ │││││││   0x00405211      8d4db0         lea ecx, [var_50h]
│ │││││││   0x00405214      e8d72b0000     call fcn.00407df0
│ │││││││   ; CODE XREF from fcn.00404fa0 @ 0x405202(x)
│ └───────> 0x00405219      33c0           xor eax, eax
│  ││││││   0x0040521b      c745fc0100..   mov dword [var_4h], 1
│  ││││││   0x00405222      89850cffffff   mov dword [var_f4h], eax
│  ││││││   0x00405228      85ff           test edi, edi
│ ┌───────< 0x0040522a      0f8486000000   je 0x4052b6
│ │││││││   ; CODE XREF from fcn.00404fa0 @ 0x4052b0(x)
│ ────────> 0x00405230      8b8d68ffffff   mov ecx, dword [lpFileInformation]
│ │││││││   0x00405236      ba00000100     mov edx, 0x10000
│ │││││││   0x0040523b      8bf7           mov esi, edi
│ │││││││   0x0040523d      c745a80000..   mov dword [lpNumberOfBytesRead], 0
│ │││││││   0x00405244      2bf0           sub esi, eax
│ │││││││   0x00405246      3bf2           cmp esi, edx
│ │││││││   0x00405248      6a00           push 0
│ │││││││   0x0040524a      0f47f2         cmova esi, edx
│ │││││││   0x0040524d      49             dec ecx
│ │││││││   0x0040524e      03ce           add ecx, esi
│ │││││││   0x00405250      33d2           xor edx, edx
│ │││││││   0x00405252      8bc1           mov eax, ecx
│ │││││││   0x00405254      f7b568ffffff   div dword [lpFileInformation]
│ │││││││   0x0040525a      8d45a8         lea eax, [lpNumberOfBytesRead]
│ │││││││   0x0040525d      50             push eax                    ; LPDWORD lpNumberOfBytesRead
│ │││││││   0x0040525e      2bca           sub ecx, edx
│ │││││││   0x00405260      51             push ecx                    ; DWORD nNumberOfBytesToRead
│ │││││││   0x00405261      ffb560ffffff   push dword [lpBuffer]       ; LPVOID lpBuffer
│ │││││││   0x00405267      ffb558ffffff   push dword [hObject]        ; HANDLE hFile
│ │││││││   0x0040526d      ff1500e04100   call dword [sym.imp.KERNEL32.dll_ReadFile] ; 0x41e000 ; BOOL ReadFile(HANDLE hFile, LPVOID lpBuffer, DWORD nNumberOfBytesToRead, LPDWORD lpNumberOfBytesRead, LPOVERLAPPED lpOverlapped)
│ │││││││   0x00405273      85c0           test eax, eax
│ ────────< 0x00405275      0f84b2000000   je 0x40532d
│ │││││││   0x0040527b      3975a8         cmp dword [lpNumberOfBytesRead], esi
│ ────────< 0x0040527e      0f829f000000   jb 0x405323
│ │││││││   0x00405284      8b8d60ffffff   mov ecx, dword [lpBuffer]
│ │││││││   0x0040528a      ffb504ffffff   push dword [var_fch]
│ │││││││   0x00405290      8d040e         lea eax, [esi + ecx]
│ │││││││   0x00405293      50             push eax
│ │││││││   0x00405294      51             push ecx
│ │││││││   0x00405295      ff75b4         push dword [cbInput]
│ │││││││   0x00405298      8d4db0         lea ecx, [var_50h]
│ │││││││   0x0040529b      e880450000     call fcn.00409820
│ │││││││   0x004052a0      8b850cffffff   mov eax, dword [var_f4h]
│ │││││││   0x004052a6      03c6           add eax, esi
│ │││││││   0x004052a8      89850cffffff   mov dword [var_f4h], eax
│ │││││││   0x004052ae      3bc7           cmp eax, edi
│ ────────< 0x004052b0      0f827affffff   jb 0x405230
│ │││││││   ; CODE XREF from fcn.00404fa0 @ 0x40522a(x)
│ └───────> 0x004052b6      ffb558ffffff   push dword [hObject]        ; HANDLE hObject
│  ││││││   0x004052bc      ff151ce04100   call dword [sym.imp.KERNEL32.dll_CloseHandle] ; 0x41e01c ; "hi\x02" ; BOOL CloseHandle(HANDLE hObject)
│  ││││││   0x004052c2      6a00           push 0
│  ││││││   0x004052c4      6a00           push 0
│  ││││││   0x004052c6      6898474200     push 0x424798               ; LPCWSTR pszAlgId
│  ││││││   0x004052cb      8d855cffffff   lea eax, [phAlgorithm]
│  ││││││   0x004052d1      c78558ffff..   mov dword [hObject], 0xffffffff ; -1
│  ││││││   0x004052db      50             push eax                    ; BCRYPT_ALG_HANDLE *phAlgorithm
│  ││││││   0x004052dc      ff1574e14100   call dword [sym.imp.bcrypt.dll_BCryptOpenAlgorithmProvider] ; 0x41e174 ; NTSTATUS BCryptOpenAlgorithmProvider(BCRYPT_ALG_HANDLE *phAlgorithm, LPCWSTR pszAlgId, LPCWSTR pszImplementation, ULONG dwFlags)
│  ││││││   0x004052e2      85c0           test eax, eax
│ ┌───────< 0x004052e4      0f84e6000000   je 0x4053d0
│ │││││││   0x004052ea      68a0474200     push str.____BCryptOpenAlgorithmProvider_failed_n ; 0x4247a0 ; "[-] BCryptOpenAlgorithmProvider failed\n"
│ ────────< 0x004052ef      e9fe070000     jmp 0x405af2
  │││││││   0x004052f4      ffb50cffffff   push dword [ebp - 0xf4]
  │││││││   0x004052fa      6838474200     push str.____Heap_reserve_failed_for__lu_bytes_n ; 0x424738 ; "[-] Heap reserve failed for %lu bytes\n"
  │││││││   0x004052ff      6a02           push 2                      ; 2
  │││││││   0x00405301      e835870000     call fcn.0040da3b
  │││││││   0x00405306      83c404         add esp, 4
  │││││││   0x00405309      50             push eax
  │││││││   0x0040530a      e811bdffff     call fcn.00401020
  │││││││   0x0040530f      83c40c         add esp, 0xc
  │││││││   0x00405312      8d8de0feffff   lea ecx, [ebp - 0x120]
  │││││││   0x00405318      e863080000     call fcn.00405b80
  │││││││   0x0040531d      b897574000     mov eax, 0x405797
  │││││││   0x00405322      c3             ret
│ │││││││   ; CODE XREF from fcn.00404fa0 @ 0x40527e(x)
│ ────────> 0x00405323      6878474200     push str.____ReadFile:_unexpected_EOF_n ; 0x424778 ; "[-] ReadFile: unexpected EOF\n"
│ ────────< 0x00405328      e9c5070000     jmp 0x405af2
│ │││││││   ; CODE XREF from fcn.00404fa0 @ 0x405275(x)
│ ────────> 0x0040532d      6860474200     push str.____ReadFile_failed_n ; 0x424760 ; "[-] ReadFile failed\n"
│ │││││││   0x00405332      6a02           push 2                      ; 2
│ │││││││   0x00405334      e802870000     call fcn.0040da3b
│ │││││││   0x00405339      83c404         add esp, 4
│ │││││││   0x0040533c      50             push eax
│ │││││││   0x0040533d      e8debcffff     call fcn.00401020
│ │││││││   0x00405342      83c408         add esp, 8
│ │││││││   0x00405345      8d8de0feffff   lea ecx, [var_120h]
│ │││││││   0x0040534b      e830080000     call fcn.00405b80
│ │││││││   0x00405350      8b4dc8         mov ecx, dword [var_38h]
│ │││││││   0x00405353      85c9           test ecx, ecx
│ ────────< 0x00405355      7442           je 0x405399
│ │││││││   0x00405357      8b55d0         mov edx, dword [var_30h]
│ │││││││   0x0040535a      8bc1           mov eax, ecx
│ │││││││   0x0040535c      2bd1           sub edx, ecx
│ │││││││   0x0040535e      81fa00100000   cmp edx, 0x1000
│ ────────< 0x00405364      7214           jb 0x40537a
│ │││││││   0x00405366      8b49fc         mov ecx, dword [ecx - 4]
│ │││││││   0x00405369      83c223         add edx, 0x23               ; 35
│ │││││││   0x0040536c      2bc1           sub eax, ecx
│ │││││││   0x0040536e      83c0fc         add eax, 0xfffffffc
│ │││││││   0x00405371      83f81f         cmp eax, 0x1f               ; 31
│ ────────< 0x00405374      0f87f6070000   ja 0x405b70
│ │││││││   ; CODE XREFS from fcn.00404fa0 @ 0x405364(x), 0x405b50(x), 0x405b66(x)
│ ────────> 0x0040537a      52             push edx
│ │││││││   0x0040537b      51             push ecx
│ │││││││   0x0040537c      e8a4560000     call fcn.0040aa25
│ │││││││   0x00405381      83c408         add esp, 8
│ │││││││   0x00405384      c745c80000..   mov dword [var_38h], 0
│ │││││││   0x0040538b      c745cc0000..   mov dword [var_34h], 0
│ │││││││   0x00405392      c745d00000..   mov dword [var_30h], 0
│ │││││││   ; CODE XREFS from fcn.00404fa0 @ 0x405355(x), 0x405b3d(x)
│ ────────> 0x00405399      8b4db0         mov ecx, dword [var_50h]
│ │││││││   0x0040539c      85c9           test ecx, ecx
│ ────────< 0x0040539e      0f8470040000   je 0x405814
│ │││││││   0x004053a4      8b55b8         mov edx, dword [var_48h]
│ │││││││   0x004053a7      8bc1           mov eax, ecx
│ │││││││   0x004053a9      2bd1           sub edx, ecx
│ │││││││   0x004053ab      81fa00100000   cmp edx, 0x1000
│ ────────< 0x004053b1      0f8253040000   jb 0x40580a
│ │││││││   0x004053b7      8b49fc         mov ecx, dword [ecx - 4]
│ │││││││   0x004053ba      83c223         add edx, 0x23               ; 35
│ │││││││   0x004053bd      2bc1           sub eax, ecx
│ │││││││   0x004053bf      83c0fc         add eax, 0xfffffffc
│ │││││││   0x004053c2      83f81f         cmp eax, 0x1f               ; 31
│ ────────< 0x004053c5      0f87a5070000   ja 0x405b70
│ ────────< 0x004053cb      e93a040000     jmp 0x40580a
│ │││││││   ; CODE XREF from fcn.00404fa0 @ 0x4052e4(x)
│ └───────> 0x004053d0      6a00           push 0
│  ││││││   0x004053d2      6a20           push 0x20                   ; 32
│  ││││││   0x004053d4      68c8474200     push str.ChainingModeGCM    ; 0x4247c8 ; u"ChainingModeGCM"
│  ││││││   0x004053d9      68e8474200     push str.ChainingMode       ; 0x4247e8 ; u"ChainingMode"
│  ││││││   0x004053de      ffb55cffffff   push dword [phAlgorithm]    ; BCRYPT_HANDLE hObject
│  ││││││   0x004053e4      ff158ce14100   call dword [sym.imp.bcrypt.dll_BCryptSetProperty] ; 0x41e18c ; "Tk\x02" ; NTSTATUS BCryptSetProperty(BCRYPT_HANDLE hObject, LPCWSTR pszProperty, PUCHAR pbInput, ULONG cbInput, ULONG dwFlags)
│  ││││││   0x004053ea      85c0           test eax, eax
│ ┌───────< 0x004053ec      740a           je 0x4053f8
│ │││││││   0x004053ee      6804484200     push str.____BCryptSetProperty_failed_n ; 0x424804 ; "[-] BCryptSetProperty failed\n"
│ ────────< 0x004053f3      e9fa060000     jmp 0x405af2
│ │││││││   ; CODE XREF from fcn.00404fa0 @ 0x4053ec(x)
│ └───────> 0x004053f8      6a00           push 0
│  ││││││   0x004053fa      8d459c         lea eax, [var_64h]
│  ││││││   0x004053fd      c745a40000..   mov dword [var_5ch], 0
│  ││││││   0x00405404      50             push eax
│  ││││││   0x00405405      6a04           push 4                      ; 4
│  ││││││   0x00405407      8d45a4         lea eax, [var_5ch]
│  ││││││   0x0040540a      c7459c0000..   mov dword [var_64h], 0
│  ││││││   0x00405411      50             push eax
│  ││││││   0x00405412      6824484200     push str.ObjectLength       ; 0x424824 ; u"ObjectLength"
│  ││││││   0x00405417      ffb55cffffff   push dword [phAlgorithm]    ; BCRYPT_HANDLE hObject
│  ││││││   0x0040541d      ff1570e14100   call dword [sym.imp.bcrypt.dll_BCryptGetProperty] ; 0x41e170 ; NTSTATUS BCryptGetProperty(BCRYPT_HANDLE hObject, LPCWSTR pszProperty, PUCHAR pbOutput, ULONG cbOutput, ULONG *pcbResult, ULONG dwFlags)
│  ││││││   0x00405423      85c0           test eax, eax
│ ┌───────< 0x00405425      740a           je 0x405431
│ │││││││   0x00405427      6840484200     push str.____BCryptGetProperty_failed_n ; 0x424840 ; "[-] BCryptGetProperty failed\n"
│ ────────< 0x0040542c      e9c1060000     jmp 0x405af2
│ │││││││   ; CODE XREF from fcn.00404fa0 @ 0x405425(x)
│ └───────> 0x00405431      8b4dcc         mov ecx, dword [var_34h]
│  ││││││   0x00405434      8bf9           mov edi, ecx
│  ││││││   0x00405436      8b75c8         mov esi, dword [var_38h]
│  ││││││   0x00405439      2bfe           sub edi, esi
│  ││││││   0x0040543b      8b55a4         mov edx, dword [var_5ch]
│  ││││││   0x0040543e      3bd7           cmp edx, edi
│ ┌───────< 0x00405440      7305           jae 0x405447
│ │││││││   0x00405442      8d0c16         lea ecx, [esi + edx]
│ ────────< 0x00405445      eb33           jmp 0x40547a
│ │││││││   ; CODE XREF from fcn.00404fa0 @ 0x405440(x)
│ └───────> 0x00405447      7634           jbe 0x40547d
│  ││││││   0x00405449      8b45d0         mov eax, dword [var_30h]
│  ││││││   0x0040544c      2bc6           sub eax, esi
│  ││││││   0x0040544e      3bd0           cmp edx, eax
│ ┌───────< 0x00405450      7612           jbe 0x405464
│ │││││││   0x00405452      51             push ecx
│ │││││││   0x00405453      52             push edx
│ │││││││   0x00405454      8d4dc8         lea ecx, [var_38h]
│ │││││││   0x00405457      e824460000     call fcn.00409a80
│ │││││││   0x0040545c      8b4dcc         mov ecx, dword [var_34h]
│ │││││││   0x0040545f      8b75c8         mov esi, dword [var_38h]
│ ────────< 0x00405462      eb19           jmp 0x40547d
│ │││││││   ; CODE XREF from fcn.00404fa0 @ 0x405450(x)
│ └───────> 0x00405464      2bd7           sub edx, edi
│  ││││││   0x00405466      52             push edx
│  ││││││   0x00405467      6a00           push 0
│  ││││││   0x00405469      51             push ecx
│  ││││││   0x0040546a      8d340a         lea esi, [edx + ecx]
│  ││││││   0x0040546d      e81e670000     call fcn.0040bb90
│  ││││││   0x00405472      8bce           mov ecx, esi
│  ││││││   0x00405474      83c40c         add esp, 0xc
│  ││││││   0x00405477      8b75c8         mov esi, dword [var_38h]
│  ││││││   ; CODE XREF from fcn.00404fa0 @ 0x405445(x)
│ ────────> 0x0040547a      894dcc         mov dword [var_34h], ecx
│  ││││││   ; CODE XREFS from fcn.00404fa0 @ 0x405447(x), 0x405462(x)
│ ────────> 0x0040547d      6a00           push 0
│  ││││││   0x0040547f      6a20           push 0x20                   ; 32 ; ULONG cbSecret
│  ││││││   0x00405481      ffb5dcfeffff   push dword [pbSecret]       ; PUCHAR pbSecret
│  ││││││   0x00405487      2bce           sub ecx, esi
│  ││││││   0x00405489      8d8554ffffff   lea eax, [phKey]
│  ││││││   0x0040548f      51             push ecx                    ; ULONG cbKeyObject
│  ││││││   0x00405490      56             push esi                    ; PUCHAR pbKeyObject
│  ││││││   0x00405491      50             push eax                    ; BCRYPT_KEY_HANDLE *phKey
│  ││││││   0x00405492      ffb55cffffff   push dword [phAlgorithm]    ; BCRYPT_ALG_HANDLE hAlgorithm
│  ││││││   0x00405498      ff1594e14100   call dword [sym.imp.bcrypt.dll_BCryptGenerateSymmetricKey] ; 0x41e194 ; "|k\x02" ; NTSTATUS BCryptGenerateSymmetricKey(BCRYPT_ALG_HANDLE hAlgorithm, BCRYPT_KEY_HANDLE *phKey, PUCHAR pbKeyObject, ULONG cbKeyObject, PUCHAR pbSecret, ULONG cbSecret, ULONG dwFlags)
│  ││││││   0x0040549e      85c0           test eax, eax
│ ┌───────< 0x004054a0      740a           je 0x4054ac
│ │││││││   0x004054a2      6860484200     push str.____BCryptGenerateSymmetricKey_failed_n ; 0x424860 ; "[-] BCryptGenerateSymmetricKey failed\n"
│ ────────< 0x004054a7      e946060000     jmp 0x405af2
│ │││││││   ; CODE XREF from fcn.00404fa0 @ 0x4054a0(x)
│ └───────> 0x004054ac      8b75b4         mov esi, dword [cbInput]
│  ││││││   0x004054af      b800000000     mov eax, 0
│  ││││││   0x004054b4      8b55b0         mov edx, dword [var_50h]
│  ││││││   0x004054b7      0f57c0         xorps xmm0, xmm0
│  ││││││   0x004054ba      660fd645bc     movq qword [var_44h], xmm0
│  ││││││   0x004054bf      8bf8           mov edi, eax
│  ││││││   0x004054c1      c745c40000..   mov dword [var_3ch], 0
│  ││││││   0x004054c8      8945bc         mov dword [var_44h], eax
│  ││││││   0x004054cb      897dc0         mov dword [var_40h], edi
│  ││││││   0x004054ce      8945c4         mov dword [var_3ch], eax
│  ││││││   0x004054d1      2bf2           sub esi, edx
│ ┌───────< 0x004054d3      7464           je 0x405539
│ │││││││   0x004054d5      81feffffff7f   cmp esi, 0x7fffffff
│ ────────< 0x004054db      0f8794060000   ja 0x405b75
│ │││││││   0x004054e1      81fe00100000   cmp esi, 0x1000
│ ────────< 0x004054e7      7229           jb 0x405512
│ │││││││   0x004054e9      8d4623         lea eax, [esi + 0x23]
│ │││││││   0x004054ec      3bc6           cmp eax, esi
│ ────────< 0x004054ee      0f8686060000   jbe 0x405b7a
│ │││││││   0x004054f4      50             push eax
│ │││││││   0x004054f5      e8aa520000     call fcn.0040a7a4
│ │││││││   0x004054fa      8bc8           mov ecx, eax
│ │││││││   0x004054fc      83c404         add esp, 4
│ │││││││   0x004054ff      85c9           test ecx, ecx
│ ────────< 0x00405501      0f8469060000   je 0x405b70
│ │││││││   0x00405507      8d4123         lea eax, [ecx + 0x23]
│ │││││││   0x0040550a      83e0e0         and eax, 0xffffffe0         ; 4294967264
│ │││││││   0x0040550d      8948fc         mov dword [eax - 4], ecx
│ ────────< 0x00405510      eb09           jmp 0x40551b
│ │││││││   ; CODE XREF from fcn.00404fa0 @ 0x4054e7(x)
│ ────────> 0x00405512      56             push esi
│ │││││││   0x00405513      e88c520000     call fcn.0040a7a4
│ │││││││   0x00405518      83c404         add esp, 4
│ │││││││   ; CODE XREF from fcn.00404fa0 @ 0x405510(x)
│ ────────> 0x0040551b      56             push esi
│ │││││││   0x0040551c      8d3c06         lea edi, [esi + eax]
│ │││││││   0x0040551f      8945bc         mov dword [var_44h], eax
│ │││││││   0x00405522      6a00           push 0
│ │││││││   0x00405524      50             push eax
│ │││││││   0x00405525      897dc4         mov dword [var_3ch], edi
│ │││││││   0x00405528      e863660000     call fcn.0040bb90
│ │││││││   0x0040552d      8b55b0         mov edx, dword [var_50h]
│ │││││││   0x00405530      83c40c         add esp, 0xc
│ │││││││   0x00405533      8b45bc         mov eax, dword [var_44h]
│ │││││││   0x00405536      897dc0         mov dword [var_40h], edi
│ │││││││   ; CODE XREF from fcn.00404fa0 @ 0x4054d3(x)
│ └───────> 0x00405539      c645fc04       mov byte [var_4h], 4
│  ││││││   0x0040553d      33f6           xor esi, esi
│  ││││││   0x0040553f      8b8d08ffffff   mov ecx, dword [var_f8h]
│  ││││││   0x00405545      0f57c0         xorps xmm0, xmm0
│  ││││││   0x00405548      898d18ffffff   mov dword [var_e8h], ecx
│  ││││││   0x0040554e      8d4d84         lea ecx, [var_7ch]
│  ││││││   0x00405551      898d28ffffff   mov dword [var_d8h], ecx
│  ││││││   0x00405557      8bcf           mov ecx, edi
│  ││││││   0x00405559      2bc8           sub ecx, eax
│  ││││││   0x0040555b      660f138520..   movlpd qword [var_e0h], xmm0
│  ││││││   0x00405563      3bc7           cmp eax, edi
│  ││││││   0x00405565      660f138530..   movlpd qword [var_d0h], xmm0
│  ││││││   0x0040556d      660f138538..   movlpd qword [var_c8h], xmm0
│  ││││││   0x00405575      0f44c6         cmove eax, esi
│  ││││││   0x00405578      660f138540..   movlpd qword [var_c0h], xmm0
│  ││││││   0x00405580      33ff           xor edi, edi
│  ││││││   0x00405582      898508ffffff   mov dword [var_f8h], eax
│  ││││││   0x00405588      8b45b4         mov eax, dword [cbInput]
│  ││││││   0x0040558b      8d75a0         lea esi, [var_60h]
│  ││││││   0x0040558e      57             push edi
│  ││││││   0x0040558f      56             push esi
│  ││││││   0x00405590      51             push ecx
│  ││││││   0x00405591      ffb508ffffff   push dword [var_f8h]
│  ││││││   0x00405597      2bc2           sub eax, edx
│  ││││││   0x00405599      660f138548..   movlpd qword [var_b8h], xmm0
│  ││││││   0x004055a1      3b55b4         cmp edx, dword [cbInput]
│  ││││││   0x004055a4      8d8d10ffffff   lea ecx, [var_f0h]
│  ││││││   0x004055aa      57             push edi
│  ││││││   0x004055ab      57             push edi
│  ││││││   0x004055ac      51             push ecx
│  ││││││   0x004055ad      50             push eax                    ; ULONG cbInput
│  ││││││   0x004055ae      0f44d7         cmove edx, edi
│  ││││││   0x004055b1      c78510ffff..   mov dword [var_f0h], 0x40   ; '@' ; 64
│  ││││││   0x004055bb      52             push edx                    ; PUCHAR pbInput
│  ││││││   0x004055bc      ffb554ffffff   push dword [phKey]          ; BCRYPT_KEY_HANDLE hKey
│  ││││││   0x004055c2      c78514ffff..   mov dword [var_ech], 1
│  ││││││   0x004055cc      c7851cffff..   mov dword [var_e4h], 0xc    ; 12
│  ││││││   0x004055d6      c7852cffff..   mov dword [var_d4h], 0x10   ; 16
│  ││││││   0x004055e0      c745a00000..   mov dword [var_60h], 0
│  ││││││   0x004055e7      ff1568e14100   call dword [sym.imp.bcrypt.dll_BCryptEncrypt] ; 0x41e168 ; NTSTATUS BCryptEncrypt(BCRYPT_KEY_HANDLE hKey, PUCHAR pbInput, ULONG cbInput, VOID *pPaddingInfo, PUCHAR pbIV, ULONG cbIV, PUCHAR pbOutput, ULONG cbOutput, ULONG *pcbResult, ULONG dwFlags)
│  ││││││   0x004055ed      85c0           test eax, eax
│ ┌───────< 0x004055ef      0f84a4000000   je 0x405699
│ │││││││   0x004055f5      50             push eax
│ │││││││   0x004055f6      6888484200     push str.____BCryptEncrypt_failed__status0x_lx_n ; str.____BCryptEncrypt_failed__status0x_lx_n
│ │││││││                                                              ; 0x424888 ; "[-] BCryptEncrypt failed | status=0x%lx\n"
│ │││││││   0x004055fb      6a02           push 2                      ; 2
│ │││││││   0x004055fd      e839840000     call fcn.0040da3b
│ │││││││   0x00405602      83c404         add esp, 4
│ │││││││   0x00405605      50             push eax
│ │││││││   0x00405606      e815baffff     call fcn.00401020
│ │││││││   0x0040560b      83c40c         add esp, 0xc
│ │││││││   0x0040560e      8d8de0feffff   lea ecx, [var_120h]
│ │││││││   0x00405614      e867050000     call fcn.00405b80
│ │││││││   0x00405619      8b4dbc         mov ecx, dword [var_44h]
│ │││││││   0x0040561c      85c9           test ecx, ecx
│ ────────< 0x0040561e      7436           je 0x405656
│ │││││││   0x00405620      8b55c4         mov edx, dword [var_3ch]
│ │││││││   0x00405623      8bc1           mov eax, ecx
│ │││││││   0x00405625      2bd1           sub edx, ecx
│ │││││││   0x00405627      81fa00100000   cmp edx, 0x1000
│ ────────< 0x0040562d      7214           jb 0x405643
│ │││││││   0x0040562f      8b49fc         mov ecx, dword [ecx - 4]
│ │││││││   0x00405632      83c223         add edx, 0x23               ; 35
│ │││││││   0x00405635      2bc1           sub eax, ecx
│ │││││││   0x00405637      83c0fc         add eax, 0xfffffffc
│ │││││││   0x0040563a      83f81f         cmp eax, 0x1f               ; 31
│ ────────< 0x0040563d      0f872d050000   ja 0x405b70
│ │││││││   ; CODE XREF from fcn.00404fa0 @ 0x40562d(x)
│ ────────> 0x00405643      52             push edx
│ │││││││   0x00405644      51             push ecx
│ │││││││   0x00405645      e8db530000     call fcn.0040aa25
│ │││││││   0x0040564a      83c408         add esp, 8
│ │││││││   0x0040564d      897dbc         mov dword [var_44h], edi
│ │││││││   0x00405650      897dc0         mov dword [var_40h], edi
│ │││││││   0x00405653      897dc4         mov dword [var_3ch], edi
│ │││││││   ; CODE XREF from fcn.00404fa0 @ 0x40561e(x)
│ ────────> 0x00405656      8b4dc8         mov ecx, dword [var_38h]
│ │││││││   0x00405659      85c9           test ecx, ecx
│ ────────< 0x0040565b      0f847f010000   je 0x4057e0
│ │││││││   0x00405661      8b55d0         mov edx, dword [var_30h]
│ │││││││   0x00405664      8bc1           mov eax, ecx
│ │││││││   0x00405666      2bd1           sub edx, ecx
│ │││││││   0x00405668      81fa00100000   cmp edx, 0x1000
│ ────────< 0x0040566e      7214           jb 0x405684
│ │││││││   0x00405670      8b49fc         mov ecx, dword [ecx - 4]
│ │││││││   0x00405673      83c223         add edx, 0x23               ; 35
│ │││││││   0x00405676      2bc1           sub eax, ecx
│ │││││││   0x00405678      83c0fc         add eax, 0xfffffffc
│ │││││││   0x0040567b      83f81f         cmp eax, 0x1f               ; 31
│ ────────< 0x0040567e      0f87ec040000   ja 0x405b70
│ │││││││   ; CODE XREF from fcn.00404fa0 @ 0x40566e(x)
│ ────────> 0x00405684      52             push edx
│ │││││││   0x00405685      51             push ecx
│ │││││││   0x00405686      e89a530000     call fcn.0040aa25
│ │││││││   0x0040568b      897dc8         mov dword [var_38h], edi
│ │││││││   0x0040568e      897dcc         mov dword [var_34h], edi
│ │││││││   0x00405691      897dd0         mov dword [var_30h], edi
│ ────────< 0x00405694      e944010000     jmp 0x4057dd
│ │││││││   ; CODE XREF from fcn.00404fa0 @ 0x4055ef(x)
│ └───────> 0x00405699      8b4db4         mov ecx, dword [cbInput]
│  ││││││   0x0040569c      8b45b0         mov eax, dword [var_50h]
│  ││││││   0x0040569f      2bc8           sub ecx, eax
│ ┌───────< 0x004056a1      740e           je 0x4056b1
│ │││││││   ; CODE XREF from fcn.00404fa0 @ 0x4056ac(x)
│ ────────> 0x004056a3      c60000         mov byte [eax], 0
│ │││││││   0x004056a6      8d4001         lea eax, [eax + 1]
│ │││││││   0x004056a9      83e901         sub ecx, 1
│ ────────< 0x004056ac      75f5           jne 0x4056a3
│ │││││││   0x004056ae      8b45b0         mov eax, dword [var_50h]
│ │││││││   ; CODE XREF from fcn.00404fa0 @ 0x4056a1(x)
│ └───────> 0x004056b1      8b7dc0         mov edi, dword [var_40h]
│  ││││││   0x004056b4      8bcf           mov ecx, edi
│  ││││││   0x004056b6      8b55bc         mov edx, dword [var_44h]
│  ││││││   0x004056b9      2bca           sub ecx, edx
│  ││││││   0x004056bb      8b75a0         mov esi, dword [var_60h]
│  ││││││   0x004056be      8945b4         mov dword [cbInput], eax
│  ││││││   0x004056c1      3bf1           cmp esi, ecx
│ ┌───────< 0x004056c3      7305           jae 0x4056ca
│ │││││││   0x004056c5      8d0416         lea eax, [esi + edx]
│ ────────< 0x004056c8      eb28           jmp 0x4056f2
│ │││││││   ; CODE XREF from fcn.00404fa0 @ 0x4056c3(x)
│ └───────> 0x004056ca      7629           jbe 0x4056f5
│  ││││││   0x004056cc      8b45c4         mov eax, dword [var_3ch]
│  ││││││   0x004056cf      2bc2           sub eax, edx
│  ││││││   0x004056d1      3bf0           cmp esi, eax
│ ┌───────< 0x004056d3      760c           jbe 0x4056e1
│ │││││││   0x004056d5      51             push ecx
│ │││││││   0x004056d6      56             push esi
│ │││││││   0x004056d7      8d4dbc         lea ecx, [var_44h]
│ │││││││   0x004056da      e8a1430000     call fcn.00409a80
│ ────────< 0x004056df      eb14           jmp 0x4056f5
│ │││││││   ; CODE XREF from fcn.00404fa0 @ 0x4056d3(x)
│ └───────> 0x004056e1      2bf1           sub esi, ecx
│  ││││││   0x004056e3      56             push esi
│  ││││││   0x004056e4      6a00           push 0
│  ││││││   0x004056e6      57             push edi
│  ││││││   0x004056e7      e8a4640000     call fcn.0040bb90
│  ││││││   0x004056ec      83c40c         add esp, 0xc
│  ││││││   0x004056ef      8d043e         lea eax, [esi + edi]
│  ││││││   ; CODE XREF from fcn.00404fa0 @ 0x4056c8(x)
│ ────────> 0x004056f2      8945c0         mov dword [var_40h], eax
│  ││││││   ; CODE XREFS from fcn.00404fa0 @ 0x4056ca(x), 0x4056df(x)
│ ────────> 0x004056f5      8b8504ffffff   mov eax, dword [var_fch]
│  ││││││   0x004056fb      83781408       cmp dword [eax + 0x14], 8
│ ┌───────< 0x004056ff      7202           jb 0x405703
│ │││││││   0x00405701      8b00           mov eax, dword [eax]
│ │││││││   ; CODE XREF from fcn.00404fa0 @ 0x4056ff(x)
│ └───────> 0x00405703      6a00           push 0
│  ││││││   0x00405705      6880000000     push 0x80                   ; 128
│  ││││││   0x0040570a      6a02           push 2                      ; 2
│  ││││││   0x0040570c      6a00           push 0
│  ││││││   0x0040570e      6a00           push 0
│  ││││││   0x00405710      6800000040     push 0x40000000             ; DWORD dwDesiredAccess
│  ││││││   0x00405715      50             push eax                    ; LPCWSTR lpFileName
│  ││││││   0x00405716      ff1518e04100   call dword [sym.imp.KERNEL32.dll_CreateFileW] ; 0x41e018 ; "Zi\x02" ; HANDLE CreateFileW(LPCWSTR lpFileName, DWORD dwDesiredAccess, DWORD dwShareMode, LPSECURITY_ATTRIBUTES lpSecurityAttributes, DWORD dwCreationDisposition, DWORD dwFlagsAndAttributes, HANDLE hTemplateFile)
│  ││││││   0x0040571c      898564ffffff   mov dword [hFile], eax
│  ││││││   0x00405722      83f8ff         cmp eax, 0xffffffff
│ ┌───────< 0x00405725      0f8507010000   jne 0x405832
│ │││││││   0x0040572b      68b4484200     push str.____CreateFile_output_failed_n ; 0x4248b4 ; "[-] CreateFile output failed\n"
│ │││││││   ; CODE XREFS from fcn.00404fa0 @ 0x4058e7(x), 0x405aca(x), 0x405ad4(x), 0x405ade(x), 0x405ae8(x)
│ ────────> 0x00405730      6a02           push 2                      ; 2
│ │││││││   0x00405732      e804830000     call fcn.0040da3b
│ │││││││   0x00405737      83c404         add esp, 4
│ │││││││   0x0040573a      50             push eax
│ │││││││   0x0040573b      e8e0b8ffff     call fcn.00401020
│ │││││││   0x00405740      83c408         add esp, 8
│ │││││││   0x00405743      8d8de0feffff   lea ecx, [var_120h]
│ │││││││   0x00405749      e832040000     call fcn.00405b80
│ │││││││   0x0040574e      8b4dbc         mov ecx, dword [var_44h]
│ │││││││   0x00405751      85c9           test ecx, ecx
│ ────────< 0x00405753      7442           je 0x405797
│ │││││││   0x00405755      8b55c4         mov edx, dword [var_3ch]
│ │││││││   0x00405758      8bc1           mov eax, ecx
│ │││││││   0x0040575a      2bd1           sub edx, ecx
│ │││││││   0x0040575c      81fa00100000   cmp edx, 0x1000
│ ────────< 0x00405762      7214           jb 0x405778
│ │││││││   0x00405764      8b49fc         mov ecx, dword [ecx - 4]
│ │││││││   0x00405767      83c223         add edx, 0x23               ; 35
│ │││││││   0x0040576a      2bc1           sub eax, ecx
│ │││││││   0x0040576c      83c0fc         add eax, 0xfffffffc
│ │││││││   0x0040576f      83f81f         cmp eax, 0x1f               ; 31
│ ────────< 0x00405772      0f87f8030000   ja 0x405b70
│ │││││││   ; CODE XREF from fcn.00404fa0 @ 0x405762(x)
│ ────────> 0x00405778      52             push edx
│ │││││││   0x00405779      51             push ecx
│ │││││││   0x0040577a      e8a6520000     call fcn.0040aa25
│ │││││││   0x0040577f      c745bc0000..   mov dword [var_44h], 0
│ │││││││   0x00405786      c745c00000..   mov dword [var_40h], 0
│ │││││││   0x0040578d      c745c40000..   mov dword [var_3ch], 0
│ │││││││   ; CODE XREF from fcn.00404fa0 @ 0x40511d(x)
│ │││││└──> 0x00405794      83c408         add esp, 8
│ │││││ │   ; CODE XREFS from fcn.00404fa0 @ 0x37d(r), 0x405753(x), 0x405b10(x)
│ ─────┌──> 0x00405797      8b4dc8         mov ecx, dword [var_38h]
│ │││││╎│   0x0040579a      85c9           test ecx, ecx
│ ────────< 0x0040579c      7442           je 0x4057e0
│ │││││╎│   0x0040579e      8b55d0         mov edx, dword [var_30h]
│ │││││╎│   0x004057a1      8bc1           mov eax, ecx
│ │││││╎│   0x004057a3      2bd1           sub edx, ecx
│ │││││╎│   0x004057a5      81fa00100000   cmp edx, 0x1000
│ ────────< 0x004057ab      7214           jb 0x4057c1
│ │││││╎│   0x004057ad      8b49fc         mov ecx, dword [ecx - 4]
│ │││││╎│   0x004057b0      83c223         add edx, 0x23               ; 35
│ │││││╎│   0x004057b3      2bc1           sub eax, ecx
│ │││││╎│   0x004057b5      83c0fc         add eax, 0xfffffffc
│ │││││╎│   0x004057b8      83f81f         cmp eax, 0x1f               ; 31
│ ────────< 0x004057bb      0f87af030000   ja 0x405b70
│ │││││╎│   ; CODE XREF from fcn.00404fa0 @ 0x4057ab(x)
│ ────────> 0x004057c1      52             push edx
│ │││││╎│   0x004057c2      51             push ecx
│ │││││╎│   0x004057c3      e85d520000     call fcn.0040aa25
│ │││││╎│   0x004057c8      c745d00000..   mov dword [var_30h], 0
│ │││││╎│   0x004057cf      c745cc0000..   mov dword [var_34h], 0
│ │││││╎│   0x004057d6      c745c80000..   mov dword [var_38h], 0
│ │││││╎│   ; CODE XREF from fcn.00404fa0 @ 0x405694(x)
│ ────────> 0x004057dd      83c408         add esp, 8
│ │││││╎│   ; CODE XREFS from fcn.00404fa0 @ 0x40565b(x), 0x40579c(x)
│ ────────> 0x004057e0      8b4db0         mov ecx, dword [var_50h]
│ │││││╎│   0x004057e3      85c9           test ecx, ecx
│ ────────< 0x004057e5      742d           je 0x405814
│ │││││╎│   0x004057e7      8b55b8         mov edx, dword [var_48h]
│ │││││╎│   0x004057ea      8bc1           mov eax, ecx
│ │││││╎│   0x004057ec      2bd1           sub edx, ecx
│ │││││╎│   0x004057ee      81fa00100000   cmp edx, 0x1000
│ ────────< 0x004057f4      7214           jb 0x40580a
│ │││││╎│   0x004057f6      8b49fc         mov ecx, dword [ecx - 4]
│ │││││╎│   0x004057f9      83c223         add edx, 0x23               ; 35
│ │││││╎│   0x004057fc      2bc1           sub eax, ecx
│ │││││╎│   0x004057fe      83c0fc         add eax, 0xfffffffc
│ │││││╎│   0x00405801      83f81f         cmp eax, 0x1f               ; 31
│ ────────< 0x00405804      0f8766030000   ja 0x405b70
│ │││││╎│   ; CODE XREFS from fcn.00404fa0 @ 0x4053b1(x), 0x4053cb(x), 0x4057f4(x)
│ ────────> 0x0040580a      52             push edx
│ │││││╎│   0x0040580b      51             push ecx
│ │││││╎│   0x0040580c      e814520000     call fcn.0040aa25
│ │││││╎│   0x00405811      83c408         add esp, 8
│ │││││╎│   ; CODE XREFS from fcn.00404fa0 @ 0x40539e(x), 0x4057e5(x)
│ ────────> 0x00405814      32c0           xor al, al
│ │││││╎│   ; CODE XREF from fcn.00404fa0 @ 0x405ac0(x)
│ ────────> 0x00405816      8b4df4         mov ecx, dword [var_ch_3]
│ │││││╎│   0x00405819      64890d0000..   mov dword fs:[0], ecx
│ │││││╎│   0x00405820      59             pop ecx
│ │││││╎│   0x00405821      5f             pop edi
│ │││││╎│   0x00405822      5e             pop esi
│ │││││╎│   0x00405823      5b             pop ebx
│ │││││╎│   0x00405824      8b4dec         mov ecx, dword [var_14h_2]
│ │││││╎│   0x00405827      33cd           xor ecx, ebp
│ │││││╎│   0x00405829      e8684f0000     call fcn.0040a796
│ │││││╎│   0x0040582e      8be5           mov esp, ebp
│ │││││╎│   0x00405830      5d             pop ebp
│ │││││╎│   0x00405831      c3             ret
│ │││││╎│   ; CODE XREF from fcn.00404fa0 @ 0x405725(x)
│ └───────> 0x00405832      8b3510e04100   mov esi, dword [sym.imp.KERNEL32.dll_WriteFile] ; [0x41e010:4]=0x2693e reloc.KERNEL32.dll_WriteFile ; ">i\x02"
│  ││││╎│   0x00405838      8d4dac         lea ecx, [var_54h]
│  ││││╎│   0x0040583b      6a00           push 0
│  ││││╎│   0x0040583d      51             push ecx
│  ││││╎│   0x0040583e      6a08           push 8                      ; 8
│  ││││╎│   0x00405840      8d4de4         lea ecx, [var_1ch]
│  ││││╎│   0x00405843      c745e43133..   mov dword [var_1ch], 0x37333331 ; '1337'
│  ││││╎│   0x0040584a      51             push ecx
│  ││││╎│   0x0040584b      50             push eax
│  ││││╎│   0x0040584c      c745e84461..   mov dword [var_18h], 0x4c4b6144 ; 'DaKL'
│  ││││╎│   0x00405853      c745ac0000..   mov dword [var_54h], 0
│  ││││╎│   0x0040585a      ffd6           call esi
│  ││││╎│   0x0040585c      85c0           test eax, eax
│ ┌───────< 0x0040585e      0f847f020000   je 0x405ae3
│ │││││╎│   0x00405864      837dac08       cmp dword [var_54h], 8
│ ────────< 0x00405868      0f8575020000   jne 0x405ae3
│ │││││╎│   0x0040586e      6a00           push 0
│ │││││╎│   0x00405870      8d45ac         lea eax, [var_54h]
│ │││││╎│   0x00405873      0f57c0         xorps xmm0, xmm0
│ │││││╎│   0x00405876      50             push eax
│ │││││╎│   0x00405877      6a10           push 0x10                   ; 16
│ │││││╎│   0x00405879      8d45d4         lea eax, [var_2ch]
│ │││││╎│   0x0040587c      50             push eax
│ │││││╎│   0x0040587d      ffb564ffffff   push dword [hFile]
│ │││││╎│   0x00405883      0f1145d4       movups xmmword [var_2ch], xmm0
│ │││││╎│   0x00405887      ffd6           call esi
│ │││││╎│   0x00405889      85c0           test eax, eax
│ ────────< 0x0040588b      0f8448020000   je 0x405ad9
│ │││││╎│   0x00405891      837dac10       cmp dword [var_54h], 0x10
│ ────────< 0x00405895      0f853e020000   jne 0x405ad9
│ │││││╎│   0x0040589b      8b4dc0         mov ecx, dword [var_40h]
│ │││││╎│   0x0040589e      8d55ac         lea edx, [var_54h]
│ │││││╎│   0x004058a1      8b45bc         mov eax, dword [var_44h]
│ │││││╎│   0x004058a4      2bc8           sub ecx, eax
│ │││││╎│   0x004058a6      6a00           push 0
│ │││││╎│   0x004058a8      52             push edx
│ │││││╎│   0x004058a9      51             push ecx
│ │││││╎│   0x004058aa      50             push eax
│ │││││╎│   0x004058ab      ffb564ffffff   push dword [hFile]
│ │││││╎│   0x004058b1      ffd6           call esi
│ │││││╎│   0x004058b3      85c0           test eax, eax
│ ────────< 0x004058b5      0f8414020000   je 0x405acf
│ │││││╎│   0x004058bb      8b45c0         mov eax, dword [var_40h]
│ │││││╎│   0x004058be      2b45bc         sub eax, dword [var_44h]
│ │││││╎│   0x004058c1      3945ac         cmp dword [var_54h], eax
│ ────────< 0x004058c4      0f8505020000   jne 0x405acf
│ │││││╎│   0x004058ca      6a00           push 0
│ │││││╎│   0x004058cc      6a00           push 0
│ │││││╎│   0x004058ce      6a00           push 0
│ │││││╎│   0x004058d0      6a08           push 8                      ; 8 ; LARGE_INTEGER liDistanceToMove
│ │││││╎│   0x004058d2      ffb564ffffff   push dword [hFile]          ; HANDLE hFile
│ │││││╎│   0x004058d8      ff1520e04100   call dword [sym.imp.KERNEL32.dll_SetFilePointerEx] ; 0x41e020 ; "vi\x02" ; BOOL SetFilePointerEx(HANDLE hFile, LARGE_INTEGER liDistanceToMove, PLARGE_INTEGER lpNewFilePointer, DWORD dwMoveMethod)
│ │││││╎│   0x004058de      85c0           test eax, eax
│ ────────< 0x004058e0      750a           jne 0x4058ec
│ │││││╎│   0x004058e2      683c494200     push str.____SetFilePointerEx_failed_n ; 0x42493c ; "[-] SetFilePointerEx failed\n"
│ ────────< 0x004058e7      e944feffff     jmp 0x405730
│ │││││╎│   ; CODE XREF from fcn.00404fa0 @ 0x4058e0(x)
│ ────────> 0x004058ec      6a00           push 0
│ │││││╎│   0x004058ee      8d45ac         lea eax, [var_54h]
│ │││││╎│   0x004058f1      50             push eax
│ │││││╎│   0x004058f2      6a10           push 0x10                   ; 16
│ │││││╎│   0x004058f4      8d4584         lea eax, [var_7ch]
│ │││││╎│   0x004058f7      50             push eax
│ │││││╎│   0x004058f8      ffb564ffffff   push dword [hFile]
│ │││││╎│   0x004058fe      ffd6           call esi
│ │││││╎│   0x00405900      85c0           test eax, eax
│ ────────< 0x00405902      0f84bd010000   je 0x405ac5
│ │││││╎│   0x00405908      837dac10       cmp dword [var_54h], 0x10
│ ────────< 0x0040590c      0f85b3010000   jne 0x405ac5
│ │││││╎│   0x00405912      8b8d50ffffff   mov ecx, dword [var_b0h]
│ │││││╎│   0x00405918      8b8560ffffff   mov eax, dword [lpBuffer]
│ │││││╎│   0x0040591e      85c9           test ecx, ecx
│ ────────< 0x00405920      7411           je 0x405933
│ │││││╎│   ; CODE XREF from fcn.00404fa0 @ 0x40592b(x)
│ ────────> 0x00405922      c60000         mov byte [eax], 0
│ │││││╎│   0x00405925      8d4001         lea eax, [eax + 1]
│ │││││╎│   0x00405928      83e901         sub ecx, 1
│ ────────< 0x0040592b      75f5           jne 0x405922
│ │││││╎│   0x0040592d      8b8560ffffff   mov eax, dword [lpBuffer]
│ │││││╎│   ; CODE XREF from fcn.00404fa0 @ 0x405920(x)
│ ────────> 0x00405933      6800800000     push 0x8000
│ │││││╎│   0x00405938      6a00           push 0
│ │││││╎│   0x0040593a      50             push eax                    ; LPVOID lpAddress
│ │││││╎│   0x0040593b      ff150ce04100   call dword [sym.imp.KERNEL32.dll_VirtualFree] ; 0x41e00c ; "0i\x02" ; BOOL VirtualFree(LPVOID lpAddress, SIZE_T dwSize, DWORD dwFreeType)
│ │││││╎│   0x00405941      8b45c0         mov eax, dword [var_40h]
│ │││││╎│   0x00405944      8b4dbc         mov ecx, dword [var_44h]
│ │││││╎│   0x00405947      c78560ffff..   mov dword [lpBuffer], 0
│ │││││╎│   0x00405951      2bc1           sub eax, ecx
│ ────────< 0x00405953      740e           je 0x405963
│ │││││╎│   ; CODE XREF from fcn.00404fa0 @ 0x40595e(x)
│ ────────> 0x00405955      c60100         mov byte [ecx], 0
│ │││││╎│   0x00405958      8d4901         lea ecx, [ecx + 1]
│ │││││╎│   0x0040595b      83e801         sub eax, 1
│ ────────< 0x0040595e      75f5           jne 0x405955
│ │││││╎│   0x00405960      8b4dbc         mov ecx, dword [var_44h]
│ │││││╎│   ; CODE XREF from fcn.00404fa0 @ 0x405953(x)
│ ────────> 0x00405963      8b8554ffffff   mov eax, dword [phKey]
│ │││││╎│   0x00405969      894dc0         mov dword [var_40h], ecx
│ │││││╎│   0x0040596c      85c0           test eax, eax
│ ────────< 0x0040596e      7414           je 0x405984
│ │││││╎│   0x00405970      50             push eax                    ; BCRYPT_KEY_HANDLE hKey
│ │││││╎│   0x00405971      ff156ce14100   call dword [sym.imp.bcrypt.dll_BCryptDestroyKey] ; 0x41e16c ; NTSTATUS BCryptDestroyKey(BCRYPT_KEY_HANDLE hKey)
│ │││││╎│   0x00405977      8b4dbc         mov ecx, dword [var_44h]
│ │││││╎│   0x0040597a      c78554ffff..   mov dword [phKey], 0
│ │││││╎│   ; CODE XREF from fcn.00404fa0 @ 0x40596e(x)
│ ────────> 0x00405984      8b855cffffff   mov eax, dword [phAlgorithm]
│ │││││╎│   0x0040598a      85c0           test eax, eax
│ ────────< 0x0040598c      7416           je 0x4059a4
│ │││││╎│   0x0040598e      6a00           push 0
│ │││││╎│   0x00405990      50             push eax                    ; BCRYPT_ALG_HANDLE hAlgorithm
│ │││││╎│   0x00405991      ff1580e14100   call dword [sym.imp.bcrypt.dll_BCryptCloseAlgorithmProvider] ; 0x41e180 ; NTSTATUS BCryptCloseAlgorithmProvider(BCRYPT_ALG_HANDLE hAlgorithm, ULONG dwFlags)
│ │││││╎│   0x00405997      8b4dbc         mov ecx, dword [var_44h]
│ │││││╎│   0x0040599a      c7855cffff..   mov dword [phAlgorithm], 0
│ │││││╎│   ; CODE XREF from fcn.00404fa0 @ 0x40598c(x)
│ ────────> 0x004059a4      8b55c8         mov edx, dword [var_38h]
│ │││││╎│   0x004059a7      8b45cc         mov eax, dword [var_34h]
│ │││││╎│   0x004059aa      3bd0           cmp edx, eax
│ ────────< 0x004059ac      7418           je 0x4059c6
│ │││││╎│   0x004059ae      2bc2           sub eax, edx
│ ────────< 0x004059b0      7411           je 0x4059c3
│ │││││╎│   ; CODE XREF from fcn.00404fa0 @ 0x4059bb(x)
│ ────────> 0x004059b2      c60200         mov byte [edx], 0
│ │││││╎│   0x004059b5      8d5201         lea edx, [edx + 1]
│ │││││╎│   0x004059b8      83e801         sub eax, 1
│ ────────< 0x004059bb      75f5           jne 0x4059b2
│ │││││╎│   0x004059bd      8b55c8         mov edx, dword [var_38h]
│ │││││╎│   0x004059c0      8b4dbc         mov ecx, dword [var_44h]
│ │││││╎│   ; CODE XREF from fcn.00404fa0 @ 0x4059b0(x)
│ ────────> 0x004059c3      8955cc         mov dword [var_34h], edx
│ │││││╎│   ; CODE XREF from fcn.00404fa0 @ 0x4059ac(x)
│ ────────> 0x004059c6      8b8564ffffff   mov eax, dword [hFile]
│ │││││╎│   0x004059cc      83f8ff         cmp eax, 0xffffffff
│ ────────< 0x004059cf      7417           je 0x4059e8
│ │││││╎│   0x004059d1      50             push eax                    ; HANDLE hObject
│ │││││╎│   0x004059d2      ff151ce04100   call dword [sym.imp.KERNEL32.dll_CloseHandle] ; 0x41e01c ; "hi\x02" ; BOOL CloseHandle(HANDLE hObject)
│ │││││╎│   0x004059d8      8b55c8         mov edx, dword [var_38h]
│ │││││╎│   0x004059db      8b4dbc         mov ecx, dword [var_44h]
│ │││││╎│   0x004059de      c78564ffff..   mov dword [hFile], 0xffffffff ; -1
│ │││││╎│   ; CODE XREF from fcn.00404fa0 @ 0x4059cf(x)
│ ────────> 0x004059e8      be10000000     mov esi, 0x10               ; 16
│ │││││╎│   0x004059ed      8d4584         lea eax, [var_7ch]
│ │││││╎│   ; CODE XREF from fcn.00404fa0 @ 0x4059f9(x)
│ ────────> 0x004059f0      c60000         mov byte [eax], 0
│ │││││╎│   0x004059f3      8d4001         lea eax, [eax + 1]
│ │││││╎│   0x004059f6      83ee01         sub esi, 1
│ ────────< 0x004059f9      75f5           jne 0x4059f0
│ │││││╎│   0x004059fb      85c9           test ecx, ecx
│ ────────< 0x004059fd      7445           je 0x405a44
│ │││││╎│   0x004059ff      8b55c4         mov edx, dword [var_3ch]
│ │││││╎│   0x00405a02      8bc1           mov eax, ecx
│ │││││╎│   0x00405a04      2bd1           sub edx, ecx
│ │││││╎│   0x00405a06      81fa00100000   cmp edx, 0x1000
│ ────────< 0x00405a0c      7214           jb 0x405a22
│ │││││╎│   0x00405a0e      8b49fc         mov ecx, dword [ecx - 4]
│ │││││╎│   0x00405a11      83c223         add edx, 0x23               ; 35
│ │││││╎│   0x00405a14      2bc1           sub eax, ecx
│ │││││╎│   0x00405a16      83c0fc         add eax, 0xfffffffc
│ │││││╎│   0x00405a19      83f81f         cmp eax, 0x1f               ; 31
│ ────────< 0x00405a1c      0f874e010000   ja 0x405b70
│ │││││╎│   ; CODE XREF from fcn.00404fa0 @ 0x405a0c(x)
│ ────────> 0x00405a22      52             push edx
│ │││││╎│   0x00405a23      51             push ecx
│ │││││╎│   0x00405a24      e8fc4f0000     call fcn.0040aa25
│ │││││╎│   0x00405a29      8b55c8         mov edx, dword [var_38h]
│ │││││╎│   0x00405a2c      83c408         add esp, 8
│ │││││╎│   0x00405a2f      c745bc0000..   mov dword [var_44h], 0
│ │││││╎│   0x00405a36      c745c00000..   mov dword [var_40h], 0
│ │││││╎│   0x00405a3d      c745c40000..   mov dword [var_3ch], 0
│ │││││╎│   ; CODE XREF from fcn.00404fa0 @ 0x4059fd(x)
│ ────────> 0x00405a44      85d2           test edx, edx
│ ────────< 0x00405a46      7442           je 0x405a8a
│ │││││╎│   0x00405a48      8b4dd0         mov ecx, dword [var_30h]
│ │││││╎│   0x00405a4b      8bc2           mov eax, edx
│ │││││╎│   0x00405a4d      2bca           sub ecx, edx
│ │││││╎│   0x00405a4f      81f900100000   cmp ecx, 0x1000
│ ────────< 0x00405a55      7214           jb 0x405a6b
│ │││││╎│   0x00405a57      8b52fc         mov edx, dword [edx - 4]
│ │││││╎│   0x00405a5a      83c123         add ecx, 0x23               ; 35
│ │││││╎│   0x00405a5d      2bc2           sub eax, edx
│ │││││╎│   0x00405a5f      83c0fc         add eax, 0xfffffffc
│ │││││╎│   0x00405a62      83f81f         cmp eax, 0x1f               ; 31
│ ────────< 0x00405a65      0f8705010000   ja 0x405b70
│ │││││╎│   ; CODE XREF from fcn.00404fa0 @ 0x405a55(x)
│ ────────> 0x00405a6b      51             push ecx
│ │││││╎│   0x00405a6c      52             push edx
│ │││││╎│   0x00405a6d      e8b34f0000     call fcn.0040aa25
│ │││││╎│   0x00405a72      83c408         add esp, 8
│ │││││╎│   0x00405a75      c745c80000..   mov dword [var_38h], 0
│ │││││╎│   0x00405a7c      c745cc0000..   mov dword [var_34h], 0
│ │││││╎│   0x00405a83      c745d00000..   mov dword [var_30h], 0
│ │││││╎│   ; CODE XREF from fcn.00404fa0 @ 0x405a46(x)
│ ────────> 0x00405a8a      8b4db0         mov ecx, dword [var_50h]
│ │││││╎│   0x00405a8d      85c9           test ecx, ecx
│ ────────< 0x00405a8f      742d           je 0x405abe
│ │││││╎│   0x00405a91      8b55b8         mov edx, dword [var_48h]
│ │││││╎│   0x00405a94      8bc1           mov eax, ecx
│ │││││╎│   0x00405a96      2bd1           sub edx, ecx
│ │││││╎│   0x00405a98      81fa00100000   cmp edx, 0x1000
│ ────────< 0x00405a9e      7214           jb 0x405ab4
│ │││││╎│   0x00405aa0      8b49fc         mov ecx, dword [ecx - 4]
│ │││││╎│   0x00405aa3      83c223         add edx, 0x23               ; 35
│ │││││╎│   0x00405aa6      2bc1           sub eax, ecx
│ │││││╎│   0x00405aa8      83c0fc         add eax, 0xfffffffc
│ │││││╎│   0x00405aab      83f81f         cmp eax, 0x1f               ; 31
│ ────────< 0x00405aae      0f87bc000000   ja 0x405b70
│ │││││╎│   ; CODE XREF from fcn.00404fa0 @ 0x405a9e(x)
│ ────────> 0x00405ab4      52             push edx
│ │││││╎│   0x00405ab5      51             push ecx
│ │││││╎│   0x00405ab6      e86a4f0000     call fcn.0040aa25
│ │││││╎│   0x00405abb      83c408         add esp, 8
│ │││││╎│   ; CODE XREF from fcn.00404fa0 @ 0x405a8f(x)
│ ────────> 0x00405abe      b001           mov al, 1
│ ────────< 0x00405ac0      e951fdffff     jmp 0x405816
│ │││││╎│   ; CODE XREFS from fcn.00404fa0 @ 0x405902(x), 0x40590c(x)
│ ────────> 0x00405ac5      685c494200     push str.____WriteFile_tag__failed_n ; 0x42495c ; "[-] WriteFile(tag) failed\n"
│ ────────< 0x00405aca      e961fcffff     jmp 0x405730
│ │││││╎│   ; CODE XREFS from fcn.00404fa0 @ 0x4058b5(x), 0x4058c4(x)
│ ────────> 0x00405acf      6818494200     push str.____WriteFile_ciphertext__failed_n ; 0x424918 ; "[-] WriteFile(ciphertext) failed\n"
│ ────────< 0x00405ad4      e957fcffff     jmp 0x405730
│ │││││╎│   ; CODE XREFS from fcn.00404fa0 @ 0x40588b(x), 0x405895(x)
│ ────────> 0x00405ad9      68f4484200     push str.____WriteFile_placeholder__failed_n ; 0x4248f4 ; "[-] WriteFile(placeholder) failed\n"
│ ────────< 0x00405ade      e94dfcffff     jmp 0x405730
│ │││││╎│   ; CODE XREFS from fcn.00404fa0 @ 0x40585e(x), 0x405868(x)
│ └───────> 0x00405ae3      68d4484200     push str.____WriteFile_magic__failed_n ; 0x4248d4 ; "[-] WriteFile(magic) failed\n"
│ ────────< 0x00405ae8      e943fcffff     jmp 0x405730
│  ││││╎│   ; CODE XREFS from fcn.00404fa0 @ 0x4051a7(x), 0x4051b2(x)
│ ──└─────> 0x00405aed      6800474200     push str.____Invalid_file_size_n ; 0x424700 ; "[-] Invalid file size\n"
│  │ ││╎│   ; XREFS: CODE 0x00405192  CODE 0x004051f1  CODE 0x004052ef  
│  │ ││╎│   ; XREFS: CODE 0x00405328  CODE 0x004053f3  CODE 0x0040542c  
│  │ ││╎│   ; XREFS: CODE 0x004054a7  
│ ─└──────> 0x00405af2      6a02           push 2                      ; 2
│    ││╎│   0x00405af4      e8427f0000     call fcn.0040da3b
│    ││╎│   0x00405af9      83c404         add esp, 4
│    ││╎│   0x00405afc      50             push eax
│    ││╎│   0x00405afd      e81eb5ffff     call fcn.00401020
│    ││╎│   0x00405b02      83c408         add esp, 8
│    ││╎│   0x00405b05      8d8de0feffff   lea ecx, [var_120h]
│    ││╎│   0x00405b0b      e870000000     call fcn.00405b80
│    ││└──< 0x00405b10      e982fcffff     jmp 0x405797
│    ││ │   ; CODE XREFS from fcn.00404fa0 @ 0x40514f(x), 0x405163(x), 0x40516b(x)
│    └└─└─> 0x00405b15      68c8464200     push str.____alignment_query_failed_n ; 0x4246c8 ; "[-] alignment query failed\n"
│           0x00405b1a      6a02           push 2                      ; 2
│           0x00405b1c      e81a7f0000     call fcn.0040da3b
│           0x00405b21      83c404         add esp, 4
│           0x00405b24      50             push eax
│           0x00405b25      e8f6b4ffff     call fcn.00401020
│           0x00405b2a      83c408         add esp, 8
│           0x00405b2d      8d8de0feffff   lea ecx, [var_120h]
│           0x00405b33      e848000000     call fcn.00405b80
│           0x00405b38      8b4dc8         mov ecx, dword [var_38h]
│           0x00405b3b      85c9           test ecx, ecx
│ ────────< 0x00405b3d      0f8456f8ffff   je 0x405399
│           0x00405b43      8b55d0         mov edx, dword [var_30h]
│           0x00405b46      8bc1           mov eax, ecx
│           0x00405b48      2bd1           sub edx, ecx
│           0x00405b4a      81fa00100000   cmp edx, 0x1000
│ ────────< 0x00405b50      0f8224f8ffff   jb 0x40537a
│           0x00405b56      8b             invalid
│           0x00405b57      49             dec ecx
