// ===== FUNC 32290 size=391

void FUN_00032290(undefined *param_1,int *param_2)

{
  int iVar1;
  undefined (*pauVar2) [16];
  undefined *puVar3;
  undefined (*pauVar4) [16];
  undefined *puVar5;
  undefined *puVar6;
  undefined *puVar7;
  int *piVar8;
  int *piVar9;
  long in_FS_OFFSET;
  undefined local_59;
  undefined *local_58;
  undefined (*local_50) [16];
  long local_40;
  
  local_40 = *(long *)(in_FS_OFFSET + 0x28);
  *param_1 = 0;
  *(undefined8 *)(param_1 + 8) = 0;
                    /* try { // try from 000322cd to 000322ee has its CatchHandler @ 0003245f */
  FUN_00024620(param_1 + 8,0);
  *param_1 = 2;
  pauVar2 = (undefined (*) [16])FUN_00041fe0(0x18);
  *(undefined8 *)pauVar2[1] = 0;
  *pauVar2 = (undefined  [16])0x0;
                    /* try { // try from 0003230b to 0003230f has its CatchHandler @ 0003245a */
  puVar3 = (undefined *)FUN_00041fe0(0xa0);
  *(undefined **)*pauVar2 = puVar3;
  *(undefined **)pauVar2[1] = puVar3 + 0xa0;
  if (param_2 + 100 != param_2) {
    piVar8 = param_2;
    do {
      *puVar3 = 0;
      *(undefined8 *)(puVar3 + 8) = 0;
                    /* try { // try from 00032351 to 0003236c has its CatchHandler @ 0003241c */
      FUN_00024620(puVar3 + 8,0);
      *puVar3 = 2;
      piVar9 = piVar8 + 10;
      pauVar4 = (undefined (*) [16])FUN_00041fe0(0x18);
      *(undefined8 *)pauVar4[1] = 0;
      *pauVar4 = (undefined  [16])0x0;
      local_58 = &local_59;
      local_50 = pauVar4;
                    /* try { // try from 00032394 to 00032398 has its CatchHandler @ 00032417 */
      puVar5 = (undefined *)FUN_00041fe0(0xa0);
      *(undefined **)*pauVar4 = puVar5;
      *(undefined **)pauVar4[1] = puVar5 + 0xa0;
      puVar6 = puVar5;
      do {
        iVar1 = *piVar8;
        *puVar6 = 5;
        puVar7 = puVar6 + 0x10;
        piVar8 = piVar8 + 1;
        *(long *)(puVar6 + 8) = (long)iVar1;
        puVar6 = puVar7;
      } while (puVar7 != puVar5 + 0xa0);
      *(undefined (**) [16])(puVar3 + 8) = pauVar4;
      puVar3 = puVar3 + 0x10;
      *(undefined **)(*pauVar4 + 8) = puVar7;
      piVar8 = piVar9;
    } while (param_2 + 100 != piVar9);
  }
  *(undefined **)(*pauVar2 + 8) = puVar3;
  *(undefined (**) [16])(param_1 + 8) = pauVar2;
  if (local_40 != *(long *)(in_FS_OFFSET + 0x28)) {
                    /* WARNING: Subroutine does not return */
    __stack_chk_fail();
  }
  return;
}


