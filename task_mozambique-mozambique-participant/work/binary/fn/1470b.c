// ===== FUNC 1470b size=148

void FUN_0001470b(void)

{
  char cVar1;
  long *plVar2;
  undefined8 *puVar3;
  
  FUN_000410a0();
  plVar2 = (long *)FUN_00041320();
  puVar3 = (undefined8 *)*plVar2;
  if ((*(byte *)(puVar3 + 10) & 1) == 0) {
    puVar3 = puVar3 + 0xe;
  }
  else {
    puVar3 = (undefined8 *)*puVar3;
  }
                    /* try { // try from 0001472c to 0001478b has its CatchHandler @ 00014792 */
  FUN_000416a0(0);
  cVar1 = FUN_000415b0(&stack0x00000000,puVar3[-0xe],puVar3);
  if (cVar1 == '\0') {
    cVar1 = FUN_000415b0(&stack0x00000000,&PTR_PTR_FUN_0011ce00,0);
    if (cVar1 != '\0') {
      puVar3 = (undefined8 *)FUN_00040f40(8);
      *puVar3 = &PTR_FUN_0011ce70;
                    /* WARNING: Subroutine does not return */
      FUN_00041f00(puVar3,&PTR_PTR_FUN_0011ce00,FUN_00041200);
    }
                    /* WARNING: Subroutine does not return */
    FUN_00041d80();
  }
                    /* WARNING: Subroutine does not return */
                    /* try { // try from 000147ab to 000147af has its CatchHandler @ 00014792 */
  FUN_00041f50();
}


