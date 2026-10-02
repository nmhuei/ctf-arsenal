
script/offline_audit/collector_code_3410a040.bin:     file format binary


Disassembly of section .data:

0000000000401300 <.data+0x300>:
  401300:	09 ec                	or     esp,ebp
  401302:	44 2b a7 00 01 00 00 	sub    r12d,DWORD PTR [rdi+0x100]
  401309:	41 29 d4             	sub    r12d,edx
  40130c:	44 89 da             	mov    edx,r11d
  40130f:	f7 d2                	not    edx
  401311:	21 da                	and    edx,ebx
  401313:	41 29 d4             	sub    r12d,edx
  401316:	44 89 da             	mov    edx,r11d
  401319:	41 c1 e3 0b          	shl    r11d,0xb
  40131d:	66 c1 ea 05          	shr    dx,0x5
  401321:	44 89 e5             	mov    ebp,r12d
  401324:	0f b7 d2             	movzx  edx,dx
  401327:	44 09 da             	or     edx,r11d
  40132a:	41 89 c3             	mov    r11d,eax
  40132d:	2b 97 fc 00 00 00    	sub    edx,DWORD PTR [rdi+0xfc]
  401333:	41 21 db             	and    r11d,ebx
  401336:	44 29 da             	sub    edx,r11d
  401339:	41 89 c3             	mov    r11d,eax
  40133c:	41 f7 d3             	not    r11d
  40133f:	45 21 e3             	and    r11d,r12d
  401342:	44 29 da             	sub    edx,r11d
  401345:	41 89 c3             	mov    r11d,eax
  401348:	c1 e0 0d             	shl    eax,0xd
  40134b:	66 41 c1 eb 03       	shr    r11w,0x3
  401350:	45 0f b7 db          	movzx  r11d,r11w
  401354:	41 09 c3             	or     r11d,eax
  401357:	89 d8                	mov    eax,ebx
  401359:	44 2b 9f f8 00 00 00 	sub    r11d,DWORD PTR [rdi+0xf8]
  401360:	44 21 e0             	and    eax,r12d
  401363:	41 29 c3             	sub    r11d,eax
  401366:	89 d8                	mov    eax,ebx
  401368:	f7 d0                	not    eax
  40136a:	21 d0                	and    eax,edx
  40136c:	41 29 c3             	sub    r11d,eax
  40136f:	89 d8                	mov    eax,ebx
  401371:	c1 e3 0e             	shl    ebx,0xe
  401374:	66 c1 e8 02          	shr    ax,0x2
  401378:	0f b7 c0             	movzx  eax,ax
  40137b:	09 d8                	or     eax,ebx
  40137d:	44 89 e3             	mov    ebx,r12d
  401380:	2b 87 f4 00 00 00    	sub    eax,DWORD PTR [rdi+0xf4]
  401386:	21 d3                	and    ebx,edx
  401388:	29 d8                	sub    eax,ebx
  40138a:	44 89 e3             	mov    ebx,r12d
  40138d:	f7 d3                	not    ebx
  40138f:	44 21 db             	and    ebx,r11d
  401392:	29 d8                	sub    eax,ebx
  401394:	66 d1 ed             	shr    bp,1
  401397:	89 d3                	mov    ebx,edx
  401399:	41 c1 e4 0f          	shl    r12d,0xf
  40139d:	0f b7 ed             	movzx  ebp,bp
  4013a0:	44 21 db             	and    ebx,r11d
  4013a3:	44 09 e5             	or     ebp,r12d
  4013a6:	2b af f0 00 00 00    	sub    ebp,DWORD PTR [rdi+0xf0]
  4013ac:	29 dd                	sub    ebp,ebx
  4013ae:	89 d3                	mov    ebx,edx
  4013b0:	f7 d3                	not    ebx
  4013b2:	21 c3                	and    ebx,eax
  4013b4:	29 dd                	sub    ebp,ebx
  4013b6:	89 d3                	mov    ebx,edx
  4013b8:	c1 e2 0b             	shl    edx,0xb
  4013bb:	66 c1 eb 05          	shr    bx,0x5
  4013bf:	41 89 ec             	mov    r12d,ebp
  4013c2:	0f b7 db             	movzx  ebx,bx
  4013c5:	09 d3                	or     ebx,edx
  4013c7:	44 89 da             	mov    edx,r11d
  4013ca:	2b 9f ec 00 00 00    	sub    ebx,DWORD PTR [rdi+0xec]
  4013d0:	21 c2                	and    edx,eax
  4013d2:	29 d3                	sub    ebx,edx
  4013d4:	44 89 da             	mov    edx,r11d
  4013d7:	f7 d2                	not    edx
  4013d9:	21 ea                	and    edx,ebp
  4013db:	29 d3                	sub    ebx,edx
  4013dd:	44 89 da             	mov    edx,r11d
  4013e0:	41 c1 e3 0d          	shl    r11d,0xd
  4013e4:	66 c1 ea 03          	shr    dx,0x3
  4013e8:	0f b7 d2             	movzx  edx,dx
  4013eb:	44 09 da             	or     edx,r11d
  4013ee:	41 89 c3             	mov    r11d,eax
  4013f1:	2b 97 e8 00 00 00    	sub    edx,DWORD PTR [rdi+0xe8]
  4013f7:	41 21 eb             	and    r11d,ebp
  4013fa:	44 29 da             	sub    edx,r11d
  4013fd:	41 89 c3             	mov    r11d,eax
  401400:	41 f7 d3             	not    r11d
  401403:	41 21 db             	and    r11d,ebx
  401406:	44 29 da             	sub    edx,r11d
  401409:	41 89 c3             	mov    r11d,eax
  40140c:	c1 e0 0e             	shl    eax,0xe
  40140f:	66 41 c1 eb 02       	shr    r11w,0x2
  401414:	45 0f b7 db          	movzx  r11d,r11w
  401418:	41 09 c3             	or     r11d,eax
  40141b:	89 e8                	mov    eax,ebp
  40141d:	44 2b 9f e4 00 00 00 	sub    r11d,DWORD PTR [rdi+0xe4]
  401424:	21 d8                	and    eax,ebx
  401426:	41 29 c3             	sub    r11d,eax
  401429:	89 e8                	mov    eax,ebp
  40142b:	f7 d0                	not    eax
  40142d:	21 d0                	and    eax,edx
  40142f:	41 29 c3             	sub    r11d,eax
  401432:	66 41 d1 ec          	shr    r12w,1
  401436:	89 d8                	mov    eax,ebx
  401438:	c1 e5 0f             	shl    ebp,0xf
  40143b:	45 0f b7 e4          	movzx  r12d,r12w
  40143f:	21 d0                	and    eax,edx
  401441:	41 09 ec             	or     r12d,ebp
  401444:	44 2b a7 e0 00 00 00 	sub    r12d,DWORD PTR [rdi+0xe0]
  40144b:	89 dd                	mov    ebp,ebx
  40144d:	41 29 c4             	sub    r12d,eax
  401450:	89 d8                	mov    eax,ebx
  401452:	66 c1 ed 05          	shr    bp,0x5
  401456:	f7 d0                	not    eax
  401458:	c1 e3 0b             	shl    ebx,0xb
  40145b:	0f b7 ed             	movzx  ebp,bp
  40145e:	44 21 d8             	and    eax,r11d
  401461:	09 dd                	or     ebp,ebx
  401463:	2b af dc 00 00 00    	sub    ebp,DWORD PTR [rdi+0xdc]
  401469:	89 d3                	mov    ebx,edx
  40146b:	41 29 c4             	sub    r12d,eax
  40146e:	89 d0                	mov    eax,edx
  401470:	66 c1 eb 03          	shr    bx,0x3
  401474:	44 21 d8             	and    eax,r11d
  401477:	0f b7 db             	movzx  ebx,bx
  40147a:	29 c5                	sub    ebp,eax
  40147c:	89 d0                	mov    eax,edx
  40147e:	c1 e2 0d             	shl    edx,0xd
  401481:	f7 d0                	not    eax
  401483:	09 d3                	or     ebx,edx
  401485:	2b 9f d8 00 00 00    	sub    ebx,DWORD PTR [rdi+0xd8]
  40148b:	44 89 da             	mov    edx,r11d
  40148e:	44 21 e0             	and    eax,r12d
  401491:	66 c1 ea 02          	shr    dx,0x2
  401495:	29 c5                	sub    ebp,eax
  401497:	44 89 d8             	mov    eax,r11d
  40149a:	0f b7 d2             	movzx  edx,dx
  40149d:	44 21 e0             	and    eax,r12d
  4014a0:	29 c3                	sub    ebx,eax
  4014a2:	44 89 d8             	mov    eax,r11d
  4014a5:	41 c1 e3 0e          	shl    r11d,0xe
  4014a9:	f7 d0                	not    eax
  4014ab:	44 09 da             	or     edx,r11d
  4014ae:	2b 97 d4 00 00 00    	sub    edx,DWORD PTR [rdi+0xd4]
  4014b4:	45 89 e3             	mov    r11d,r12d
  4014b7:	21 e8                	and    eax,ebp
  4014b9:	29 c3                	sub    ebx,eax
  4014bb:	44 89 e0             	mov    eax,r12d
  4014be:	21 e8                	and    eax,ebp
  4014c0:	29 c2                	sub    edx,eax
  4014c2:	44 89 e0             	mov    eax,r12d
  4014c5:	f7 d0                	not    eax
  4014c7:	21 d8                	and    eax,ebx
  4014c9:	29 c2                	sub    edx,eax
  4014cb:	66 41 d1 eb          	shr    r11w,1
  4014cf:	41 0f b7 c3          	movzx  eax,r11w
  4014d3:	41 c1 e4 0f          	shl    r12d,0xf
  4014d7:	41 89 eb             	mov    r11d,ebp
  4014da:	41 21 db             	and    r11d,ebx
  4014dd:	44 09 e0             	or     eax,r12d
  4014e0:	2b 87 d0 00 00 00    	sub    eax,DWORD PTR [rdi+0xd0]
  4014e6:	44 29 d8             	sub    eax,r11d
  4014e9:	41 89 eb             	mov    r11d,ebp
  4014ec:	41 f7 d3             	not    r11d
  4014ef:	41 21 d3             	and    r11d,edx
  4014f2:	44 29 d8             	sub    eax,r11d
  4014f5:	41 89 db             	mov    r11d,ebx
  4014f8:	41 83 e3 3f          	and    r11d,0x3f
  4014fc:	42 2b 2c 99          	sub    ebp,DWORD PTR [rcx+r11*4]
  401500:	41 89 d3             	mov    r11d,edx
  401503:	41 83 e3 3f          	and    r11d,0x3f
  401507:	42 2b 1c 99          	sub    ebx,DWORD PTR [rcx+r11*4]
  40150b:	41 89 c3             	mov    r11d,eax
  40150e:	41 83 e3 3f          	and    r11d,0x3f
  401512:	41 89 dc             	mov    r12d,ebx
  401515:	89 eb                	mov    ebx,ebp
  401517:	42 2b 14 99          	sub    edx,DWORD PTR [rcx+r11*4]
  40151b:	41 89 eb             	mov    r11d,ebp
  40151e:	66 c1 ed 05          	shr    bp,0x5
  401522:	41 83 e3 3f          	and    r11d,0x3f
  401526:	c1 e3 0b             	shl    ebx,0xb
  401529:	0f b7 ed             	movzx  ebp,bp
  40152c:	42 2b 04 99          	sub    eax,DWORD PTR [rcx+r11*4]
  401530:	45 89 e3             	mov    r11d,r12d
  401533:	09 eb                	or     ebx,ebp
  401535:	2b 9f cc 00 00 00    	sub    ebx,DWORD PTR [rdi+0xcc]
  40153b:	41 21 d3             	and    r11d,edx
  40153e:	89 d5                	mov    ebp,edx
  401540:	44 29 db             	sub    ebx,r11d
  401543:	45 89 e3             	mov    r11d,r12d
  401546:	21 c5                	and    ebp,eax
  401548:	41 f7 d3             	not    r11d
  40154b:	41 21 c3             	and    r11d,eax
  40154e:	44 29 db             	sub    ebx,r11d
  401551:	45 89 e3             	mov    r11d,r12d
  401554:	66 41 c1 ec 03       	shr    r12w,0x3
  401559:	41 c1 e3 0d          	shl    r11d,0xd
  40155d:	45 0f b7 e4          	movzx  r12d,r12w
  401561:	45 09 e3             	or     r11d,r12d
  401564:	44 2b 9f c8 00 00 00 	sub    r11d,DWORD PTR [rdi+0xc8]
  40156b:	41 29 eb             	sub    r11d,ebp
  40156e:	89 d5                	mov    ebp,edx
  401570:	f7 d5                	not    ebp
  401572:	21 dd                	and    ebp,ebx
  401574:	41 29 eb             	sub    r11d,ebp
  401577:	89 d5                	mov    ebp,edx
  401579:	c1 e5 0e             	shl    ebp,0xe
  40157c:	66 c1 ea 02          	shr    dx,0x2
  401580:	0f b7 d2             	movzx  edx,dx
  401583:	09 ea                	or     edx,ebp
  401585:	89 c5                	mov    ebp,eax
  401587:	2b 97 c4 00 00 00    	sub    edx,DWORD PTR [rdi+0xc4]
  40158d:	21 dd                	and    ebp,ebx
  40158f:	29 ea                	sub    edx,ebp
  401591:	89 c5                	mov    ebp,eax
  401593:	f7 d5                	not    ebp
  401595:	44 21 dd             	and    ebp,r11d
  401598:	29 ea                	sub    edx,ebp
  40159a:	89 c5                	mov    ebp,eax
  40159c:	66 d1 e8             	shr    ax,1
  40159f:	c1 e5 0f             	shl    ebp,0xf
  4015a2:	0f b7 c0             	movzx  eax,ax
  4015a5:	09 e8                	or     eax,ebp
  4015a7:	44 89 dd             	mov    ebp,r11d
  4015aa:	2b 87 c0 00 00 00    	sub    eax,DWORD PTR [rdi+0xc0]
  4015b0:	21 dd                	and    ebp,ebx
  4015b2:	29 e8                	sub    eax,ebp
  4015b4:	89 dd                	mov    ebp,ebx
  4015b6:	f7 d5                	not    ebp
  4015b8:	21 d5                	and    ebp,edx
  4015ba:	29 e8                	sub    eax,ebp
  4015bc:	89 dd                	mov    ebp,ebx
  4015be:	66 c1 eb 05          	shr    bx,0x5
  4015c2:	c1 e5 0b             	shl    ebp,0xb
  4015c5:	0f b7 db             	movzx  ebx,bx
  4015c8:	09 eb                	or     ebx,ebp
  4015ca:	89 d5                	mov    ebp,edx
  4015cc:	2b 9f bc 00 00 00    	sub    ebx,DWORD PTR [rdi+0xbc]
  4015d2:	44 21 dd             	and    ebp,r11d
  4015d5:	29 eb                	sub    ebx,ebp
  4015d7:	44 89 dd             	mov    ebp,r11d
  4015da:	f7 d5                	not    ebp
  4015dc:	21 c5                	and    ebp,eax
  4015de:	29 eb                	sub    ebx,ebp
  4015e0:	44 89 dd             	mov    ebp,r11d
  4015e3:	66 41 c1 eb 03       	shr    r11w,0x3
  4015e8:	c1 e5 0d             	shl    ebp,0xd
  4015eb:	45 0f b7 db          	movzx  r11d,r11w
  4015ef:	41 09 eb             	or     r11d,ebp
  4015f2:	89 c5                	mov    ebp,eax
  4015f4:	44 2b 9f b8 00 00 00 	sub    r11d,DWORD PTR [rdi+0xb8]
  4015fb:	21 d5                	and    ebp,edx
  4015fd:	41 29 eb             	sub    r11d,ebp
  401600:	89 d5                	mov    ebp,edx
  401602:	f7 d5                	not    ebp
  401604:	21 dd                	and    ebp,ebx
  401606:	41 29 eb             	sub    r11d,ebp
  401609:	89 d5                	mov    ebp,edx
  40160b:	c1 e5 0e             	shl    ebp,0xe
  40160e:	66 c1 ea 02          	shr    dx,0x2
  401612:	0f b7 d2             	movzx  edx,dx
  401615:	09 ea                	or     edx,ebp
  401617:	89 dd                	mov    ebp,ebx
  401619:	2b 97 b4 00 00 00    	sub    edx,DWORD PTR [rdi+0xb4]
  40161f:	21 c5                	and    ebp,eax
  401621:	29 ea                	sub    edx,ebp
  401623:	89 c5                	mov    ebp,eax
  401625:	f7 d5                	not    ebp
  401627:	44 21 dd             	and    ebp,r11d
  40162a:	29 ea                	sub    edx,ebp
  40162c:	89 c5                	mov    ebp,eax
  40162e:	66 d1 e8             	shr    ax,1
  401631:	c1 e5 0f             	shl    ebp,0xf
  401634:	0f b7 c0             	movzx  eax,ax
  401637:	09 e8                	or     eax,ebp
  401639:	44 89 dd             	mov    ebp,r11d
  40163c:	2b 87 b0 00 00 00    	sub    eax,DWORD PTR [rdi+0xb0]
  401642:	21 dd                	and    ebp,ebx
  401644:	29 e8                	sub    eax,ebp
  401646:	89 dd                	mov    ebp,ebx
  401648:	f7 d5                	not    ebp
  40164a:	21 d5                	and    ebp,edx
  40164c:	29 e8                	sub    eax,ebp
  40164e:	89 dd                	mov    ebp,ebx
  401650:	66 c1 eb 05          	shr    bx,0x5
  401654:	c1 e5 0b             	shl    ebp,0xb
  401657:	0f b7 db             	movzx  ebx,bx
  40165a:	09 eb                	or     ebx,ebp
  40165c:	89 d5                	mov    ebp,edx
  40165e:	2b 9f ac 00 00 00    	sub    ebx,DWORD PTR [rdi+0xac]
  401664:	44 21 dd             	and    ebp,r11d
  401667:	29 eb                	sub    ebx,ebp
  401669:	44 89 dd             	mov    ebp,r11d
  40166c:	f7 d5                	not    ebp
  40166e:	21 c5                	and    ebp,eax
  401670:	29 eb                	sub    ebx,ebp
  401672:	44 89 dd             	mov    ebp,r11d
  401675:	66 41 c1 eb 03       	shr    r11w,0x3
  40167a:	c1 e5 0d             	shl    ebp,0xd
  40167d:	45 0f b7 db          	movzx  r11d,r11w
  401681:	41 09 eb             	or     r11d,ebp
  401684:	89 c5                	mov    ebp,eax
  401686:	44 2b 9f a8 00 00 00 	sub    r11d,DWORD PTR [rdi+0xa8]
  40168d:	21 d5                	and    ebp,edx
  40168f:	41 29 eb             	sub    r11d,ebp
  401692:	89 d5                	mov    ebp,edx
  401694:	f7 d5                	not    ebp
  401696:	21 dd                	and    ebp,ebx
  401698:	41 29 eb             	sub    r11d,ebp
  40169b:	89 d5                	mov    ebp,edx
  40169d:	c1 e5 0e             	shl    ebp,0xe
  4016a0:	66 c1 ea 02          	shr    dx,0x2
  4016a4:	0f b7 d2             	movzx  edx,dx
  4016a7:	09 ea                	or     edx,ebp
  4016a9:	89 dd                	mov    ebp,ebx
  4016ab:	2b 97 a4 00 00 00    	sub    edx,DWORD PTR [rdi+0xa4]
  4016b1:	21 c5                	and    ebp,eax
  4016b3:	29 ea                	sub    edx,ebp
  4016b5:	89 c5                	mov    ebp,eax
  4016b7:	f7 d5                	not    ebp
  4016b9:	44 21 dd             	and    ebp,r11d
  4016bc:	29 ea                	sub    edx,ebp
  4016be:	89 c5                	mov    ebp,eax
  4016c0:	66 d1 e8             	shr    ax,1
  4016c3:	c1 e5 0f             	shl    ebp,0xf
  4016c6:	0f b7 c0             	movzx  eax,ax
  4016c9:	09 e8                	or     eax,ebp
  4016cb:	44 89 dd             	mov    ebp,r11d
  4016ce:	2b 87 a0 00 00 00    	sub    eax,DWORD PTR [rdi+0xa0]
  4016d4:	21 dd                	and    ebp,ebx
  4016d6:	29 e8                	sub    eax,ebp
  4016d8:	89 dd                	mov    ebp,ebx
  4016da:	f7 d5                	not    ebp
  4016dc:	21 d5                	and    ebp,edx
  4016de:	29 e8                	sub    eax,ebp
  4016e0:	89 dd                	mov    ebp,ebx
  4016e2:	66 c1 eb 05          	shr    bx,0x5
  4016e6:	c1 e5 0b             	shl    ebp,0xb
  4016e9:	0f b7 db             	movzx  ebx,bx
  4016ec:	09 eb                	or     ebx,ebp
  4016ee:	89 d5                	mov    ebp,edx
  4016f0:	2b 9f 9c 00 00 00    	sub    ebx,DWORD PTR [rdi+0x9c]
  4016f6:	44 21 dd             	and    ebp,r11d
  4016f9:	29 eb                	sub    ebx,ebp
  4016fb:	44 89 dd             	mov    ebp,r11d
  4016fe:	f7 d5                	not    ebp
  401700:	21 c5                	and    ebp,eax
  401702:	29 eb                	sub    ebx,ebp
  401704:	44 89 dd             	mov    ebp,r11d
  401707:	66 41 c1 eb 03       	shr    r11w,0x3
  40170c:	c1 e5 0d             	shl    ebp,0xd
  40170f:	45 0f b7 db          	movzx  r11d,r11w
  401713:	41 09 eb             	or     r11d,ebp
  401716:	89 c5                	mov    ebp,eax
  401718:	44 2b 9f 98 00 00 00 	sub    r11d,DWORD PTR [rdi+0x98]
  40171f:	21 d5                	and    ebp,edx
  401721:	41 29 eb             	sub    r11d,ebp
  401724:	89 d5                	mov    ebp,edx
  401726:	f7 d5                	not    ebp
  401728:	21 dd                	and    ebp,ebx
  40172a:	41 29 eb             	sub    r11d,ebp
  40172d:	89 d5                	mov    ebp,edx
  40172f:	c1 e5 0e             	shl    ebp,0xe
  401732:	66 c1 ea 02          	shr    dx,0x2
  401736:	0f b7 d2             	movzx  edx,dx
  401739:	09 ea                	or     edx,ebp
  40173b:	89 dd                	mov    ebp,ebx
  40173d:	2b 97 94 00 00 00    	sub    edx,DWORD PTR [rdi+0x94]
  401743:	21 c5                	and    ebp,eax
  401745:	29 ea                	sub    edx,ebp
  401747:	89 c5                	mov    ebp,eax
  401749:	f7 d5                	not    ebp
  40174b:	44 21 dd             	and    ebp,r11d
  40174e:	29 ea                	sub    edx,ebp
  401750:	89 c5                	mov    ebp,eax
  401752:	66 d1 e8             	shr    ax,1
  401755:	c1 e5 0f             	shl    ebp,0xf
  401758:	0f b7 c0             	movzx  eax,ax
  40175b:	09 e8                	or     eax,ebp
  40175d:	44 89 dd             	mov    ebp,r11d
  401760:	2b 87 90 00 00 00    	sub    eax,DWORD PTR [rdi+0x90]
  401766:	21 dd                	and    ebp,ebx
  401768:	29 e8                	sub    eax,ebp
  40176a:	89 dd                	mov    ebp,ebx
  40176c:	f7 d5                	not    ebp
  40176e:	21 d5                	and    ebp,edx
  401770:	29 e8                	sub    eax,ebp
  401772:	89 dd                	mov    ebp,ebx
  401774:	66 c1 eb 05          	shr    bx,0x5
  401778:	c1 e5 0b             	shl    ebp,0xb
  40177b:	0f b7 db             	movzx  ebx,bx
  40177e:	41 89 c4             	mov    r12d,eax
  401781:	09 eb                	or     ebx,ebp
  401783:	89 d5                	mov    ebp,edx
  401785:	2b 9f 8c 00 00 00    	sub    ebx,DWORD PTR [rdi+0x8c]
  40178b:	44 21 dd             	and    ebp,r11d
  40178e:	29 eb                	sub    ebx,ebp
  401790:	44 89 dd             	mov    ebp,r11d
  401793:	f7 d5                	not    ebp
  401795:	21 c5                	and    ebp,eax
  401797:	29 eb                	sub    ebx,ebp
  401799:	44 89 dd             	mov    ebp,r11d
  40179c:	66 41 c1 eb 03       	shr    r11w,0x3
  4017a1:	c1 e5 0d             	shl    ebp,0xd
  4017a4:	45 0f b7 db          	movzx  r11d,r11w
  4017a8:	41 09 eb             	or     r11d,ebp
  4017ab:	89 c5                	mov    ebp,eax
  4017ad:	44 2b 9f 88 00 00 00 	sub    r11d,DWORD PTR [rdi+0x88]
  4017b4:	21 d5                	and    ebp,edx
  4017b6:	41 29 eb             	sub    r11d,ebp
  4017b9:	89 d5                	mov    ebp,edx
  4017bb:	f7 d5                	not    ebp
  4017bd:	21 dd                	and    ebp,ebx
  4017bf:	41 29 eb             	sub    r11d,ebp
  4017c2:	89 d5                	mov    ebp,edx
  4017c4:	c1 e5 0e             	shl    ebp,0xe
  4017c7:	66 c1 ea 02          	shr    dx,0x2
  4017cb:	0f b7 d2             	movzx  edx,dx
  4017ce:	41 c1 e4 0f          	shl    r12d,0xf
  4017d2:	09 ea                	or     edx,ebp
  4017d4:	89 dd                	mov    ebp,ebx
  4017d6:	2b 97 84 00 00 00    	sub    edx,DWORD PTR [rdi+0x84]
  4017dc:	21 c5                	and    ebp,eax
  4017de:	29 ea                	sub    edx,ebp
  4017e0:	89 c5                	mov    ebp,eax
  4017e2:	66 d1 e8             	shr    ax,1
  4017e5:	0f b7 c0             	movzx  eax,ax
  4017e8:	f7 d5                	not    ebp
  4017ea:	41 09 c4             	or     r12d,eax
  4017ed:	44 89 d8             	mov    eax,r11d
  4017f0:	44 2b a7 80 00 00 00 	sub    r12d,DWORD PTR [rdi+0x80]
  4017f7:	44 21 dd             	and    ebp,r11d
  4017fa:	21 d8                	and    eax,ebx
  4017fc:	29 ea                	sub    edx,ebp
  4017fe:	44 89 dd             	mov    ebp,r11d
  401801:	41 29 c4             	sub    r12d,eax
  401804:	89 d8                	mov    eax,ebx
  401806:	66 c1 ed 03          	shr    bp,0x3
  40180a:	f7 d0                	not    eax
  40180c:	0f b7 ed             	movzx  ebp,bp
  40180f:	21 d0                	and    eax,edx
  401811:	41 29 c4             	sub    r12d,eax
  401814:	89 d8                	mov    eax,ebx
  401816:	c1 e3 0b             	shl    ebx,0xb
  401819:	66 c1 e8 05          	shr    ax,0x5
  40181d:	0f b7 c0             	movzx  eax,ax
  401820:	09 c3                	or     ebx,eax
  401822:	89 d0                	mov    eax,edx
  401824:	2b 5f 7c             	sub    ebx,DWORD PTR [rdi+0x7c]
  401827:	44 21 d8             	and    eax,r11d
  40182a:	29 c3                	sub    ebx,eax
  40182c:	44 89 d8             	mov    eax,r11d
  40182f:	41 c1 e3 0d          	shl    r11d,0xd
  401833:	f7 d0                	not    eax
  401835:	44 09 dd             	or     ebp,r11d
  401838:	2b 6f 78             	sub    ebp,DWORD PTR [rdi+0x78]
  40183b:	45 89 e3             	mov    r11d,r12d
  40183e:	44 21 e0             	and    eax,r12d
  401841:	29 c3                	sub    ebx,eax
  401843:	44 89 e0             	mov    eax,r12d
  401846:	21 d0                	and    eax,edx
  401848:	29 c5                	sub    ebp,eax
  40184a:	89 d0                	mov    eax,edx
  40184c:	f7 d0                	not    eax
  40184e:	21 d8                	and    eax,ebx
  401850:	29 c5                	sub    ebp,eax
  401852:	89 d0                	mov    eax,edx
  401854:	66 c1 e8 02          	shr    ax,0x2
  401858:	c1 e2 0e             	shl    edx,0xe
  40185b:	0f b7 c0             	movzx  eax,ax
  40185e:	66 41 d1 eb          	shr    r11w,1
  401862:	09 c2                	or     edx,eax
  401864:	89 d8                	mov    eax,ebx
  401866:	2b 57 74             	sub    edx,DWORD PTR [rdi+0x74]
  401869:	44 21 e0             	and    eax,r12d
  40186c:	29 c2                	sub    edx,eax
  40186e:	44 89 e0             	mov    eax,r12d
  401871:	41 c1 e4 0f          	shl    r12d,0xf
  401875:	f7 d0                	not    eax
  401877:	21 e8                	and    eax,ebp
  401879:	29 c2                	sub    edx,eax
  40187b:	41 0f b7 c3          	movzx  eax,r11w
  40187f:	41 89 db             	mov    r11d,ebx
  401882:	41 21 eb             	and    r11d,ebp
  401885:	44 09 e0             	or     eax,r12d
  401888:	2b 47 70             	sub    eax,DWORD PTR [rdi+0x70]
  40188b:	44 29 d8             	sub    eax,r11d
  40188e:	41 89 db             	mov    r11d,ebx
  401891:	41 f7 d3             	not    r11d
  401894:	41 21 d3             	and    r11d,edx
  401897:	44 29 d8             	sub    eax,r11d
  40189a:	41 89 eb             	mov    r11d,ebp
  40189d:	41 83 e3 3f          	and    r11d,0x3f
  4018a1:	42 2b 1c 99          	sub    ebx,DWORD PTR [rcx+r11*4]
  4018a5:	41 89 db             	mov    r11d,ebx
  4018a8:	89 d3                	mov    ebx,edx
  4018aa:	83 e3 3f             	and    ebx,0x3f
  4018ad:	2b 2c 99             	sub    ebp,DWORD PTR [rcx+rbx*4]
  4018b0:	89 c3                	mov    ebx,eax
  4018b2:	83 e3 3f             	and    ebx,0x3f
  4018b5:	2b 14 99             	sub    edx,DWORD PTR [rcx+rbx*4]
  4018b8:	44 89 db             	mov    ebx,r11d
  4018bb:	83 e3 3f             	and    ebx,0x3f
  4018be:	2b 04 99             	sub    eax,DWORD PTR [rcx+rbx*4]
  4018c1:	44 89 db             	mov    ebx,r11d
  4018c4:	66 41 c1 eb 05       	shr    r11w,0x5
  4018c9:	c1 e3 0b             	shl    ebx,0xb
  4018cc:	45 0f b7 db          	movzx  r11d,r11w
  4018d0:	44 09 db             	or     ebx,r11d
  4018d3:	41 89 eb             	mov    r11d,ebp
  4018d6:	2b 5f 6c             	sub    ebx,DWORD PTR [rdi+0x6c]
  4018d9:	41 21 d3             	and    r11d,edx
  4018dc:	44 29 db             	sub    ebx,r11d
  4018df:	41 89 eb             	mov    r11d,ebp
  4018e2:	41 f7 d3             	not    r11d
  4018e5:	41 21 c3             	and    r11d,eax
  4018e8:	44 29 db             	sub    ebx,r11d
  4018eb:	41 89 eb             	mov    r11d,ebp
  4018ee:	41 c1 e3 0d          	shl    r11d,0xd
  4018f2:	66 c1 ed 03          	shr    bp,0x3
  4018f6:	0f b7 ed             	movzx  ebp,bp
  4018f9:	41 09 eb             	or     r11d,ebp
  4018fc:	89 d5                	mov    ebp,edx
  4018fe:	44 2b 5f 68          	sub    r11d,DWORD PTR [rdi+0x68]
  401902:	21 c5                	and    ebp,eax
  401904:	41 29 eb             	sub    r11d,ebp
  401907:	89 d5                	mov    ebp,edx
  401909:	f7 d5                	not    ebp
  40190b:	21 dd                	and    ebp,ebx
  40190d:	41 29 eb             	sub    r11d,ebp
  401910:	89 d5                	mov    ebp,edx
  401912:	66 c1 ea 02          	shr    dx,0x2
  401916:	c1 e5 0e             	shl    ebp,0xe
  401919:	0f b7 d2             	movzx  edx,dx
  40191c:	09 ea                	or     edx,ebp
  40191e:	89 c5                	mov    ebp,eax
  401920:	2b 57 64             	sub    edx,DWORD PTR [rdi+0x64]
  401923:	21 dd                	and    ebp,ebx
  401925:	29 ea                	sub    edx,ebp
  401927:	89 c5                	mov    ebp,eax
  401929:	f7 d5                	not    ebp
  40192b:	44 21 dd             	and    ebp,r11d
  40192e:	29 ea                	sub    edx,ebp
  401930:	89 c5                	mov    ebp,eax
  401932:	66 d1 e8             	shr    ax,1
  401935:	c1 e5 0f             	shl    ebp,0xf
  401938:	0f b7 c0             	movzx  eax,ax
  40193b:	09 e8                	or     eax,ebp
  40193d:	44 89 dd             	mov    ebp,r11d
  401940:	2b 47 60             	sub    eax,DWORD PTR [rdi+0x60]
  401943:	21 dd                	and    ebp,ebx
  401945:	29 e8                	sub    eax,ebp
  401947:	89 dd                	mov    ebp,ebx
  401949:	f7 d5                	not    ebp
  40194b:	21 d5                	and    ebp,edx
  40194d:	29 e8                	sub    eax,ebp
  40194f:	89 dd                	mov    ebp,ebx
  401951:	66 c1 eb 05          	shr    bx,0x5
  401955:	c1 e5 0b             	shl    ebp,0xb
  401958:	0f b7 db             	movzx  ebx,bx
  40195b:	09 eb                	or     ebx,ebp
  40195d:	89 d5                	mov    ebp,edx
  40195f:	2b 5f 5c             	sub    ebx,DWORD PTR [rdi+0x5c]
  401962:	44 21 dd             	and    ebp,r11d
  401965:	29 eb                	sub    ebx,ebp
  401967:	44 89 dd             	mov    ebp,r11d
  40196a:	f7 d5                	not    ebp
  40196c:	21 c5                	and    ebp,eax
  40196e:	29 eb                	sub    ebx,ebp
  401970:	44 89 dd             	mov    ebp,r11d
  401973:	c1 e5 0d             	shl    ebp,0xd
  401976:	66 41 c1 eb 03       	shr    r11w,0x3
  40197b:	45 0f b7 db          	movzx  r11d,r11w
  40197f:	41 09 eb             	or     r11d,ebp
  401982:	89 c5                	mov    ebp,eax
  401984:	44 2b 5f 58          	sub    r11d,DWORD PTR [rdi+0x58]
  401988:	21 d5                	and    ebp,edx
  40198a:	41 29 eb             	sub    r11d,ebp
  40198d:	89 d5                	mov    ebp,edx
  40198f:	f7 d5                	not    ebp
  401991:	21 dd                	and    ebp,ebx
  401993:	41 29 eb             	sub    r11d,ebp
  401996:	89 d5                	mov    ebp,edx
  401998:	66 c1 ea 02          	shr    dx,0x2
  40199c:	c1 e5 0e             	shl    ebp,0xe
  40199f:	0f b7 d2             	movzx  edx,dx
  4019a2:	09 ea                	or     edx,ebp
  4019a4:	89 dd                	mov    ebp,ebx
  4019a6:	2b 57 54             	sub    edx,DWORD PTR [rdi+0x54]
  4019a9:	21 c5                	and    ebp,eax
  4019ab:	29 ea                	sub    edx,ebp
  4019ad:	89 c5                	mov    ebp,eax
  4019af:	f7 d5                	not    ebp
  4019b1:	44 21 dd             	and    ebp,r11d
  4019b4:	29 ea                	sub    edx,ebp
  4019b6:	89 c5                	mov    ebp,eax
  4019b8:	66 d1 e8             	shr    ax,1
  4019bb:	c1 e5 0f             	shl    ebp,0xf
  4019be:	0f b7 c0             	movzx  eax,ax
  4019c1:	09 e8                	or     eax,ebp
  4019c3:	44 89 dd             	mov    ebp,r11d
  4019c6:	2b 47 50             	sub    eax,DWORD PTR [rdi+0x50]
  4019c9:	21 dd                	and    ebp,ebx
  4019cb:	29 e8                	sub    eax,ebp
  4019cd:	89 dd                	mov    ebp,ebx
  4019cf:	f7 d5                	not    ebp
  4019d1:	21 d5                	and    ebp,edx
  4019d3:	29 e8                	sub    eax,ebp
  4019d5:	89 dd                	mov    ebp,ebx
  4019d7:	66 c1 eb 05          	shr    bx,0x5
  4019db:	c1 e5 0b             	shl    ebp,0xb
  4019de:	0f b7 db             	movzx  ebx,bx
  4019e1:	09 eb                	or     ebx,ebp
  4019e3:	89 d5                	mov    ebp,edx
  4019e5:	2b 5f 4c             	sub    ebx,DWORD PTR [rdi+0x4c]
  4019e8:	44 21 dd             	and    ebp,r11d
  4019eb:	29 eb                	sub    ebx,ebp
  4019ed:	44 89 dd             	mov    ebp,r11d
  4019f0:	f7 d5                	not    ebp
  4019f2:	21 c5                	and    ebp,eax
  4019f4:	29 eb                	sub    ebx,ebp
  4019f6:	44 89 dd             	mov    ebp,r11d
  4019f9:	c1 e5 0d             	shl    ebp,0xd
  4019fc:	66 41 c1 eb 03       	shr    r11w,0x3
  401a01:	45 0f b7 db          	movzx  r11d,r11w
  401a05:	41 09 eb             	or     r11d,ebp
  401a08:	89 c5                	mov    ebp,eax
  401a0a:	44 2b 5f 48          	sub    r11d,DWORD PTR [rdi+0x48]
  401a0e:	21 d5                	and    ebp,edx
  401a10:	41 29 eb             	sub    r11d,ebp
  401a13:	89 d5                	mov    ebp,edx
  401a15:	f7 d5                	not    ebp
  401a17:	21 dd                	and    ebp,ebx
  401a19:	41 29 eb             	sub    r11d,ebp
  401a1c:	89 d5                	mov    ebp,edx
  401a1e:	66 c1 ea 02          	shr    dx,0x2
  401a22:	c1 e5 0e             	shl    ebp,0xe
  401a25:	0f b7 d2             	movzx  edx,dx
  401a28:	09 ea                	or     edx,ebp
  401a2a:	89 dd                	mov    ebp,ebx
  401a2c:	2b 57 44             	sub    edx,DWORD PTR [rdi+0x44]
  401a2f:	21 c5                	and    ebp,eax
  401a31:	29 ea                	sub    edx,ebp
  401a33:	89 c5                	mov    ebp,eax
  401a35:	f7 d5                	not    ebp
  401a37:	44 21 dd             	and    ebp,r11d
  401a3a:	29 ea                	sub    edx,ebp
  401a3c:	89 c5                	mov    ebp,eax
  401a3e:	66 d1 e8             	shr    ax,1
  401a41:	c1 e5 0f             	shl    ebp,0xf
  401a44:	0f b7 c0             	movzx  eax,ax
  401a47:	09 e8                	or     eax,ebp
  401a49:	44 89 dd             	mov    ebp,r11d
  401a4c:	2b 47 40             	sub    eax,DWORD PTR [rdi+0x40]
  401a4f:	21 dd                	and    ebp,ebx
  401a51:	29 e8                	sub    eax,ebp
  401a53:	89 dd                	mov    ebp,ebx
  401a55:	f7 d5                	not    ebp
  401a57:	21 d5                	and    ebp,edx
  401a59:	29 e8                	sub    eax,ebp
  401a5b:	89 dd                	mov    ebp,ebx
  401a5d:	66 c1 eb 05          	shr    bx,0x5
  401a61:	c1 e5 0b             	shl    ebp,0xb
  401a64:	0f b7 db             	movzx  ebx,bx
  401a67:	41 89 c4             	mov    r12d,eax
  401a6a:	09 eb                	or     ebx,ebp
  401a6c:	89 d5                	mov    ebp,edx
  401a6e:	2b 5f 3c             	sub    ebx,DWORD PTR [rdi+0x3c]
  401a71:	44 21 dd             	and    ebp,r11d
  401a74:	29 eb                	sub    ebx,ebp
  401a76:	44 89 dd             	mov    ebp,r11d
  401a79:	f7 d5                	not    ebp
  401a7b:	21 c5                	and    ebp,eax
  401a7d:	29 eb                	sub    ebx,ebp
  401a7f:	44 89 dd             	mov    ebp,r11d
  401a82:	c1 e5 0d             	shl    ebp,0xd
  401a85:	66 41 c1 eb 03       	shr    r11w,0x3
  401a8a:	45 0f b7 db          	movzx  r11d,r11w
  401a8e:	41 c1 e4 0f          	shl    r12d,0xf
  401a92:	41 09 eb             	or     r11d,ebp
  401a95:	89 c5                	mov    ebp,eax
  401a97:	44 2b 5f 38          	sub    r11d,DWORD PTR [rdi+0x38]
  401a9b:	21 d5                	and    ebp,edx
  401a9d:	41 29 eb             	sub    r11d,ebp
  401aa0:	89 d5                	mov    ebp,edx
  401aa2:	f7 d5                	not    ebp
  401aa4:	21 dd                	and    ebp,ebx
  401aa6:	41 29 eb             	sub    r11d,ebp
  401aa9:	89 d5                	mov    ebp,edx
  401aab:	66 c1 ea 02          	shr    dx,0x2
  401aaf:	c1 e5 0e             	shl    ebp,0xe
  401ab2:	0f b7 d2             	movzx  edx,dx
  401ab5:	09 ea                	or     edx,ebp
  401ab7:	89 dd                	mov    ebp,ebx
  401ab9:	2b 57 34             	sub    edx,DWORD PTR [rdi+0x34]
  401abc:	21 c5                	and    ebp,eax
  401abe:	29 ea                	sub    edx,ebp
  401ac0:	89 c5                	mov    ebp,eax
  401ac2:	66 d1 e8             	shr    ax,1
  401ac5:	0f b7 c0             	movzx  eax,ax
  401ac8:	f7 d5                	not    ebp
  401aca:	41 09 c4             	or     r12d,eax
  401acd:	44 89 d8             	mov    eax,r11d
  401ad0:	44 2b 67 30          	sub    r12d,DWORD PTR [rdi+0x30]
  401ad4:	44 21 dd             	and    ebp,r11d
  401ad7:	21 d8                	and    eax,ebx
  401ad9:	29 ea                	sub    edx,ebp
  401adb:	41 29 c4             	sub    r12d,eax
  401ade:	89 d8                	mov    eax,ebx
  401ae0:	89 d5                	mov    ebp,edx
  401ae2:	f7 d0                	not    eax
  401ae4:	21 d0                	and    eax,edx
  401ae6:	41 29 c4             	sub    r12d,eax
  401ae9:	89 d8                	mov    eax,ebx
  401aeb:	c1 e3 0b             	shl    ebx,0xb
  401aee:	66 c1 e8 05          	shr    ax,0x5
  401af2:	0f b7 c0             	movzx  eax,ax
  401af5:	09 c3                	or     ebx,eax
  401af7:	89 d0                	mov    eax,edx
  401af9:	2b 5f 2c             	sub    ebx,DWORD PTR [rdi+0x2c]
  401afc:	44 21 d8             	and    eax,r11d
  401aff:	29 c3                	sub    ebx,eax
  401b01:	44 89 d8             	mov    eax,r11d
  401b04:	f7 d0                	not    eax
  401b06:	44 21 e0             	and    eax,r12d
  401b09:	29 c3                	sub    ebx,eax
  401b0b:	44 89 d8             	mov    eax,r11d
  401b0e:	66 c1 e8 03          	shr    ax,0x3
  401b12:	41 c1 e3 0d          	shl    r11d,0xd
  401b16:	4d 29 ca             	sub    r10,r9
  401b19:	4c 01 ce             	add    rsi,r9
  401b1c:	0f b7 c0             	movzx  eax,ax
  401b1f:	66 c1 ed 02          	shr    bp,0x2
  401b23:	41 09 c3             	or     r11d,eax
  401b26:	44 89 e0             	mov    eax,r12d
  401b29:	44 2b 5f 28          	sub    r11d,DWORD PTR [rdi+0x28]
  401b2d:	0f b7 ed             	movzx  ebp,bp
  401b30:	21 d0                	and    eax,edx
  401b32:	41 29 c3             	sub    r11d,eax
  401b35:	89 d0                	mov    eax,edx
  401b37:	c1 e2 0e             	shl    edx,0xe
  401b3a:	f7 d0                	not    eax
  401b3c:	09 d5                	or     ebp,edx
  401b3e:	2b 6f 24             	sub    ebp,DWORD PTR [rdi+0x24]
  401b41:	44 89 e2             	mov    edx,r12d
  401b44:	21 d8                	and    eax,ebx
  401b46:	66 d1 ea             	shr    dx,1
  401b49:	41 29 c3             	sub    r11d,eax
  401b4c:	89 d8                	mov    eax,ebx
  401b4e:	44 21 e0             	and    eax,r12d
  401b51:	29 c5                	sub    ebp,eax
  401b53:	44 89 e0             	mov    eax,r12d
  401b56:	41 c1 e4 0f          	shl    r12d,0xf
  401b5a:	f7 d0                	not    eax
  401b5c:	44 21 d8             	and    eax,r11d
  401b5f:	29 c5                	sub    ebp,eax
  401b61:	0f b7 c2             	movzx  eax,dx
  401b64:	89 da                	mov    edx,ebx
  401b66:	44 21 da             	and    edx,r11d
  401b69:	44 09 e0             	or     eax,r12d
  401b6c:	2b 47 20             	sub    eax,DWORD PTR [rdi+0x20]
  401b6f:	41 88 68 02          	mov    BYTE PTR [r8+0x2],bpl
  401b73:	29 d0                	sub    eax,edx
  401b75:	89 da                	mov    edx,ebx
  401b77:	45 88 58 04          	mov    BYTE PTR [r8+0x4],r11b
  401b7b:	f7 d2                	not    edx
  401b7d:	41 88 58 06          	mov    BYTE PTR [r8+0x6],bl
  401b81:	21 ea                	and    edx,ebp
  401b83:	29 d0                	sub    eax,edx
  401b85:	41 88 00             	mov    BYTE PTR [r8],al
  401b88:	0f b6 c4             	movzx  eax,ah
  401b8b:	41 88 40 01          	mov    BYTE PTR [r8+0x1],al
  401b8f:	89 e8                	mov    eax,ebp
  401b91:	0f b6 c4             	movzx  eax,ah
  401b94:	41 88 40 03          	mov    BYTE PTR [r8+0x3],al
  401b98:	44 89 d8             	mov    eax,r11d
  401b9b:	0f b6 c4             	movzx  eax,ah
  401b9e:	41 88 40 05          	mov    BYTE PTR [r8+0x5],al
  401ba2:	0f b6 c7             	movzx  eax,bh
  401ba5:	41 88 40 07          	mov    BYTE PTR [r8+0x7],al
  401ba9:	4d 01 c8             	add    r8,r9
  401bac:	4d 39 d1             	cmp    r9,r10
  401baf:	0f 86 eb f5 ff ff    	jbe    0x4011a0
  401bb5:	49 83 fa 01          	cmp    r10,0x1
  401bb9:	5b                   	pop    rbx
  401bba:	5d                   	pop    rbp
  401bbb:	19 c0                	sbb    eax,eax
  401bbd:	41 5c                	pop    r12
  401bbf:	41 5d                	pop    r13
  401bc1:	f7 d0                	not    eax
  401bc3:	83 e0 03             	and    eax,0x3
  401bc6:	c3                   	ret
  401bc7:	66 0f 1f 84 00 00 00 	nop    WORD PTR [rax+rax*1+0x0]
  401bce:	00 00 
  401bd0:	b8 01 00 00 00       	mov    eax,0x1
  401bd5:	c3                   	ret
  401bd6:	48 83 f9 01          	cmp    rcx,0x1
  401bda:	19 c0                	sbb    eax,eax
  401bdc:	f7 d0                	not    eax
  401bde:	83 e0 03             	and    eax,0x3
  401be1:	c3                   	ret
  401be2:	66 66 2e 0f 1f 84 00 	data16 cs nop WORD PTR [rax+rax*1+0x0]
  401be9:	00 00 00 00 
  401bed:	0f 1f 00             	nop    DWORD PTR [rax]
  401bf0:	49 89 d1             	mov    r9,rdx
  401bf3:	48 85 f6             	test   rsi,rsi
  401bf6:	0f 94 c2             	sete   dl
  401bf9:	4d 85 c9             	test   r9,r9
  401bfc:	0f 94 c0             	sete   al
  401bff:	08 c2                	or     dl,al
  401c01:	0f 85 a9 09 00 00    	jne    0x4025b0
  401c07:	48 85 ff             	test   rdi,rdi
  401c0a:	0f 84 a0 09 00 00    	je     0x4025b0
  401c10:	4c 8b 5f 18          	mov    r11,QWORD PTR [rdi+0x18]
  401c14:	41 55                	push   r13
  401c16:	41 54                	push   r12
  401c18:	55                   	push   rbp
  401c19:	53                   	push   rbx
  401c1a:	48 89 cb             	mov    rbx,rcx
  401c1d:	4c 39 d9             	cmp    rcx,r11
  401c20:	0f 82 73 09 00 00    	jb     0x402599
  401c26:	49 89 f0             	mov    r8,rsi
  401c29:	4c 8d 57 20          	lea    r10,[rdi+0x20]
  401c2d:	0f 1f 00             	nop    DWORD PTR [rax]
  401c30:	41 0f b6 50 03       	movzx  edx,BYTE PTR [r8+0x3]
  401c35:	41 0f b6 40 02       	movzx  eax,BYTE PTR [r8+0x2]
  401c3a:	41 0f b6 48 05       	movzx  ecx,BYTE PTR [r8+0x5]
  401c3f:	41 0f b6 70 06       	movzx  esi,BYTE PTR [r8+0x6]
  401c44:	c1 e2 08             	shl    edx,0x8
  401c47:	01 c2                	add    edx,eax
  401c49:	41 0f b6 40 04       	movzx  eax,BYTE PTR [r8+0x4]
  401c4e:	c1 e1 08             	shl    ecx,0x8
  401c51:	01 c1                	add    ecx,eax
  401c53:	41 0f b6 40 07       	movzx  eax,BYTE PTR [r8+0x7]
  401c58:	41 89 cc             	mov    r12d,ecx
  401c5b:	c1 e0 08             	shl    eax,0x8
  401c5e:	01 f0                	add    eax,esi
  401c60:	41 0f b6 30          	movzx  esi,BYTE PTR [r8]
  401c64:	03 77 20             	add    esi,DWORD PTR [rdi+0x20]
  401c67:	89 f5                	mov    ebp,esi
  401c69:	41 0f b6 70 01       	movzx  esi,BYTE PTR [r8+0x1]
  401c6e:	41 21 c4             	and    r12d,eax
  401c71:	c1 e6 08             	shl    esi,0x8
  401c74:	01 ee                	add    esi,ebp
  401c76:	41 01 f4             	add    r12d,esi
  401c79:	89 c6                	mov    esi,eax
  401c7b:	f7 d6                	not    esi
  401c7d:	21 d6                	and    esi,edx
  401c7f:	03 57 24             	add    edx,DWORD PTR [rdi+0x24]
  401c82:	44 01 e6             	add    esi,r12d
  401c85:	8d 2c 36             	lea    ebp,[rsi+rsi*1]
  401c88:	66 c1 ee 0f          	shr    si,0xf
  401c8c:	0f b7 f6             	movzx  esi,si
  401c8f:	09 f5                	or     ebp,esi
  401c91:	89 ee                	mov    esi,ebp
  401c93:	21 c6                	and    esi,eax
  401c95:	01 f2                	add    edx,esi
  401c97:	89 ee                	mov    esi,ebp
  401c99:	f7 d6                	not    esi
  401c9b:	21 ce                	and    esi,ecx
  401c9d:	03 4f 28             	add    ecx,DWORD PTR [rdi+0x28]
  401ca0:	01 d6                	add    esi,edx
  401ca2:	8d 14 b5 00 00 00 00 	lea    edx,[rsi*4+0x0]
  401ca9:	66 c1 ee 0e          	shr    si,0xe
  401cad:	0f b7 f6             	movzx  esi,si
  401cb0:	09 f2                	or     edx,esi
  401cb2:	89 ee                	mov    esi,ebp
  401cb4:	21 d6                	and    esi,edx
  401cb6:	01 ce                	add    esi,ecx
  401cb8:	89 d1                	mov    ecx,edx
  401cba:	f7 d1                	not    ecx
  401cbc:	21 c1                	and    ecx,eax
  401cbe:	03 47 2c             	add    eax,DWORD PTR [rdi+0x2c]
  401cc1:	01 f1                	add    ecx,esi
  401cc3:	8d 34 cd 00 00 00 00 	lea    esi,[rcx*8+0x0]
  401cca:	66 c1 e9 0d          	shr    cx,0xd
  401cce:	0f b7 c9             	movzx  ecx,cx
  401cd1:	09 ce                	or     esi,ecx
  401cd3:	89 d1                	mov    ecx,edx
  401cd5:	21 f1                	and    ecx,esi
  401cd7:	41 89 f4             	mov    r12d,esi
  401cda:	01 c8                	add    eax,ecx
  401cdc:	89 f1                	mov    ecx,esi
  401cde:	f7 d1                	not    ecx
  401ce0:	21 e9                	and    ecx,ebp
  401ce2:	03 6f 30             	add    ebp,DWORD PTR [rdi+0x30]
  401ce5:	01 c1                	add    ecx,eax
  401ce7:	89 c8                	mov    eax,ecx
  401ce9:	66 c1 e9 0b          	shr    cx,0xb
  401ced:	c1 e0 05             	shl    eax,0x5
  401cf0:	0f b7 c9             	movzx  ecx,cx
  401cf3:	09 c8                	or     eax,ecx
  401cf5:	41 21 c4             	and    r12d,eax
  401cf8:	41 01 ec             	add    r12d,ebp
  401cfb:	89 c5                	mov    ebp,eax
  401cfd:	f7 d5                	not    ebp
  401cff:	21 d5                	and    ebp,edx
  401d01:	03 57 34             	add    edx,DWORD PTR [rdi+0x34]
  401d04:	44 01 e5             	add    ebp,r12d
  401d07:	8d 4c 2d 00          	lea    ecx,[rbp+rbp*1+0x0]
  401d0b:	66 c1 ed 0f          	shr    bp,0xf
  401d0f:	0f b7 ed             	movzx  ebp,bp
  401d12:	09 e9                	or     ecx,ebp
  401d14:	89 c5                	mov    ebp,eax
  401d16:	21 cd                	and    ebp,ecx
  401d18:	01 ea                	add    edx,ebp
  401d1a:	89 cd                	mov    ebp,ecx
  401d1c:	f7 d5                	not    ebp
  401d1e:	21 f5                	and    ebp,esi
  401d20:	03 77 38             	add    esi,DWORD PTR [rdi+0x38]
  401d23:	01 d5                	add    ebp,edx
  401d25:	8d 14 ad 00 00 00 00 	lea    edx,[rbp*4+0x0]
  401d2c:	66 c1 ed 0e          	shr    bp,0xe
  401d30:	0f b7 ed             	movzx  ebp,bp
  401d33:	09 ea                	or     edx,ebp
  401d35:	89 cd                	mov    ebp,ecx
  401d37:	21 d5                	and    ebp,edx
  401d39:	01 ee                	add    esi,ebp
  401d3b:	89 d5                	mov    ebp,edx
  401d3d:	f7 d5                	not    ebp
  401d3f:	21 c5                	and    ebp,eax
  401d41:	03 47 3c             	add    eax,DWORD PTR [rdi+0x3c]
  401d44:	01 f5                	add    ebp,esi
  401d46:	8d 34 ed 00 00 00 00 	lea    esi,[rbp*8+0x0]
  401d4d:	66 c1 ed 0d          	shr    bp,0xd
  401d51:	0f b7 ed             	movzx  ebp,bp
  401d54:	09 ee                	or     esi,ebp
  401d56:	89 d5                	mov    ebp,edx
  401d58:	21 f5                	and    ebp,esi
  401d5a:	01 e8                	add    eax,ebp
  401d5c:	89 f5                	mov    ebp,esi
  401d5e:	f7 d5                	not    ebp
  401d60:	21 cd                	and    ebp,ecx
  401d62:	01 c5                	add    ebp,eax
  401d64:	89 e8                	mov    eax,ebp
  401d66:	c1 e0 05             	shl    eax,0x5
  401d69:	66 c1 ed 0b          	shr    bp,0xb
  401d6d:	03 4f 40             	add    ecx,DWORD PTR [rdi+0x40]
  401d70:	0f b7 ed             	movzx  ebp,bp
  401d73:	09 e8                	or     eax,ebp
  401d75:	89 f5                	mov    ebp,esi
  401d77:	21 c5                	and    ebp,eax
  401d79:	01 e9                	add    ecx,ebp
  401d7b:	89 c5                	mov    ebp,eax
  401d7d:	f7 d5                	not    ebp
  401d7f:	21 d5                	and    ebp,edx
  401d81:	03 57 44             	add    edx,DWORD PTR [rdi+0x44]
  401d84:	01 cd                	add    ebp,ecx
  401d86:	8d 4c 2d 00          	lea    ecx,[rbp+rbp*1+0x0]
  401d8a:	66 c1 ed 0f          	shr    bp,0xf
  401d8e:	0f b7 ed             	movzx  ebp,bp
  401d91:	09 e9                	or     ecx,ebp
  401d93:	89 c5                	mov    ebp,eax
  401d95:	21 cd                	and    ebp,ecx
  401d97:	01 ea                	add    edx,ebp
  401d99:	89 cd                	mov    ebp,ecx
  401d9b:	f7 d5                	not    ebp
  401d9d:	21 f5                	and    ebp,esi
  401d9f:	03 77 48             	add    esi,DWORD PTR [rdi+0x48]
  401da2:	01 d5                	add    ebp,edx
  401da4:	8d 14 ad 00 00 00 00 	lea    edx,[rbp*4+0x0]
  401dab:	66 c1 ed 0e          	shr    bp,0xe
  401daf:	0f b7 ed             	movzx  ebp,bp
  401db2:	09 ea                	or     edx,ebp
  401db4:	89 cd                	mov    ebp,ecx
  401db6:	21 d5                	and    ebp,edx
  401db8:	01 ee                	add    esi,ebp
  401dba:	89 d5                	mov    ebp,edx
  401dbc:	f7 d5                	not    ebp
  401dbe:	21 c5                	and    ebp,eax
  401dc0:	03 47 4c             	add    eax,DWORD PTR [rdi+0x4c]
  401dc3:	01 f5                	add    ebp,esi
  401dc5:	8d 34 ed 00 00 00 00 	lea    esi,[rbp*8+0x0]
  401dcc:	66 c1 ed 0d          	shr    bp,0xd
  401dd0:	0f b7 ed             	movzx  ebp,bp
  401dd3:	09 ee                	or     esi,ebp
  401dd5:	89 d5                	mov    ebp,edx
  401dd7:	21 f5                	and    ebp,esi
  401dd9:	01 e8                	add    eax,ebp
  401ddb:	89 f5                	mov    ebp,esi
  401ddd:	f7 d5                	not    ebp
  401ddf:	21 cd                	and    ebp,ecx
  401de1:	03 4f 50             	add    ecx,DWORD PTR [rdi+0x50]
  401de4:	01 c5                	add    ebp,eax
  401de6:	89 e8                	mov    eax,ebp
  401de8:	66 c1 ed 0b          	shr    bp,0xb
  401dec:	c1 e0 05             	shl    eax,0x5
  401def:	0f b7 ed             	movzx  ebp,bp
  401df2:	09 e8                	or     eax,ebp
  401df4:	89 f5                	mov    ebp,esi
  401df6:	21 c5                	and    ebp,eax
  401df8:	01 e9                	add    ecx,ebp
  401dfa:	89 c5                	mov    ebp,eax
  401dfc:	f7 d5                	not    ebp
  401dfe:	21 d5                	and    ebp,edx
  401e00:	03 57 54             	add    edx,DWORD PTR [rdi+0x54]
  401e03:	01 cd                	add    ebp,ecx
  401e05:	8d 4c 2d 00          	lea    ecx,[rbp+rbp*1+0x0]
  401e09:	66 c1 ed 0f          	shr    bp,0xf
  401e0d:	0f b7 ed             	movzx  ebp,bp
  401e10:	09 e9                	or     ecx,ebp
  401e12:	89 c5                	mov    ebp,eax
  401e14:	21 cd                	and    ebp,ecx
  401e16:	01 ea                	add    edx,ebp
  401e18:	89 cd                	mov    ebp,ecx
  401e1a:	f7 d5                	not    ebp
  401e1c:	21 f5                	and    ebp,esi
  401e1e:	03 77 58             	add    esi,DWORD PTR [rdi+0x58]
  401e21:	01 d5                	add    ebp,edx
  401e23:	8d 14 ad 00 00 00 00 	lea    edx,[rbp*4+0x0]
  401e2a:	66 c1 ed 0e          	shr    bp,0xe
  401e2e:	0f b7 ed             	movzx  ebp,bp
  401e31:	09 ea                	or     edx,ebp
  401e33:	89 cd                	mov    ebp,ecx
  401e35:	21 d5                	and    ebp,edx
  401e37:	01 ee                	add    esi,ebp
  401e39:	89 d5                	mov    ebp,edx
  401e3b:	f7 d5                	not    ebp
  401e3d:	21 c5                	and    ebp,eax
  401e3f:	03 47 5c             	add    eax,DWORD PTR [rdi+0x5c]
  401e42:	01 f5                	add    ebp,esi
  401e44:	8d 34 ed 00 00 00 00 	lea    esi,[rbp*8+0x0]
  401e4b:	66 c1 ed 0d          	shr    bp,0xd
  401e4f:	0f b7 ed             	movzx  ebp,bp
  401e52:	09 ee                	or     esi,ebp
  401e54:	89 d5                	mov    ebp,edx
  401e56:	21 f5                	and    ebp,esi
  401e58:	01 e8                	add    eax,ebp
  401e5a:	89 f5                	mov    ebp,esi
  401e5c:	f7 d5                	not    ebp
  401e5e:	21 cd                	and    ebp,ecx
  401e60:	03 4f 60             	add    ecx,DWORD PTR [rdi+0x60]
  401e63:	01 c5                	add    ebp,eax
  401e65:	89 e8                	mov    eax,ebp
  401e67:	66 c1 ed 0b          	shr    bp,0xb
  401e6b:	c1 e0 05             	shl    eax,0x5
  401e6e:	0f b7 ed             	movzx  ebp,bp
  401e71:	09 e8                	or     eax,ebp
  401e73:	89 f5                	mov    ebp,esi
  401e75:	21 c5                	and    ebp,eax
  401e77:	01 e9                	add    ecx,ebp
  401e79:	89 c5                	mov    ebp,eax
  401e7b:	f7 d5                	not    ebp
  401e7d:	21 d5                	and    ebp,edx
  401e7f:	01 cd                	add    ebp,ecx
  401e81:	03 57 64             	add    edx,DWORD PTR [rdi+0x64]
  401e84:	8d 4c 2d 00          	lea    ecx,[rbp+rbp*1+0x0]
  401e88:	66 c1 ed 0f          	shr    bp,0xf
  401e8c:	0f b7 ed             	movzx  ebp,bp
  401e8f:	09 e9                	or     ecx,ebp
  401e91:	89 c5                	mov    ebp,eax
  401e93:	21 cd                	and    ebp,ecx
  401e95:	01 ea                	add    edx,ebp
  401e97:	89 cd                	mov    ebp,ecx
  401e99:	f7 d5                	not    ebp
  401e9b:	21 f5                	and    ebp,esi
  401e9d:	03 77 68             	add    esi,DWORD PTR [rdi+0x68]
  401ea0:	01 d5                	add    ebp,edx
  401ea2:	8d 14 ad 00 00 00 00 	lea    edx,[rbp*4+0x0]
  401ea9:	66 c1 ed 0e          	shr    bp,0xe
  401ead:	0f b7 ed             	movzx  ebp,bp
  401eb0:	09 ea                	or     edx,ebp
  401eb2:	89 cd                	mov    ebp,ecx
  401eb4:	21 d5                	and    ebp,edx
  401eb6:	01 f5                	add    ebp,esi
  401eb8:	89 d6                	mov    esi,edx
  401eba:	f7 d6                	not    esi
  401ebc:	21 c6                	and    esi,eax
  401ebe:	03 47 6c             	add    eax,DWORD PTR [rdi+0x6c]
  401ec1:	01 ee                	add    esi,ebp
  401ec3:	44 8d 2c f5 00 00 00 	lea    r13d,[rsi*8+0x0]
  401eca:	00 
  401ecb:	66 c1 ee 0d          	shr    si,0xd
  401ecf:	0f b7 f6             	movzx  esi,si
  401ed2:	41 09 f5             	or     r13d,esi
  401ed5:	89 d6                	mov    esi,edx
  401ed7:	44 21 ee             	and    esi,r13d
  401eda:	01 f0                	add    eax,esi
  401edc:	44 89 ee             	mov    esi,r13d
  401edf:	f7 d6                	not    esi
  401ee1:	21 ce                	and    esi,ecx
  401ee3:	01 c6                	add    esi,eax
  401ee5:	89 f0                	mov    eax,esi
  401ee7:	66 c1 ee 0b          	shr    si,0xb
  401eeb:	c1 e0 05             	shl    eax,0x5
  401eee:	0f b7 f6             	movzx  esi,si
  401ef1:	09 c6                	or     esi,eax
  401ef3:	89 f0                	mov    eax,esi
  401ef5:	83 e0 3f             	and    eax,0x3f
  401ef8:	41 03 0c 82          	add    ecx,DWORD PTR [r10+rax*4]
  401efc:	89 c8                	mov    eax,ecx
  401efe:	83 e0 3f             	and    eax,0x3f
  401f01:	41 03 14 82          	add    edx,DWORD PTR [r10+rax*4]
  401f05:	89 d0                	mov    eax,edx
  401f07:	83 e0 3f             	and    eax,0x3f
  401f0a:	45 03 2c 82          	add    r13d,DWORD PTR [r10+rax*4]
  401f0e:	44 89 e8             	mov    eax,r13d
  401f11:	83 e0 3f             	and    eax,0x3f
  401f14:	41 03 34 82          	add    esi,DWORD PTR [r10+rax*4]
  401f18:	03 4f 70             	add    ecx,DWORD PTR [rdi+0x70]
  401f1b:	89 f0                	mov    eax,esi
  401f1d:	44 89 ee             	mov    esi,r13d
  401f20:	21 c6                	and    esi,eax
  401f22:	89 c5                	mov    ebp,eax
  401f24:	01 ce                	add    esi,ecx
  401f26:	89 c1                	mov    ecx,eax
  401f28:	f7 d1                	not    ecx
  401f2a:	21 d1                	and    ecx,edx
  401f2c:	03 57 74             	add    edx,DWORD PTR [rdi+0x74]
  401f2f:	01 f1                	add    ecx,esi
  401f31:	8b b7 80 00 00 00    	mov    esi,DWORD PTR [rdi+0x80]
  401f37:	41 89 cc             	mov    r12d,ecx
  401f3a:	01 c9                	add    ecx,ecx
  401f3c:	66 41 c1 ec 0f       	shr    r12w,0xf
  401f41:	45 0f b7 e4          	movzx  r12d,r12w
  401f45:	41 09 cc             	or     r12d,ecx
  401f48:	44 21 e5             	and    ebp,r12d
  401f4b:	01 d5                	add    ebp,edx
  401f4d:	44 89 e2             	mov    edx,r12d
  401f50:	f7 d2                	not    edx
  401f52:	44 21 ea             	and    edx,r13d
  401f55:	44 03 6f 78          	add    r13d,DWORD PTR [rdi+0x78]
  401f59:	01 ea                	add    edx,ebp
  401f5b:	89 d5                	mov    ebp,edx
  401f5d:	c1 e2 02             	shl    edx,0x2
  401f60:	66 c1 ed 0e          	shr    bp,0xe
  401f64:	0f b7 ed             	movzx  ebp,bp
  401f67:	09 d5                	or     ebp,edx
  401f69:	89 e9                	mov    ecx,ebp
  401f6b:	44 21 e1             	and    ecx,r12d
  401f6e:	44 01 e9             	add    ecx,r13d
  401f71:	41 89 ed             	mov    r13d,ebp
  401f74:	41 f7 d5             	not    r13d
  401f77:	41 21 c5             	and    r13d,eax
  401f7a:	03 47 7c             	add    eax,DWORD PTR [rdi+0x7c]
  401f7d:	41 01 cd             	add    r13d,ecx
  401f80:	44 89 e9             	mov    ecx,r13d
  401f83:	41 c1 e5 03          	shl    r13d,0x3
  401f87:	66 c1 e9 0d          	shr    cx,0xd
  401f8b:	0f b7 c9             	movzx  ecx,cx
  401f8e:	44 09 e9             	or     ecx,r13d
  401f91:	89 ca                	mov    edx,ecx
  401f93:	21 ea                	and    edx,ebp
  401f95:	01 d0                	add    eax,edx
  401f97:	89 ca                	mov    edx,ecx
  401f99:	f7 d2                	not    edx
  401f9b:	44 21 e2             	and    edx,r12d
  401f9e:	01 c2                	add    edx,eax
  401fa0:	89 d0                	mov    eax,edx
  401fa2:	c1 e2 05             	shl    edx,0x5
  401fa5:	66 c1 e8 0b          	shr    ax,0xb
  401fa9:	0f b7 c0             	movzx  eax,ax
  401fac:	09 d0                	or     eax,edx
  401fae:	44 01 e6             	add    esi,r12d
  401fb1:	41 89 c4             	mov    r12d,eax
  401fb4:	41 21 cc             	and    r12d,ecx
  401fb7:	41 01 f4             	add    r12d,esi
  401fba:	89 c6                	mov    esi,eax
  401fbc:	f7 d6                	not    esi
  401fbe:	21 ee                	and    esi,ebp
  401fc0:	03 af 84 00 00 00    	add    ebp,DWORD PTR [rdi+0x84]
  401fc6:	44 01 e6             	add    esi,r12d
  401fc9:	89 f2                	mov    edx,esi
  401fcb:	01 f6                	add    esi,esi
  401fcd:	66 c1 ea 0f          	shr    dx,0xf
  401fd1:	0f b7 d2             	movzx  edx,dx
  401fd4:	09 f2                	or     edx,esi
  401fd6:	89 d6                	mov    esi,edx
  401fd8:	21 c6                	and    esi,eax
  401fda:	01 ee                	add    esi,ebp
  401fdc:	89 d5                	mov    ebp,edx
  401fde:	f7 d5                	not    ebp
  401fe0:	21 cd                	and    ebp,ecx
  401fe2:	03 8f 88 00 00 00    	add    ecx,DWORD PTR [rdi+0x88]
  401fe8:	01 f5                	add    ebp,esi
  401fea:	89 ee                	mov    esi,ebp
  401fec:	c1 e5 02             	shl    ebp,0x2
  401fef:	66 c1 ee 0e          	shr    si,0xe
  401ff3:	0f b7 f6             	movzx  esi,si
  401ff6:	09 ee                	or     esi,ebp
  401ff8:	89 f5                	mov    ebp,esi
  401ffa:	21 d5                	and    ebp,edx
  401ffc:	01 e9                	add    ecx,ebp
  401ffe:	89 f5                	mov    ebp,esi
  402000:	08 4e 00             	or     BYTE PTR [rsi+0x0],cl
	...
  402017:	00 36                	add    BYTE PTR [rsi],dh
  402019:	10 00                	adc    BYTE PTR [rax],al
  40201b:	00 00                	add    BYTE PTR [rax],al
  40201d:	00 00                	add    BYTE PTR [rax],al
  40201f:	00 46 10             	add    BYTE PTR [rsi+0x10],al
  402022:	00 00                	add    BYTE PTR [rax],al
  402024:	00 00                	add    BYTE PTR [rax],al
  402026:	00 00                	add    BYTE PTR [rax],al
  402028:	56                   	push   rsi
  402029:	10 00                	adc    BYTE PTR [rax],al
  40202b:	00 00                	add    BYTE PTR [rax],al
  40202d:	00 00                	add    BYTE PTR [rax],al
  40202f:	00 66 10             	add    BYTE PTR [rsi+0x10],ah
  402032:	00 00                	add    BYTE PTR [rax],al
  402034:	00 00                	add    BYTE PTR [rax],al
  402036:	00 00                	add    BYTE PTR [rax],al
  402038:	76 10                	jbe    0x40204a
  40203a:	00 00                	add    BYTE PTR [rax],al
  40203c:	00 00                	add    BYTE PTR [rax],al
  40203e:	00 00                	add    BYTE PTR [rax],al
  402040:	47                   	rex.RXB
  402041:	43                   	rex.XB
  402042:	43 3a 20             	rex.XB cmp spl,BYTE PTR [r8]
  402045:	28 47 4e             	sub    BYTE PTR [rdi+0x4e],al
  402048:	55                   	push   rbp
  402049:	29 20                	sub    DWORD PTR [rax],esp
  40204b:	31 30                	xor    DWORD PTR [rax],esi
  40204d:	2e 32 2e             	cs xor ch,BYTE PTR [rsi]
  402050:	31 20                	xor    DWORD PTR [rax],esp
  402052:	32 30                	xor    dh,BYTE PTR [rax]
  402054:	32 31                	xor    dh,BYTE PTR [rcx]
  402056:	30 31                	xor    BYTE PTR [rcx],dh
  402058:	33 30                	xor    esi,DWORD PTR [rax]
  40205a:	20 28                	and    BYTE PTR [rax],ch
  40205c:	52                   	push   rdx
  40205d:	65 64 20 48 61       	gs and BYTE PTR fs:[rax+0x61],cl
  402062:	74 20                	je     0x402084
  402064:	31 30                	xor    DWORD PTR [rax],esi
  402066:	2e 32 2e             	cs xor ch,BYTE PTR [rsi]
  402069:	31 2d 31 31 29 00    	xor    DWORD PTR [rip+0x293131],ebp        # 0x6951a0
  40206f:	2c 00                	sub    al,0x0
  402071:	00 00                	add    BYTE PTR [rax],al
  402073:	02 00                	add    al,BYTE PTR [rax]
  402075:	00 00                	add    BYTE PTR [rax],al
  402077:	00 00                	add    BYTE PTR [rax],al
  402079:	08 00                	or     BYTE PTR [rax],al
  40207b:	00 00                	add    BYTE PTR [rax],al
  40207d:	00 00                	add    BYTE PTR [rax],al
  40207f:	40 11 00             	rex adc DWORD PTR [rax],eax
  402082:	00 00                	add    BYTE PTR [rax],al
  402084:	00 00                	add    BYTE PTR [rax],al
  402086:	00 4d 18             	add    BYTE PTR [rbp+0x18],cl
	...
  40209d:	00 00                	add    BYTE PTR [rax],al
  40209f:	44 0b 00             	or     r8d,DWORD PTR [rax]
  4020a2:	00 04 00             	add    BYTE PTR [rax+rax*1],al
  4020a5:	00 00                	add    BYTE PTR [rax],al
  4020a7:	00 00                	add    BYTE PTR [rax],al
  4020a9:	08 01                	or     BYTE PTR [rcx],al
  4020ab:	b5 01                	mov    ch,0x1
  4020ad:	00 00                	add    BYTE PTR [rax],al
  4020af:	0c 14                	or     al,0x14
  4020b1:	00 00                	add    BYTE PTR [rax],al
  4020b3:	00 00                	add    BYTE PTR [rax],al
  4020b5:	00 00                	add    BYTE PTR [rax],al
  4020b7:	00 40 11             	add    BYTE PTR [rax+0x11],al
  4020ba:	00 00                	add    BYTE PTR [rax],al
  4020bc:	00 00                	add    BYTE PTR [rax],al
  4020be:	00 00                	add    BYTE PTR [rax],al
  4020c0:	4d 18 00             	rex.WRB sbb BYTE PTR [r8],r8b
	...
  4020cb:	00 02                	add    BYTE PTR [rdx],al
  4020cd:	98                   	cwde
  4020ce:	00 00                	add    BYTE PTR [rax],al
  4020d0:	00 03                	add    BYTE PTR [rbx],al
  4020d2:	d1 17                	rcl    DWORD PTR [rdi],1
  4020d4:	39 00                	cmp    DWORD PTR [rax],eax
  4020d6:	00 00                	add    BYTE PTR [rax],al
  4020d8:	03 08                	add    ecx,DWORD PTR [rax]
  4020da:	07                   	(bad)
  4020db:	34 00                	xor    al,0x0
  4020dd:	00 00                	add    BYTE PTR [rax],al
  4020df:	03 01                	add    eax,DWORD PTR [rcx]
  4020e1:	08 62 01             	or     BYTE PTR [rdx+0x1],ah
  4020e4:	00 00                	add    BYTE PTR [rax],al
  4020e6:	03 02                	add    eax,DWORD PTR [rdx]
  4020e8:	07                   	(bad)
  4020e9:	aa                   	stos   BYTE PTR [rdi],al
  4020ea:	00 00                	add    BYTE PTR [rax],al
  4020ec:	00 03                	add    BYTE PTR [rbx],al
  4020ee:	04 07                	add    al,0x7
  4020f0:	39 00                	cmp    DWORD PTR [rax],eax
  4020f2:	00 00                	add    BYTE PTR [rax],al
  4020f4:	04 4e                	add    al,0x4e
  4020f6:	00 00                	add    BYTE PTR [rax],al
  4020f8:	00 03                	add    BYTE PTR [rbx],al
  4020fa:	01 06                	add    DWORD PTR [rsi],eax
  4020fc:	64 01 00             	add    DWORD PTR fs:[rax],eax
  4020ff:	00 03                	add    BYTE PTR [rbx],al
  402101:	02 05 70 01 00 00    	add    al,BYTE PTR [rip+0x170]        # 0x402277
  402107:	05 04 05 69 6e       	add    eax,0x6e690504
  40210c:	74 00                	je     0x40210e
  40210e:	03 08                	add    ecx,DWORD PTR [rax]
  402110:	05 5e 00 00 00       	add    eax,0x5e
  402115:	06                   	(bad)
  402116:	08 03                	or     BYTE PTR [rbx],al
  402118:	01 06                	add    DWORD PTR [rsi],eax
  40211a:	6b 01 00             	imul   eax,DWORD PTR [rcx],0x0
  40211d:	00 03                	add    BYTE PTR [rbx],al
  40211f:	08 05 59 00 00 00    	or     BYTE PTR [rip+0x59],al        # 0x40217e
  402125:	03 08                	add    ecx,DWORD PTR [rax]
  402127:	07                   	(bad)
  402128:	2f                   	(bad)
  402129:	00 00                	add    BYTE PTR [rax],al
  40212b:	00 07                	add    BYTE PTR [rdi],al
  40212d:	08 93 00 00 00 08    	or     BYTE PTR [rbx+0x8000000],dl
  402133:	02 2e                	add    ch,BYTE PTR [rsi]
  402135:	02 00                	add    al,BYTE PTR [rax]
  402137:	00 04 30             	add    BYTE PTR [rax+rsi*1],al
  40213a:	18 40 00             	sbb    BYTE PTR [rax+0x0],al
  40213d:	00 00                	add    BYTE PTR [rax],al
  40213f:	04 94                	add    al,0x94
  402141:	00 00                	add    BYTE PTR [rax],al
  402143:	00 02                	add    BYTE PTR [rdx],al
  402145:	75 00                	jne    0x402147
  402147:	00 00                	add    BYTE PTR [rax],al
  402149:	04 31                	add    al,0x31
  40214b:	1c 47                	sbb    al,0x47
  40214d:	00 00                	add    BYTE PTR [rax],al
  40214f:	00 02                	add    BYTE PTR [rdx],al
  402151:	1f                   	(bad)
  402152:	00 00                	add    BYTE PTR [rax],al
  402154:	00 05 08 0f bd 00    	add    BYTE PTR [rip+0xbd0f08],al        # 0xfd3062
  40215a:	00 00                	add    BYTE PTR [rax],al
  40215c:	07                   	(bad)
  40215d:	08 c3                	or     bl,al
  40215f:	00 00                	add    BYTE PTR [rax],al
  402161:	00 09                	add    BYTE PTR [rcx],cl
  402163:	68 00 00 00 e1       	push   0xffffffffe1000000
  402168:	00 00                	add    BYTE PTR [rax],al
  40216a:	00 0a                	add    BYTE PTR [rdx],cl
  40216c:	e1 00                	loope  0x40216e
  40216e:	00 00                	add    BYTE PTR [rax],al
  402170:	0a 2e                	or     ch,BYTE PTR [rsi]
  402172:	01 00                	add    DWORD PTR [rax],eax
  402174:	00 0a                	add    BYTE PTR [rdx],cl
  402176:	34 01                	xor    al,0x1
  402178:	00 00                	add    BYTE PTR [rax],al
  40217a:	0a 2d 00 00 00 00    	or     ch,BYTE PTR [rip+0x0]        # 0x402180
  402180:	07                   	(bad)
  402181:	08 29                	or     BYTE PTR [rcx],ch
  402183:	01 00                	add    DWORD PTR [rax],eax
  402185:	00 0b                	add    BYTE PTR [rbx],cl
  402187:	09 00                	or     DWORD PTR [rax],eax
  402189:	00 00                	add    BYTE PTR [rax],al
  40218b:	20 05 0a 10 29 01    	and    BYTE PTR [rip+0x129100a],al        # 0x169319b
  402191:	00 00                	add    BYTE PTR [rax],al
  402193:	0c c2                	or     al,0xc2
  402195:	00 00                	add    BYTE PTR [rax],al
  402197:	00 05 0b 15 b1 00    	add    BYTE PTR [rip+0xb1150b],al        # 0xf136a8
  40219d:	00 00                	add    BYTE PTR [rax],al
  40219f:	00 0c 26             	add    BYTE PTR [rsi+riz*1],cl
  4021a2:	02 00                	add    al,BYTE PTR [rax]
  4021a4:	00 05 0c 15 b1 00    	add    BYTE PTR [rip+0xb1150c],al        # 0xf136b6
  4021aa:	00 00                	add    BYTE PTR [rax],al
  4021ac:	08 0c 8e             	or     BYTE PTR [rsi+rcx*4],cl
  4021af:	01 00                	add    DWORD PTR [rax],eax
  4021b1:	00 05 0d 0b 4f 01    	add    BYTE PTR [rip+0x14f0b0d],al        # 0x18f2cc4
  4021b7:	00 00                	add    BYTE PTR [rax],al
  4021b9:	10 0c 7e             	adc    BYTE PTR [rsi+rdi*2],cl
  4021bc:	00 00                	add    BYTE PTR [rax],al
  4021be:	00 05 0e 0c 2d 00    	add    BYTE PTR [rip+0x2d0c0e],al        # 0x6d2dd2
  4021c4:	00 00                	add    BYTE PTR [rax],al
  4021c6:	18 00                	sbb    BYTE PTR [rax],al
  4021c8:	04 e7                	add    al,0xe7
  4021ca:	00 00                	add    BYTE PTR [rax],al
  4021cc:	00 07                	add    BYTE PTR [rdi],al
  4021ce:	08 a0 00 00 00 07    	or     BYTE PTR [rax+0x7000000],ah
  4021d4:	08 94 00 00 00 09 68 	or     BYTE PTR [rax+rax*1+0x68090000],dl
  4021db:	00 00                	add    BYTE PTR [rax],al
  4021dd:	00 49 01             	add    BYTE PTR [rcx+0x1],cl
  4021e0:	00 00                	add    BYTE PTR [rax],al
  4021e2:	0a 49 01             	or     cl,BYTE PTR [rcx+0x1]
  4021e5:	00 00                	add    BYTE PTR [rax],al
  4021e7:	00 07                	add    BYTE PTR [rdi],al
  4021e9:	08 e7                	or     bh,ah
  4021eb:	00 00                	add    BYTE PTR [rax],al
  4021ed:	00 07                	add    BYTE PTR [rdi],al
  4021ef:	08 3a                	or     BYTE PTR [rdx],bh
  4021f1:	01 00                	add    DWORD PTR [rax],eax
  4021f3:	00 02                	add    BYTE PTR [rdx],al
  4021f5:	0a 00                	or     al,BYTE PTR [rax]
  4021f7:	00 00                	add    BYTE PTR [rax],al
  4021f9:	05 0f 03 e7 00       	add    eax,0xe7030f
  4021fe:	00 00                	add    BYTE PTR [rax],al
  402200:	04 55                	add    al,0x55
  402202:	01 00                	add    DWORD PTR [rax],eax
  402204:	00 0d f0 00 00 00    	add    BYTE PTR [rip+0xf0],cl        # 0x4022fa
  40220a:	00 01                	add    BYTE PTR [rcx],al
  40220c:	02 2b                	add    ch,BYTE PTR [rbx]
  40220e:	08 82 01 00 00 0c    	or     BYTE PTR [rdx+0xc000001],al
  402214:	a8 01                	test   al,0x1
  402216:	00 00                	add    BYTE PTR [rax],al
  402218:	02 2c 0e             	add    ch,BYTE PTR [rsi+rcx*1]
  40221b:	82                   	(bad)
  40221c:	01 00                	add    DWORD PTR [rax],eax
  40221e:	00 00                	add    BYTE PTR [rax],al
  402220:	00 0e                	add    BYTE PTR [rsi],cl
  402222:	4e 00 00             	rex.WRX add BYTE PTR [rax],r8b
  402225:	00 92 01 00 00 0f    	add    BYTE PTR [rdx+0xf000001],dl
  40222b:	39 00                	cmp    DWORD PTR [rax],eax
  40222d:	00 00                	add    BYTE PTR [rax],al
  40222f:	3f                   	(bad)
  402230:	00 10                	add    BYTE PTR [rax],dl
  402232:	20 01                	and    BYTE PTR [rcx],al
  402234:	01 2a                	add    DWORD PTR [rdx],ebp
  402236:	09 b7 01 00 00 0c    	or     DWORD PTR [rdi+0xc000001],esi
  40223c:	88 00                	mov    BYTE PTR [rax],al
  40223e:	00 00                	add    BYTE PTR [rax],al
  402240:	01 2b                	add    DWORD PTR [rbx],ebp
  402242:	10 55 01             	adc    BYTE PTR [rbp+0x1],dl
  402245:	00 00                	add    BYTE PTR [rax],al
  402247:	00 0c 36             	add    BYTE PTR [rsi+rsi*1],cl
  40224a:	02 00                	add    al,BYTE PTR [rax]
  40224c:	00 01                	add    BYTE PTR [rcx],al
  40224e:	2c 18                	sub    al,0x18
  402250:	66 01 00             	add    WORD PTR [rax],ax
  402253:	00 20                	add    BYTE PTR [rax],ah
  402255:	00 02                	add    BYTE PTR [rdx],al
  402257:	41 02 00             	add    al,BYTE PTR [r8]
  40225a:	00 01                	add    BYTE PTR [rcx],al
  40225c:	2d 03 92 01 00       	sub    eax,0x19203
  402261:	00 11                	add    BYTE PTR [rcx],dl
  402263:	d4                   	(bad)
  402264:	00 00                	add    BYTE PTR [rax],al
  402266:	00 06                	add    BYTE PTR [rsi],al
  402268:	2a 0e                	sub    cl,BYTE PTR [rsi]
  40226a:	76 00                	jbe    0x40226c
  40226c:	00 00                	add    BYTE PTR [rax],al
  40226e:	e3 01                	jrcxz  0x402271
  402270:	00 00                	add    BYTE PTR [rax],al
  402272:	0a 76 00             	or     dh,BYTE PTR [rsi+0x0]
  402275:	00 00                	add    BYTE PTR [rax],al
  402277:	0a 8d 00 00 00 0a    	or     cl,BYTE PTR [rbp+0xa000000]
  40227d:	2d 00 00 00 00       	sub    eax,0x0
  402282:	12 1a                	adc    bl,BYTE PTR [rdx]
  402284:	02 00                	add    al,BYTE PTR [rax]
  402286:	00 07                	add    BYTE PTR [rdi],al
  402288:	d3 01                	rol    DWORD PTR [rcx],cl
  40228a:	0e                   	(bad)
  40228b:	76 00                	jbe    0x40228d
  40228d:	00 00                	add    BYTE PTR [rax],al
  40228f:	ff 01                	inc    DWORD PTR [rcx]
  402291:	00 00                	add    BYTE PTR [rax],al
  402293:	0a 2d 00 00 00 0a    	or     ch,BYTE PTR [rip+0xa000000]        # 0xa402299
  402299:	2d 00 00 00 00       	sub    eax,0x0
  40229e:	13 54 00 00          	adc    edx,DWORD PTR [rax+rax*1+0x0]
  4022a2:	00 07                	add    BYTE PTR [rdi],al
  4022a4:	e2 01                	loop   0x4022a7
  4022a6:	0d 12 02 00 00       	or     eax,0x212
  4022ab:	0a 76 00             	or     dh,BYTE PTR [rsi+0x0]
  4022ae:	00 00                	add    BYTE PTR [rax],al
  4022b0:	00 14 db             	add    BYTE PTR [rbx+rbx*8],dl
  4022b3:	00 00                	add    BYTE PTR [rax],al
  4022b5:	00 02                	add    BYTE PTR [rdx],al
  4022b7:	ca 10 68             	retf   0x6810
  4022ba:	00 00                	add    BYTE PTR [rax],al
  4022bc:	00 c0                	add    al,al
  4022be:	25 00 00 00 00       	and    eax,0x0
  4022c3:	00 00                	add    BYTE PTR [rax],al
  4022c5:	cd 03                	int    0x3
  4022c7:	00 00                	add    BYTE PTR [rax],al
  4022c9:	00 00                	add    BYTE PTR [rax],al
  4022cb:	00 00                	add    BYTE PTR [rax],al
  4022cd:	01 9c 59 03 00 00 15 	add    DWORD PTR [rcx+rbx*2+0x15000003],ebx
  4022d4:	6b 65 79 00          	imul   esp,DWORD PTR [rbp+0x79],0x0
  4022d8:	02 ca                	add    cl,dl
  4022da:	33 2e                	xor    ebp,DWORD PTR [rsi]
  4022dc:	01 00                	add    DWORD PTR [rax],eax
  4022de:	00 0a                	add    BYTE PTR [rdx],cl
  4022e0:	00 00                	add    BYTE PTR [rax],al
  4022e2:	00 00                	add    BYTE PTR [rax],al
  4022e4:	00 00                	add    BYTE PTR [rax],al
  4022e6:	00 16                	add    BYTE PTR [rsi],dl
  4022e8:	39 01                	cmp    DWORD PTR [rcx],eax
  4022ea:	00 00                	add    BYTE PTR [rax],al
  4022ec:	02 ca                	add    cl,dl
  4022ee:	41 2d 00 00 00 86    	rex.B sub eax,0x86000000
	...
