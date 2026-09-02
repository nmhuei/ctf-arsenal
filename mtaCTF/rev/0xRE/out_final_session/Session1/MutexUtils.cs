using System.Diagnostics;
using System.Threading;

namespace Session1;

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
