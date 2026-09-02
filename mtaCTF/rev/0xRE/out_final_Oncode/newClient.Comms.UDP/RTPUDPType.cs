namespace newClient.Comms.UDP;

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
