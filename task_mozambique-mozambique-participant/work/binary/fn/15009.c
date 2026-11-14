// ===== FUNC 15009 size=5

/* WARNING: Removing unreachable block (ram,0x00014fc6) */

void FUN_00015009(void)

{
  long unaff_RBP;
  long unaff_R15;
  undefined8 unaff_retaddr;
  long in_stack_00000008;
  
  FUN_000410a0();
  if (*(long **)(unaff_RBP + 0x10) != (long *)0x0) {
    (**(code **)(**(long **)(unaff_RBP + 0x10) + 8))();
  }
  *(undefined8 *)(unaff_RBP + 0x10) = 0;
  if (in_stack_00000008 != 0) {
    thunk_FUN_000d36e0(in_stack_00000008);
  }
  if (unaff_R15 != 0) {
    thunk_FUN_000d36e0();
  }
  __uselocale(unaff_retaddr);
                    /* WARNING: Subroutine does not return */
  FUN_00041f50();
}


