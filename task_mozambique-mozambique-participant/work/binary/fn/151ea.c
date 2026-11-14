// ===== FUNC 151ea size=100

/* WARNING: Removing unreachable block (ram,0x0001522b) */
/* WARNING: Removing unreachable block (ram,0x00015238) */
/* WARNING: Removing unreachable block (ram,0x0001521c) */

void FUN_000151ea(void)

{
  long unaff_RBP;
  undefined8 unaff_retaddr;
  
  FUN_000410a0();
  if (*(long **)(unaff_RBP + 0x10) != (long *)0x0) {
                    /* try { // try from 0001520b to 0001524d has its CatchHandler @ 00015267 */
    (**(code **)(**(long **)(unaff_RBP + 0x10) + 8))();
    *(undefined8 *)(unaff_RBP + 0x10) = 0;
  }
  __uselocale(unaff_retaddr);
                    /* WARNING: Subroutine does not return */
  FUN_00041f50();
}


