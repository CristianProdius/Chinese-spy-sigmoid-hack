// ===== FUNC 14801 size=108

void FUN_00014801(undefined8 param_1,undefined8 param_2,long param_3)

{
  long *plVar1;
  char *__s;
  undefined8 *unaff_RBP;
  
  if (param_3 == 1) {
    plVar1 = (long *)FUN_000410a0();
    __s = (char *)(**(code **)(*plVar1 + 0x10))(plVar1);
                    /* try { // try from 00014838 to 00014856 has its CatchHandler @ 0001487a */
    fwrite("  what():  ",1,0xb,(FILE *)*unaff_RBP);
    fputs(__s,(FILE *)*unaff_RBP);
    fputc(10,(FILE *)*unaff_RBP);
    FUN_00041110();
  }
  else {
    FUN_000410a0();
    FUN_00041110();
  }
                    /* WARNING: Subroutine does not return */
  abort();
}


