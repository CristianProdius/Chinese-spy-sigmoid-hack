// ===== FUNC 2b090 size=629

undefined  [16] FUN_0002b090(long *param_1,undefined *param_2,char param_3)

{
  ulong *puVar1;
  undefined uVar2;
  char *pcVar3;
  undefined *puVar4;
  undefined uVar5;
  byte bVar6;
  char cVar7;
  ulong uVar8;
  undefined8 uVar9;
  long lVar10;
  long lVar11;
  int iVar12;
  long in_FS_OFFSET;
  undefined auVar13 [16];
  undefined local_59;
  undefined local_58;
  undefined7 uStack_57;
  undefined8 uStack_50;
  undefined8 local_48;
  undefined8 auStack_40 [2];
  long local_30;
  
  local_30 = *(long *)(in_FS_OFFSET + 0x28);
  lVar10 = (ulong)*(uint *)(param_1 + 7) - 1;
  lVar11 = (ulong)*(uint *)(param_1 + 7) + 0x3e;
  if (-1 < lVar10) {
    lVar11 = lVar10;
  }
  puVar1 = (ulong *)(param_1[6] + (lVar11 >> 6) * 8);
  if (lVar10 % 0x40 == -1) {
    uVar8 = puVar1[-1] & 0x8000000000000000;
  }
  else {
    uVar8 = 1L << ((byte)(lVar10 % 0x40) & 0x3f) & *puVar1;
  }
  if (uVar8 == 0) {
    uVar8 = 0;
    lVar11 = 0;
    goto LAB_0002b0f5;
  }
  local_58 = *param_2;
  FUN_000210f0(&uStack_50);
  if (param_3 == '\0') {
    local_59 = 5;
    local_48 = CONCAT44(local_48._4_4_,(int)(param_1[2] - param_1[1] >> 3));
    if (param_1[0x12] == 0) {
                    /* try { // try from 0002b30b to 0002b30f has its CatchHandler @ 0002b310 */
      uVar9 = FUN_00016056();
                    /* catch() { ... } // from try @ 0002b1f7 with catch @ 0002b310
                       catch() { ... } // from try @ 0002b30b with catch @ 0002b310 */
      FUN_00024620(&uStack_50,local_58);
                    /* WARNING: Subroutine does not return */
      FUN_000ddde0(uVar9);
    }
                    /* try { // try from 0002b1f7 to 0002b21b has its CatchHandler @ 0002b310 */
    cVar7 = (*(code *)param_1[0x13])(param_1 + 0x10,&local_48,&local_59,&local_58);
    if (cVar7 != '\0') goto LAB_0002b152;
LAB_0002b1a2:
    bVar6 = 0;
    lVar11 = 0;
  }
  else {
LAB_0002b152:
    uVar9 = uStack_50;
    uVar5 = local_58;
    if (param_1[2] == param_1[1]) {
      puVar4 = (undefined *)*param_1;
      local_58 = 0;
      uStack_50 = 0;
      uVar2 = *puVar4;
      *puVar4 = uVar5;
      auStack_40[0] = *(undefined8 *)(puVar4 + 8);
      local_48 = CONCAT71(uStack_57,uVar2);
      *(undefined8 *)(puVar4 + 8) = uVar9;
      FUN_00024620(auStack_40);
      lVar11 = *param_1;
      bVar6 = 1;
    }
    else {
      pcVar3 = *(char **)(param_1[2] + -8);
      if (pcVar3 == (char *)0x0) goto LAB_0002b1a2;
      if (*pcVar3 == '\x02') {
        FUN_000182f0(*(undefined8 *)(pcVar3 + 8),&local_58);
        bVar6 = 1;
        lVar11 = *(long *)(*(long *)(*(long *)(param_1[2] + -8) + 8) + 8) + -0x10;
      }
      else {
        lVar11 = param_1[0xb];
        iVar12 = *(int *)(param_1 + 0xc);
        auVar13 = FUN_00017eb0(lVar11,iVar12);
        uVar9 = uStack_50;
        uVar5 = local_58;
        uVar8 = *auVar13._0_8_;
        if (iVar12 == 0) {
          *(undefined4 *)(param_1 + 0xc) = 0x3f;
          param_1[0xb] = lVar11 + -8;
        }
        else {
          *(int *)(param_1 + 0xc) = iVar12 + -1;
        }
        if ((auVar13._8_8_ & uVar8) == 0) goto LAB_0002b1a2;
        puVar4 = (undefined *)param_1[0xe];
        local_58 = 0;
        uStack_50 = 0;
        uVar2 = *puVar4;
        *puVar4 = uVar5;
        auStack_40[0] = *(undefined8 *)(puVar4 + 8);
        local_48 = CONCAT71(uStack_57,uVar2);
        *(undefined8 *)(puVar4 + 8) = uVar9;
        FUN_00024620(auStack_40);
        lVar11 = param_1[0xe];
        bVar6 = 1;
      }
    }
  }
  uVar8 = (ulong)bVar6;
  FUN_00024620(&uStack_50,local_58);
LAB_0002b0f5:
  if (local_30 == *(long *)(in_FS_OFFSET + 0x28)) {
    auVar13._8_8_ = lVar11;
    auVar13._0_8_ = uVar8;
    return auVar13;
  }
                    /* WARNING: Subroutine does not return */
  __stack_chk_fail();
}


