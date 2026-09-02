using System;

namespace Models;

public struct _PROCESS_BASIC_INFORMATION
{
	public IntPtr ExitStatus;

	public IntPtr PebBaseAddress;

	public IntPtr AffinityMask;

	public IntPtr BasePriority;

	public UIntPtr UniqueProcessId;

	public IntPtr InheritedFromUniqueProcessId;

	public int Size => 6 * IntPtr.Size;
}
