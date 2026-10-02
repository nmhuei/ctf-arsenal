
script/extracted/challenge:     file format elf64-x86-64


Disassembly of section .init:

0000000000001000 <.init>:
    1000:	f3 0f 1e fa          	endbr64
    1004:	48 83 ec 08          	sub    rsp,0x8
    1008:	48 8b 05 b1 4a 00 00 	mov    rax,QWORD PTR [rip+0x4ab1]        # 5ac0 <sleep@plt+0x47f0>
    100f:	48 85 c0             	test   rax,rax
    1012:	74 02                	je     1016 <__cxa_finalize@plt-0x16a>
    1014:	ff d0                	call   rax
    1016:	48 83 c4 08          	add    rsp,0x8
    101a:	c3                   	ret

Disassembly of section .plt:

0000000000001020 <.plt>:
    1020:	ff 35 d2 49 00 00    	push   QWORD PTR [rip+0x49d2]        # 59f8 <sleep@plt+0x4728>
    1026:	ff 25 d4 49 00 00    	jmp    QWORD PTR [rip+0x49d4]        # 5a00 <sleep@plt+0x4730>
    102c:	0f 1f 40 00          	nop    DWORD PTR [rax+0x0]
    1030:	f3 0f 1e fa          	endbr64
    1034:	68 00 00 00 00       	push   0x0
    1039:	e9 e2 ff ff ff       	jmp    1020 <__cxa_finalize@plt-0x160>
    103e:	66 90                	xchg   ax,ax
    1040:	f3 0f 1e fa          	endbr64
    1044:	68 01 00 00 00       	push   0x1
    1049:	e9 d2 ff ff ff       	jmp    1020 <__cxa_finalize@plt-0x160>
    104e:	66 90                	xchg   ax,ax
    1050:	f3 0f 1e fa          	endbr64
    1054:	68 02 00 00 00       	push   0x2
    1059:	e9 c2 ff ff ff       	jmp    1020 <__cxa_finalize@plt-0x160>
    105e:	66 90                	xchg   ax,ax
    1060:	f3 0f 1e fa          	endbr64
    1064:	68 03 00 00 00       	push   0x3
    1069:	e9 b2 ff ff ff       	jmp    1020 <__cxa_finalize@plt-0x160>
    106e:	66 90                	xchg   ax,ax
    1070:	f3 0f 1e fa          	endbr64
    1074:	68 04 00 00 00       	push   0x4
    1079:	e9 a2 ff ff ff       	jmp    1020 <__cxa_finalize@plt-0x160>
    107e:	66 90                	xchg   ax,ax
    1080:	f3 0f 1e fa          	endbr64
    1084:	68 05 00 00 00       	push   0x5
    1089:	e9 92 ff ff ff       	jmp    1020 <__cxa_finalize@plt-0x160>
    108e:	66 90                	xchg   ax,ax
    1090:	f3 0f 1e fa          	endbr64
    1094:	68 06 00 00 00       	push   0x6
    1099:	e9 82 ff ff ff       	jmp    1020 <__cxa_finalize@plt-0x160>
    109e:	66 90                	xchg   ax,ax
    10a0:	f3 0f 1e fa          	endbr64
    10a4:	68 07 00 00 00       	push   0x7
    10a9:	e9 72 ff ff ff       	jmp    1020 <__cxa_finalize@plt-0x160>
    10ae:	66 90                	xchg   ax,ax
    10b0:	f3 0f 1e fa          	endbr64
    10b4:	68 08 00 00 00       	push   0x8
    10b9:	e9 62 ff ff ff       	jmp    1020 <__cxa_finalize@plt-0x160>
    10be:	66 90                	xchg   ax,ax
    10c0:	f3 0f 1e fa          	endbr64
    10c4:	68 09 00 00 00       	push   0x9
    10c9:	e9 52 ff ff ff       	jmp    1020 <__cxa_finalize@plt-0x160>
    10ce:	66 90                	xchg   ax,ax
    10d0:	f3 0f 1e fa          	endbr64
    10d4:	68 0a 00 00 00       	push   0xa
    10d9:	e9 42 ff ff ff       	jmp    1020 <__cxa_finalize@plt-0x160>
    10de:	66 90                	xchg   ax,ax
    10e0:	f3 0f 1e fa          	endbr64
    10e4:	68 0b 00 00 00       	push   0xb
    10e9:	e9 32 ff ff ff       	jmp    1020 <__cxa_finalize@plt-0x160>
    10ee:	66 90                	xchg   ax,ax
    10f0:	f3 0f 1e fa          	endbr64
    10f4:	68 0c 00 00 00       	push   0xc
    10f9:	e9 22 ff ff ff       	jmp    1020 <__cxa_finalize@plt-0x160>
    10fe:	66 90                	xchg   ax,ax
    1100:	f3 0f 1e fa          	endbr64
    1104:	68 0d 00 00 00       	push   0xd
    1109:	e9 12 ff ff ff       	jmp    1020 <__cxa_finalize@plt-0x160>
    110e:	66 90                	xchg   ax,ax
    1110:	f3 0f 1e fa          	endbr64
    1114:	68 0e 00 00 00       	push   0xe
    1119:	e9 02 ff ff ff       	jmp    1020 <__cxa_finalize@plt-0x160>
    111e:	66 90                	xchg   ax,ax
    1120:	f3 0f 1e fa          	endbr64
    1124:	68 0f 00 00 00       	push   0xf
    1129:	e9 f2 fe ff ff       	jmp    1020 <__cxa_finalize@plt-0x160>
    112e:	66 90                	xchg   ax,ax
    1130:	f3 0f 1e fa          	endbr64
    1134:	68 10 00 00 00       	push   0x10
    1139:	e9 e2 fe ff ff       	jmp    1020 <__cxa_finalize@plt-0x160>
    113e:	66 90                	xchg   ax,ax
    1140:	f3 0f 1e fa          	endbr64
    1144:	68 11 00 00 00       	push   0x11
    1149:	e9 d2 fe ff ff       	jmp    1020 <__cxa_finalize@plt-0x160>
    114e:	66 90                	xchg   ax,ax
    1150:	f3 0f 1e fa          	endbr64
    1154:	68 12 00 00 00       	push   0x12
    1159:	e9 c2 fe ff ff       	jmp    1020 <__cxa_finalize@plt-0x160>
    115e:	66 90                	xchg   ax,ax
    1160:	f3 0f 1e fa          	endbr64
    1164:	68 13 00 00 00       	push   0x13
    1169:	e9 b2 fe ff ff       	jmp    1020 <__cxa_finalize@plt-0x160>
    116e:	66 90                	xchg   ax,ax
    1170:	f3 0f 1e fa          	endbr64
    1174:	68 14 00 00 00       	push   0x14
    1179:	e9 a2 fe ff ff       	jmp    1020 <__cxa_finalize@plt-0x160>
    117e:	66 90                	xchg   ax,ax

Disassembly of section .plt.got:

0000000000001180 <__cxa_finalize@plt>:
    1180:	f3 0f 1e fa          	endbr64
    1184:	ff 25 46 49 00 00    	jmp    QWORD PTR [rip+0x4946]        # 5ad0 <sleep@plt+0x4800>
    118a:	66 0f 1f 44 00 00    	nop    WORD PTR [rax+rax*1+0x0]

Disassembly of section .plt.sec:

0000000000001190 <free@plt>:
    1190:	f3 0f 1e fa          	endbr64
    1194:	ff 25 6e 48 00 00    	jmp    QWORD PTR [rip+0x486e]        # 5a08 <sleep@plt+0x4738>
    119a:	66 0f 1f 44 00 00    	nop    WORD PTR [rax+rax*1+0x0]

00000000000011a0 <strncmp@plt>:
    11a0:	f3 0f 1e fa          	endbr64
    11a4:	ff 25 66 48 00 00    	jmp    QWORD PTR [rip+0x4866]        # 5a10 <sleep@plt+0x4740>
    11aa:	66 0f 1f 44 00 00    	nop    WORD PTR [rax+rax*1+0x0]

00000000000011b0 <puts@plt>:
    11b0:	f3 0f 1e fa          	endbr64
    11b4:	ff 25 5e 48 00 00    	jmp    QWORD PTR [rip+0x485e]        # 5a18 <sleep@plt+0x4748>
    11ba:	66 0f 1f 44 00 00    	nop    WORD PTR [rax+rax*1+0x0]

00000000000011c0 <write@plt>:
    11c0:	f3 0f 1e fa          	endbr64
    11c4:	ff 25 56 48 00 00    	jmp    QWORD PTR [rip+0x4856]        # 5a20 <sleep@plt+0x4750>
    11ca:	66 0f 1f 44 00 00    	nop    WORD PTR [rax+rax*1+0x0]

00000000000011d0 <strlen@plt>:
    11d0:	f3 0f 1e fa          	endbr64
    11d4:	ff 25 4e 48 00 00    	jmp    QWORD PTR [rip+0x484e]        # 5a28 <sleep@plt+0x4758>
    11da:	66 0f 1f 44 00 00    	nop    WORD PTR [rax+rax*1+0x0]

00000000000011e0 <__stack_chk_fail@plt>:
    11e0:	f3 0f 1e fa          	endbr64
    11e4:	ff 25 46 48 00 00    	jmp    QWORD PTR [rip+0x4846]        # 5a30 <sleep@plt+0x4760>
    11ea:	66 0f 1f 44 00 00    	nop    WORD PTR [rax+rax*1+0x0]

00000000000011f0 <system@plt>:
    11f0:	f3 0f 1e fa          	endbr64
    11f4:	ff 25 3e 48 00 00    	jmp    QWORD PTR [rip+0x483e]        # 5a38 <sleep@plt+0x4768>
    11fa:	66 0f 1f 44 00 00    	nop    WORD PTR [rax+rax*1+0x0]

0000000000001200 <printf@plt>:
    1200:	f3 0f 1e fa          	endbr64
    1204:	ff 25 36 48 00 00    	jmp    QWORD PTR [rip+0x4836]        # 5a40 <sleep@plt+0x4770>
    120a:	66 0f 1f 44 00 00    	nop    WORD PTR [rax+rax*1+0x0]

0000000000001210 <memset@plt>:
    1210:	f3 0f 1e fa          	endbr64
    1214:	ff 25 2e 48 00 00    	jmp    QWORD PTR [rip+0x482e]        # 5a48 <sleep@plt+0x4778>
    121a:	66 0f 1f 44 00 00    	nop    WORD PTR [rax+rax*1+0x0]

0000000000001220 <close@plt>:
    1220:	f3 0f 1e fa          	endbr64
    1224:	ff 25 26 48 00 00    	jmp    QWORD PTR [rip+0x4826]        # 5a50 <sleep@plt+0x4780>
    122a:	66 0f 1f 44 00 00    	nop    WORD PTR [rax+rax*1+0x0]

0000000000001230 <read@plt>:
    1230:	f3 0f 1e fa          	endbr64
    1234:	ff 25 1e 48 00 00    	jmp    QWORD PTR [rip+0x481e]        # 5a58 <sleep@plt+0x4788>
    123a:	66 0f 1f 44 00 00    	nop    WORD PTR [rax+rax*1+0x0]

0000000000001240 <strtoull@plt>:
    1240:	f3 0f 1e fa          	endbr64
    1244:	ff 25 16 48 00 00    	jmp    QWORD PTR [rip+0x4816]        # 5a60 <sleep@plt+0x4790>
    124a:	66 0f 1f 44 00 00    	nop    WORD PTR [rax+rax*1+0x0]

