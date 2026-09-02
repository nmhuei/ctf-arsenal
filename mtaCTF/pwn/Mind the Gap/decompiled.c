// Function: _DT_INIT @ 00101000

void _DT_INIT(void)

{
  if (PTR___gmon_start___00103fe8 != (undefined *)0x0) {
    (*(code *)PTR___gmon_start___00103fe8)();
  }
  return;
}



// Function: FUN_00101020 @ 00101020

void FUN_00101020(void)

{
  (*(code *)PTR_00103f90)();
  return;
}



// Function: _exit @ 00101030

/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void _exit(int __status)

{
  (*(code *)PTR__exit_00103f98)();
  return;
}



// Function: write @ 00101040

/* WARNING: Unknown calling convention -- yet parameter storage is locked */

ssize_t write(int __fd,void *__buf,size_t __n)

{
  ssize_t sVar1;
  
  sVar1 = (*(code *)PTR_write_00103fa0)();
  return sVar1;
}



// Function: __stack_chk_fail @ 00101050

void __stack_chk_fail(void)

{
  (*(code *)PTR___stack_chk_fail_00103fa8)();
  return;
}



// Function: memset @ 00101060

/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void * memset(void *__s,int __c,size_t __n)

{
  void *pvVar1;
  
  pvVar1 = (void *)(*(code *)PTR_memset_00103fb0)();
  return pvVar1;
}



// Function: read @ 00101070

/* WARNING: Unknown calling convention -- yet parameter storage is locked */

ssize_t read(int __fd,void *__buf,size_t __nbytes)

{
  ssize_t sVar1;
  
  sVar1 = (*(code *)PTR_read_00103fb8)();
  return sVar1;
}



// Function: memcpy @ 00101080

/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void * memcpy(void *__dest,void *__src,size_t __n)

{
  void *pvVar1;
  
  pvVar1 = (void *)(*(code *)PTR_memcpy_00103fc0)();
  return pvVar1;
}



// Function: dlsym @ 00101090

void dlsym(void)

{
  (*(code *)PTR_dlsym_00103fc8)();
  return;
}



// Function: posix_memalign @ 001010a0

/* WARNING: Unknown calling convention -- yet parameter storage is locked */

int posix_memalign(void **__memptr,size_t __alignment,size_t __size)

{
  int iVar1;
  
  iVar1 = (*(code *)PTR_posix_memalign_00103fd0)();
  return iVar1;
}



// Function: __cxa_finalize @ 001010b0

void __cxa_finalize(void)

{
  (*(code *)PTR___cxa_finalize_00103ff8)();
  return;
}



// Function: entry @ 001010c0

void processEntry entry(undefined8 param_1,undefined8 param_2)

{
  undefined1 auStack_8 [8];
  
  (*(code *)PTR___libc_start_main_00103fd8)
            (FUN_001015ad,param_2,&stack0x00000008,0,0,param_1,auStack_8);
  do {
                    /* WARNING: Do nothing block with infinite loop */
  } while( true );
}



// Function: FUN_001010f0 @ 001010f0

/* WARNING: Removing unreachable block (ram,0x00101103) */
/* WARNING: Removing unreachable block (ram,0x0010110f) */

void FUN_001010f0(void)

{
  return;
}



// Function: FUN_00101120 @ 00101120

/* WARNING: Removing unreachable block (ram,0x00101144) */
/* WARNING: Removing unreachable block (ram,0x00101150) */

void FUN_00101120(void)

{
  return;
}



// Function: _FINI_0 @ 00101160

void _FINI_0(void)

{
  if (DAT_00104020 == '\0') {
    if (PTR___cxa_finalize_00103ff8 != (undefined *)0x0) {
      __cxa_finalize(PTR_LOOP_00104008);
    }
    FUN_001010f0();
    DAT_00104020 = 1;
    return;
  }
  return;
}



// Function: _INIT_0 @ 001011a0

void _INIT_0(void)

{
  FUN_00101120();
  return;
}



