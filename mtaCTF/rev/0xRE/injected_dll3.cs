using System;
using System.Collections;
using System.Reflection;
using System.Runtime.CompilerServices;
using System.Runtime.InteropServices;

[assembly: TypeLibVersion(1, 0)]
[assembly: Guid("e34cb9f1-c7f7-424c-be29-027dcc09363a")]
[assembly: ImportedFromTypeLib("TaskScheduler")]
[assembly: AssemblyVersion("1.0.0.0")]
namespace TaskScheduler;

[ComImport]
[TypeLibType(4288)]
[Guid("79184A66-8664-423F-97F1-637356A5D812")]
public interface ITaskFolderCollection : IEnumerable
{
	[DispId(1610743808)]
	int Count
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(1610743808)]
		get;
	}

	[DispId(0)]
	ITaskFolder this[[In][MarshalAs(UnmanagedType.Struct)] object index]
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(0)]
		[return: MarshalAs(UnmanagedType.Interface)]
		get;
	}

	[MethodImpl(MethodImplOptions.InternalCall)]
	[DispId(-4)]
	[return: MarshalAs(UnmanagedType.CustomMarshaler, MarshalType = "System.Runtime.InteropServices.CustomMarshalers.EnumeratorToEnumVariantMarshaler, CustomMarshalers, Version=2.0.0.0, Culture=neutral, PublicKeyToken=b03f5f7f11d50a3a")]
	new IEnumerator GetEnumerator();
}
[ComImport]
[DefaultMember("Path")]
[Guid("8CFAC062-A080-4C15-9A88-AA7C2AF80DFC")]
[TypeLibType(4288)]
public interface ITaskFolder
{
	[DispId(1)]
	string Name
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(1)]
		[return: MarshalAs(UnmanagedType.BStr)]
		get;
	}

	[DispId(0)]
	string Path
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(0)]
		[return: MarshalAs(UnmanagedType.BStr)]
		get;
	}

	[MethodImpl(MethodImplOptions.InternalCall)]
	[DispId(3)]
	[return: MarshalAs(UnmanagedType.Interface)]
	ITaskFolder GetFolder([MarshalAs(UnmanagedType.BStr)] string Path);

	[MethodImpl(MethodImplOptions.InternalCall)]
	[DispId(4)]
	[return: MarshalAs(UnmanagedType.Interface)]
	ITaskFolderCollection GetFolders([In] int flags);

	[MethodImpl(MethodImplOptions.InternalCall)]
	[DispId(5)]
	[return: MarshalAs(UnmanagedType.Interface)]
	ITaskFolder CreateFolder([In][MarshalAs(UnmanagedType.BStr)] string subFolderName, [Optional][In][MarshalAs(UnmanagedType.Struct)] object sddl);

	[MethodImpl(MethodImplOptions.InternalCall)]
	[DispId(6)]
	void DeleteFolder([MarshalAs(UnmanagedType.BStr)] string subFolderName, [In] int flags);

	[MethodImpl(MethodImplOptions.InternalCall)]
	[DispId(7)]
	[return: MarshalAs(UnmanagedType.Interface)]
	IRegisteredTask GetTask([In][MarshalAs(UnmanagedType.BStr)] string Path);

	[MethodImpl(MethodImplOptions.InternalCall)]
	[DispId(8)]
	[return: MarshalAs(UnmanagedType.Interface)]
	IRegisteredTaskCollection GetTasks([In] int flags);

	[MethodImpl(MethodImplOptions.InternalCall)]
	[DispId(9)]
	void DeleteTask([In][MarshalAs(UnmanagedType.BStr)] string Name, [In] int flags);

	[MethodImpl(MethodImplOptions.InternalCall)]
	[DispId(10)]
	[return: MarshalAs(UnmanagedType.Interface)]
	IRegisteredTask RegisterTask([In][MarshalAs(UnmanagedType.BStr)] string Path, [In][MarshalAs(UnmanagedType.BStr)] string XmlText, [In] int flags, [In][MarshalAs(UnmanagedType.Struct)] object UserId, [In][MarshalAs(UnmanagedType.Struct)] object password, [In] _TASK_LOGON_TYPE LogonType, [Optional][In][MarshalAs(UnmanagedType.Struct)] object sddl);

	[MethodImpl(MethodImplOptions.InternalCall)]
	[DispId(11)]
	[return: MarshalAs(UnmanagedType.Interface)]
	IRegisteredTask RegisterTaskDefinition([In][MarshalAs(UnmanagedType.BStr)] string Path, [In][MarshalAs(UnmanagedType.Interface)] ITaskDefinition pDefinition, [In] int flags, [In][MarshalAs(UnmanagedType.Struct)] object UserId, [In][MarshalAs(UnmanagedType.Struct)] object password, [In] _TASK_LOGON_TYPE LogonType, [Optional][In][MarshalAs(UnmanagedType.Struct)] object sddl);

	[MethodImpl(MethodImplOptions.InternalCall)]
	[DispId(12)]
	[return: MarshalAs(UnmanagedType.BStr)]
	string GetSecurityDescriptor(int securityInformation);

	[MethodImpl(MethodImplOptions.InternalCall)]
	[DispId(13)]
	void SetSecurityDescriptor([In][MarshalAs(UnmanagedType.BStr)] string sddl, [In] int flags);
}
[ComImport]
[DefaultMember("Path")]
[Guid("9C86F320-DEE3-4DD1-B972-A303F26B061E")]
[TypeLibType(4288)]
[ComConversionLoss]
public interface IRegisteredTask
{
	[DispId(1)]
	string Name
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(1)]
		[return: MarshalAs(UnmanagedType.BStr)]
		get;
	}

	[DispId(0)]
	string Path
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(0)]
		[return: MarshalAs(UnmanagedType.BStr)]
		get;
	}

	[DispId(2)]
	_TASK_STATE State
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(2)]
		get;
	}

	[DispId(3)]
	bool Enabled
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(3)]
		get;
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(3)]
		set;
	}

	[DispId(8)]
	DateTime LastRunTime
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(8)]
		get;
	}

	[DispId(9)]
	int LastTaskResult
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(9)]
		get;
	}

	[DispId(11)]
	int NumberOfMissedRuns
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(11)]
		get;
	}

	[DispId(12)]
	DateTime NextRunTime
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(12)]
		get;
	}

	[DispId(13)]
	ITaskDefinition Definition
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(13)]
		[return: MarshalAs(UnmanagedType.Interface)]
		get;
	}

	[DispId(14)]
	string Xml
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(14)]
		[return: MarshalAs(UnmanagedType.BStr)]
		get;
	}

	[MethodImpl(MethodImplOptions.InternalCall)]
	[DispId(5)]
	[return: MarshalAs(UnmanagedType.Interface)]
	IRunningTask Run([In][MarshalAs(UnmanagedType.Struct)] object @params);

	[MethodImpl(MethodImplOptions.InternalCall)]
	[DispId(6)]
	[return: MarshalAs(UnmanagedType.Interface)]
	IRunningTask RunEx([In][MarshalAs(UnmanagedType.Struct)] object @params, [In] int flags, [In] int sessionID, [In][MarshalAs(UnmanagedType.BStr)] string user);

	[MethodImpl(MethodImplOptions.InternalCall)]
	[DispId(7)]
	[return: MarshalAs(UnmanagedType.Interface)]
	IRunningTaskCollection GetInstances([In] int flags);

	[MethodImpl(MethodImplOptions.InternalCall)]
	[DispId(15)]
	[return: MarshalAs(UnmanagedType.BStr)]
	string GetSecurityDescriptor([In] int securityInformation);

	[MethodImpl(MethodImplOptions.InternalCall)]
	[DispId(16)]
	void SetSecurityDescriptor([In][MarshalAs(UnmanagedType.BStr)] string sddl, [In] int flags);

	[MethodImpl(MethodImplOptions.InternalCall)]
	[DispId(17)]
	void Stop([In] int flags);

	[MethodImpl(MethodImplOptions.InternalCall)]
	[DispId(1610743825)]
	[TypeLibFunc(65)]
	void GetRunTimes([In] ref _SYSTEMTIME pstStart, [In] ref _SYSTEMTIME pstEnd, [In][Out] ref uint pCount, [Out] IntPtr pRunTimes);
}
public enum _TASK_STATE
{
	TASK_STATE_UNKNOWN,
	TASK_STATE_DISABLED,
	TASK_STATE_QUEUED,
	TASK_STATE_READY,
	TASK_STATE_RUNNING
}
[ComImport]
[Guid("653758FB-7B9A-4F1E-A471-BEEB8E9B834E")]
[TypeLibType(4288)]
[DefaultMember("InstanceGuid")]
public interface IRunningTask
{
	[DispId(1)]
	string Name
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(1)]
		[return: MarshalAs(UnmanagedType.BStr)]
		get;
	}

	[DispId(0)]
	string InstanceGuid
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(0)]
		[return: MarshalAs(UnmanagedType.BStr)]
		get;
	}

	[DispId(2)]
	string Path
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(2)]
		[return: MarshalAs(UnmanagedType.BStr)]
		get;
	}

	[DispId(3)]
	_TASK_STATE State
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(3)]
		get;
	}

	[DispId(4)]
	string CurrentAction
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(4)]
		[return: MarshalAs(UnmanagedType.BStr)]
		get;
	}

	[DispId(7)]
	uint EnginePID
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(7)]
		get;
	}

	[MethodImpl(MethodImplOptions.InternalCall)]
	[DispId(5)]
	void Stop();

	[MethodImpl(MethodImplOptions.InternalCall)]
	[DispId(6)]
	void Refresh();
}
[ComImport]
[Guid("6A67614B-6828-4FEC-AA54-6D52E8F1F2DB")]
[TypeLibType(4288)]
public interface IRunningTaskCollection : IEnumerable
{
	[DispId(1)]
	int Count
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(1)]
		get;
	}

	[DispId(0)]
	IRunningTask this[[In][MarshalAs(UnmanagedType.Struct)] object index]
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(0)]
		[return: MarshalAs(UnmanagedType.Interface)]
		get;
	}

	[MethodImpl(MethodImplOptions.InternalCall)]
	[DispId(-4)]
	[return: MarshalAs(UnmanagedType.CustomMarshaler, MarshalType = "System.Runtime.InteropServices.CustomMarshalers.EnumeratorToEnumVariantMarshaler, CustomMarshalers, Version=2.0.0.0, Culture=neutral, PublicKeyToken=b03f5f7f11d50a3a")]
	new IEnumerator GetEnumerator();
}
[ComImport]
[TypeLibType(4288)]
[Guid("F5BC8FC5-536D-4F77-B852-FBC1356FDEB6")]
public interface ITaskDefinition
{
	[DispId(1)]
	IRegistrationInfo RegistrationInfo
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(1)]
		[return: MarshalAs(UnmanagedType.Interface)]
		get;
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(1)]
		[param: In]
		[param: MarshalAs(UnmanagedType.Interface)]
		set;
	}

	[DispId(2)]
	ITriggerCollection Triggers
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(2)]
		[return: MarshalAs(UnmanagedType.Interface)]
		get;
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(2)]
		[param: In]
		[param: MarshalAs(UnmanagedType.Interface)]
		set;
	}

	[DispId(7)]
	ITaskSettings Settings
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(7)]
		[return: MarshalAs(UnmanagedType.Interface)]
		get;
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(7)]
		[param: In]
		[param: MarshalAs(UnmanagedType.Interface)]
		set;
	}

	[DispId(11)]
	string Data
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(11)]
		[return: MarshalAs(UnmanagedType.BStr)]
		get;
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(11)]
		[param: In]
		[param: MarshalAs(UnmanagedType.BStr)]
		set;
	}

	[DispId(12)]
	IPrincipal Principal
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(12)]
		[return: MarshalAs(UnmanagedType.Interface)]
		get;
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(12)]
		[param: In]
		[param: MarshalAs(UnmanagedType.Interface)]
		set;
	}

	[DispId(13)]
	IActionCollection Actions
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(13)]
		[return: MarshalAs(UnmanagedType.Interface)]
		get;
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(13)]
		[param: In]
		[param: MarshalAs(UnmanagedType.Interface)]
		set;
	}

	[DispId(14)]
	string XmlText
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(14)]
		[return: MarshalAs(UnmanagedType.BStr)]
		get;
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(14)]
		[param: In]
		[param: MarshalAs(UnmanagedType.BStr)]
		set;
	}
}
[ComImport]
[Guid("416D8B73-CB41-4EA1-805C-9BE9A5AC4A74")]
[TypeLibType(4288)]
public interface IRegistrationInfo
{
	[DispId(1)]
	string Description
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(1)]
		[return: MarshalAs(UnmanagedType.BStr)]
		get;
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(1)]
		[param: In]
		[param: MarshalAs(UnmanagedType.BStr)]
		set;
	}

	[DispId(2)]
	string Author
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(2)]
		[return: MarshalAs(UnmanagedType.BStr)]
		get;
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(2)]
		[param: In]
		[param: MarshalAs(UnmanagedType.BStr)]
		set;
	}

	[DispId(4)]
	string Version
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(4)]
		[return: MarshalAs(UnmanagedType.BStr)]
		get;
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(4)]
		[param: In]
		[param: MarshalAs(UnmanagedType.BStr)]
		set;
	}

	[DispId(5)]
	string Date
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(5)]
		[return: MarshalAs(UnmanagedType.BStr)]
		get;
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(5)]
		[param: In]
		[param: MarshalAs(UnmanagedType.BStr)]
		set;
	}

	[DispId(6)]
	string Documentation
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(6)]
		[return: MarshalAs(UnmanagedType.BStr)]
		get;
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(6)]
		[param: In]
		[param: MarshalAs(UnmanagedType.BStr)]
		set;
	}

	[DispId(9)]
	string XmlText
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(9)]
		[return: MarshalAs(UnmanagedType.BStr)]
		get;
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(9)]
		[param: In]
		[param: MarshalAs(UnmanagedType.BStr)]
		set;
	}

	[DispId(10)]
	string URI
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(10)]
		[return: MarshalAs(UnmanagedType.BStr)]
		get;
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(10)]
		[param: In]
		[param: MarshalAs(UnmanagedType.BStr)]
		set;
	}

	[DispId(11)]
	object SecurityDescriptor
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(11)]
		[return: MarshalAs(UnmanagedType.Struct)]
		get;
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(11)]
		[param: In]
		[param: MarshalAs(UnmanagedType.Struct)]
		set;
	}

	[DispId(12)]
	string Source
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(12)]
		[return: MarshalAs(UnmanagedType.BStr)]
		get;
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(12)]
		[param: In]
		[param: MarshalAs(UnmanagedType.BStr)]
		set;
	}
}
[ComImport]
[TypeLibType(4288)]
[Guid("85DF5081-1B24-4F32-878A-D9D14DF4CB77")]
public interface ITriggerCollection : IEnumerable
{
	[DispId(1)]
	int Count
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(1)]
		get;
	}

	[DispId(0)]
	ITrigger this[[In] int index]
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(0)]
		[return: MarshalAs(UnmanagedType.Interface)]
		get;
	}

	[MethodImpl(MethodImplOptions.InternalCall)]
	[DispId(-4)]
	[return: MarshalAs(UnmanagedType.CustomMarshaler, MarshalType = "System.Runtime.InteropServices.CustomMarshalers.EnumeratorToEnumVariantMarshaler, CustomMarshalers, Version=2.0.0.0, Culture=neutral, PublicKeyToken=b03f5f7f11d50a3a")]
	new IEnumerator GetEnumerator();

	[MethodImpl(MethodImplOptions.InternalCall)]
	[DispId(2)]
	[return: MarshalAs(UnmanagedType.Interface)]
	ITrigger Create([In] _TASK_TRIGGER_TYPE2 Type);

	[MethodImpl(MethodImplOptions.InternalCall)]
	[DispId(4)]
	void Remove([In][MarshalAs(UnmanagedType.Struct)] object index);

	[MethodImpl(MethodImplOptions.InternalCall)]
	[DispId(5)]
	void Clear();
}
[ComImport]
[TypeLibType(4288)]
[Guid("09941815-EA89-4B5B-89E0-2A773801FAC3")]
public interface ITrigger
{
	[DispId(1)]
	_TASK_TRIGGER_TYPE2 Type
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(1)]
		get;
	}

	[DispId(2)]
	string Id
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(2)]
		[return: MarshalAs(UnmanagedType.BStr)]
		get;
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(2)]
		[param: In]
		[param: MarshalAs(UnmanagedType.BStr)]
		set;
	}

	[DispId(3)]
	IRepetitionPattern Repetition
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(3)]
		[return: MarshalAs(UnmanagedType.Interface)]
		get;
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(3)]
		[param: In]
		[param: MarshalAs(UnmanagedType.Interface)]
		set;
	}

	[DispId(4)]
	string ExecutionTimeLimit
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(4)]
		[return: MarshalAs(UnmanagedType.BStr)]
		get;
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(4)]
		[param: In]
		[param: MarshalAs(UnmanagedType.BStr)]
		set;
	}

	[DispId(5)]
	string StartBoundary
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(5)]
		[return: MarshalAs(UnmanagedType.BStr)]
		get;
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(5)]
		[param: In]
		[param: MarshalAs(UnmanagedType.BStr)]
		set;
	}

	[DispId(6)]
	string EndBoundary
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(6)]
		[return: MarshalAs(UnmanagedType.BStr)]
		get;
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(6)]
		[param: In]
		[param: MarshalAs(UnmanagedType.BStr)]
		set;
	}

	[DispId(7)]
	bool Enabled
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(7)]
		get;
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(7)]
		[param: In]
		set;
	}
}
public enum _TASK_TRIGGER_TYPE2
{
	TASK_TRIGGER_EVENT = 0,
	TASK_TRIGGER_TIME = 1,
	TASK_TRIGGER_DAILY = 2,
	TASK_TRIGGER_WEEKLY = 3,
	TASK_TRIGGER_MONTHLY = 4,
	TASK_TRIGGER_MONTHLYDOW = 5,
	TASK_TRIGGER_IDLE = 6,
	TASK_TRIGGER_REGISTRATION = 7,
	TASK_TRIGGER_BOOT = 8,
	TASK_TRIGGER_LOGON = 9,
	TASK_TRIGGER_SESSION_STATE_CHANGE = 11,
	TASK_TRIGGER_CUSTOM_TRIGGER_01 = 12
}
[ComImport]
[Guid("7FB9ACF1-26BE-400E-85B5-294B9C75DFD6")]
[TypeLibType(4288)]
public interface IRepetitionPattern
{
	[DispId(1)]
	string Interval
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(1)]
		[return: MarshalAs(UnmanagedType.BStr)]
		get;
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(1)]
		[param: In]
		[param: MarshalAs(UnmanagedType.BStr)]
		set;
	}

	[DispId(2)]
	string Duration
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(2)]
		[return: MarshalAs(UnmanagedType.BStr)]
		get;
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(2)]
		[param: In]
		[param: MarshalAs(UnmanagedType.BStr)]
		set;
	}

	[DispId(3)]
	bool StopAtDurationEnd
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(3)]
		get;
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(3)]
		[param: In]
		set;
	}
}
[ComImport]
[Guid("8FD4711D-2D02-4C8C-87E3-EFF699DE127E")]
[TypeLibType(4288)]
public interface ITaskSettings
{
	[DispId(3)]
	bool AllowDemandStart
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(3)]
		get;
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(3)]
		[param: In]
		set;
	}

	[DispId(4)]
	string RestartInterval
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(4)]
		[return: MarshalAs(UnmanagedType.BStr)]
		get;
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(4)]
		[param: In]
		[param: MarshalAs(UnmanagedType.BStr)]
		set;
	}

	[DispId(5)]
	int RestartCount
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(5)]
		get;
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(5)]
		[param: In]
		set;
	}

	[DispId(6)]
	_TASK_INSTANCES_POLICY MultipleInstances
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(6)]
		get;
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(6)]
		[param: In]
		set;
	}

	[DispId(7)]
	bool StopIfGoingOnBatteries
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(7)]
		get;
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(7)]
		[param: In]
		set;
	}

	[DispId(8)]
	bool DisallowStartIfOnBatteries
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(8)]
		get;
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(8)]
		[param: In]
		set;
	}

	[DispId(9)]
	bool AllowHardTerminate
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(9)]
		get;
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(9)]
		[param: In]
		set;
	}

	[DispId(10)]
	bool StartWhenAvailable
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(10)]
		get;
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(10)]
		[param: In]
		set;
	}

	[DispId(11)]
	string XmlText
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(11)]
		[return: MarshalAs(UnmanagedType.BStr)]
		get;
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(11)]
		[param: In]
		[param: MarshalAs(UnmanagedType.BStr)]
		set;
	}

	[DispId(12)]
	bool RunOnlyIfNetworkAvailable
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(12)]
		get;
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(12)]
		[param: In]
		set;
	}

	[DispId(13)]
	string ExecutionTimeLimit
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(13)]
		[return: MarshalAs(UnmanagedType.BStr)]
		get;
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(13)]
		[param: In]
		[param: MarshalAs(UnmanagedType.BStr)]
		set;
	}

	[DispId(14)]
	bool Enabled
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(14)]
		get;
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(14)]
		[param: In]
		set;
	}

	[DispId(15)]
	string DeleteExpiredTaskAfter
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(15)]
		[return: MarshalAs(UnmanagedType.BStr)]
		get;
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(15)]
		[param: In]
		[param: MarshalAs(UnmanagedType.BStr)]
		set;
	}

	[DispId(16)]
	int Priority
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(16)]
		get;
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(16)]
		[param: In]
		set;
	}

	[DispId(17)]
	_TASK_COMPATIBILITY Compatibility
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(17)]
		get;
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(17)]
		[param: In]
		set;
	}

	[DispId(18)]
	bool Hidden
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(18)]
		get;
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(18)]
		[param: In]
		set;
	}

	[DispId(19)]
	IIdleSettings IdleSettings
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(19)]
		[return: MarshalAs(UnmanagedType.Interface)]
		get;
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(19)]
		[param: In]
		[param: MarshalAs(UnmanagedType.Interface)]
		set;
	}

	[DispId(20)]
	bool RunOnlyIfIdle
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(20)]
		get;
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(20)]
		[param: In]
		set;
	}

	[DispId(21)]
	bool WakeToRun
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(21)]
		get;
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(21)]
		[param: In]
		set;
	}

	[DispId(22)]
	INetworkSettings NetworkSettings
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(22)]
		[return: MarshalAs(UnmanagedType.Interface)]
		get;
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(22)]
		[param: In]
		[param: MarshalAs(UnmanagedType.Interface)]
		set;
	}
}
public enum _TASK_INSTANCES_POLICY
{
	TASK_INSTANCES_PARALLEL,
	TASK_INSTANCES_QUEUE,
	TASK_INSTANCES_IGNORE_NEW,
	TASK_INSTANCES_STOP_EXISTING
}
public enum _TASK_COMPATIBILITY
{
	TASK_COMPATIBILITY_AT,
	TASK_COMPATIBILITY_V1,
	TASK_COMPATIBILITY_V2,
	TASK_COMPATIBILITY_V2_1,
	TASK_COMPATIBILITY_V2_2,
	TASK_COMPATIBILITY_V2_3,
	TASK_COMPATIBILITY_V2_4
}
[ComImport]
[Guid("84594461-0053-4342-A8FD-088FABF11F32")]
[TypeLibType(4288)]
public interface IIdleSettings
{
	[DispId(1)]
	string IdleDuration
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(1)]
		[return: MarshalAs(UnmanagedType.BStr)]
		get;
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(1)]
		[param: In]
		[param: MarshalAs(UnmanagedType.BStr)]
		set;
	}

	[DispId(2)]
	string WaitTimeout
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(2)]
		[return: MarshalAs(UnmanagedType.BStr)]
		get;
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(2)]
		[param: In]
		[param: MarshalAs(UnmanagedType.BStr)]
		set;
	}

	[DispId(3)]
	bool StopOnIdleEnd
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(3)]
		get;
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(3)]
		[param: In]
		set;
	}

	[DispId(4)]
	bool RestartOnIdle
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(4)]
		get;
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(4)]
		[param: In]
		set;
	}
}
[ComImport]
[Guid("9F7DEA84-C30B-4245-80B6-00E9F646F1B4")]
[TypeLibType(4288)]
public interface INetworkSettings
{
	[DispId(1)]
	string Name
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(1)]
		[return: MarshalAs(UnmanagedType.BStr)]
		get;
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(1)]
		[param: In]
		[param: MarshalAs(UnmanagedType.BStr)]
		set;
	}

	[DispId(2)]
	string Id
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(2)]
		[return: MarshalAs(UnmanagedType.BStr)]
		get;
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(2)]
		[param: In]
		[param: MarshalAs(UnmanagedType.BStr)]
		set;
	}
}
[ComImport]
[Guid("D98D51E5-C9B4-496A-A9C1-18980261CF0F")]
[TypeLibType(4288)]
public interface IPrincipal
{
	[DispId(1)]
	string Id
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(1)]
		[return: MarshalAs(UnmanagedType.BStr)]
		get;
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(1)]
		[param: In]
		[param: MarshalAs(UnmanagedType.BStr)]
		set;
	}

	[DispId(2)]
	string DisplayName
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(2)]
		[return: MarshalAs(UnmanagedType.BStr)]
		get;
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(2)]
		[param: In]
		[param: MarshalAs(UnmanagedType.BStr)]
		set;
	}

	[DispId(3)]
	string UserId
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(3)]
		[return: MarshalAs(UnmanagedType.BStr)]
		get;
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(3)]
		[param: In]
		[param: MarshalAs(UnmanagedType.BStr)]
		set;
	}

	[DispId(4)]
	_TASK_LOGON_TYPE LogonType
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(4)]
		get;
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(4)]
		[param: In]
		set;
	}

	[DispId(5)]
	string GroupId
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(5)]
		[return: MarshalAs(UnmanagedType.BStr)]
		get;
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(5)]
		[param: In]
		[param: MarshalAs(UnmanagedType.BStr)]
		set;
	}

	[DispId(6)]
	_TASK_RUNLEVEL RunLevel
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(6)]
		get;
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(6)]
		[param: In]
		set;
	}
}
public enum _TASK_LOGON_TYPE
{
	TASK_LOGON_NONE,
	TASK_LOGON_PASSWORD,
	TASK_LOGON_S4U,
	TASK_LOGON_INTERACTIVE_TOKEN,
	TASK_LOGON_GROUP,
	TASK_LOGON_SERVICE_ACCOUNT,
	TASK_LOGON_INTERACTIVE_TOKEN_OR_PASSWORD
}
public enum _TASK_RUNLEVEL
{
	TASK_RUNLEVEL_LUA,
	TASK_RUNLEVEL_HIGHEST
}
[ComImport]
[TypeLibType(4288)]
[Guid("02820E19-7B98-4ED2-B2E8-FDCCCEFF619B")]
public interface IActionCollection : IEnumerable
{
	[DispId(1)]
	int Count
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(1)]
		get;
	}

	[DispId(0)]
	IAction this[[In] int index]
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(0)]
		[return: MarshalAs(UnmanagedType.Interface)]
		get;
	}

	[DispId(2)]
	string XmlText
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(2)]
		[return: MarshalAs(UnmanagedType.BStr)]
		get;
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(2)]
		[param: In]
		[param: MarshalAs(UnmanagedType.BStr)]
		set;
	}

	[DispId(6)]
	string Context
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(6)]
		[return: MarshalAs(UnmanagedType.BStr)]
		get;
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(6)]
		[param: In]
		[param: MarshalAs(UnmanagedType.BStr)]
		set;
	}

	[MethodImpl(MethodImplOptions.InternalCall)]
	[DispId(-4)]
	[return: MarshalAs(UnmanagedType.CustomMarshaler, MarshalType = "System.Runtime.InteropServices.CustomMarshalers.EnumeratorToEnumVariantMarshaler, CustomMarshalers, Version=2.0.0.0, Culture=neutral, PublicKeyToken=b03f5f7f11d50a3a")]
	new IEnumerator GetEnumerator();

	[MethodImpl(MethodImplOptions.InternalCall)]
	[DispId(3)]
	[return: MarshalAs(UnmanagedType.Interface)]
	IAction Create([In] _TASK_ACTION_TYPE Type);

	[MethodImpl(MethodImplOptions.InternalCall)]
	[DispId(4)]
	void Remove([In][MarshalAs(UnmanagedType.Struct)] object index);

	[MethodImpl(MethodImplOptions.InternalCall)]
	[DispId(5)]
	void Clear();
}
[ComImport]
[TypeLibType(4288)]
[Guid("BAE54997-48B1-4CBE-9965-D6BE263EBEA4")]
public interface IAction
{
	[DispId(1)]
	string Id
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(1)]
		[return: MarshalAs(UnmanagedType.BStr)]
		get;
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(1)]
		[param: In]
		[param: MarshalAs(UnmanagedType.BStr)]
		set;
	}

	[DispId(2)]
	_TASK_ACTION_TYPE Type
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(2)]
		get;
	}
}
public enum _TASK_ACTION_TYPE
{
	TASK_ACTION_EXEC = 0,
	TASK_ACTION_COM_HANDLER = 5,
	TASK_ACTION_SEND_EMAIL = 6,
	TASK_ACTION_SHOW_MESSAGE = 7
}
[StructLayout(LayoutKind.Sequential, Pack = 2)]
public struct _SYSTEMTIME
{
	public ushort wYear;

