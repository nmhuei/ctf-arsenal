namespace Models;

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
