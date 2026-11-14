// ===== FUNC 15280 size=100

/* WARNING: Removing unreachable block (ram,0x000152c1) */
/* WARNING: Removing unreachable block (ram,0x000152ce) */
/* WARNING: Removing unreachable block (ram,0x000152b2) */

void FUN_00015280(void)

{
  long unaff_RBP;
  undefined8 unaff_retaddr;
  
  FUN_000410a0();
  if (*(long **)(unaff_RBP + 0x10) != (long *)0x0) {
                    /* try { // try from 000152a1 to 000152e3 has its CatchHandler @ 000152fd */
    (**(code **)(**(long **)(unaff_RBP + 0x10) + 8))();
    *(undefined8 *)(unaff_RBP + 0x10) = 0;
  }
  __uselocale(unaff_retaddr);
                    /* WARNING: Subroutine does not return */
  FUN_00041f50();
}


