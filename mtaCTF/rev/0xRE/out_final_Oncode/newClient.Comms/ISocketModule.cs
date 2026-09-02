using Models;
using algorithm;

namespace newClient.Comms;

public interface ISocketModule
{
	AesManaged aesManaged { get; set; }

	bool Connected { get; set; }

	ProType ProtocolType { get; set; }

	Channel<byte[]> ConsumerChannel { get; set; }

	bool socketConnect(string host, int port);

	int socketSend(byte[] message);

	void socketclose();
}
