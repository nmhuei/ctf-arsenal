using System;
using System.Security.Cryptography;
using System.Text;

namespace algorithm;

public class Hash
{
	public static string GetHash(string str, string Replace)
	{
		using MD5CryptoServiceProvider mD5CryptoServiceProvider = new MD5CryptoServiceProvider();
		return BitConverter.ToString(mD5CryptoServiceProvider.ComputeHash(Encoding.UTF8.GetBytes(str))).Replace("-", Replace);
	}
}