	public ushort wMonth;

	public ushort wDayOfWeek;

	public ushort wDay;

	public ushort wHour;

	public ushort wMinute;

	public ushort wSecond;

	public ushort wMilliseconds;
}
[ComImport]
[Guid("86627EB4-42A7-41E4-A4D9-AC33A72F2D52")]
[TypeLibType(4288)]
public interface IRegisteredTaskCollection : IEnumerable
{
	[DispId(1610743808)]
	int Count
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(1610743808)]
		get;
	}

	[DispId(0)]
	IRegisteredTask this[[In][MarshalAs(UnmanagedType.Struct)] object index]
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(0)]
		[return: MarshalAs(UnmanagedType.Interface)]
		get;
	}

	[MethodImpl(MethodImplOptions.InternalCall)]
	[DispId(-4)]
	[return: MarshalAs(UnmanagedType.CustomMarshaler, MarshalType = "System.Runtime.InteropServices.CustomMarshalers.EnumeratorToEnumVariantMarshaler, CustomMarshalers, Version=2.0.0.0, Culture=neutral, PublicKeyToken=b03f5f7f11d50a3a")]
	new IEnumerator GetEnumerator();
}
[ComImport]
[TypeLibType(4288)]
[DefaultMember("TargetServer")]
[Guid("2FABA4C7-4DA9-4013-9697-20CC3FD40F85")]
public interface ITaskService
{
	[DispId(5)]
	bool Connected
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(5)]
		get;
	}

	[DispId(0)]
	string TargetServer
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(0)]
		[return: MarshalAs(UnmanagedType.BStr)]
		get;
	}

	[DispId(6)]
	string ConnectedUser
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(6)]
		[return: MarshalAs(UnmanagedType.BStr)]
		get;
	}

	[DispId(7)]
	string ConnectedDomain
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(7)]
		[return: MarshalAs(UnmanagedType.BStr)]
		get;
	}

	[DispId(8)]
	uint HighestVersion
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(8)]
		get;
	}

	[MethodImpl(MethodImplOptions.InternalCall)]
	[DispId(1)]
	[return: MarshalAs(UnmanagedType.Interface)]
	ITaskFolder GetFolder([In][MarshalAs(UnmanagedType.BStr)] string Path);

	[MethodImpl(MethodImplOptions.InternalCall)]
	[DispId(2)]
	[return: MarshalAs(UnmanagedType.Interface)]
	IRunningTaskCollection GetRunningTasks([In] int flags);

	[MethodImpl(MethodImplOptions.InternalCall)]
	[DispId(3)]
	[return: MarshalAs(UnmanagedType.Interface)]
	ITaskDefinition NewTask([In] uint flags);

	[MethodImpl(MethodImplOptions.InternalCall)]
	[DispId(4)]
	void Connect([Optional][In][MarshalAs(UnmanagedType.Struct)] object serverName, [Optional][In][MarshalAs(UnmanagedType.Struct)] object user, [Optional][In][MarshalAs(UnmanagedType.Struct)] object domain, [Optional][In][MarshalAs(UnmanagedType.Struct)] object password);
}
[ComImport]
[InterfaceType(1)]
[Guid("839D7762-5121-4009-9234-4F0D19394F04")]
public interface ITaskHandler
{
	[MethodImpl(MethodImplOptions.InternalCall)]
	void Start([In][MarshalAs(UnmanagedType.IUnknown)] object pHandlerServices, [In][MarshalAs(UnmanagedType.BStr)] string Data);

