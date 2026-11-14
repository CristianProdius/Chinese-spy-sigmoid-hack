// ===== FUNC 17f10 size=211

void FUN_00017f10(char *param_1,undefined8 *param_2,long param_3)

{
  long lVar1;
  long *plVar2;
  undefined8 *puVar3;
  long lVar4;
  char cVar5;
  int iVar6;
  undefined8 uVar7;
  long lVar8;
  long lVar9;
  
  if ((*param_1 != '\x01') || (param_3 != *(long *)(*(long *)(param_1 + 8) + 0x28))) {
    uVar7 = FUN_00040f40(0x10);
    FUN_00053220(uVar7,"unexpected fields");
                    /* WARNING: Subroutine does not return */
    FUN_00041f00(uVar7,&PTR_PTR_FUN_0011d470,FUN_00049930);
  }
  puVar3 = param_2 + param_3;
  if (puVar3 == param_2) {
    return;
  }
  cVar5 = '\x01';
  while (uVar7 = *param_2, cVar5 == '\x01') {
    lVar4 = *(long *)(*(long *)(param_1 + 8) + 0x10);
    lVar1 = *(long *)(param_1 + 8) + 8;
    lVar8 = lVar1;
    if (lVar4 == 0) {
      FUN_00013844();
      return;
    }
    do {
      while( true ) {
        lVar9 = lVar4;
        iVar6 = FUN_000b31e0(lVar9 + 0x20,uVar7);
        plVar2 = (long *)(lVar9 + 0x18);
        if (-1 < iVar6) break;
        lVar4 = *plVar2;
        lVar9 = lVar8;
        if (*plVar2 == 0) goto LAB_00017fab;
      }
      lVar4 = *(long *)(lVar9 + 0x10);
      lVar8 = lVar9;
    } while (*(long *)(lVar9 + 0x10) != 0);
LAB_00017fab:
    if ((lVar1 == lVar9) || (iVar6 = FUN_000b31e0(lVar9 + 0x20,uVar7), 0 < iVar6)) break;
    param_2 = param_2 + 1;
    if (puVar3 == param_2) {
      return;
    }
    cVar5 = *param_1;
  }
  uVar7 = FUN_00040f40(0x10);
  FUN_00053220(uVar7,"missing field");
                    /* WARNING: Subroutine does not return */
  FUN_00041f00(uVar7,&PTR_PTR_FUN_0011d470,FUN_00049930);
}


