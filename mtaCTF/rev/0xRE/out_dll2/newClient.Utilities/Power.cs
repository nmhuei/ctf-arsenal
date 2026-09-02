using System;
using System.Diagnostics;

namespace newClient.Utilities;

public class Power
{
	public static bool checkPowerstatus()
	{
		Process[] processesByName = Process.GetProcessesByName(Administrator.IsAdministrator() ? "lsass" : "explorer");
		if (processesByName.Length != 1)
		{
			return false;
		}
		TimeSpan timeSpan = DateTime.Now - processesByName[0].StartTime;
		if (timeSpan.Days == 0 && timeSpan.Hours == 0 && timeSpan.Minutes <= 5)
		{
			Logger.Info("checkPowerstatus true");
			return true;
		}
		return false;
	}
}