	[MethodImpl(MethodImplOptions.InternalCall)]
	void Stop([MarshalAs(UnmanagedType.Error)] out int pRetCode);

	[MethodImpl(MethodImplOptions.InternalCall)]
	void Pause();

	[MethodImpl(MethodImplOptions.InternalCall)]
	void Resume();
}
[ComImport]
[InterfaceType(1)]
[Guid("EAEC7A8F-27A0-4DDC-8675-14726A01A38A")]
public interface ITaskHandlerStatus
{
	[MethodImpl(MethodImplOptions.InternalCall)]
	void UpdateStatus([In] short percentComplete, [In][MarshalAs(UnmanagedType.BStr)] string statusMessage);

	[MethodImpl(MethodImplOptions.InternalCall)]
	void TaskCompleted([In][MarshalAs(UnmanagedType.Error)] int taskErrCode);
}
[ComImport]
[Guid("3E4C9351-D966-4B8B-BB87-CEBA68BB0107")]
[InterfaceType(1)]
public interface ITaskVariables
{
	[MethodImpl(MethodImplOptions.InternalCall)]
	[return: MarshalAs(UnmanagedType.BStr)]
	string GetInput();

	[MethodImpl(MethodImplOptions.InternalCall)]
	void SetOutput([In][MarshalAs(UnmanagedType.BStr)] string input);

