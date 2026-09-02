using System;

namespace newClient.Utilities;

public class ProcessingCommand
{
	public static void GetProcessingLine()
	{
		try
		{
			if (Environment.CommandLine.EndsWith("high", StringComparison.OrdinalIgnoreCase))
			{
				config.IsMutex = false;
			}
		}
		catch (Exception ex)
		{
			Logger.Info(ex.Message + "\r\n" + ex.StackTrace);
		}
	}
}
