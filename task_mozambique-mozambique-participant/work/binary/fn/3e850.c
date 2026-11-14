// ===== FUNC 3e850 size=3451

void FUN_0003e850(undefined *param_1,long param_2)

{
  int *piVar1;
  undefined uVar2;
  int iVar3;
  char cVar4;
  undefined (*pauVar5) [16];
  long *plVar6;
  undefined8 uVar7;
  ulong uVar8;
  undefined *puVar9;
  undefined *puVar10;
  undefined *puVar11;
  long lVar12;
  undefined *puVar13;
  int *piVar14;
  long in_FS_OFFSET;
  bool bVar15;
  undefined8 local_340;
  char local_338 [8];
  undefined (*local_330) [16];
  undefined8 *local_328;
  undefined (*local_320) [16];
  undefined local_318 [8];
  undefined (*local_310) [16];
  undefined8 local_308;
  undefined local_300 [8];
  undefined8 local_2f8;
  undefined8 local_2f0;
  undefined local_2e8 [8];
  undefined (*local_2e0) [16];
  undefined8 local_2d8;
  undefined local_2d0 [8];
  undefined8 local_2c8;
  undefined8 local_2c0;
  undefined local_2b8 [8];
  long *local_2b0;
  undefined8 local_2a8;
  undefined local_2a0;
  long local_298 [2];
  undefined local_288 [8];
  long *local_280;
  undefined8 local_278;
  undefined local_270;
  long local_268 [2];
  undefined local_258 [8];
  undefined8 local_250;
  undefined8 local_248;
  undefined local_240;
  long local_238 [2];
  undefined local_228 [8];
  long *local_220;
  undefined8 local_218;
  undefined local_210 [8];
  undefined local_208 [8];
  undefined8 local_200;
  undefined local_1f8 [8];
  undefined8 local_1f0;
  undefined8 local_1e8;
  undefined local_1e0;
  undefined (*local_1d8) [16];
  undefined8 local_1d0;
  undefined local_1c8 [8];
  long *local_1c0;
  undefined8 local_1b8;
  undefined local_1b0;
  undefined (*local_1a8) [16];
  undefined8 local_1a0;
  undefined local_198 [8];
  long *local_190;
  undefined8 local_188;
  undefined local_180;
  undefined8 local_178;
  int *local_170;
  undefined local_168 [8];
  undefined (*local_160) [16];
  undefined8 local_158;
  undefined local_150 [8];
  undefined local_148 [8];
  undefined8 local_140;
  undefined local_138 [16];
  undefined8 local_128;
  undefined local_120 [16];
  undefined8 local_110;
  undefined local_108 [16];
  undefined8 local_f8;
  undefined local_f0 [16];
  undefined8 local_e0;
  undefined local_d8 [16];
  undefined8 local_c8;
  undefined local_c0 [16];
  undefined8 local_b0;
  undefined local_a8 [16];
  undefined8 local_98;
  undefined local_90 [16];
  undefined8 local_80;
  undefined local_78 [16];
  undefined8 local_68;
  undefined local_60 [16];
  undefined8 local_50;
  long local_40;
  
  lVar12 = 0;
  local_40 = *(long *)(in_FS_OFFSET + 0x28);
  FUN_0002fd20(local_338,0,0,0,2);
  do {
    cVar4 = local_338[0];
    if (*(char *)(param_2 + 0x694 + lVar12) == '\0') {
      local_328 = (undefined8 *)0x0;
      local_320 = (undefined (*) [16])0x0;
      if (local_338[0] == '\0') goto LAB_0003e8d9;
LAB_0003e967:
      if (local_338[0] != '\x02') {
        uVar7 = FUN_00040f40(0x20);
        local_340 = FUN_000137b8(cVar4,"cannot use push_back() with ");
                    /* try { // try from 0003fcca to 0003fcce has its CatchHandler @ 0003fd2d */
        FUN_0001df60();
                    /* try { // try from 0003fcdc to 0003fce0 has its CatchHandler @ 0003fd28 */
        FUN_00013ba0(uVar7,0x134,local_138);
        FUN_000b07c0(local_138);
                    /* WARNING: Subroutine does not return */
                    /* try { // try from 0003fcfc to 0003fd00 has its CatchHandler @ 0003fc8a */
        FUN_00041f00(uVar7,&PTR_PTR_FUN_0011cc70,FUN_0001ab10);
      }
    }
    else {
      local_320 = (undefined (*) [16])(long)*(int *)(param_2 + 0x66c + lVar12 * 4);
      local_328 = (undefined8 *)CONCAT71(local_328._1_7_,5);
      if (local_338[0] != '\0') goto LAB_0003e967;
LAB_0003e8d9:
      local_338[0] = '\x02';
                    /* try { // try from 0003e8e6 to 0003e914 has its CatchHandler @ 0003fc8a */
      local_330 = (undefined (*) [16])FUN_00041fe0(0x18);
      *(undefined8 *)local_330[1] = 0;
      *local_330 = (undefined  [16])0x0;
    }
    FUN_000182f0(local_330,&local_328);
    lVar12 = lVar12 + 1;
    FUN_00024620(&local_320,(ulong)local_328 & 0xff);
    if (lVar12 == 10) {
      local_318[0] = 0;
      local_310 = (undefined (*) [16])0x0;
                    /* try { // try from 0003e9a6 to 0003e9bc has its CatchHandler @ 0003fc5e */
      FUN_00024620(&local_310,0);
      local_318[0] = 3;
      pauVar5 = (undefined (*) [16])FUN_00041fe0(0x20);
      local_328 = &local_340;
      local_320 = pauVar5;
                    /* try { // try from 0003e9e6 to 0003e9ea has its CatchHandler @ 0003fc59 */
      FUN_00018b10(pauVar5,"map");
      local_308 = 0;
      local_300[0] = 0;
      local_2f8 = 0;
      local_310 = pauVar5;
                    /* try { // try from 0003ea1e to 0003ea22 has its CatchHandler @ 0003fab4 */
      FUN_00032dc0(local_300,param_2);
      local_2f0 = 0;
                    /* try { // try from 0003ea5c to 0003ea60 has its CatchHandler @ 0003faa7 */
      FUN_0002fd20(local_138,local_318,2,1,2);
      local_128 = 0;
      local_2e8[0] = 0;
      local_2e0 = (undefined (*) [16])0x0;
                    /* try { // try from 0003ea93 to 0003eaa9 has its CatchHandler @ 0003fdaf */
      FUN_00024620(&local_2e0,0);
      local_2e8[0] = 3;
      pauVar5 = (undefined (*) [16])FUN_00041fe0(0x20);
      local_328 = &local_340;
      local_320 = pauVar5;
                    /* try { // try from 0003eacb to 0003eacf has its CatchHandler @ 0003fdaa */
      FUN_00018b10(pauVar5,&DAT_000e1db8);
      local_2d8 = 0;
      local_2d0[0] = 0;
      local_2c8 = 0;
      local_2e0 = pauVar5;
                    /* try { // try from 0003eb07 to 0003eb0b has its CatchHandler @ 0003fd6d */
      FUN_0003d910(local_2d0,param_2 + 0x588);
      local_2c0 = 0;
                    /* try { // try from 0003eb40 to 0003eb44 has its CatchHandler @ 0003fd68 */
      FUN_0002fd20(local_120,local_2e8,2,1,2);
      local_110 = 0;
      local_2b8[0] = 0;
      local_2b0 = (long *)0x0;
                    /* try { // try from 0003eb77 to 0003eb8d has its CatchHandler @ 0003fd37 */
      FUN_00024620(&local_2b0,0);
      local_2b8[0] = 3;
      plVar6 = (long *)FUN_00041fe0(0x20);
      *plVar6 = (long)(plVar6 + 2);
                    /* try { // try from 0003eba7 to 0003ebab has its CatchHandler @ 0003fd32 */
      FUN_00017bf0(plVar6,"round");
      local_298[0] = (long)*(int *)(param_2 + 0x660);
      local_2a8 = 0;
      local_2a0 = 5;
      local_298[1] = 0;
      local_2b0 = plVar6;
                    /* try { // try from 0003ec03 to 0003ec07 has its CatchHandler @ 0003fc0a */
      FUN_0002fd20(local_108,local_2b8,2,1,2);
      local_f8 = 0;
      local_288[0] = 0;
      local_280 = (long *)0x0;
                    /* try { // try from 0003ec3a to 0003ec50 has its CatchHandler @ 0003fc02 */
      FUN_00024620(&local_280,0);
      local_288[0] = 3;
      plVar6 = (long *)FUN_00041fe0(0x20);
      *plVar6 = (long)(plVar6 + 2);
                    /* try { // try from 0003ec6a to 0003ec6e has its CatchHandler @ 0003f5b1 */
      FUN_00017bf0(plVar6,&DAT_000e1dc2);
      local_268[0] = (long)*(int *)(param_2 + 0x664);
      local_278 = 0;
      local_270 = 5;
      local_268[1] = 0;
      local_280 = plVar6;
                    /* try { // try from 0003ecc6 to 0003ecca has its CatchHandler @ 0003f591 */
      FUN_0002fd20(local_f0,local_288,2,1,2);
      local_e0 = 0;
      local_258[0] = 0;
      local_250 = 0;
                    /* try { // try from 0003ecfd to 0003ed13 has its CatchHandler @ 0003f5a1 */
      FUN_00024620(&local_250,0);
      local_258[0] = 3;
      uVar7 = FUN_00041fe0(0x20);
                    /* try { // try from 0003ed21 to 0003ed25 has its CatchHandler @ 0003f581 */
      FUN_00018b10(uVar7,"opponent_score");
      local_238[0] = (long)*(int *)(param_2 + 0x668);
      local_248 = 0;
      local_240 = 5;
      local_238[1] = 0;
      local_250 = uVar7;
                    /* try { // try from 0003ed7d to 0003ed81 has its CatchHandler @ 0003f5a9 */
      FUN_0002fd20(local_d8,local_258,2,1,2);
      local_c8 = 0;
      local_228[0] = 0;
      local_220 = (long *)0x0;
                    /* try { // try from 0003edb4 to 0003edca has its CatchHandler @ 0003f589 */
      FUN_00024620(&local_220,0);
      local_228[0] = 3;
      plVar6 = (long *)FUN_00041fe0(0x20);
      *plVar6 = (long)(plVar6 + 2);
                    /* try { // try from 0003ede4 to 0003ede8 has its CatchHandler @ 0003fc35 */
      FUN_00017bf0(plVar6,"stocks");
      local_218 = 0;
      local_220 = plVar6;
                    /* try { // try from 0003ee08 to 0003ee0c has its CatchHandler @ 0003fc30 */
      FUN_0002f160(local_210,local_338);
      local_200 = 0;
                    /* try { // try from 0003ee44 to 0003ee48 has its CatchHandler @ 0003fc17 */
      FUN_0002fd20(local_c0,local_228,2,1,2);
      local_b0 = 0;
      local_1f8[0] = 0;
      local_1f0 = 0;
                    /* try { // try from 0003ee7b to 0003ee91 has its CatchHandler @ 0003fc0f */
      FUN_00024620(&local_1f0,0);
      local_1f8[0] = 3;
      uVar7 = FUN_00041fe0(0x20);
                    /* try { // try from 0003ee9f to 0003eea3 has its CatchHandler @ 0003fb09 */
      FUN_00018b10(uVar7,"visible");
      local_1e8 = 0;
      local_1e0 = 0;
      local_1d8 = (undefined (*) [16])0x0;
      local_1f0 = uVar7;
                    /* try { // try from 0003eede to 0003ef02 has its CatchHandler @ 0003faac */
      FUN_00024620(&local_1d8,0);
      local_1e0 = 2;
      puVar10 = (undefined *)(param_2 + 0x69e);
      puVar13 = (undefined *)(param_2 + 0x694);
      pauVar5 = (undefined (*) [16])FUN_00041fe0(0x18);
      uVar8 = (long)puVar10 - (long)puVar13;
      *(undefined8 *)pauVar5[1] = 0;
      *pauVar5 = (undefined  [16])0x0;
      local_320 = pauVar5;
      if (uVar8 >> 0x3b != 0) {
        local_328 = &local_340;
                    /* WARNING: Subroutine does not return */
                    /* try { // try from 0003f56a to 0003f56e has its CatchHandler @ 0003f599 */
        FUN_00015e26("cannot create std::vector larger than max_size()");
      }
      if (uVar8 == 0) {
        puVar9 = (undefined *)0x0;
        local_328 = &local_340;
      }
      else {
        local_328 = &local_340;
                    /* try { // try from 0003ef52 to 0003ef56 has its CatchHandler @ 0003f599 */
        puVar9 = (undefined *)FUN_00041fe0();
      }
      *(undefined **)*pauVar5 = puVar9;
      *(undefined **)pauVar5[1] = puVar9 + uVar8 * 0x10;
      puVar11 = puVar9;
      if (puVar10 != puVar13) {
        do {
          uVar2 = *puVar13;
          puVar13 = puVar13 + 1;
          *puVar11 = 4;
          *(undefined8 *)(puVar11 + 8) = 0;
          puVar11[8] = uVar2;
          puVar11 = puVar11 + 0x10;
        } while (puVar10 != puVar13);
        puVar9 = puVar9 + 0xa0;
      }
      *(undefined **)(*pauVar5 + 8) = puVar9;
      local_1d0 = 0;
      local_1d8 = pauVar5;
                    /* try { // try from 0003efd9 to 0003efdd has its CatchHandler @ 0003f579 */
      FUN_0002fd20(local_a8,local_1f8,2,1,2);
      local_98 = 0;
      local_1c8[0] = 0;
      local_1c0 = (long *)0x0;
                    /* try { // try from 0003f010 to 0003f026 has its CatchHandler @ 0003f992 */
      FUN_00024620(&local_1c0,0);
      local_1c8[0] = 3;
      plVar6 = (long *)FUN_00041fe0(0x20);
      *plVar6 = (long)(plVar6 + 2);
                    /* try { // try from 0003f040 to 0003f044 has its CatchHandler @ 0003f98d */
      FUN_00017bf0(plVar6,&DAT_000e1de5);
      local_1b8 = 0;
      local_1b0 = 0;
      local_1a8 = (undefined (*) [16])0x0;
      local_1c0 = plVar6;
                    /* try { // try from 0003f07f to 0003f0a3 has its CatchHandler @ 0003f574 */
      FUN_00024620(&local_1a8,0);
      local_1b0 = 2;
      piVar1 = (int *)(param_2 + 0x6c0);
      piVar14 = (int *)(param_2 + 0x6a0);
      pauVar5 = (undefined (*) [16])FUN_00041fe0(0x18);
      *(undefined8 *)pauVar5[1] = 0;
      *pauVar5 = (undefined  [16])0x0;
      lVar12 = (long)piVar1 - (long)piVar14 >> 2;
      local_320 = pauVar5;
      if (0x1ffffffffffffffc < (ulong)((long)piVar1 - (long)piVar14)) {
        local_328 = &local_340;
                    /* WARNING: Subroutine does not return */
                    /* try { // try from 0003f55e to 0003f562 has its CatchHandler @ 0003fbbc */
        FUN_00015e26("cannot create std::vector larger than max_size()");
      }
      if (lVar12 == 0) {
        puVar10 = (undefined *)0x0;
        local_328 = &local_340;
      }
      else {
        local_328 = &local_340;
                    /* try { // try from 0003f100 to 0003f104 has its CatchHandler @ 0003fbbc */
        puVar10 = (undefined *)FUN_00041fe0();
      }
      *(undefined **)*pauVar5 = puVar10;
      *(undefined **)pauVar5[1] = puVar10 + lVar12 * 0x10;
      puVar13 = puVar10;
      if (piVar1 != piVar14) {
        do {
          iVar3 = *piVar14;
          piVar14 = piVar14 + 1;
          *puVar13 = 5;
          *(long *)(puVar13 + 8) = (long)iVar3;
          puVar13 = puVar13 + 0x10;
        } while (piVar1 != piVar14);
        puVar10 = puVar10 + 0x80;
      }
      *(undefined **)(*pauVar5 + 8) = puVar10;
      local_1a0 = 0;
      local_1a8 = pauVar5;
                    /* try { // try from 0003f17c to 0003f180 has its CatchHandler @ 0003fbb2 */
      FUN_0002fd20(local_90,local_1c8,2,1,2);
      local_80 = 0;
      local_198[0] = 0;
      local_190 = (long *)0x0;
                    /* try { // try from 0003f1ae to 0003f1c4 has its CatchHandler @ 0003fbb7 */
      FUN_00024620(&local_190,0);
      local_198[0] = 3;
      plVar6 = (long *)FUN_00041fe0(0x20);
      *plVar6 = (long)(plVar6 + 2);
                    /* try { // try from 0003f1de to 0003f1e2 has its CatchHandler @ 0003fbad */
      FUN_00017bf0(plVar6,"enemy_boats");
      local_188 = 0;
      local_180 = 0;
      local_178 = 0;
      local_190 = plVar6;
      local_170 = piVar1;
                    /* try { // try from 0003f233 to 0003f237 has its CatchHandler @ 0003fba8 */
      FUN_0002fd20(local_78,local_198,2,1,2);
      local_68 = 0;
      local_168[0] = 0;
      local_160 = (undefined (*) [16])0x0;
                    /* try { // try from 0003f265 to 0003f27b has its CatchHandler @ 0003fba3 */
      FUN_00024620(&local_160,0);
      local_168[0] = 3;
      pauVar5 = (undefined (*) [16])FUN_00041fe0(0x20);
      local_328 = &local_340;
      local_320 = pauVar5;
                    /* try { // try from 0003f29d to 0003f2a1 has its CatchHandler @ 0003fb5e */
      FUN_00018b10(pauVar5,"legal_actions");
      local_158 = 0;
      local_160 = pauVar5;
                    /* try { // try from 0003f2c5 to 0003f2c9 has its CatchHandler @ 0003fb59 */
      FUN_00031050(local_150,param_2 + 0x6d0);
      local_140 = 0;
                    /* try { // try from 0003f2fc to 0003f300 has its CatchHandler @ 0003f9d7 */
      FUN_0002fd20(local_60,local_168,2,1,2);
      local_50 = 0;
                    /* try { // try from 0003f325 to 0003f329 has its CatchHandler @ 0003f9d2 */
      FUN_0002fd20(&local_328,local_138,10,1,2);
      uVar2 = *param_1;
      *param_1 = local_328._0_1_;
      pauVar5 = *(undefined (**) [16])(param_1 + 8);
      *(undefined (**) [16])(param_1 + 8) = local_320;
      local_328 = (undefined8 *)CONCAT71(local_328._1_7_,uVar2);
      local_320 = pauVar5;
      FUN_00024620(&local_320);
      puVar10 = local_60;
      do {
        FUN_00024620(puVar10 + 8,*puVar10);
        bVar15 = local_138 != puVar10;
        puVar10 = puVar10 + -0x18;
      } while (bVar15);
      FUN_00024620(local_148,local_150[0]);
      FUN_00024620(&local_160,local_168[0]);
      FUN_00024620(&local_178,local_180);
      FUN_00024620(&local_190,local_198[0]);
      FUN_00024620(&local_1a8,local_1b0);
      FUN_00024620(&local_1c0,local_1c8[0]);
      FUN_00024620(&local_1d8,local_1e0);
      FUN_00024620(&local_1f0,local_1f8[0]);
      FUN_00024620(local_208,local_210[0]);
      FUN_00024620(&local_220,local_228[0]);
      FUN_00024620(local_238,local_240);
      FUN_00024620(&local_250,local_258[0]);
      FUN_00024620(local_268,local_270);
      FUN_00024620(&local_280,local_288[0]);
      FUN_00024620(local_298,local_2a0);
      FUN_00024620(&local_2b0,local_2b8[0]);
      FUN_00024620(&local_2c8,local_2d0[0]);
      FUN_00024620(&local_2e0,local_2e8[0]);
      FUN_00024620(&local_2f8,local_300[0]);
      FUN_00024620(&local_310,local_318[0]);
      FUN_00024620(&local_330,local_338[0]);
      if (local_40 != *(long *)(in_FS_OFFSET + 0x28)) {
                    /* WARNING: Subroutine does not return */
        __stack_chk_fail();
      }
      return;
    }
  } while( true );
}


