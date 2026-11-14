// ===== FUNC 210f0 size=237

void FUN_000210f0(long *param_1,undefined param_2)

{
  undefined (*pauVar1) [16];
  long lVar2;
  
  switch(param_2) {
  default:
    *param_1 = 0;
    break;
  case 1:
    lVar2 = FUN_00041fe0(0x30);
    *(undefined4 *)(lVar2 + 8) = 0;
    *(undefined8 *)(lVar2 + 0x10) = 0;
    *(long *)(lVar2 + 0x18) = lVar2 + 8;
    *(long *)(lVar2 + 0x20) = lVar2 + 8;
    *(undefined8 *)(lVar2 + 0x28) = 0;
    *param_1 = lVar2;
    break;
  case 2:
    pauVar1 = (undefined (*) [16])FUN_00041fe0(0x18);
    *(undefined8 *)pauVar1[1] = 0;
    *pauVar1 = (undefined  [16])0x0;
    *param_1 = (long)pauVar1;
    break;
  case 3:
    lVar2 = FUN_00041fe0(0x20);
                    /* try { // try from 000211f7 to 000211fb has its CatchHandler @ 00021204 */
    FUN_00018b10(lVar2,&DAT_000e3155);
    *param_1 = lVar2;
    break;
  case 4:
    *(undefined *)param_1 = 0;
    return;
  case 7:
    *param_1 = 0;
    return;
  case 8:
    pauVar1 = (undefined (*) [16])FUN_00041fe0(0x28);
    *(undefined8 *)pauVar1[1] = 0;
    *(undefined8 *)(pauVar1[1] + 8) = 0;
    pauVar1[2][0] = 0;
    *pauVar1 = (undefined  [16])0x0;
    *param_1 = (long)pauVar1;
  }
  return;
}


