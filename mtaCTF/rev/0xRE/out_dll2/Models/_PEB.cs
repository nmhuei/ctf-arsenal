using System;
using System.Runtime.InteropServices;

namespace Models;

[StructLayout(LayoutKind.Explicit, Size = 16)]
public struct _PEB
{
	[FieldOffset(0)]
	public byte InheritedAddressSpace;

	[FieldOffset(1)]
	public byte ReadImageFileExecOptions;

	[FieldOffset(2)]
	public byte BeingDebugged;

	[FieldOffset(3)]
	public byte Spare;

	[FieldOffset(4)]
	public IntPtr Mutant;

	[FieldOffset(8)]
	public IntPtr ImageBaseAddress;

	[FieldOffset(12)]
	public IntPtr Ldr;

	[FieldOffset(16)]
	public IntPtr ProcessParameters;
}
