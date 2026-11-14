// ===== FUNC 17b10 size=78

ulong FUN_00017b10(void *param_1,ulong param_2,void *param_3,ulong param_4)

{
  uint uVar1;
  ulong uVar2;
  
  uVar2 = param_4;
  if (param_2 <= param_4) {
    uVar2 = param_2;
  }
  if (uVar2 != 0) {
    uVar1 = memcmp(param_1,param_3,uVar2);
    if (uVar1 != 0) {
      return (ulong)uVar1;
    }
  }
  param_2 = param_2 - param_4;
  uVar2 = 0x7fffffff;
  if (((long)param_2 < 0x80000000) && (uVar2 = 0x80000000, -0x80000001 < (long)param_2)) {
    uVar2 = param_2 & 0xffffffff;
  }
  return uVar2;
}


