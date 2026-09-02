using System;
using System.Runtime.InteropServices;
using System.Text;

namespace Session1;

public static class NtApi32
{
	public delegate IntPtr HookProc(int nCode, IntPtr wParam, IntPtr lParam);

	public const uint CF_TEXT = 1u;

	public const uint CF_DSPBITMAP = 2u;

	public const uint CF_HDROP = 15u;

	[DllImport("user32.dll", SetLastError = true)]
	public static extern IntPtr GetClipboardData(uint uFormat);

	[DllImport("user32.dll", SetLastError = true)]
	public static extern bool IsClipboardFormatAvailable(uint format);

	[DllImport("user32.dll", SetLastError = true)]
	public static extern bool OpenClipboard(IntPtr hWndNewOwner);

	[DllImport("user32.dll", SetLastError = true)]
	public static extern bool CloseClipboard();

	[DllImport("kernel32.dll")]
	public static extern IntPtr GlobalLock(IntPtr hMem);

	[DllImport("kernel32.dll")]
	public static extern bool GlobalUnlock(IntPtr hMem);

	[DllImport("kernel32.dll")]
	public static extern int GlobalSize(IntPtr hMem);

	[DllImport("user32.dll", CharSet = CharSet.Auto)]
	public static extern IntPtr GetClipboardFormatName(uint format, StringBuilder lpszFormatName, int cchMaxCount);

	[DllImport("shell32.dll", CharSet = CharSet.Unicode, SetLastError = true)]
	public static extern uint DragQueryFile(IntPtr hDrop, uint iFile, [Out] char[] lpszFile, uint cch);

	[DllImport("user32.dll")]
	public static extern IntPtr FindWindowA([In][MarshalAs(UnmanagedType.LPStr)] string lpClassName, [In][MarshalAs(UnmanagedType.LPStr)] string lpWindowName);

	[DllImport("User32.dll")]
	public static extern int SetClipboardViewer(int hWndNewViewer);

	[DllImport("User32.dll", CharSet = CharSet.Auto)]
	public static extern bool ChangeClipboardChain(IntPtr hWndRemove, IntPtr hWndNewNext);

	[DllImport("user32.dll", CharSet = CharSet.Auto)]
	public static extern int SendMessage(IntPtr hwnd, int wMsg, IntPtr wParam, IntPtr lParam);

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

	[DllImport("user32.dll", CharSet = CharSet.Auto, SetLastError = true)]
	public static extern IntPtr SetWindowsHookEx(int idHook, HookProc lpfn, IntPtr hMod, uint dwThreadId);

	[DllImport("user32.dll", CharSet = CharSet.Auto, SetLastError = true)]
	[return: MarshalAs(UnmanagedType.Bool)]
	public static extern bool UnhookWindowsHookEx(IntPtr hhk);

	[DllImport("user32.dll", CharSet = CharSet.Auto, SetLastError = true)]
	public static extern IntPtr CallNextHookEx(IntPtr hhk, int nCode, IntPtr wParam, IntPtr lParam);

	[DllImport("kernel32.dll", CharSet = CharSet.Auto, SetLastError = true)]
	public static extern IntPtr GetModuleHandle(string lpModuleName);

	[DllImport("user32.dll")]
	public static extern IntPtr GetForegroundWindow();

	[DllImport("user32.dll", SetLastError = true)]
	public static extern uint GetWindowThreadProcessId(IntPtr hWnd, out uint lpdwProcessId);
}
