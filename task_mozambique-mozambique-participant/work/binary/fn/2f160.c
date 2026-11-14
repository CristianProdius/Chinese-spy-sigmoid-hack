// ===== FUNC 2f160 size=688

void FUN_0002f160(undefined *param_1,undefined *param_2)

{
  undefined uVar1;
  long *plVar2;
  undefined8 uVar3;
  long lVar4;
  undefined (*pauVar5) [16];
  void *__dest;
  size_t __n;
  long lVar6;
  ulong uVar7;
  long lVar8;
  long lVar9;
  size_t sVar10;
  long in_FS_OFFSET;
  undefined local_59;
  undefined *local_58;
  undefined (*local_50) [16];
  long local_40;
  
  local_40 = *(long *)(in_FS_OFFSET + 0x28);
  uVar1 = *param_2;
  *(undefined8 *)(param_1 + 8) = 0;
  *param_1 = uVar1;
  switch(uVar1) {
  case 1:
    lVar9 = *(long *)(param_2 + 8);
                    /* try { // try from 0002f281 to 0002f285 has its CatchHandler @ 0002f498 */
    pauVar5 = (undefined (*) [16])FUN_00041fe0(0x30);
    *(undefined8 *)pauVar5[1] = 0;
    lVar4 = *(long *)(lVar9 + 0x10);
    *(undefined4 *)(*pauVar5 + 8) = 0;
    *(undefined **)(pauVar5[1] + 8) = *pauVar5 + 8;
    *(undefined **)pauVar5[2] = *pauVar5 + 8;
    *(undefined8 *)(pauVar5[2] + 8) = 0;
    if (lVar4 != 0) {
                    /* try { // try from 0002f2ba to 0002f2be has its CatchHandler @ 0002f493 */
      lVar8 = FUN_0002fb70();
      lVar4 = lVar8;
      do {
        lVar6 = lVar4;
        lVar4 = *(long *)(lVar6 + 0x10);
      } while (lVar4 != 0);
      *(long *)(pauVar5[1] + 8) = lVar6;
      lVar4 = lVar8;
      do {
        lVar6 = lVar4;
        lVar4 = *(long *)(lVar6 + 0x18);
      } while (lVar4 != 0);
      uVar3 = *(undefined8 *)(lVar9 + 0x28);
      *(long *)pauVar5[2] = lVar6;
      *(long *)pauVar5[1] = lVar8;
      *(undefined8 *)(pauVar5[2] + 8) = uVar3;
    }
    goto LAB_0002f22e;
  case 2:
    plVar2 = *(long **)(param_2 + 8);
                    /* try { // try from 0002f311 to 0002f315 has its CatchHandler @ 0002f498 */
    pauVar5 = (undefined (*) [16])FUN_00041fe0(0x18);
    uVar7 = plVar2[1] - *plVar2;
    *(undefined8 *)pauVar5[1] = 0;
    *pauVar5 = (undefined  [16])0x0;
    if (uVar7 == 0) {
LAB_0002f408:
      lVar9 = 0;
    }
    else {
      if (0x7ffffffffffffff0 < uVar7) {
                    /* try { // try from 0002f3fc to 0002f400 has its CatchHandler @ 0002f441 */
        FUN_00015c88();
        goto LAB_0002f408;
      }
                    /* try { // try from 0002f34b to 0002f34f has its CatchHandler @ 0002f441 */
      lVar9 = FUN_00041fe0(uVar7);
    }
    *(ulong *)pauVar5[1] = uVar7 + lVar9;
    *(long *)*pauVar5 = lVar9;
    *(long *)(*pauVar5 + 8) = lVar9;
    lVar4 = plVar2[1];
    for (lVar8 = *plVar2; lVar4 != lVar8; lVar8 = lVar8 + 0x10) {
                    /* try { // try from 0002f386 to 0002f38a has its CatchHandler @ 0002f446 */
      FUN_0002f160(lVar9,lVar8);
      lVar9 = lVar9 + 0x10;
    }
    *(long *)(*pauVar5 + 8) = lVar9;
    *(undefined (**) [16])(param_1 + 8) = pauVar5;
    break;
  case 3:
    plVar2 = *(long **)(param_2 + 8);
                    /* try { // try from 0002f3b1 to 0002f3b5 has its CatchHandler @ 0002f498 */
    pauVar5 = (undefined (*) [16])FUN_00041fe0(0x20);
    local_58 = &local_59;
    lVar9 = plVar2[1];
    *(undefined (**) [16])*pauVar5 = pauVar5 + 1;
    lVar4 = *plVar2;
    local_50 = pauVar5;
                    /* try { // try from 0002f3df to 0002f3e3 has its CatchHandler @ 0002f49d */
    FUN_00017e00(pauVar5,lVar4,lVar9 + lVar4);
    goto LAB_0002f22e;
  case 4:
    param_1[8] = param_2[8];
    break;
  case 5:
  case 6:
    *(undefined8 *)(param_1 + 8) = *(undefined8 *)(param_2 + 8);
    break;
  case 7:
    *(undefined8 *)(param_1 + 8) = *(undefined8 *)(param_2 + 8);
    break;
  case 8:
    plVar2 = *(long **)(param_2 + 8);
                    /* try { // try from 0002f1b9 to 0002f1bd has its CatchHandler @ 0002f498 */
    pauVar5 = (undefined (*) [16])FUN_00041fe0(0x28);
    lVar9 = plVar2[1] - *plVar2;
    *(undefined8 *)pauVar5[1] = 0;
    *pauVar5 = (undefined  [16])0x0;
    if (lVar9 == 0) {
      __dest = (void *)0x0;
    }
    else {
      if (lVar9 < 0) {
                    /* try { // try from 0002f437 to 0002f43b has its CatchHandler @ 0002f48e */
        FUN_00015c55();
        goto LAB_0002f43c;
      }
                    /* try { // try from 0002f1e7 to 0002f1eb has its CatchHandler @ 0002f48e */
      __dest = (void *)FUN_00041fe0(lVar9);
    }
    *(long *)pauVar5[1] = lVar9 + (long)__dest;
    *(void **)*pauVar5 = __dest;
    *(void **)(*pauVar5 + 8) = __dest;
    __n = plVar2[1] - *plVar2;
    sVar10 = 0;
    if (__n != 0) {
      __dest = memmove(__dest,(void *)*plVar2,__n);
      sVar10 = __n;
    }
    lVar9 = plVar2[3];
    *(size_t *)(*pauVar5 + 8) = (long)__dest + sVar10;
    *(long *)(pauVar5[1] + 8) = lVar9;
    pauVar5[2][0] = *(undefined *)(plVar2 + 4);
LAB_0002f22e:
    *(undefined (**) [16])(param_1 + 8) = pauVar5;
  }
  if (local_40 == *(long *)(in_FS_OFFSET + 0x28)) {
    return;
  }
LAB_0002f43c:
                    /* WARNING: Subroutine does not return */
  __stack_chk_fail();
}