// Function: FUN_001011c0 @ 001011c0

int FUN_001011c0(ushort param_1,undefined1 param_2)

{
  long lVar1;
  int iVar2;
  long lVar3;
  undefined4 *puVar4;
  int iVar5;
  int iVar6;
  long in_FS_OFFSET;
  
  iVar2 = DAT_00118860;
  lVar1 = *(long *)(in_FS_OFFSET + 0x28);
  if (param_1 == 0) {
    iVar5 = -1;
  }
  else {
    iVar6 = DAT_00118040 + -1;
    if (-1 < iVar6) {
      lVar3 = (long)iVar6;
      do {
        iVar5 = *(int *)(&DAT_00118060 + lVar3 * 4);
        if (*(ushort *)(&DAT_00118884 + (long)iVar5 * 8) == param_1) {
          iVar2 = (int)lVar3;
          if (iVar2 < iVar6) {
            puVar4 = (undefined4 *)(&DAT_00118060 + (long)iVar2 * 4);
            do {
              *puVar4 = puVar4[1];
              puVar4 = puVar4 + 1;
            } while (puVar4 != (undefined4 *)
                               (&DAT_00118064 +
                               ((ulong)(uint)((DAT_00118040 + -2) - iVar2) + (long)iVar2) * 4));
          }
          DAT_00118040 = iVar6;
          (&DAT_00118886)[(long)iVar5 * 8] = 1;
          (&DAT_00118887)[(long)iVar5 * 8] = param_2;
          goto LAB_0010129b;
        }
        lVar3 = lVar3 + -1;
      } while (-1 < (int)lVar3);
    }
    if (DAT_00118860 < 0x200) {
      if ((ulong)DAT_00104010 + (ulong)param_1 < 0x10001) {
        lVar3 = (long)DAT_00118860;
        DAT_00118860 = DAT_00118860 + 1;
        *(uint *)(&DAT_00118880 + lVar3 * 8) = DAT_00104010;
        *(ushort *)(&DAT_00118884 + lVar3 * 8) = param_1;
        (&DAT_00118886)[lVar3 * 8] = 1;
        (&DAT_00118887)[lVar3 * 8] = param_2;
        DAT_00104010 = param_1 + DAT_00104010;
        iVar5 = iVar2;
      }
      else {
        iVar5 = -1;
      }
    }
    else {
      iVar5 = -1;
    }
  }
LAB_0010129b:
  if (lVar1 == *(long *)(in_FS_OFFSET + 0x28)) {
    return iVar5;
  }
                    /* WARNING: Subroutine does not return */
  __stack_chk_fail();
}



// Function: FUN_0010132a @ 0010132a

void FUN_0010132a(long *param_1)

{
  long lVar1;
  long in_FS_OFFSET;
  
  lVar1 = *(long *)(in_FS_OFFSET + 0x28);
  if (param_1 != (long *)0x0) {
    *param_1 = *param_1 + -1;
  }
  if (lVar1 == *(long *)(in_FS_OFFSET + 0x28)) {
    return;
  }
                    /* WARNING: Subroutine does not return */
  __stack_chk_fail();
}



// Function: FUN_00101361 @ 00101361

void FUN_00101361(void)

{
  long lVar1;
  undefined8 *puVar2;
  long in_FS_OFFSET;
  
  lVar1 = *(long *)(in_FS_OFFSET + 0x28);
  for (puVar2 = DAT_00119880; puVar2 != (undefined8 *)0x0; puVar2 = (undefined8 *)*puVar2) {
    if ((code *)puVar2[1] != (code *)0x0) {
      (*(code *)puVar2[1])(puVar2[2]);
    }
  }
  if (lVar1 != *(long *)(in_FS_OFFSET + 0x28)) {
                    /* WARNING: Subroutine does not return */
    __stack_chk_fail();
  }
  return;
}



// Function: FUN_001013be @ 001013be

undefined8 FUN_001013be(long param_1,ulong param_2)

