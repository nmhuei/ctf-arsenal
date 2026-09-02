// Function: FUN_00011000 at 00011000

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_00011000(uint param_1,int param_2)

{
  _DAT_00015018 = param_2 << 0x10 ^ param_1;
  return;
}



// Function: WinCaptureDeviceControl at 00011010

undefined4 WinCaptureDeviceControl(undefined8 param_1,longlong param_2)

{
  undefined8 *puVar1;
  int *piVar2;
  ulonglong uVar3;
  uint uVar4;
  uint uVar5;
  undefined4 uVar6;
  ulonglong uVar7;
  uint *puVar8;
  longlong lVar9;
  undefined8 *puVar10;
  undefined8 *puVar11;
  undefined *puVar12;
  
                    /* 0x1010  2  WinCaptureDeviceControl */
  puVar8 = *(uint **)(param_2 + 0x18);
  uVar5 = *(uint *)(param_2 + 0x7c);
  switch(*(undefined4 *)(param_2 + 0x80)) {
  case 0xc2002000:
    if ((uVar5 < 0x1008) || (uVar5 = *puVar8, 3 < uVar5)) goto LAB_00011330;
    *(uint *)(&DAT_00019020 + (ulonglong)uVar5 * 4) = puVar8[1];
    puVar11 = (undefined8 *)(&DAT_00015020 + (ulonglong)uVar5 * 0x1000);
    for (lVar9 = 0x200; puVar8 = puVar8 + 2, lVar9 != 0; lVar9 = lVar9 + -1) {
      *puVar11 = *(undefined8 *)puVar8;
      puVar11 = puVar11 + 1;
    }
    break;
  default:
    goto switchD_00011048_caseD_c2002001;
  case 0xc2002004:
    if ((uVar5 < 4) || (uVar5 = *puVar8, 0x1ff < uVar5 - 1)) goto LAB_00011330;
    if (DAT_00015010 != (undefined8 *)0x0) goto LAB_00011358;
    uVar4 = (uVar5 + 0xf & 0xfffffff0) + DAT_00019030;
    DAT_00015008 = uVar5;
    if (0x10000 < uVar4) goto LAB_00011347;
    DAT_00015010 = (undefined8 *)(&DAT_00019040 + DAT_00019030);
    DAT_00019030 = uVar4;
    break;
  case 0xc2002008:
    if (DAT_00015000 != (int *)0x0) {
LAB_00011358:
      uVar6 = 0xc0000022;
      goto LAB_00011098;
    }
    if (0x10000 < DAT_00019030 + 0x10) {
LAB_00011347:
      uVar6 = 0xc000009a;
      goto LAB_00011098;
    }
    DAT_00015000 = (int *)(&DAT_00019040 + DAT_00019030);
    piVar2 = DAT_00015000 + 1;
    DAT_00019030 = DAT_00019030 + 0x10;
    DAT_00015000[0] = 0x4b455901;
    *piVar2 = 0;
    break;
  case 0xc200200c:
    if ((3 < uVar5) && (uVar5 = *puVar8, uVar5 < 4)) {
      puVar12 = &DAT_00019020;
      uVar3 = (ulonglong)uVar5;
      if (*(uint *)(&DAT_00019020 + uVar3 * 4) <= DAT_00015008) {
        param_2 = FUN_00011000(uVar5,*(uint *)(&DAT_00019020 + uVar3 * 4));
        puVar11 = DAT_00015010;
        uVar7 = (ulonglong)*(uint *)(puVar12 + uVar3 * 4);
        if (DAT_00015010 != (undefined8 *)0x0) {
          if (0x1000 < *(uint *)(puVar12 + uVar3 * 4)) {
            uVar7 = 0x1000;
          }
          lVar9 = uVar3 * 0x1000;
          puVar10 = (undefined8 *)(&DAT_00015020 + lVar9);
          uVar5 = (uint)uVar7;
          if (uVar5 < 8) {
            if ((uVar7 & 4) == 0) {
              if ((uVar5 != 0) &&
                 (*(undefined1 *)DAT_00015010 = *(undefined1 *)puVar10, (uVar7 & 2) != 0)) {
                *(undefined2 *)((longlong)puVar11 + (uVar7 - 2)) =
                     *(undefined2 *)(lVar9 + 0x1501e + uVar7);
              }
            }
            else {
              *(undefined4 *)DAT_00015010 = *(undefined4 *)puVar10;
              *(undefined4 *)((longlong)puVar11 + (uVar7 - 4)) =
                   *(undefined4 *)(lVar9 + 0x1501c + uVar7);
            }
          }
          else {
            puVar1 = DAT_00015010 + 1;
            *DAT_00015010 = *puVar10;
            *(undefined8 *)((longlong)puVar11 + (uVar7 - 8)) =
                 *(undefined8 *)(&DAT_00015018 + uVar7 + lVar9);
            lVar9 = (longlong)puVar11 - (longlong)((ulonglong)puVar1 & 0xfffffffffffffff8);
            puVar11 = (undefined8 *)((longlong)puVar10 - lVar9);
            puVar10 = (undefined8 *)((ulonglong)puVar1 & 0xfffffffffffffff8);
            for (uVar3 = (ulonglong)((int)lVar9 + uVar5 >> 3); uVar3 != 0; uVar3 = uVar3 - 1) {
              *puVar10 = *puVar11;
              puVar11 = puVar11 + 1;
              puVar10 = puVar10 + 1;
            }
          }
          break;
        }
        goto switchD_00011048_caseD_c2002001;
      }
    }
LAB_00011330:
    uVar6 = 0xc000000d;
    goto LAB_00011098;
  case 0xc2002010:
    if (DAT_00015000 != (int *)0x0) {
      if (*DAT_00015000 == 0x4b455901) {
        if (DAT_00015000[1] == 0) {
          uVar6 = 0xc0000022;
        }
        else {
          if (0x7f < *(uint *)(param_2 + 0x78)) {
            puVar8[8] = 0;
            puVar8[9] = 0;
            puVar8[0] = 0x7b465443;
            puVar8[1] = 0x63616c70;
            puVar8[2] = 0x6c6f6865;
            puVar8[3] = 0x5f726564;
            puVar8[4] = 0x5f746573;
            puVar8[5] = 0x725f7461;
            puVar8[6] = 0x69746e75;
            puVar8[7] = 0x7d656d;
            puVar8[10] = 0;
            puVar8[0xb] = 0;
            puVar8[0xc] = 0;
            puVar8[0xd] = 0;
            puVar8[0xe] = 0;
            puVar8[0xf] = 0;
            puVar8[0x10] = 0;
            puVar8[0x11] = 0;
            puVar8[0x12] = 0;
            puVar8[0x13] = 0;
            puVar8[0x14] = 0;
            puVar8[0x15] = 0;
            puVar8[0x16] = 0;
            puVar8[0x17] = 0;
            puVar8[0x18] = 0;
            puVar8[0x19] = 0;
            puVar8[0x1a] = 0;
            puVar8[0x1b] = 0;
            puVar8[0x1c] = 0;
            puVar8[0x1d] = 0;
            puVar8[0x1e] = 0;
            puVar8[0x1f] = 0;
            *(undefined4 *)(param_2 + 0x38) = 0x80;
            *(undefined4 *)(param_2 + 0x30) = 0;
            return 0;
          }
          uVar6 = 0xc0000023;
        }
        goto LAB_00011098;
      }
      goto LAB_00011358;
    }
    goto switchD_00011048_caseD_c2002001;
  }
  uVar6 = 0;
LAB_00011098:
  *(undefined4 *)(param_2 + 0x38) = 0;
  *(undefined4 *)(param_2 + 0x30) = uVar6;
  return uVar6;
switchD_00011048_caseD_c2002001:
  uVar6 = 0xc0000010;
  goto LAB_00011098;
}



// Function: DriverEntry at 00011390

undefined8 DriverEntry(longlong param_1)

{
                    /* 0x1390  1  DriverEntry */
  DAT_00019030 = 0;
  DAT_00015010 = 0;
  DAT_00015000 = 0;
  *(code **)(param_1 + 0xa8) = WinCaptureDeviceControl;
  return 0;
}