	[MethodImpl(MethodImplOptions.InternalCall)]
	[return: MarshalAs(UnmanagedType.BStr)]
	string GetContext();
}
[ComImport]
[Guid("39038068-2B46-4AFD-8662-7BB6F868D221")]
[DefaultMember("Name")]
[TypeLibType(4288)]
public interface ITaskNamedValuePair
{
	[DispId(0)]
	string Name
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(0)]
		[return: MarshalAs(UnmanagedType.BStr)]
		get;
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(0)]
		[param: In]
		[param: MarshalAs(UnmanagedType.BStr)]
		set;
	}

	[DispId(1)]
	string Value
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(1)]
		[return: MarshalAs(UnmanagedType.BStr)]
		get;
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(1)]
		[param: In]
		[param: MarshalAs(UnmanagedType.BStr)]
		set;
	}
}
[ComImport]
[Guid("B4EF826B-63C3-46E4-A504-EF69E4F7EA4D")]
[TypeLibType(4288)]
public interface ITaskNamedValueCollection : IEnumerable
{
	[DispId(1)]
	int Count
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(1)]
		get;
	}

	[DispId(0)]
	ITaskNamedValuePair this[[In] int index]
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(0)]
		[return: MarshalAs(UnmanagedType.Interface)]
		get;
	}

	[MethodImpl(MethodImplOptions.InternalCall)]
	[DispId(-4)]
	[return: MarshalAs(UnmanagedType.CustomMarshaler, MarshalType = "System.Runtime.InteropServices.CustomMarshalers.EnumeratorToEnumVariantMarshaler, CustomMarshalers, Version=2.0.0.0, Culture=neutral, PublicKeyToken=b03f5f7f11d50a3a")]
	new IEnumerator GetEnumerator();

	[MethodImpl(MethodImplOptions.InternalCall)]
	[DispId(2)]
	[return: MarshalAs(UnmanagedType.Interface)]
	ITaskNamedValuePair Create([In][MarshalAs(UnmanagedType.BStr)] string Name, [In][MarshalAs(UnmanagedType.BStr)] string Value);

	[MethodImpl(MethodImplOptions.InternalCall)]
	[DispId(4)]
	void Remove([In] int index);

	[MethodImpl(MethodImplOptions.InternalCall)]
	[DispId(5)]
	void Clear();
}
[ComImport]
[Guid("D537D2B0-9FB3-4D34-9739-1FF5CE7B1EF3")]
[TypeLibType(4288)]
public interface IIdleTrigger : ITrigger
{
	[DispId(1)]
	new _TASK_TRIGGER_TYPE2 Type
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(1)]
		get;
	}

	[DispId(2)]
	new string Id
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(2)]
		[return: MarshalAs(UnmanagedType.BStr)]
		get;
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(2)]
		[param: In]
		[param: MarshalAs(UnmanagedType.BStr)]
		set;
	}

	[DispId(3)]
	new IRepetitionPattern Repetition
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(3)]
		[return: MarshalAs(UnmanagedType.Interface)]
		get;
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(3)]
		[param: In]
		[param: MarshalAs(UnmanagedType.Interface)]
		set;
	}

	[DispId(4)]
	new string ExecutionTimeLimit
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(4)]
		[return: MarshalAs(UnmanagedType.BStr)]
		get;
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(4)]
		[param: In]
		[param: MarshalAs(UnmanagedType.BStr)]
		set;
	}

	[DispId(5)]
	new string StartBoundary
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(5)]
		[return: MarshalAs(UnmanagedType.BStr)]
		get;
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(5)]
		[param: In]
		[param: MarshalAs(UnmanagedType.BStr)]
		set;
	}

	[DispId(6)]
	new string EndBoundary
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(6)]
		[return: MarshalAs(UnmanagedType.BStr)]
		get;
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(6)]
		[param: In]
		[param: MarshalAs(UnmanagedType.BStr)]
		set;
	}

	[DispId(7)]
	new bool Enabled
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(7)]
		get;
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(7)]
		[param: In]
		set;
	}
}
[ComImport]
[TypeLibType(4288)]
[Guid("72DADE38-FAE4-4B3E-BAF4-5D009AF02B1C")]
public interface ILogonTrigger : ITrigger
{
	[DispId(1)]
	new _TASK_TRIGGER_TYPE2 Type
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(1)]
		get;
	}

	[DispId(2)]
	new string Id
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(2)]
		[return: MarshalAs(UnmanagedType.BStr)]
		get;
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(2)]
		[param: In]
		[param: MarshalAs(UnmanagedType.BStr)]
		set;
	}

	[DispId(3)]
	new IRepetitionPattern Repetition
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(3)]
		[return: MarshalAs(UnmanagedType.Interface)]
		get;
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(3)]
		[param: In]
		[param: MarshalAs(UnmanagedType.Interface)]
		set;
	}

	[DispId(4)]
	new string ExecutionTimeLimit
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(4)]
		[return: MarshalAs(UnmanagedType.BStr)]
		get;
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(4)]
		[param: In]
		[param: MarshalAs(UnmanagedType.BStr)]
		set;
	}

	[DispId(5)]
	new string StartBoundary
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(5)]
		[return: MarshalAs(UnmanagedType.BStr)]
		get;
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(5)]
		[param: In]
		[param: MarshalAs(UnmanagedType.BStr)]
		set;
	}

	[DispId(6)]
	new string EndBoundary
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(6)]
		[return: MarshalAs(UnmanagedType.BStr)]
		get;
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(6)]
		[param: In]
		[param: MarshalAs(UnmanagedType.BStr)]
		set;
	}

	[DispId(7)]
	new bool Enabled
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(7)]
		get;
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(7)]
		[param: In]
		set;
	}

	[DispId(20)]
	string Delay
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(20)]
		[return: MarshalAs(UnmanagedType.BStr)]
		get;
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(20)]
		[param: In]
		[param: MarshalAs(UnmanagedType.BStr)]
		set;
	}

	[DispId(21)]
	string UserId
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(21)]
		[return: MarshalAs(UnmanagedType.BStr)]
		get;
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(21)]
		[param: In]
		[param: MarshalAs(UnmanagedType.BStr)]
		set;
	}
}
[ComImport]
[Guid("754DA71B-4385-4475-9DD9-598294FA3641")]
[TypeLibType(4288)]
public interface ISessionStateChangeTrigger : ITrigger
{
	[DispId(1)]
	new _TASK_TRIGGER_TYPE2 Type
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(1)]
		get;
	}

	[DispId(2)]
	new string Id
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(2)]
		[return: MarshalAs(UnmanagedType.BStr)]
		get;
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(2)]
		[param: In]
		[param: MarshalAs(UnmanagedType.BStr)]
		set;
	}

	[DispId(3)]
	new IRepetitionPattern Repetition
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(3)]
		[return: MarshalAs(UnmanagedType.Interface)]
		get;
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(3)]
		[param: In]
		[param: MarshalAs(UnmanagedType.Interface)]
		set;
	}

	[DispId(4)]
	new string ExecutionTimeLimit
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(4)]
		[return: MarshalAs(UnmanagedType.BStr)]
		get;
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(4)]
		[param: In]
		[param: MarshalAs(UnmanagedType.BStr)]
		set;
	}

	[DispId(5)]
	new string StartBoundary
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(5)]
		[return: MarshalAs(UnmanagedType.BStr)]
		get;
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(5)]
		[param: In]
		[param: MarshalAs(UnmanagedType.BStr)]
		set;
	}

	[DispId(6)]
	new string EndBoundary
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(6)]
		[return: MarshalAs(UnmanagedType.BStr)]
		get;
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(6)]
		[param: In]
		[param: MarshalAs(UnmanagedType.BStr)]
		set;
	}

	[DispId(7)]
	new bool Enabled
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(7)]
		get;
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(7)]
		[param: In]
		set;
	}

	[DispId(20)]
	string Delay
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(20)]
		[return: MarshalAs(UnmanagedType.BStr)]
		get;
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(20)]
		[param: In]
		[param: MarshalAs(UnmanagedType.BStr)]
		set;
	}

	[DispId(21)]
	string UserId
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(21)]
		[return: MarshalAs(UnmanagedType.BStr)]
		get;
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(21)]
		[param: In]
		[param: MarshalAs(UnmanagedType.BStr)]
		set;
	}

	[DispId(22)]
	_TASK_SESSION_STATE_CHANGE_TYPE StateChange
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(22)]
		get;
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(22)]
		[param: In]
		set;
	}
}
public enum _TASK_SESSION_STATE_CHANGE_TYPE
{
	TASK_CONSOLE_CONNECT = 1,
	TASK_CONSOLE_DISCONNECT = 2,
	TASK_REMOTE_CONNECT = 3,
	TASK_REMOTE_DISCONNECT = 4,
	TASK_SESSION_LOCK = 7,
	TASK_SESSION_UNLOCK = 8
}
[ComImport]
[Guid("D45B0167-9653-4EEF-B94F-0732CA7AF251")]
[TypeLibType(4288)]
public interface IEventTrigger : ITrigger
{
	[DispId(1)]
	new _TASK_TRIGGER_TYPE2 Type
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(1)]
		get;
	}

	[DispId(2)]
	new string Id
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(2)]
		[return: MarshalAs(UnmanagedType.BStr)]
		get;
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(2)]
		[param: In]
		[param: MarshalAs(UnmanagedType.BStr)]
		set;
	}

	[DispId(3)]
	new IRepetitionPattern Repetition
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(3)]
		[return: MarshalAs(UnmanagedType.Interface)]
		get;
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(3)]
		[param: In]
		[param: MarshalAs(UnmanagedType.Interface)]
		set;
	}

	[DispId(4)]
	new string ExecutionTimeLimit
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(4)]
		[return: MarshalAs(UnmanagedType.BStr)]
		get;
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(4)]
		[param: In]
		[param: MarshalAs(UnmanagedType.BStr)]
		set;
	}

	[DispId(5)]
	new string StartBoundary
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(5)]
		[return: MarshalAs(UnmanagedType.BStr)]
		get;
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(5)]
		[param: In]
		[param: MarshalAs(UnmanagedType.BStr)]
		set;
	}

	[DispId(6)]
	new string EndBoundary
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(6)]
		[return: MarshalAs(UnmanagedType.BStr)]
		get;
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(6)]
		[param: In]
		[param: MarshalAs(UnmanagedType.BStr)]
		set;
	}

	[DispId(7)]
	new bool Enabled
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(7)]
		get;
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(7)]
		[param: In]
		set;
	}

	[DispId(20)]
	string Subscription
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(20)]
		[return: MarshalAs(UnmanagedType.BStr)]
		get;
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(20)]
		[param: In]
		[param: MarshalAs(UnmanagedType.BStr)]
		set;
	}

	[DispId(21)]
	string Delay
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(21)]
		[return: MarshalAs(UnmanagedType.BStr)]
		get;
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(21)]
		[param: In]
		[param: MarshalAs(UnmanagedType.BStr)]
		set;
	}

	[DispId(22)]
	ITaskNamedValueCollection ValueQueries
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(22)]
		[return: MarshalAs(UnmanagedType.Interface)]
		get;
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(22)]
		[param: In]
		[param: MarshalAs(UnmanagedType.Interface)]
		set;
	}
}
[ComImport]
[TypeLibType(4288)]
[Guid("B45747E0-EBA7-4276-9F29-85C5BB300006")]
public interface ITimeTrigger : ITrigger
{
	[DispId(1)]
	new _TASK_TRIGGER_TYPE2 Type
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(1)]
		get;
	}

	[DispId(2)]
	new string Id
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(2)]
		[return: MarshalAs(UnmanagedType.BStr)]
		get;
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(2)]
		[param: In]
		[param: MarshalAs(UnmanagedType.BStr)]
		set;
	}

	[DispId(3)]
	new IRepetitionPattern Repetition
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(3)]
		[return: MarshalAs(UnmanagedType.Interface)]
		get;
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(3)]
		[param: In]
		[param: MarshalAs(UnmanagedType.Interface)]
		set;
	}

	[DispId(4)]
	new string ExecutionTimeLimit
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(4)]
		[return: MarshalAs(UnmanagedType.BStr)]
		get;
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(4)]
		[param: In]
		[param: MarshalAs(UnmanagedType.BStr)]
		set;
	}

	[DispId(5)]
	new string StartBoundary
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(5)]
		[return: MarshalAs(UnmanagedType.BStr)]
		get;
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(5)]
		[param: In]
		[param: MarshalAs(UnmanagedType.BStr)]
		set;
	}

	[DispId(6)]
	new string EndBoundary
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(6)]
		[return: MarshalAs(UnmanagedType.BStr)]
		get;
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(6)]
		[param: In]
		[param: MarshalAs(UnmanagedType.BStr)]
		set;
	}

	[DispId(7)]
	new bool Enabled
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(7)]
		get;
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(7)]
		[param: In]
		set;
	}

	[DispId(20)]
	string RandomDelay
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(20)]
		[return: MarshalAs(UnmanagedType.BStr)]
		get;
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(20)]
		[param: In]
		[param: MarshalAs(UnmanagedType.BStr)]
		set;
	}
}
[ComImport]
[TypeLibType(4288)]
[Guid("126C5CD8-B288-41D5-8DBF-E491446ADC5C")]
public interface IDailyTrigger : ITrigger
{
	[DispId(1)]
	new _TASK_TRIGGER_TYPE2 Type
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(1)]
		get;
	}

	[DispId(2)]
	new string Id
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(2)]
		[return: MarshalAs(UnmanagedType.BStr)]
		get;
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(2)]
		[param: In]
		[param: MarshalAs(UnmanagedType.BStr)]
		set;
	}

	[DispId(3)]
	new IRepetitionPattern Repetition
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(3)]
		[return: MarshalAs(UnmanagedType.Interface)]
		get;
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(3)]
		[param: In]
		[param: MarshalAs(UnmanagedType.Interface)]
		set;
	}

	[DispId(4)]
	new string ExecutionTimeLimit
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(4)]
		[return: MarshalAs(UnmanagedType.BStr)]
		get;
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(4)]
		[param: In]
		[param: MarshalAs(UnmanagedType.BStr)]
		set;
	}

	[DispId(5)]
	new string StartBoundary
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(5)]
		[return: MarshalAs(UnmanagedType.BStr)]
		get;
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(5)]
		[param: In]
		[param: MarshalAs(UnmanagedType.BStr)]
		set;
	}

	[DispId(6)]
	new string EndBoundary
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(6)]
		[return: MarshalAs(UnmanagedType.BStr)]
		get;
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(6)]
		[param: In]
		[param: MarshalAs(UnmanagedType.BStr)]
		set;
	}

	[DispId(7)]
	new bool Enabled
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(7)]
		get;
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(7)]
		[param: In]
		set;
	}

	[DispId(25)]
	short DaysInterval
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(25)]
		get;
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(25)]
		[param: In]
		set;
	}

	[DispId(20)]
	string RandomDelay
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(20)]
		[return: MarshalAs(UnmanagedType.BStr)]
		get;
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(20)]
		[param: In]
		[param: MarshalAs(UnmanagedType.BStr)]
		set;
	}
}
[ComImport]
[TypeLibType(4288)]
[Guid("5038FC98-82FF-436D-8728-A512A57C9DC1")]
public interface IWeeklyTrigger : ITrigger
{
	[DispId(1)]
	new _TASK_TRIGGER_TYPE2 Type
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(1)]
		get;
	}

	[DispId(2)]
	new string Id
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(2)]
		[return: MarshalAs(UnmanagedType.BStr)]
		get;
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(2)]
		[param: In]
		[param: MarshalAs(UnmanagedType.BStr)]
		set;
	}

	[DispId(3)]
	new IRepetitionPattern Repetition
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(3)]
		[return: MarshalAs(UnmanagedType.Interface)]
		get;
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(3)]
		[param: In]
		[param: MarshalAs(UnmanagedType.Interface)]
		set;
	}

	[DispId(4)]
	new string ExecutionTimeLimit
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(4)]
		[return: MarshalAs(UnmanagedType.BStr)]
		get;
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(4)]
		[param: In]
		[param: MarshalAs(UnmanagedType.BStr)]
		set;
	}

	[DispId(5)]
	new string StartBoundary
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(5)]
		[return: MarshalAs(UnmanagedType.BStr)]
		get;
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(5)]
		[param: In]
		[param: MarshalAs(UnmanagedType.BStr)]
		set;
	}

	[DispId(6)]
	new string EndBoundary
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(6)]
		[return: MarshalAs(UnmanagedType.BStr)]
		get;
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(6)]
		[param: In]
		[param: MarshalAs(UnmanagedType.BStr)]
		set;
	}

	[DispId(7)]
	new bool Enabled
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(7)]
		get;
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(7)]
		[param: In]
		set;
	}

	[DispId(25)]
	short DaysOfWeek
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(25)]
		get;
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(25)]
		[param: In]
		set;
	}

	[DispId(26)]
	short WeeksInterval
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(26)]
		get;
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(26)]
		[param: In]
		set;
	}

	[DispId(20)]
	string RandomDelay
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(20)]
		[return: MarshalAs(UnmanagedType.BStr)]
		get;
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(20)]
		[param: In]
		[param: MarshalAs(UnmanagedType.BStr)]
		set;
	}
}
[ComImport]
[Guid("97C45EF1-6B02-4A1A-9C0E-1EBFBA1500AC")]
[TypeLibType(4288)]
public interface IMonthlyTrigger : ITrigger
{
	[DispId(1)]
	new _TASK_TRIGGER_TYPE2 Type
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(1)]
		get;
	}

	[DispId(2)]
	new string Id
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(2)]
		[return: MarshalAs(UnmanagedType.BStr)]
		get;
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(2)]
		[param: In]
		[param: MarshalAs(UnmanagedType.BStr)]
		set;
	}

	[DispId(3)]
	new IRepetitionPattern Repetition
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(3)]
		[return: MarshalAs(UnmanagedType.Interface)]
		get;
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(3)]
		[param: In]
		[param: MarshalAs(UnmanagedType.Interface)]
		set;
	}

	[DispId(4)]
	new string ExecutionTimeLimit
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(4)]
		[return: MarshalAs(UnmanagedType.BStr)]
		get;
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(4)]
		[param: In]
		[param: MarshalAs(UnmanagedType.BStr)]
		set;
	}

	[DispId(5)]
	new string StartBoundary
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(5)]
		[return: MarshalAs(UnmanagedType.BStr)]
		get;
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(5)]
		[param: In]
		[param: MarshalAs(UnmanagedType.BStr)]
		set;
	}

	[DispId(6)]
	new string EndBoundary
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(6)]
		[return: MarshalAs(UnmanagedType.BStr)]
		get;
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(6)]
		[param: In]
		[param: MarshalAs(UnmanagedType.BStr)]
		set;
	}

	[DispId(7)]
	new bool Enabled
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(7)]
		get;
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(7)]
		[param: In]
		set;
	}

	[DispId(25)]
	int DaysOfMonth
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(25)]
		get;
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(25)]
		[param: In]
		set;
	}

	[DispId(26)]
	short MonthsOfYear
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(26)]
		get;
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(26)]
		[param: In]
		set;
	}

	[DispId(27)]
	bool RunOnLastDayOfMonth
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(27)]
		get;
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(27)]
		[param: In]
		set;
	}

	[DispId(20)]
	string RandomDelay
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(20)]
		[return: MarshalAs(UnmanagedType.BStr)]
		get;
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(20)]
		[param: In]
		[param: MarshalAs(UnmanagedType.BStr)]
		set;
	}
}
[ComImport]
[TypeLibType(4288)]
[Guid("77D025A3-90FA-43AA-B52E-CDA5499B946A")]
public interface IMonthlyDOWTrigger : ITrigger
{
	[DispId(1)]
	new _TASK_TRIGGER_TYPE2 Type
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(1)]
		get;
	}

	[DispId(2)]
	new string Id
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(2)]
		[return: MarshalAs(UnmanagedType.BStr)]
		get;
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(2)]
		[param: In]
		[param: MarshalAs(UnmanagedType.BStr)]
		set;
	}

	[DispId(3)]
	new IRepetitionPattern Repetition
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(3)]
		[return: MarshalAs(UnmanagedType.Interface)]
		get;
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(3)]
		[param: In]
		[param: MarshalAs(UnmanagedType.Interface)]
		set;
	}

	[DispId(4)]
	new string ExecutionTimeLimit
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(4)]
		[return: MarshalAs(UnmanagedType.BStr)]
		get;
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(4)]
		[param: In]
		[param: MarshalAs(UnmanagedType.BStr)]
		set;
	}

	[DispId(5)]
	new string StartBoundary
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(5)]
		[return: MarshalAs(UnmanagedType.BStr)]
		get;
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(5)]
		[param: In]
		[param: MarshalAs(UnmanagedType.BStr)]
		set;
	}

	[DispId(6)]
	new string EndBoundary
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(6)]
		[return: MarshalAs(UnmanagedType.BStr)]
		get;
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(6)]
		[param: In]
		[param: MarshalAs(UnmanagedType.BStr)]
		set;
	}

	[DispId(7)]
	new bool Enabled
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(7)]
		get;
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(7)]
		[param: In]
		set;
	}

	[DispId(25)]
	short DaysOfWeek
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(25)]
		get;
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(25)]
		[param: In]
		set;
	}

	[DispId(26)]
	short WeeksOfMonth
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(26)]
		get;
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(26)]
		[param: In]
		set;
	}

	[DispId(27)]
	short MonthsOfYear
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(27)]
		get;
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(27)]
		[param: In]
		set;
	}

	[DispId(28)]
	bool RunOnLastWeekOfMonth
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(28)]
		get;
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(28)]
		[param: In]
		set;
	}

	[DispId(20)]
	string RandomDelay
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(20)]
		[return: MarshalAs(UnmanagedType.BStr)]
		get;
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(20)]
		[param: In]
		[param: MarshalAs(UnmanagedType.BStr)]
		set;
	}
}
[ComImport]
[TypeLibType(4288)]
[Guid("2A9C35DA-D357-41F4-BBC1-207AC1B1F3CB")]
public interface IBootTrigger : ITrigger
{
	[DispId(1)]
	new _TASK_TRIGGER_TYPE2 Type
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(1)]
		get;
	}

	[DispId(2)]
	new string Id
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(2)]
		[return: MarshalAs(UnmanagedType.BStr)]
		get;
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(2)]
		[param: In]
		[param: MarshalAs(UnmanagedType.BStr)]
		set;
	}

	[DispId(3)]
	new IRepetitionPattern Repetition
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(3)]
		[return: MarshalAs(UnmanagedType.Interface)]
		get;
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(3)]
		[param: In]
		[param: MarshalAs(UnmanagedType.Interface)]
		set;
	}

	[DispId(4)]
	new string ExecutionTimeLimit
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(4)]
		[return: MarshalAs(UnmanagedType.BStr)]
		get;
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(4)]
		[param: In]
		[param: MarshalAs(UnmanagedType.BStr)]
		set;
	}

	[DispId(5)]
	new string StartBoundary
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(5)]
		[return: MarshalAs(UnmanagedType.BStr)]
		get;
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(5)]
		[param: In]
		[param: MarshalAs(UnmanagedType.BStr)]
		set;
	}

	[DispId(6)]
	new string EndBoundary
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(6)]
		[return: MarshalAs(UnmanagedType.BStr)]
		get;
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(6)]
		[param: In]
		[param: MarshalAs(UnmanagedType.BStr)]
		set;
	}

	[DispId(7)]
	new bool Enabled
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(7)]
		get;
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(7)]
		[param: In]
		set;
	}

	[DispId(20)]
	string Delay
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(20)]
		[return: MarshalAs(UnmanagedType.BStr)]
		get;
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(20)]
		[param: In]
		[param: MarshalAs(UnmanagedType.BStr)]
		set;
	}
}
[ComImport]
[Guid("4C8FEC3A-C218-4E0C-B23D-629024DB91A2")]
[TypeLibType(4288)]
public interface IRegistrationTrigger : ITrigger
{
	[DispId(1)]
	new _TASK_TRIGGER_TYPE2 Type
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(1)]
		get;
	}

	[DispId(2)]
	new string Id
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(2)]
		[return: MarshalAs(UnmanagedType.BStr)]
		get;
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(2)]
		[param: In]
		[param: MarshalAs(UnmanagedType.BStr)]
		set;
	}

	[DispId(3)]
	new IRepetitionPattern Repetition
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(3)]
		[return: MarshalAs(UnmanagedType.Interface)]
		get;
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(3)]
		[param: In]
		[param: MarshalAs(UnmanagedType.Interface)]
		set;
	}

	[DispId(4)]
	new string ExecutionTimeLimit
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(4)]
		[return: MarshalAs(UnmanagedType.BStr)]
		get;
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(4)]
		[param: In]
		[param: MarshalAs(UnmanagedType.BStr)]
		set;
	}

	[DispId(5)]
	new string StartBoundary
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(5)]
		[return: MarshalAs(UnmanagedType.BStr)]
		get;
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(5)]
		[param: In]
		[param: MarshalAs(UnmanagedType.BStr)]
		set;
	}

	[DispId(6)]
	new string EndBoundary
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(6)]
		[return: MarshalAs(UnmanagedType.BStr)]
		get;
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(6)]
		[param: In]
		[param: MarshalAs(UnmanagedType.BStr)]
		set;
	}

	[DispId(7)]
	new bool Enabled
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(7)]
		get;
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(7)]
		[param: In]
		set;
	}

	[DispId(20)]
	string Delay
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(20)]
		[return: MarshalAs(UnmanagedType.BStr)]
		get;
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(20)]
		[param: In]
		[param: MarshalAs(UnmanagedType.BStr)]
		set;
	}
}
[ComImport]
[Guid("4C3D624D-FD6B-49A3-B9B7-09CB3CD3F047")]
[TypeLibType(4288)]
public interface IExecAction : IAction
{
	[DispId(1)]
	new string Id
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(1)]
		[return: MarshalAs(UnmanagedType.BStr)]
		get;
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(1)]
		[param: In]
		[param: MarshalAs(UnmanagedType.BStr)]
		set;
	}

	[DispId(2)]
	new _TASK_ACTION_TYPE Type
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(2)]
		get;
	}

	[DispId(10)]
	string Path
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(10)]
		[return: MarshalAs(UnmanagedType.BStr)]
		get;
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(10)]
		[param: In]
		[param: MarshalAs(UnmanagedType.BStr)]
		set;
	}

	[DispId(11)]
	string Arguments
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(11)]
		[return: MarshalAs(UnmanagedType.BStr)]
		get;
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(11)]
		[param: In]
		[param: MarshalAs(UnmanagedType.BStr)]
		set;
	}

	[DispId(12)]
	string WorkingDirectory
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(12)]
		[return: MarshalAs(UnmanagedType.BStr)]
		get;
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(12)]
		[param: In]
		[param: MarshalAs(UnmanagedType.BStr)]
		set;
	}
}
[ComImport]
[Guid("F2A82542-BDA5-4E6B-9143-E2BF4F8987B6")]
[TypeLibType(4288)]
public interface IExecAction2 : IExecAction
{
	[DispId(1)]
	new string Id
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(1)]
		[return: MarshalAs(UnmanagedType.BStr)]
		get;
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(1)]
		[param: In]
		[param: MarshalAs(UnmanagedType.BStr)]
		set;
	}

	[DispId(2)]
	new _TASK_ACTION_TYPE Type
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(2)]
		get;
	}

	[DispId(10)]
	new string Path
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(10)]
		[return: MarshalAs(UnmanagedType.BStr)]
		get;
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(10)]
		[param: In]
		[param: MarshalAs(UnmanagedType.BStr)]
		set;
	}

	[DispId(11)]
	new string Arguments
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(11)]
		[return: MarshalAs(UnmanagedType.BStr)]
		get;
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(11)]
		[param: In]
		[param: MarshalAs(UnmanagedType.BStr)]
		set;
	}

	[DispId(12)]
	new string WorkingDirectory
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(12)]
		[return: MarshalAs(UnmanagedType.BStr)]
		get;
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(12)]
		[param: In]
		[param: MarshalAs(UnmanagedType.BStr)]
		set;
	}

	[DispId(13)]
	bool HideAppWindow
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(13)]
		get;
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(13)]
		[param: In]
		set;
	}
}
[ComImport]
[TypeLibType(4288)]
[Guid("505E9E68-AF89-46B8-A30F-56162A83D537")]
public interface IShowMessageAction : IAction
{
	[DispId(1)]
	new string Id
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(1)]
		[return: MarshalAs(UnmanagedType.BStr)]
		get;
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(1)]
		[param: In]
		[param: MarshalAs(UnmanagedType.BStr)]
		set;
	}

	[DispId(2)]
	new _TASK_ACTION_TYPE Type
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(2)]
		get;
	}

	[DispId(10)]
	string Title
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(10)]
		[return: MarshalAs(UnmanagedType.BStr)]
		get;
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(10)]
		[param: In]
		[param: MarshalAs(UnmanagedType.BStr)]
		set;
	}

	[DispId(11)]
	string MessageBody
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(11)]
		[return: MarshalAs(UnmanagedType.BStr)]
		get;
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(11)]
		[param: In]
		[param: MarshalAs(UnmanagedType.BStr)]
		set;
	}
}
[ComImport]
[Guid("6D2FD252-75C5-4F66-90BA-2A7D8CC3039F")]
[TypeLibType(4288)]
public interface IComHandlerAction : IAction
{
	[DispId(1)]
	new string Id
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(1)]
		[return: MarshalAs(UnmanagedType.BStr)]
		get;
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(1)]
		[param: In]
		[param: MarshalAs(UnmanagedType.BStr)]
		set;
	}

	[DispId(2)]
	new _TASK_ACTION_TYPE Type
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(2)]
		get;
	}

	[DispId(10)]
	string ClassId
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(10)]
		[return: MarshalAs(UnmanagedType.BStr)]
		get;
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(10)]
		[param: In]
		[param: MarshalAs(UnmanagedType.BStr)]
		set;
	}

	[DispId(11)]
	string Data
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(11)]
		[return: MarshalAs(UnmanagedType.BStr)]
		get;
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(11)]
		[param: In]
		[param: MarshalAs(UnmanagedType.BStr)]
		set;
	}
}
[ComImport]
[TypeLibType(4288)]
[Guid("10F62C64-7E16-4314-A0C2-0C3683F99D40")]
public interface IEmailAction : IAction
{
	[DispId(1)]
	new string Id
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(1)]
		[return: MarshalAs(UnmanagedType.BStr)]
		get;
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(1)]
		[param: In]
		[param: MarshalAs(UnmanagedType.BStr)]
		set;
	}

	[DispId(2)]
	new _TASK_ACTION_TYPE Type
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(2)]
		get;
	}

	[DispId(10)]
	string Server
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(10)]
		[return: MarshalAs(UnmanagedType.BStr)]
		get;
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(10)]
		[param: In]
		[param: MarshalAs(UnmanagedType.BStr)]
		set;
	}

	[DispId(11)]
	string Subject
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(11)]
		[return: MarshalAs(UnmanagedType.BStr)]
		get;
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(11)]
		[param: In]
		[param: MarshalAs(UnmanagedType.BStr)]
		set;
	}

	[DispId(12)]
	string To
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(12)]
		[return: MarshalAs(UnmanagedType.BStr)]
		get;
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(12)]
		[param: In]
		[param: MarshalAs(UnmanagedType.BStr)]
		set;
	}

	[DispId(13)]
	string Cc
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(13)]
		[return: MarshalAs(UnmanagedType.BStr)]
		get;
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(13)]
		[param: In]
		[param: MarshalAs(UnmanagedType.BStr)]
		set;
	}

	[DispId(14)]
	string Bcc
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(14)]
		[return: MarshalAs(UnmanagedType.BStr)]
		get;
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(14)]
		[param: In]
		[param: MarshalAs(UnmanagedType.BStr)]
		set;
	}

	[DispId(15)]
	string ReplyTo
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(15)]
		[return: MarshalAs(UnmanagedType.BStr)]
		get;
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(15)]
		[param: In]
		[param: MarshalAs(UnmanagedType.BStr)]
		set;
	}

	[DispId(16)]
	string From
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(16)]
		[return: MarshalAs(UnmanagedType.BStr)]
		get;
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(16)]
		[param: In]
		[param: MarshalAs(UnmanagedType.BStr)]
		set;
	}

	[DispId(17)]
	ITaskNamedValueCollection HeaderFields
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(17)]
		[return: MarshalAs(UnmanagedType.Interface)]
		get;
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(17)]
		[param: In]
		[param: MarshalAs(UnmanagedType.Interface)]
		set;
	}

	[DispId(18)]
	string Body
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(18)]
		[return: MarshalAs(UnmanagedType.BStr)]
		get;
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(18)]
		[param: In]
		[param: MarshalAs(UnmanagedType.BStr)]
		set;
	}

	[DispId(19)]
	Array Attachments
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(19)]
		[return: MarshalAs(UnmanagedType.SafeArray, SafeArraySubType = VarEnum.VT_VARIANT)]
		get;
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(19)]
		[param: In]
		[param: MarshalAs(UnmanagedType.SafeArray, SafeArraySubType = VarEnum.VT_VARIANT)]
		set;
	}
}
[ComImport]
[Guid("248919AE-E345-4A6D-8AEB-E0D3165C904E")]
[TypeLibType(4288)]
public interface IPrincipal2
{
	[DispId(10)]
	_TASK_PROCESSTOKENSID ProcessTokenSidType
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(10)]
		get;
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(10)]
		[param: In]
		set;
	}

	[DispId(11)]
	int RequiredPrivilegeCount
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(11)]
		get;
	}

	[DispId(12)]
	string RequiredPrivilege
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(12)]
		[return: MarshalAs(UnmanagedType.BStr)]
		get;
	}

	[MethodImpl(MethodImplOptions.InternalCall)]
	[DispId(13)]
	void AddRequiredPrivilege([In][MarshalAs(UnmanagedType.BStr)] string privilege);
}
public enum _TASK_PROCESSTOKENSID
{
	TASK_PROCESSTOKENSID_NONE,
	TASK_PROCESSTOKENSID_UNRESTRICTED,
	TASK_PROCESSTOKENSID_DEFAULT
}
[ComImport]
[TypeLibType(4288)]
[Guid("2C05C3F0-6EED-4C05-A15F-ED7D7A98A369")]
public interface ITaskSettings2
{
	[DispId(30)]
	bool DisallowStartOnRemoteAppSession
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(30)]
		get;
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(30)]
		[param: In]
		set;
	}

	[DispId(31)]
	bool UseUnifiedSchedulingEngine
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(31)]
		get;
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(31)]
		[param: In]
		set;
	}
}
[ComImport]
[Guid("0AD9D0D7-0C7F-4EBB-9A5F-D1C648DCA528")]
[TypeLibType(4288)]
public interface ITaskSettings3 : ITaskSettings
{
	[DispId(3)]
	new bool AllowDemandStart
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(3)]
		get;
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(3)]
		[param: In]
		set;
	}

	[DispId(4)]
	new string RestartInterval
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(4)]
		[return: MarshalAs(UnmanagedType.BStr)]
		get;
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(4)]
		[param: In]
		[param: MarshalAs(UnmanagedType.BStr)]
		set;
	}

	[DispId(5)]
	new int RestartCount
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(5)]
		get;
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(5)]
		[param: In]
		set;
	}

	[DispId(6)]
	new _TASK_INSTANCES_POLICY MultipleInstances
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(6)]
		get;
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(6)]
		[param: In]
		set;
	}

	[DispId(7)]
	new bool StopIfGoingOnBatteries
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(7)]
		get;
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(7)]
		[param: In]
		set;
	}

	[DispId(8)]
	new bool DisallowStartIfOnBatteries
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(8)]
		get;
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(8)]
		[param: In]
		set;
	}

	[DispId(9)]
	new bool AllowHardTerminate
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(9)]
		get;
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(9)]
		[param: In]
		set;
	}

	[DispId(10)]
	new bool StartWhenAvailable
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(10)]
		get;
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(10)]
		[param: In]
		set;
	}

	[DispId(11)]
	new string XmlText
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(11)]
		[return: MarshalAs(UnmanagedType.BStr)]
		get;
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(11)]
		[param: In]
		[param: MarshalAs(UnmanagedType.BStr)]
		set;
	}

	[DispId(12)]
	new bool RunOnlyIfNetworkAvailable
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(12)]
		get;
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(12)]
		[param: In]
		set;
	}

	[DispId(13)]
	new string ExecutionTimeLimit
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(13)]
		[return: MarshalAs(UnmanagedType.BStr)]
		get;
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(13)]
		[param: In]
		[param: MarshalAs(UnmanagedType.BStr)]
		set;
	}

	[DispId(14)]
	new bool Enabled
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(14)]
		get;
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(14)]
		[param: In]
		set;
	}

	[DispId(15)]
	new string DeleteExpiredTaskAfter
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(15)]
		[return: MarshalAs(UnmanagedType.BStr)]
		get;
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(15)]
		[param: In]
		[param: MarshalAs(UnmanagedType.BStr)]
		set;
	}

	[DispId(16)]
	new int Priority
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(16)]
		get;
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(16)]
		[param: In]
		set;
	}

	[DispId(17)]
	new _TASK_COMPATIBILITY Compatibility
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(17)]
		get;
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(17)]
		[param: In]
		set;
	}

	[DispId(18)]
	new bool Hidden
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(18)]
		get;
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(18)]
		[param: In]
		set;
	}

	[DispId(19)]
	new IIdleSettings IdleSettings
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(19)]
		[return: MarshalAs(UnmanagedType.Interface)]
		get;
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(19)]
		[param: In]
		[param: MarshalAs(UnmanagedType.Interface)]
		set;
	}

	[DispId(20)]
	new bool RunOnlyIfIdle
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(20)]
		get;
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(20)]
		[param: In]
		set;
	}

	[DispId(21)]
	new bool WakeToRun
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(21)]
		get;
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(21)]
		[param: In]
		set;
	}

	[DispId(22)]
	new INetworkSettings NetworkSettings
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(22)]
		[return: MarshalAs(UnmanagedType.Interface)]
		get;
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(22)]
		[param: In]
		[param: MarshalAs(UnmanagedType.Interface)]
		set;
	}

	[DispId(30)]
	bool DisallowStartOnRemoteAppSession
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(30)]
		get;
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(30)]
		[param: In]
		set;
	}

	[DispId(31)]
	bool UseUnifiedSchedulingEngine
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(31)]
		get;
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(31)]
		[param: In]
		set;
	}

	[DispId(40)]
	IMaintenanceSettings MaintenanceSettings
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(40)]
		[return: MarshalAs(UnmanagedType.Interface)]
		get;
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(40)]
		[param: In]
		[param: MarshalAs(UnmanagedType.Interface)]
		set;
	}

	[DispId(42)]
	bool Volatile
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(42)]
		get;
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(42)]
		[param: In]
		set;
	}

	[MethodImpl(MethodImplOptions.InternalCall)]
	[DispId(41)]
	[return: MarshalAs(UnmanagedType.Interface)]
	IMaintenanceSettings CreateMaintenanceSettings();
}
[ComImport]
[TypeLibType(4288)]
[Guid("A6024FA8-9652-4ADB-A6BF-5CFCD877A7BA")]
public interface IMaintenanceSettings
{
	[DispId(34)]
	string Period
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(34)]
		[return: MarshalAs(UnmanagedType.BStr)]
		get;
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(34)]
		[param: In]
		[param: MarshalAs(UnmanagedType.BStr)]
		set;
	}

	[DispId(35)]
	string Deadline
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(35)]
		[return: MarshalAs(UnmanagedType.BStr)]
		get;
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(35)]
		[param: In]
		[param: MarshalAs(UnmanagedType.BStr)]
		set;
	}

	[DispId(36)]
	bool Exclusive
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(36)]
		get;
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(36)]
		[param: In]
		set;
	}
}
public enum _TASK_RUN_FLAGS
{
	TASK_RUN_NO_FLAGS = 0,
	TASK_RUN_AS_SELF = 1,
	TASK_RUN_IGNORE_CONSTRAINTS = 2,
	TASK_RUN_USE_SESSION_ID = 4,
	TASK_RUN_USER_SID = 8
}
public enum _TASK_ENUM_FLAGS
{
	TASK_ENUM_HIDDEN = 1
}
public enum _TASK_CREATION
{
	TASK_VALIDATE_ONLY = 1,
	TASK_CREATE = 2,
	TASK_UPDATE = 4,
	TASK_CREATE_OR_UPDATE = 6,
	TASK_DISABLE = 8,
	TASK_DONT_ADD_PRINCIPAL_ACE = 16,
	TASK_IGNORE_REGISTRATION_TRIGGERS = 32
}
[ComImport]
[DefaultMember("TargetServer")]
[Guid("0F87369F-A4E5-4CFC-BD3E-73E6154572DD")]
[TypeLibType(2)]
[ClassInterface(0)]
public class TaskSchedulerClass : ITaskService, TaskScheduler
{
	[DispId(5)]
	public virtual extern bool Connected
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(5)]
		get;
	}

	[DispId(0)]
	public virtual extern string TargetServer
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(0)]
		[return: MarshalAs(UnmanagedType.BStr)]
		get;
	}

	[DispId(6)]
	public virtual extern string ConnectedUser
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(6)]
		[return: MarshalAs(UnmanagedType.BStr)]
		get;
	}

	[DispId(7)]
	public virtual extern string ConnectedDomain
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(7)]
		[return: MarshalAs(UnmanagedType.BStr)]
		get;
	}

	[DispId(8)]
	public virtual extern uint HighestVersion
	{
		[MethodImpl(MethodImplOptions.InternalCall)]
		[DispId(8)]
		get;
	}

	[MethodImpl(MethodImplOptions.InternalCall)]
	public extern TaskSchedulerClass();

	[MethodImpl(MethodImplOptions.InternalCall)]
	[DispId(1)]
	[return: MarshalAs(UnmanagedType.Interface)]
	public virtual extern ITaskFolder GetFolder([In][MarshalAs(UnmanagedType.BStr)] string Path);

	ITaskFolder ITaskService.GetFolder([In][MarshalAs(UnmanagedType.BStr)] string Path)
	{
		//ILSpy generated this explicit interface implementation from .override directive in GetFolder
		return this.GetFolder(Path);
	}

	[MethodImpl(MethodImplOptions.InternalCall)]
	[DispId(2)]
	[return: MarshalAs(UnmanagedType.Interface)]
	public virtual extern IRunningTaskCollection GetRunningTasks([In] int flags);

	IRunningTaskCollection ITaskService.GetRunningTasks([In] int flags)
	{
		//ILSpy generated this explicit interface implementation from .override directive in GetRunningTasks
		return this.GetRunningTasks(flags);
	}

	[MethodImpl(MethodImplOptions.InternalCall)]
	[DispId(3)]
	[return: MarshalAs(UnmanagedType.Interface)]
	public virtual extern ITaskDefinition NewTask([In] uint flags);

	ITaskDefinition ITaskService.NewTask([In] uint flags)
	{
		//ILSpy generated this explicit interface implementation from .override directive in NewTask
		return this.NewTask(flags);
	}

	[MethodImpl(MethodImplOptions.InternalCall)]
	[DispId(4)]
	public virtual extern void Connect([Optional][In][MarshalAs(UnmanagedType.Struct)] object serverName, [Optional][In][MarshalAs(UnmanagedType.Struct)] object user, [Optional][In][MarshalAs(UnmanagedType.Struct)] object domain, [Optional][In][MarshalAs(UnmanagedType.Struct)] object password);

	void ITaskService.Connect([Optional][In][MarshalAs(UnmanagedType.Struct)] object serverName, [Optional][In][MarshalAs(UnmanagedType.Struct)] object user, [Optional][In][MarshalAs(UnmanagedType.Struct)] object domain, [Optional][In][MarshalAs(UnmanagedType.Struct)] object password)
	{
		//ILSpy generated this explicit interface implementation from .override directive in Connect
		this.Connect(serverName, user, domain, password);
	}
}
[ComImport]
[CoClass(typeof(TaskSchedulerClass))]
[Guid("2FABA4C7-4DA9-4013-9697-20CC3FD40F85")]
public interface TaskScheduler : ITaskService
{
}
[ComImport]
[TypeLibType(2)]
[ClassInterface(0)]
[Guid("F2A69DB7-DA2C-4352-9066-86FEE6DACAC9")]
public class TaskHandlerPSClass : ITaskHandler, TaskHandlerPS
{
	[MethodImpl(MethodImplOptions.InternalCall)]
	public extern TaskHandlerPSClass();