{
  long lVar1;
  ssize_t sVar2;
  undefined8 uVar3;
  ulong uVar4;
  long in_FS_OFFSET;
  
  lVar1 = *(long *)(in_FS_OFFSET + 0x28);
  if (param_2 == 0) {
    uVar3 = 0;
  }
  else {
    uVar4 = 0;
    do {
      sVar2 = read(0,(void *)(param_1 + uVar4),param_2 - uVar4);
      if (sVar2 < 1) {
        uVar3 = 0xffffffff;
        goto LAB_0010141a;
      }
      uVar4 = uVar4 + sVar2;
    } while (uVar4 < param_2);
    uVar3 = 0;
  }
LAB_0010141a:
  if (lVar1 == *(long *)(in_FS_OFFSET + 0x28)) {
    return uVar3;
  }
                    /* WARNING: Subroutine does not return */
  __stack_chk_fail();
}



// Function: FUN_00101438 @ 00101438

void FUN_00101438(long param_1,ulong param_2)

{
  long lVar1;
  ssize_t sVar2;
  ulong uVar3;
  long in_FS_OFFSET;
  
  lVar1 = *(long *)(in_FS_OFFSET + 0x28);
  if (param_2 != 0) {
    uVar3 = 0;
    do {
      sVar2 = write(1,(void *)(param_1 + uVar3),param_2 - uVar3);
      if (sVar2 < 1) break;
      uVar3 = uVar3 + sVar2;
    } while (uVar3 < param_2);
  }
  if (lVar1 == *(long *)(in_FS_OFFSET + 0x28)) {
    return;
  }
                    /* WARNING: Subroutine does not return */
  __stack_chk_fail();
}



// Function: FUN_0010149f @ 0010149f

void FUN_0010149f(undefined1 param_1,undefined8 param_2,uint param_3)

{
  long in_FS_OFFSET;
  undefined1 local_23;
  undefined1 local_22;
  undefined1 local_21;
  long local_20;
  
  local_20 = *(long *)(in_FS_OFFSET + 0x28);
  local_22 = (undefined1)(param_3 >> 8);
  local_21 = (undefined1)param_3;
  local_23 = param_1;
  FUN_00101438(&local_23,3);
  if ((short)param_3 != 0) {
    FUN_00101438(param_2,param_3 & 0xffff);
  }
  if (local_20 == *(long *)(in_FS_OFFSET + 0x28)) {
    return;
  }
                    /* WARNING: Subroutine does not return */
  __stack_chk_fail();
}



// Function: FUN_00101504 @ 00101504

void FUN_00101504(byte *param_1,byte *param_2,long param_3,int *param_4,byte *param_5)

{
  byte bVar1;
  long lVar2;
  byte *pbVar3;
  byte *pbVar4;
  long in_FS_OFFSET;
  
  lVar2 = *(long *)(in_FS_OFFSET + 0x28);
  if (param_3 != 0) {
    pbVar3 = param_2 + param_3;
    do {
      bVar1 = *param_2;
      if ((*param_4 == 0) ||
         ((*(uint *)(&DAT_00102080 + (ulong)(bVar1 >> 5) * 4) >> (bVar1 & 0x1f) & 1) == 0)) {
        pbVar4 = param_1 + 1;
        if (param_5 < pbVar4) break;
        *param_1 = bVar1;
      }
      else {
        pbVar4 = param_1 + 3;
        if (param_5 < pbVar4) break;
        *param_1 = 0x25;
        param_1[1] = "0123456789ABCDEF"[bVar1 >> 4];
        param_1[2] = "0123456789ABCDEF"[bVar1 & 0xf];
      }
      param_2 = param_2 + 1;
      param_1 = pbVar4;
    } while (param_2 != pbVar3);
  }
  if (lVar2 == *(long *)(in_FS_OFFSET + 0x28)) {
    return;
  }
                    /* WARNING: Subroutine does not return */
  __stack_chk_fail();
}



// Function: FUN_001015ad @ 001015ad

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined8 FUN_001015ad(void)

