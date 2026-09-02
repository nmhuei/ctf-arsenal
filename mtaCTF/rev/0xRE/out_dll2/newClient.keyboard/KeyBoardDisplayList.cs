using System.Collections;

namespace newClient.keyboard;

public static class KeyBoardDisplayList
{
	private static Hashtable HtKeyBoardButton = new Hashtable();

	public static void clearHashtable()
	{
		HtKeyBoardButton.Clear();
	}

	public static void Init()
	{
		if (HtKeyBoardButton.Count == 0)
		{
			HtKeyBoardButton.Add(0, "[None]");
			HtKeyBoardButton.Add(8, "[Backspace]");
			HtKeyBoardButton.Add(9, "[Tab]");
			HtKeyBoardButton.Add(12, "[Clear]");
			HtKeyBoardButton.Add(13, "[Enter]");
			HtKeyBoardButton.Add(16, "[Shift]");
			HtKeyBoardButton.Add(17, "[Ctrl]");
			HtKeyBoardButton.Add(18, "[Alt]");
			HtKeyBoardButton.Add(19, "[Pause]");
			HtKeyBoardButton.Add(20, "[CapsLock]");
			HtKeyBoardButton.Add(27, "[Esc]");
			HtKeyBoardButton.Add(32, " ");
			HtKeyBoardButton.Add(33, "[PageUp]");
			HtKeyBoardButton.Add(34, "[PageDown]");
			HtKeyBoardButton.Add(35, "[End]");
			HtKeyBoardButton.Add(36, "[Home]");
			HtKeyBoardButton.Add(37, "[←]");
			HtKeyBoardButton.Add(38, "[↑]");
			HtKeyBoardButton.Add(39, "[→]");
			HtKeyBoardButton.Add(40, "[↓]");
			HtKeyBoardButton.Add(41, "[Select]");
			HtKeyBoardButton.Add(42, "[PrintScreen]");
			HtKeyBoardButton.Add(43, "[Execute]");
			HtKeyBoardButton.Add(44, "[SnapShot]");
			HtKeyBoardButton.Add(45, "[Insert]");
			HtKeyBoardButton.Add(46, "[Delete]");
			HtKeyBoardButton.Add(47, "[Help]");
			HtKeyBoardButton.Add(48, "0");
			HtKeyBoardButton.Add(49, "1");
			HtKeyBoardButton.Add(50, "2");
			HtKeyBoardButton.Add(51, "3");
			HtKeyBoardButton.Add(52, "4");
			HtKeyBoardButton.Add(53, "5");
			HtKeyBoardButton.Add(54, "6");
			HtKeyBoardButton.Add(55, "7");
			HtKeyBoardButton.Add(56, "8");
			HtKeyBoardButton.Add(57, "9");
			HtKeyBoardButton.Add(65, "A");
			HtKeyBoardButton.Add(66, "B");
			HtKeyBoardButton.Add(67, "C");
			HtKeyBoardButton.Add(68, "D");
			HtKeyBoardButton.Add(69, "E");
			HtKeyBoardButton.Add(70, "F");
			HtKeyBoardButton.Add(71, "G");
			HtKeyBoardButton.Add(72, "H");
			HtKeyBoardButton.Add(73, "I");
			HtKeyBoardButton.Add(74, "J");
			HtKeyBoardButton.Add(75, "K");
			HtKeyBoardButton.Add(76, "L");
			HtKeyBoardButton.Add(77, "M");
			HtKeyBoardButton.Add(78, "N");
			HtKeyBoardButton.Add(79, "O");
			HtKeyBoardButton.Add(80, "P");
			HtKeyBoardButton.Add(81, "Q");
			HtKeyBoardButton.Add(82, "R");
			HtKeyBoardButton.Add(83, "S");
			HtKeyBoardButton.Add(84, "T");
			HtKeyBoardButton.Add(85, "U");
			HtKeyBoardButton.Add(86, "V");
			HtKeyBoardButton.Add(87, "W");
			HtKeyBoardButton.Add(88, "X");
			HtKeyBoardButton.Add(89, "Y");
			HtKeyBoardButton.Add(90, "Z");
			HtKeyBoardButton.Add(91, "[LWin]");
			HtKeyBoardButton.Add(92, "[RWin]");
			HtKeyBoardButton.Add(93, "[Apps]");
			HtKeyBoardButton.Add(96, "0");
			HtKeyBoardButton.Add(97, "1");
			HtKeyBoardButton.Add(98, "2");
			HtKeyBoardButton.Add(99, "3");
			HtKeyBoardButton.Add(100, "4");
			HtKeyBoardButton.Add(101, "5");
			HtKeyBoardButton.Add(102, "6");
			HtKeyBoardButton.Add(103, "7");
			HtKeyBoardButton.Add(104, "8");
			HtKeyBoardButton.Add(105, "9");
			HtKeyBoardButton.Add(106, "*");
			HtKeyBoardButton.Add(107, "+");
			HtKeyBoardButton.Add(108, "[Enter]");
			HtKeyBoardButton.Add(109, "-");
			HtKeyBoardButton.Add(110, ".");
			HtKeyBoardButton.Add(111, "/");
			HtKeyBoardButton.Add(112, "F1");
			HtKeyBoardButton.Add(113, "F2");
			HtKeyBoardButton.Add(114, "F3");
			HtKeyBoardButton.Add(115, "F4");
			HtKeyBoardButton.Add(116, "F5");
			HtKeyBoardButton.Add(117, "F6");
			HtKeyBoardButton.Add(118, "F7");
			HtKeyBoardButton.Add(119, "F8");
			HtKeyBoardButton.Add(120, "F9");
			HtKeyBoardButton.Add(121, "F10");
			HtKeyBoardButton.Add(122, "F11");
			HtKeyBoardButton.Add(123, "F12");
			HtKeyBoardButton.Add(124, "F13");
			HtKeyBoardButton.Add(125, "F14");
			HtKeyBoardButton.Add(126, "F15");
			HtKeyBoardButton.Add(127, "F16");
			HtKeyBoardButton.Add(144, "[NumLock]");
			HtKeyBoardButton.Add(145, "[ScreenPrint]");
			HtKeyBoardButton.Add(160, "[Shift]");
			HtKeyBoardButton.Add(161, "[Shift]");
			HtKeyBoardButton.Add(162, "[Ctrl]");
			HtKeyBoardButton.Add(163, "[Ctrl]");
			HtKeyBoardButton.Add(164, "[Alt]");
			HtKeyBoardButton.Add(165, "[Alt]");
			HtKeyBoardButton.Add(186, ";");
			HtKeyBoardButton.Add(187, "+");
			HtKeyBoardButton.Add(188, ",");
			HtKeyBoardButton.Add(189, "-");
			HtKeyBoardButton.Add(190, ".");
			HtKeyBoardButton.Add(191, "/");
			HtKeyBoardButton.Add(192, "~");
			HtKeyBoardButton.Add(219, "[");
			HtKeyBoardButton.Add(220, "\\");
			HtKeyBoardButton.Add(221, "]");
			HtKeyBoardButton.Add(222, "'");
		}
	}

	public static string GetStrByCode(int code)
	{
		if (HtKeyBoardButton.Contains(code))
		{
			return ((string)HtKeyBoardButton[code]) ?? null;
		}
		return null;
	}
}