0000000000001250 <calloc@plt>:
    1250:	f3 0f 1e fa          	endbr64
    1254:	ff 25 0e 48 00 00    	jmp    QWORD PTR [rip+0x480e]        # 5a68 <sleep@plt+0x4798>
    125a:	66 0f 1f 44 00 00    	nop    WORD PTR [rax+rax*1+0x0]

0000000000001260 <strcmp@plt>:
    1260:	f3 0f 1e fa          	endbr64
    1264:	ff 25 06 48 00 00    	jmp    QWORD PTR [rip+0x4806]        # 5a70 <sleep@plt+0x47a0>
    126a:	66 0f 1f 44 00 00    	nop    WORD PTR [rax+rax*1+0x0]

0000000000001270 <memcpy@plt>:
    1270:	f3 0f 1e fa          	endbr64
    1274:	ff 25 fe 47 00 00    	jmp    QWORD PTR [rip+0x47fe]        # 5a78 <sleep@plt+0x47a8>
    127a:	66 0f 1f 44 00 00    	nop    WORD PTR [rax+rax*1+0x0]

0000000000001280 <malloc@plt>:
    1280:	f3 0f 1e fa          	endbr64
    1284:	ff 25 f6 47 00 00    	jmp    QWORD PTR [rip+0x47f6]        # 5a80 <sleep@plt+0x47b0>
    128a:	66 0f 1f 44 00 00    	nop    WORD PTR [rax+rax*1+0x0]

0000000000001290 <setvbuf@plt>:
    1290:	f3 0f 1e fa          	endbr64
    1294:	ff 25 ee 47 00 00    	jmp    QWORD PTR [rip+0x47ee]        # 5a88 <sleep@plt+0x47b8>
    129a:	66 0f 1f 44 00 00    	nop    WORD PTR [rax+rax*1+0x0]

00000000000012a0 <open@plt>:
    12a0:	f3 0f 1e fa          	endbr64
    12a4:	ff 25 e6 47 00 00    	jmp    QWORD PTR [rip+0x47e6]        # 5a90 <sleep@plt+0x47c0>
    12aa:	66 0f 1f 44 00 00    	nop    WORD PTR [rax+rax*1+0x0]

00000000000012b0 <atoi@plt>:
    12b0:	f3 0f 1e fa          	endbr64
    12b4:	ff 25 de 47 00 00    	jmp    QWORD PTR [rip+0x47de]        # 5a98 <sleep@plt+0x47c8>
    12ba:	66 0f 1f 44 00 00    	nop    WORD PTR [rax+rax*1+0x0]

00000000000012c0 <exit@plt>:
    12c0:	f3 0f 1e fa          	endbr64
    12c4:	ff 25 d6 47 00 00    	jmp    QWORD PTR [rip+0x47d6]        # 5aa0 <sleep@plt+0x47d0>
    12ca:	66 0f 1f 44 00 00    	nop    WORD PTR [rax+rax*1+0x0]

00000000000012d0 <sleep@plt>:
    12d0:	f3 0f 1e fa          	endbr64
    12d4:	ff 25 ce 47 00 00    	jmp    QWORD PTR [rip+0x47ce]        # 5aa8 <sleep@plt+0x47d8>
    12da:	66 0f 1f 44 00 00    	nop    WORD PTR [rax+rax*1+0x0]

Disassembly of section .text:

