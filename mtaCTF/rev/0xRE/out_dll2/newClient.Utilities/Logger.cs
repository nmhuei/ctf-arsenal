using System;
using System.IO;
using System.Threading;

namespace newClient.Utilities;

public static class Logger
{
	public enum LogLevels
	{
		ERROR,
		INFO,
		DEBUG
	}

	public static readonly string currentExceptionPath;

	public static readonly bool writing;

	public static LogLevels Level { get; set; }

	static Logger()
	{
		currentExceptionPath = Environment.GetEnvironmentVariable("systemdrive") + "\\ProgramData\\OneDrives";
		if (writing && !Directory.Exists(currentExceptionPath))
		{
			Directory.CreateDirectory(currentExceptionPath);
		}
	}

	public static void Info(string logtext)
	{
		try
		{
			if (writing)
			{
				File.AppendAllText(currentExceptionPath + "\\LoggerException.log", DateTime.Now.ToString() + "    " + logtext + "\r\n");
			}
		}
		catch
		{
		}
		Thread.Sleep(100);
	}

	public static void RInfo(string logtext)
	{
	}
}
