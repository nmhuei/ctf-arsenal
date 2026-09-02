using System;
using System.Linq;
using System.Security.Cryptography;
using System.Text;

namespace algorithm;

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
