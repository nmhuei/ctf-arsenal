using System;

namespace Models;

public struct SYSTEM_INFO
{
	public ushort processorArchitecture;

	private ushort reserved;

	public uint pageSize;

	public UIntPtr minimumApplicationAddress;

	public UIntPtr maximumApplicationAddress;

	public UIntPtr activeProcessorMask;

	public uint numberOfProcessors;

	public uint processorType;

	public uint allocationGranularity;

	public ushort processorLevel;

	public ushort processorRevision;
}
