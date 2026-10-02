
script/offline_audit/collector_code_1136fa4be.bin:     file format binary


Disassembly of section .data:

0000000000401000 <.data>:
  401000:	48 83 ec 08          	sub    $0x8,%rsp
  401004:	48 8b 05 dd 3f 00 00 	mov    0x3fdd(%rip),%rax        # 0x404fe8
  40100b:	48 85 c0             	test   %rax,%rax
  40100e:	74 05                	je     0x401015
  401010:	e8 5b 00 00 00       	call   0x401070
  401015:	48 83 c4 08          	add    $0x8,%rsp
  401019:	c3                   	ret
  40101a:	00 00                	add    %al,(%rax)
  40101c:	00 00                	add    %al,(%rax)
  40101e:	00 00                	add    %al,(%rax)
  401020:	ff 35 e2 3f 00 00    	push   0x3fe2(%rip)        # 0x405008
  401026:	ff 25 e4 3f 00 00    	jmp    *0x3fe4(%rip)        # 0x405010
  40102c:	0f 1f 40 00          	nopl   0x0(%rax)
  401030:	ff 25 e2 3f 00 00    	jmp    *0x3fe2(%rip)        # 0x405018
  401036:	68 00 00 00 00       	push   $0x0
  40103b:	e9 e0 ff ff ff       	jmp    0x401020
  401040:	ff 25 da 3f 00 00    	jmp    *0x3fda(%rip)        # 0x405020
  401046:	68 01 00 00 00       	push   $0x1
  40104b:	e9 d0 ff ff ff       	jmp    0x401020
  401050:	ff 25 d2 3f 00 00    	jmp    *0x3fd2(%rip)        # 0x405028
  401056:	68 02 00 00 00       	push   $0x2
  40105b:	e9 c0 ff ff ff       	jmp    0x401020
  401060:	ff 25 ca 3f 00 00    	jmp    *0x3fca(%rip)        # 0x405030
  401066:	68 03 00 00 00       	push   $0x3
  40106b:	e9 b0 ff ff ff       	jmp    0x401020
  401070:	ff 25 c2 3f 00 00    	jmp    *0x3fc2(%rip)        # 0x405038
  401076:	68 04 00 00 00       	push   $0x4
  40107b:	e9 a0 ff ff ff       	jmp    0x401020
  401080:	ff 25 ba 3f 00 00    	jmp    *0x3fba(%rip)        # 0x405040
  401086:	68 05 00 00 00       	push   $0x5
  40108b:	e9 90 ff ff ff       	jmp    0x401020
  401090:	ff 25 b2 3f 00 00    	jmp    *0x3fb2(%rip)        # 0x405048
  401096:	68 06 00 00 00       	push   $0x6
  40109b:	e9 80 ff ff ff       	jmp    0x401020
  4010a0:	ff 25 aa 3f 00 00    	jmp    *0x3faa(%rip)        # 0x405050
  4010a6:	68 07 00 00 00       	push   $0x7
  4010ab:	e9 70 ff ff ff       	jmp    0x401020
  4010b0:	48 8d 3d a1 3f 00 00 	lea    0x3fa1(%rip),%rdi        # 0x405058
  4010b7:	48 8d 05 9a 3f 00 00 	lea    0x3f9a(%rip),%rax        # 0x405058
  4010be:	48 39 f8             	cmp    %rdi,%rax
  4010c1:	74 15                	je     0x4010d8
  4010c3:	48 8b 05 16 3f 00 00 	mov    0x3f16(%rip),%rax        # 0x404fe0
  4010ca:	48 85 c0             	test   %rax,%rax
  4010cd:	74 09                	je     0x4010d8
  4010cf:	ff e0                	jmp    *%rax
  4010d1:	0f 1f 80 00 00 00 00 	nopl   0x0(%rax)
  4010d8:	c3                   	ret
  4010d9:	0f 1f 80 00 00 00 00 	nopl   0x0(%rax)
  4010e0:	48 8d 3d 71 3f 00 00 	lea    0x3f71(%rip),%rdi        # 0x405058
  4010e7:	48 8d 35 6a 3f 00 00 	lea    0x3f6a(%rip),%rsi        # 0x405058
  4010ee:	48 29 fe             	sub    %rdi,%rsi
  4010f1:	48 89 f0             	mov    %rsi,%rax
  4010f4:	48 c1 ee 3f          	shr    $0x3f,%rsi
  4010f8:	48 c1 f8 03          	sar    $0x3,%rax
  4010fc:	48 01 c6             	add    %rax,%rsi
  4010ff:	48 d1 fe             	sar    $1,%rsi
  401102:	74 14                	je     0x401118
  401104:	48 8b 05 e5 3e 00 00 	mov    0x3ee5(%rip),%rax        # 0x404ff0
  40110b:	48 85 c0             	test   %rax,%rax
  40110e:	74 08                	je     0x401118
  401110:	ff e0                	jmp    *%rax
  401112:	66 0f 1f 44 00 00    	nopw   0x0(%rax,%rax,1)
  401118:	c3                   	ret
  401119:	0f 1f 80 00 00 00 00 	nopl   0x0(%rax)
  401120:	80 3d 31 3f 00 00 00 	cmpb   $0x0,0x3f31(%rip)        # 0x405058
  401127:	75 2f                	jne    0x401158
  401129:	55                   	push   %rbp
  40112a:	48 83 3d c6 3e 00 00 	cmpq   $0x0,0x3ec6(%rip)        # 0x404ff8
  401131:	00 
  401132:	48 89 e5             	mov    %rsp,%rbp
  401135:	74 0c                	je     0x401143
  401137:	48 8d 3d ca 3c 00 00 	lea    0x3cca(%rip),%rdi        # 0x404e08
  40113e:	e8 5d ff ff ff       	call   0x4010a0
  401143:	e8 68 ff ff ff       	call   0x4010b0
  401148:	c6 05 09 3f 00 00 01 	movb   $0x1,0x3f09(%rip)        # 0x405058
  40114f:	5d                   	pop    %rbp
  401150:	c3                   	ret
  401151:	0f 1f 80 00 00 00 00 	nopl   0x0(%rax)
  401158:	c3                   	ret
  401159:	0f 1f 80 00 00 00 00 	nopl   0x0(%rax)
  401160:	e9 7b ff ff ff       	jmp    0x4010e0
  401165:	66 2e 0f 1f 84 00 00 	cs nopw 0x0(%rax,%rax,1)
  40116c:	00 00 00 
  40116f:	90                   	nop
  401170:	41 57                	push   %r15
  401172:	48 89 f9             	mov    %rdi,%rcx
  401175:	41 56                	push   %r14
  401177:	41 55                	push   %r13
  401179:	41 54                	push   %r12
  40117b:	55                   	push   %rbp
  40117c:	53                   	push   %rbx
  40117d:	48 83 ec 60          	sub    $0x60,%rsp
  401181:	48 8b 41 08          	mov    0x8(%rcx),%rax
  401185:	4c 8b 79 60          	mov    0x60(%rcx),%r15
  401189:	83 fe 18             	cmp    $0x18,%esi
  40118c:	48 89 7c 24 50       	mov    %rdi,0x50(%rsp)
  401191:	4c 8b 41 50          	mov    0x50(%rcx),%r8
  401195:	48 89 44 24 98       	mov    %rax,-0x68(%rsp)
  40119a:	48 8b 41 10          	mov    0x10(%rcx),%rax
  40119e:	48 8b 3f             	mov    (%rdi),%rdi
  4011a1:	48 89 44 24 a0       	mov    %rax,-0x60(%rsp)
  4011a6:	48 8b 41 18          	mov    0x18(%rcx),%rax
  4011aa:	48 89 44 24 a8       	mov    %rax,-0x58(%rsp)
  4011af:	48 8b 41 20          	mov    0x20(%rcx),%rax
  4011b3:	48 89 44 24 b0       	mov    %rax,-0x50(%rsp)
  4011b8:	48 8b 41 28          	mov    0x28(%rcx),%rax
  4011bc:	48 89 44 24 b8       	mov    %rax,-0x48(%rsp)
  4011c1:	48 8b 41 30          	mov    0x30(%rcx),%rax
  4011c5:	48 89 44 24 c0       	mov    %rax,-0x40(%rsp)
  4011ca:	48 8b 41 38          	mov    0x38(%rcx),%rax
  4011ce:	48 89 44 24 c8       	mov    %rax,-0x38(%rsp)
  4011d3:	48 8b 41 40          	mov    0x40(%rcx),%rax
  4011d7:	48 89 44 24 d0       	mov    %rax,-0x30(%rsp)
  4011dc:	48 8b 41 48          	mov    0x48(%rcx),%rax
  4011e0:	48 89 44 24 d8       	mov    %rax,-0x28(%rsp)
  4011e5:	48 8b 41 58          	mov    0x58(%rcx),%rax
  4011e9:	48 89 44 24 e0       	mov    %rax,-0x20(%rsp)
  4011ee:	48 8b 41 68          	mov    0x68(%rcx),%rax
  4011f2:	48 89 44 24 e8       	mov    %rax,-0x18(%rsp)
  4011f7:	48 8b 81 80 00 00 00 	mov    0x80(%rcx),%rax
  4011fe:	48 8b 59 70          	mov    0x70(%rcx),%rbx
  401202:	4c 8b 49 78          	mov    0x78(%rcx),%r9
  401206:	48 89 44 24 f0       	mov    %rax,-0x10(%rsp)
  40120b:	48 8b 81 98 00 00 00 	mov    0x98(%rcx),%rax
  401212:	48 8b 91 b8 00 00 00 	mov    0xb8(%rcx),%rdx
  401219:	4c 8b 91 88 00 00 00 	mov    0x88(%rcx),%r10
  401220:	4c 89 cd             	mov    %r9,%rbp
  401223:	49 89 d9             	mov    %rbx,%r9
  401226:	48 89 44 24 f8       	mov    %rax,-0x8(%rsp)
  40122b:	4c 8b b1 90 00 00 00 	mov    0x90(%rcx),%r14
  401232:	48 8b 81 a0 00 00 00 	mov    0xa0(%rcx),%rax
  401239:	4c 8b 99 a8 00 00 00 	mov    0xa8(%rcx),%r11
  401240:	48 89 14 24          	mov    %rdx,(%rsp)
  401244:	ba 0c 00 00 00       	mov    $0xc,%edx
  401249:	4c 8b a1 b0 00 00 00 	mov    0xb0(%rcx),%r12
  401250:	48 8b 89 c0 00 00 00 	mov    0xc0(%rcx),%rcx
  401257:	48 89 c3             	mov    %rax,%rbx
  40125a:	48 89 4c 24 08       	mov    %rcx,0x8(%rsp)
  40125f:	b9 00 00 00 00       	mov    $0x0,%ecx
  401264:	0f 45 ca             	cmovne %edx,%ecx
  401267:	48 8d 15 32 1e 00 00 	lea    0x1e32(%rip),%rdx        # 0x4030a0
  40126e:	89 ce                	mov    %ecx,%esi
  401270:	48 8d 14 f2          	lea    (%rdx,%rsi,8),%rdx
  401274:	48 89 54 24 88       	mov    %rdx,-0x78(%rsp)
  401279:	ba 17 00 00 00       	mov    $0x17,%edx
  40127e:	29 ca                	sub    %ecx,%edx
  401280:	48 8d 0d 21 1e 00 00 	lea    0x1e21(%rip),%rcx        # 0x4030a8
  401287:	48 01 f2             	add    %rsi,%rdx
  40128a:	48 8d 34 d1          	lea    (%rcx,%rdx,8),%rsi
  40128e:	48 89 74 24 48       	mov    %rsi,0x48(%rsp)
  401293:	4c 89 fe             	mov    %r15,%rsi
  401296:	49 89 ff             	mov    %rdi,%r15
  401299:	0f 1f 80 00 00 00 00 	nopl   0x0(%rax)
  4012a0:	48 8b 44 24 98       	mov    -0x68(%rsp),%rax
  4012a5:	48 33 44 24 c0       	xor    -0x40(%rsp),%rax
  4012aa:	48 33 44 24 e0       	xor    -0x20(%rsp),%rax
  4012af:	48 33 44 24 f0       	xor    -0x10(%rsp),%rax
  4012b4:	49 89 c5             	mov    %rax,%r13
  4012b7:	48 8b 44 24 a0       	mov    -0x60(%rsp),%rax
  4012bc:	48 33 44 24 c8       	xor    -0x38(%rsp),%rax
  4012c1:	48 31 f0             	xor    %rsi,%rax
  4012c4:	48 8b 54 24 a8       	mov    -0x58(%rsp),%rdx
  4012c9:	48 33 54 24 d0       	xor    -0x30(%rsp),%rdx
  4012ce:	4d 31 dd             	xor    %r11,%r13
  4012d1:	4c 31 d0             	xor    %r10,%rax
  4012d4:	48 33 54 24 e8       	xor    -0x18(%rsp),%rdx
  4012d9:	48 8b 4c 24 b8       	mov    -0x48(%rsp),%rcx
  4012de:	48 89 c7             	mov    %rax,%rdi
  4012e1:	4c 31 f2             	xor    %r14,%rdx
  4012e4:	48 33 14 24          	xor    (%rsp),%rdx
  4012e8:	4c 89 e8             	mov    %r13,%rax
  4012eb:	4c 31 e7             	xor    %r12,%rdi
  4012ee:	48 89 54 24 18       	mov    %rdx,0x18(%rsp)
  4012f3:	4c 31 f9             	xor    %r15,%rcx
  4012f6:	48 d1 c0             	rol    $1,%rax
  4012f9:	48 89 7c 24 10       	mov    %rdi,0x10(%rsp)
  4012fe:	48 8b 7c 24 b0       	mov    -0x50(%rsp),%rdi
  401303:	4c 31 c1             	xor    %r8,%rcx
  401306:	48 33 7c 24 d8       	xor    -0x28(%rsp),%rdi
  40130b:	48 31 e9             	xor    %rbp,%rcx
  40130e:	48 89 fa             	mov    %rdi,%rdx
  401311:	4c 89 ff             	mov    %r15,%rdi
  401314:	4c 8b 7c 24 b8       	mov    -0x48(%rsp),%r15
  401319:	48 31 d9             	xor    %rbx,%rcx
  40131c:	4c 31 ca             	xor    %r9,%rdx
  40131f:	48 33 54 24 f8       	xor    -0x8(%rsp),%rdx
  401324:	48 33 54 24 08       	xor    0x8(%rsp),%rdx
  401329:	48 31 d0             	xor    %rdx,%rax
  40132c:	49 31 c7             	xor    %rax,%r15
  40132f:	48 31 c7             	xor    %rax,%rdi
  401332:	49 31 c0             	xor    %rax,%r8
  401335:	48 31 c5             	xor    %rax,%rbp
  401338:	49 c1 cf 1c          	ror    $0x1c,%r15
  40133c:	48 31 d8             	xor    %rbx,%rax
  40133f:	49 c1 c0 03          	rol    $0x3,%r8
  401343:	48 8b 5c 24 f0       	mov    -0x10(%rsp),%rbx
  401348:	4c 89 7c 24 20       	mov    %r15,0x20(%rsp)
  40134d:	4c 8b 7c 24 10       	mov    0x10(%rsp),%r15
  401352:	48 c1 c0 12          	rol    $0x12,%rax
  401356:	48 c1 cd 17          	ror    $0x17,%rbp
  40135a:	4c 89 44 24 b8       	mov    %r8,-0x48(%rsp)
  40135f:	4c 8b 44 24 98       	mov    -0x68(%rsp),%r8
  401364:	49 d1 c7             	rol    $1,%r15
  401367:	48 89 44 24 30       	mov    %rax,0x30(%rsp)
  40136c:	4c 89 f8             	mov    %r15,%rax
  40136f:	48 89 6c 24 28       	mov    %rbp,0x28(%rsp)
  401374:	48 8b 6c 24 c0       	mov    -0x40(%rsp),%rbp
  401379:	48 31 c8             	xor    %rcx,%rax
  40137c:	49 31 c0             	xor    %rax,%r8
  40137f:	48 31 c5             	xor    %rax,%rbp
  401382:	48 31 c3             	xor    %rax,%rbx
  401385:	49 d1 c0             	rol    $1,%r8
  401388:	48 c1 cd 14          	ror    $0x14,%rbp
  40138c:	4c 89 44 24 38       	mov    %r8,0x38(%rsp)
  401391:	4c 8b 44 24 e0       	mov    -0x20(%rsp),%r8
  401396:	48 c1 cb 13          	ror    $0x13,%rbx
  40139a:	49 31 c0             	xor    %rax,%r8
  40139d:	4c 31 d8             	xor    %r11,%rax
  4013a0:	4d 89 c7             	mov    %r8,%r15
  4013a3:	48 c1 c0 02          	rol    $0x2,%rax
  4013a7:	49 c1 c7 0a          	rol    $0xa,%r15
  4013ab:	48 89 44 24 90       	mov    %rax,-0x70(%rsp)
  4013b0:	4c 89 7c 24 40       	mov    %r15,0x40(%rsp)
  4013b5:	4c 8b 7c 24 18       	mov    0x18(%rsp),%r15
  4013ba:	4d 89 fb             	mov    %r15,%r11
  4013bd:	49 d1 c3             	rol    $1,%r11
  4013c0:	4c 89 d8             	mov    %r11,%rax
  4013c3:	49 89 d3             	mov    %rdx,%r11
  4013c6:	4c 31 e8             	xor    %r13,%rax
  4013c9:	4c 8b 6c 24 a0       	mov    -0x60(%rsp),%r13
  4013ce:	49 d1 c3             	rol    $1,%r11
  4013d1:	49 31 c2             	xor    %rax,%r10
  4013d4:	49 31 c4             	xor    %rax,%r12
  4013d7:	49 c1 c2 0f          	rol    $0xf,%r10
  4013db:	49 31 c5             	xor    %rax,%r13
  4013de:	49 c1 cc 03          	ror    $0x3,%r12
  4013e2:	49 c1 cd 02          	ror    $0x2,%r13
  4013e6:	4c 89 6c 24 18       	mov    %r13,0x18(%rsp)
  4013eb:	4c 8b 44 24 c8       	mov    -0x38(%rsp),%r8
  4013f0:	49 89 f5             	mov    %rsi,%r13
  4013f3:	49 31 c5             	xor    %rax,%r13
  4013f6:	48 8b 54 24 d0       	mov    -0x30(%rsp),%rdx
  4013fb:	48 8b 74 24 a8       	mov    -0x58(%rsp),%rsi
  401400:	4c 89 54 24 f0       	mov    %r10,-0x10(%rsp)
  401405:	49 31 c0             	xor    %rax,%r8
  401408:	48 8b 44 24 10       	mov    0x10(%rsp),%rax
  40140d:	4c 8b 54 24 e8       	mov    -0x18(%rsp),%r10
  401412:	49 c1 cd 15          	ror    $0x15,%r13
  401416:	49 c1 c0 06          	rol    $0x6,%r8
  40141a:	4c 31 d8             	xor    %r11,%rax
  40141d:	4d 89 f3             	mov    %r14,%r11
  401420:	49 89 ee             	mov    %rbp,%r14
  401423:	4c 89 44 24 e0       	mov    %r8,-0x20(%rsp)
  401428:	48 31 c2             	xor    %rax,%rdx
  40142b:	48 31 c6             	xor    %rax,%rsi
  40142e:	49 31 c2             	xor    %rax,%r10
  401431:	49 31 c3             	xor    %rax,%r11
  401434:	48 c1 ca 09          	ror    $0x9,%rdx
  401438:	49 c1 c2 19          	rol    $0x19,%r10
  40143c:	49 f7 d6             	not    %r14
  40143f:	48 89 54 24 10       	mov    %rdx,0x10(%rsp)
  401444:	48 89 ca             	mov    %rcx,%rdx
  401447:	48 c1 c6 1c          	rol    $0x1c,%rsi
  40144b:	48 8b 4c 24 b0       	mov    -0x50(%rsp),%rcx
  401450:	49 c1 c3 15          	rol    $0x15,%r11
  401454:	48 d1 c2             	rol    $1,%rdx
  401457:	4d 21 ee             	and    %r13,%r14
  40145a:	48 33 04 24          	xor    (%rsp),%rax
  40145e:	4c 31 fa             	xor    %r15,%rdx
  401461:	4c 8b 7c 24 d8       	mov    -0x28(%rsp),%r15
  401466:	4c 89 74 24 98       	mov    %r14,-0x68(%rsp)
  40146b:	48 c1 c8 08          	ror    $0x8,%rax
  40146f:	49 31 d1             	xor    %rdx,%r9
  401472:	48 31 d1             	xor    %rdx,%rcx
  401475:	49 c1 c9 19          	ror    $0x19,%r9
  401479:	49 31 d7             	xor    %rdx,%r15
  40147c:	48 c1 c1 1b          	rol    $0x1b,%rcx
  401480:	4d 89 f8             	mov    %r15,%r8
  401483:	4c 8b 7c 24 88       	mov    -0x78(%rsp),%r15
  401488:	4c 89 0c 24          	mov    %r9,(%rsp)
  40148c:	4c 8b 4c 24 f8       	mov    -0x8(%rsp),%r9
  401491:	49 c1 c0 14          	rol    $0x14,%r8
  401495:	4d 8b 37             	mov    (%r15),%r14
  401498:	4c 8b 7c 24 98       	mov    -0x68(%rsp),%r15
  40149d:	49 31 d1             	xor    %rdx,%r9
  4014a0:	48 33 54 24 08       	xor    0x8(%rsp),%rdx
  4014a5:	48 c1 c2 0e          	rol    $0xe,%rdx
  4014a9:	49 31 fe             	xor    %rdi,%r14
  4014ac:	49 c1 c1 08          	rol    $0x8,%r9
  4014b0:	4d 31 f7             	xor    %r14,%r15
  4014b3:	4d 89 ee             	mov    %r13,%r14
  4014b6:	49 f7 d6             	not    %r14
  4014b9:	4d 21 de             	and    %r11,%r14
  4014bc:	49 31 ee             	xor    %rbp,%r14
  4014bf:	4c 89 74 24 98       	mov    %r14,-0x68(%rsp)
  4014c4:	4d 89 de             	mov    %r11,%r14
  4014c7:	49 f7 d6             	not    %r14
  4014ca:	49 21 d6             	and    %rdx,%r14
  4014cd:	4d 31 ee             	xor    %r13,%r14
  4014d0:	49 89 d5             	mov    %rdx,%r13
  4014d3:	49 f7 d5             	not    %r13
  4014d6:	4c 89 74 24 a0       	mov    %r14,-0x60(%rsp)
  4014db:	4c 8b 74 24 b8       	mov    -0x48(%rsp),%r14
  4014e0:	49 21 fd             	and    %rdi,%r13
  4014e3:	48 f7 d7             	not    %rdi
  4014e6:	48 21 ef             	and    %rbp,%rdi
  4014e9:	4d 31 dd             	xor    %r11,%r13
  4014ec:	48 89 fd             	mov    %rdi,%rbp
  4014ef:	4c 89 6c 24 a8       	mov    %r13,-0x58(%rsp)
  4014f4:	48 31 d5             	xor    %rdx,%rbp
  4014f7:	4c 89 c2             	mov    %r8,%rdx
  4014fa:	48 f7 d2             	not    %rdx
  4014fd:	48 89 6c 24 b0       	mov    %rbp,-0x50(%rsp)
  401502:	4c 89 f5             	mov    %r14,%rbp
  401505:	4c 21 f2             	and    %r14,%rdx
  401508:	48 f7 d5             	not    %rbp
  40150b:	48 31 f2             	xor    %rsi,%rdx
  40150e:	48 21 dd             	and    %rbx,%rbp
  401511:	48 89 54 24 b8       	mov    %rdx,-0x48(%rsp)
  401516:	48 89 da             	mov    %rbx,%rdx
  401519:	4c 31 c5             	xor    %r8,%rbp
  40151c:	48 f7 d2             	not    %rdx
  40151f:	48 89 6c 24 c0       	mov    %rbp,-0x40(%rsp)
  401524:	48 8b 6c 24 e0       	mov    -0x20(%rsp),%rbp
  401529:	4c 21 e2             	and    %r12,%rdx
  40152c:	4c 31 f2             	xor    %r14,%rdx
  40152f:	4c 8b 74 24 38       	mov    0x38(%rsp),%r14
  401534:	48 89 54 24 c8       	mov    %rdx,-0x38(%rsp)
  401539:	4c 89 e2             	mov    %r12,%rdx
  40153c:	48 f7 d2             	not    %rdx
  40153f:	48 21 f2             	and    %rsi,%rdx
  401542:	48 f7 d6             	not    %rsi
  401545:	4c 21 c6             	and    %r8,%rsi
  401548:	48 31 da             	xor    %rbx,%rdx
  40154b:	48 8b 5c 24 30       	mov    0x30(%rsp),%rbx
  401550:	49 89 e8             	mov    %rbp,%r8
  401553:	4c 31 e6             	xor    %r12,%rsi
  401556:	48 89 54 24 d0       	mov    %rdx,-0x30(%rsp)
  40155b:	49 f7 d0             	not    %r8
  40155e:	4c 89 d2             	mov    %r10,%rdx
  401561:	48 89 74 24 d8       	mov    %rsi,-0x28(%rsp)
  401566:	4c 89 ce             	mov    %r9,%rsi
  401569:	49 89 db             	mov    %rbx,%r11
  40156c:	4d 21 d0             	and    %r10,%r8
  40156f:	48 f7 d6             	not    %rsi
  401572:	49 f7 d3             	not    %r11
  401575:	48 f7 d2             	not    %rdx
  401578:	4d 31 f0             	xor    %r14,%r8
  40157b:	49 89 f5             	mov    %rsi,%r13
  40157e:	4c 21 ca             	and    %r9,%rdx
  401581:	49 21 dd             	and    %rbx,%r13
  401584:	48 31 ea             	xor    %rbp,%rdx
  401587:	4c 89 ee             	mov    %r13,%rsi
  40158a:	48 89 54 24 e0       	mov    %rdx,-0x20(%rsp)
  40158f:	4c 31 d6             	xor    %r10,%rsi
  401592:	4d 89 da             	mov    %r11,%r10
  401595:	4d 21 f2             	and    %r14,%r10
  401598:	49 f7 d6             	not    %r14
  40159b:	4d 31 ca             	xor    %r9,%r10
  40159e:	4d 89 f1             	mov    %r14,%r9
  4015a1:	4c 89 54 24 e8       	mov    %r10,-0x18(%rsp)
  4015a6:	4c 8b 5c 24 40       	mov    0x40(%rsp),%r11
  4015ab:	49 21 e9             	and    %rbp,%r9
  4015ae:	48 8b 7c 24 f0       	mov    -0x10(%rsp),%rdi
  4015b3:	49 31 d9             	xor    %rbx,%r9
  4015b6:	4c 8b 64 24 20       	mov    0x20(%rsp),%r12
  4015bb:	4c 89 db             	mov    %r11,%rbx
  4015be:	4c 8b 2c 24          	mov    (%rsp),%r13
  4015c2:	48 8b 54 24 18       	mov    0x18(%rsp),%rdx
  4015c7:	48 f7 d3             	not    %rbx
  4015ca:	49 89 fa             	mov    %rdi,%r10
  4015cd:	4c 89 e5             	mov    %r12,%rbp
  4015d0:	48 21 fb             	and    %rdi,%rbx
  4015d3:	49 f7 d2             	not    %r10
  4015d6:	48 f7 d5             	not    %rbp
  4015d9:	4c 31 e3             	xor    %r12,%rbx
  4015dc:	49 21 c2             	and    %rax,%r10
  4015df:	4c 21 dd             	and    %r11,%rbp
  4015e2:	48 89 5c 24 f0       	mov    %rbx,-0x10(%rsp)
  4015e7:	48 89 c3             	mov    %rax,%rbx
  4015ea:	4d 31 da             	xor    %r11,%r10
  4015ed:	48 31 cd             	xor    %rcx,%rbp
  4015f0:	48 f7 d3             	not    %rbx
  4015f3:	49 89 db             	mov    %rbx,%r11
  4015f6:	49 21 cb             	and    %rcx,%r11
  4015f9:	48 f7 d1             	not    %rcx
  4015fc:	4c 21 e1             	and    %r12,%rcx
  4015ff:	4c 31 df             	xor    %r11,%rdi
  401602:	4d 89 eb             	mov    %r13,%r11
  401605:	48 89 cb             	mov    %rcx,%rbx
  401608:	48 8b 4c 24 28       	mov    0x28(%rsp),%rcx
  40160d:	49 89 fe             	mov    %rdi,%r14
  401610:	48 8b 7c 24 10       	mov    0x10(%rsp),%rdi
  401615:	48 31 c3             	xor    %rax,%rbx
  401618:	48 8b 44 24 90       	mov    -0x70(%rsp),%rax
  40161d:	49 f7 d3             	not    %r11
  401620:	49 89 cc             	mov    %rcx,%r12
  401623:	48 89 5c 24 f8       	mov    %rbx,-0x8(%rsp)
  401628:	48 89 fb             	mov    %rdi,%rbx
  40162b:	49 21 cb             	and    %rcx,%r11
  40162e:	49 f7 d4             	not    %r12
  401631:	48 f7 d3             	not    %rbx
  401634:	49 31 fb             	xor    %rdi,%r11
  401637:	49 21 c4             	and    %rax,%r12
  40163a:	48 f7 d0             	not    %rax
  40163d:	4c 21 eb             	and    %r13,%rbx
  401640:	48 21 d0             	and    %rdx,%rax
  401643:	48 31 d3             	xor    %rdx,%rbx
  401646:	4d 31 ec             	xor    %r13,%r12
  401649:	48 f7 d2             	not    %rdx
  40164c:	49 89 c5             	mov    %rax,%r13
  40164f:	49 31 cd             	xor    %rcx,%r13
  401652:	48 21 d7             	and    %rdx,%rdi
  401655:	48 8b 54 24 90       	mov    -0x70(%rsp),%rdx
  40165a:	48 83 44 24 88 08    	addq   $0x8,-0x78(%rsp)
  401660:	4c 89 2c 24          	mov    %r13,(%rsp)
  401664:	48 8b 44 24 88       	mov    -0x78(%rsp),%rax
  401669:	48 31 fa             	xor    %rdi,%rdx
  40166c:	48 89 54 24 08       	mov    %rdx,0x8(%rsp)
  401671:	48 39 44 24 48       	cmp    %rax,0x48(%rsp)
  401676:	0f 85 24 fc ff ff    	jne    0x4012a0
  40167c:	4c 89 f9             	mov    %r15,%rcx
  40167f:	49 89 f7             	mov    %rsi,%r15
  401682:	48 8b 74 24 50       	mov    0x50(%rsp),%rsi
  401687:	66 48 0f 6e cd       	movq   %rbp,%xmm1
  40168c:	66 48 0f 6e c1       	movq   %rcx,%xmm0
  401691:	66 49 0f 6e d2       	movq   %r10,%xmm2
  401696:	66 49 0f 6e db       	movq   %r11,%xmm3
  40169b:	0f 16 44 24 98       	movhps -0x68(%rsp),%xmm0
  4016a0:	48 89 96 c0 00 00 00 	mov    %rdx,0xc0(%rsi)
  4016a7:	0f 11 06             	movups %xmm0,(%rsi)
  4016aa:	f3 0f 7e 44 24 a0    	movq   -0x60(%rsp),%xmm0
  4016b0:	0f 16 44 24 a8       	movhps -0x58(%rsp),%xmm0
  4016b5:	0f 11 46 10          	movups %xmm0,0x10(%rsi)
  4016b9:	f3 0f 7e 44 24 b0    	movq   -0x50(%rsp),%xmm0
  4016bf:	0f 16 44 24 b8       	movhps -0x48(%rsp),%xmm0
  4016c4:	0f 11 46 20          	movups %xmm0,0x20(%rsi)
  4016c8:	f3 0f 7e 44 24 c0    	movq   -0x40(%rsp),%xmm0
  4016ce:	0f 16 44 24 c8       	movhps -0x38(%rsp),%xmm0
  4016d3:	0f 11 46 30          	movups %xmm0,0x30(%rsi)
  4016d7:	f3 0f 7e 44 24 d0    	movq   -0x30(%rsp),%xmm0
  4016dd:	0f 16 44 24 d8       	movhps -0x28(%rsp),%xmm0
  4016e2:	0f 11 46 40          	movups %xmm0,0x40(%rsi)
  4016e6:	66 49 0f 6e c0       	movq   %r8,%xmm0
  4016eb:	0f 16 44 24 e0       	movhps -0x20(%rsp),%xmm0
  4016f0:	0f 11 46 50          	movups %xmm0,0x50(%rsi)
  4016f4:	66 49 0f 6e c7       	movq   %r15,%xmm0
  4016f9:	0f 16 44 24 e8       	movhps -0x18(%rsp),%xmm0
  4016fe:	0f 11 46 60          	movups %xmm0,0x60(%rsi)
  401702:	66 49 0f 6e c1       	movq   %r9,%xmm0
  401707:	66 0f 6c c1          	punpcklqdq %xmm1,%xmm0
  40170b:	0f 11 46 70          	movups %xmm0,0x70(%rsi)
  40170f:	f3 0f 7e 44 24 f0    	movq   -0x10(%rsp),%xmm0
  401715:	66 0f 6c c2          	punpcklqdq %xmm2,%xmm0
  401719:	0f 11 86 80 00 00 00 	movups %xmm0,0x80(%rsi)
  401720:	66 49 0f 6e c6       	movq   %r14,%xmm0
  401725:	0f 16 44 24 f8       	movhps -0x8(%rsp),%xmm0
  40172a:	0f 11 86 90 00 00 00 	movups %xmm0,0x90(%rsi)
  401731:	66 48 0f 6e c3       	movq   %rbx,%xmm0
  401736:	66 0f 6c c3          	punpcklqdq %xmm3,%xmm0
  40173a:	0f 11 86 a0 00 00 00 	movups %xmm0,0xa0(%rsi)
  401741:	66 49 0f 6e c4       	movq   %r12,%xmm0
  401746:	0f 16 04 24          	movhps (%rsp),%xmm0
  40174a:	0f 11 86 b0 00 00 00 	movups %xmm0,0xb0(%rsi)
  401751:	48 83 c4 60          	add    $0x60,%rsp
  401755:	5b                   	pop    %rbx
  401756:	5d                   	pop    %rbp
  401757:	41 5c                	pop    %r12
  401759:	41 5d                	pop    %r13
  40175b:	41 5e                	pop    %r14
  40175d:	41 5f                	pop    %r15
  40175f:	c3                   	ret
  401760:	48 89 fa             	mov    %rdi,%rdx
  401763:	b8 01 00 00 00       	mov    $0x1,%eax
  401768:	48 85 ff             	test   %rdi,%rdi
  40176b:	74 73                	je     0x4017e0
  40176d:	48 c7 07 00 00 00 00 	movq   $0x0,(%rdi)
  401774:	48 8d b7 d0 00 00 00 	lea    0xd0(%rdi),%rsi
  40177b:	48 8d 7f 08          	lea    0x8(%rdi),%rdi
  40177f:	31 c0                	xor    %eax,%eax
  401781:	48 c7 87 b8 00 00 00 	movq   $0x0,0xb8(%rdi)
  401788:	00 00 00 00 
  40178c:	48 89 d1             	mov    %rdx,%rcx
  40178f:	48 83 e7 f8          	and    $0xfffffffffffffff8,%rdi
  401793:	48 83 e6 f8          	and    $0xfffffffffffffff8,%rsi
  401797:	48 29 f9             	sub    %rdi,%rcx
  40179a:	81 c1 c8 00 00 00    	add    $0xc8,%ecx
  4017a0:	c1 e9 03             	shr    $0x3,%ecx
  4017a3:	f3 48 ab             	rep stos %rax,(%rdi)
  4017a6:	89 d1                	mov    %edx,%ecx
  4017a8:	48 89 f7             	mov    %rsi,%rdi
  4017ab:	48 c7 82 c8 00 00 00 	movq   $0x0,0xc8(%rdx)
  4017b2:	00 00 00 00 
  4017b6:	48 c7 82 88 01 00 00 	movq   $0x0,0x188(%rdx)
  4017bd:	00 00 00 00 
  4017c1:	29 f1                	sub    %esi,%ecx
  4017c3:	81 c1 90 01 00 00    	add    $0x190,%ecx
  4017c9:	c1 e9 03             	shr    $0x3,%ecx
  4017cc:	f3 48 ab             	rep stos %rax,(%rdi)
  4017cf:	c6 82 9c 01 00 00 00 	movb   $0x0,0x19c(%rdx)
  4017d6:	c7 82 90 01 00 00 00 	movl   $0x0,0x190(%rdx)
  4017dd:	00 00 00 
  4017e0:	c3                   	ret
  4017e1:	66 66 2e 0f 1f 84 00 	data16 cs nopw 0x0(%rax,%rax,1)
  4017e8:	00 00 00 00 
  4017ec:	0f 1f 40 00          	nopl   0x0(%rax)
  4017f0:	41 b8 01 00 00 00    	mov    $0x1,%r8d
  4017f6:	48 85 ff             	test   %rdi,%rdi
  4017f9:	74 75                	je     0x401870
  4017fb:	41 54                	push   %r12
  4017fd:	41 89 d4             	mov    %edx,%r12d
  401800:	55                   	push   %rbp
  401801:	48 89 f5             	mov    %rsi,%rbp
  401804:	be a0 01 00 00       	mov    $0x1a0,%esi
  401809:	53                   	push   %rbx
  40180a:	48 89 fb             	mov    %rdi,%rbx
  40180d:	bf 01 00 00 00       	mov    $0x1,%edi
  401812:	e8 49 f8 ff ff       	call   0x401060
  401817:	48 89 03             	mov    %rax,(%rbx)
  40181a:	48 85 c0             	test   %rax,%rax
  40181d:	74 55                	je     0x401874
  40181f:	41 b8 09 00 00 00    	mov    $0x9,%r8d
  401825:	48 81 fd c7 00 00 00 	cmp    $0xc7,%rbp
  40182c:	77 36                	ja     0x401864
  40182e:	41 80 fc 0c          	cmp    $0xc,%r12b
  401832:	74 0c                	je     0x401840
  401834:	41 b8 08 00 00 00    	mov    $0x8,%r8d
  40183a:	41 80 fc 18          	cmp    $0x18,%r12b
  40183e:	75 24                	jne    0x401864
  401840:	ba c8 00 00 00       	mov    $0xc8,%edx
  401845:	89 a8 94 01 00 00    	mov    %ebp,0x194(%rax)
  40184b:	45 31 c0             	xor    %r8d,%r8d
  40184e:	29 ea                	sub    %ebp,%edx
  401850:	c6 80 9c 01 00 00 00 	movb   $0x0,0x19c(%rax)
  401857:	89 90 98 01 00 00    	mov    %edx,0x198(%rax)
  40185d:	44 88 a0 9d 01 00 00 	mov    %r12b,0x19d(%rax)
  401864:	5b                   	pop    %rbx
  401865:	44 89 c0             	mov    %r8d,%eax
  401868:	5d                   	pop    %rbp
  401869:	41 5c                	pop    %r12
  40186b:	c3                   	ret
  40186c:	0f 1f 40 00          	nopl   0x0(%rax)
  401870:	44 89 c0             	mov    %r8d,%eax
  401873:	c3                   	ret
  401874:	41 b8 02 00 00 00    	mov    $0x2,%r8d
  40187a:	eb e8                	jmp    0x401864
  40187c:	0f 1f 40 00          	nopl   0x0(%rax)
  401880:	48 83 ec 08          	sub    $0x8,%rsp
  401884:	e8 a7 f7 ff ff       	call   0x401030
  401889:	31 c0                	xor    %eax,%eax
  40188b:	48 83 c4 08          	add    $0x8,%rsp
  40188f:	c3                   	ret
  401890:	48 85 ff             	test   %rdi,%rdi
  401893:	0f 84 9f 02 00 00    	je     0x401b38
  401899:	41 57                	push   %r15
  40189b:	49 89 f7             	mov    %rsi,%r15
  40189e:	41 56                	push   %r14
  4018a0:	41 55                	push   %r13
  4018a2:	41 54                	push   %r12
  4018a4:	55                   	push   %rbp
  4018a5:	53                   	push   %rbx
  4018a6:	48 83 ec 08          	sub    $0x8,%rsp
  4018aa:	48 85 f6             	test   %rsi,%rsi
  4018ad:	0f 84 65 02 00 00    	je     0x401b18
  4018b3:	80 bf 9c 01 00 00 00 	cmpb   $0x0,0x19c(%rdi)
  4018ba:	48 89 fb             	mov    %rdi,%rbx
  4018bd:	b8 20 00 00 00       	mov    $0x20,%eax
  4018c2:	0f 85 3a 02 00 00    	jne    0x401b02
  4018c8:	49 89 d4             	mov    %rdx,%r12
  4018cb:	48 85 d2             	test   %rdx,%rdx
  4018ce:	0f 84 2c 02 00 00    	je     0x401b00
  4018d4:	48 8d af c8 00 00 00 	lea    0xc8(%rdi),%rbp
  4018db:	8b bf 90 01 00 00    	mov    0x190(%rdi),%edi
  4018e1:	eb 0e                	jmp    0x4018f1
  4018e3:	0f 1f 44 00 00       	nopl   0x0(%rax,%rax,1)
  4018e8:	4d 85 e4             	test   %r12,%r12
  4018eb:	0f 84 0f 02 00 00    	je     0x401b00
  4018f1:	44 8b b3 98 01 00 00 	mov    0x198(%rbx),%r14d
  4018f8:	41 29 fe             	sub    %edi,%r14d
  4018fb:	45 89 f5             	mov    %r14d,%r13d
  4018fe:	4d 39 e5             	cmp    %r12,%r13
  401901:	76 06                	jbe    0x401909
  401903:	45 89 e6             	mov    %r12d,%r14d
  401906:	4d 89 e5             	mov    %r12,%r13
  401909:	48 01 ef             	add    %rbp,%rdi
  40190c:	4c 89 fe             	mov    %r15,%rsi
  40190f:	4c 89 ea             	mov    %r13,%rdx
  401912:	4d 01 ef             	add    %r13,%r15
  401915:	e8 66 f7 ff ff       	call   0x401080
  40191a:	44 89 f7             	mov    %r14d,%edi
  40191d:	03 bb 90 01 00 00    	add    0x190(%rbx),%edi
  401923:	4d 29 ec             	sub    %r13,%r12
  401926:	89 bb 90 01 00 00    	mov    %edi,0x190(%rbx)
  40192c:	3b bb 98 01 00 00    	cmp    0x198(%rbx),%edi
  401932:	75 b4                	jne    0x4018e8
  401934:	85 ff                	test   %edi,%edi
  401936:	0f 84 9d 01 00 00    	je     0x401ad9
  40193c:	83 ef 01             	sub    $0x1,%edi
  40193f:	89 f9                	mov    %edi,%ecx
  401941:	c1 e9 03             	shr    $0x3,%ecx
  401944:	83 c1 01             	add    $0x1,%ecx
  401947:	83 ff 07             	cmp    $0x7,%edi
  40194a:	0f 86 dc 01 00 00    	jbe    0x401b2c
  401950:	f3 0f 6f 0b          	movdqu (%rbx),%xmm1
  401954:	f3 0f 6f 83 c8 00 00 	movdqu 0xc8(%rbx),%xmm0
  40195b:	00 
  40195c:	89 c8                	mov    %ecx,%eax
  40195e:	d1 e8                	shr    $1,%eax
  401960:	66 0f ef c1          	pxor   %xmm1,%xmm0
  401964:	0f 11 03             	movups %xmm0,(%rbx)
  401967:	83 f8 01             	cmp    $0x1,%eax
  40196a:	0f 84 50 01 00 00    	je     0x401ac0
  401970:	f3 0f 6f 53 10       	movdqu 0x10(%rbx),%xmm2
  401975:	f3 0f 6f 83 d8 00 00 	movdqu 0xd8(%rbx),%xmm0
  40197c:	00 
  40197d:	66 0f ef c2          	pxor   %xmm2,%xmm0
  401981:	0f 11 43 10          	movups %xmm0,0x10(%rbx)
  401985:	83 f8 02             	cmp    $0x2,%eax
  401988:	0f 84 32 01 00 00    	je     0x401ac0
  40198e:	f3 0f 6f 5b 20       	movdqu 0x20(%rbx),%xmm3
  401993:	f3 0f 6f 83 e8 00 00 	movdqu 0xe8(%rbx),%xmm0
  40199a:	00 
  40199b:	66 0f ef c3          	pxor   %xmm3,%xmm0
  40199f:	0f 11 43 20          	movups %xmm0,0x20(%rbx)
  4019a3:	83 f8 03             	cmp    $0x3,%eax
  4019a6:	0f 84 14 01 00 00    	je     0x401ac0
  4019ac:	f3 0f 6f 63 30       	movdqu 0x30(%rbx),%xmm4
  4019b1:	f3 0f 6f 83 f8 00 00 	movdqu 0xf8(%rbx),%xmm0
  4019b8:	00 
  4019b9:	66 0f ef c4          	pxor   %xmm4,%xmm0
  4019bd:	0f 11 43 30          	movups %xmm0,0x30(%rbx)
  4019c1:	83 f8 04             	cmp    $0x4,%eax
  4019c4:	0f 84 f6 00 00 00    	je     0x401ac0
  4019ca:	f3 0f 6f 6b 40       	movdqu 0x40(%rbx),%xmm5
  4019cf:	f3 0f 6f 83 08 01 00 	movdqu 0x108(%rbx),%xmm0
  4019d6:	00 
  4019d7:	66 0f ef c5          	pxor   %xmm5,%xmm0
  4019db:	0f 11 43 40          	movups %xmm0,0x40(%rbx)
  4019df:	83 f8 05             	cmp    $0x5,%eax
  4019e2:	0f 84 d8 00 00 00    	je     0x401ac0
  4019e8:	f3 0f 6f 73 50       	movdqu 0x50(%rbx),%xmm6
  4019ed:	f3 0f 6f 83 18 01 00 	movdqu 0x118(%rbx),%xmm0
  4019f4:	00 
  4019f5:	66 0f ef c6          	pxor   %xmm6,%xmm0
  4019f9:	0f 11 43 50          	movups %xmm0,0x50(%rbx)
  4019fd:	83 f8 06             	cmp    $0x6,%eax
  401a00:	0f 84 ba 00 00 00    	je     0x401ac0
  401a06:	f3 0f 6f 7b 60       	movdqu 0x60(%rbx),%xmm7
  401a0b:	f3 0f 6f 83 28 01 00 	movdqu 0x128(%rbx),%xmm0
  401a12:	00 
  401a13:	66 0f ef c7          	pxor   %xmm7,%xmm0
  401a17:	0f 11 43 60          	movups %xmm0,0x60(%rbx)
  401a1b:	83 f8 07             	cmp    $0x7,%eax
  401a1e:	0f 84 9c 00 00 00    	je     0x401ac0
  401a24:	f3 0f 6f 7b 70       	movdqu 0x70(%rbx),%xmm7
  401a29:	f3 0f 6f 83 38 01 00 	movdqu 0x138(%rbx),%xmm0
  401a30:	00 
  401a31:	66 0f ef c7          	pxor   %xmm7,%xmm0
  401a35:	0f 11 43 70          	movups %xmm0,0x70(%rbx)
  401a39:	83 f8 08             	cmp    $0x8,%eax
  401a3c:	0f 84 7e 00 00 00    	je     0x401ac0
  401a42:	f3 0f 6f b3 80 00 00 	movdqu 0x80(%rbx),%xmm6
  401a49:	00 
  401a4a:	f3 0f 6f 83 48 01 00 	movdqu 0x148(%rbx),%xmm0
  401a51:	00 
  401a52:	66 0f ef c6          	pxor   %xmm6,%xmm0
  401a56:	0f 11 83 80 00 00 00 	movups %xmm0,0x80(%rbx)
  401a5d:	83 f8 09             	cmp    $0x9,%eax
  401a60:	74 5e                	je     0x401ac0
  401a62:	f3 0f 6f ab 90 00 00 	movdqu 0x90(%rbx),%xmm5
  401a69:	00 
  401a6a:	f3 0f 6f 83 58 01 00 	movdqu 0x158(%rbx),%xmm0
  401a71:	00 
  401a72:	66 0f ef c5          	pxor   %xmm5,%xmm0
  401a76:	0f 11 83 90 00 00 00 	movups %xmm0,0x90(%rbx)
  401a7d:	83 f8 0a             	cmp    $0xa,%eax
  401a80:	74 3e                	je     0x401ac0
  401a82:	f3 0f 6f a3 a0 00 00 	movdqu 0xa0(%rbx),%xmm4
  401a89:	00 
  401a8a:	f3 0f 6f 83 68 01 00 	movdqu 0x168(%rbx),%xmm0
  401a91:	00 
  401a92:	66 0f ef c4          	pxor   %xmm4,%xmm0
  401a96:	0f 11 83 a0 00 00 00 	movups %xmm0,0xa0(%rbx)
  401a9d:	83 f8 0b             	cmp    $0xb,%eax
  401aa0:	74 1e                	je     0x401ac0
  401aa2:	f3 0f 6f bb b0 00 00 	movdqu 0xb0(%rbx),%xmm7
  401aa9:	00 
  401aaa:	f3 0f 6f 83 78 01 00 	movdqu 0x178(%rbx),%xmm0
  401ab1:	00 
  401ab2:	66 0f ef c7          	pxor   %xmm7,%xmm0
  401ab6:	0f 11 83 b0 00 00 00 	movups %xmm0,0xb0(%rbx)
  401abd:	0f 1f 00             	nopl   (%rax)
  401ac0:	89 c8                	mov    %ecx,%eax
  401ac2:	83 e0 fe             	and    $0xfffffffe,%eax
  401ac5:	8d 14 c5 00 00 00 00 	lea    0x0(,%rax,8),%edx
  401acc:	39 c8                	cmp    %ecx,%eax
  401ace:	74 09                	je     0x401ad9
  401ad0:	48 8b 54 15 00       	mov    0x0(%rbp,%rdx,1),%rdx
  401ad5:	48 31 14 c3          	xor    %rdx,(%rbx,%rax,8)
  401ad9:	0f b6 b3 9d 01 00 00 	movzbl 0x19d(%rbx),%esi
  401ae0:	48 89 df             	mov    %rbx,%rdi
  401ae3:	e8 88 f6 ff ff       	call   0x401170
  401ae8:	31 ff                	xor    %edi,%edi
  401aea:	c7 83 90 01 00 00 00 	movl   $0x0,0x190(%rbx)
  401af1:	00 00 00 
  401af4:	4d 85 e4             	test   %r12,%r12
  401af7:	0f 85 f4 fd ff ff    	jne    0x4018f1
  401afd:	0f 1f 00             	nopl   (%rax)
  401b00:	31 c0                	xor    %eax,%eax
  401b02:	48 83 c4 08          	add    $0x8,%rsp
  401b06:	5b                   	pop    %rbx
  401b07:	5d                   	pop    %rbp
  401b08:	41 5c                	pop    %r12
  401b0a:	41 5d                	pop    %r13
  401b0c:	41 5e                	pop    %r14
  401b0e:	41 5f                	pop    %r15
  401b10:	c3                   	ret
  401b11:	0f 1f 80 00 00 00 00 	nopl   0x0(%rax)
  401b18:	48 83 c4 08          	add    $0x8,%rsp
  401b1c:	b8 01 00 00 00       	mov    $0x1,%eax
  401b21:	5b                   	pop    %rbx
  401b22:	5d                   	pop    %rbp
  401b23:	41 5c                	pop    %r12
  401b25:	41 5d                	pop    %r13
  401b27:	41 5e                	pop    %r14
  401b29:	41 5f                	pop    %r15
  401b2b:	c3                   	ret
  401b2c:	31 c0                	xor    %eax,%eax
  401b2e:	31 d2                	xor    %edx,%edx
  401b30:	eb 9e                	jmp    0x401ad0
  401b32:	66 0f 1f 44 00 00    	nopw   0x0(%rax,%rax,1)
  401b38:	b8 01 00 00 00       	mov    $0x1,%eax
  401b3d:	c3                   	ret
  401b3e:	66 90                	xchg   %ax,%ax
  401b40:	48 85 ff             	test   %rdi,%rdi
  401b43:	0f 84 6f 03 00 00    	je     0x401eb8
  401b49:	41 57                	push   %r15
  401b4b:	41 56                	push   %r14
  401b4d:	49 89 f6             	mov    %rsi,%r14
  401b50:	41 55                	push   %r13
  401b52:	41 54                	push   %r12
  401b54:	55                   	push   %rbp
  401b55:	53                   	push   %rbx
  401b56:	48 83 ec 08          	sub    $0x8,%rsp
  401b5a:	48 85 f6             	test   %rsi,%rsi
  401b5d:	0f 84 3d 03 00 00    	je     0x401ea0
  401b63:	0f b6 87 9c 01 00 00 	movzbl 0x19c(%rdi),%eax
  401b6a:	48 89 fb             	mov    %rdi,%rbx
  401b6d:	49 89 d4             	mov    %rdx,%r12
  401b70:	84 c0                	test   %al,%al
  401b72:	0f 84 e0 00 00 00    	je     0x401c58
  401b78:	3c 01                	cmp    $0x1,%al
  401b7a:	0f 85 98 03 00 00    	jne    0x401f18
  401b80:	8b 83 90 01 00 00    	mov    0x190(%rbx),%eax
  401b86:	85 c0                	test   %eax,%eax
  401b88:	0f 84 3a 03 00 00    	je     0x401ec8
  401b8e:	8b b3 98 01 00 00    	mov    0x198(%rbx),%esi
  401b94:	39 f0                	cmp    %esi,%eax
  401b96:	0f 87 9b 03 00 00    	ja     0x401f37
  401b9c:	48 8d ab c8 00 00 00 	lea    0xc8(%rbx),%rbp
  401ba3:	4d 85 e4             	test   %r12,%r12
  401ba6:	75 17                	jne    0x401bbf
  401ba8:	e9 94 00 00 00       	jmp    0x401c41
  401bad:	0f 1f 00             	nopl   (%rax)
  401bb0:	4d 85 e4             	test   %r12,%r12
  401bb3:	0f 84 88 00 00 00    	je     0x401c41
  401bb9:	8b b3 98 01 00 00    	mov    0x198(%rbx),%esi
  401bbf:	41 00 ee             	add    %bpl,%r14b
  401bc2:	2f                   	(bad)
  401bc3:	10 00                	adc    %al,(%rax)
  401bc5:	00 00                	add    %al,(%rax)
  401bc7:	00 08                	add    %cl,(%rax)
  401bc9:	00 00                	add    %al,(%rax)
  401bcb:	00 00                	add    %al,(%rax)
  401bcd:	00 00                	add    %al,(%rax)
  401bcf:	00 10                	add    %dl,(%rax)
  401bd1:	3a e0                	cmp    %al,%ah
  401bd3:	02 00                	add    (%rax),%al
  401bd5:	00 00                	add    %al,(%rax)
  401bd7:	00 08                	add    %cl,(%rax)
  401bd9:	ee                   	out    %al,(%dx)
  401bda:	2f                   	(bad)
  401bdb:	10 00                	adc    %al,(%rax)
  401bdd:	00 00                	add    %al,(%rax)
  401bdf:	00 08                	add    %cl,(%rax)
  401be1:	00 00                	add    %al,(%rax)
  401be3:	00 00                	add    %al,(%rax)
  401be5:	00 00                	add    %al,(%rax)
  401be7:	00 48 b1             	add    %cl,-0x4f(%rax)
  401bea:	da 03                	fiaddl (%rbx)
  401bec:	00 00                	add    %al,(%rax)
  401bee:	00 00                	add    %al,(%rax)
  401bf0:	10 ee                	adc    %ch,%dh
  401bf2:	2f                   	(bad)
  401bf3:	10 00                	adc    %al,(%rax)
  401bf5:	00 00                	add    %al,(%rax)
  401bf7:	00 08                	add    %cl,(%rax)
  401bf9:	00 00                	add    %al,(%rax)
  401bfb:	00 00                	add    %al,(%rax)
  401bfd:	00 00                	add    %al,(%rax)
  401bff:	00 60 a4             	add    %ah,-0x5c(%rax)
  401c02:	b4 0f                	mov    $0xf,%ah
  401c04:	00 00                	add    %al,(%rax)
  401c06:	00 00                	add    %al,(%rax)
  401c08:	18 ee                	sbb    %ch,%dh
  401c0a:	2f                   	(bad)
  401c0b:	10 00                	adc    %al,(%rax)
  401c0d:	00 00                	add    %al,(%rax)
  401c0f:	00 08                	add    %cl,(%rax)
  401c11:	00 00                	add    %al,(%rax)
  401c13:	00 00                	add    %al,(%rax)
  401c15:	00 00                	add    %al,(%rax)
  401c17:	00 80 a4 b4 0f 00    	add    %al,0xfb4a4(%rax)
  401c1d:	00 00                	add    %al,(%rax)
  401c1f:	00 38                	add    %bh,(%rax)
  401c21:	ee                   	out    %al,(%dx)
  401c22:	2f                   	(bad)
  401c23:	10 00                	adc    %al,(%rax)
  401c25:	00 00                	add    %al,(%rax)
  401c27:	00 08                	add    %cl,(%rax)
  401c29:	00 00                	add    %al,(%rax)
  401c2b:	00 00                	add    %al,(%rax)
  401c2d:	00 00                	add    %al,(%rax)
  401c2f:	00 f0                	add    %dh,%al
  401c31:	00 1d 03 00 00 00    	add    %bl,0x3(%rip)        # 0x401c3a
  401c37:	00 40 ee             	add    %al,-0x12(%rax)
  401c3a:	2f                   	(bad)
  401c3b:	10 00                	adc    %al,(%rax)
  401c3d:	00 00                	add    %al,(%rax)
  401c3f:	00 08                	add    %cl,(%rax)
  401c41:	00 00                	add    %al,(%rax)
  401c43:	00 00                	add    %al,(%rax)
  401c45:	00 00                	add    %al,(%rax)
  401c47:	00 10                	add    %dl,(%rax)
  401c49:	3a e0                	cmp    %al,%ah
  401c4b:	02 00                	add    (%rax),%al
  401c4d:	00 00                	add    %al,(%rax)
  401c4f:	00 48 ee             	add    %cl,-0x12(%rax)
  401c52:	2f                   	(bad)
  401c53:	10 00                	adc    %al,(%rax)
  401c55:	00 00                	add    %al,(%rax)
  401c57:	00 08                	add    %cl,(%rax)
  401c59:	00 00                	add    %al,(%rax)
  401c5b:	00 00                	add    %al,(%rax)
  401c5d:	00 00                	add    %al,(%rax)
  401c5f:	00 48 b1             	add    %cl,-0x4f(%rax)
  401c62:	da 03                	fiaddl (%rbx)
  401c64:	00 00                	add    %al,(%rax)
  401c66:	00 00                	add    %al,(%rax)
  401c68:	50                   	push   %rax
  401c69:	ee                   	out    %al,(%dx)
  401c6a:	2f                   	(bad)
  401c6b:	10 00                	adc    %al,(%rax)
  401c6d:	00 00                	add    %al,(%rax)
  401c6f:	00 08                	add    %cl,(%rax)
  401c71:	00 00                	add    %al,(%rax)
  401c73:	00 00                	add    %al,(%rax)
  401c75:	00 00                	add    %al,(%rax)
  401c77:	00 c0                	add    %al,%al
  401c79:	27                   	(bad)
  401c7a:	b5 0f                	mov    $0xf,%ch
  401c7c:	00 00                	add    %al,(%rax)
  401c7e:	00 00                	add    %al,(%rax)
  401c80:	58                   	pop    %rax
  401c81:	ee                   	out    %al,(%dx)
  401c82:	2f                   	(bad)
  401c83:	10 00                	adc    %al,(%rax)
  401c85:	00 00                	add    %al,(%rax)
  401c87:	00 08                	add    %cl,(%rax)
  401c89:	00 00                	add    %al,(%rax)
  401c8b:	00 00                	add    %al,(%rax)
  401c8d:	00 00                	add    %al,(%rax)
  401c8f:	00 e0                	add    %ah,%al
  401c91:	27                   	(bad)
  401c92:	b5 0f                	mov    $0xf,%ch
  401c94:	00 00                	add    %al,(%rax)
  401c96:	00 00                	add    %al,(%rax)
  401c98:	78 ee                	js     0x401c88
  401c9a:	2f                   	(bad)
  401c9b:	10 00                	adc    %al,(%rax)
  401c9d:	00 00                	add    %al,(%rax)
  401c9f:	00 08                	add    %cl,(%rax)
  401ca1:	00 00                	add    %al,(%rax)
  401ca3:	00 00                	add    %al,(%rax)
  401ca5:	00 00                	add    %al,(%rax)
  401ca7:	00 f0                	add    %dh,%al
  401ca9:	00 1d 03 00 00 00    	add    %bl,0x3(%rip)        # 0x401cb2
  401caf:	00 80 ee 2f 10 00    	add    %al,0x102fee(%rax)
  401cb5:	00 00                	add    %al,(%rax)
  401cb7:	00 08                	add    %cl,(%rax)
  401cb9:	00 00                	add    %al,(%rax)
  401cbb:	00 00                	add    %al,(%rax)
  401cbd:	00 00                	add    %al,(%rax)
  401cbf:	00 10                	add    %dl,(%rax)
  401cc1:	3a e0                	cmp    %al,%ah
  401cc3:	02 00                	add    (%rax),%al
  401cc5:	00 00                	add    %al,(%rax)
  401cc7:	00 88 ee 2f 10 00    	add    %cl,0x102fee(%rax)
  401ccd:	00 00                	add    %al,(%rax)
  401ccf:	00 08                	add    %cl,(%rax)
  401cd1:	00 00                	add    %al,(%rax)
  401cd3:	00 00                	add    %al,(%rax)
  401cd5:	00 00                	add    %al,(%rax)
  401cd7:	00 48 b1             	add    %cl,-0x4f(%rax)
  401cda:	da 03                	fiaddl (%rbx)
  401cdc:	00 00                	add    %al,(%rax)
  401cde:	00 00                	add    %al,(%rax)
  401ce0:	90                   	nop
  401ce1:	ee                   	out    %al,(%dx)
  401ce2:	2f                   	(bad)
  401ce3:	10 00                	adc    %al,(%rax)
  401ce5:	00 00                	add    %al,(%rax)
  401ce7:	00 08                	add    %cl,(%rax)
  401ce9:	00 00                	add    %al,(%rax)
  401ceb:	00 00                	add    %al,(%rax)
  401ced:	00 00                	add    %al,(%rax)
  401cef:	00 70 43             	add    %dh,0x43(%rax)
  401cf2:	b5 0f                	mov    $0xf,%ch
  401cf4:	00 00                	add    %al,(%rax)
  401cf6:	00 00                	add    %al,(%rax)
  401cf8:	98                   	cwtl
  401cf9:	ee                   	out    %al,(%dx)
  401cfa:	2f                   	(bad)
  401cfb:	10 00                	adc    %al,(%rax)
  401cfd:	00 00                	add    %al,(%rax)
  401cff:	00 08                	add    %cl,(%rax)
  401d01:	00 00                	add    %al,(%rax)
  401d03:	00 00                	add    %al,(%rax)
  401d05:	00 00                	add    %al,(%rax)
  401d07:	00 30                	add    %dh,(%rax)
  401d09:	50                   	push   %rax
  401d0a:	12 07                	adc    (%rdi),%al
  401d0c:	00 00                	add    %al,(%rax)
  401d0e:	00 00                	add    %al,(%rax)
  401d10:	b8 ee 2f 10 00       	mov    $0x102fee,%eax
  401d15:	00 00                	add    %al,(%rax)
  401d17:	00 08                	add    %cl,(%rax)
  401d19:	00 00                	add    %al,(%rax)
  401d1b:	00 00                	add    %al,(%rax)
  401d1d:	00 00                	add    %al,(%rax)
  401d1f:	00 f0                	add    %dh,%al
  401d21:	00 1d 03 00 00 00    	add    %bl,0x3(%rip)        # 0x401d2a
  401d27:	00 c0                	add    %al,%al
  401d29:	ee                   	out    %al,(%dx)
  401d2a:	2f                   	(bad)
  401d2b:	10 00                	adc    %al,(%rax)
  401d2d:	00 00                	add    %al,(%rax)
  401d2f:	00 08                	add    %cl,(%rax)
  401d31:	00 00                	add    %al,(%rax)
  401d33:	00 00                	add    %al,(%rax)
  401d35:	00 00                	add    %al,(%rax)
  401d37:	00 10                	add    %dl,(%rax)
  401d39:	3a e0                	cmp    %al,%ah
  401d3b:	02 00                	add    (%rax),%al
  401d3d:	00 00                	add    %al,(%rax)
  401d3f:	00 c8                	add    %cl,%al
  401d41:	ee                   	out    %al,(%dx)
  401d42:	2f                   	(bad)
  401d43:	10 00                	adc    %al,(%rax)
  401d45:	00 00                	add    %al,(%rax)
  401d47:	00 08                	add    %cl,(%rax)
  401d49:	00 00                	add    %al,(%rax)
  401d4b:	00 00                	add    %al,(%rax)
  401d4d:	00 00                	add    %al,(%rax)
  401d4f:	00 48 b1             	add    %cl,-0x4f(%rax)
  401d52:	da 03                	fiaddl (%rbx)
  401d54:	00 00                	add    %al,(%rax)
  401d56:	00 00                	add    %al,(%rax)
  401d58:	d0 ee                	shr    $1,%dh
  401d5a:	2f                   	(bad)
  401d5b:	10 00                	adc    %al,(%rax)
  401d5d:	00 00                	add    %al,(%rax)
  401d5f:	00 08                	add    %cl,(%rax)
  401d61:	00 00                	add    %al,(%rax)
  401d63:	00 00                	add    %al,(%rax)
  401d65:	00 00                	add    %al,(%rax)
  401d67:	00 e0                	add    %ah,%al
  401d69:	c0 ac 07 00 00 00 00 	shrb   $0xd8,0x0(%rdi,%rax,1)
  401d70:	d8 
  401d71:	ee                   	out    %al,(%dx)
  401d72:	2f                   	(bad)
  401d73:	10 00                	adc    %al,(%rax)
  401d75:	00 00                	add    %al,(%rax)
  401d77:	00 08                	add    %cl,(%rax)
  401d79:	00 00                	add    %al,(%rax)
  401d7b:	00 00                	add    %al,(%rax)
  401d7d:	00 00                	add    %al,(%rax)
  401d7f:	00 80 55 b5 0f 00    	add    %al,0xfb555(%rax)
  401d85:	00 00                	add    %al,(%rax)
  401d87:	00 f8                	add    %bh,%al
  401d89:	ee                   	out    %al,(%dx)
  401d8a:	2f                   	(bad)
  401d8b:	10 00                	adc    %al,(%rax)
  401d8d:	00 00                	add    %al,(%rax)
  401d8f:	00 08                	add    %cl,(%rax)
  401d91:	00 00                	add    %al,(%rax)
  401d93:	00 00                	add    %al,(%rax)
  401d95:	00 00                	add    %al,(%rax)
  401d97:	00 f0                	add    %dh,%al
  401d99:	00 1d 03 00 00 00    	add    %bl,0x3(%rip)        # 0x401da2
  401d9f:	00 00                	add    %al,(%rax)
  401da1:	ef                   	out    %eax,(%dx)
  401da2:	2f                   	(bad)
  401da3:	10 00                	adc    %al,(%rax)
  401da5:	00 00                	add    %al,(%rax)
  401da7:	00 08                	add    %cl,(%rax)
  401da9:	00 00                	add    %al,(%rax)
  401dab:	00 00                	add    %al,(%rax)
  401dad:	00 00                	add    %al,(%rax)
  401daf:	00 10                	add    %dl,(%rax)
  401db1:	3a e0                	cmp    %al,%ah
  401db3:	02 00                	add    (%rax),%al
  401db5:	00 00                	add    %al,(%rax)
  401db7:	00 08                	add    %cl,(%rax)
  401db9:	ef                   	out    %eax,(%dx)
  401dba:	2f                   	(bad)
  401dbb:	10 00                	adc    %al,(%rax)
  401dbd:	00 00                	add    %al,(%rax)
  401dbf:	00 08                	add    %cl,(%rax)
  401dc1:	00 00                	add    %al,(%rax)
  401dc3:	00 00                	add    %al,(%rax)
  401dc5:	00 00                	add    %al,(%rax)
  401dc7:	00 48 b1             	add    %cl,-0x4f(%rax)
  401dca:	da 03                	fiaddl (%rbx)
  401dcc:	00 00                	add    %al,(%rax)
  401dce:	00 00                	add    %al,(%rax)
  401dd0:	10 ef                	adc    %ch,%bh
  401dd2:	2f                   	(bad)
  401dd3:	10 00                	adc    %al,(%rax)
  401dd5:	00 00                	add    %al,(%rax)
  401dd7:	00 08                	add    %cl,(%rax)
  401dd9:	00 00                	add    %al,(%rax)
  401ddb:	00 00                	add    %al,(%rax)
  401ddd:	00 00                	add    %al,(%rax)
  401ddf:	00 d0                	add    %dl,%al
  401de1:	9e                   	sahf
  401de2:	b5 0f                	mov    $0xf,%ch
  401de4:	00 00                	add    %al,(%rax)
  401de6:	00 00                	add    %al,(%rax)
  401de8:	18 ef                	sbb    %ch,%bh
  401dea:	2f                   	(bad)
  401deb:	10 00                	adc    %al,(%rax)
  401ded:	00 00                	add    %al,(%rax)
  401def:	00 08                	add    %cl,(%rax)
  401df1:	00 00                	add    %al,(%rax)
  401df3:	00 00                	add    %al,(%rax)
  401df5:	00 00                	add    %al,(%rax)
  401df7:	00 30                	add    %dh,(%rax)
  401df9:	50                   	push   %rax
  401dfa:	12 07                	adc    (%rdi),%al
  401dfc:	00 00                	add    %al,(%rax)
  401dfe:	00 00                	add    %al,(%rax)
  401e00:	38 ef                	cmp    %ch,%bh
  401e02:	2f                   	(bad)
  401e03:	10 00                	adc    %al,(%rax)
  401e05:	00 00                	add    %al,(%rax)
  401e07:	00 08                	add    %cl,(%rax)
  401e09:	00 00                	add    %al,(%rax)
  401e0b:	00 00                	add    %al,(%rax)
  401e0d:	00 00                	add    %al,(%rax)
  401e0f:	00 f0                	add    %dh,%al
  401e11:	00 1d 03 00 00 00    	add    %bl,0x3(%rip)        # 0x401e1a
  401e17:	00 40 ef             	add    %al,-0x11(%rax)
  401e1a:	2f                   	(bad)
  401e1b:	10 00                	adc    %al,(%rax)
  401e1d:	00 00                	add    %al,(%rax)
  401e1f:	00 08                	add    %cl,(%rax)
  401e21:	00 00                	add    %al,(%rax)
  401e23:	00 00                	add    %al,(%rax)
  401e25:	00 00                	add    %al,(%rax)
  401e27:	00 10                	add    %dl,(%rax)
  401e29:	3a e0                	cmp    %al,%ah
  401e2b:	02 00                	add    (%rax),%al
  401e2d:	00 00                	add    %al,(%rax)
  401e2f:	00 48 ef             	add    %cl,-0x11(%rax)
  401e32:	2f                   	(bad)
  401e33:	10 00                	adc    %al,(%rax)
  401e35:	00 00                	add    %al,(%rax)
  401e37:	00 08                	add    %cl,(%rax)
  401e39:	00 00                	add    %al,(%rax)
  401e3b:	00 00                	add    %al,(%rax)
  401e3d:	00 00                	add    %al,(%rax)
  401e3f:	00 48 b1             	add    %cl,-0x4f(%rax)
  401e42:	da 03                	fiaddl (%rbx)
  401e44:	00 00                	add    %al,(%rax)
  401e46:	00 00                	add    %al,(%rax)
  401e48:	50                   	push   %rax
  401e49:	ef                   	out    %eax,(%dx)
  401e4a:	2f                   	(bad)
  401e4b:	10 00                	adc    %al,(%rax)
  401e4d:	00 00                	add    %al,(%rax)
  401e4f:	00 08                	add    %cl,(%rax)
  401e51:	00 00                	add    %al,(%rax)
  401e53:	00 00                	add    %al,(%rax)
  401e55:	00 00                	add    %al,(%rax)
  401e57:	00 a0 ae b5 0f 00    	add    %ah,0xfb5ae(%rax)
  401e5d:	00 00                	add    %al,(%rax)
  401e5f:	00 58 ef             	add    %bl,-0x11(%rax)
  401e62:	2f                   	(bad)
  401e63:	10 00                	adc    %al,(%rax)
  401e65:	00 00                	add    %al,(%rax)
  401e67:	00 08                	add    %cl,(%rax)
  401e69:	00 00                	add    %al,(%rax)
  401e6b:	00 00                	add    %al,(%rax)
  401e6d:	00 00                	add    %al,(%rax)
  401e6f:	00 30                	add    %dh,(%rax)
  401e71:	50                   	push   %rax
  401e72:	12 07                	adc    (%rdi),%al
  401e74:	00 00                	add    %al,(%rax)
  401e76:	00 00                	add    %al,(%rax)
  401e78:	78 ef                	js     0x401e69
  401e7a:	2f                   	(bad)
  401e7b:	10 00                	adc    %al,(%rax)
  401e7d:	00 00                	add    %al,(%rax)
  401e7f:	00 08                	add    %cl,(%rax)
  401e81:	00 00                	add    %al,(%rax)
  401e83:	00 00                	add    %al,(%rax)
  401e85:	00 00                	add    %al,(%rax)
  401e87:	00 f0                	add    %dh,%al
  401e89:	00 1d 03 00 00 00    	add    %bl,0x3(%rip)        # 0x401e92
  401e8f:	00 80 ef 2f 10 00    	add    %al,0x102fef(%rax)
  401e95:	00 00                	add    %al,(%rax)
  401e97:	00 08                	add    %cl,(%rax)
  401e99:	00 00                	add    %al,(%rax)
  401e9b:	00 00                	add    %al,(%rax)
  401e9d:	00 00                	add    %al,(%rax)
  401e9f:	00 10                	add    %dl,(%rax)
  401ea1:	3a e0                	cmp    %al,%ah
  401ea3:	02 00                	add    (%rax),%al
  401ea5:	00 00                	add    %al,(%rax)
  401ea7:	00 88 ef 2f 10 00    	add    %cl,0x102fef(%rax)
  401ead:	00 00                	add    %al,(%rax)
  401eaf:	00 08                	add    %cl,(%rax)
  401eb1:	00 00                	add    %al,(%rax)
  401eb3:	00 00                	add    %al,(%rax)
  401eb5:	00 00                	add    %al,(%rax)
  401eb7:	00 48 b1             	add    %cl,-0x4f(%rax)
  401eba:	da 03                	fiaddl (%rbx)
  401ebc:	00 00                	add    %al,(%rax)
  401ebe:	00 00                	add    %al,(%rax)
  401ec0:	90                   	nop
  401ec1:	ef                   	out    %eax,(%dx)
  401ec2:	2f                   	(bad)
  401ec3:	10 00                	adc    %al,(%rax)
  401ec5:	00 00                	add    %al,(%rax)
  401ec7:	00 08                	add    %cl,(%rax)
  401ec9:	00 00                	add    %al,(%rax)
  401ecb:	00 00                	add    %al,(%rax)
  401ecd:	00 00                	add    %al,(%rax)
  401ecf:	00 60 2d             	add    %ah,0x2d(%rax)
  401ed2:	2f                   	(bad)
  401ed3:	05 00 00 00 00       	add    $0x0,%eax
  401ed8:	98                   	cwtl
  401ed9:	ef                   	out    %eax,(%dx)
  401eda:	2f                   	(bad)
  401edb:	10 00                	adc    %al,(%rax)
  401edd:	00 00                	add    %al,(%rax)
  401edf:	00 08                	add    %cl,(%rax)
  401ee1:	00 00                	add    %al,(%rax)
  401ee3:	00 00                	add    %al,(%rax)
  401ee5:	00 00                	add    %al,(%rax)
  401ee7:	00 30                	add    %dh,(%rax)
  401ee9:	50                   	push   %rax
  401eea:	12 07                	adc    (%rdi),%al
  401eec:	00 00                	add    %al,(%rax)
  401eee:	00 00                	add    %al,(%rax)
  401ef0:	b8 ef 2f 10 00       	mov    $0x102fef,%eax
  401ef5:	00 00                	add    %al,(%rax)
  401ef7:	00 08                	add    %cl,(%rax)
  401ef9:	00 00                	add    %al,(%rax)
  401efb:	00 00                	add    %al,(%rax)
  401efd:	00 00                	add    %al,(%rax)
  401eff:	00 f0                	add    %dh,%al
  401f01:	00 1d 03 00 00 00    	add    %bl,0x3(%rip)        # 0x401f0a
  401f07:	00 c0                	add    %al,%al
  401f09:	ef                   	out    %eax,(%dx)
  401f0a:	2f                   	(bad)
  401f0b:	10 00                	adc    %al,(%rax)
  401f0d:	00 00                	add    %al,(%rax)
  401f0f:	00 08                	add    %cl,(%rax)
  401f11:	00 00                	add    %al,(%rax)
  401f13:	00 00                	add    %al,(%rax)
  401f15:	00 00                	add    %al,(%rax)
  401f17:	00 10                	add    %dl,(%rax)
  401f19:	3a e0                	cmp    %al,%ah
  401f1b:	02 00                	add    (%rax),%al
  401f1d:	00 00                	add    %al,(%rax)
  401f1f:	00 c8                	add    %cl,%al
  401f21:	ef                   	out    %eax,(%dx)
  401f22:	2f                   	(bad)
  401f23:	10 00                	adc    %al,(%rax)
  401f25:	00 00                	add    %al,(%rax)
  401f27:	00 08                	add    %cl,(%rax)
  401f29:	00 00                	add    %al,(%rax)
  401f2b:	00 00                	add    %al,(%rax)
  401f2d:	00 00                	add    %al,(%rax)
  401f2f:	00 48 b1             	add    %cl,-0x4f(%rax)
  401f32:	da 03                	fiaddl (%rbx)
  401f34:	00 00                	add    %al,(%rax)
  401f36:	00 00                	add    %al,(%rax)
  401f38:	d0 ef                	shr    $1,%bh
  401f3a:	2f                   	(bad)
  401f3b:	10 00                	adc    %al,(%rax)
  401f3d:	00 00                	add    %al,(%rax)
  401f3f:	00 08                	add    %cl,(%rax)
  401f41:	00 00                	add    %al,(%rax)
  401f43:	00 00                	add    %al,(%rax)
  401f45:	00 00                	add    %al,(%rax)
  401f47:	00 10                	add    %dl,(%rax)
  401f49:	f7 2f                	imull  (%rdi)
  401f4b:	06                   	(bad)
  401f4c:	00 00                	add    %al,(%rax)
  401f4e:	00 00                	add    %al,(%rax)
  401f50:	d8 ef                	fsubr  %st(7),%st
  401f52:	2f                   	(bad)
  401f53:	10 00                	adc    %al,(%rax)
  401f55:	00 00                	add    %al,(%rax)
  401f57:	00 08                	add    %cl,(%rax)
  401f59:	00 00                	add    %al,(%rax)
  401f5b:	00 00                	add    %al,(%rax)
  401f5d:	00 00                	add    %al,(%rax)
  401f5f:	00 30                	add    %dh,(%rax)
  401f61:	50                   	push   %rax
  401f62:	12 07                	adc    (%rdi),%al
  401f64:	00 00                	add    %al,(%rax)
  401f66:	00 00                	add    %al,(%rax)
  401f68:	f8                   	clc
  401f69:	ef                   	out    %eax,(%dx)
  401f6a:	2f                   	(bad)
  401f6b:	10 00                	adc    %al,(%rax)
  401f6d:	00 00                	add    %al,(%rax)
  401f6f:	00 08                	add    %cl,(%rax)
  401f71:	00 00                	add    %al,(%rax)
  401f73:	00 00                	add    %al,(%rax)
  401f75:	00 00                	add    %al,(%rax)
  401f77:	00 f0                	add    %dh,%al
  401f79:	00 1d 03 00 00 00    	add    %bl,0x3(%rip)        # 0x401f82
  401f7f:	00 00                	add    %al,(%rax)
  401f81:	f0 2f                	lock (bad)
  401f83:	10 00                	adc    %al,(%rax)
  401f85:	00 00                	add    %al,(%rax)
  401f87:	00 08                	add    %cl,(%rax)
  401f89:	00 00                	add    %al,(%rax)
  401f8b:	00 00                	add    %al,(%rax)
  401f8d:	00 00                	add    %al,(%rax)
  401f8f:	00 10                	add    %dl,(%rax)
  401f91:	3a e0                	cmp    %al,%ah
  401f93:	02 00                	add    (%rax),%al
  401f95:	00 00                	add    %al,(%rax)
  401f97:	00 08                	add    %cl,(%rax)
  401f99:	f0 2f                	lock (bad)
  401f9b:	10 00                	adc    %al,(%rax)
  401f9d:	00 00                	add    %al,(%rax)
  401f9f:	00 08                	add    %cl,(%rax)
  401fa1:	00 00                	add    %al,(%rax)
  401fa3:	00 00                	add    %al,(%rax)
  401fa5:	00 00                	add    %al,(%rax)
  401fa7:	00 48 b1             	add    %cl,-0x4f(%rax)
  401faa:	da 03                	fiaddl (%rbx)
  401fac:	00 00                	add    %al,(%rax)
  401fae:	00 00                	add    %al,(%rax)
  401fb0:	10 f0                	adc    %dh,%al
  401fb2:	2f                   	(bad)
  401fb3:	10 00                	adc    %al,(%rax)
  401fb5:	00 00                	add    %al,(%rax)
  401fb7:	00 08                	add    %cl,(%rax)
  401fb9:	00 00                	add    %al,(%rax)
  401fbb:	00 00                	add    %al,(%rax)
  401fbd:	00 00                	add    %al,(%rax)
  401fbf:	00 80 71 a7 05 00    	add    %al,0x5a771(%rax)
  401fc5:	00 00                	add    %al,(%rax)
  401fc7:	00 18                	add    %bl,(%rax)
  401fc9:	f0 2f                	lock (bad)
  401fcb:	10 00                	adc    %al,(%rax)
  401fcd:	00 00                	add    %al,(%rax)
  401fcf:	00 08                	add    %cl,(%rax)
  401fd1:	00 00                	add    %al,(%rax)
  401fd3:	00 00                	add    %al,(%rax)
  401fd5:	00 00                	add    %al,(%rax)
  401fd7:	00 30                	add    %dh,(%rax)
  401fd9:	50                   	push   %rax
  401fda:	12 07                	adc    (%rdi),%al
  401fdc:	00 00                	add    %al,(%rax)
  401fde:	00 00                	add    %al,(%rax)
  401fe0:	38 f0                	cmp    %dh,%al
  401fe2:	2f                   	(bad)
  401fe3:	10 00                	adc    %al,(%rax)
  401fe5:	00 00                	add    %al,(%rax)
  401fe7:	00 08                	add    %cl,(%rax)
  401fe9:	00 00                	add    %al,(%rax)
  401feb:	00 00                	add    %al,(%rax)
  401fed:	00 00                	add    %al,(%rax)
  401fef:	00 f0                	add    %dh,%al
  401ff1:	00 1d 03 00 00 00    	add    %bl,0x3(%rip)        # 0x401ffa
  401ff7:	00 40 f0             	add    %al,-0x10(%rax)
  401ffa:	2f                   	(bad)
  401ffb:	10 00                	adc    %al,(%rax)
  401ffd:	00 00                	add    %al,(%rax)
  401fff:	00 08                	add    %cl,(%rax)
  402001:	00 00                	add    %al,(%rax)
  402003:	00 00                	add    %al,(%rax)
  402005:	00 00                	add    %al,(%rax)
  402007:	00 10                	add    %dl,(%rax)
  402009:	3a e0                	cmp    %al,%ah
  40200b:	02 00                	add    (%rax),%al
  40200d:	00 00                	add    %al,(%rax)
  40200f:	00 48 f0             	add    %cl,-0x10(%rax)
  402012:	2f                   	(bad)
  402013:	10 00                	adc    %al,(%rax)
  402015:	00 00                	add    %al,(%rax)
  402017:	00 08                	add    %cl,(%rax)
  402019:	00 00                	add    %al,(%rax)
  40201b:	00 00                	add    %al,(%rax)
  40201d:	00 00                	add    %al,(%rax)
  40201f:	00 48 b1             	add    %cl,-0x4f(%rax)
  402022:	da 03                	fiaddl (%rbx)
  402024:	00 00                	add    %al,(%rax)
  402026:	00 00                	add    %al,(%rax)
  402028:	50                   	push   %rax
  402029:	f0 2f                	lock (bad)
  40202b:	10 00                	adc    %al,(%rax)
  40202d:	00 00                	add    %al,(%rax)
  40202f:	00 08                	add    %cl,(%rax)
  402031:	00 00                	add    %al,(%rax)
  402033:	00 00                	add    %al,(%rax)
  402035:	00 00                	add    %al,(%rax)
  402037:	00 70 2a             	add    %dh,0x2a(%rax)
  40203a:	b6 0f                	mov    $0xf,%dh
  40203c:	00 00                	add    %al,(%rax)
  40203e:	00 00                	add    %al,(%rax)
  402040:	58                   	pop    %rax
  402041:	f0 2f                	lock (bad)
  402043:	10 00                	adc    %al,(%rax)
  402045:	00 00                	add    %al,(%rax)
  402047:	00 08                	add    %cl,(%rax)
  402049:	00 00                	add    %al,(%rax)
  40204b:	00 00                	add    %al,(%rax)
  40204d:	00 00                	add    %al,(%rax)
  40204f:	00 30                	add    %dh,(%rax)
  402051:	50                   	push   %rax
  402052:	12 07                	adc    (%rdi),%al
  402054:	00 00                	add    %al,(%rax)
  402056:	00 00                	add    %al,(%rax)
  402058:	78 f0                	js     0x40204a
  40205a:	2f                   	(bad)
  40205b:	10 00                	adc    %al,(%rax)
  40205d:	00 00                	add    %al,(%rax)
  40205f:	00 08                	add    %cl,(%rax)
  402061:	00 00                	add    %al,(%rax)
  402063:	00 00                	add    %al,(%rax)
  402065:	00 00                	add    %al,(%rax)
  402067:	00 f0                	add    %dh,%al
  402069:	00 1d 03 00 00 00    	add    %bl,0x3(%rip)        # 0x402072
  40206f:	00 80 f0 2f 10 00    	add    %al,0x102ff0(%rax)
  402075:	00 00                	add    %al,(%rax)
  402077:	00 08                	add    %cl,(%rax)
  402079:	00 00                	add    %al,(%rax)
  40207b:	00 00                	add    %al,(%rax)
  40207d:	00 00                	add    %al,(%rax)
  40207f:	00 10                	add    %dl,(%rax)
  402081:	3a e0                	cmp    %al,%ah
  402083:	02 00                	add    (%rax),%al
  402085:	00 00                	add    %al,(%rax)
  402087:	00 88 f0 2f 10 00    	add    %cl,0x102ff0(%rax)
  40208d:	00 00                	add    %al,(%rax)
  40208f:	00 08                	add    %cl,(%rax)
  402091:	00 00                	add    %al,(%rax)
  402093:	00 00                	add    %al,(%rax)
  402095:	00 00                	add    %al,(%rax)
  402097:	00 48 b1             	add    %cl,-0x4f(%rax)
  40209a:	da 03                	fiaddl (%rbx)
  40209c:	00 00                	add    %al,(%rax)
  40209e:	00 00                	add    %al,(%rax)
  4020a0:	90                   	nop
  4020a1:	f0 2f                	lock (bad)
  4020a3:	10 00                	adc    %al,(%rax)
  4020a5:	00 00                	add    %al,(%rax)
  4020a7:	00 08                	add    %cl,(%rax)
  4020a9:	00 00                	add    %al,(%rax)
  4020ab:	00 00                	add    %al,(%rax)
  4020ad:	00 00                	add    %al,(%rax)
  4020af:	00 10                	add    %dl,(%rax)
  4020b1:	46 b6 0f             	rex.RX mov $0xf,%sil
  4020b4:	00 00                	add    %al,(%rax)
  4020b6:	00 00                	add    %al,(%rax)
  4020b8:	98                   	cwtl
  4020b9:	f0 2f                	lock (bad)
  4020bb:	10 00                	adc    %al,(%rax)
  4020bd:	00 00                	add    %al,(%rax)
  4020bf:	00 08                	add    %cl,(%rax)
  4020c1:	00 00                	add    %al,(%rax)
  4020c3:	00 00                	add    %al,(%rax)
  4020c5:	00 00                	add    %al,(%rax)
  4020c7:	00 30                	add    %dh,(%rax)
  4020c9:	46 b6 0f             	rex.RX mov $0xf,%sil
  4020cc:	00 00                	add    %al,(%rax)
  4020ce:	00 00                	add    %al,(%rax)
  4020d0:	b8 f0 2f 10 00       	mov    $0x102ff0,%eax
  4020d5:	00 00                	add    %al,(%rax)
  4020d7:	00 08                	add    %cl,(%rax)
  4020d9:	00 00                	add    %al,(%rax)
  4020db:	00 00                	add    %al,(%rax)
  4020dd:	00 00                	add    %al,(%rax)
  4020df:	00 f0                	add    %dh,%al
  4020e1:	00 1d 03 00 00 00    	add    %bl,0x3(%rip)        # 0x4020ea
  4020e7:	00 c0                	add    %al,%al
  4020e9:	f0 2f                	lock (bad)
  4020eb:	10 00                	adc    %al,(%rax)
  4020ed:	00 00                	add    %al,(%rax)
  4020ef:	00 08                	add    %cl,(%rax)
  4020f1:	00 00                	add    %al,(%rax)
  4020f3:	00 00                	add    %al,(%rax)
  4020f5:	00 00                	add    %al,(%rax)
  4020f7:	00 10                	add    %dl,(%rax)
  4020f9:	3a e0                	cmp    %al,%ah
  4020fb:	02 00                	add    (%rax),%al
  4020fd:	00 00                	add    %al,(%rax)
  4020ff:	00 c8                	add    %cl,%al
  402101:	f0 2f                	lock (bad)
  402103:	10 00                	adc    %al,(%rax)
  402105:	00 00                	add    %al,(%rax)
  402107:	00 08                	add    %cl,(%rax)
  402109:	00 00                	add    %al,(%rax)
  40210b:	00 00                	add    %al,(%rax)
  40210d:	00 00                	add    %al,(%rax)
  40210f:	00 48 b1             	add    %cl,-0x4f(%rax)
  402112:	da 03                	fiaddl (%rbx)
  402114:	00 00                	add    %al,(%rax)
  402116:	00 00                	add    %al,(%rax)
  402118:	d0 f0                	shl    $1,%al
  40211a:	2f                   	(bad)
  40211b:	10 00                	adc    %al,(%rax)
  40211d:	00 00                	add    %al,(%rax)
  40211f:	00 08                	add    %cl,(%rax)
  402121:	00 00                	add    %al,(%rax)
  402123:	00 00                	add    %al,(%rax)
  402125:	00 00                	add    %al,(%rax)
  402127:	00 50 30             	add    %dl,0x30(%rax)
  40212a:	42 06                	rex.X (bad)
  40212c:	00 00                	add    %al,(%rax)
  40212e:	00 00                	add    %al,(%rax)
  402130:	d8 f0                	fdiv   %st(0),%st
  402132:	2f                   	(bad)
  402133:	10 00                	adc    %al,(%rax)
  402135:	00 00                	add    %al,(%rax)
  402137:	00 08                	add    %cl,(%rax)
  402139:	00 00                	add    %al,(%rax)
  40213b:	00 00                	add    %al,(%rax)
  40213d:	00 00                	add    %al,(%rax)
  40213f:	00 30                	add    %dh,(%rax)
  402141:	50                   	push   %rax
  402142:	12 07                	adc    (%rdi),%al
  402144:	00 00                	add    %al,(%rax)
  402146:	00 00                	add    %al,(%rax)
  402148:	f8                   	clc
  402149:	f0 2f                	lock (bad)
  40214b:	10 00                	adc    %al,(%rax)
  40214d:	00 00                	add    %al,(%rax)
  40214f:	00 08                	add    %cl,(%rax)
  402151:	00 00                	add    %al,(%rax)
  402153:	00 00                	add    %al,(%rax)
  402155:	00 00                	add    %al,(%rax)
  402157:	00 f0                	add    %dh,%al
  402159:	00 1d 03 00 00 00    	add    %bl,0x3(%rip)        # 0x402162
  40215f:	00 00                	add    %al,(%rax)
  402161:	f1                   	int1
  402162:	2f                   	(bad)
  402163:	10 00                	adc    %al,(%rax)
  402165:	00 00                	add    %al,(%rax)
  402167:	00 08                	add    %cl,(%rax)
  402169:	00 00                	add    %al,(%rax)
  40216b:	00 00                	add    %al,(%rax)
  40216d:	00 00                	add    %al,(%rax)
  40216f:	00 10                	add    %dl,(%rax)
  402171:	3a e0                	cmp    %al,%ah
  402173:	02 00                	add    (%rax),%al
  402175:	00 00                	add    %al,(%rax)
  402177:	00 08                	add    %cl,(%rax)
  402179:	f1                   	int1
  40217a:	2f                   	(bad)
  40217b:	10 00                	adc    %al,(%rax)
  40217d:	00 00                	add    %al,(%rax)
  40217f:	00 08                	add    %cl,(%rax)
  402181:	00 00                	add    %al,(%rax)
  402183:	00 00                	add    %al,(%rax)
  402185:	00 00                	add    %al,(%rax)
  402187:	00 48 b1             	add    %cl,-0x4f(%rax)
  40218a:	da 03                	fiaddl (%rbx)
  40218c:	00 00                	add    %al,(%rax)
  40218e:	00 00                	add    %al,(%rax)
  402190:	10 f1                	adc    %dh,%cl
  402192:	2f                   	(bad)
  402193:	10 00                	adc    %al,(%rax)
  402195:	00 00                	add    %al,(%rax)
  402197:	00 08                	add    %cl,(%rax)
  402199:	00 00                	add    %al,(%rax)
  40219b:	00 00                	add    %al,(%rax)
  40219d:	00 00                	add    %al,(%rax)
  40219f:	00 30                	add    %dh,(%rax)
  4021a1:	54                   	push   %rsp
  4021a2:	b6 0f                	mov    $0xf,%dh
  4021a4:	00 00                	add    %al,(%rax)
  4021a6:	00 00                	add    %al,(%rax)
  4021a8:	18 f1                	sbb    %dh,%cl
  4021aa:	2f                   	(bad)
  4021ab:	10 00                	adc    %al,(%rax)
  4021ad:	00 00                	add    %al,(%rax)
  4021af:	00 08                	add    %cl,(%rax)
  4021b1:	00 00                	add    %al,(%rax)
  4021b3:	00 00                	add    %al,(%rax)
  4021b5:	00 00                	add    %al,(%rax)
  4021b7:	00 30                	add    %dh,(%rax)
  4021b9:	50                   	push   %rax
  4021ba:	12 07                	adc    (%rdi),%al
  4021bc:	00 00                	add    %al,(%rax)
  4021be:	00 00                	add    %al,(%rax)
  4021c0:	38 f1                	cmp    %dh,%cl
  4021c2:	2f                   	(bad)
  4021c3:	10 00                	adc    %al,(%rax)
  4021c5:	00 00                	add    %al,(%rax)
  4021c7:	00 08                	add    %cl,(%rax)
  4021c9:	00 00                	add    %al,(%rax)
  4021cb:	00 00                	add    %al,(%rax)
  4021cd:	00 00                	add    %al,(%rax)
  4021cf:	00 f0                	add    %dh,%al
  4021d1:	00 1d 03 00 00 00    	add    %bl,0x3(%rip)        # 0x4021da
  4021d7:	00 40 f1             	add    %al,-0xf(%rax)
  4021da:	2f                   	(bad)
  4021db:	10 00                	adc    %al,(%rax)
  4021dd:	00 00                	add    %al,(%rax)
  4021df:	00 08                	add    %cl,(%rax)
  4021e1:	00 00                	add    %al,(%rax)
  4021e3:	00 00                	add    %al,(%rax)
  4021e5:	00 00                	add    %al,(%rax)
  4021e7:	00 10                	add    %dl,(%rax)
  4021e9:	3a e0                	cmp    %al,%ah
  4021eb:	02 00                	add    (%rax),%al
  4021ed:	00 00                	add    %al,(%rax)
  4021ef:	00 48 f1             	add    %cl,-0xf(%rax)
  4021f2:	2f                   	(bad)
  4021f3:	10 00                	adc    %al,(%rax)
  4021f5:	00 00                	add    %al,(%rax)
  4021f7:	00 08                	add    %cl,(%rax)
  4021f9:	00 00                	add    %al,(%rax)
  4021fb:	00 00                	add    %al,(%rax)
  4021fd:	00 00                	add    %al,(%rax)
  4021ff:	00 48 b1             	add    %cl,-0x4f(%rax)
  402202:	da 03                	fiaddl (%rbx)
  402204:	00 00                	add    %al,(%rax)
  402206:	00 00                	add    %al,(%rax)
  402208:	50                   	push   %rax
  402209:	f1                   	int1
  40220a:	2f                   	(bad)
  40220b:	10 00                	adc    %al,(%rax)
  40220d:	00 00                	add    %al,(%rax)
  40220f:	00 08                	add    %cl,(%rax)
  402211:	00 00                	add    %al,(%rax)
  402213:	00 00                	add    %al,(%rax)
  402215:	00 00                	add    %al,(%rax)
  402217:	00 e0                	add    %ah,%al
  402219:	c0 ac 07 00 00 00 00 	shrb   $0x58,0x0(%rdi,%rax,1)
  402220:	58 
  402221:	f1                   	int1
  402222:	2f                   	(bad)
  402223:	10 00                	adc    %al,(%rax)
  402225:	00 00                	add    %al,(%rax)
  402227:	00 08                	add    %cl,(%rax)
  402229:	00 00                	add    %al,(%rax)
  40222b:	00 00                	add    %al,(%rax)
  40222d:	00 00                	add    %al,(%rax)
  40222f:	00 a0 35 4a 06 00    	add    %ah,0x64a35(%rax)
  402235:	00 00                	add    %al,(%rax)
  402237:	00 78 f1             	add    %bh,-0xf(%rax)
  40223a:	2f                   	(bad)
  40223b:	10 00                	adc    %al,(%rax)
  40223d:	00 00                	add    %al,(%rax)
  40223f:	00 08                	add    %cl,(%rax)
  402241:	00 00                	add    %al,(%rax)
  402243:	00 00                	add    %al,(%rax)
  402245:	00 00                	add    %al,(%rax)
  402247:	00 f0                	add    %dh,%al
  402249:	00 1d 03 00 00 00    	add    %bl,0x3(%rip)        # 0x402252
  40224f:	00 80 f1 2f 10 00    	add    %al,0x102ff1(%rax)
  402255:	00 00                	add    %al,(%rax)
  402257:	00 08                	add    %cl,(%rax)
  402259:	00 00                	add    %al,(%rax)
  40225b:	00 00                	add    %al,(%rax)
  40225d:	00 00                	add    %al,(%rax)
  40225f:	00 10                	add    %dl,(%rax)
  402261:	3a e0                	cmp    %al,%ah
  402263:	02 00                	add    (%rax),%al
  402265:	00 00                	add    %al,(%rax)
  402267:	00 88 f1 2f 10 00    	add    %cl,0x102ff1(%rax)
  40226d:	00 00                	add    %al,(%rax)
  40226f:	00 08                	add    %cl,(%rax)
  402271:	00 00                	add    %al,(%rax)
  402273:	00 00                	add    %al,(%rax)
  402275:	00 00                	add    %al,(%rax)
  402277:	00 48 b1             	add    %cl,-0x4f(%rax)
  40227a:	da 03                	fiaddl (%rbx)
  40227c:	00 00                	add    %al,(%rax)
  40227e:	00 00                	add    %al,(%rax)
  402280:	90                   	nop
  402281:	f1                   	int1
  402282:	2f                   	(bad)
  402283:	10 00                	adc    %al,(%rax)
  402285:	00 00                	add    %al,(%rax)
  402287:	00 08                	add    %cl,(%rax)
  402289:	00 00                	add    %al,(%rax)
  40228b:	00 00                	add    %al,(%rax)
  40228d:	00 00                	add    %al,(%rax)
  40228f:	00 a0 aa b7 0f 00    	add    %ah,0xfb7aa(%rax)
  402295:	00 00                	add    %al,(%rax)
  402297:	00 98 f1 2f 10 00    	add    %bl,0x102ff1(%rax)
  40229d:	00 00                	add    %al,(%rax)
  40229f:	00 08                	add    %cl,(%rax)
  4022a1:	00 00                	add    %al,(%rax)
  4022a3:	00 00                	add    %al,(%rax)
  4022a5:	00 00                	add    %al,(%rax)
  4022a7:	00 c0                	add    %al,%al
  4022a9:	aa                   	stos   %al,(%rdi)
  4022aa:	b7 0f                	mov    $0xf,%bh
  4022ac:	00 00                	add    %al,(%rax)
  4022ae:	00 00                	add    %al,(%rax)
  4022b0:	b8 f1 2f 10 00       	mov    $0x102ff1,%eax
  4022b5:	00 00                	add    %al,(%rax)
  4022b7:	00 08                	add    %cl,(%rax)
  4022b9:	00 00                	add    %al,(%rax)
  4022bb:	00 00                	add    %al,(%rax)
  4022bd:	00 00                	add    %al,(%rax)
  4022bf:	00 f0                	add    %dh,%al
  4022c1:	00 1d 03 00 00 00    	add    %bl,0x3(%rip)        # 0x4022ca
  4022c7:	00 c0                	add    %al,%al
  4022c9:	f1                   	int1
  4022ca:	2f                   	(bad)
  4022cb:	10 00                	adc    %al,(%rax)
  4022cd:	00 00                	add    %al,(%rax)
  4022cf:	00 08                	add    %cl,(%rax)
  4022d1:	00 00                	add    %al,(%rax)
  4022d3:	00 00                	add    %al,(%rax)
  4022d5:	00 00                	add    %al,(%rax)
  4022d7:	00 10                	add    %dl,(%rax)
  4022d9:	3a e0                	cmp    %al,%ah
  4022db:	02 00                	add    (%rax),%al
  4022dd:	00 00                	add    %al,(%rax)
  4022df:	00 c8                	add    %cl,%al
  4022e1:	f1                   	int1
  4022e2:	2f                   	(bad)
  4022e3:	10 00                	adc    %al,(%rax)
  4022e5:	00 00                	add    %al,(%rax)
  4022e7:	00 08                	add    %cl,(%rax)
  4022e9:	00 00                	add    %al,(%rax)
  4022eb:	00 00                	add    %al,(%rax)
  4022ed:	00 00                	add    %al,(%rax)
  4022ef:	00 48 b1             	add    %cl,-0x4f(%rax)
  4022f2:	da 03                	fiaddl (%rbx)
	...
