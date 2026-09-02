using System;
using System.Runtime.InteropServices;

namespace Models;

[StructLayout(LayoutKind.Sequential, CharSet = CharSet.Unicode)]
public struct STARTUPINFOEX
{
	public STARTUPINFO StartupInfo;

	public IntPtr lpAttributeList;
}