	[MethodImpl(MethodImplOptions.InternalCall)]
	public virtual extern void Start([In][MarshalAs(UnmanagedType.IUnknown)] object pHandlerServices, [In][MarshalAs(UnmanagedType.BStr)] string Data);

	void ITaskHandler.Start([In][MarshalAs(UnmanagedType.IUnknown)] object pHandlerServices, [In][MarshalAs(UnmanagedType.BStr)] string Data)
	{
		//ILSpy generated this explicit interface implementation from .override directive in Start
		this.Start(pHandlerServices, Data);
	}

	[MethodImpl(MethodImplOptions.InternalCall)]
	public virtual extern void Stop([MarshalAs(UnmanagedType.Error)] out int pRetCode);

	void ITaskHandler.Stop([MarshalAs(UnmanagedType.Error)] out int pRetCode)
	{
		//ILSpy generated this explicit interface implementation from .override directive in Stop
		this.Stop(out pRetCode);
	}

	[MethodImpl(MethodImplOptions.InternalCall)]
	public virtual extern void Pause();

	void ITaskHandler.Pause()
	{
		//ILSpy generated this explicit interface implementation from .override directive in Pause
		this.Pause();
	}

	[MethodImpl(MethodImplOptions.InternalCall)]
	public virtual extern void Resume();

