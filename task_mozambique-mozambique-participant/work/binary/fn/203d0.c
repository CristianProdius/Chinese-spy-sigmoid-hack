// ===== FUNC 203d0 size=740

void FUN_000203d0(long *param_1,undefined8 *param_2)

{
  long *plVar1;
  ulong uVar2;
  undefined *__src;
  long lVar3;
  void *__src_00;
  long lVar4;
  long *plVar5;
  size_t __n;
  long lVar6;
  long lVar7;
  ulong uVar8;
  long *__dest;
  long in_FS_OFFSET;
  ulong local_48;
  long local_40;
  
  plVar5 = (long *)param_1[9];
  plVar1 = (long *)param_1[5];
  local_40 = *(long *)(in_FS_OFFSET + 0x28);
  lVar7 = (long)plVar5 - (long)plVar1;
  if ((param_1[6] - param_1[7] >> 3) * 0x6db6db6db6db6db7 +
      ((lVar7 >> 3) + -1 + (ulong)(plVar5 == (long *)0x0)) * 9 +
      (param_1[4] - param_1[2] >> 3) * 0x6db6db6db6db6db7 == 0x249249249249249) {
LAB_000206c0:
                    /* WARNING: Subroutine does not return */
    FUN_00015e26("cannot create std::deque larger than max_size()");
  }
  uVar2 = param_1[1];
  if (uVar2 - ((long)plVar5 - *param_1 >> 3) < 2) {
    lVar3 = (lVar7 >> 3) + 2;
    if ((ulong)(lVar3 * 2) < uVar2) {
      plVar5 = plVar5 + 1;
      __dest = (long *)(*param_1 + (uVar2 - lVar3 >> 1) * 8);
      __n = (long)plVar5 - (long)plVar1;
      if (__dest < plVar1) {
        if (plVar5 != plVar1) {
          memmove(__dest,plVar1,__n);
        }
      }
      else if (plVar5 != plVar1) {
        memmove((void *)(((lVar7 + 8) - __n) + (long)__dest),plVar1,__n);
      }
    }
    else {
      if (uVar2 == 0) {
        lVar6 = 0x18;
        uVar8 = 3;
      }
      else {
        uVar8 = (uVar2 + 1) * 2;
        if (uVar8 >> 0x3c != 0) {
          if (uVar8 >> 0x3d != 0) {
            FUN_00015c88();
          }
          FUN_00015c55();
          goto LAB_000206c0;
        }
        lVar6 = (uVar2 + 1) * 0x10;
      }
      lVar6 = FUN_00041fe0(lVar6);
      __src_00 = (void *)param_1[5];
      __dest = (long *)(lVar6 + (uVar8 - lVar3 >> 1) * 8);
      if ((void *)(param_1[9] + 8) != __src_00) {
        memmove(__dest,__src_00,(param_1[9] + 8) - (long)__src_00);
      }
      thunk_FUN_000d36e0(*param_1,param_1[1] * 8);
      *param_1 = lVar6;
      param_1[1] = uVar8;
    }
    lVar3 = *__dest;
    plVar5 = (long *)((long)__dest + lVar7);
    param_1[5] = (long)__dest;
    param_1[9] = (long)plVar5;
    param_1[3] = lVar3;
    param_1[4] = lVar3 + 0x1f8;
    lVar7 = *plVar5;
    param_1[7] = lVar7;
    param_1[8] = lVar7 + 0x1f8;
  }
  lVar7 = FUN_00041fe0(0x1f8);
  plVar5[1] = lVar7;
  plVar1 = (long *)param_1[6];
  uVar2 = param_2[1];
  plVar5 = plVar1 + 2;
  *plVar1 = (long)plVar5;
  __src = (undefined *)*param_2;
  local_48 = uVar2;
  if (uVar2 < 0x10) {
    if (uVar2 == 1) {
      *(undefined *)(plVar1 + 2) = *__src;
      goto LAB_000204bc;
    }
    if (uVar2 == 0) goto LAB_000204bc;
  }
  else {
                    /* try { // try from 00020618 to 0002061c has its CatchHandler @ 000206d1 */
    plVar5 = (long *)FUN_000b0760(plVar1,&local_48,0);
    *plVar1 = (long)plVar5;
    plVar1[2] = local_48;
  }
  memcpy(plVar5,__src,uVar2);
  plVar5 = (long *)*plVar1;
LAB_000204bc:
  plVar1[1] = local_48;
  *(undefined *)((long)plVar5 + local_48) = 0;
  lVar7 = param_1[9];
  lVar6 = param_2[4];
  lVar4 = param_2[5];
  *(undefined4 *)(plVar1 + 6) = *(undefined4 *)(param_2 + 6);
  lVar3 = *(long *)(lVar7 + 8);
  plVar1[4] = lVar6;
  plVar1[5] = lVar4;
  param_1[6] = lVar3;
  param_1[7] = lVar3;
  param_1[8] = lVar3 + 0x1f8;
  param_1[9] = lVar7 + 8;
  if (local_40 == *(long *)(in_FS_OFFSET + 0x28)) {
    return;
  }
                    /* WARNING: Subroutine does not return */
  __stack_chk_fail();
}


