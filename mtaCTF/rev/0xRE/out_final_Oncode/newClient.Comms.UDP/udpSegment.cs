using System;

namespace newClient.Comms.UDP;

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
