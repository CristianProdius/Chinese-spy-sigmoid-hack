// LD_PRELOAD tracer for mozambique-engine: logs every Professor decision.
// Patches the single `call 3ae20` (ReferencePlayer::choose) at 0x3d309 to go through wrapper().
// Output (one JSON line per decision) goes to the file named by $MOZ_TRACE (default stderr).
#define _GNU_SOURCE
#include <link.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <sys/mman.h>
#include <unistd.h>

static uintptr_t base;
static FILE *out;
typedef void *(*choose_t)(void *, void *, void *);

static void put_order(const unsigned char *o) {
    const char *s = *(const char **)o;
    size_t n = *(size_t *)(o + 8);
    const int *f = (const int *)(o + 0x20);
    fprintf(out, "{\"op\":\"%.*s\",\"boat\":%d,\"destination\":%d,\"good\":%d,\"quantity\":%d,\"contract\":%d}",
            (int)n, s, f[0], f[1], f[2], f[3], f[4]);
}

static void *wrapper(void *ret, unsigned char *player, unsigned char *view) {
    choose_t orig = (choose_t)(base + 0x3ae20);
    void *r = orig(ret, player, view);
    fprintf(out, "{\"round\":%d,\"seat\":%d,\"style\":[%g,%g,%d],\"action\":",
            *(int *)(view + 0x660), *(int *)(view + 0x664),
            *(double *)player, *(double *)(player + 8), *(int *)(player + 0x10));
    put_order((unsigned char *)ret);
    fprintf(out, ",\"est\":[");
    for (int i = 0; i < 10; i++) fprintf(out, "%s%d", i ? "," : "", *(int *)(player + 0x6e0 + 4 * i));
    fprintf(out, "],\"plan_contracts\":[");
    int *cb = *(int **)(player + 0x758), *ce = *(int **)(player + 0x760);
    for (int *p = cb; p != ce; p++) fprintf(out, "%s%d", p == cb ? "" : ",", *p);
    fprintf(out, "],\"plan\":[");
    unsigned char *cur = *(unsigned char **)(player + 0x718);
    unsigned char **node = *(unsigned char ***)(player + 0x730);
    unsigned char *fin = *(unsigned char **)(player + 0x738);
    int first = 1, guard = 0;
    while (cur && cur != fin && guard++ < 2000) {
        if (!first) fputc(',', out);
        first = 0;
        put_order(cur);
        cur += 0x38;
        if (cur == *node + 0x1f8) { node++; cur = *node; }
    }
    fprintf(out, "]}\n");
    fflush(out);
    return r;
}

static int cb(struct dl_phdr_info *info, size_t sz, void *data) {
    if (!base && (info->dlpi_name == NULL || info->dlpi_name[0] == 0)) base = info->dlpi_addr;
    return 0;
}

__attribute__((constructor)) static void init(void) {
    char exe[512];
    ssize_t n = readlink("/proc/self/exe", exe, sizeof exe - 1);
    if (n <= 0) return;
    exe[n] = 0;
    if (!strstr(exe, "mozambique-engine")) return;
    dl_iterate_phdr(cb, NULL);
    const char *path = getenv("MOZ_TRACE");
    out = path ? fopen(path, "w") : stderr;
    if (!out) out = stderr;
    unsigned char *site = (unsigned char *)(base + 0x3d309);
    if (site[0] != 0xe8) { fprintf(stderr, "hook: unexpected byte at call site\n"); return; }
    // rel32 cannot reach a far library: use a small trampoline in a code cave? Simpler: allocate near page.
    unsigned char *tramp = mmap((void *)((base + 0x200000) & ~0xfffUL), 4096, PROT_READ | PROT_WRITE | PROT_EXEC,
                                MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
    if (tramp == MAP_FAILED) { fprintf(stderr, "hook: mmap failed\n"); return; }
    intptr_t rel = (intptr_t)tramp - (intptr_t)(site + 5);
    if (rel > 0x7fffffffL || rel < -0x80000000L) { fprintf(stderr, "hook: trampoline too far\n"); return; }
    // tramp: movabs rax, wrapper ; jmp rax
    tramp[0] = 0x48; tramp[1] = 0xb8; uintptr_t w = (uintptr_t)wrapper; memcpy(tramp + 2, &w, 8);
    tramp[10] = 0xff; tramp[11] = 0xe0;
    uintptr_t pg = (uintptr_t)site & ~0xfffUL;
    mprotect((void *)pg, 8192, PROT_READ | PROT_WRITE | PROT_EXEC);
    int32_t r32 = (int32_t)rel; memcpy(site + 1, &r32, 4);
    mprotect((void *)pg, 8192, PROT_READ | PROT_EXEC);
}
