// ===== FUNC 1540e size=31

void FUN_0001540e(void)

{
  long unaff_RBX;
  
  FUN_000410a0();
  if (*(long **)(unaff_RBX + 0x10) != (long *)0x0) {
                    /* try { // try from 0001541f to 0001542c has its CatchHandler @ 0001542d */
    (**(code **)(**(long **)(unaff_RBX + 0x10) + 8))();
  }
  *(undefined8 *)(unaff_RBX + 0x10) = 0;
                    /* WARNING: Subroutine does not return */
  FUN_00041f50();
}


