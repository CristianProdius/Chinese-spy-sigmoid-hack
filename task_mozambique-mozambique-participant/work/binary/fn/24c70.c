// ===== FUNC 24c70 size=565

void FUN_00024c70(undefined8 *param_1,byte *param_2,char param_3)

{
  ulong *puVar1;
  undefined uVar2;
  char *pcVar3;
  undefined *puVar4;
  ulong uVar5;
  ulong uVar6;
  char cVar7;
  long lVar8;
  ulong uVar9;
  undefined8 uVar10;
  long lVar11;
  int iVar12;
  long in_FS_OFFSET;
  undefined auVar13 [16];
  undefined local_39;
  ulong local_38;
  ulong uStack_30;
  undefined8 local_28;
  undefined8 auStack_20 [2];
  long local_10;
  
  local_10 = *(long *)(in_FS_OFFSET + 0x28);
  lVar11 = (ulong)*(uint *)(param_1 + 7) - 1;
  lVar8 = (ulong)*(uint *)(param_1 + 7) + 0x3e;
  if (-1 < lVar11) {
    lVar8 = lVar11;
  }
  puVar1 = (ulong *)(param_1[6] + (lVar8 >> 6) * 8);
  if (lVar11 % 0x40 == -1) {
    uVar9 = puVar1[-1] & 0x8000000000000000;
  }
  else {
    uVar9 = 1L << ((byte)(lVar11 % 0x40) & 0x3f) & *puVar1;
  }
  if (uVar9 == 0) goto LAB_00024cca;
  local_38 = 4;
  uStack_30 = (ulong)*param_2;
  if (param_3 == '\0') {
    local_39 = 5;
    local_28 = CONCAT44(local_28._4_4_,(int)((long)(param_1[2] - param_1[1]) >> 3));
    if (param_1[0x12] == 0) {
                    /* try { // try from 00024e99 to 00024e9d has its CatchHandler @ 00024e9e */
      uVar10 = FUN_00016056();
                    /* catch() { ... } // from try @ 00024dbc with catch @ 00024e9e
                       catch() { ... } // from try @ 00024e99 with catch @ 00024e9e */
      FUN_00024620(&uStack_30,local_38 & 0xff);
                    /* WARNING: Subroutine does not return */
      FUN_000ddde0(uVar10);
    }
                    /* try { // try from 00024dbc to 00024ddd has its CatchHandler @ 00024e9e */
    cVar7 = (*(code *)param_1[0x13])(param_1 + 0x10,&local_28,&local_39,&local_38);
    if (cVar7 != '\0') goto LAB_00024d20;
  }
  else {
LAB_00024d20:
    uVar5 = uStack_30;
    uVar9 = local_38;
    if (param_1[2] == param_1[1]) {
      puVar4 = (undefined *)*param_1;
      local_38 = local_38 & 0xffffffffffffff00;
      uStack_30 = 0;
      local_28._0_1_ = (undefined)uVar9;
      uVar2 = *puVar4;
      *puVar4 = (undefined)local_28;
      auStack_20[0] = *(undefined8 *)(puVar4 + 8);
      local_28._1_7_ = (undefined7)(uVar9 >> 8);
      local_28 = CONCAT71(local_28._1_7_,uVar2);
      *(ulong *)(puVar4 + 8) = uVar5;
      FUN_00024620(auStack_20);
    }
    else {
      pcVar3 = *(char **)(param_1[2] + -8);
      if (pcVar3 != (char *)0x0) {
        if (*pcVar3 == '\x02') {
          FUN_000182f0(*(undefined8 *)(pcVar3 + 8),&local_38);
        }
        else {
          lVar8 = param_1[0xb];
          iVar12 = *(int *)(param_1 + 0xc);
          auVar13 = FUN_00017eb0(lVar8,iVar12);
          uVar6 = uStack_30;
          uVar5 = local_38;
          uVar9 = *auVar13._0_8_;
          if (iVar12 == 0) {
            *(undefined4 *)(param_1 + 0xc) = 0x3f;
            param_1[0xb] = lVar8 + -8;
          }
          else {
            *(int *)(param_1 + 0xc) = iVar12 + -1;
          }
          if ((auVar13._8_8_ & uVar9) != 0) {
            puVar4 = (undefined *)param_1[0xe];
            local_38 = local_38 & 0xffffffffffffff00;
            uStack_30 = 0;
            local_28._0_1_ = (undefined)uVar5;
            uVar2 = *puVar4;
            *puVar4 = (undefined)local_28;
            auStack_20[0] = *(undefined8 *)(puVar4 + 8);
            local_28._1_7_ = (undefined7)(uVar5 >> 8);
            local_28 = CONCAT71(local_28._1_7_,uVar2);
            *(ulong *)(puVar4 + 8) = uVar6;
            FUN_00024620(auStack_20);
          }
        }
      }
    }
  }
  FUN_00024620(&uStack_30,local_38 & 0xff);
LAB_00024cca:
  if (local_10 == *(long *)(in_FS_OFFSET + 0x28)) {
    return;
  }
                    /* WARNING: Subroutine does not return */
  __stack_chk_fail();
}