	void ITaskHandler.Resume()
	{
		//ILSpy generated this explicit interface implementation from .override directive in Resume
		this.Resume();
	}
}
[ComImport]
[Guid("839D7762-5121-4009-9234-4F0D19394F04")]
[CoClass(typeof(TaskHandlerPSClass))]
public interface TaskHandlerPS : ITaskHandler
{
}
[ComImport]
[Guid("9F15266D-D7BA-48F0-93C1-E6895F6FE5AC")]
[TypeLibType(2)]
[ClassInterface(0)]
public class TaskHandlerStatusPSClass : ITaskHandlerStatus, TaskHandlerStatusPS, ITaskVariables
{
	[MethodImpl(MethodImplOptions.InternalCall)]
	public extern TaskHandlerStatusPSClass();

	[MethodImpl(MethodImplOptions.InternalCall)]
	public virtual extern void UpdateStatus([In] short percentComplete, [In][MarshalAs(UnmanagedType.BStr)] string statusMessage);

	void ITaskHandlerStatus.UpdateStatus([In] short percentComplete, [In][MarshalAs(UnmanagedType.BStr)] string statusMessage)
	{
		//ILSpy generated this explicit interface implementation from .override directive in UpdateStatus
		this.UpdateStatus(percentComplete, statusMessage);
	}

