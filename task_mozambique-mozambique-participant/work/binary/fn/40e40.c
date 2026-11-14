// ===== FUNC 40e40 size=172

ulong * FUN_00040e40(long param_1)

{
  int iVar1;
  ulong uVar2;
  ulong *puVar3;
  ulong *puVar4;
  ulong *puVar5;
  ulong uVar6;
  
  iVar1 = pthread_mutex_lock((pthread_mutex_t *)&DAT_001231a0);
  if (iVar1 == 0) {
    uVar2 = param_1 + 0x10;
    if (uVar2 < 0x10) {
      uVar2 = 0x10;
    }
    puVar4 = (ulong *)&DAT_001231c8;
    uVar2 = uVar2 + 0xf & 0xfffffffffffffff0;
    puVar5 = DAT_001231c8;
    if (DAT_001231c8 == (ulong *)0x0) {
      puVar5 = (ulong *)0x0;
    }
    else {
      do {
        if (uVar2 <= *puVar5) {
          uVar6 = *puVar5 - uVar2;
          if (uVar6 < 0x10) {
            *puVar5 = *puVar5;
            puVar3 = (ulong *)puVar5[1];
          }
          else {
            puVar3 = (ulong *)((long)puVar5 + uVar2);
            puVar3[1] = puVar5[1];
            puVar5 = (ulong *)*puVar4;
            *puVar3 = uVar6;
            *puVar5 = uVar2;
          }
          *puVar4 = (ulong)puVar3;
          puVar5 = puVar5 + 2;
          break;
        }
        puVar4 = puVar5 + 1;
        puVar5 = (ulong *)puVar5[1];
      } while (puVar5 != (ulong *)0x0);
    }
    iVar1 = pthread_mutex_unlock((pthread_mutex_t *)&DAT_001231a0);
    if (iVar1 == 0) {
      return puVar5;
    }
  }
  else {
    FUN_00014676();
  }
  FUN_000146a9();
                    /* WARNING: Subroutine does not return */
  abort();
}


