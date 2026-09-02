using System;

namespace Models;

public struct MEMORY_BASIC_INFORMATION
{
	public IntPtr BaseAddress;

	public IntPtr AllocationBase;

	public uint AllocationProtect;

	public IntPtr RegionSize;

	public uint State;

	public uint Protect;

	public uint Type;
}
