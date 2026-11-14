// ===== FUNC 3d7b0 size=267

undefined * FUN_0003d7b0(int *param_1,int *param_2,undefined *param_3)

{
  int iVar1;
  undefined (*pauVar2) [16];
  undefined *puVar3;
  undefined *puVar4;
  int *piVar5;
  long in_FS_OFFSET;
  undefined local_59;
  undefined *local_58;
  undefined (*local_50) [16];
  long local_40;
  
  local_40 = *(long *)(in_FS_OFFSET + 0x28);
  if (param_1 != param_2) {
    do {
      *param_3 = 0;
      *(undefined8 *)(param_3 + 8) = 0;
                    /* try { // try from 0003d804 to 0003d81f has its CatchHandler @ 0003d8c0 */
      FUN_00024620(param_3 + 8,0);
      *param_3 = 2;
      piVar5 = param_1 + 3;
      pauVar2 = (undefined (*) [16])FUN_00041fe0(0x18);
      *(undefined8 *)pauVar2[1] = 0;
      *pauVar2 = (undefined  [16])0x0;
      local_58 = &local_59;
      local_50 = pauVar2;
                    /* try { // try from 0003d848 to 0003d84c has its CatchHandler @ 0003d8bb */
      puVar3 = (undefined *)FUN_00041fe0(0x30);
      *(undefined **)*pauVar2 = puVar3;
      *(undefined **)pauVar2[1] = puVar3 + 0x30;
      puVar4 = puVar3;
      do {
        iVar1 = *param_1;
        param_1 = param_1 + 1;
        *puVar4 = 5;
        *(long *)(puVar4 + 8) = (long)iVar1;
        puVar4 = puVar4 + 0x10;
      } while (piVar5 != param_1);
      *(undefined (**) [16])(param_3 + 8) = pauVar2;
      param_3 = param_3 + 0x10;
      *(undefined **)(*pauVar2 + 8) = puVar3 + 0x30;
      param_1 = piVar5;
    } while (param_2 != piVar5);
  }
  if (local_40 != *(long *)(in_FS_OFFSET + 0x28)) {
                    /* WARNING: Subroutine does not return */
    __stack_chk_fail();
  }
  return param_3;
}


