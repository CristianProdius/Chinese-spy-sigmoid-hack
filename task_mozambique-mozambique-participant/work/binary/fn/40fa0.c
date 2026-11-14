// ===== FUNC 40fa0 size=51

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_00040fa0(long param_1)

{
  void *__ptr;
  
  __ptr = (void *)(param_1 + -0x80);
  if ((DAT_001231d0 < __ptr) && (__ptr < (void *)((long)DAT_001231d0 + _DAT_001231d8))) {
    FUN_00040d40();
    return;
  }
  free(__ptr);
  return;
}


