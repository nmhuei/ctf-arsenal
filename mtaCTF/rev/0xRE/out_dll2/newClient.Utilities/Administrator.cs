using System.Security.Principal;

namespace newClient.Utilities;

public class Administrator
{
	public static bool IsAdministrator()
	{
		using WindowsIdentity ntIdentity = WindowsIdentity.GetCurrent();
		return new WindowsPrincipal(ntIdentity).IsInRole(WindowsBuiltInRole.Administrator);
	}
}
