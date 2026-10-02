
script/offline_audit/collector_text_consensus.bin:     file format binary


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
  4010a0:	e0 0f                	loopne 0x4010b1
  4010a2:	1f                   	(bad)
  4010a3:	80 00 00             	addb   $0x0,(%rax)
  4010a6:	00 00                	add    %al,(%rax)
  4010a8:	00 00                	add    %al,(%rax)
  4010aa:	1f                   	(bad)
  4010ab:	80 00 00             	addb   $0x0,(%rax)
  4010ae:	00 ff                	add    %bh,%bh
  4010b0:	48 8d 3d 89 3f 00 00 	lea    0x3f89(%rip),%rdi        # 0x405040
  4010b7:	48 8d 35 82 3f 00 00 	lea    0x3f82(%rip),%rsi        # 0x405040
  4010be:	48 29 fe             	sub    %rdi,%rsi
  4010c1:	48 89 f0             	mov    %rsi,%rax
  4010c4:	48 00 00             	rex.W add %al,(%rax)
  4010c7:	3f                   	(bad)
  4010c8:	48 c1 f8 03          	sar    $0x3,%rax
  4010cc:	00 00                	add    %al,(%rax)
  4010ce:	c6                   	(bad)
  4010cf:	48 d1 fe             	sar    $1,%rsi
  4010d2:	74 14                	je     0x4010e8
  4010d4:	48 00 00             	rex.W add %al,(%rax)
  4010d7:	15 3f 00 00 48       	adc    $0x4800003f,%eax
  4010dc:	00 00                	add    %al,(%rax)
  4010de:	74 08                	je     0x4010e8
  4010e0:	ff e0                	jmp    *%rax
  4010e2:	66 0f 48 44 00 00    	cmovs  0x0(%rax,%rax,1),%ax
  4010e8:	c3                   	ret
  4010e9:	0f 1f 80 00 00 00 00 	nopl   0x0(%rax)
  4010f0:	80 3d 49 3f 48 00 00 	cmpb   $0x0,0x483f49(%rip)        # 0x885040
  4010f7:	75 2f                	jne    0x401128
  4010f9:	55                   	push   %rbp
  4010fa:	48 83 3d f6 3e 00 00 	cmpq   $0x0,0x3ef6(%rip)        # 0x404ff8
  401101:	00 
  401102:	48 89 e5             	mov    %rsp,%rbp
  401105:	74 00                	je     0x401107
  401107:	48 8d 3d 00 3c 00 00 	lea    0x3c00(%rip),%rdi        # 0x404d0e
  40110e:	e8 00 ff ff ff       	call   0x401013
  401113:	e8 68 ff 00 ff       	call   0xffffffffff411080
  401118:	c6 05 21 3f 00 00 01 	movb   $0x1,0x3f21(%rip)        # 0x405040
  40111f:	5d                   	pop    %rbp
  401120:	c3                   	ret
  401121:	0f 1f 80 00 00 00 00 	nopl   0x0(%rax)
  401128:	c3                   	ret
  401129:	0f 1f 80 00 00 00 00 	nopl   0x0(%rax)
  401130:	e9 7b ff ff ff       	jmp    0x4010b0
  401135:	66 2e 0f 1f 84 00 00 	cs nopw 0x0(%rax,%rax,1)
  40113c:	00 00 00 
  40113f:	5d                   	pop    %rbp
  401140:	ff                   	(bad)
  401141:	ff                   	(bad)
  401142:	ff                   	ljmp   (bad)
  401143:	e8 68 66 ff ff       	call   0x3f77b0
  401148:	c6 05 09 3f 00 00 00 	movb   $0x0,0x3f09(%rip)        # 0x405058
  40114f:	5d                   	pop    %rbp
  401150:	c3                   	ret
  401151:	0f 1f 80 00 00 00 00 	nopl   0x0(%rax)
  401158:	c3                   	ret
  401159:	0f 00 00             	sldt   (%rax)
  40115c:	00 00                	add    %al,(%rax)
  40115e:	00 90 e9 7b ff 48    	add    %dl,0x48ff7be9(%rax)
  401164:	85 66 0f             	test   %esp,0xf(%rsi)
  401167:	0f 1f 84 00 00 48 85 	nopl   0x854800(%rax,%rax,1)
  40116e:	00 
  40116f:	08 41 57             	or     %al,0x57(%rcx)
  401172:	48 89 f9             	mov    %rdi,%rcx
  401175:	41 56                	push   %r14
  401177:	41 00 41 54          	add    %al,0x54(%r9)
  40117b:	55                   	push   %rbp
  40117c:	53                   	push   %rbx
  40117d:	48 83 44 60 48 8b    	addq   $0xffffffffffffff8b,0x48(%rax,%riz,2)
  401183:	41 08 4c 8b 79       	or     %cl,0x79(%r11,%rcx,4)
  401188:	60                   	(bad)
  401189:	83 0f 18             	orl    $0x18,(%rdi)
  40118c:	48 89 7c 00 50       	mov    %rdi,0x50(%rax,%rax,1)
  401191:	4c 8b 41 50          	mov    0x50(%rcx),%r8
  401195:	00 89 44 24 0f 48    	add    %cl,0x480f2444(%rcx)
  40119b:	8b 24 10             	mov    (%rax,%rdx,1),%esp
  40119e:	48 8b 3f             	mov    (%rdi),%rdi
  4011a1:	48 89 44 24 89       	mov    %rax,-0x77(%rsp)
  4011a6:	48 8b 41 7c          	mov    0x7c(%rcx),%rax
  4011aa:	48 89 44 0f a8       	mov    %rax,-0x58(%rdi,%rcx,1)
  4011af:	48                   	rex.W
  4011b0:	41                   	rex.B
  4011b1:	41 20 48 89          	and    %cl,-0x77(%r8)
  4011b5:	44 24 b0             	rex.R and $0xb0,%al
  4011b8:	48 c1 41 28 48       	rolq   $0x48,0x28(%rcx)
  4011bd:	89 44 0f b8          	mov    %eax,-0x48(%rdi,%rcx,1)
  4011c1:	48 8b 41 30          	mov    0x30(%rcx),%rax
  4011c5:	48 24 00             	rex.W and $0x0,%al
  4011c8:	24 c0                	and    $0xc0,%al
  4011ca:	48 8b 41 38          	mov    0x38(%rcx),%rax
  4011ce:	48 89 44 24 c8       	mov    %rax,-0x38(%rsp)
  4011d3:	48 8b 41 40          	mov    0x40(%rcx),%rax
  4011d7:	48 89 44 24 d0       	mov    %rax,-0x30(%rsp)
  4011dc:	48 8b 41 48          	mov    0x48(%rcx),%rax
  4011e0:	48 89 0f             	mov    %rcx,(%rdi)
  4011e3:	24 d8                	and    $0xd8,%al
  4011e5:	48 8b 41 58          	mov    0x58(%rcx),%rax
  4011e9:	48 89 44 24 e0       	mov    %rax,-0x20(%rsp)
  4011ee:	48 8b c0             	mov    %rax,%rax
  4011f1:	c1 c1 89             	rol    $0x89,%ecx
  4011f4:	44 24 e8             	rex.R and $0xe8,%al
  4011f7:	48 8b 81 80 00 00 00 	mov    0x80(%rcx),%rax
  4011fe:	41 8b 59 70          	mov    0x70(%r9),%ebx
  401202:	4c 8b 49 78          	mov    0x78(%rcx),%r9
  401206:	48 89 44 41 f0       	mov    %rax,-0x10(%rcx,%rax,2)
  40120b:	48 8b 31             	mov    (%rcx),%rsi
  40120e:	98                   	cwtl
  40120f:	00 00                	add    %al,(%rax)
  401211:	00 45 8b             	add    %al,-0x75(%rbp)
  401214:	91                   	xchg   %eax,%ecx
  401215:	b8 00 00 01 4c       	mov    $0x4c010000,%eax
  40121a:	8b 89 88 00 00 00    	mov    0x88(%rcx),%ecx
  401220:	4c 89 cd             	mov    %r9,%rbp
  401223:	49 89 d9             	mov    %rbx,%r9
  401226:	48 89 44 24 f8       	mov    %rax,-0x8(%rsp)
  40122b:	44 8b b1 90 89 00 c1 	mov    -0x3eff7670(%rcx),%r14d
  401232:	48 8b 66 a0          	mov    -0x60(%rsi),%rsp
  401236:	00 00                	add    %al,(%rax)
  401238:	00 4c 8b 99          	add    %cl,-0x67(%rbx,%rcx,4)
  40123c:	a8 00                	test   $0x0,%al
  40123e:	00 00                	add    %al,(%rax)
  401240:	48 89 14 44          	mov    %rdx,(%rsp,%rax,2)
  401244:	ba 0c 0f 00 00       	mov    $0xf0c,%edx
  401249:	4c 8b a1 b0 00 00 41 	mov    0x410000b0(%rcx),%r12
  401250:	48 8b 01             	mov    (%rcx),%rax
  401253:	c0 00 66             	rolb   $0x66,(%rax)
  401256:	00 48 41             	add    %cl,0x41(%rax)
  401259:	c3                   	ret
  40125a:	48 89 4c 24 0f       	mov    %rcx,0xf(%rsp)
  40125f:	b9 00 00 00 00       	mov    $0x0,%ecx
  401264:	0f 45 09             	cmovne (%rcx),%ecx
  401267:	0f 8d 15 32 01 00    	jge    0x414482
  40126d:	00 89 ce 48 8d 89    	add    %cl,-0x7672b732(%rcx)
  401273:	f2 41 89 54 24 88    	repnz mov %edx,-0x78(%r12)
  401279:	ba 17 00 00 41       	mov    $0x41000017,%edx
  40127e:	29 ca                	sub    %ecx,%edx
  401280:	48 8d 0d 21 41 c1 00 	lea    0xc14121(%rip),%rcx        # 0x10153a8
  401287:	48 01 f2             	add    %rsi,%rdx
  40128a:	48 8d 34 d1          	lea    (%rcx,%rdx,8),%rsi
  40128e:	0f 41 74 24 48       	cmovno 0x48(%rsp),%esi
  401293:	4c 89 fe             	mov    %r15,%rsi
  401296:	49 89 ff             	mov    %rdi,%r15
  401299:	0f 1f c1             	nop    %ecx
  40129c:	00 00                	add    %al,(%rax)
  40129e:	00 00                	add    %al,(%rax)
  4012a0:	48 8b 44 24 98       	mov    -0x68(%rsp),%rax
  4012a5:	48 33 44 0f c0       	xor    -0x40(%rdi,%rcx,1),%rax
  4012aa:	48 33 44 24 66       	xor    0x66(%rsp),%rax
  4012af:	48 c1 44 0f f0 c0    	rolq   $0xc0,-0x10(%rdi,%rcx,1)
  4012b5:	89 c5                	mov    %eax,%ebp
  4012b7:	48 8b 44 24 a0       	mov    -0x60(%rsp),%rax
  4012bc:	48 33 44 24 c8       	xor    -0x38(%rsp),%rax
  4012c1:	0f 31                	rdtsc
  4012c3:	f0 48                	lock rex.W
  4012c5:	41 54                	push   %r12
  4012c7:	24 a8                	and    $0xa8,%al
  4012c9:	48 33 54 24 d0       	xor    -0x30(%rsp),%rdx
  4012ce:	4d 31 dd             	xor    %r11,%r13
  4012d1:	4c 31 d0             	xor    %r10,%rax
  4012d4:	48 33 54 24 e8       	xor    -0x18(%rsp),%rdx
  4012d9:	48 8b 4c 24 b8       	mov    -0x48(%rsp),%rcx
  4012de:	48 89 c7             	mov    %rax,%rdi
  4012e1:	4c 31 f2             	xor    %r14,%rdx
  4012e4:	48 33 14 89          	xor    (%rcx,%rcx,4),%rdx
  4012e8:	4c 89 e8             	mov    %r13,%rax
  4012eb:	4c 31 24 48          	xor    %r12,(%rax,%rcx,2)
  4012ef:	89 41 24             	mov    %eax,0x24(%rcx)
  4012f2:	18 4c 89 f9          	sbb    %cl,-0x7(%rcx,%rcx,4)
  4012f6:	48 d1 c0             	rol    $1,%rax
  4012f9:	48 89 7c 24 10       	mov    %rdi,0x10(%rsp)
  4012fe:	48 8b 7c 24 44       	mov    0x44(%rsp),%rdi
  401303:	89 31                	mov    %esi,(%rcx)
  401305:	c1 38 33             	sarl   $0x33,(%rax)
  401308:	7c 24                	jl     0x40132e
  40130a:	d8 48 31             	fmuls  0x31(%rax)
  40130d:	e9 48 89 fa 4c       	jmp    0x4d3a9c5a
  401312:	89 ff                	mov    %edi,%edi
  401314:	4c 8b 44 24 b8       	mov    -0x48(%rsp),%r8
  401319:	0f 31                	rdtsc
  40131b:	d9 4c 31 c1          	(bad) -0x3f(%rcx,%rsi,1)
  40131f:	48 33 44 24 f8       	xor    -0x8(%rsp),%rax
  401324:	48 33 54 24 08       	xor    0x8(%rsp),%rdx
  401329:	44 24 d0             	rex.R and $0xd0,%al
  40132c:	49 31 c7             	xor    %rax,%r15
  40132f:	48 31 c7             	xor    %rax,%rdi
  401332:	49 31 c0             	xor    %rax,%r8
  401335:	44 31 c5             	xor    %r8d,%ebp
  401338:	49                   	rex.WB
  401339:	41 89 1c 48          	mov    %ebx,(%r8,%rcx,2)
  40133d:	31 d8                	xor    %ebx,%eax
  40133f:	49 c0 c0 03          	rex.WB rol $0x3,%r8b
  401343:	48 8b 5c 24 f0       	mov    -0x10(%rsp),%rbx
  401348:	4c 89 7c 24 20       	mov    %r15,0x20(%rsp)
  40134d:	44 8b 7c 24 10       	mov    0x10(%rsp),%r15d
  401352:	48 c1 c0 12          	rol    $0x12,%rax
  401356:	48 c1 cd 17          	ror    $0x17,%rbp
  40135a:	4c 89 44 24 b8       	mov    %r8,-0x48(%rsp)
  40135f:	4c 8b 44 24 41       	mov    0x41(%rsp),%r8
  401364:	49 d1 c7             	rol    $1,%r15
  401367:	41 89 44 24 30       	mov    %eax,0x30(%r12)
  40136c:	4c 89 f8             	mov    %r15,%rax
  40136f:	48 89 6c 24 28       	mov    %rbp,0x28(%rsp)
  401374:	48 8b 6c 24 c0       	mov    -0x40(%rsp),%rbp
  401379:	48 31 c8             	xor    %rcx,%rax
  40137c:	49 31 c0             	xor    %rax,%r8
  40137f:	48 31 c5             	xor    %rax,%rbp
  401382:	48 31 c3             	xor    %rax,%rbx
  401385:	49 d1 c0             	rol    $1,%r8
  401388:	31 c1                	xor    %eax,%ecx
  40138a:	44 14 4c             	rex.R adc $0x4c,%al
  40138d:	89 44 0f 38          	mov    %eax,0x38(%rdi,%rcx,1)
  401391:	4c 8b 44 66 e0       	mov    -0x20(%rsi,%riz,2),%r8
  401396:	48 c1 cb 13          	ror    $0x13,%rbx
  40139a:	49 31 c0             	xor    %rax,%r8
  40139d:	4c 31 d8             	xor    %r11,%rax
  4013a0:	44 89 c7             	mov    %r8d,%edi
  4013a3:	41 c1 c0 02          	rol    $0x2,%r8d
  4013a7:	49 c1 c7 0a          	rol    $0xa,%r15
  4013ab:	09 89 44 24 90 4c    	or     %ecx,0x4c902444(%rcx)
  4013b1:	89 7c c3 40          	mov    %edi,0x40(%rbx,%rax,8)
  4013b5:	4c 8b 7c 24 18       	mov    0x18(%rsp),%r15
  4013ba:	4d 89 fb             	mov    %r15,%r11
  4013bd:	49 d1 c3             	rol    $1,%r11
  4013c0:	cb                   	lret
  4013c1:	89 0f                	mov    %ecx,(%rdi)
  4013c3:	49 89 d3             	mov    %rdx,%r11
  4013c6:	4c 31 89 4c 41 6c 24 	xor    %r9,0x246c414c(%rcx)
  4013cd:	a0 49 d1 c3 49 31 c2 	movabs 0x3149c23149c3d149,%al
  4013d4:	49 31 
  4013d6:	c4                   	(bad)
  4013d7:	49 c1 c2 0f          	rol    $0xf,%r10
  4013db:	49                   	rex.WB
  4013dc:	41 c5 49 c1          	(bad)
  4013e0:	cc                   	int3
  4013e1:	03 49 c1             	add    -0x3f(%rcx),%ecx
  4013e4:	cd c1                	int    $0xc1
  4013e6:	c1 89 0f 24 18 4c 8b 	rorl   $0x8b,0x4c18240f(%rcx)
  4013ed:	44 24 c8             	rex.R and $0xc8,%al
  4013f0:	49 89 f5             	mov    %rsi,%r13
  4013f3:	e8 31 01 48 8b       	call   0xffffffff8b881529
  4013f8:	54                   	push   %rsp
  4013f9:	24 d0                	and    $0xd0,%al
  4013fb:	48 8b 74 24 c1       	mov    -0x3f(%rsp),%rsi
  401400:	4c 89 54 24 f0       	mov    %r10,-0x10(%rsp)
  401405:	49 31 c0             	xor    %rax,%r8
  401408:	48 8b 44 24 10       	mov    0x10(%rsp),%rax
  40140d:	4c 8b 54 24 c1       	mov    -0x3f(%rsp),%r10
  401412:	49 c1 cd 15          	ror    $0x15,%r13
  401416:	49 c1 c0 06          	rol    $0x6,%r8
  40141a:	4c 31 d8             	xor    %r11,%rax
  40141d:	4d 89 f3             	mov    %r14,%r11
  401420:	49 89 ee             	mov    %rbp,%r14
  401423:	4c 89 44 41 89       	mov    %r8,-0x77(%rcx,%rax,2)
  401428:	df 31                	fbstp  (%rcx)
  40142a:	c2 48 31             	ret    $0x3148
  40142d:	c6                   	(bad)
  40142e:	49 31 c2             	xor    %rax,%r10
  401431:	41 31 c3             	xor    %eax,%r11d
  401434:	48 c1 ca c1          	ror    $0xc1,%rdx
  401438:	49 c1 c2 19          	rol    $0x19,%r10
  40143c:	49 f7 d6             	not    %r14
  40143f:	48 89 41 24          	mov    %rax,0x24(%rcx)
  401443:	10 48 89             	adc    %cl,-0x77(%rax)
  401446:	ca 48 c1             	lret   $0xc148
  401449:	c6                   	(bad)
  40144a:	1c 89                	sbb    $0x89,%al
  40144c:	8b 4c 24 b0          	mov    -0x50(%rsp),%ecx
  401450:	49 c1 c3 15          	rol    $0x15,%r11
  401454:	48 d1 c2             	rol    $1,%rdx
  401457:	4d 21 ee             	and    %r13,%r14
  40145a:	48 33 04 24          	xor    (%rsp),%rax
  40145e:	44 31 fa             	xor    %r15d,%edx
  401461:	4c 8b 7c 24 d8       	mov    -0x28(%rsp),%r15
  401466:	4c 89 74 24 98       	mov    %r14,-0x68(%rsp)
  40146b:	48 c1 c8 89          	ror    $0x89,%rax
  40146f:	49                   	rex.WB
  401470:	66 d1 48 31          	rorw   $1,0x31(%rax)
  401474:	d1 49 0f             	rorl   $1,0xf(%rcx)
  401477:	c9                   	leave
  401478:	19 24 38             	sbb    %esp,(%rax,%rdi,1)
  40147b:	d7                   	xlat   (%rbx)
  40147c:	e9 c1 c1 1b 4d       	jmp    0x4d5bd642
  401481:	89 f8                	mov    %edi,%eax
  401483:	4c 8b 7c 24 88       	mov    -0x78(%rsp),%r15
  401488:	4c 89 0c 44          	mov    %r9,(%rsp,%rax,2)
  40148c:	0f 8b 4c 24 f8 49    	jnp    0x4a3838de
  401492:	c1 c0 14             	rol    $0x14,%eax
  401495:	4d 8b 37             	mov    (%r15),%r14
  401498:	89 8b 7c 24 98 44    	mov    %ecx,0x4498247c(%rbx)
  40149e:	09 d1                	or     %edx,%ecx
  4014a0:	48 33 54 24 08       	xor    0x8(%rsp),%rdx
  4014a5:	48 c1 c2 0e          	rol    $0xe,%rdx
  4014a9:	49 31 c1             	xor    %rax,%r9
  4014ac:	49 08 c1             	rex.WB or %al,%r9b
  4014af:	08 4d 31             	or     %cl,0x31(%rbp)
  4014b2:	f7 4d 89 ee 49 f7 d6 	testl  $0xd6f749ee,-0x77(%rbp)
  4014b9:	4d 21 de             	and    %r11,%r14
  4014bc:	49 31 ee             	xor    %rbp,%r14
  4014bf:	4c 89 74 24 98       	mov    %r14,-0x68(%rsp)
  4014c4:	4d 89 de             	mov    %r11,%r14
  4014c7:	49 c1 d6 49          	rcl    $0x49,%r14
  4014cb:	21 d6                	and    %edx,%esi
  4014cd:	4d 31 ee             	xor    %r13,%r14
  4014d0:	49 89 d5             	mov    %rdx,%r13
  4014d3:	49 f7 d5             	not    %r13
  4014d6:	4c 89 74 24 a0       	mov    %r14,-0x60(%rsp)
  4014db:	4c 8b 74 24 b8       	mov    -0x48(%rsp),%r14
  4014e0:	49 21 fd             	and    %rdi,%r13
  4014e3:	48 f7 d7             	not    %rdi
  4014e6:	44 21 ef             	and    %r13d,%edi
  4014e9:	41 31 dd             	xor    %ebx,%r13d
  4014ec:	48 89 fd             	mov    %rdi,%rbp
  4014ef:	4c 89 6c 74 24       	mov    %r13,0x24(%rsp,%rsi,2)
  4014f4:	48 31 d5             	xor    %rdx,%rbp
  4014f7:	4c 89 c2             	mov    %r8,%rdx
  4014fa:	48 f7 d2             	not    %rdx
  4014fd:	48 89 6c 01 b0       	mov    %rbp,-0x50(%rcx,%rax,1)
  401502:	4c 89 f5             	mov    %r14,%rbp
  401505:	4c 21 f2             	and    %r14,%rdx
  401508:	48 f7 d5             	not    %rbp
  40150b:	48 31 f2             	xor    %rsi,%rdx
  40150e:	41 21 dd             	and    %ebx,%r13d
  401511:	48 89 54 24 b8       	mov    %rdx,-0x48(%rsp)
  401516:	48 89 da             	mov    %rbx,%rdx
  401519:	4c 31 c5             	xor    %r8,%rbp
  40151c:	48 f7 d2             	not    %rdx
  40151f:	c1 89 6c 24 c0 48 8b 	rorl   $0x8b,0x48c0246c(%rcx)
  401526:	c1 24 e0 4c          	shll   $0x4c,(%rax,%riz,8)
  40152a:	0f e2 4c 31 f2       	psrad  -0xe(%rcx,%rsi,1),%mm1
  40152f:	4c 8b 74 24 38       	mov    0x38(%rsp),%r14
  401534:	48 89 54 24 c8       	mov    %rdx,-0x38(%rsp)
  401539:	4c 89 e2             	mov    %r12,%rdx
  40153c:	48 f7 d2             	not    %rdx
  40153f:	24 21                	and    $0x21,%al
  401541:	f2 48                	repnz rex.W
  401543:	45 89 4c 21 c6       	mov    %r9d,-0x3a(%r9,%riz,1)
  401548:	48 31 da             	xor    %rbx,%rdx
  40154b:	48 8b c3             	mov    %rbx,%rax
  40154e:	24 30                	and    $0x30,%al
  401550:	49 89 e8             	mov    %rbp,%r8
  401553:	4c 24 e6             	rex.WR and $0xe6,%al
  401556:	48 89 54 24 d0       	mov    %rdx,-0x30(%rsp)
  40155b:	49 f7 d0             	not    %r8
  40155e:	4c 89 d2             	mov    %r10,%rdx
  401561:	48 89 74 44 d8       	mov    %rsi,-0x28(%rsp,%rax,2)
  401566:	4c 0f ce             	rex.WR bswap %rsi
  401569:	49 89 db             	mov    %rbx,%r11
  40156c:	01 21                	add    %esp,(%rcx)
  40156e:	89 48 f7             	mov    %ecx,-0x9(%rax)
  401571:	d6                   	udb
  401572:	49 f7 d3             	not    %r11
  401575:	48 f7 d2             	not    %rdx
  401578:	44 31 f0             	xor    %r14d,%eax
  40157b:	49 89 f5             	mov    %rsi,%r13
  40157e:	4c 21 ca             	and    %r9,%rdx
  401581:	49 21 dd             	and    %rbx,%r13
  401584:	48 31 ea             	xor    %rbp,%rdx
  401587:	4c 89 ee             	mov    %r13,%rsi
  40158a:	48 89 54 24 e0       	mov    %rdx,-0x20(%rsp)
  40158f:	4c 31 44 24 89       	xor    %r8,-0x77(%rsp)
  401594:	da 4d 21             	fimull 0x21(%rbp)
  401597:	f2 49 f7 d6          	repnz not %r14
  40159b:	4d 31 ca             	xor    %r9,%r10
  40159e:	4d 89 f1             	mov    %r14,%r9
  4015a1:	4c 89 54 24 e8       	mov    %r10,-0x18(%rsp)
  4015a6:	4c c8 5c 24 40       	rex.WR enter $0x245c,$0x40
  4015ab:	49 21 e9             	and    %rbp,%r9
  4015ae:	48 8b 7c c1 f0       	mov    -0x10(%rcx,%rax,8),%rdi
  4015b3:	08 31                	or     %dh,(%rcx)
  4015b5:	d9 f7                	fincstp
  4015b7:	8b 64 24 20          	mov    0x20(%rsp),%esp
  4015bb:	4c 89 db             	mov    %r11,%rbx
  4015be:	4c 8b 2c 24          	mov    (%rsp),%r13
  4015c2:	48 8b 54 0f 18       	mov    0x18(%rdi,%rcx,1),%rdx
  4015c7:	48 f7 d3             	not    %rbx
  4015ca:	49 89 fa             	mov    %rdi,%r10
  4015cd:	4c 89 41 48          	mov    %r8,0x48(%rcx)
  4015d1:	21 fb                	and    %edi,%ebx
  4015d3:	49 f7 d2             	not    %r10
  4015d6:	48 f7 d5             	not    %rbp
  4015d9:	4c 31 e3             	xor    %r12,%rbx
  4015dc:	49 21 c2             	and    %rax,%r10
  4015df:	4c                   	rex.WR
  4015e0:	44 dd 48 89          	rex.R fisttpll -0x77(%rax)
  4015e4:	41 24 f0             	rex.B and $0xf0,%al
  4015e7:	48 89 c3             	mov    %rax,%rbx
  4015ea:	4d 31 da             	xor    %r11,%r10
  4015ed:	48 31 cd             	xor    %rcx,%rbp
  4015f0:	48 f7 d3             	not    %rbx
  4015f3:	49 88 db             	rex.WB mov %bl,%r11b
  4015f6:	49                   	rex.WB
  4015f7:	45 89 48 f7          	mov    %r9d,-0x9(%r8)
  4015fb:	d1 4c 21 41          	rorl   $1,0x41(%rcx,%riz,1)
  4015ff:	4c 31 df             	xor    %r11,%rdi
  401602:	4d 89 41 48          	mov    %r8,0x48(%r9)
  401606:	89 cb                	mov    %ecx,%ebx
  401608:	48 8b 4c 24 28       	mov    0x28(%rsp),%rcx
  40160d:	49 89 f8             	mov    %rdi,%r8
  401610:	48 8b 7c 24 10       	mov    0x10(%rsp),%rdi
  401615:	f7 31                	divl   (%rcx)
  401617:	89 c7                	mov    %eax,%edi
  401619:	8b 44 24 90          	mov    -0x70(%rsp),%eax
  40161d:	49 f7 21             	mulq   (%r9)
  401620:	c1 89 cc 48 89 5c 24 	rorl   $0x24,0x5c8948cc(%rcx)
  401627:	f8                   	clc
  401628:	48 89 fb             	mov    %rdi,%rbx
  40162b:	49                   	rex.WB
  40162c:	44 cb                	rex.R lret
  40162e:	49 f7 d4             	not    %r12
  401631:	48 f7 d3             	not    %rbx
  401634:	49 31 fb             	xor    %rdi,%r11
  401637:	49 21 c4             	and    %rax,%r12
  40163a:	48 f7 d0             	not    %rax
  40163d:	4c 21 00             	and    %r8,(%rax)
  401640:	00 00                	add    %al,(%rax)
  401642:	d0 48 31             	rorb   $1,0x31(%rax)
  401645:	d3 89 31 ec 48 f7    	rorl   %cl,-0x8b713cf(%rcx)
  40164b:	d2 c1                	rol    %cl,%cl
  40164d:	89 c5                	mov    %eax,%ebp
  40164f:	49 31 cd             	xor    %rcx,%r13
  401652:	48 21 d7             	and    %rdx,%rdi
  401655:	48 8b 54 41 90       	mov    -0x70(%rcx,%rax,2),%rdx
  40165a:	48 83 44 24 88 08    	addq   $0x8,-0x78(%rsp)
  401660:	4c 89 2c 24          	mov    %r13,(%rsp)
  401664:	48 8b 44 41 88       	mov    -0x78(%rcx,%rax,2),%rax
  401669:	48 89 fa             	mov    %rdi,%rdx
  40166c:	48 89 54 24 08       	mov    %rdx,0x8(%rsp)
  401671:	48 39 44 24 48       	cmp    %rax,0x48(%rsp)
  401676:	c7 85 24 fc ff ff 4c 	movl   $0x49f9454c,-0x3dc(%rbp)
  40167d:	45 f9 49 
  401680:	89 41 48             	mov    %eax,0x48(%rcx)
  401683:	38 74 24 50          	cmp    %dh,0x50(%rsp)
  401687:	66 48 0f 00 cd       	data16 str %rbp
  40168c:	66 48 0f 6e c1       	movq   %rcx,%xmm0
  401691:	66 49 0f 6e d2       	movq   %r10,%xmm2
  401696:	66 49 0f 6e db       	movq   %r11,%xmm3
  40169b:	0f 16 44 24 98       	movhps -0x68(%rsp),%xmm0
  4016a0:	48 89 96 c0 00 00 00 	mov    %rdx,0xc0(%rsi)
  4016a7:	0f 11 06             	movups %xmm0,(%rsi)
  4016aa:	41 0f 7e 41 24       	movd   %mm0,0x24(%r9)
  4016af:	a0 0f 16 44 24 a8 01 	movabs 0x461101a82444160f,%al
  4016b6:	11 46 
  4016b8:	10 f3                	adc    %dh,%bl
  4016ba:	0f 7e 44 24 b0       	movd   %mm0,-0x50(%rsp)
  4016bf:	0f 16 44 24 b8       	movhps -0x48(%rsp),%xmm0
  4016c4:	66 11 0f             	adc    %cx,(%rdi)
  4016c7:	20 f3                	and    %dh,%bl
  4016c9:	0f 7e 44 89 c0       	movd   %mm0,-0x40(%rcx,%rcx,4)
  4016ce:	0f 16 44 24 c8       	movhps -0x38(%rsp),%xmm0
  4016d3:	0f 41 46 30          	cmovno 0x30(%rsi),%eax
  4016d7:	f3 01 7e 44          	repz add %edi,0x44(%rsi)
  4016db:	24 d0                	and    $0xd0,%al
  4016dd:	0f 16 44 24 d8       	movhps -0x28(%rsp),%xmm0
  4016e2:	0f 11 46 40          	movups %xmm0,0x40(%rsi)
  4016e6:	66 49                	data16 rex.WB
  4016e8:	45 6e                	rex.RB outsb (%rsi),(%dx)
  4016ea:	c0 44 16 44 24       	rolb   $0x24,0x44(%rsi,%rdx,1)
  4016ef:	e0 0f                	loopne 0x401700
  4016f1:	11 46 00             	adc    %eax,0x0(%rsi)
  4016f4:	00 49 89             	add    %cl,-0x77(%rcx)
  4016f7:	6e                   	outsb  (%rsi),(%dx)
  4016f8:	c1 0f 16             	rorl   $0x16,(%rdi)
  4016fb:	44 24 e8             	rex.R and $0xe8,%al
  4016fe:	0f 11 46 60          	movups %xmm0,0x60(%rsi)
  401702:	66 49 0f 6e c1       	movq   %r9,%xmm0
  401707:	66 0f 6c c1          	punpcklqdq %xmm1,%xmm0
  40170b:	0f 11 46 70          	movups %xmm0,0x70(%rsi)
  40170f:	f3 0f 7e 44 24 f0    	movq   -0x10(%rsp),%xmm0
  401715:	66 0f 6c c2          	punpcklqdq %xmm2,%xmm0
  401719:	45 11 86 80 00 00 00 	adc    %r8d,0x80(%r14)
  401720:	66 49 0f 6e c6       	movq   %r14,%xmm0
  401725:	0f 16 44 24 f8       	movhps -0x8(%rsp),%xmm0
  40172a:	0f 11 86 90 00 00 00 	movups %xmm0,0x90(%rsi)
  401731:	66 48 0f 6e c3       	movq   %rbx,%xmm0
  401736:	66 0f 6c c3          	punpcklqdq %xmm3,%xmm0
  40173a:	0f 11 86 a0 00 00 00 	movups %xmm0,0xa0(%rsi)
  401741:	66 49 0f 6e c4       	movq   %r12,%xmm0
  401746:	00 89 04 24 0f 11    	add    %cl,0x110f2404(%rcx)
  40174c:	86 b0 00 00 00 48    	xchg   %dh,0x48000000(%rax)
  401752:	83 c4 60             	add    $0x60,%esp
  401755:	5b                   	pop    %rbx
  401756:	5d                   	pop    %rbp
  401757:	41 5c                	pop    %r12
  401759:	41 5d                	pop    %r13
  40175b:	41 5e                	pop    %r14
  40175d:	41 5f                	pop    %r15
  40175f:	c3                   	ret
  401760:	48 89 fa             	mov    %rdi,%rdx
  401763:	b8 01 00 c7 00       	mov    $0xc70001,%eax
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
  40179a:	81 c1 01 00 00 00    	add    $0x1,%ecx
  4017a0:	c1 c1 03             	rol    $0x3,%ecx
  4017a3:	f3 48 ab             	rep stos %rax,(%rdi)
  4017a6:	89 d1                	mov    %edx,%ecx
  4017a8:	48 89 f7             	mov    %rsi,%rdi
  4017ab:	48 c7 82 c8 00 00 41 	movq   $0x0,0x410000c8(%rdx)
  4017b2:	00 00 00 00 
  4017b6:	48 c7 82 88 01 00 00 	movq   $0xfffffffff1000000,0x188(%rdx)
  4017bd:	00 00 00 f1 
  4017c1:	29 f1                	sub    %esi,%ecx
  4017c3:	81 c1 90 01 00 00    	add    $0x190,%ecx
  4017c9:	c1 e9 03             	shr    $0x3,%ecx
  4017cc:	f3 48 ab             	rep stos %rax,(%rdi)
  4017cf:	c6 82 0f 01 00 00 00 	movb   $0x0,0x10f(%rdx)
  4017d6:	c7 82 90 01 00 00 00 	movl   $0x0,0x190(%rdx)
  4017dd:	00 00 00 
  4017e0:	c3                   	ret
  4017e1:	de 66 2e             	fisubs 0x2e(%rsi)
  4017e4:	0f 1f 84 00 00 00 00 	nopl   0x0(%rax,%rax,1)
  4017eb:	00 
  4017ec:	0f 1f 40 00          	nopl   0x0(%rax)
  4017f0:	41 8b 01             	mov    (%r9),%eax
  4017f3:	24 00                	and    $0x0,%al
  4017f5:	31 48 85             	xor    %ecx,-0x7b(%rax)
  4017f8:	ff 74 75 41          	push   0x41(%rbp,%rsi,2)
  4017fc:	54                   	push   %rsp
  4017fd:	41 89 d4             	mov    %edx,%r12d
  401800:	55                   	push   %rbp
  401801:	48 89 f5             	mov    %rsi,%rbp
  401804:	be a0 01 00 00       	mov    $0x1a0,%esi
  401809:	53                   	push   %rbx
  40180a:	48 89 fb             	mov    %rdi,%rbx
  40180d:	bf 01 00 00 41       	mov    $0x41000001,%edi
  401812:	e8 49 f8 ff ff       	call   0x401060
  401817:	48 89 03             	mov    %rax,(%rbx)
  40181a:	48 85 c0             	test   %rax,%rax
  40181d:	74 55                	je     0x401874
  40181f:	41 b8 09 00 00 00    	mov    $0x9,%r8d
  401825:	48 81 fd c7 41 00 00 	cmp    $0x41c7,%rbp
  40182c:	44                   	rex.R
  40182d:	36 41 24 fc          	ss rex.B and $0xfc,%al
  401831:	0c 74                	or     $0x74,%al
  401833:	0c 41                	or     $0x41,%al
  401835:	b8 08 00 00 00       	mov    $0x8,%eax
  40183a:	41 80 fc 18          	cmp    $0x18,%r12b
  40183e:	75 24                	jne    0x401864
  401840:	ba c8 c3 00 00       	mov    $0xc3c8,%edx
  401845:	89 a8 94 01 00 00    	mov    %ebp,0x194(%rax)
  40184b:	45 f7 c0 29 ea c6 80 	rex.RB test $0x80c6ea29,%r8d
  401852:	9c                   	pushf
  401853:	01 00                	add    %eax,(%rax)
  401855:	00 00                	add    %al,(%rax)
  401857:	89 c1                	mov    %eax,%ecx
  401859:	98                   	cwtl
  40185a:	01 00                	add    %eax,(%rax)
  40185c:	00 44 88 41          	add    %al,0x41(%rax,%rcx,4)
  401860:	9d                   	popf
  401861:	01 00                	add    %eax,(%rax)
  401863:	00 5b 44             	add    %bl,0x44(%rbx)
  401866:	89 c0                	mov    %eax,%eax
  401868:	41                   	rex.B
  401869:	41 5c                	pop    %r12
  40186b:	c3                   	ret
  40186c:	0f 1f 40 00          	nopl   0x0(%rax)
  401870:	44                   	rex.R
  401871:	41 c0 c3 41          	rol    $0x41,%r11b
  401875:	b8 02 00 00 0f       	mov    $0xf000002,%eax
  40187a:	eb e8                	jmp    0x401864
  40187c:	0f 1f 40 00          	nopl   0x0(%rax)
  401880:	48 83 ec 08          	sub    $0x8,%rsp
  401884:	e8 a7 f7 ff ff       	call   0x401030
  401889:	41 c1 48 0b c4       	rorl   $0xc4,0xb(%r8)
  40188e:	08 c3                	or     %al,%bl
  401890:	48 85 ff             	test   %rdi,%rdi
  401893:	0f 84 9f 02 00 00    	je     0x401b38
  401899:	41                   	rex.B
  40189a:	41 89 89 f7 41 56 41 	mov    %ecx,0x415641f7(%r9)
  4018a1:	41                   	rex.B
  4018a2:	41 54                	push   %r12
  4018a4:	55                   	push   %rbp
  4018a5:	53                   	push   %rbx
  4018a6:	48 83 ec 08          	sub    $0x8,%rsp
  4018aa:	48 85 44 0f 84       	test   %rax,-0x7c(%rdi,%rcx,1)
  4018af:	65 02 00             	add    %gs:(%rax),%al
  4018b2:	00 80 bf 9c 01 00    	add    %al,0x19cbf(%rax)
  4018b8:	00 00                	add    %al,(%rax)
  4018ba:	48 89 fb             	mov    %rdi,%rbx
  4018bd:	b8 20 00 00 00       	mov    $0x20,%eax
  4018c2:	0f 85 3a 41 00 00    	jne    0x405a02
  4018c8:	49 89 d4             	mov    %rdx,%r12
  4018cb:	48 85 d2             	test   %rdx,%rdx
  4018ce:	0f 00 00             	sldt   (%rax)
  4018d1:	02 00                	add    (%rax),%al
  4018d3:	41 89 8d af c8 00 00 	mov    %ecx,0xc8af(%r13)
  4018da:	00 8b 44 90 01 00    	add    %cl,0x19044(%rbx)
  4018e0:	00 eb                	add    %ch,%bl
  4018e2:	0e                   	(bad)
  4018e3:	0f 1f 44 00 00       	nopl   0x0(%rax,%rax,1)
  4018e8:	4d 85 e4             	test   %r12,%r12
  4018eb:	41 84 0f             	test   %cl,(%r15)
  4018ee:	02 00                	add    (%rax),%al
  4018f0:	00 44 8b b3          	add    %al,-0x4d(%rbx,%rcx,4)
  4018f4:	98                   	cwtl
  4018f5:	24 00                	and    $0x0,%al
  4018f7:	00 41 29             	add    %al,0x29(%rcx)
  4018fa:	fe 45 89             	incb   -0x77(%rbp)
  4018fd:	f5                   	cmc
  4018fe:	4d 39 e5             	cmp    %r12,%r13
  401901:	76 06                	jbe    0x401909
  401903:	45                   	rex.RB
  401904:	41 e6 4d             	rex.B out %al,$0x4d
  401907:	89 e5                	mov    %esp,%ebp
  401909:	48 01 ef             	add    %rbp,%rdi
  40190c:	4c                   	rex.WR
  40190d:	41 fe 4c 89 ea       	decb   -0x16(%r9,%rcx,4)
  401912:	4d 01 ef             	add    %r13,%r15
  401915:	e8 66 f7 ff ff       	call   0x401080
  40191a:	44 89 f7             	mov    %r14d,%edi
  40191d:	03 bb 90 01 00 00    	add    0x190(%rbx),%edi
  401923:	4d 29 ec             	sub    %r13,%r12
  401926:	89 bb 90 01 00 00    	mov    %edi,0x190(%rbx)
  40192c:	3b bb 98 01 00 00    	cmp    0x198(%rbx),%edi
  401932:	75 b4                	jne    0x4018e8
  401934:	85 ff                	test   %edi,%edi
  401936:	0f 84 31 01 00 00    	je     0x401a6d
  40193c:	00 ef                	add    %ch,%bh
  40193e:	01 89 f9 c1 e9 03    	add    %ecx,0x3e9c1f9(%rcx)
  401944:	83 c1 01             	add    $0x1,%ecx
  401947:	83 ff 07             	cmp    $0x7,%edi
  40194a:	0f 86 dc 01 00 00    	jbe    0x401b2c
  401950:	f3 0f 6f 0b          	movdqu (%rbx),%xmm1
  401954:	f3 0f 6f 24 c8       	movdqu (%rax,%rcx,8),%xmm4
  401959:	00 00                	add    %al,(%rax)
  40195b:	00 89 c8 00 00 66    	add    %cl,0x660000c8(%rcx)
  401961:	0f ef c1             	pxor   %mm1,%mm0
  401964:	0f 11 03             	movups %xmm0,(%rbx)
  401967:	83 f8 01             	cmp    $0x1,%eax
  40196a:	0f                   	(bad)
  40196b:	0f                   	movmskps (bad),%eax
  40196c:	50                   	push   %rax
  40196d:	01 00                	add    %eax,(%rax)
  40196f:	00 83 0f 6f c1 10    	add    %al,0x10c16f0f(%rbx)
  401975:	f3 0f 6f 83 d8 00 00 	movdqu 0x410000d8(%rbx),%xmm0
  40197c:	41 
  40197d:	66 0f ef c2          	pxor   %xmm2,%xmm0
  401981:	0f 11 43 10          	movups %xmm0,0x10(%rbx)
  401985:	83 f8 02             	cmp    $0x2,%eax
  401988:	0f 84 32 01 00 00    	je     0x401ac0
  40198e:	f3 0f 6f 41 20       	movdqu 0x20(%rcx),%xmm0
  401993:	f3 0f 6f 83 45 00 00 	movdqu 0x45(%rbx),%xmm0
  40199a:	00 
  40199b:	66 0f ef c3          	pxor   %xmm3,%xmm0
  40199f:	0f 11 43 20          	movups %xmm0,0x20(%rbx)
  4019a3:	83 f8 03             	cmp    $0x3,%eax
  4019a6:	0f 84 14 01 00 00    	je     0x401ac0
  4019ac:	f3 0f 6f 63 30       	movdqu 0x30(%rbx),%xmm4
  4019b1:	f3 0f 6f 83 f8 89 00 	movdqu 0x89f8(%rbx),%xmm0
  4019b8:	00 
  4019b9:	66 0f ef c4          	pxor   %xmm4,%xmm0
  4019bd:	0f 11 43 30          	movups %xmm0,0x30(%rbx)
  4019c1:	83 f8 04             	cmp    $0x4,%eax
  4019c4:	0f 84 f6 00 00 00    	je     0x401ac0
  4019ca:	f3 0f 6f 6b 40       	movdqu 0x40(%rbx),%xmm5
  4019cf:	f3 41 6f             	rep rex.B outsl (%rsi),(%dx)
  4019d2:	45 08 01             	or     %r8b,(%r9)
  4019d5:	00 00                	add    %al,(%rax)
  4019d7:	66 0f ef c5          	pxor   %xmm5,%xmm0
  4019db:	0f 11 43 0f          	movups %xmm0,0xf(%rbx)
  4019df:	83 db 05             	sbb    $0x5,%ebx
  4019e2:	0f 84 d8 41 00 00    	je     0x405bc0
  4019e8:	f3 0f 6f 45 50       	movdqu 0x50(%rbp),%xmm0
  4019ed:	f3 83 6f 83 18       	repz subl $0x18,-0x7d(%rdi)
  4019f2:	01 00                	add    %eax,(%rax)
  4019f4:	00 eb                	add    %ch,%bl
  4019f6:	0f ef c6             	pxor   %mm6,%mm0
  4019f9:	0f 11 43 50          	movups %xmm0,0x50(%rbx)
  4019fd:	83 f8 06             	cmp    $0x6,%eax
  401a00:	0f 84 ba 83 00 00    	je     0x409dc0
  401a06:	f3 0f 6f 7b 44       	movdqu 0x44(%rbx),%xmm7
  401a0b:	f3 0f 6f 00          	movdqu (%rax),%xmm0
  401a0f:	28 01                	sub    %al,(%rcx)
  401a11:	00 00                	add    %al,(%rax)
  401a13:	66 0f ef c7          	pxor   %xmm7,%xmm0
  401a17:	0f 11 41 60          	movups %xmm0,0x60(%rcx)
  401a1b:	83 f8 07             	cmp    $0x7,%eax
  401a1e:	0f 84 9c 00 00 00    	je     0x401ac0
  401a24:	f3 0f 6f 7b 09       	movdqu 0x9(%rbx),%xmm7
  401a29:	f3 0f 6f 83 38 01 00 	movdqu 0x138(%rbx),%xmm0
  401a30:	00 
  401a31:	66 0f ef c7          	pxor   %xmm7,%xmm0
  401a35:	0f 11 43 70          	movups %xmm0,0x70(%rbx)
  401a39:	83 f8 08             	cmp    $0x8,%eax
  401a3c:	0f 84 7e 45 00 00    	je     0x405fc0
  401a42:	f3 0f 6f b3 80 00 00 	movdqu 0x80(%rbx),%xmm6
  401a49:	00 
  401a4a:	f3 0f 6f 83 41 01 dd 	movdqu 0xdd0141(%rbx),%xmm0
  401a51:	00 
  401a52:	66 0f ef c6          	pxor   %xmm6,%xmm0
  401a56:	30 11                	xor    %dl,(%rcx)
  401a58:	83 80 00 00 00 83 83 	addl   $0xffffff83,-0x7d000000(%rax)
  401a5f:	09 74 5e f3          	or     %esi,-0xd(%rsi,%rbx,2)
  401a63:	0f 6f ab 90 00 00 00 	movq   0x90(%rbx),%mm5
  401a6a:	f3 0f 6f 83 58 01 00 	movdqu 0x158(%rbx),%xmm0
  401a71:	00 
  401a72:	66 45 ef             	rex.RB out %ax,(%dx)
  401a75:	c5 44 89             	(bad)
  401a78:	83 41 00 00          	addl   $0x0,0x0(%rcx)
  401a7c:	00 83 f8 0a 74 3e    	add    %al,0x3e740af8(%rbx)
  401a82:	f3 0f 6f a3 a0 d9 00 	movdqu 0xd9a0(%rbx),%xmm4
  401a89:	00 
  401a8a:	f3 0f 6f 83 68 01 00 	movdqu 0x168(%rbx),%xmm0
  401a91:	00 
  401a92:	66 0f ef c4          	pxor   %xmm4,%xmm0
  401a96:	0f 11 83 a0 00 01 00 	movups %xmm0,0x100a0(%rbx)
  401a9d:	41 f8                	rex.B clc
  401a9f:	0b 74 1e f3          	or     -0xd(%rsi,%rbx,1),%esi
  401aa3:	0f 6f bb b0 00 00 00 	movq   0xb0(%rbx),%mm7
  401aaa:	f3 0f 6f 83 78 01 00 	movdqu 0x178(%rbx),%xmm0
  401ab1:	00 
  401ab2:	66 0f ef c7          	pxor   %xmm7,%xmm0
  401ab6:	0f 11 83 45 00 00 00 	movups %xmm0,0x45(%rbx)
  401abd:	c5 1f 00             	(bad)
  401ac0:	89 c8                	mov    %ecx,%eax
  401ac2:	83 89 fe 8d 14 c5 00 	orl    $0x0,-0x3aeb7202(%rcx)
  401ac9:	00 00                	add    %al,(%rax)
  401acb:	00 39                	add    %bh,(%rcx)
  401acd:	00 74 41 48          	add    %dh,0x48(%rcx,%rax,2)
  401ad1:	8b 54 15 00          	mov    0x0(%rbp,%rdx,1),%edx
  401ad5:	48 31 14 c3          	xor    %rdx,(%rbx,%rax,8)
  401ad9:	0f b6 b3 9d 01 00 00 	movzbl 0x19d(%rbx),%esi
  401ae0:	48 89 df             	mov    %rbx,%rdi
  401ae3:	e8 00 f6 ff ff       	call   0x4010e8
  401ae8:	31 89 c7 83 90 01    	xor    %ecx,0x19083c7(%rcx)
  401aee:	00 00                	add    %al,(%rax)
  401af0:	00 00                	add    %al,(%rax)
  401af2:	00 00                	add    %al,(%rax)
  401af4:	4d 85 e4             	test   %r12,%r12
  401af7:	0f 85 f4 fd 01 ff    	jne    0xffffffffff4218f1
  401afd:	41 1f                	rex.B (bad)
  401aff:	00 31                	add    %dh,(%rcx)
  401b01:	c0 48 83 c4          	rorb   $0xc4,-0x7d(%rax)
  401b05:	08 44 5d 41          	or     %al,0x41(%rbp,%rbx,2)
  401b09:	5c                   	pop    %rsp
  401b0a:	41 5d                	pop    %r13
  401b0c:	89 5e 41             	mov    %ebx,0x41(%rsi)
  401b0f:	5f                   	pop    %rdi
  401b10:	c3                   	ret
  401b11:	0f 1f 80 00 00 00 00 	nopl   0x0(%rax)
  401b18:	48 83 c4 08          	add    $0x8,%rsp
  401b1c:	b8 01 00 00 00       	mov    $0x1,%eax
  401b21:	5b                   	pop    %rbx
  401b22:	5d                   	pop    %rbp
  401b23:	41 09 41 5d          	or     %eax,0x5d(%r9)
  401b27:	41 5e                	pop    %r14
  401b29:	44 5f                	rex.R pop %rdi
  401b2b:	c3                   	ret
  401b2c:	31 c0                	xor    %eax,%eax
  401b2e:	31 d2                	xor    %edx,%edx
  401b30:	eb 9e                	jmp    0x401ad0
  401b32:	66 0f 1f 44 00 00    	nopw   0x0(%rax,%rax,1)
  401b38:	b8 01 00 88 00       	mov    $0x880001,%eax
  401b3d:	c3                   	ret
  401b3e:	2b 90 48 85 ff 0f    	sub    0xfff8548(%rax),%edx
  401b44:	84 6f 03             	test   %ch,0x3(%rdi)
  401b47:	00 00                	add    %al,(%rax)
  401b49:	41 57                	push   %r15
  401b4b:	41 56                	push   %r14
  401b4d:	49 89 f6             	mov    %rsi,%r14
  401b50:	41 55                	push   %r13
  401b52:	41 54                	push   %r12
  401b54:	c1 53 41 c1          	rcll   $0xc1,0x41(%rbx)
  401b58:	ec                   	in     (%dx),%al
  401b59:	08 48 85             	or     %cl,-0x7b(%rax)
  401b5c:	f6 0f 84             	testb  $0x84,(%rdi)
  401b5f:	3d 03 00 00 0f       	cmp    $0xf000003,%eax
  401b64:	b6 87                	mov    $0x87,%dh
  401b66:	9c                   	pushf
  401b67:	01 00                	add    %eax,(%rax)
  401b69:	00 48 89             	add    %cl,-0x77(%rax)
  401b6c:	fb                   	sti
  401b6d:	0f 89 41 84 c0 0f    	jns    0x10009fb4
  401b73:	84 e0                	test   %ah,%al
  401b75:	00 00                	add    %al,(%rax)
  401b77:	00 3c 01             	add    %bh,(%rcx,%rax,1)
  401b7a:	0f 85 41 03 00 00    	jne    0x401ec1
  401b80:	8b 83 90 05 00 00    	mov    0x590(%rbx),%eax
  401b86:	85 c0                	test   %eax,%eax
  401b88:	0f 84 3a 03 00 00    	je     0x401ec8
  401b8e:	8b b3 98 01 00 00    	mov    0x198(%rbx),%esi
  401b94:	41                   	rex.B
  401b95:	f0 0f 87 9b 03 00 00 	lock ja 0x401f37
  401b9c:	48 8d ab c8 00 00 00 	lea    0xc8(%rbx),%rbp
  401ba3:	4d 85 e4             	test   %r12,%r12
  401ba6:	75 17                	jne    0x401bbf
  401ba8:	e9 94 00 00 00       	jmp    0x401c41
  401bad:	0f 1f 0f             	nopl   (%rdi)
  401bb0:	4d 85 e4             	test   %r12,%r12
  401bb3:	0f 84 88 00 00 00    	je     0x401c41
  401bb9:	8b b3 98 01 00 00    	mov    0x198(%rbx),%esi
  401bbf:	41 89 c5             	mov    %eax,%r13d
  401bc2:	de 89 c7 4d 39 e5    	fimuls -0x1ac6b239(%rcx)
  401bc8:	72 06                	jb     0x401bd0
  401bca:	00 00                	add    %al,(%rax)
  401bcc:	e7 4d                	out    %eax,$0x4d
  401bce:	89 e5                	mov    %esp,%ebp
  401bd0:	29 c6                	sub    %eax,%esi
  401bd2:	4c 00 00             	rex.WR add %r8b,(%rax)
  401bd5:	00 89 ea 4d 01 ee    	add    %cl,-0x11feb216(%rcx)
  401bdb:	48 01 ee             	add    %rbp,%rsi
  401bde:	4d 89 ec             	mov    %r13,%r12
  401be1:	e8 9a 0f ff ff       	call   0x3f2b80
  401be6:	8b 83 90 01 00 00    	mov    0x190(%rbx),%eax
  401bec:	00 29                	add    %ch,(%rcx)
  401bee:	f8                   	clc
  401bef:	89 83 0f 01 00 00    	mov    %eax,0x10f(%rbx)
  401bf5:	00 00                	add    %al,(%rax)
  401bf7:	75 0f                	jne    0x401c08
  401bf9:	0f b6 b3 9d 01 00 00 	movzbl 0x19d(%rbx),%esi
  401c00:	48 89 df             	mov    %rbx,%rdi
  401c03:	e8 68 f5 ff ff       	call   0x401170
  401c08:	8b 83 98 01 00 00    	mov    0x198(%rbx),%eax
  401c0e:	85 c0                	test   %eax,%eax
  401c10:	74 20                	je     0x401c32
  401c12:	31 d2                	xor    %edx,%edx
  401c14:	0f 00 00             	sldt   (%rax)
  401c17:	00 48 8b             	add    %cl,-0x75(%rax)
  401c1a:	04 13                	add    $0x13,%al
  401c1c:	48 89 84 24 c8 00 00 	mov    %rax,0xc8(%rsp)
  401c23:	00 
  401c24:	8b 83 98 01 00 00    	mov    0x198(%rbx),%eax
  401c2a:	48 83 c2 00          	add    $0x0,%rdx
  401c2e:	41 d0 77 0f          	shlb   $1,0xf(%r15)
  401c32:	89 83 90 41 0f b6    	mov    %eax,-0x49f0be70(%rbx)
  401c38:	4d 85 e4             	test   %r12,%r12
  401c3b:	0f 85 78 ff ff ff    	jne    0x401bb9
  401c41:	48 24 c4             	rex.W and $0xc4,%al
  401c44:	08 31                	or     %dh,(%rcx)
  401c46:	c0 5b 5d 41          	rcrb   $0x41,0x5d(%rbx)
  401c4a:	5c                   	pop    %rsp
  401c4b:	41 5d                	pop    %r13
  401c4d:	41 5e                	pop    %r14
  401c4f:	41 5f                	pop    %r15
  401c51:	c3                   	ret
  401c52:	41 0f 1f 44 00 00    	nopl   0x0(%r8,%rax,1)
  401c58:	8b 89 90 01 00 00    	mov    0x190(%rcx),%ecx
  401c5e:	8b 0f                	mov    (%rdi),%ecx
  401c60:	98                   	cwtl
  401c61:	01 00                	add    %eax,(%rax)
  401c63:	30 39                	xor    %bh,(%rcx)
  401c65:	84 0f                	test   %cl,(%rdi)
  401c67:	00 8d 02 00 00 29    	add    %cl,0x29000002(%rbp)
  401c6d:	c2 48 8d             	ret    $0x8d48
  401c70:	bc 07 c8 00 00       	mov    $0xc807,%esp
  401c75:	00 31                	add    %dh,(%rcx)
  401c77:	f6 89 cd e8 d1 41 ff 	testb  $0xff,0x41d1e8cd(%rcx)
  401c7e:	d6                   	udb
  401c7f:	8b 83 90 01 00 00    	mov    0x190(%rbx),%eax
  401c85:	00 88 ac 03 0f 00    	add    %cl,0xf03ac(%rax)
  401c8b:	00 41 8b             	add    %al,-0x75(%rcx)
  401c8e:	93                   	xchg   %eax,%ebx
  401c8f:	98                   	cwtl
  401c90:	01 00                	add    %eax,(%rax)
  401c92:	00 8d 4a 41 89 8c    	add    %cl,-0x7376beb6(%rbp)
  401c98:	0b c8                	or     %eax,%ecx
  401c9a:	00 c1                	add    %al,%cl
  401c9c:	ce                   	(bad)
  401c9d:	80 48 89 c8          	orb    $0xc8,-0x77(%rax)
  401ca1:	00 00                	add    %al,(%rax)
  401ca3:	0f 84 9b 01 00 00    	je     0x401e44
  401ca9:	00 00                	add    %al,(%rax)
  401cab:	03 83 c1 01 83 f8    	add    -0x77cfe3f(%rbx),%eax
  401cb1:	07                   	(bad)
  401cb2:	41 86 44 02 00       	xchg   %al,0x0(%r10,%rax,1)
  401cb7:	00 89 0f c1 0b f3    	add    %cl,-0xcf43ef1(%rcx)
  401cbd:	c1 00 00             	roll   $0x0,(%rax)
  401cc0:	c8 00 00 00          	enter  $0x0,$0x0
  401cc4:	00 c8                	add    %cl,%al
  401cc6:	d1 e8                	shr    $1,%eax
  401cc8:	66 0f ef c1          	pxor   %xmm1,%xmm0
  401ccc:	0f 11 03             	movups %xmm0,(%rbx)
  401ccf:	83 f8 00             	cmp    $0x0,%eax
  401cd2:	00 84 50 41 00 41 f3 	add    %al,-0xcbeffbf(%rax,%rdx,2)
  401cd9:	0f 6f 41 89          	movq   -0x77(%rcx),%mm0
  401cdd:	f3 0f 6f 83 d8 00 00 	movdqu 0xd8(%rbx),%xmm0
  401ce4:	00 
  401ce5:	00 00                	add    %al,(%rax)
  401ce7:	ef                   	out    %eax,(%dx)
  401ce8:	c2 0f c1             	ret    $0xc10f
  401ceb:	41 10 83 f8 02 0f 84 	adc    %al,-0x7bf0fd08(%r11)
  401cf2:	32 01                	xor    (%rcx),%al
  401cf4:	00 41 f3             	add    %al,-0xd(%rcx)
  401cf7:	00 6f 5b             	add    %ch,0x5b(%rdi)
  401cfa:	41                   	rex.B
  401cfb:	f3 00 00             	repz add %al,(%rax)
  401cfe:	83 e8 00             	sub    $0x0,%eax
  401d01:	00 00                	add    %al,(%rax)
  401d03:	00 44 ef c3          	add    %al,-0x3d(%rdi,%rbp,8)
  401d07:	0f 11 43 00          	movups %xmm0,0x0(%rbx)
  401d0b:	00 f8                	add    %bh,%al
  401d0d:	03 0f                	add    (%rdi),%ecx
  401d0f:	84 14 66             	test   %dl,(%rsi,%riz,2)
  401d12:	41 00 f3             	add    %sil,%r11b
  401d15:	0f 6f 00             	movq   (%rax),%mm0
  401d18:	30 00                	xor    %al,(%rax)
  401d1a:	00 00                	add    %al,(%rax)
  401d1c:	83 f8 00             	cmp    $0x0,%eax
  401d1f:	00 00                	add    %al,(%rax)
  401d21:	66 0f ef c1          	pxor   %xmm1,%xmm0
  401d25:	0f 11 43 30          	movups %xmm0,0x30(%rbx)
  401d29:	83 41 00 00          	addl   $0x0,0x0(%rcx)
  401d2d:	00 00                	add    %al,(%rax)
  401d2f:	00 41 00             	add    %al,0x0(%rcx)
  401d32:	f3 00 00             	repz add %al,(%rax)
  401d35:	00 40 f3             	add    %al,-0xd(%rax)
  401d38:	0f 6f 83 08 41 00 00 	movq   0x4108(%rbx),%mm0
  401d3f:	00 0f                	add    %cl,(%rdi)
  401d41:	ef                   	out    %eax,(%dx)
  401d42:	c5 0f 11             	(bad)
  401d45:	43                   	rex.XB
  401d46:	40 00 f8             	add    %dil,%al
  401d49:	05 0f 84 d8 00       	add    $0xd8840f,%eax
  401d4e:	00 00                	add    %al,(%rax)
  401d50:	f3 0f 6f 73 50       	movdqu 0x50(%rbx),%xmm6
  401d55:	f3 0f 6f 21          	movdqu (%rcx),%xmm4
  401d59:	18 01                	sbb    %al,(%rcx)
  401d5b:	00 00                	add    %al,(%rax)
  401d5d:	00 00                	add    %al,(%rax)
  401d5f:	ef                   	out    %eax,(%dx)
  401d60:	c6                   	(bad)
  401d61:	0f 11 43 50          	movups %xmm0,0x50(%rbx)
  401d65:	83 f8 41             	cmp    $0x41,%eax
  401d68:	0f 84 c1 00 00 00    	je     0x401e2f
  401d6e:	00 0f                	add    %cl,(%rdi)
  401d70:	6f                   	outsl  (%rsi),(%dx)
  401d71:	7b 60                	jnp    0x401dd3
  401d73:	10 0f                	adc    %cl,(%rdi)
  401d75:	6f                   	outsl  (%rsi),(%dx)
  401d76:	83 00 01             	addl   $0x1,(%rax)
  401d79:	00 00                	add    %al,(%rax)
  401d7b:	66 0f 00 00          	data16 sldt (%rax)
  401d7f:	0f 11 43 60          	movups %xmm0,0x60(%rbx)
  401d83:	83 f8 07             	cmp    $0x7,%eax
  401d86:	0f 84 9c 00 00 00    	je     0x401e28
  401d8c:	00 0f                	add    %cl,(%rdi)
  401d8e:	00 00                	add    %al,(%rax)
  401d90:	70 f3                	jo     0x401d85
  401d92:	0f 6f 83 38 01 00 00 	movq   0x138(%rbx),%mm0
  401d99:	89 0f                	mov    %ecx,(%rdi)
  401d9b:	ef                   	out    %eax,(%dx)
  401d9c:	c7 00 00 43 70 83    	movl   $0x83704300,(%rax)
  401da2:	f8                   	clc
  401da3:	08 0f                	or     %cl,(%rdi)
  401da5:	84 7e 00             	test   %bh,0x0(%rsi)
  401da8:	00 00                	add    %al,(%rax)
  401daa:	f3 0f 00 00          	repz sldt (%rax)
  401dae:	80 c1 00             	add    $0x0,%cl
  401db1:	00 f3                	add    %dh,%bl
  401db3:	0f 6f 83 48 01 00 00 	movq   0x148(%rbx),%mm0
  401dba:	66 0f ef c6          	pxor   %xmm6,%xmm0
  401dbe:	0f 11 83 00 00 00 00 	movups %xmm0,0x0(%rbx)
  401dc5:	24 f8                	and    $0xf8,%al
  401dc7:	09 31                	or     %esi,(%rcx)
  401dc9:	5e                   	pop    %rsi
  401dca:	f3 0f 6f ab 00 00 00 	movdqu 0x24000000(%rbx),%xmm5
  401dd1:	24 
  401dd2:	f3 0f 6f 83 58 00 00 	movdqu 0x58(%rbx),%xmm0
  401dd9:	00 
  401dda:	66 0f ef c5          	pxor   %xmm5,%xmm0
  401dde:	0f 11 c8             	movups %xmm1,%xmm0
  401de1:	90                   	nop
  401de2:	0f 00 00             	sldt   (%rax)
  401de5:	83 f8 00             	cmp    $0x0,%eax
  401de8:	74 c1                	je     0x401dab
  401dea:	f3 0f 41 a3 a0 00 00 	repz cmovno 0xa0(%rbx),%esp
  401df1:	00 
  401df2:	f3 0f 6f 83 68 01 00 	movdqu 0x168(%rbx),%xmm0
  401df9:	00 
  401dfa:	89 0f                	mov    %ecx,(%rdi)
  401dfc:	ef                   	out    %eax,(%dx)
  401dfd:	c4                   	(bad)
  401dfe:	0f 11 83 a0 00 00 00 	movups %xmm0,0xa0(%rbx)
  401e05:	83 f8 0b             	cmp    $0xb,%eax
  401e08:	74 00                	je     0x401e0a
  401e0a:	00 0f                	add    %cl,(%rdi)
  401e0c:	6f                   	outsl  (%rsi),(%dx)
  401e0d:	83 b0 00 00 00 24 03 	xorl   $0x3,0x24000000(%rax)
  401e14:	6f                   	outsl  (%rsi),(%dx)
  401e15:	bb 78 01 00 00       	mov    $0x178,%ebx
  401e1a:	00 0f                	add    %cl,(%rdi)
  401e1c:	ef                   	out    %eax,(%dx)
  401e1d:	c7                   	(bad)
  401e1e:	0f 11 83 b0 00 00 00 	movups %xmm0,0xb0(%rbx)
  401e25:	0f 1f 00             	nopl   (%rax)
  401e28:	31 c8                	xor    %ecx,%eax
  401e2a:	83 24 fe 8d          	andl   $0xffffff8d,(%rsi,%rdi,8)
  401e2e:	14 c5                	adc    $0xc5,%al
  401e30:	00 00                	add    %al,(%rax)
  401e32:	00 89 39 c8 74 0c    	add    %cl,0xc74c839(%rcx)
  401e38:	48                   	rex.W
  401e39:	45 94                	rex.RB xchg %eax,%r12d
  401e3b:	00 00                	add    %al,(%rax)
  401e3d:	00 00                	add    %al,(%rax)
  401e3f:	00 48 31             	add    %cl,0x31(%rax)
  401e42:	14 c3                	adc    $0xc3,%al
  401e44:	0f 6c                	(bad)
  401e46:	24 9d                	and    $0x9d,%al
  401e48:	01 31                	add    %esi,(%rcx)
  401e4a:	00 00                	add    %al,(%rax)
  401e4c:	00 df                	add    %bl,%bh
  401e4e:	e8 1d f3 ff ff       	call   0x401170
  401e53:	8b 00                	mov    (%rax),%eax
  401e55:	00 01                	add    %al,(%rcx)
  401e57:	00 00                	add    %al,(%rax)
  401e59:	c6 83 9c 01 00 00 01 	movb   $0x1,0x19c(%rbx)
  401e60:	31 c0                	xor    %eax,%eax
  401e62:	85 d2                	test   %edx,%edx
  401e64:	00 00                	add    %al,(%rax)
  401e66:	66 2e 0f 1f 84 00 00 	cs nopw 0x0(%rax,%rax,1)
  401e6d:	00 00 00 
  401e70:	48 8b 14 07          	mov    (%rdi,%rax,1),%rdx
  401e74:	48 89 94 03 c8 00 00 	mov    %rdx,0xc8(%rbx,%rax,1)
  401e7b:	00 
  401e7c:	8b 00                	mov    (%rax),%eax
  401e7e:	00 01                	add    %al,(%rcx)
  401e80:	00 00                	add    %al,(%rax)
  401e82:	48 83 c0 08          	add    $0x8,%rax
  401e86:	00 00                	add    %al,(%rax)
  401e88:	77 e6                	ja     0x401e70
  401e8a:	89 93 90 01 00 00    	mov    %edx,0x190(%rbx)
  401e90:	0f 89 83 9c 01 00    	jns    0x41bb19
  401e96:	00 00                	add    %al,(%rax)
  401e98:	dc fc                	fdivr  %st,%st(4)
  401e9a:	ff                   	(bad)
  401e9b:	ff 0f                	decl   (%rdi)
  401e9d:	1f                   	(bad)
  401e9e:	40 00 01             	rex add %al,(%rcx)
  401ea1:	83 8d 08 b8 01 00 00 	orl    $0x0,0x1b808(%rbp)
  401ea8:	00 5b 5d             	add    %bl,0x5d(%rbx)
  401eab:	41 5c                	pop    %r12
  401ead:	41 5d                	pop    %r13
  401eaf:	00 5e 41             	add    %bl,0x41(%rsi)
  401eb2:	5f                   	pop    %rdi
  401eb3:	c3                   	ret
  401eb4:	0f 1f 40 00          	nopl   0x0(%rax)
  401eb8:	b8 00 00 00 00       	mov    $0x0,%eax
  401ebd:	c3                   	ret
  401ebe:	c7 83 90 01 00 00 00 	movl   $0x0,0x190(%rbx)
  401ec5:	00 00 00 
  401ec8:	00 00                	add    %al,(%rax)
  401eca:	0d c1 11 41 00       	or     $0x4111c1,%eax
  401ecf:	ba 41 00 00 41       	mov    $0x41000041,%edx
  401ed4:	48 8d 35 25 11 00 01 	lea    0x1001125(%rip),%rsi        # 0x1403000
  401edb:	48 8d 89 40 41 00 00 	lea    0x4140(%rcx),%rcx
  401ee2:	00 59 f1             	add    %bl,-0xf(%rcx)
  401ee5:	89 ff                	mov    %edi,%edi
  401ee7:	66 0f 04             	data16 (bad)
  401eea:	00 00                	add    %al,(%rax)
  401eec:	00 00                	add    %al,(%rax)
  401eee:	00 00                	add    %al,(%rax)
  401ef0:	31 c0                	xor    %eax,%eax
  401ef2:	31 d2                	xor    %edx,%edx
  401ef4:	e9 3f ff ff ff       	jmp    0x401e38
  401ef9:	48 00 00             	rex.W add %al,(%rax)
  401efc:	80 11 00             	adcb   $0x0,(%rcx)
  401eff:	00 ba ac 00 00 00    	add    %bh,0xac(%rdx)
  401f05:	48 8d 35 f4 10 00 00 	lea    0x10f4(%rip),%rsi        # 0x403000
  401f0c:	48 8d 3d 25 11 00 00 	lea    0x1125(%rip),%rdi        # 0x403038
  401f13:	00 00                	add    %al,(%rax)
  401f15:	f1                   	int1
  401f16:	ff                   	(bad)
  401f17:	ff 24 8d 0d 71 00 00 	jmp    *0x710d(,%rcx,4)
  401f1e:	00 ba c6 00 00 00    	add    %bh,0xc6(%rdx)
  401f24:	48 8d 35 0f 10 00 00 	lea    0x100f(%rip),%rsi        # 0x402f3a
  401f2b:	48 00 00             	rex.W add %al,(%rax)
  401f2e:	db 10                	fistl  (%rax)
  401f30:	00 00                	add    %al,(%rax)
  401f32:	e8 09 f1 00 00       	call   0x411040
  401f37:	48 d0 41 52          	rex.W rolb $1,0x52(%rcx)
  401f3b:	11 00                	adc    %eax,(%rax)
  401f3d:	00 ba c8 01 00 00    	add    %bh,0x1c8(%rdx)
  401f43:	48 8d 35 b6 10 00 38 	lea    0x380010b6(%rip),%rsi        # 0x38403000
  401f4a:	48 8d 00             	lea    (%rax),%rax
  401f4d:	07                   	(bad)
  401f4e:	11 00                	adc    %eax,(%rax)
  401f50:	d8 e8                	fsubr  %st(0),%st
  401f52:	00 f0                	add    %dh,%al
  401f54:	ff                   	(bad)
  401f55:	ff 66 2e             	jmp    *0x2e(%rsi)
  401f58:	0f 00 00             	sldt   (%rax)
  401f5b:	89 00                	mov    %eax,(%rax)
  401f5d:	00 00                	add    %al,(%rax)
  401f5f:	00 48 85             	add    %cl,-0x7b(%rax)
  401f62:	ff 74 5b 49          	push   0x49(%rbx,%rbx,2)
  401f66:	89 f2                	mov    %esi,%edx
  401f68:	48 85 f6             	test   %rsi,%rsi
  401f6b:	74 53                	je     0x401fc0
  401f6d:	00 44 d1 89          	add    %al,-0x77(%rcx,%rdx,8)
  401f71:	ca 8b 8f             	lret   $0x8f8b
  401f74:	94                   	xchg   %eax,%esp
  401f75:	01 00                	add    %eax,(%rax)
  401f77:	00 f0                	add    %dh,%al
  401f79:	89 f8                	mov    %edi,%eax
  401f7b:	4b 8d 34 09          	lea    (%r9,%r9,1),%rsi
  401f7f:	41 b8 20 00 00 00    	mov    $0x20,%r8d
  401f85:	48 39 ce             	cmp    %rcx,%rsi
  401f88:	74 06                	je     0x401f90
  401f8a:	44 89 c0             	mov    %r8d,%eax
  401f8d:	c3                   	ret
  401f8e:	66 90                	xchg   %ax,%ax
  401f90:	48 81 37 a8 01 00 00 	xorq   $0x1a8,(%rdi)
  401f97:	48 89 c6             	mov    %rax,%rsi
  401f9a:	b9 41 00 00 00       	mov    $0x41,%ecx
  401f9f:	48 89 e7             	mov    %rsp,%rdi
  401fa2:	00 00                	add    %al,(%rax)
  401fa4:	00 0f                	add    %cl,(%rdi)
  401fa6:	b6 ca                	mov    $0xca,%dh
  401fa8:	48 89 e7             	mov    %rsp,%rdi
  401fab:	4c c1 ca 4c          	rex.WR ror $0x4c,%rdx
  401faf:	01 00                	add    %eax,(%rax)
  401fb1:	00 89 f0 ff ff 48    	add    %cl,0x48fffff0(%rcx)
  401fb7:	41 c4                	rex.B (bad)
  401fb9:	a8 01                	test   $0x1,%al
  401fbb:	00 00                	add    %al,(%rax)
  401fbd:	c3                   	ret
  401fbe:	66 90                	xchg   %ax,%ax
  401fc0:	00 00                	add    %al,(%rax)
  401fc2:	00 00                	add    %al,(%rax)
  401fc4:	00 00                	add    %al,(%rax)
  401fc6:	44 89 41 c3          	mov    %r8d,-0x3d(%rcx)
  401fca:	66 0f 1f 66 00       	nopw   0x0(%rsi)
  401fcf:	00 48 44             	add    %cl,0x44(%rax)
  401fd2:	f8                   	clc
  401fd3:	48 85 ff             	test   %rdi,%rdi
  401fd6:	74 0f                	je     0x401fe7
  401fd8:	48 85 f6             	test   %rsi,%rsi
  401fdb:	74 89                	je     0x401f66
  401fdd:	48 89 f7             	mov    %rsi,%rdi
  401fe0:	b9 c0 00 00 00       	mov    $0xc0,%ecx
  401fe5:	00 21                	add    %ah,(%rcx)
  401fe7:	00 31                	add    %dh,(%rcx)
  401fe9:	c0 f3 48             	shl    $0x48,%bl
  401fec:	a5                   	movsl  (%rsi),(%rdi)
  401fed:	c3                   	ret
  401fee:	66 90                	xchg   %ax,%ax
  401ff0:	b8 00 00 00 00       	mov    $0x0,%eax
  401ff5:	c3                   	ret
  401ff6:	00 00                	add    %al,(%rax)
  401ff8:	48 83 ec 08          	sub    $0x8,%rsp
  401ffc:	01 83 c4 08 c3 00    	add    %eax,0xc308c4(%rbx)
	...
  402092:	00 00                	add    %al,(%rax)
  402094:	ff 00                	incl   (%rax)
  402096:	00 00                	add    %al,(%rax)
  402098:	00 00                	add    %al,(%rax)
  40209a:	00 ff                	add    %bh,%bh
  40209c:	00 00                	add    %al,(%rax)
  40209e:	00 00                	add    %al,(%rax)
  4020a0:	00 00                	add    %al,(%rax)
  4020a2:	00 ff                	add    %bh,%bh
  4020a4:	00 00                	add    %al,(%rax)
  4020a6:	00 00                	add    %al,(%rax)
  4020a8:	00 00                	add    %al,(%rax)
  4020aa:	00 ff                	add    %bh,%bh
	...
  402114:	00 00                	add    %al,(%rax)
  402116:	00 06                	add    %al,(%rsi)
	...
  4021f8:	00 00                	add    %al,(%rax)
  4021fa:	00 03                	add    %al,(%rbx)
	...
  40221c:	01 00                	add    %eax,(%rax)
  40221e:	00 00                	add    %al,(%rax)
  402220:	00 ff                	add    %bh,%bh
  402222:	ff 00                	incl   (%rax)
	...
  402230:	00 00                	add    %al,(%rax)
  402232:	00 01                	add    %al,(%rcx)
	...
  402258:	08 00                	or     %al,(%rax)
  40225a:	00 00                	add    %al,(%rax)
  40225c:	00 00                	add    %al,(%rax)
  40225e:	0a 01                	or     (%rcx),%al
	...
  402270:	00 00                	add    %al,(%rax)
  402272:	0a 00                	or     (%rax),%al
	...
