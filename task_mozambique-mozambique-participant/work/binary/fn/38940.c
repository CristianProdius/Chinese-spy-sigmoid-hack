// ===== FUNC 38940 size=652

undefined *
FUN_00038940(undefined *param_1,long *param_2,undefined (*param_3) [16],undefined param_4,
            undefined param_5)

{
  undefined auVar1 [16];
  undefined auVar2 [16];
  lconv *plVar3;
  long in_FS_OFFSET;
  undefined local_148 [16];
  undefined local_138 [16];
  undefined local_128 [16];
  undefined local_118 [16];
  undefined local_108 [16];
  code *local_f8;
  ulong local_f0;
  undefined4 local_e8;
  long local_e0;
  long lStack_d8;
  undefined local_d0;
  undefined4 local_cc;
  undefined local_c8;
  undefined local_c0 [16];
  undefined8 local_b0;
  undefined local_a8 [16];
  long local_98;
  undefined *local_90;
  undefined8 local_88;
  undefined local_80;
  undefined7 uStack_7f;
  undefined *local_70;
  undefined8 local_68;
  undefined8 local_60;
  undefined8 local_58;
  int local_50;
  undefined8 local_48;
  undefined local_40;
  long local_30;
  
  local_f0 = *(ulong *)(param_3[1] + 8);
  local_30 = *(long *)(in_FS_OFFSET + 0x28);
  *param_1 = 0;
  *(undefined8 *)(param_1 + 8) = 0;
  local_f8 = *(code **)param_3[1];
  auVar1._8_8_ = 0;
  auVar1._0_8_ = local_f0;
  local_138 = auVar1 << 0x40;
  local_148 = (undefined  [16])0x0;
  if (local_f8 == (code *)0x0) {
    local_e0 = *param_2;
    auVar2._8_8_ = 0;
    auVar2._0_8_ = local_f0;
    local_118 = auVar2 << 0x40;
    lStack_d8 = param_2[1] + local_e0;
    local_128 = (undefined  [16])0x0;
    local_f8 = (code *)0x0;
    local_108 = (undefined  [16])0x0;
  }
  else {
    local_108 = *param_3;
    local_128 = *param_3;
    local_148 = *param_3;
    param_3[1] = (undefined  [16])0x0;
    local_e0 = *param_2;
    lStack_d8 = param_2[1] + local_e0;
    local_138 = (undefined  [16])0x0;
    local_118 = (undefined  [16])0x0;
  }
  local_e8 = 0;
  local_cc = 0xffffffff;
  local_c8 = 0;
  local_b0 = 0;
  local_98 = 0;
  local_88 = 0;
  local_80 = 0;
  local_70 = &DAT_000e3155;
  local_68 = 0;
  local_60 = 0;
  local_58 = 0;
  local_c0 = (undefined  [16])0x0;
  local_a8 = (undefined  [16])0x0;
  local_d0 = param_5;
  local_90 = &local_80;
  plVar3 = localeconv();
  if (plVar3->decimal_point == (char *)0x0) {
    local_50 = 0x2e;
  }
  else {
    local_50 = (int)*plVar3->decimal_point;
  }
  local_48 = 0xffffffffffffffff;
  local_40 = param_4;
                    /* try { // try from 00038ab6 to 00038aba has its CatchHandler @ 00038bd7 */
  local_e8 = FUN_00034bb0(&local_e0);
  if ((code *)local_118._0_8_ != (code *)0x0) {
    (*(code *)local_118._0_8_)(local_128,local_128,3);
  }
                    /* try { // try from 00038ae8 to 00038aec has its CatchHandler @ 00038bdc */
  FUN_00038160(local_108,1,param_1);
  if (local_90 != &local_80) {
    thunk_FUN_000d36e0(local_90,CONCAT71(uStack_7f,local_80) + 1);
  }
  if (local_a8._0_8_ != 0) {
    thunk_FUN_000d36e0(local_a8._0_8_,local_98 - local_a8._0_8_);
  }
  if (local_f8 != (code *)0x0) {
    (*local_f8)(local_108,local_108,3);
  }
  if ((code *)local_138._0_8_ != (code *)0x0) {
    (*(code *)local_138._0_8_)(local_148,local_148,3);
  }
  if (local_30 == *(long *)(in_FS_OFFSET + 0x28)) {
    return param_1;
  }
                    /* WARNING: Subroutine does not return */
  __stack_chk_fail();
}


