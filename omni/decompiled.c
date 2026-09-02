// Function: sub_11000 (0x11000)
void __fastcall sub_11000(int a1, int a2)
{
  dword_15018 = a1 ^ (a2 << 16);
}


// Function: WinCaptureDeviceControl (0x11010)
__int64 __fastcall WinCaptureDeviceControl(__int64 a1, __int64 a2)
{
  int *v2; // rsi
  unsigned int v3; // r8d
  __int64 v4; // rax
  __int64 v5; // rdx
  unsigned int v6; // edx
  int v8; // r8d
  __int64 v9; // rcx
  __int64 v10; // rdx
  unsigned int v11; // ecx
  __int64 v12; // rsi
  unsigned int v13; // edx
  __int64 v14; // rcx
  __int64 v15; // r8
  __int64 v16; // rdx
  _QWORD *v17; // rsi
  char *v18; // rdi

  v2 = *(int **)(a2 + 24);
  v3 = *(_DWORD *)(a2 + 124);
  v4 = a2;
  switch ( *(_DWORD *)(a2 + 128) )
  {
    case 0xC2002000:
      if ( v3 <= 0x1007 )
        goto LABEL_33;
      v5 = (unsigned int)*v2;
      if ( (unsigned int)v5 > 3 )
        goto LABEL_33;
      dword_19020[v5] = v2[1];
      qmemcpy((char *)&unk_15020 + 4096 * v5, v2 + 2, 0x1000uLL);
      goto LABEL_5;
    case 0xC2002004:
      if ( v3 <= 3 )
        goto LABEL_33;
      v8 = *v2;
      if ( (unsigned int)(*v2 - 1) > 0x1FF )
        goto LABEL_33;
      if ( qword_15010 )
        goto LABEL_36;
      v9 = (unsigned int)dword_19030;
      if ( dword_19030 + ((v8 + 15) & 0xFFFFFFF0) <= 0x10000 )
      {
        dword_19030 += (v8 + 15) & 0xFFFFFFF0;
        dword_15008 = v8;
        qword_15010 = (__int64)&unk_19040 + v9;
        goto LABEL_5;
      }
      dword_15008 = *v2;
LABEL_35:
      v6 = -1073741670;
      goto LABEL_6;
    case 0xC2002008:
      if ( qword_15000 )
        goto LABEL_36;
      v10 = (unsigned int)dword_19030;
      if ( (unsigned int)(dword_19030 + 16) > 0x10000 )
        goto LABEL_35;
      dword_19030 += 16;
      qword_15000 = (__int64)&unk_19040 + v10;
      *(_QWORD *)((char *)&unk_19040 + v10) = 1262835969LL;
      goto LABEL_5;
    case 0xC200200C:
      if ( v3 <= 3 || (v11 = *v2, (unsigned int)*v2 > 3) || (v12 = v11, v13 = dword_19020[v11], dword_15008 < v13) )
      {
LABEL_33:
        v6 = -1073741811;
      }
      else
      {
        sub_11000(v11, v13);
        v14 = qword_15010;
        v16 = *(unsigned int *)(v15 + 4 * v12);
        if ( qword_15010 )
        {
          if ( (unsigned int)v16 > 0x1000 )
            v16 = 4096LL;
          v17 = (_QWORD *)((char *)&unk_15020 + 4096 * v12);
          if ( (unsigned int)v16 >= 8 )
          {
            v18 = (char *)((qword_15010 + 8) & 0xFFFFFFFFFFFFFFF8uLL);
            *(_QWORD *)qword_15010 = *v17;
            *(_QWORD *)(v14 + (unsigned int)v16 - 8) = *(_QWORD *)((char *)v17 + (unsigned int)v16 - 8);
            qmemcpy(v18, (char *)v17 - (v14 - (_QWORD)v18), 8LL * ((unsigned int)(v16 + v14 - (_DWORD)v18) >> 3));
          }
          else if ( (v16 & 4) != 0 )
          {
            *(_DWORD *)qword_15010 = *(_DWORD *)v17;
            *(_DWORD *)(v14 + v16 - 4) = *(_DWORD *)((char *)v17 + v16 - 4);
          }
          else if ( (_DWORD)v16 )
          {
            *(_BYTE *)qword_15010 = *(_BYTE *)v17;
            if ( (v16 & 2) != 0 )
              *(_WORD *)(v14 + v16 - 2) = *(_WORD *)((char *)v17 + v16 - 2);
          }
LABEL_5:
          v6 = 0;
        }
        else
        {
LABEL_32:
          v6 = -1073741808;
        }
      }
      goto LABEL_6;
    case 0xC2002010:
      if ( !qword_15000 )
        goto LABEL_32;
      if ( *(_DWORD *)qword_15000 != 1262835969 )
      {
LABEL_36:
        v6 = -1073741790;
LABEL_6:
        *(_DWORD *)(v4 + 56) = 0;
        *(_DWORD *)(v4 + 48) = v6;
        return v6;
      }
      if ( !*(_DWORD *)(qword_15000 + 4) )
      {
        v6 = -1073741790;
        goto LABEL_6;
      }
      if ( *(_DWORD *)(a2 + 120) <= 0x7Fu )
      {
        v6 = -1073741789;
        goto LABEL_6;
      }
      *((_QWORD *)v2 + 4) = 0LL;
      strcpy((char *)v2, "CTF{placeholder_set_at_runtime}");
      *((_QWORD *)v2 + 5) = 0LL;
      *((_QWORD *)v2 + 6) = 0LL;
      *((_QWORD *)v2 + 7) = 0LL;
      *((_QWORD *)v2 + 8) = 0LL;
      *((_QWORD *)v2 + 9) = 0LL;
      *((_QWORD *)v2 + 10) = 0LL;
      *((_QWORD *)v2 + 11) = 0LL;
      *((_QWORD *)v2 + 12) = 0LL;
      *((_QWORD *)v2 + 13) = 0LL;
      *((_QWORD *)v2 + 14) = 0LL;
      *((_QWORD *)v2 + 15) = 0LL;
      *(_DWORD *)(a2 + 56) = 128;
      *(_DWORD *)(a2 + 48) = 0;
      return 0LL;
    default:
      goto LABEL_32;
  }
}


// Function: DriverEntry (0x11390)
NTSTATUS __stdcall DriverEntry(PDRIVER_OBJECT DriverObject, PUNICODE_STRING RegistryPath)
{
  dword_19030 = 0;
  qword_15010 = 0LL;
  qword_15000 = 0LL;
  DriverObject->MajorFunction[7] = (PDRIVER_DISPATCH)WinCaptureDeviceControl;
  return 0;
}


