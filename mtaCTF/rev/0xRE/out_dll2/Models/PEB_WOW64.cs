using System.Runtime.InteropServices;

namespace Models;

public struct PEB_WOW64
{
	[MarshalAs(UnmanagedType.ByValArray, SizeConst = 2)]
	private readonly byte[] Reserved_1;

	public byte BeingDebugged;

	[MarshalAs(UnmanagedType.ByValArray, SizeConst = 1)]
	private readonly byte[] Reserved2;

	[MarshalAs(UnmanagedType.ByValArray, SizeConst = 2)]
	private readonly long[] Reserved3;

	public long Ldr;

	public long ProcessParameters;

	[MarshalAs(UnmanagedType.ByValArray, SizeConst = 3)]
	private readonly long[] Reserved4;

	private readonly long AtlThunkSListPtr;

	private readonly long Reserved5;

	private readonly uint Reserved6;

	private readonly long Reserved7;

	private readonly uint Reserved8;

	private readonly uint AtlThunkSListPtr32;

	[MarshalAs(UnmanagedType.ByValArray, SizeConst = 45)]
	private readonly long[] Reserved9;

	[MarshalAs(UnmanagedType.ByValArray, SizeConst = 96)]
	private readonly byte[] Reserved10;

	private readonly long PostProcessInitRoutine;

	[MarshalAs(UnmanagedType.ByValArray, SizeConst = 128)]
	private readonly byte[] Reserved11;

	[MarshalAs(UnmanagedType.ByValArray, SizeConst = 1)]
	private readonly long[] Reserved12;

	public uint SessionId;
}
