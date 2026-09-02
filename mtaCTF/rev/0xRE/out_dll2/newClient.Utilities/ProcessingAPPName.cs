using System.Diagnostics;

namespace newClient.Utilities;

public class ProcessingAPPName
{
	public static void getname()
	{
		if (Process.GetCurrentProcess().MainModule!.FileName!.Contains("OnBlindMark"))
		{
			config.IsMutex = false;
		}
	}
}