{
  ushort uVar1;
  undefined1 uVar2;
  undefined1 uVar3;
  undefined1 uVar4;
  int iVar5;
  uint uVar6;
  undefined8 uVar7;
  ulong uVar8;
  undefined8 *puVar9;
  ushort uVar10;
  long lVar11;
  ulong __n;
  size_t __n_00;
  byte *pbVar12;
  void *__src;
  long in_FS_OFFSET;
  undefined4 local_54;
  void *local_50;
  undefined1 local_45;
  undefined1 local_44;
  undefined1 local_43;
  undefined1 local_42;
  undefined1 local_41;
  long local_40;
  
  local_40 = *(long *)(in_FS_OFFSET + 0x28);
  iVar5 = posix_memalign(&local_50,0x10000,0x10000);
  if ((iVar5 != 0) || (DAT_00119890 = local_50, local_50 == (void *)0x0)) {
                    /* WARNING: Subroutine does not return */
    _exit(1);
  }
  memset(local_50,0,0x10000);
  *(void **)((long)local_50 + 0x300) = local_50;
  uVar7 = dlsym(0,"toupper");
  *(undefined8 *)((long)local_50 + 0x308) = uVar7;
  _DAT_00119888 = _DAT_00119888 + 1;
  do {
    iVar5 = FUN_001013be(&local_43,3);
    uVar4 = local_41;
    uVar3 = local_42;
    uVar2 = local_43;
    if (iVar5 < 0) {
LAB_001016b6:
      FUN_00101361();
      if (local_40 != *(long *)(in_FS_OFFSET + 0x28)) {
                    /* WARNING: Subroutine does not return */
        __stack_chk_fail();
      }
      return 0;
    }
    uVar1 = CONCAT11(local_42,local_41);
    if (0x4000 < uVar1) {
      FUN_0010149f(3,0,0);
      goto LAB_001016b6;
    }
    if (uVar1 == 0) {
      switch(local_43) {
      case 0x10:
        __n_00 = 0;
        goto LAB_001017ac;
      case 0x11:
switchD_00101696_caseD_11:
        local_54 = 1;
        iVar5 = FUN_001011c0(CONCAT11(uVar3,uVar4),0);
        if (iVar5 < 0) {
          FUN_0010149f(2,0,0);
        }
        else {
          FUN_00101504((ulong)*(uint *)(&DAT_00118880 + (long)iVar5 * 8) + (long)DAT_00119890,
                       &DAT_00114040,CONCAT11(uVar3,uVar4),&local_54,(long)DAT_00119890 + 0x10000);
          FUN_0010149f(0,"rerouted",8);
        }
        break;
      case 0x12:
switchD_00101696_caseD_12:
        if (uVar1 < 2) {
          FUN_0010149f(3,0,0);
        }
        else {
          iVar5 = FUN_001011c0(CONCAT11(DAT_00114040,DAT_00114041),0);
          if (iVar5 < 0) {
            FUN_0010149f(2,0,0);
          }
          else {
            local_45 = (undefined1)((uint)iVar5 >> 8);
            local_44 = (undefined1)iVar5;
            FUN_0010149f(0,&local_45,2);
          }
        }
        break;
      case 0x13:
switchD_00101696_caseD_13:
        if (uVar1 < 2) {
          FUN_0010149f(3,0,0);
        }
        else {
          uVar6 = (uint)CONCAT11(DAT_00114040,DAT_00114041);
          if ((int)uVar6 < DAT_00118860) {
            lVar11 = (long)(int)uVar6;
            if ((&DAT_00118886)[lVar11 * 8] == '\0') {
              iVar5 = -1;
            }
            else if ((&DAT_00118887)[lVar11 * 8] == '\0') {
              (&DAT_00118886)[lVar11 * 8] = 0;
              lVar11 = (long)DAT_00118040;
              DAT_00118040 = DAT_00118040 + 1;
              *(uint *)(&DAT_00118060 + lVar11 * 4) = uVar6;
              iVar5 = 0;
            }
            else {
              iVar5 = -1;
            }
          }
          else {
            iVar5 = -1;
          }
          FUN_0010149f((iVar5 != 0) * '\x02',0,0);
        }
        break;
      case 0x14:
switchD_00101696_caseD_14:
        if (uVar1 < 2) {
          FUN_0010149f(3,0,0);
        }
        else {
          uVar6 = (uint)CONCAT11(DAT_00114040,DAT_00114041);
          if ((((int)uVar6 < DAT_00118860) && ((&DAT_00118886)[(long)(int)uVar6 * 8] != '\0')) &&
             ((&DAT_00118887)[(long)(int)uVar6 * 8] == '\0')) {
            uVar8 = (ulong)(int)(CONCAT11(uVar3,uVar4) - 2);
            __n = (ulong)*(ushort *)(&DAT_00118884 + (long)(int)uVar6 * 8);
            if (uVar8 < *(ushort *)(&DAT_00118884 + (long)(int)uVar6 * 8)) {
              __n = uVar8;
            }
            memcpy((void *)((ulong)*(uint *)(&DAT_00118880 + (long)(int)uVar6 * 8) +
                           (long)DAT_00119890),&DAT_00114042,__n);
            FUN_0010149f(0,0,0);
          }
          else {
            FUN_0010149f(2,0,0);
          }
        }
        break;
      case 0x15:
switchD_00101696_caseD_15:
        iVar5 = FUN_001011c0(0x18,1);
        if (iVar5 < 0) {
          FUN_0010149f(2,0,0);
        }
        else {
          puVar9 = (undefined8 *)
                   ((ulong)*(uint *)(&DAT_00118880 + (long)iVar5 * 8) + (long)DAT_00119890);
          *puVar9 = DAT_00119880;
          puVar9[1] = FUN_0010132a;
          puVar9[2] = &DAT_00119888;
          DAT_00119880 = puVar9;
          FUN_0010149f(0,0,0);
        }
        break;
      case 0x16:
switchD_00101696_caseD_16:
        FUN_0010149f(0,0,0);
        FUN_00101361();
                    /* WARNING: Subroutine does not return */
        _exit(0);
      default:
switchD_00101696_default:
        FUN_0010149f(0xff,0,0);
      }
    }
    else {
      uVar10 = CONCAT11(local_42,local_41);
      iVar5 = FUN_001013be(&DAT_00114040,(ulong)uVar10);
      if (iVar5 < 0) goto LAB_001016b6;
      switch(uVar2) {
      case 0x10:
        pbVar12 = &DAT_00114040;
        __n_00 = 0;
        do {
          __n_00 = __n_00 + (long)(int)((-(uint)((*(uint *)(&DAT_00102080 +
                                                           (ulong)(*pbVar12 >> 5) * 4) >>
                                                  (*pbVar12 & 0x1f) & 1) == 0) & 0xfffffffe) + 3);
          pbVar12 = pbVar12 + 1;
        } while (&DAT_00114040 + uVar10 != pbVar12);
        break;
      case 0x11:
        goto switchD_00101696_caseD_11;
      case 0x12:
        goto switchD_00101696_caseD_12;
      case 0x13:
        goto switchD_00101696_caseD_13;
      case 0x14:
        goto switchD_00101696_caseD_14;
      case 0x15:
        goto switchD_00101696_caseD_15;
      case 0x16:
        goto switchD_00101696_caseD_16;
      default:
        goto switchD_00101696_default;
      }
LAB_001017ac:
      local_54 = 0;
      __src = (void *)((long)DAT_00119890 + 0x100);
      if (0xff00 < __n_00) {
        __n_00 = 0xff00;
      }
      uVar10 = 0x80;
      if (uVar1 < 0x81) {
        uVar10 = uVar1;
      }
      FUN_00101504(__src,&DAT_00114040,uVar10,&local_54,(long)DAT_00119890 + 0x180);
      _DAT_00104040 = 0x2079656e72756f6a;
      _DAT_00104048 = 0x72656e6e616c70;
      DAT_0010404f = 0x20;
      uRam0000000000104050 = 0x656e696c66666f;
      _DAT_00104057 = 0x3d7972657571203b;
      memcpy(&DAT_0010405f,__src,__n_00);
      FUN_0010149f(0,&DAT_00104040,(int)__n_00 + 0x1fU & 0xffff);
    }
  } while( true );
}



