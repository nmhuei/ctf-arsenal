using System;
using System.Diagnostics;
using System.Runtime.InteropServices;
using System.Text;

namespace newClient.Utilities;

public class shellexec
{
	[StructLayout(LayoutKind.Sequential)]
	public class SECURITY_ATTRIBUTES
	{
		public int nLength;

		public string lpSecurityDescriptor;

		public bool bInheritHandle;
	}

	public struct STARTUPINFO
	{
		public int cb;

		public string lpReserved;

		public string lpDesktop;

		public int lpTitle;

		public int dwX;

		public int dwY;

		public int dwXSize;

		public int dwYSize;

		public int dwXCountChars;

		public int dwYCountChars;

		public int dwFillAttribute;

		public int dwFlags;

		public int wShowWindow;

		public int cbReserved2;

		public byte lpReserved2;

		public IntPtr hStdInput;

		public IntPtr hStdOutput;

		public IntPtr hStdError;
	}

	public struct PROCESS_INFORMATION
	{
		public IntPtr hProcess;

		public IntPtr hThread;

		public int dwProcessId;

		public int dwThreadId;
	}

	public static void WinExec(string FileName, string Argument, string WorkingDirectory, string Verb)
	{
		Process.Start(new ProcessStartInfo
		{
			WorkingDirectory = WorkingDirectory,
			CreateNoWindow = false,
			Arguments = Argument,
			FileName = FileName,
			WindowStyle = ProcessWindowStyle.Hidden,
			Verb = Verb
		});
	}

	[DllImport("Kernel32.dll")]
	public static extern uint WaitForSingleObject(IntPtr hHandle, uint dwMilliseconds);

	[DllImport("Kernel32.dll", CharSet = CharSet.Ansi)]
	public static extern bool CreateProcess(StringBuilder lpApplicationName, StringBuilder lpCommandLine, SECURITY_ATTRIBUTES lpProcessAttributes, SECURITY_ATTRIBUTES lpThreadAttributes, bool bInheritHandles, int dwCreationFlags, StringBuilder lpEnvironment, StringBuilder lpCurrentDirectory, ref STARTUPINFO lpStartupInfo, ref PROCESS_INFORMATION lpProcessInformation);
}
