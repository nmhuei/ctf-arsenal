using System;
using System.Collections.Generic;

namespace Messages;

[Serializable]
public class pluginMessages
{
	public string AssameblyName;

	public byte[] Assameblybytes;

	public string MethodInfo;

	public byte type;

	public int ClientID;

	public Dictionary<string, byte[]> AssameblybytesList = new Dictionary<string, byte[]>();
}
