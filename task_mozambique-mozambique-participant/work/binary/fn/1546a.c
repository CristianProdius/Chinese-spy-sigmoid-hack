// ===== FUNC 1546a size=31

void FUN_0001546a(void)

{
  long unaff_RBX;
  
  FUN_000410a0();
  if (*(long **)(unaff_RBX + 0x10) != (long *)0x0) {
                    /* try { // try from 0001547b to 00015488 has its CatchHandler @ 00015489 */
    (**(code **)(**(long **)(unaff_RBX + 0x10) + 8))();
  }
  *(undefined8 *)(unaff_RBX + 0x10) = 0;
                    /* WARNING: Subroutine does not return */
  FUN_00041f50();
}


