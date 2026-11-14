// ===== FUNC 1524e size=25

/* WARNING: Removing unreachable block (ram,0x0001522b) */
/* WARNING: Removing unreachable block (ram,0x00015238) */

void FUN_0001524e(void)

{
  long unaff_RBP;
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
  __uselocale(unaff_retaddr);
                    /* WARNING: Subroutine does not return */
  FUN_00041f50();
}


