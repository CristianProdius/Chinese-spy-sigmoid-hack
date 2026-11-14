// ===== FUNC 1504e size=105

/* WARNING: Removing unreachable block (ram,0x00015096) */
/* WARNING: Removing unreachable block (ram,0x00015084) */
/* WARNING: Removing unreachable block (ram,0x000150a8) */

void FUN_0001504e(void)

{
  long unaff_RBX;
  
  FUN_000410a0();
  if (*(long **)(unaff_RBX + 0x10) != (long *)0x0) {
                    /* try { // try from 00015073 to 000150b6 has its CatchHandler @ 000150d6 */
    (**(code **)(**(long **)(unaff_RBX + 0x10) + 8))();
    *(undefined8 *)(unaff_RBX + 0x10) = 0;
  }
                    /* WARNING: Subroutine does not return */
  FUN_00041f50();
}


