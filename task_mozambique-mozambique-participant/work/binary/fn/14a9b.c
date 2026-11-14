// ===== FUNC 14a9b size=92

void FUN_00014a9b(void)

{
  long *plVar1;
  long *plVar2;
  int iVar3;
  long lVar4;
  long unaff_RBX;
  undefined8 *unaff_RBP;
  ulong uVar5;
  long unaff_R12;
  char *unaff_R13;
  long *unaff_R14;
  undefined8 unaff_retaddr;
  undefined8 param_7;
  
  FUN_000d36e0();
  FUN_000410a0(param_7);
                    /* try { // try from 00014aad to 00014ab1 has its CatchHandler @ 00014aed */
  FUN_00041110();
  *unaff_RBP = unaff_retaddr;
  plVar2 = (long *)*unaff_R14;
  if (*unaff_R13 == '\0') {
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
                    /* try { // try from 00043d44 to 00043d48 has its CatchHandler @ 00043eaf */
      FUN_00042ee0();
      FUN_000d36e0(plVar2);
    }
    else {
      (**(code **)(*plVar2 + 8))(plVar2);
    }
  }
  lVar4 = *(long *)(unaff_RBX + 0x10);
  *unaff_R14 = unaff_R12;
  if (lVar4 != 0) {
    lVar4 = *(long *)(unaff_RBX + 0x18);
    uVar5 = 0;
    do {
      plVar2 = *(long **)(lVar4 + uVar5 * 8);
      if (plVar2 != (long *)0x0) {
        if (*unaff_R13 == '\0') {
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
        lVar4 = *(long *)(unaff_RBX + 0x18);
        *(undefined8 *)(lVar4 + uVar5 * 8) = 0;
      }
      uVar5 = uVar5 + 1;
    } while (uVar5 < *(ulong *)(unaff_RBX + 0x10));
  }
  return;
}


