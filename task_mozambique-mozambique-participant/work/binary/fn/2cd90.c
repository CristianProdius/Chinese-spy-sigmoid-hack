// ===== FUNC 2cd90 size=144

void FUN_0002cd90(long param_1,long param_2)

{
  long lVar1;
  long lVar2;
  
  if (0x1340 < param_2 - param_1) {
    lVar2 = ((param_2 - param_1 >> 5) * 0x2e8ba2e8ba2e8ba3 >> 1) * 0x160;
    lVar1 = param_1 + lVar2;
    FUN_0002cd90(param_1,lVar1);
    FUN_0002cd90(lVar1,param_2);
    FUN_0002cc00(param_1,lVar1,param_2,(lVar2 >> 5) * 0x2e8ba2e8ba2e8ba3,
                 (param_2 - lVar1 >> 5) * 0x2e8ba2e8ba2e8ba3);
    return;
  }
  FUN_0001ae80();
  return;
}


