// ===== FUNC 40d40 size=223

void FUN_00040d40(long param_1)

{
  long *plVar1;
  long *plVar2;
  long *plVar3;
  long lVar4;
  int iVar5;
  long *plVar6;
  long *plVar7;
  long *plVar8;
  long lVar9;
  
  iVar5 = pthread_mutex_lock((pthread_mutex_t *)&DAT_001231a0);
  if (iVar5 == 0) {
    lVar9 = *(long *)(param_1 + -0x10);
    plVar1 = (long *)(param_1 + -0x10);
    if ((DAT_001231c8 == (long *)0x0) ||
       (plVar3 = (long *)((long)plVar1 + lVar9), plVar3 < DAT_001231c8)) {
      *(long **)(param_1 + -8) = DAT_001231c8;
      DAT_001231c8 = plVar1;
    }
    else {
      plVar7 = (long *)DAT_001231c8[1];
      if (DAT_001231c8 == plVar3) {
        lVar4 = *DAT_001231c8;
        *(long **)(param_1 + -8) = plVar7;
        *(long *)(param_1 + -0x10) = lVar9 + lVar4;
        DAT_001231c8 = plVar1;
      }
      else {
        plVar8 = (long *)&DAT_001231c8;
        plVar6 = DAT_001231c8;
        if (plVar7 != (long *)0x0) {
          do {
            if (plVar7 <= plVar3) {
              if (plVar3 == plVar7) {
                lVar9 = lVar9 + *plVar3;
                plVar6[1] = plVar3[1];
              }
              break;
            }
            plVar2 = plVar7 + 1;
            plVar8 = plVar6 + 1;
            plVar6 = plVar7;
            plVar7 = (long *)*plVar2;
          } while ((long *)*plVar2 != (long *)0x0);
          plVar6 = (long *)*plVar8;
        }
        if (plVar1 == (long *)((long)plVar6 + *plVar6)) {
          *plVar6 = *plVar6 + lVar9;
        }
        else {
          lVar4 = plVar6[1];
          *(long *)(param_1 + -0x10) = lVar9;
          *(long *)(param_1 + -8) = lVar4;
          *(long **)(*plVar8 + 8) = plVar1;
        }
      }
    }
    iVar5 = pthread_mutex_unlock((pthread_mutex_t *)&DAT_001231a0);
    if (iVar5 == 0) {
      return;
    }
    FUN_000146a9();
  }
  FUN_00014676();
  FUN_00014676();
  FUN_000146a9();
                    /* WARNING: Subroutine does not return */
  abort();
}


