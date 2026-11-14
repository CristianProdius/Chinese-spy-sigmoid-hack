// ===== FUNC 1fd50 size=301

void FUN_0001fd50(long *param_1,ulong param_2)

{
  undefined8 *puVar1;
  long *plVar2;
  long *plVar3;
  long lVar4;
  undefined auVar5 [16];
  undefined8 uVar6;
  ulong uVar7;
  long *plVar8;
  long lVar9;
  undefined8 *unaff_R14;
  
  puVar1 = (undefined8 *)(param_2 / 9 + 1);
  uVar7 = param_2 / 9 + 3;
  if (uVar7 < 9) {
    param_1[1] = 8;
    lVar9 = 0x40;
  }
  else {
    param_1[1] = uVar7;
    lVar9 = uVar7 * 8;
    if (uVar7 >> 0x3c != 0) {
      uVar6 = FUN_00015c55(lVar9);
                    /* catch(type#1 @ 00000000) { ... } // from try @ 0001fdbd with catch @ 0001fe5b
                        */
      FUN_000410a0(uVar6);
      for (; unaff_R14 < puVar1; unaff_R14 = unaff_R14 + 1) {
        thunk_FUN_000d36e0(*unaff_R14,0x1f8);
      }
                    /* WARNING: Subroutine does not return */
                    /* try { // try from 0001fe7b to 0001fe7f has its CatchHandler @ 0001fe80 */
      FUN_00041f50();
    }
  }
  lVar9 = FUN_00041fe0(lVar9);
  *param_1 = lVar9;
  plVar2 = (long *)(lVar9 + ((ulong)(param_1[1] - (long)puVar1) >> 1) * 8);
  plVar3 = plVar2 + (long)puVar1;
  for (plVar8 = plVar2; plVar8 < plVar3; plVar8 = plVar8 + 1) {
                    /* try { // try from 0001fdbd to 0001fdc1 has its CatchHandler @ 0001fe5b */
    lVar9 = FUN_00041fe0(0x1f8);
    *plVar8 = lVar9;
  }
  lVar9 = *plVar2;
  lVar4 = plVar3[-1];
  param_1[5] = (long)plVar2;
  param_1[3] = lVar9;
  param_1[4] = lVar9 + 0x1f8;
  param_1[9] = (long)(plVar3 + -1);
  param_1[2] = lVar9;
  param_1[8] = lVar4 + 0x1f8;
  auVar5._8_8_ = 0;
  auVar5._0_8_ = param_2;
  param_1[7] = lVar4;
  param_1[6] = lVar4 + (param_2 -
                       ((SUB168(ZEXT816(0xe38e38e38e38e38f) * auVar5,8) & 0xfffffffffffffff8) +
                       param_2 / 9)) * 0x38;
  return;
}


