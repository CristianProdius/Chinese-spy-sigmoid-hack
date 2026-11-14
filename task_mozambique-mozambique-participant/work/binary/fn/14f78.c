// ===== FUNC 14f78 size=100

/* WARNING: Removing unreachable block (ram,0x00014fb9) */
/* WARNING: Removing unreachable block (ram,0x00014fc6) */
/* WARNING: Removing unreachable block (ram,0x00014faa) */

void FUN_00014f78(void)

{
  long unaff_RBP;
  undefined8 unaff_retaddr;
  
  FUN_000410a0();
  if (*(long **)(unaff_RBP + 0x10) != (long *)0x0) {
                    /* try { // try from 00014f99 to 00014fdb has its CatchHandler @ 00014ff5 */
    (**(code **)(**(long **)(unaff_RBP + 0x10) + 8))();
    *(undefined8 *)(unaff_RBP + 0x10) = 0;
  }
  __uselocale(unaff_retaddr);
                    /* WARNING: Subroutine does not return */
  FUN_00041f50();
}


