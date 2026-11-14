// ===== FUNC 14dfc size=105

/* WARNING: Removing unreachable block (ram,0x00014e44) */
/* WARNING: Removing unreachable block (ram,0x00014e32) */
/* WARNING: Removing unreachable block (ram,0x00014e56) */

void FUN_00014dfc(void)

{
  long unaff_RBX;
  
  FUN_000410a0();
  if (*(long **)(unaff_RBX + 0x10) != (long *)0x0) {
                    /* try { // try from 00014e21 to 00014e64 has its CatchHandler @ 00014e84 */
    (**(code **)(**(long **)(unaff_RBX + 0x10) + 8))();
    *(undefined8 *)(unaff_RBX + 0x10) = 0;
  }
                    /* WARNING: Subroutine does not return */
  FUN_00041f50();
}


