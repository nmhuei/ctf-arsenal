using System.IO;
using System.Runtime.Serialization;
using System.Runtime.Serialization.Formatters.Binary;
using System.Runtime.Serialization.Json;

namespace algorithm;

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
