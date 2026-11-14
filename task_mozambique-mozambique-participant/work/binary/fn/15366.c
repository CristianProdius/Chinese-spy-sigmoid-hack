// ===== FUNC 15366 size=31

void FUN_00015366(void)

{
  long unaff_RBX;
  
  FUN_000410a0();
  if (*(long **)(unaff_RBX + 0x10) != (long *)0x0) {
                    /* try { // try from 00015377 to 00015384 has its CatchHandler @ 00015385 */
    (**(code **)(**(long **)(unaff_RBX + 0x10) + 8))();
  }
  *(undefined8 *)(unaff_RBX + 0x10) = 0;
                    /* WARNING: Subroutine does not return */
  FUN_00041f50();
}


