// ===== FUNC 2aaf0 size=163

void FUN_0002aaf0(long param_1,long param_2)

{
  long lVar1;
  long lVar2;
  
  if (0x70 < param_2 - param_1) {
    lVar2 = (param_2 - param_1 >> 4) * 8;
    lVar1 = param_1 + lVar2;
    FUN_0002aaf0(param_1,lVar1);
    FUN_0002aaf0(lVar1,param_2);
    FUN_0002a900(param_1,lVar1,param_2,lVar2 >> 3,param_2 - lVar1 >> 3);
    return;
  }
  FUN_00025060();
  return;
}