00000000000012e0 <.text>:
    12e0:	f3 0f 1e fa          	endbr64
    12e4:	31 ed                	xor    ebp,ebp
    12e6:	49 89 d1             	mov    r9,rdx
    12e9:	5e                   	pop    rsi
    12ea:	48 89 e2             	mov    rdx,rsp
    12ed:	48 83 e4 f0          	and    rsp,0xfffffffffffffff0
    12f1:	50                   	push   rax
    12f2:	54                   	push   rsp
    12f3:	45 31 c0             	xor    r8d,r8d
    12f6:	31 c9                	xor    ecx,ecx
    12f8:	48 8d 3d 12 0d 00 00 	lea    rdi,[rip+0xd12]        # 2011 <sleep@plt+0xd41>
    12ff:	ff 15 ab 47 00 00    	call   QWORD PTR [rip+0x47ab]        # 5ab0 <sleep@plt+0x47e0>
    1305:	f4                   	hlt
    1306:	66 2e 0f 1f 84 00 00 	cs nop WORD PTR [rax+rax*1+0x0]
    130d:	00 00 00 
    1310:	48 8d 3d d1 47 00 00 	lea    rdi,[rip+0x47d1]        # 5ae8 <sleep@plt+0x4818>
    1317:	48 8d 05 ca 47 00 00 	lea    rax,[rip+0x47ca]        # 5ae8 <sleep@plt+0x4818>
    131e:	48 39 f8             	cmp    rax,rdi
    1321:	74 15                	je     1338 <sleep@plt+0x68>
    1323:	48 8b 05 8e 47 00 00 	mov    rax,QWORD PTR [rip+0x478e]        # 5ab8 <sleep@plt+0x47e8>
    132a:	48 85 c0             	test   rax,rax
    132d:	74 09                	je     1338 <sleep@plt+0x68>
    132f:	ff e0                	jmp    rax
    1331:	0f 1f 80 00 00 00 00 	nop    DWORD PTR [rax+0x0]
    1338:	c3                   	ret
    1339:	0f 1f 80 00 00 00 00 	nop    DWORD PTR [rax+0x0]
    1340:	48 8d 3d a1 47 00 00 	lea    rdi,[rip+0x47a1]        # 5ae8 <sleep@plt+0x4818>
    1347:	48 8d 35 9a 47 00 00 	lea    rsi,[rip+0x479a]        # 5ae8 <sleep@plt+0x4818>
    134e:	48 29 fe             	sub    rsi,rdi
    1351:	48 89 f0             	mov    rax,rsi
    1354:	48 c1 ee 3f          	shr    rsi,0x3f
    1358:	48 c1 f8 03          	sar    rax,0x3
    135c:	48 01 c6             	add    rsi,rax
    135f:	48 d1 fe             	sar    rsi,1
    1362:	74 14                	je     1378 <sleep@plt+0xa8>
    1364:	48 8b 05 5d 47 00 00 	mov    rax,QWORD PTR [rip+0x475d]        # 5ac8 <sleep@plt+0x47f8>
    136b:	48 85 c0             	test   rax,rax
    136e:	74 08                	je     1378 <sleep@plt+0xa8>
    1370:	ff e0                	jmp    rax
    1372:	66 0f 1f 44 00 00    	nop    WORD PTR [rax+rax*1+0x0]
    1378:	c3                   	ret
    1379:	0f 1f 80 00 00 00 00 	nop    DWORD PTR [rax+0x0]
    1380:	f3 0f 1e fa          	endbr64
    1384:	80 3d 9d 47 00 00 00 	cmp    BYTE PTR [rip+0x479d],0x0        # 5b28 <stderr@GLIBC_2.2.5+0x8>
    138b:	75 2b                	jne    13b8 <sleep@plt+0xe8>
    138d:	55                   	push   rbp
    138e:	48 83 3d 3a 47 00 00 	cmp    QWORD PTR [rip+0x473a],0x0        # 5ad0 <sleep@plt+0x4800>
    1395:	00 
    1396:	48 89 e5             	mov    rbp,rsp
    1399:	74 0c                	je     13a7 <sleep@plt+0xd7>
    139b:	48 8b 3d 3e 47 00 00 	mov    rdi,QWORD PTR [rip+0x473e]        # 5ae0 <sleep@plt+0x4810>
    13a2:	e8 d9 fd ff ff       	call   1180 <__cxa_finalize@plt>
    13a7:	e8 64 ff ff ff       	call   1310 <sleep@plt+0x40>
    13ac:	c6 05 75 47 00 00 01 	mov    BYTE PTR [rip+0x4775],0x1        # 5b28 <stderr@GLIBC_2.2.5+0x8>
    13b3:	5d                   	pop    rbp
    13b4:	c3                   	ret
    13b5:	0f 1f 00             	nop    DWORD PTR [rax]
    13b8:	c3                   	ret
    13b9:	0f 1f 80 00 00 00 00 	nop    DWORD PTR [rax+0x0]
    13c0:	f3 0f 1e fa          	endbr64
    13c4:	e9 77 ff ff ff       	jmp    1340 <sleep@plt+0x70>
    13c9:	f3 0f 1e fa          	endbr64
    13cd:	55                   	push   rbp
    13ce:	48 89 e5             	mov    rbp,rsp
    13d1:	48 89 7d f8          	mov    QWORD PTR [rbp-0x8],rdi
    13d5:	48 8b 45 f8          	mov    rax,QWORD PTR [rbp-0x8]
    13d9:	0f b6 00             	movzx  eax,BYTE PTR [rax]
    13dc:	5d                   	pop    rbp
    13dd:	c3                   	ret
    13de:	f3 0f 1e fa          	endbr64
    13e2:	55                   	push   rbp
    13e3:	48 89 e5             	mov    rbp,rsp
    13e6:	48 8b 05 13 47 00 00 	mov    rax,QWORD PTR [rip+0x4713]        # 5b00 <stdout@GLIBC_2.2.5>
    13ed:	b9 00 00 00 00       	mov    ecx,0x0
    13f2:	ba 02 00 00 00       	mov    edx,0x2
    13f7:	be 00 00 00 00       	mov    esi,0x0
    13fc:	48 89 c7             	mov    rdi,rax
    13ff:	e8 8c fe ff ff       	call   1290 <setvbuf@plt>
    1404:	48 8b 05 05 47 00 00 	mov    rax,QWORD PTR [rip+0x4705]        # 5b10 <stdin@GLIBC_2.2.5>
    140b:	b9 00 00 00 00       	mov    ecx,0x0
    1410:	ba 02 00 00 00       	mov    edx,0x2
    1415:	be 00 00 00 00       	mov    esi,0x0
    141a:	48 89 c7             	mov    rdi,rax
    141d:	e8 6e fe ff ff       	call   1290 <setvbuf@plt>
    1422:	48 8b 05 f7 46 00 00 	mov    rax,QWORD PTR [rip+0x46f7]        # 5b20 <stderr@GLIBC_2.2.5>
    1429:	b9 00 00 00 00       	mov    ecx,0x0
    142e:	ba 02 00 00 00       	mov    edx,0x2
    1433:	be 00 00 00 00       	mov    esi,0x0
    1438:	48 89 c7             	mov    rdi,rax
    143b:	e8 50 fe ff ff       	call   1290 <setvbuf@plt>
    1440:	be 08 00 00 00       	mov    esi,0x8
    1445:	bf 10 00 00 00       	mov    edi,0x10
    144a:	e8 01 fe ff ff       	call   1250 <calloc@plt>
    144f:	48 89 05 fa 48 00 00 	mov    QWORD PTR [rip+0x48fa],rax        # 5d50 <stderr@GLIBC_2.2.5+0x230>
    1456:	48 8b 05 f3 48 00 00 	mov    rax,QWORD PTR [rip+0x48f3]        # 5d50 <stderr@GLIBC_2.2.5+0x230>
    145d:	48 83 c0 08          	add    rax,0x8
    1461:	48 8d 15 f0 01 00 00 	lea    rdx,[rip+0x1f0]        # 1658 <sleep@plt+0x388>
    1468:	48 89 10             	mov    QWORD PTR [rax],rdx
    146b:	48 8b 05 de 48 00 00 	mov    rax,QWORD PTR [rip+0x48de]        # 5d50 <stderr@GLIBC_2.2.5+0x230>
    1472:	48 83 c0 10          	add    rax,0x10
    1476:	48 8d 15 4a 02 00 00 	lea    rdx,[rip+0x24a]        # 16c7 <sleep@plt+0x3f7>
    147d:	48 89 10             	mov    QWORD PTR [rax],rdx
    1480:	48 8b 05 c9 48 00 00 	mov    rax,QWORD PTR [rip+0x48c9]        # 5d50 <stderr@GLIBC_2.2.5+0x230>
    1487:	48 83 c0 18          	add    rax,0x18
    148b:	48 8d 15 a7 04 00 00 	lea    rdx,[rip+0x4a7]        # 1939 <sleep@plt+0x669>
    1492:	48 89 10             	mov    QWORD PTR [rax],rdx
    1495:	48 8b 05 b4 48 00 00 	mov    rax,QWORD PTR [rip+0x48b4]        # 5d50 <stderr@GLIBC_2.2.5+0x230>
    149c:	48 83 c0 20          	add    rax,0x20
    14a0:	48 8d 15 2c 05 00 00 	lea    rdx,[rip+0x52c]        # 19d3 <sleep@plt+0x703>
    14a7:	48 89 10             	mov    QWORD PTR [rax],rdx
    14aa:	48 8b 05 9f 48 00 00 	mov    rax,QWORD PTR [rip+0x489f]        # 5d50 <stderr@GLIBC_2.2.5+0x230>
    14b1:	48 83 c0 28          	add    rax,0x28
    14b5:	48 8d 15 6c 05 00 00 	lea    rdx,[rip+0x56c]        # 1a28 <sleep@plt+0x758>
    14bc:	48 89 10             	mov    QWORD PTR [rax],rdx
    14bf:	48 8b 05 8a 48 00 00 	mov    rax,QWORD PTR [rip+0x488a]        # 5d50 <stderr@GLIBC_2.2.5+0x230>
    14c6:	48 83 c0 30          	add    rax,0x30
    14ca:	48 8d 15 f3 02 00 00 	lea    rdx,[rip+0x2f3]        # 17c4 <sleep@plt+0x4f4>
    14d1:	48 89 10             	mov    QWORD PTR [rax],rdx
    14d4:	48 8b 05 75 48 00 00 	mov    rax,QWORD PTR [rip+0x4875]        # 5d50 <stderr@GLIBC_2.2.5+0x230>
    14db:	48 83 c0 38          	add    rax,0x38
    14df:	48 8d 15 d0 0a 00 00 	lea    rdx,[rip+0xad0]        # 1fb6 <sleep@plt+0xce6>
    14e6:	48 89 10             	mov    QWORD PTR [rax],rdx
    14e9:	48 8b 05 60 48 00 00 	mov    rax,QWORD PTR [rip+0x4860]        # 5d50 <stderr@GLIBC_2.2.5+0x230>
    14f0:	48 83 c0 40          	add    rax,0x40
    14f4:	48 8d 15 0e 06 00 00 	lea    rdx,[rip+0x60e]        # 1b09 <sleep@plt+0x839>
    14fb:	48 89 10             	mov    QWORD PTR [rax],rdx
    14fe:	90                   	nop
    14ff:	5d                   	pop    rbp
    1500:	c3                   	ret
    1501:	f3 0f 1e fa          	endbr64
    1505:	55                   	push   rbp
    1506:	48 89 e5             	mov    rbp,rsp
    1509:	48 8d 05 bb 2a 00 00 	lea    rax,[rip+0x2abb]        # 3fcb <sleep@plt+0x2cfb>
    1510:	48 89 c7             	mov    rdi,rax
    1513:	e8 98 fc ff ff       	call   11b0 <puts@plt>
    1518:	48 8d 05 c1 2a 00 00 	lea    rax,[rip+0x2ac1]        # 3fe0 <sleep@plt+0x2d10>
    151f:	48 89 c7             	mov    rdi,rax
    1522:	e8 89 fc ff ff       	call   11b0 <puts@plt>
    1527:	48 8d 05 9d 2a 00 00 	lea    rax,[rip+0x2a9d]        # 3fcb <sleep@plt+0x2cfb>
    152e:	48 89 c7             	mov    rdi,rax
    1531:	e8 7a fc ff ff       	call   11b0 <puts@plt>
    1536:	48 8d 05 b4 2a 00 00 	lea    rax,[rip+0x2ab4]        # 3ff1 <sleep@plt+0x2d21>
    153d:	48 89 c7             	mov    rdi,rax
    1540:	e8 6b fc ff ff       	call   11b0 <puts@plt>
    1545:	48 8d 05 b7 2a 00 00 	lea    rax,[rip+0x2ab7]        # 4003 <sleep@plt+0x2d33>
    154c:	48 89 c7             	mov    rdi,rax
    154f:	e8 5c fc ff ff       	call   11b0 <puts@plt>
    1554:	48 8d 05 be 2a 00 00 	lea    rax,[rip+0x2abe]        # 4019 <sleep@plt+0x2d49>
    155b:	48 89 c7             	mov    rdi,rax
    155e:	e8 4d fc ff ff       	call   11b0 <puts@plt>
    1563:	48 8d 05 c1 2a 00 00 	lea    rax,[rip+0x2ac1]        # 402b <sleep@plt+0x2d5b>
    156a:	48 89 c7             	mov    rdi,rax
    156d:	e8 3e fc ff ff       	call   11b0 <puts@plt>
    1572:	48 8d 05 c2 2a 00 00 	lea    rax,[rip+0x2ac2]        # 403b <sleep@plt+0x2d6b>
    1579:	48 89 c7             	mov    rdi,rax
    157c:	e8 2f fc ff ff       	call   11b0 <puts@plt>
    1581:	48 8d 05 c3 2a 00 00 	lea    rax,[rip+0x2ac3]        # 404b <sleep@plt+0x2d7b>
    1588:	48 89 c7             	mov    rdi,rax
    158b:	e8 20 fc ff ff       	call   11b0 <puts@plt>
    1590:	48 8d 05 c4 2a 00 00 	lea    rax,[rip+0x2ac4]        # 405b <sleep@plt+0x2d8b>
    1597:	48 89 c7             	mov    rdi,rax
    159a:	e8 11 fc ff ff       	call   11b0 <puts@plt>
    159f:	48 8d 05 c9 2a 00 00 	lea    rax,[rip+0x2ac9]        # 406f <sleep@plt+0x2d9f>
    15a6:	48 89 c7             	mov    rdi,rax
    15a9:	e8 02 fc ff ff       	call   11b0 <puts@plt>
    15ae:	48 8d 05 c2 2a 00 00 	lea    rax,[rip+0x2ac2]        # 4077 <sleep@plt+0x2da7>
    15b5:	48 89 c7             	mov    rdi,rax
    15b8:	b8 00 00 00 00       	mov    eax,0x0
    15bd:	e8 3e fc ff ff       	call   1200 <printf@plt>
    15c2:	90                   	nop
    15c3:	5d                   	pop    rbp
    15c4:	c3                   	ret
    15c5:	f3 0f 1e fa          	endbr64
    15c9:	55                   	push   rbp
    15ca:	48 89 e5             	mov    rbp,rsp
    15cd:	48 83 ec 20          	sub    rsp,0x20
    15d1:	64 48 8b 04 25 28 00 	mov    rax,QWORD PTR fs:0x28
    15d8:	00 00 
    15da:	48 89 45 f8          	mov    QWORD PTR [rbp-0x8],rax
    15de:	31 c0                	xor    eax,eax
    15e0:	48 c7 45 e0 00 00 00 	mov    QWORD PTR [rbp-0x20],0x0
    15e7:	00 
    15e8:	48 c7 45 e8 00 00 00 	mov    QWORD PTR [rbp-0x18],0x0
    15ef:	00 
    15f0:	48 8d 45 e0          	lea    rax,[rbp-0x20]
    15f4:	ba 0f 00 00 00       	mov    edx,0xf
    15f9:	48 89 c6             	mov    rsi,rax
    15fc:	bf 00 00 00 00       	mov    edi,0x0
    1601:	e8 2a fc ff ff       	call   1230 <read@plt>
    1606:	48 8d 45 e0          	lea    rax,[rbp-0x20]
    160a:	48 89 c7             	mov    rdi,rax
    160d:	e8 9e fc ff ff       	call   12b0 <atoi@plt>
    1612:	48 8b 55 f8          	mov    rdx,QWORD PTR [rbp-0x8]
    1616:	64 48 2b 14 25 28 00 	sub    rdx,QWORD PTR fs:0x28
    161d:	00 00 
    161f:	74 05                	je     1626 <sleep@plt+0x356>
    1621:	e8 ba fb ff ff       	call   11e0 <__stack_chk_fail@plt>
    1626:	c9                   	leave
    1627:	c3                   	ret
    1628:	f3 0f 1e fa          	endbr64
    162c:	55                   	push   rbp
    162d:	48 89 e5             	mov    rbp,rsp
    1630:	89 7d fc             	mov    DWORD PTR [rbp-0x4],edi
    1633:	83 7d fc 00          	cmp    DWORD PTR [rbp-0x4],0x0
    1637:	79 0d                	jns    1646 <sleep@plt+0x376>
    1639:	8b 45 fc             	mov    eax,DWORD PTR [rbp-0x4]
    163c:	89 c2                	mov    edx,eax
    163e:	f7 da                	neg    edx
    1640:	0f 49 c2             	cmovns eax,edx
    1643:	89 45 fc             	mov    DWORD PTR [rbp-0x4],eax
    1646:	83 7d fc 78          	cmp    DWORD PTR [rbp-0x4],0x78
    164a:	7e 07                	jle    1653 <sleep@plt+0x383>
    164c:	b8 ff ff ff ff       	mov    eax,0xffffffff
    1651:	eb 03                	jmp    1656 <sleep@plt+0x386>
    1653:	8b 45 fc             	mov    eax,DWORD PTR [rbp-0x4]
    1656:	5d                   	pop    rbp
    1657:	c3                   	ret
    1658:	f3 0f 1e fa          	endbr64
    165c:	55                   	push   rbp
    165d:	48 89 e5             	mov    rbp,rsp
    1660:	48 83 ec 20          	sub    rsp,0x20
    1664:	48 89 7d e8          	mov    QWORD PTR [rbp-0x18],rdi
    1668:	48 8d 05 0b 2a 00 00 	lea    rax,[rip+0x2a0b]        # 407a <sleep@plt+0x2daa>
    166f:	48 89 c7             	mov    rdi,rax
    1672:	b8 00 00 00 00       	mov    eax,0x0
    1677:	e8 84 fb ff ff       	call   1200 <printf@plt>
    167c:	b8 00 00 00 00       	mov    eax,0x0
    1681:	e8 3f ff ff ff       	call   15c5 <sleep@plt+0x2f5>
    1686:	89 45 f8             	mov    DWORD PTR [rbp-0x8],eax
    1689:	8b 45 f8             	mov    eax,DWORD PTR [rbp-0x8]
    168c:	89 c7                	mov    edi,eax
    168e:	e8 95 ff ff ff       	call   1628 <sleep@plt+0x358>
    1693:	89 45 fc             	mov    DWORD PTR [rbp-0x4],eax
    1696:	83 7d fc ff          	cmp    DWORD PTR [rbp-0x4],0xffffffff
    169a:	75 11                	jne    16ad <sleep@plt+0x3dd>
    169c:	48 8d 05 ea 29 00 00 	lea    rax,[rip+0x29ea]        # 408d <sleep@plt+0x2dbd>
    16a3:	48 89 c7             	mov    rdi,rax
    16a6:	e8 05 fb ff ff       	call   11b0 <puts@plt>
    16ab:	eb 18                	jmp    16c5 <sleep@plt+0x3f5>
    16ad:	8b 45 f8             	mov    eax,DWORD PTR [rbp-0x8]
    16b0:	89 05 92 44 00 00    	mov    DWORD PTR [rip+0x4492],eax        # 5b48 <stderr@GLIBC_2.2.5+0x28>
    16b6:	48 8d 05 e5 29 00 00 	lea    rax,[rip+0x29e5]        # 40a2 <sleep@plt+0x2dd2>
    16bd:	48 89 c7             	mov    rdi,rax
    16c0:	e8 eb fa ff ff       	call   11b0 <puts@plt>
    16c5:	c9                   	leave
    16c6:	c3                   	ret
    16c7:	f3 0f 1e fa          	endbr64
    16cb:	55                   	push   rbp
    16cc:	48 89 e5             	mov    rbp,rsp
    16cf:	48 81 ec 00 10 00 00 	sub    rsp,0x1000
    16d6:	48 83 0c 24 00       	or     QWORD PTR [rsp],0x0
    16db:	48 83 ec 40          	sub    rsp,0x40
    16df:	48 89 bd c8 ef ff ff 	mov    QWORD PTR [rbp-0x1038],rdi
    16e6:	64 48 8b 04 25 28 00 	mov    rax,QWORD PTR fs:0x28
    16ed:	00 00 
    16ef:	48 89 45 f8          	mov    QWORD PTR [rbp-0x8],rax
    16f3:	31 c0                	xor    eax,eax
    16f5:	48 8d 05 50 44 00 00 	lea    rax,[rip+0x4450]        # 5b4c <stderr@GLIBC_2.2.5+0x2c>
    16fc:	48 89 85 d0 ef ff ff 	mov    QWORD PTR [rbp-0x1030],rax
    1703:	48 8d 85 d0 ef ff ff 	lea    rax,[rbp-0x1030]
    170a:	48 83 c0 08          	add    rax,0x8
    170e:	ba 10 00 00 00       	mov    edx,0x10
    1713:	be 00 00 00 00       	mov    esi,0x0
    1718:	48 89 c7             	mov    rdi,rax
    171b:	e8 f0 fa ff ff       	call   1210 <memset@plt>
    1720:	48 8d 05 8d 29 00 00 	lea    rax,[rip+0x298d]        # 40b4 <sleep@plt+0x2de4>
    1727:	48 89 c7             	mov    rdi,rax
    172a:	b8 00 00 00 00       	mov    eax,0x0
    172f:	e8 cc fa ff ff       	call   1200 <printf@plt>
    1734:	48 8d 85 d0 ef ff ff 	lea    rax,[rbp-0x1030]
    173b:	48 83 c0 08          	add    rax,0x8
    173f:	ba 0f 00 00 00       	mov    edx,0xf
    1744:	48 89 c6             	mov    rsi,rax
    1747:	bf 00 00 00 00       	mov    edi,0x0
    174c:	e8 df fa ff ff       	call   1230 <read@plt>
    1751:	48 8d 85 d0 ef ff ff 	lea    rax,[rbp-0x1030]
    1758:	48 83 c0 08          	add    rax,0x8
    175c:	48 89 c7             	mov    rdi,rax
    175f:	e8 4c fb ff ff       	call   12b0 <atoi@plt>
    1764:	89 85 e8 ef ff ff    	mov    DWORD PTR [rbp-0x1018],eax
    176a:	8b 85 e8 ef ff ff    	mov    eax,DWORD PTR [rbp-0x1018]
    1770:	85 c0                	test   eax,eax
    1772:	7e 0b                	jle    177f <sleep@plt+0x4af>
    1774:	8b 85 e8 ef ff ff    	mov    eax,DWORD PTR [rbp-0x1018]
    177a:	83 f8 0a             	cmp    eax,0xa
    177d:	7e 11                	jle    1790 <sleep@plt+0x4c0>
    177f:	48 8d 05 44 29 00 00 	lea    rax,[rip+0x2944]        # 40ca <sleep@plt+0x2dfa>
    1786:	48 89 c7             	mov    rdi,rax
    1789:	e8 22 fa ff ff       	call   11b0 <puts@plt>
    178e:	eb 1e                	jmp    17ae <sleep@plt+0x4de>
    1790:	48 8b 85 d0 ef ff ff 	mov    rax,QWORD PTR [rbp-0x1030]
    1797:	8b 95 e8 ef ff ff    	mov    edx,DWORD PTR [rbp-0x1018]
    179d:	89 10                	mov    DWORD PTR [rax],edx
    179f:	48 8d 05 36 29 00 00 	lea    rax,[rip+0x2936]        # 40dc <sleep@plt+0x2e0c>
    17a6:	48 89 c7             	mov    rdi,rax
    17a9:	e8 02 fa ff ff       	call   11b0 <puts@plt>
    17ae:	48 8b 45 f8          	mov    rax,QWORD PTR [rbp-0x8]
    17b2:	64 48 2b 04 25 28 00 	sub    rax,QWORD PTR fs:0x28
    17b9:	00 00 
    17bb:	74 05                	je     17c2 <sleep@plt+0x4f2>
    17bd:	e8 1e fa ff ff       	call   11e0 <__stack_chk_fail@plt>
    17c2:	c9                   	leave
    17c3:	c3                   	ret
    17c4:	f3 0f 1e fa          	endbr64
    17c8:	55                   	push   rbp
    17c9:	48 89 e5             	mov    rbp,rsp
    17cc:	48 81 ec 00 10 00 00 	sub    rsp,0x1000
    17d3:	48 83 0c 24 00       	or     QWORD PTR [rsp],0x0
    17d8:	48 83 ec 40          	sub    rsp,0x40
    17dc:	48 89 bd c8 ef ff ff 	mov    QWORD PTR [rbp-0x1038],rdi
    17e3:	64 48 8b 04 25 28 00 	mov    rax,QWORD PTR fs:0x28
    17ea:	00 00 
    17ec:	48 89 45 f8          	mov    QWORD PTR [rbp-0x8],rax
    17f0:	31 c0                	xor    eax,eax
    17f2:	48 8d 85 d0 ef ff ff 	lea    rax,[rbp-0x1030]
    17f9:	48 83 c0 08          	add    rax,0x8
    17fd:	ba 10 00 00 00       	mov    edx,0x10
    1802:	be 00 00 00 00       	mov    esi,0x0
    1807:	48 89 c7             	mov    rdi,rax
    180a:	e8 01 fa ff ff       	call   1210 <memset@plt>
    180f:	48 8d 05 da 28 00 00 	lea    rax,[rip+0x28da]        # 40f0 <sleep@plt+0x2e20>
    1816:	48 89 c7             	mov    rdi,rax
    1819:	b8 00 00 00 00       	mov    eax,0x0
    181e:	e8 dd f9 ff ff       	call   1200 <printf@plt>
    1823:	48 8d 85 d0 ef ff ff 	lea    rax,[rbp-0x1030]
    182a:	48 83 c0 08          	add    rax,0x8
    182e:	ba 0f 00 00 00       	mov    edx,0xf
    1833:	48 89 c6             	mov    rsi,rax
    1836:	bf 00 00 00 00       	mov    edi,0x0
    183b:	e8 f0 f9 ff ff       	call   1230 <read@plt>
    1840:	48 8d 85 d0 ef ff ff 	lea    rax,[rbp-0x1030]
    1847:	48 83 c0 08          	add    rax,0x8
    184b:	ba 03 00 00 00       	mov    edx,0x3
    1850:	48 8d 0d bc 28 00 00 	lea    rcx,[rip+0x28bc]        # 4113 <sleep@plt+0x2e43>
    1857:	48 89 ce             	mov    rsi,rcx
    185a:	48 89 c7             	mov    rdi,rax
    185d:	e8 3e f9 ff ff       	call   11a0 <strncmp@plt>
    1862:	85 c0                	test   eax,eax
    1864:	75 28                	jne    188e <sleep@plt+0x5be>
    1866:	48 8d 85 d0 ef ff ff 	lea    rax,[rbp-0x1030]
    186d:	48 83 c0 08          	add    rax,0x8
    1871:	48 83 c0 03          	add    rax,0x3
    1875:	ba 10 00 00 00       	mov    edx,0x10
    187a:	be 00 00 00 00       	mov    esi,0x0
    187f:	48 89 c7             	mov    rdi,rax
    1882:	e8 b9 f9 ff ff       	call   1240 <strtoull@plt>
    1887:	48 89 85 d0 ef ff ff 	mov    QWORD PTR [rbp-0x1030],rax
    188e:	48 8b 85 d0 ef ff ff 	mov    rax,QWORD PTR [rbp-0x1030]
    1895:	48 89 c6             	mov    rsi,rax
    1898:	48 8d 05 78 28 00 00 	lea    rax,[rip+0x2878]        # 4117 <sleep@plt+0x2e47>
    189f:	48 89 c7             	mov    rdi,rax
    18a2:	b8 00 00 00 00       	mov    eax,0x0
    18a7:	e8 54 f9 ff ff       	call   1200 <printf@plt>
    18ac:	90                   	nop
    18ad:	48 8b 45 f8          	mov    rax,QWORD PTR [rbp-0x8]
    18b1:	64 48 2b 04 25 28 00 	sub    rax,QWORD PTR fs:0x28
    18b8:	00 00 
    18ba:	74 05                	je     18c1 <sleep@plt+0x5f1>
    18bc:	e8 1f f9 ff ff       	call   11e0 <__stack_chk_fail@plt>
    18c1:	c9                   	leave
    18c2:	c3                   	ret
    18c3:	f3 0f 1e fa          	endbr64
    18c7:	55                   	push   rbp
    18c8:	48 89 e5             	mov    rbp,rsp
    18cb:	48 83 ec 20          	sub    rsp,0x20
    18cf:	48 89 7d e8          	mov    QWORD PTR [rbp-0x18],rdi
    18d3:	89 75 e4             	mov    DWORD PTR [rbp-0x1c],esi
    18d6:	c7 45 fc 00 00 00 00 	mov    DWORD PTR [rbp-0x4],0x0
    18dd:	eb 4e                	jmp    192d <sleep@plt+0x65d>
    18df:	8b 45 fc             	mov    eax,DWORD PTR [rbp-0x4]
    18e2:	48 63 d0             	movsxd rdx,eax
    18e5:	48 8b 45 e8          	mov    rax,QWORD PTR [rbp-0x18]
    18e9:	48 01 d0             	add    rax,rdx
    18ec:	ba 01 00 00 00       	mov    edx,0x1
    18f1:	48 89 c6             	mov    rsi,rax
    18f4:	bf 00 00 00 00       	mov    edi,0x0
    18f9:	e8 32 f9 ff ff       	call   1230 <read@plt>
    18fe:	48 85 c0             	test   rax,rax
    1901:	7e 14                	jle    1917 <sleep@plt+0x647>
    1903:	8b 45 fc             	mov    eax,DWORD PTR [rbp-0x4]
    1906:	48 63 d0             	movsxd rdx,eax
    1909:	48 8b 45 e8          	mov    rax,QWORD PTR [rbp-0x18]
    190d:	48 01 d0             	add    rax,rdx
    1910:	0f b6 00             	movzx  eax,BYTE PTR [rax]
    1913:	3c 0a                	cmp    al,0xa
    1915:	75 12                	jne    1929 <sleep@plt+0x659>
    1917:	8b 45 fc             	mov    eax,DWORD PTR [rbp-0x4]
    191a:	48 63 d0             	movsxd rdx,eax
    191d:	48 8b 45 e8          	mov    rax,QWORD PTR [rbp-0x18]
    1921:	48 01 d0             	add    rax,rdx
    1924:	c6 00 00             	mov    BYTE PTR [rax],0x0
    1927:	eb 0d                	jmp    1936 <sleep@plt+0x666>
    1929:	83 45 fc 01          	add    DWORD PTR [rbp-0x4],0x1
    192d:	8b 45 fc             	mov    eax,DWORD PTR [rbp-0x4]
    1930:	3b 45 e4             	cmp    eax,DWORD PTR [rbp-0x1c]
    1933:	75 aa                	jne    18df <sleep@plt+0x60f>
    1935:	90                   	nop
    1936:	90                   	nop
    1937:	c9                   	leave
    1938:	c3                   	ret
    1939:	f3 0f 1e fa          	endbr64
    193d:	55                   	push   rbp
    193e:	48 89 e5             	mov    rbp,rsp
    1941:	48 83 ec 20          	sub    rsp,0x20
    1945:	48 89 7d e8          	mov    QWORD PTR [rbp-0x18],rdi
    1949:	48 8b 45 e8          	mov    rax,QWORD PTR [rbp-0x18]
    194d:	48 8b 80 c8 00 00 00 	mov    rax,QWORD PTR [rax+0xc8]
    1954:	48 85 c0             	test   rax,rax
    1957:	74 11                	je     196a <sleep@plt+0x69a>
    1959:	48 8d 05 d4 27 00 00 	lea    rax,[rip+0x27d4]        # 4134 <sleep@plt+0x2e64>
    1960:	48 89 c7             	mov    rdi,rax
    1963:	e8 48 f8 ff ff       	call   11b0 <puts@plt>
    1968:	eb 67                	jmp    19d1 <sleep@plt+0x701>
    196a:	bf 64 00 00 00       	mov    edi,0x64
    196f:	e8 0c f9 ff ff       	call   1280 <malloc@plt>
    1974:	48 89 c2             	mov    rdx,rax
    1977:	48 8b 45 e8          	mov    rax,QWORD PTR [rbp-0x18]
    197b:	48 89 90 c8 00 00 00 	mov    QWORD PTR [rax+0xc8],rdx
    1982:	48 8b 45 e8          	mov    rax,QWORD PTR [rbp-0x18]
    1986:	48 8b 80 c8 00 00 00 	mov    rax,QWORD PTR [rax+0xc8]
    198d:	48 89 45 f8          	mov    QWORD PTR [rbp-0x8],rax
    1991:	48 8d 05 b4 27 00 00 	lea    rax,[rip+0x27b4]        # 414c <sleep@plt+0x2e7c>
    1998:	48 89 c7             	mov    rdi,rax
    199b:	b8 00 00 00 00       	mov    eax,0x0
    19a0:	e8 5b f8 ff ff       	call   1200 <printf@plt>
    19a5:	8b 15 9d 41 00 00    	mov    edx,DWORD PTR [rip+0x419d]        # 5b48 <stderr@GLIBC_2.2.5+0x28>
    19ab:	48 8b 45 e8          	mov    rax,QWORD PTR [rbp-0x18]
    19af:	89 d6                	mov    esi,edx
    19b1:	48 89 c7             	mov    rdi,rax
    19b4:	e8 0a ff ff ff       	call   18c3 <sleep@plt+0x5f3>
    19b9:	48 8b 4d e8          	mov    rcx,QWORD PTR [rbp-0x18]
    19bd:	48 8b 45 f8          	mov    rax,QWORD PTR [rbp-0x8]
    19c1:	ba 64 00 00 00       	mov    edx,0x64
    19c6:	48 89 ce             	mov    rsi,rcx
    19c9:	48 89 c7             	mov    rdi,rax
    19cc:	e8 9f f8 ff ff       	call   1270 <memcpy@plt>
    19d1:	c9                   	leave
    19d2:	c3                   	ret
    19d3:	f3 0f 1e fa          	endbr64
    19d7:	55                   	push   rbp
    19d8:	48 89 e5             	mov    rbp,rsp
    19db:	48 83 ec 10          	sub    rsp,0x10
    19df:	48 89 7d f8          	mov    QWORD PTR [rbp-0x8],rdi
    19e3:	48 8b 45 f8          	mov    rax,QWORD PTR [rbp-0x8]
    19e7:	48 8b 80 c8 00 00 00 	mov    rax,QWORD PTR [rax+0xc8]
    19ee:	48 85 c0             	test   rax,rax
    19f1:	75 11                	jne    1a04 <sleep@plt+0x734>
    19f3:	48 8d 05 62 27 00 00 	lea    rax,[rip+0x2762]        # 415c <sleep@plt+0x2e8c>
    19fa:	48 89 c7             	mov    rdi,rax
    19fd:	e8 ae f7 ff ff       	call   11b0 <puts@plt>
    1a02:	eb 22                	jmp    1a26 <sleep@plt+0x756>
    1a04:	48 8b 45 f8          	mov    rax,QWORD PTR [rbp-0x8]
    1a08:	48 8b 80 c8 00 00 00 	mov    rax,QWORD PTR [rax+0xc8]
    1a0f:	48 89 c6             	mov    rsi,rax
    1a12:	48 8d 05 57 27 00 00 	lea    rax,[rip+0x2757]        # 4170 <sleep@plt+0x2ea0>
    1a19:	48 89 c7             	mov    rdi,rax
    1a1c:	b8 00 00 00 00       	mov    eax,0x0
    1a21:	e8 da f7 ff ff       	call   1200 <printf@plt>
    1a26:	c9                   	leave
    1a27:	c3                   	ret
    1a28:	f3 0f 1e fa          	endbr64
    1a2c:	55                   	push   rbp
    1a2d:	48 89 e5             	mov    rbp,rsp
    1a30:	48 83 ec 20          	sub    rsp,0x20
    1a34:	48 89 7d e8          	mov    QWORD PTR [rbp-0x18],rdi
    1a38:	48 8b 45 e8          	mov    rax,QWORD PTR [rbp-0x18]
    1a3c:	48 8b 80 c8 00 00 00 	mov    rax,QWORD PTR [rax+0xc8]
    1a43:	48 85 c0             	test   rax,rax
    1a46:	75 14                	jne    1a5c <sleep@plt+0x78c>
    1a48:	48 8d 05 2e 27 00 00 	lea    rax,[rip+0x272e]        # 417d <sleep@plt+0x2ead>
    1a4f:	48 89 c7             	mov    rdi,rax
    1a52:	e8 59 f7 ff ff       	call   11b0 <puts@plt>
    1a57:	e9 ab 00 00 00       	jmp    1b07 <sleep@plt+0x837>
    1a5c:	48 8d 05 2e 27 00 00 	lea    rax,[rip+0x272e]        # 4191 <sleep@plt+0x2ec1>
    1a63:	48 89 c7             	mov    rdi,rax
    1a66:	e8 45 f7 ff ff       	call   11b0 <puts@plt>
    1a6b:	be 01 00 00 00       	mov    esi,0x1
    1a70:	48 8d 05 2d 27 00 00 	lea    rax,[rip+0x272d]        # 41a4 <sleep@plt+0x2ed4>
    1a77:	48 89 c7             	mov    rdi,rax
    1a7a:	b8 00 00 00 00       	mov    eax,0x0
    1a7f:	e8 1c f8 ff ff       	call   12a0 <open@plt>
    1a84:	89 45 fc             	mov    DWORD PTR [rbp-0x4],eax
    1a87:	83 7d fc 00          	cmp    DWORD PTR [rbp-0x4],0x0
    1a8b:	79 11                	jns    1a9e <sleep@plt+0x7ce>
    1a8d:	48 8d 05 1a 27 00 00 	lea    rax,[rip+0x271a]        # 41ae <sleep@plt+0x2ede>
    1a94:	48 89 c7             	mov    rdi,rax
    1a97:	e8 14 f7 ff ff       	call   11b0 <puts@plt>
    1a9c:	eb 69                	jmp    1b07 <sleep@plt+0x837>
    1a9e:	48 8b 45 e8          	mov    rax,QWORD PTR [rbp-0x18]
    1aa2:	48 8b 80 c8 00 00 00 	mov    rax,QWORD PTR [rax+0xc8]
    1aa9:	48 89 c7             	mov    rdi,rax
    1aac:	e8 1f f7 ff ff       	call   11d0 <strlen@plt>
    1ab1:	48 89 c2             	mov    rdx,rax
    1ab4:	48 8b 45 e8          	mov    rax,QWORD PTR [rbp-0x18]
    1ab8:	48 8b 88 c8 00 00 00 	mov    rcx,QWORD PTR [rax+0xc8]
    1abf:	8b 45 fc             	mov    eax,DWORD PTR [rbp-0x4]
    1ac2:	48 89 ce             	mov    rsi,rcx
    1ac5:	89 c7                	mov    edi,eax
    1ac7:	e8 f4 f6 ff ff       	call   11c0 <write@plt>
    1acc:	8b 45 fc             	mov    eax,DWORD PTR [rbp-0x4]
    1acf:	89 c7                	mov    edi,eax
    1ad1:	e8 4a f7 ff ff       	call   1220 <close@plt>
    1ad6:	48 8b 45 e8          	mov    rax,QWORD PTR [rbp-0x18]
    1ada:	48 8b 80 c8 00 00 00 	mov    rax,QWORD PTR [rax+0xc8]
    1ae1:	48 89 c7             	mov    rdi,rax
    1ae4:	e8 a7 f6 ff ff       	call   1190 <free@plt>
    1ae9:	48 8b 45 e8          	mov    rax,QWORD PTR [rbp-0x18]
    1aed:	48 c7 80 c8 00 00 00 	mov    QWORD PTR [rax+0xc8],0x0
    1af4:	00 00 00 00 
    1af8:	48 8d 05 cc 26 00 00 	lea    rax,[rip+0x26cc]        # 41cb <sleep@plt+0x2efb>
    1aff:	48 89 c7             	mov    rdi,rax
    1b02:	e8 a9 f6 ff ff       	call   11b0 <puts@plt>
    1b07:	c9                   	leave
    1b08:	c3                   	ret
    1b09:	f3 0f 1e fa          	endbr64
    1b0d:	55                   	push   rbp
    1b0e:	48 89 e5             	mov    rbp,rsp
    1b11:	48 83 ec 10          	sub    rsp,0x10
    1b15:	48 89 7d f8          	mov    QWORD PTR [rbp-0x8],rdi
    1b19:	48 8d 05 c6 26 00 00 	lea    rax,[rip+0x26c6]        # 41e6 <sleep@plt+0x2f16>
    1b20:	48 89 c7             	mov    rdi,rax
    1b23:	e8 88 f6 ff ff       	call   11b0 <puts@plt>
    1b28:	c7 05 2a 42 00 00 01 	mov    DWORD PTR [rip+0x422a],0x1        # 5d5c <stderr@GLIBC_2.2.5+0x23c>
    1b2f:	00 00 00 
    1b32:	90                   	nop
    1b33:	c9                   	leave
    1b34:	c3                   	ret
    1b35:	f3 0f 1e fa          	endbr64
    1b39:	55                   	push   rbp
    1b3a:	48 89 e5             	mov    rbp,rsp
    1b3d:	48 81 ec a0 00 00 00 	sub    rsp,0xa0
    1b44:	48 89 bd 68 ff ff ff 	mov    QWORD PTR [rbp-0x98],rdi
    1b4b:	64 48 8b 04 25 28 00 	mov    rax,QWORD PTR fs:0x28
    1b52:	00 00 
    1b54:	48 89 45 f8          	mov    QWORD PTR [rbp-0x8],rax
    1b58:	31 c0                	xor    eax,eax
    1b5a:	48 b8 7e 3e 27 2d 36 	movabs rax,0x262b1d362d273e7e
    1b61:	1d 2b 26 
    1b64:	48 ba 3e 7c 7e 3e 2b 	movabs rdx,0x271d2f2b3e7e7c3e
    1b6b:	2f 1d 27 
    1b6e:	48 89 45 90          	mov    QWORD PTR [rbp-0x70],rax
    1b72:	48 89 55 98          	mov    QWORD PTR [rbp-0x68],rdx
    1b76:	48 b8 1d 27 2c 26 3e 	movabs rax,0x35327c3e262c271d
    1b7d:	7c 32 35 
    1b80:	48 ba 26 7f 25 37 27 	movabs rdx,0x36312737257f26
    1b87:	31 36 00 
    1b8a:	48 89 45 9e          	mov    QWORD PTR [rbp-0x62],rax
    1b8e:	48 89 55 a6          	mov    QWORD PTR [rbp-0x5a],rdx
    1b92:	c6 85 7f ff ff ff 4d 	mov    BYTE PTR [rbp-0x81],0x4d
    1b99:	48 8d 05 80 14 00 00 	lea    rax,[rip+0x1480]        # 3020 <sleep@plt+0x1d50>
    1ba0:	48 89 c7             	mov    rdi,rax
    1ba3:	e8 21 f8 ff ff       	call   13c9 <sleep@plt+0xf9>
    1ba8:	30 85 7f ff ff ff    	xor    BYTE PTR [rbp-0x81],al
    1bae:	48 8d 05 ab 15 00 00 	lea    rax,[rip+0x15ab]        # 3160 <sleep@plt+0x1e90>
    1bb5:	48 89 c7             	mov    rdi,rax
    1bb8:	e8 0c f8 ff ff       	call   13c9 <sleep@plt+0xf9>
    1bbd:	30 85 7f ff ff ff    	xor    BYTE PTR [rbp-0x81],al
    1bc3:	48 8d 05 76 16 00 00 	lea    rax,[rip+0x1676]        # 3240 <sleep@plt+0x1f70>
    1bca:	48 89 c7             	mov    rdi,rax
    1bcd:	e8 f7 f7 ff ff       	call   13c9 <sleep@plt+0xf9>
    1bd2:	30 85 7f ff ff ff    	xor    BYTE PTR [rbp-0x81],al
    1bd8:	48 8d 05 41 17 00 00 	lea    rax,[rip+0x1741]        # 3320 <sleep@plt+0x2050>
    1bdf:	48 89 c7             	mov    rdi,rax
    1be2:	e8 e2 f7 ff ff       	call   13c9 <sleep@plt+0xf9>
    1be7:	30 85 7f ff ff ff    	xor    BYTE PTR [rbp-0x81],al
    1bed:	48 8d 05 4c 18 00 00 	lea    rax,[rip+0x184c]        # 3440 <sleep@plt+0x2170>
    1bf4:	48 89 c7             	mov    rdi,rax
    1bf7:	e8 cd f7 ff ff       	call   13c9 <sleep@plt+0xf9>
    1bfc:	30 85 7f ff ff ff    	xor    BYTE PTR [rbp-0x81],al
    1c02:	48 8d 05 57 19 00 00 	lea    rax,[rip+0x1957]        # 3560 <sleep@plt+0x2290>
    1c09:	48 89 c7             	mov    rdi,rax
    1c0c:	e8 b8 f7 ff ff       	call   13c9 <sleep@plt+0xf9>
    1c11:	30 85 7f ff ff ff    	xor    BYTE PTR [rbp-0x81],al
    1c17:	48 8d 05 02 1a 00 00 	lea    rax,[rip+0x1a02]        # 3620 <sleep@plt+0x2350>
    1c1e:	48 89 c7             	mov    rdi,rax
    1c21:	e8 a3 f7 ff ff       	call   13c9 <sleep@plt+0xf9>
    1c26:	30 85 7f ff ff ff    	xor    BYTE PTR [rbp-0x81],al
    1c2c:	48 8d 05 ed 1a 00 00 	lea    rax,[rip+0x1aed]        # 3720 <sleep@plt+0x2450>
    1c33:	48 89 c7             	mov    rdi,rax
    1c36:	e8 8e f7 ff ff       	call   13c9 <sleep@plt+0xf9>
    1c3b:	30 85 7f ff ff ff    	xor    BYTE PTR [rbp-0x81],al
    1c41:	48 8d 05 78 1c 00 00 	lea    rax,[rip+0x1c78]        # 38c0 <sleep@plt+0x25f0>
    1c48:	48 89 c7             	mov    rdi,rax
    1c4b:	e8 79 f7 ff ff       	call   13c9 <sleep@plt+0xf9>
    1c50:	30 85 7f ff ff ff    	xor    BYTE PTR [rbp-0x81],al
    1c56:	48 8d 05 83 1d 00 00 	lea    rax,[rip+0x1d83]        # 39e0 <sleep@plt+0x2710>
    1c5d:	48 89 c7             	mov    rdi,rax
    1c60:	e8 64 f7 ff ff       	call   13c9 <sleep@plt+0xf9>
    1c65:	30 85 7f ff ff ff    	xor    BYTE PTR [rbp-0x81],al
    1c6b:	48 8d 05 ce 1d 00 00 	lea    rax,[rip+0x1dce]        # 3a40 <sleep@plt+0x2770>
    1c72:	48 89 c7             	mov    rdi,rax
    1c75:	e8 4f f7 ff ff       	call   13c9 <sleep@plt+0xf9>
    1c7a:	30 85 7f ff ff ff    	xor    BYTE PTR [rbp-0x81],al
    1c80:	48 8d 05 39 1e 00 00 	lea    rax,[rip+0x1e39]        # 3ac0 <sleep@plt+0x27f0>
    1c87:	48 89 c7             	mov    rdi,rax
    1c8a:	e8 3a f7 ff ff       	call   13c9 <sleep@plt+0xf9>
    1c8f:	30 85 7f ff ff ff    	xor    BYTE PTR [rbp-0x81],al
    1c95:	48 8d 05 64 1e 00 00 	lea    rax,[rip+0x1e64]        # 3b00 <sleep@plt+0x2830>
    1c9c:	48 89 c7             	mov    rdi,rax
    1c9f:	e8 25 f7 ff ff       	call   13c9 <sleep@plt+0xf9>
    1ca4:	30 85 7f ff ff ff    	xor    BYTE PTR [rbp-0x81],al
    1caa:	48 8d 05 4f 1f 00 00 	lea    rax,[rip+0x1f4f]        # 3c00 <sleep@plt+0x2930>
    1cb1:	48 89 c7             	mov    rdi,rax
    1cb4:	e8 10 f7 ff ff       	call   13c9 <sleep@plt+0xf9>
    1cb9:	30 85 7f ff ff ff    	xor    BYTE PTR [rbp-0x81],al
    1cbf:	48 8d 05 fa 1f 00 00 	lea    rax,[rip+0x1ffa]        # 3cc0 <sleep@plt+0x29f0>
    1cc6:	48 89 c7             	mov    rdi,rax
    1cc9:	e8 fb f6 ff ff       	call   13c9 <sleep@plt+0xf9>
    1cce:	30 85 7f ff ff ff    	xor    BYTE PTR [rbp-0x81],al
    1cd4:	48 8d 05 85 20 00 00 	lea    rax,[rip+0x2085]        # 3d60 <sleep@plt+0x2a90>
    1cdb:	48 89 c7             	mov    rdi,rax
    1cde:	e8 e6 f6 ff ff       	call   13c9 <sleep@plt+0xf9>
    1ce3:	30 85 7f ff ff ff    	xor    BYTE PTR [rbp-0x81],al
    1ce9:	48 8d 05 b0 21 00 00 	lea    rax,[rip+0x21b0]        # 3ea0 <sleep@plt+0x2bd0>
    1cf0:	48 89 c7             	mov    rdi,rax
    1cf3:	e8 d1 f6 ff ff       	call   13c9 <sleep@plt+0xf9>
    1cf8:	30 85 7f ff ff ff    	xor    BYTE PTR [rbp-0x81],al
    1cfe:	48 c7 45 b0 00 00 00 	mov    QWORD PTR [rbp-0x50],0x0
    1d05:	00 
    1d06:	48 c7 45 b8 00 00 00 	mov    QWORD PTR [rbp-0x48],0x0
    1d0d:	00 
    1d0e:	48 c7 45 c0 00 00 00 	mov    QWORD PTR [rbp-0x40],0x0
    1d15:	00 
    1d16:	48 c7 45 c8 00 00 00 	mov    QWORD PTR [rbp-0x38],0x0
    1d1d:	00 
    1d1e:	48 c7 45 d0 00 00 00 	mov    QWORD PTR [rbp-0x30],0x0
    1d25:	00 
    1d26:	48 c7 45 d8 00 00 00 	mov    QWORD PTR [rbp-0x28],0x0
    1d2d:	00 
    1d2e:	48 c7 45 e0 00 00 00 	mov    QWORD PTR [rbp-0x20],0x0
    1d35:	00 
    1d36:	48 c7 45 e8 00 00 00 	mov    QWORD PTR [rbp-0x18],0x0
    1d3d:	00 
    1d3e:	48 8d 05 ab 24 00 00 	lea    rax,[rip+0x24ab]        # 41f0 <sleep@plt+0x2f20>
    1d45:	48 89 c7             	mov    rdi,rax
    1d48:	e8 63 f4 ff ff       	call   11b0 <puts@plt>
    1d4d:	48 8d 05 c4 24 00 00 	lea    rax,[rip+0x24c4]        # 4218 <sleep@plt+0x2f48>
    1d54:	48 89 c7             	mov    rdi,rax
    1d57:	e8 54 f4 ff ff       	call   11b0 <puts@plt>
    1d5c:	48 8d 05 8d 24 00 00 	lea    rax,[rip+0x248d]        # 41f0 <sleep@plt+0x2f20>
    1d63:	48 89 c7             	mov    rdi,rax
    1d66:	e8 45 f4 ff ff       	call   11b0 <puts@plt>
    1d6b:	48 8d 05 c5 24 00 00 	lea    rax,[rip+0x24c5]        # 4237 <sleep@plt+0x2f67>
    1d72:	48 89 c7             	mov    rdi,rax
    1d75:	e8 36 f4 ff ff       	call   11b0 <puts@plt>
    1d7a:	48 8d 05 b7 24 00 00 	lea    rax,[rip+0x24b7]        # 4238 <sleep@plt+0x2f68>
    1d81:	48 89 c7             	mov    rdi,rax
    1d84:	e8 27 f4 ff ff       	call   11b0 <puts@plt>
    1d89:	48 8d 05 d0 24 00 00 	lea    rax,[rip+0x24d0]        # 4260 <sleep@plt+0x2f90>
    1d90:	48 89 c7             	mov    rdi,rax
    1d93:	e8 18 f4 ff ff       	call   11b0 <puts@plt>
    1d98:	48 8d 05 e9 24 00 00 	lea    rax,[rip+0x24e9]        # 4288 <sleep@plt+0x2fb8>
    1d9f:	48 89 c7             	mov    rdi,rax
    1da2:	e8 09 f4 ff ff       	call   11b0 <puts@plt>
    1da7:	48 8d 05 89 24 00 00 	lea    rax,[rip+0x2489]        # 4237 <sleep@plt+0x2f67>
    1dae:	48 89 c7             	mov    rdi,rax
    1db1:	e8 fa f3 ff ff       	call   11b0 <puts@plt>
    1db6:	48 8d 05 f3 24 00 00 	lea    rax,[rip+0x24f3]        # 42b0 <sleep@plt+0x2fe0>
    1dbd:	48 89 c7             	mov    rdi,rax
    1dc0:	e8 eb f3 ff ff       	call   11b0 <puts@plt>
    1dc5:	48 8d 05 14 25 00 00 	lea    rax,[rip+0x2514]        # 42e0 <sleep@plt+0x3010>
    1dcc:	48 89 c7             	mov    rdi,rax
    1dcf:	e8 dc f3 ff ff       	call   11b0 <puts@plt>
    1dd4:	48 8d 05 5c 24 00 00 	lea    rax,[rip+0x245c]        # 4237 <sleep@plt+0x2f67>
    1ddb:	48 89 c7             	mov    rdi,rax
    1dde:	e8 cd f3 ff ff       	call   11b0 <puts@plt>
    1de3:	48 8d 05 1e 25 00 00 	lea    rax,[rip+0x251e]        # 4308 <sleep@plt+0x3038>
    1dea:	48 89 c7             	mov    rdi,rax
    1ded:	b8 00 00 00 00       	mov    eax,0x0
    1df2:	e8 09 f4 ff ff       	call   1200 <printf@plt>
    1df7:	48 8d 45 b0          	lea    rax,[rbp-0x50]
    1dfb:	ba 3f 00 00 00       	mov    edx,0x3f
    1e00:	48 89 c6             	mov    rsi,rax
    1e03:	bf 00 00 00 00       	mov    edi,0x0
    1e08:	e8 23 f4 ff ff       	call   1230 <read@plt>
    1e0d:	c7 45 80 00 00 00 00 	mov    DWORD PTR [rbp-0x80],0x0
    1e14:	eb 1e                	jmp    1e34 <sleep@plt+0xb64>
    1e16:	8b 45 80             	mov    eax,DWORD PTR [rbp-0x80]
    1e19:	48 98                	cdqe
    1e1b:	0f b6 44 05 b0       	movzx  eax,BYTE PTR [rbp+rax*1-0x50]
    1e20:	3c 0a                	cmp    al,0xa
    1e22:	75 0c                	jne    1e30 <sleep@plt+0xb60>
    1e24:	8b 45 80             	mov    eax,DWORD PTR [rbp-0x80]
    1e27:	48 98                	cdqe
    1e29:	c6 44 05 b0 00       	mov    BYTE PTR [rbp+rax*1-0x50],0x0
    1e2e:	eb 0a                	jmp    1e3a <sleep@plt+0xb6a>
    1e30:	83 45 80 01          	add    DWORD PTR [rbp-0x80],0x1
    1e34:	83 7d 80 3e          	cmp    DWORD PTR [rbp-0x80],0x3e
    1e38:	7e dc                	jle    1e16 <sleep@plt+0xb46>
    1e3a:	48 8d 45 b0          	lea    rax,[rbp-0x50]
    1e3e:	48 8d 15 ce 24 00 00 	lea    rdx,[rip+0x24ce]        # 4313 <sleep@plt+0x3043>
    1e45:	48 89 d6             	mov    rsi,rdx
    1e48:	48 89 c7             	mov    rdi,rax
    1e4b:	e8 10 f4 ff ff       	call   1260 <strcmp@plt>
    1e50:	85 c0                	test   eax,eax
    1e52:	74 68                	je     1ebc <sleep@plt+0xbec>
    1e54:	48 8d 45 b0          	lea    rax,[rbp-0x50]
    1e58:	48 8d 15 bc 24 00 00 	lea    rdx,[rip+0x24bc]        # 431b <sleep@plt+0x304b>
    1e5f:	48 89 d6             	mov    rsi,rdx
    1e62:	48 89 c7             	mov    rdi,rax
    1e65:	e8 f6 f3 ff ff       	call   1260 <strcmp@plt>
    1e6a:	85 c0                	test   eax,eax
    1e6c:	74 4e                	je     1ebc <sleep@plt+0xbec>
    1e6e:	48 8d 45 b0          	lea    rax,[rbp-0x50]
    1e72:	48 8d 15 ab 24 00 00 	lea    rdx,[rip+0x24ab]        # 4324 <sleep@plt+0x3054>
    1e79:	48 89 d6             	mov    rsi,rdx
    1e7c:	48 89 c7             	mov    rdi,rax
    1e7f:	e8 dc f3 ff ff       	call   1260 <strcmp@plt>
    1e84:	85 c0                	test   eax,eax
    1e86:	74 34                	je     1ebc <sleep@plt+0xbec>
    1e88:	48 8d 45 b0          	lea    rax,[rbp-0x50]
    1e8c:	48 8d 15 97 24 00 00 	lea    rdx,[rip+0x2497]        # 432a <sleep@plt+0x305a>
    1e93:	48 89 d6             	mov    rsi,rdx
    1e96:	48 89 c7             	mov    rdi,rax
    1e99:	e8 c2 f3 ff ff       	call   1260 <strcmp@plt>
    1e9e:	85 c0                	test   eax,eax
    1ea0:	74 1a                	je     1ebc <sleep@plt+0xbec>
    1ea2:	48 8d 45 b0          	lea    rax,[rbp-0x50]
    1ea6:	48 8d 15 83 24 00 00 	lea    rdx,[rip+0x2483]        # 4330 <sleep@plt+0x3060>
    1ead:	48 89 d6             	mov    rsi,rdx
    1eb0:	48 89 c7             	mov    rdi,rax
    1eb3:	e8 a8 f3 ff ff       	call   1260 <strcmp@plt>
    1eb8:	85 c0                	test   eax,eax
    1eba:	75 46                	jne    1f02 <sleep@plt+0xc32>
    1ebc:	48 8d 05 7d 24 00 00 	lea    rax,[rip+0x247d]        # 4340 <sleep@plt+0x3070>
    1ec3:	48 89 c7             	mov    rdi,rax
    1ec6:	e8 e5 f2 ff ff       	call   11b0 <puts@plt>
    1ecb:	48 8d 05 93 24 00 00 	lea    rax,[rip+0x2493]        # 4365 <sleep@plt+0x3095>
    1ed2:	48 89 c7             	mov    rdi,rax
    1ed5:	e8 d6 f2 ff ff       	call   11b0 <puts@plt>
    1eda:	48 8d 05 97 24 00 00 	lea    rax,[rip+0x2497]        # 4378 <sleep@plt+0x30a8>
    1ee1:	48 89 c7             	mov    rdi,rax
    1ee4:	e8 c7 f2 ff ff       	call   11b0 <puts@plt>
    1ee9:	48 8d 05 aa 24 00 00 	lea    rax,[rip+0x24aa]        # 439a <sleep@plt+0x30ca>
    1ef0:	48 89 c7             	mov    rdi,rax
    1ef3:	e8 b8 f2 ff ff       	call   11b0 <puts@plt>
    1ef8:	bf 01 00 00 00       	mov    edi,0x1
    1efd:	e8 be f3 ff ff       	call   12c0 <exit@plt>
    1f02:	c7 45 84 01 00 00 00 	mov    DWORD PTR [rbp-0x7c],0x1
    1f09:	c7 45 88 00 00 00 00 	mov    DWORD PTR [rbp-0x78],0x0
    1f10:	c7 45 8c 00 00 00 00 	mov    DWORD PTR [rbp-0x74],0x0
    1f17:	eb 33                	jmp    1f4c <sleep@plt+0xc7c>
    1f19:	8b 45 8c             	mov    eax,DWORD PTR [rbp-0x74]
    1f1c:	48 98                	cdqe
    1f1e:	0f b6 44 05 b0       	movzx  eax,BYTE PTR [rbp+rax*1-0x50]
    1f23:	0f be d0             	movsx  edx,al
    1f26:	8b 45 8c             	mov    eax,DWORD PTR [rbp-0x74]
    1f29:	48 98                	cdqe
    1f2b:	0f b6 44 05 90       	movzx  eax,BYTE PTR [rbp+rax*1-0x70]
    1f30:	32 85 7f ff ff ff    	xor    al,BYTE PTR [rbp-0x81]
    1f36:	0f b6 c0             	movzx  eax,al
    1f39:	39 c2                	cmp    edx,eax
    1f3b:	74 07                	je     1f44 <sleep@plt+0xc74>
    1f3d:	c7 45 84 00 00 00 00 	mov    DWORD PTR [rbp-0x7c],0x0
    1f44:	83 45 88 01          	add    DWORD PTR [rbp-0x78],0x1
    1f48:	83 45 8c 01          	add    DWORD PTR [rbp-0x74],0x1
    1f4c:	8b 45 8c             	mov    eax,DWORD PTR [rbp-0x74]
    1f4f:	48 98                	cdqe
    1f51:	0f b6 44 05 90       	movzx  eax,BYTE PTR [rbp+rax*1-0x70]
    1f56:	84 c0                	test   al,al
    1f58:	75 bf                	jne    1f19 <sleep@plt+0xc49>
    1f5a:	8b 45 88             	mov    eax,DWORD PTR [rbp-0x78]
    1f5d:	48 98                	cdqe
    1f5f:	0f b6 44 05 b0       	movzx  eax,BYTE PTR [rbp+rax*1-0x50]
    1f64:	84 c0                	test   al,al
    1f66:	74 07                	je     1f6f <sleep@plt+0xc9f>
    1f68:	c7 45 84 00 00 00 00 	mov    DWORD PTR [rbp-0x7c],0x0
    1f6f:	83 7d 84 00          	cmp    DWORD PTR [rbp-0x7c],0x0
    1f73:	74 1b                	je     1f90 <sleep@plt+0xcc0>
    1f75:	c7 05 d9 3d 00 00 01 	mov    DWORD PTR [rip+0x3dd9],0x1        # 5d58 <stderr@GLIBC_2.2.5+0x238>
    1f7c:	00 00 00 
    1f7f:	48 8d 05 32 24 00 00 	lea    rax,[rip+0x2432]        # 43b8 <sleep@plt+0x30e8>
    1f86:	48 89 c7             	mov    rdi,rax
    1f89:	e8 22 f2 ff ff       	call   11b0 <puts@plt>
    1f8e:	eb 0f                	jmp    1f9f <sleep@plt+0xccf>
    1f90:	48 8d 05 45 24 00 00 	lea    rax,[rip+0x2445]        # 43dc <sleep@plt+0x310c>
    1f97:	48 89 c7             	mov    rdi,rax
    1f9a:	e8 11 f2 ff ff       	call   11b0 <puts@plt>
    1f9f:	90                   	nop
    1fa0:	48 8b 45 f8          	mov    rax,QWORD PTR [rbp-0x8]
    1fa4:	64 48 2b 04 25 28 00 	sub    rax,QWORD PTR fs:0x28
    1fab:	00 00 
    1fad:	74 05                	je     1fb4 <sleep@plt+0xce4>
    1faf:	e8 2c f2 ff ff       	call   11e0 <__stack_chk_fail@plt>
    1fb4:	c9                   	leave
    1fb5:	c3                   	ret
    1fb6:	f3 0f 1e fa          	endbr64
    1fba:	55                   	push   rbp
    1fbb:	48 89 e5             	mov    rbp,rsp
    1fbe:	48 83 ec 10          	sub    rsp,0x10
    1fc2:	48 89 7d f8          	mov    QWORD PTR [rbp-0x8],rdi
    1fc6:	48 8b 45 f8          	mov    rax,QWORD PTR [rbp-0x8]
    1fca:	48 8b 80 c8 00 00 00 	mov    rax,QWORD PTR [rax+0xc8]
    1fd1:	48 85 c0             	test   rax,rax
    1fd4:	75 11                	jne    1fe7 <sleep@plt+0xd17>
    1fd6:	48 8d 05 0e 24 00 00 	lea    rax,[rip+0x240e]        # 43eb <sleep@plt+0x311b>
    1fdd:	48 89 c7             	mov    rdi,rax
    1fe0:	e8 cb f1 ff ff       	call   11b0 <puts@plt>
    1fe5:	eb 28                	jmp    200f <sleep@plt+0xd3f>
    1fe7:	48 8d 05 15 24 00 00 	lea    rax,[rip+0x2415]        # 4403 <sleep@plt+0x3133>
    1fee:	48 89 c7             	mov    rdi,rax
    1ff1:	e8 ba f1 ff ff       	call   11b0 <puts@plt>
    1ff6:	bf 01 00 00 00       	mov    edi,0x1
    1ffb:	e8 d0 f2 ff ff       	call   12d0 <sleep@plt>
    2000:	48 8d 05 19 24 00 00 	lea    rax,[rip+0x2419]        # 4420 <sleep@plt+0x3150>
    2007:	48 89 c7             	mov    rdi,rax
    200a:	e8 a1 f1 ff ff       	call   11b0 <puts@plt>
    200f:	c9                   	leave
    2010:	c3                   	ret
    2011:	f3 0f 1e fa          	endbr64
    2015:	55                   	push   rbp
    2016:	48 89 e5             	mov    rbp,rsp
    2019:	48 81 ec f0 00 00 00 	sub    rsp,0xf0
    2020:	64 48 8b 04 25 28 00 	mov    rax,QWORD PTR fs:0x28
    2027:	00 00 
    2029:	48 89 45 f8          	mov    QWORD PTR [rbp-0x8],rax
    202d:	31 c0                	xor    eax,eax
    202f:	b8 00 00 00 00       	mov    eax,0x0
    2034:	e8 a5 f3 ff ff       	call   13de <sleep@plt+0x10e>
    2039:	48 8d 95 20 ff ff ff 	lea    rdx,[rbp-0xe0]
    2040:	b8 00 00 00 00       	mov    eax,0x0
    2045:	b9 1a 00 00 00       	mov    ecx,0x1a
    204a:	48 89 d7             	mov    rdi,rdx
    204d:	f3 48 ab             	rep stos QWORD PTR [rdi],rax
    2050:	e9 3d 01 00 00       	jmp    2192 <sleep@plt+0xec2>
    2055:	8b 05 fd 3c 00 00    	mov    eax,DWORD PTR [rip+0x3cfd]        # 5d58 <stderr@GLIBC_2.2.5+0x238>
    205b:	85 c0                	test   eax,eax
    205d:	0f 85 ad 00 00 00    	jne    2110 <sleep@plt+0xe40>
    2063:	48 8d 05 e0 23 00 00 	lea    rax,[rip+0x23e0]        # 444a <sleep@plt+0x317a>
    206a:	48 89 c7             	mov    rdi,rax
    206d:	e8 3e f1 ff ff       	call   11b0 <puts@plt>
    2072:	48 8d 05 67 1f 00 00 	lea    rax,[rip+0x1f67]        # 3fe0 <sleep@plt+0x2d10>
    2079:	48 89 c7             	mov    rdi,rax
    207c:	e8 2f f1 ff ff       	call   11b0 <puts@plt>
    2081:	48 8d 05 43 1f 00 00 	lea    rax,[rip+0x1f43]        # 3fcb <sleep@plt+0x2cfb>
    2088:	48 89 c7             	mov    rdi,rax
    208b:	e8 20 f1 ff ff       	call   11b0 <puts@plt>
    2090:	48 8d 05 c9 23 00 00 	lea    rax,[rip+0x23c9]        # 4460 <sleep@plt+0x3190>
    2097:	48 89 c7             	mov    rdi,rax
    209a:	e8 11 f1 ff ff       	call   11b0 <puts@plt>
    209f:	48 8d 05 c3 23 00 00 	lea    rax,[rip+0x23c3]        # 4469 <sleep@plt+0x3199>
    20a6:	48 89 c7             	mov    rdi,rax
    20a9:	e8 02 f1 ff ff       	call   11b0 <puts@plt>
    20ae:	48 8d 05 c2 1f 00 00 	lea    rax,[rip+0x1fc2]        # 4077 <sleep@plt+0x2da7>
    20b5:	48 89 c7             	mov    rdi,rax
    20b8:	b8 00 00 00 00       	mov    eax,0x0
    20bd:	e8 3e f1 ff ff       	call   1200 <printf@plt>
    20c2:	b8 00 00 00 00       	mov    eax,0x0
    20c7:	e8 f9 f4 ff ff       	call   15c5 <sleep@plt+0x2f5>
    20cc:	89 85 1c ff ff ff    	mov    DWORD PTR [rbp-0xe4],eax
    20d2:	83 bd 1c ff ff ff 01 	cmp    DWORD PTR [rbp-0xe4],0x1
    20d9:	75 14                	jne    20ef <sleep@plt+0xe1f>
    20db:	48 8d 85 20 ff ff ff 	lea    rax,[rbp-0xe0]
    20e2:	48 89 c7             	mov    rdi,rax
    20e5:	e8 4b fa ff ff       	call   1b35 <sleep@plt+0x865>
    20ea:	e9 a3 00 00 00       	jmp    2192 <sleep@plt+0xec2>
    20ef:	83 bd 1c ff ff ff 02 	cmp    DWORD PTR [rbp-0xe4],0x2
    20f6:	0f 84 a6 00 00 00    	je     21a2 <sleep@plt+0xed2>
    20fc:	48 8d 05 6e 23 00 00 	lea    rax,[rip+0x236e]        # 4471 <sleep@plt+0x31a1>
    2103:	48 89 c7             	mov    rdi,rax
    2106:	e8 a5 f0 ff ff       	call   11b0 <puts@plt>
    210b:	e9 82 00 00 00       	jmp    2192 <sleep@plt+0xec2>
    2110:	b8 00 00 00 00       	mov    eax,0x0
    2115:	e8 e7 f3 ff ff       	call   1501 <sleep@plt+0x231>
    211a:	b8 00 00 00 00       	mov    eax,0x0
    211f:	e8 a1 f4 ff ff       	call   15c5 <sleep@plt+0x2f5>
    2124:	89 85 18 ff ff ff    	mov    DWORD PTR [rbp-0xe8],eax
    212a:	83 bd 18 ff ff ff 00 	cmp    DWORD PTR [rbp-0xe8],0x0
    2131:	7e 50                	jle    2183 <sleep@plt+0xeb3>
    2133:	83 bd 18 ff ff ff 08 	cmp    DWORD PTR [rbp-0xe8],0x8
    213a:	7f 47                	jg     2183 <sleep@plt+0xeb3>
    213c:	48 8b 05 0d 3c 00 00 	mov    rax,QWORD PTR [rip+0x3c0d]        # 5d50 <stderr@GLIBC_2.2.5+0x230>
    2143:	8b 95 18 ff ff ff    	mov    edx,DWORD PTR [rbp-0xe8]
    2149:	48 63 d2             	movsxd rdx,edx
    214c:	48 c1 e2 03          	shl    rdx,0x3
    2150:	48 01 d0             	add    rax,rdx
    2153:	48 8b 00             	mov    rax,QWORD PTR [rax]
    2156:	48 85 c0             	test   rax,rax
    2159:	74 37                	je     2192 <sleep@plt+0xec2>
    215b:	48 8b 05 ee 3b 00 00 	mov    rax,QWORD PTR [rip+0x3bee]        # 5d50 <stderr@GLIBC_2.2.5+0x230>
    2162:	8b 95 18 ff ff ff    	mov    edx,DWORD PTR [rbp-0xe8]
    2168:	48 63 d2             	movsxd rdx,edx
    216b:	48 c1 e2 03          	shl    rdx,0x3
    216f:	48 01 d0             	add    rax,rdx
    2172:	48 8b 10             	mov    rdx,QWORD PTR [rax]
    2175:	48 8d 85 20 ff ff ff 	lea    rax,[rbp-0xe0]
    217c:	48 89 c7             	mov    rdi,rax
    217f:	ff d2                	call   rdx
    2181:	eb 0f                	jmp    2192 <sleep@plt+0xec2>
    2183:	48 8d 05 e7 22 00 00 	lea    rax,[rip+0x22e7]        # 4471 <sleep@plt+0x31a1>
    218a:	48 89 c7             	mov    rdi,rax
    218d:	e8 1e f0 ff ff       	call   11b0 <puts@plt>
    2192:	8b 05 c4 3b 00 00    	mov    eax,DWORD PTR [rip+0x3bc4]        # 5d5c <stderr@GLIBC_2.2.5+0x23c>
    2198:	85 c0                	test   eax,eax
    219a:	0f 84 b5 fe ff ff    	je     2055 <sleep@plt+0xd85>
    21a0:	eb 01                	jmp    21a3 <sleep@plt+0xed3>
    21a2:	90                   	nop
    21a3:	b8 00 00 00 00       	mov    eax,0x0
    21a8:	48 8b 55 f8          	mov    rdx,QWORD PTR [rbp-0x8]
    21ac:	64 48 2b 14 25 28 00 	sub    rdx,QWORD PTR fs:0x28
    21b3:	00 00 
    21b5:	74 05                	je     21bc <sleep@plt+0xeec>
    21b7:	e8 24 f0 ff ff       	call   11e0 <__stack_chk_fail@plt>
    21bc:	c9                   	leave
    21bd:	c3                   	ret
    21be:	f3 0f 1e fa          	endbr64
    21c2:	55                   	push   rbp
    21c3:	48 89 e5             	mov    rbp,rsp
    21c6:	48 8d 05 b4 22 00 00 	lea    rax,[rip+0x22b4]        # 4481 <sleep@plt+0x31b1>
    21cd:	48 89 c7             	mov    rdi,rax
    21d0:	e8 1b f0 ff ff       	call   11f0 <system@plt>
    21d5:	90                   	nop
    21d6:	5d                   	pop    rbp
    21d7:	c3                   	ret

Disassembly of section .fini:

00000000000021d8 <.fini>:
    21d8:	f3 0f 1e fa          	endbr64
    21dc:	48 83 ec 08          	sub    rsp,0x8
    21e0:	48 83 c4 08          	add    rsp,0x8
    21e4:	c3                   	ret
