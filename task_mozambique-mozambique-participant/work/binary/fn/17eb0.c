// ===== FUNC 17eb0 size=79

undefined  [16] FUN_00017eb0(long param_1,uint param_2)

{
  long lVar1;
  long lVar2;
  undefined auVar3 [16];
  undefined auVar4 [16];
  
  lVar2 = (ulong)param_2 - 1;
  lVar1 = (ulong)param_2 + 0x3e;
  if (-1 < lVar2) {
    lVar1 = lVar2;
  }
  param_1 = param_1 + (lVar1 >> 6) * 8;
  if (lVar2 % 0x40 != -1) {
    auVar3._8_8_ = 1L << ((byte)(lVar2 % 0x40) & 0x3f);
    auVar3._0_8_ = param_1;
    return auVar3;
  }
  auVar4._8_8_ = 0x8000000000000000;
  auVar4._0_8_ = param_1 + -8;
  return auVar4;
}


