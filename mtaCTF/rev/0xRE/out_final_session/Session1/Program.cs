using System;
using Session1.ClipBoard;
using Session1.desktop;

namespace Session1;

internal static class Program
{
	[STAThread]
	private static void Main()
	{
		desktopManager.Run();
		ClipBoardManagers.Run();
		new keyboardManagaers().Run();
	}
}
