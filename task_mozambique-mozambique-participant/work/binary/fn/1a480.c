// ===== FUNC 1a480 size=245

long FUN_0001a480(long param_1,undefined8 param_2,long *param_3)

{
  uint uVar1;
  long lVar2;
  long lVar3;
  undefined auVar4 [16];
  
  lVar2 = FUN_00041fe0(0x50);
  param_3 = (long *)*param_3;
  *(long *)(lVar2 + 0x20) = lVar2 + 0x30;
  lVar3 = *param_3;
                    /* try { // try from 0001a4bb to 0001a4bf has its CatchHandler @ 0001a584 */
  FUN_00017e00(lVar2 + 0x20,lVar3,param_3[1] + lVar3);
  *(undefined *)(lVar2 + 0x40) = 0;
  *(undefined8 *)(lVar2 + 0x48) = 0;
  auVar4 = FUN_00026160(param_1,param_2,lVar2 + 0x20);
  lVar3 = auVar4._8_8_;
  if (lVar3 != 0) {
    uVar1 = 1;
    if ((auVar4._0_8_ == 0) && (param_1 + 8 != lVar3)) {
      uVar1 = FUN_00017b10(*(undefined8 *)(lVar2 + 0x20),*(undefined8 *)(lVar2 + 0x28),
                           *(undefined8 *)(lVar3 + 0x20),*(undefined8 *)(lVar3 + 0x28));
      uVar1 = uVar1 >> 0x1f;
    }
    FUN_00049eb0(uVar1,lVar2,lVar3,param_1 + 8);
    *(long *)(param_1 + 0x28) = *(long *)(param_1 + 0x28) + 1;
    return lVar2;
  }
  FUN_00024620(lVar2 + 0x48,0);
  if (lVar2 + 0x30 != *(long *)(lVar2 + 0x20)) {
    thunk_FUN_000d36e0(*(long *)(lVar2 + 0x20),*(long *)(lVar2 + 0x30) + 1);
  }
  thunk_FUN_000d36e0(lVar2,0x50);
  return auVar4._0_8_;
}