// Function: _DT_FINI @ 00101bb4

void _DT_FINI(void)

{
  return;
}



// Function: __libc_start_main @ 0011a000

/* WARNING: Control flow encountered bad instruction data */

void __libc_start_main(void)

{
                    /* WARNING: Bad instruction - Truncating control flow here */
  halt_baddata();
}



// Function: _ITM_deregisterTMCloneTable @ 0011a008

/* WARNING: Control flow encountered bad instruction data */

void _ITM_deregisterTMCloneTable(void)

{
                    /* WARNING: Bad instruction - Truncating control flow here */
  halt_baddata();
}



// Function: _exit @ 0011a010

/* WARNING: Control flow encountered bad instruction data */
/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void _exit(int __status)

{
                    /* WARNING: Bad instruction - Truncating control flow here */
  halt_baddata();
}



// Function: write @ 0011a018

/* WARNING: Control flow encountered bad instruction data */
/* WARNING: Unknown calling convention -- yet parameter storage is locked */

ssize_t write(int __fd,void *__buf,size_t __n)

{
                    /* WARNING: Bad instruction - Truncating control flow here */
  halt_baddata();
}



// Function: __stack_chk_fail @ 0011a020

/* WARNING: Control flow encountered bad instruction data */

void __stack_chk_fail(void)

