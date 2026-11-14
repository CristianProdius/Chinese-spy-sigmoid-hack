// ===== FUNC 22090 size=971

undefined8
FUN_00022090(long param_1,int *param_2,long param_3,long param_4,undefined4 param_5,long param_6,
            long param_7)

{
  int *piVar1;
  long lVar2;
  undefined8 *puVar3;
  int iVar4;
  int iVar5;
  undefined8 uVar6;
  long lVar7;
  long lVar8;
  long in_FS_OFFSET;
  int local_58 [2];
  undefined auStack_50 [16];
  long local_40;
  
  local_40 = *(long *)(in_FS_OFFSET + 0x28);
  iVar4 = FUN_000b31e0(param_6,&DAT_000e0454);
  if (iVar4 != 0) {
    iVar4 = FUN_000b31e0(param_6,"build_boat");
    if (iVar4 == 0) {
      puVar3 = *(undefined8 **)(param_2 + 6);
      local_58[1] = 0xffffffff;
      uVar6 = *(undefined8 *)(param_2 + (long)*param_2 * 3 + 10);
      *(ulong *)(param_2 + (long)*param_2 * 3 + 10) =
           CONCAT44((int)((ulong)uVar6 >> 0x20) + (int)((ulong)DAT_000e2e20 >> 0x20),
                    (int)uVar6 + (int)DAT_000e2e20);
      local_58[0] = *param_2;
      auStack_50 = (undefined  [16])0x0;
      if (puVar3 == *(undefined8 **)(param_2 + 8)) {
        FUN_00021ef0(param_2 + 4,puVar3,local_58);
      }
      else {
        *puVar3 = CONCAT44(0xffffffff,local_58[0]);
        puVar3[1] = 0;
        puVar3[2] = 0;
        *(undefined8 **)(param_2 + 6) = puVar3 + 3;
      }
    }
    else {
      if ((ulong)((*(long *)(param_2 + 6) - *(long *)(param_2 + 4) >> 3) * -0x5555555555555555) <=
          (ulong)(long)*(int *)(param_6 + 0x20)) {
                    /* WARNING: Subroutine does not return */
        FUN_0008c960("vector::_M_range_check: __n (which is %zu) >= this->size() (which is %zu)");
      }
      piVar1 = (int *)(*(long *)(param_2 + 4) + (long)*(int *)(param_6 + 0x20) * 0x18);
      iVar4 = *piVar1;
      iVar5 = FUN_000b31e0(param_6,&DAT_000e0459);
      if (iVar5 == 0) {
        lVar8 = (long)iVar4;
        iVar4 = *(int *)(param_6 + 0x24);
        lVar7 = (long)iVar4;
        lVar2 = param_7 + lVar8 * 10;
        if (*(char *)(lVar2 + lVar7) != '\0') {
LAB_000221e4:
          uVar6 = 0;
          goto LAB_000220df;
        }
        *(undefined *)(param_7 + lVar7 * 10 + lVar8) = 1;
        *(undefined *)(lVar2 + lVar7) = 1;
        piVar1[1] = iVar4;
        piVar1[2] = *(int *)(param_1 + 0x34 + lVar8 * 0x28 + lVar7 * 4);
      }
      else {
        iVar5 = FUN_000b31e0(param_6,"gather");
        if (iVar5 == 0) {
          iVar5 = *(int *)(param_3 + (long)iVar4 * 4);
          if (iVar5 < *(int *)(param_6 + 0x2c)) goto LAB_000221e4;
          *(int *)(param_3 + (long)iVar4 * 4) = iVar5 - *(int *)(param_6 + 0x2c);
          piVar1[(long)*(int *)(param_6 + 0x28) + 3] =
               piVar1[(long)*(int *)(param_6 + 0x28) + 3] + *(int *)(param_6 + 0x2c);
        }
        else {
          iVar5 = FUN_000b31e0(param_6,"load");
          if (iVar5 == 0) {
            param_2[(long)iVar4 * 3 + (long)*(int *)(param_6 + 0x28) + 10] =
                 param_2[(long)iVar4 * 3 + (long)*(int *)(param_6 + 0x28) + 10] -
                 *(int *)(param_6 + 0x2c);
            piVar1[(long)*(int *)(param_6 + 0x28) + 3] =
                 piVar1[(long)*(int *)(param_6 + 0x28) + 3] + *(int *)(param_6 + 0x2c);
          }
          else {
            iVar5 = FUN_000b31e0(param_6,"unload");
            if (iVar5 == 0) {
              param_2[(long)iVar4 * 3 + (long)*(int *)(param_6 + 0x28) + 10] =
                   param_2[(long)iVar4 * 3 + (long)*(int *)(param_6 + 0x28) + 10] +
                   *(int *)(param_6 + 0x2c);
              piVar1[(long)*(int *)(param_6 + 0x28) + 3] =
                   piVar1[(long)*(int *)(param_6 + 0x28) + 3] - *(int *)(param_6 + 0x2c);
            }
            else {
              iVar5 = FUN_000b31e0(param_6,"build_workshop");
              if (iVar5 == 0) {
                uVar6 = *(undefined8 *)(param_2 + (long)iVar4 * 3 + 10);
                *(ulong *)(param_2 + (long)iVar4 * 3 + 10) =
                     CONCAT44((int)((ulong)uVar6 >> 0x20) + (int)((ulong)DAT_000e2e28 >> 0x20),
                              (int)uVar6 + (int)DAT_000e2e28);
                *(undefined *)((long)param_2 + (long)iVar4 + 0xa0) = 1;
              }
              else {
                iVar5 = FUN_000b31e0(param_6,"craft");
                if (iVar5 == 0) {
                  uVar6 = *(undefined8 *)(param_2 + (long)iVar4 * 3 + 10);
                  *(ulong *)(param_2 + (long)iVar4 * 3 + 10) =
                       CONCAT44((int)((ulong)uVar6 >> 0x20) + (int)((ulong)DAT_000e2e28 >> 0x20),
                                (int)uVar6 + (int)DAT_000e2e28);
                  param_2[(long)iVar4 + 0x2b] = 3;
                }
                else {
                  iVar4 = FUN_000b31e0(param_6,"deliver");
                  if (iVar4 != 0) {
                    uVar6 = FUN_00040f40(0x10);
                    /* try { // try from 00022468 to 0002246c has its CatchHandler @ 00022483 */
                    FUN_00053220(uVar6,"unknown order");
                    /* WARNING: Subroutine does not return */
                    FUN_00041f00(uVar6,&PTR_PTR_FUN_0011d470,FUN_00049930);
                  }
                  if (*(int *)(param_4 + (long)*(int *)(param_6 + 0x30) * 4) != -1)
                  goto LAB_000221e4;
                  param_1 = param_1 + (long)*(int *)(param_6 + 0x30) * 0x14;
                  piVar1[(long)*(int *)(param_1 + 0x4e4) + 3] =
                       piVar1[(long)*(int *)(param_1 + 0x4e4) + 3] - *(int *)(param_1 + 0x4e8);
                  *(ulong *)(param_2 + 1) =
                       CONCAT44((uint)(*(int *)(param_1 + 0x4e4) == 2) +
                                (int)((ulong)*(undefined8 *)(param_2 + 1) >> 0x20),
                                *(int *)(param_1 + 0x4f0) + (int)*(undefined8 *)(param_2 + 1));
                  *(undefined4 *)(param_4 + (long)*(int *)(param_6 + 0x30) * 4) = param_5;
                }
              }
            }
          }
        }
      }
    }
  }
  uVar6 = 1;
LAB_000220df:
  if (local_40 == *(long *)(in_FS_OFFSET + 0x28)) {
    return uVar6;
  }
                    /* WARNING: Subroutine does not return */
  __stack_chk_fail();
}


