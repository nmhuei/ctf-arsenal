using System.CodeDom.Compiler;
using System.ComponentModel;
using System.Diagnostics;
using System.Globalization;
using System.Resources;
using System.Runtime.CompilerServices;

namespace client.Properties;

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