{
                    /* WARNING: Bad instruction - Truncating control flow here */
  halt_baddata();
}



// Function: memset @ 0011a028

/* WARNING: Control flow encountered bad instruction data */
/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void * memset(void *__s,int __c,size_t __n)

{
                    /* WARNING: Bad instruction - Truncating control flow here */
  halt_baddata();
}



// Function: read @ 0011a030

/* WARNING: Control flow encountered bad instruction data */
/* WARNING: Unknown calling convention -- yet parameter storage is locked */

ssize_t read(int __fd,void *__buf,size_t __nbytes)

{
                    /* WARNING: Bad instruction - Truncating control flow here */
  halt_baddata();
}



// Function: __gmon_start__ @ 0011a038

/* WARNING: Control flow encountered bad instruction data */

void __gmon_start__(void)

{
                    /* WARNING: Bad instruction - Truncating control flow here */
  halt_baddata();
}



// Function: memcpy @ 0011a040

/* WARNING: Control flow encountered bad instruction data */
/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void * memcpy(void *__dest,void *__src,size_t __n)

{
                    /* WARNING: Bad instruction - Truncating control flow here */
  halt_baddata();
}



// Function: dlsym @ 0011a048

/* WARNING: Control flow encountered bad instruction data */

void dlsym(void)

{
                    /* WARNING: Bad instruction - Truncating control flow here */
  halt_baddata();
}



// Function: posix_memalign @ 0011a050

/* WARNING: Control flow encountered bad instruction data */
/* WARNING: Unknown calling convention -- yet parameter storage is locked */

int posix_memalign(void **__memptr,size_t __alignment,size_t __size)

{
                    /* WARNING: Bad instruction - Truncating control flow here */
  halt_baddata();
}



// Function: _ITM_registerTMCloneTable @ 0011a058

/* WARNING: Control flow encountered bad instruction data */

void _ITM_registerTMCloneTable(void)

{
                    /* WARNING: Bad instruction - Truncating control flow here */
  halt_baddata();
}



// Function: __cxa_finalize @ 0011a060

/* WARNING: Control flow encountered bad instruction data */

void __cxa_finalize(void)

{
                    /* WARNING: Bad instruction - Truncating control flow here */
  halt_baddata();
}



