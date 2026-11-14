// ===== FUNC 17ba0 size=71

void FUN_00017ba0(long param_1,char *param_2)

{
  size_t sVar1;
  
  sVar1 = strlen(param_2);
  if (sVar1 <= 0x3fffffffffffffffU - *(long *)(param_1 + 8)) {
    FUN_000b2500(param_1,param_2);
    return;
  }
                    /* WARNING: Subroutine does not return */
  FUN_00015e26("basic_string::append");
}


