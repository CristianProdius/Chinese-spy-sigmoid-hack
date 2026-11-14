// ===== FUNC 149fe size=30

void FUN_000149fe(void)

{
  long *plVar1;
  long *plVar2;
  int iVar3;
  long lVar4;
  ulong unaff_RBX;
  long lVar5;
  long unaff_RBP;
  code *unaff_R13;
  
  FUN_000d36e0();
  FUN_000410a0();
                    /* try { // try from 00014a0e to 00014a12 has its CatchHandler @ 00014a3a */
  FUN_00041110();
  lVar4 = *(long *)(unaff_RBP + 0x18);
  while (unaff_RBX = unaff_RBX + 1, unaff_RBX < *(ulong *)(unaff_RBP + 0x10)) {
    plVar2 = *(long **)(lVar4 + unaff_RBX * 8);
    if (plVar2 != (long *)0x0) {
      if (*PTR___libc_single_threaded_00122b38 == '\0') {
        LOCK();
        plVar1 = plVar2 + 1;
        iVar3 = *(int *)plVar1;
        *(int *)plVar1 = *(int *)plVar1 + -1;
        UNLOCK();
      }
      else {
        iVar3 = *(int *)(plVar2 + 1);
        *(int *)(plVar2 + 1) = iVar3 + -1;
      }
      if (iVar3 == 1) {
        if (*(code **)(*plVar2 + 8) == unaff_R13) {
          FUN_00042ee0();
          FUN_000d36e0(plVar2);
        }
        else {
          (**(code **)(*plVar2 + 8))(plVar2);
        }
      }
      lVar4 = *(long *)(unaff_RBP + 0x18);
    }
  }
  if (lVar4 != 0) {
    thunk_FUN_000d36e0();
  }
  lVar4 = *(long *)(unaff_RBP + 0x20);
  lVar5 = 0;
  if (lVar4 != 0) {
    do {
      if (*(long *)(lVar4 + lVar5) != 0) {
        thunk_FUN_000d36e0();
        lVar4 = *(long *)(unaff_RBP + 0x20);
      }
      lVar5 = lVar5 + 8;
    } while (lVar5 != 0x60);
    if (lVar4 != 0) {
      thunk_FUN_000d36e0(lVar4);
      return;
    }
  }
  return;
}


