// ===== FUNC 31050 size=243

void FUN_00031050(undefined *param_1,long *param_2)

{
  long lVar1;
  undefined (*pauVar2) [16];
  long lVar3;
  undefined *puVar4;
  long lVar5;
  long lVar6;
  
  *param_1 = 0;
  *(undefined8 *)(param_1 + 8) = 0;
                    /* try { // try from 0003107d to 00031096 has its CatchHandler @ 00031149 */
  FUN_00024620(param_1 + 8,0);
  lVar1 = param_2[1];
  lVar6 = *param_2;
  *param_1 = 2;
  pauVar2 = (undefined (*) [16])FUN_00041fe0(0x18);
  *(undefined8 *)pauVar2[1] = 0;
  lVar5 = lVar1 - lVar6;
  *pauVar2 = (undefined  [16])0x0;
  lVar3 = lVar5 >> 3;
  if (-1 < lVar5) {
    lVar5 = lVar3 * -0x2492492492492490;
    if (lVar3 * 0x6db6db6db6db6db7 == 0) {
      puVar4 = (undefined *)0x0;
    }
    else {
                    /* try { // try from 000310d8 to 000310dc has its CatchHandler @ 0003114e */
      puVar4 = (undefined *)FUN_00041fe0(lVar5);
    }
    *(undefined **)*pauVar2 = puVar4;
    *(undefined **)pauVar2[1] = puVar4 + lVar5;
    for (; lVar1 != lVar6; lVar6 = lVar6 + 0x38) {
      *puVar4 = 0;
      *(undefined8 *)(puVar4 + 8) = 0;
                    /* try { // try from 00031109 to 0003110d has its CatchHandler @ 00031153 */
      FUN_000303d0(puVar4,lVar6);
      puVar4 = puVar4 + 0x10;
    }
    *(undefined **)(*pauVar2 + 8) = puVar4;
    *(undefined (**) [16])(param_1 + 8) = pauVar2;
    return;
  }
                    /* WARNING: Subroutine does not return */
                    /* try { // try from 00031144 to 00031148 has its CatchHandler @ 0003114e */
  FUN_00015e26("cannot create std::vector larger than max_size()");
}


