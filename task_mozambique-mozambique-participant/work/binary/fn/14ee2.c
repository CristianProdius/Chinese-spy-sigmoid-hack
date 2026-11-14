// ===== FUNC 14ee2 size=100

/* WARNING: Removing unreachable block (ram,0x00014f23) */
/* WARNING: Removing unreachable block (ram,0x00014f30) */
/* WARNING: Removing unreachable block (ram,0x00014f14) */

void FUN_00014ee2(void)

{
  long unaff_RBP;
  undefined8 unaff_retaddr;
  
  FUN_000410a0();
  if (*(long **)(unaff_RBP + 0x10) != (long *)0x0) {
                    /* try { // try from 00014f03 to 00014f45 has its CatchHandler @ 00014f5f */
    (**(code **)(**(long **)(unaff_RBP + 0x10) + 8))();
    *(undefined8 *)(unaff_RBP + 0x10) = 0;
  }
  __uselocale(unaff_retaddr);
                    /* WARNING: Subroutine does not return */
  FUN_00041f50();
}


