// ===== FUNC 2fb70 size=267

undefined4 * FUN_0002fb70(undefined4 *param_1,undefined8 param_2)

{
  undefined4 uVar1;
  long lVar2;
  long lVar3;
  undefined4 *puVar4;
  undefined4 *puVar5;
  undefined4 *puVar6;
  undefined8 uVar7;
  undefined4 *puVar8;
  
  puVar6 = (undefined4 *)FUN_00041fe0(0x50);
  lVar2 = *(long *)(param_1 + 8);
  lVar3 = *(long *)(param_1 + 10);
  *(undefined4 **)(puVar6 + 8) = puVar6 + 0xc;
                    /* try { // try from 0002fba6 to 0002fbaa has its CatchHandler @ 0002fc80 */
  FUN_00017e00(puVar6 + 8,lVar2,lVar3 + lVar2);
                    /* try { // try from 0002fbb4 to 0002fbb8 has its CatchHandler @ 0002fc7b */
  FUN_0002f160(puVar6 + 0x10,param_1 + 0x10);
  uVar1 = *param_1;
  lVar2 = *(long *)(param_1 + 6);
  *(undefined8 *)(puVar6 + 4) = 0;
  *(undefined8 *)(puVar6 + 6) = 0;
  *puVar6 = uVar1;
  *(undefined8 *)(puVar6 + 2) = param_2;
  if (lVar2 != 0) {
                    /* try { // try from 0002fbe2 to 0002fc04 has its CatchHandler @ 0002fc8f */
    uVar7 = FUN_0002fb70(lVar2,puVar6);
    *(undefined8 *)(puVar6 + 6) = uVar7;
  }
  puVar5 = puVar6;
  for (puVar4 = *(undefined4 **)(param_1 + 4); puVar4 != (undefined4 *)0x0;
      puVar4 = *(undefined4 **)(puVar4 + 4)) {
    puVar8 = (undefined4 *)FUN_00041fe0(0x50);
    lVar2 = *(long *)(puVar4 + 10);
    *(undefined4 **)(puVar8 + 8) = puVar8 + 0xc;
                    /* try { // try from 0002fc22 to 0002fc26 has its CatchHandler @ 0002fc85 */
    FUN_00017e00(puVar8 + 8,*(long *)(puVar4 + 8),lVar2 + *(long *)(puVar4 + 8));
                    /* try { // try from 0002fc2f to 0002fc33 has its CatchHandler @ 0002fc8a */
    FUN_0002f160(puVar8 + 0x10,puVar4 + 0x10);
    uVar1 = *puVar4;
    *(undefined8 *)(puVar8 + 4) = 0;
    *(undefined8 *)(puVar8 + 6) = 0;
    *puVar8 = uVar1;
    *(undefined4 **)(puVar5 + 4) = puVar8;
    *(undefined4 **)(puVar8 + 2) = puVar5;
    if (*(long *)(puVar4 + 6) != 0) {
                    /* try { // try from 0002fc5d to 0002fc61 has its CatchHandler @ 0002fc8f */
      uVar7 = FUN_0002fb70(*(long *)(puVar4 + 6),puVar8);
      *(undefined8 *)(puVar8 + 6) = uVar7;
    }
    puVar5 = puVar8;
  }
  return puVar6;
}