	[MethodImpl(MethodImplOptions.InternalCall)]
	public virtual extern void TaskCompleted([In][MarshalAs(UnmanagedType.Error)] int taskErrCode);

	void ITaskHandlerStatus.TaskCompleted([In][MarshalAs(UnmanagedType.Error)] int taskErrCode)
	{
		//ILSpy generated this explicit interface implementation from .override directive in TaskCompleted
		this.TaskCompleted(taskErrCode);
	}

	[MethodImpl(MethodImplOptions.InternalCall)]
	[return: MarshalAs(UnmanagedType.BStr)]
	public virtual extern string GetInput();

	string ITaskVariables.GetInput()
	{
		//ILSpy generated this explicit interface implementation from .override directive in GetInput
		return this.GetInput();
	}

	[MethodImpl(MethodImplOptions.InternalCall)]
	public virtual extern void SetOutput([In][MarshalAs(UnmanagedType.BStr)] string input);

	void ITaskVariables.SetOutput([In][MarshalAs(UnmanagedType.BStr)] string input)
	{
		//ILSpy generated this explicit interface implementation from .override directive in SetOutput
		this.SetOutput(input);
	}

	[MethodImpl(MethodImplOptions.InternalCall)]
	[return: MarshalAs(UnmanagedType.BStr)]
	public virtual extern string GetContext();

	string ITaskVariables.GetContext()
	{
		//ILSpy generated this explicit interface implementation from .override directive in GetContext
		return this.GetContext();
	}
}
[ComImport]
[Guid("EAEC7A8F-27A0-4DDC-8675-14726A01A38A")]
[CoClass(typeof(TaskHandlerStatusPSClass))]
public interface TaskHandlerStatusPS : ITaskHandlerStatus
{
}
