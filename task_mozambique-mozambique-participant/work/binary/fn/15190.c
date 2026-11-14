// ===== FUNC 15190 size=9

void FUN_00015190(void)

{
  long unaff_RBX;
  long param_7;
  long param_8;
  long in_stack_00000018;
  
  param_8 = 0;
  FUN_000410a0();
  if (*(long **)(unaff_RBX + 0x10) != (long *)0x0) {
    (**(code **)(**(long **)(unaff_RBX + 0x10) + 8))();
  }
  *(undefined8 *)(unaff_RBX + 0x10) = 0;
  if (in_stack_00000018 != 0) {
    thunk_FUN_000d36e0(in_stack_00000018);
  }
  if (param_7 != 0) {
    thunk_FUN_000d36e0(param_7);
  }
  if (param_8 != 0) {
    thunk_FUN_000d36e0(param_8);
  }
                    /* WARNING: Subroutine does not return */
  FUN_00041f50();
}


