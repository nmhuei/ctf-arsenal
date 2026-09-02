using System;
using System.Runtime.InteropServices;

namespace newClient.Utilities;

public class WindowStation
{
	private const uint MAXIMUM_ALLOWED = 33554432u;

	private const uint GENERIC_ALL = 268435456u;

	private const uint DF_ALLOWOTHERACCOUNTHOOK = 1u;

	private const int UOI_NAME = 2;

	private const uint WINSTA_ACCESSCLIPBOARD = 4u;

	private const uint WINSTA_ACCESSGLOBALATOMS = 32u;

	private const uint WINSTA_CREATEDESKTOP = 8u;

	private const uint WINSTA_ENUMDESKTOPS = 1u;

	private const uint WINSTA_ENUMERATE = 256u;

	private const uint WINSTA_EXITWINDOWS = 64u;

	private const uint WINSTA_READATTRIBUTES = 2u;

	private const uint WINSTA_READSCREEN = 512u;

	private const uint WINSTA_WRITEATTRIBUTES = 16u;

	private const int DESKTOP_READOBJECTS = 1;

	private const int DESKTOP_CREATEWINDOW = 2;

	private const int DESKTOP_CREATEMENU = 4;

	private const int DESKTOP_HOOKCONTROL = 8;

	private const int DESKTOP_JOURNALRECORD = 16;

	private const int DESKTOP_JOURNALPLAYBACK = 32;

	private const int DESKTOP_ENUMERATE = 64;

	private const int DESKTOP_WRITEOBJECTS = 128;

	private const int DESKTOP_SWITCHDESKTOP = 256;

	[DllImport("user32.dll", SetLastError = true)]
	public static extern IntPtr OpenInputDesktop(uint dwFlags, bool fInherit, uint dwDesiredAccess);

	[DllImport("user32.dll", SetLastError = true)]
	public static extern bool GetUserObjectInformation(IntPtr hObj, int nIndex, byte[] pvInfo, uint nLength, ref uint lpnLengthNeeded);

	[DllImport("user32.dll")]
	public static extern IntPtr OpenWindowStation(string lpszWinSta, bool fInherit, uint dwDesiredAccess);

	[DllImport("user32.dll")]
	public static extern bool SetProcessWindowStation(IntPtr hWinSta);

	[DllImport("user32.dll", SetLastError = true)]
	public static extern IntPtr OpenDesktop(string lpszDesktop, uint dwFlags, bool fInherit, uint dwDesiredAccess);

	[DllImport("user32.dll", SetLastError = true)]
	public static extern bool CloseDesktop(IntPtr hDesktop);

	[DllImport("user32.dll")]
	public static extern bool SetThreadDesktop(IntPtr hDesktop);

	public static void SetWindowStation()
	{
		try
		{
			if (!Environment.UserName.ToLower().Equals("system"))
			{
				return;
			}
			IntPtr intPtr = OpenWindowStation("WinSta0", fInherit: false, 895u);
			if (intPtr == IntPtr.Zero || !SetProcessWindowStation(intPtr))
			{
				return;
			}
			IntPtr intPtr2 = OpenInputDesktop(1u, fInherit: false, 33554432u);
			if (!(intPtr2 == IntPtr.Zero))
			{
				byte[] array = new byte[256];
				uint lpnLengthNeeded = 0u;
				GetUserObjectInformation(intPtr2, 2, array, (uint)array.Length, ref lpnLengthNeeded);
				if (lpnLengthNeeded != 0)
				{
					SetThreadDesktop(intPtr2);
				}
			}
		}
		catch (Exception)
		{
		}
	}
}
