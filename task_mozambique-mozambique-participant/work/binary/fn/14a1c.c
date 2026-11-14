// ===== FUNC 14a1c size=30

void FUN_00014a1c(void)

{
  long *plVar1;
  long *plVar2;
  int iVar3;
  long lVar4;
  ulong unaff_RBX;
  ulong uVar5;
  long lVar6;
  long unaff_RBP;
  code *unaff_R13;
  
  FUN_000d36e0();
  FUN_000410a0();
                    /* try { // try from 00014a2c to 00014a30 has its CatchHandler @ 00014a4f */
  FUN_00041110();
  lVar4 = *(long *)(unaff_RBP + 8);
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
      lVar4 = *(long *)(unaff_RBP + 8);
    }
  }
  if (lVar4 != 0) {
    thunk_FUN_000d36e0();
  }
  lVar4 = *(long *)(unaff_RBP + 0x18);
  if (lVar4 != 0) {
    if (*(long *)(unaff_RBP + 0x10) != 0) {
      uVar5 = 0;
      do {
        plVar2 = *(long **)(lVar4 + uVar5 * 8);
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
            if (*(code **)(*plVar2 + 8) == FUN_00042ef0) {
              FUN_00042ee0();
              FUN_000d36e0(plVar2);
            }
            else {
              (**(code **)(*plVar2 + 8))(plVar2);
            }
          }
          lVar4 = *(long *)(unaff_RBP + 0x18);
        }
        uVar5 = uVar5 + 1;
      } while (uVar5 < *(ulong *)(unaff_RBP + 0x10));
      if (lVar4 == 0) goto LAB_00043622;
    }
    thunk_FUN_000d36e0();
  }
LAB_00043622:
  lVar4 = *(long *)(unaff_RBP + 0x20);
  lVar6 = 0;
  if (lVar4 != 0) {
    do {
      if (*(long *)(lVar4 + lVar6) != 0) {
        thunk_FUN_000d36e0();
        lVar4 = *(long *)(unaff_RBP + 0x20);
      }
      lVar6 = lVar6 + 8;
    } while (lVar6 != 0x60);
    if (lVar4 != 0) {
      thunk_FUN_000d36e0(lVar4);
      return;
    }
  }
  return;
}


