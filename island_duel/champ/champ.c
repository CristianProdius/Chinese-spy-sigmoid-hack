/* Clone of the Island Duel champion (opponent) decision procedure, rebuilt from
 * the engine binary: iterative-deepening negamax alpha-beta (max 4 plies,
 * 2048-node budget shared across iterations, transposition table), searching
 * over its fogged memory of the board, with the leaf evaluation
 *
 *   100*(score_me - score_opp)
 *   + min(plies/10,1) * E[profile] * (energy_me - energy_opp)
 *   + min(plies/24,1) * F[profile] * ((H1_me - H1_opp) + 0.35*(H2_me - H2_opp))
 *
 * where H1 sums h = max(0, 3w - 4c) over empty tiles adjacent to a side's
 * territory and H2 over empty tiles one step further out.
 * Build: gcc -O2 -shared -fPIC -o libchamp.so champ.c
 */
#include <stdint.h>
#include <string.h>
#include <setjmp.h>
#include <stdlib.h>

#define NT 225
typedef struct { uint64_t w[4]; } BB;

static const double E_PROF[3] = {160.0, 240.0, 100.0};
static const double F_PROF[3] = {9.0, 6.0, 14.0};
#define NEG_INF (-1e100)
#define POS_INF (1e100)

static BB VALID, STARTS, NOTCOL0, NOTCOL14;
static int inited = 0;

static inline int bb_get(const BB *b, int i) { return (b->w[i >> 6] >> (i & 63)) & 1; }
static inline void bb_set(BB *b, int i) { b->w[i >> 6] |= 1ULL << (i & 63); }
static inline void bb_clr(BB *b, int i) { b->w[i >> 6] &= ~(1ULL << (i & 63)); }
static inline BB bb_and(BB a, BB b) { BB r; for (int k = 0; k < 4; k++) r.w[k] = a.w[k] & b.w[k]; return r; }
static inline BB bb_or(BB a, BB b) { BB r; for (int k = 0; k < 4; k++) r.w[k] = a.w[k] | b.w[k]; return r; }
static inline BB bb_not(BB a) { BB r; for (int k = 0; k < 4; k++) r.w[k] = ~a.w[k] & VALID.w[k]; return r; }
static inline int bb_any(BB a) { return (a.w[0] | a.w[1] | a.w[2] | a.w[3]) != 0; }

static BB shl(BB a, int s) { /* s < 64 */
    BB r;
    r.w[3] = (a.w[3] << s) | (a.w[2] >> (64 - s));
    r.w[2] = (a.w[2] << s) | (a.w[1] >> (64 - s));
    r.w[1] = (a.w[1] << s) | (a.w[0] >> (64 - s));
    r.w[0] = a.w[0] << s;
    return r;
}
static BB shr(BB a, int s) {
    BB r;
    r.w[0] = (a.w[0] >> s) | (a.w[1] << (64 - s));
    r.w[1] = (a.w[1] >> s) | (a.w[2] << (64 - s));
    r.w[2] = (a.w[2] >> s) | (a.w[3] << (64 - s));
    r.w[3] = a.w[3] >> s;
    return r;
}
/* orthogonal neighbours of a set (excluding nothing; callers mask) */
static BB nbr(BB a) {
    BB r = bb_or(bb_or(shl(bb_and(a, NOTCOL14), 1), shr(bb_and(a, NOTCOL0), 1)), bb_or(shl(a, 15), shr(a, 15)));
    return bb_and(r, VALID);
}

void init_masks(void) {
    if (inited) return;
    memset(&VALID, 0, sizeof VALID); memset(&STARTS, 0, sizeof STARTS);
    memset(&NOTCOL0, 0, sizeof NOTCOL0); memset(&NOTCOL14, 0, sizeof NOTCOL14);
    for (int i = 0; i < NT; i++) {
        bb_set(&VALID, i);
        if (i % 15 != 0) bb_set(&NOTCOL0, i);
        if (i % 15 != 14) bb_set(&NOTCOL14, i);
    }
    bb_set(&STARTS, 0); bb_set(&STARTS, 224);
    inited = 1;
}

/* ---- search state (side-to-move perspective) ---- */
typedef struct {
    BB me, opp;
    int e_me, e_opp, plies, s_me, s_opp;
} SS;

/* ---- transposition table: exact-key open addressing, generation-stamped ---- */
typedef struct { SS key; uint32_t gen; int depth, flag, move; double value; } TTE;
static TTE *TT = 0;
static uint64_t TT_MASK = 0;
static uint32_t TT_GEN = 0;
static void tt_prepare(int node_limit) {
    uint64_t need = 32768;
    while (need < (uint64_t)node_limit * 2 + 1024) need <<= 1;
    if (need - 1 > TT_MASK) {
        free(TT);
        TT = (TTE *)calloc(need, sizeof(TTE));
        TT_MASK = need - 1;
        TT_GEN = 0;
    }
    if (++TT_GEN == 0) { memset(TT, 0, (TT_MASK + 1) * sizeof(TTE)); TT_GEN = 1; }
}

typedef struct {
    int mem_w[NT], mem_c[NT];
    int h[NT];
    BB costbb[10];
    BB open;
    double E, F, Eopp, Fopp, h2c, d1, d2, capw;
    int ext, root_plies, omk, qdepth;
    double cE, cF;
    const double *theta;
    int nodes, node_limit;
    jmp_buf jb;
    int tt_count;
} Ctx;

static int ss_eq(const SS *a, const SS *b) {
    return memcmp(a->me.w, b->me.w, 32) == 0 && memcmp(a->opp.w, b->opp.w, 32) == 0 && a->e_me == b->e_me &&
           a->e_opp == b->e_opp && a->plies == b->plies && a->s_me == b->s_me && a->s_opp == b->s_opp;
}
static uint64_t ss_hash(const SS *s) {
    uint64_t h = 0x9e3779b97f4a7c15ULL;
    for (int k = 0; k < 4; k++) { h ^= s->me.w[k] + 0x9e3779b97f4a7c15ULL + (h << 6) + (h >> 2); }
    for (int k = 0; k < 4; k++) { h ^= s->opp.w[k] + 0xbf58476d1ce4e5b9ULL + (h << 6) + (h >> 2); }
    h ^= (uint64_t)(s->e_me + s->e_opp * 10 + s->plies * 100 + s->s_me * 30000) + (uint64_t)s->s_opp * 10000000ULL;
    h *= 0xff51afd7ed558ccdULL; h ^= h >> 33;
    return h;
}
static TTE *tt_find(Ctx *c, const SS *s) {
    (void)c;
    uint64_t i = ss_hash(s) & TT_MASK;
    while (TT[i].gen == TT_GEN) {
        if (ss_eq(&TT[i].key, s)) return &TT[i];
        i = (i + 1) & TT_MASK;
    }
    return 0;
}
static TTE *tt_slot(Ctx *c, const SS *s) {
    uint64_t i = ss_hash(s) & TT_MASK;
    while (TT[i].gen == TT_GEN) {
        if (ss_eq(&TT[i].key, s)) return &TT[i];
        i = (i + 1) & TT_MASK;
    }
    TT[i].gen = TT_GEN; TT[i].key = *s; c->tt_count++;
    return &TT[i];
}

static int sum_h(const Ctx *c, BB b) {
    int s = 0;
    for (int k = 0; k < 4; k++) {
        uint64_t x = b.w[k];
        while (x) { int t = __builtin_ctzll(x); s += c->h[k * 64 + t]; x &= x - 1; }
    }
    return s;
}

#define NF 17
#define NBK 6
static int bucket_of(int plies) {
    return plies <= 4 ? 0 : plies <= 10 ? 1 : plies <= 24 ? 2 : plies <= 64 ? 3 : plies <= 140 ? 4 : 5;
}
static int sum_w(const Ctx *c, BB b, int cost_lim, const BB *filter) {
    int s = 0;
    for (int k = 0; k < 4; k++) {
        uint64_t x = b.w[k];
        if (filter) x &= filter->w[k];
        while (x) {
            int i = k * 64 + __builtin_ctzll(x); x &= x - 1;
            if (cost_lim < 0 || c->mem_c[i] + 2 <= cost_lim) s += c->mem_w[i];
        }
    }
    return s;
}
static int popc(BB b) { return __builtin_popcountll(b.w[0]) + __builtin_popcountll(b.w[1]) + __builtin_popcountll(b.w[2]) + __builtin_popcountll(b.w[3]); }
/* features from the perspective of player U (bitboard u, energy eu, score su) vs C */
static void features(const Ctx *c, BB u, BB cc, int eu, int ec, int su, int sc, int stm_u, double *f) {
    BB empty = bb_and(bb_not(bb_or(u, cc)), c->open);
    BB nu = nbr(u), nc = nbr(cc);
    BB f1u = bb_and(empty, nu), f1c = bb_and(empty, nc);
    BB f2u = bb_and(bb_and(empty, nbr(f1u)), bb_not(f1u)), f2c = bb_and(bb_and(empty, nbr(f1c)), bb_not(f1c));
    BB xu = bb_and(u, nc), xc = bb_and(cc, nu);
    f[0] = su - sc; f[1] = eu; f[2] = ec;
    f[3] = sum_h(c, f1u); f[4] = sum_h(c, f1c); f[5] = sum_h(c, f2u); f[6] = sum_h(c, f2c);
    f[7] = sum_w(c, f1u, -1, 0); f[8] = sum_w(c, f1c, -1, 0);
    f[9] = popc(f1u); f[10] = popc(f1c);
    f[11] = sum_w(c, xu, -1, 0); f[12] = sum_w(c, xc, -1, 0);
    f[13] = sum_w(c, xc, eu, 0); f[14] = sum_w(c, xu, ec, 0);
    f[15] = stm_u; f[16] = 1;
}
static double eval_fitted(const Ctx *c, const SS *s) {
    int stm_us = ((c->root_plies - s->plies) & 1) == 0;
    double f[NF];
    if (stm_us) features(c, s->me, s->opp, s->e_me, s->e_opp, s->s_me, s->s_opp, 1, f);
    else features(c, s->opp, s->me, s->e_opp, s->e_me, s->s_opp, s->s_me, 0, f);
    const double *t = c->theta + bucket_of(s->plies) * NF;
    double v = 0;
    for (int k = 0; k < NF; k++) v += t[k] * f[k];
    return stm_us ? v : -v;
}

static double evaluate(const Ctx *c, const SS *s) {
    int diff = s->s_me - s->s_opp;
    int base = diff * 100;
    if (s->plies == 0) {
        int v = diff > 0 ? base + 1000000 : (diff < 0 ? base - 1000000 : 0);
        return (double)v;
    }
    double pl = (double)s->plies;
    if (c->ext == 2) return eval_fitted(c, s);
    if (c->ext) {
        double a = pl / c->d1; if (1.0 <= a) a = 1.0;
        BB empty = bb_and(bb_not(bb_or(s->me, s->opp)), c->open);
        BB f1m = bb_and(empty, nbr(s->me));
        BB f1o = bb_and(empty, nbr(s->opp));
        BB f2m = bb_and(bb_and(empty, nbr(f1m)), bb_not(f1m));
        BB f2o = bb_and(bb_and(empty, nbr(f1o)), bb_not(f1o));
        double b = pl / c->d2; if (1.0 <= b) b = 1.0;
        double fm = sum_h(c, f1m) + c->h2c * sum_h(c, f2m);
        double fo = sum_h(c, f1o) + c->h2c * sum_h(c, f2o);
        double v = b * (c->F * fm - c->Fopp * fo) + a * (c->E * s->e_me - c->Eopp * s->e_opp) + (double)base;
        if (c->capw != 0.0) { /* exposure: own tiles the opponent could capture next */
            BB ex = bb_and(s->me, nbr(s->opp)), ex2 = bb_and(s->opp, nbr(s->me));
            double xm = 0, xo = 0;
            for (int k = 0; k < 4; k++) {
                uint64_t q = ex.w[k];
                while (q) { int i = k * 64 + __builtin_ctzll(q); q &= q - 1; xm += c->mem_w[i]; }
                q = ex2.w[k];
                while (q) { int i = k * 64 + __builtin_ctzll(q); q &= q - 1; xo += c->mem_w[i]; }
            }
            v += b * c->capw * (xo - xm);
        }
        return v;
    }
    double a = pl / 10.0; if (1.0 <= a) a = 1.0;
    BB empty = bb_and(bb_not(bb_or(s->me, s->opp)), c->open);
    BB f1m = bb_and(empty, nbr(s->me));
    BB f1o = bb_and(empty, nbr(s->opp));
    int h1m = sum_h(c, f1m), h1o = sum_h(c, f1o);
    BB f2m = bb_and(bb_and(empty, nbr(f1m)), bb_not(f1m));
    BB f2o = bb_and(bb_and(empty, nbr(f1o)), bb_not(f1o));
    int h2m = sum_h(c, f2m), h2o = sum_h(c, f2o);
    double b = pl / 24.0; if (1.0 <= b) b = 1.0;
    double front = (double)(h2m - h2o) * 0.35 + (double)(h1m - h1o);
    return b * c->F * front + a * c->E * (double)(s->e_me - s->e_opp) + (double)base;
}

typedef struct { int first, second, key; unsigned char nothash; } MV;

static int mv_less(const MV *a, const MV *b) {
    if (a->nothash != b->nothash) return a->nothash < b->nothash;
    if (a->key != b->key) return a->key < b->key;
    if (a->second != b->second) return a->second < b->second;
    return a->first < b->first;
}
static void sort_moves(MV *m, int n) { /* insertion sort: strict total order */
    for (int i = 1; i < n; i++) {
        MV x = m[i]; int j = i - 1;
        while (j >= 0 && mv_less(&x, &m[j])) { m[j + 1] = m[j]; j--; }
        m[j + 1] = x;
    }
}
static int tile_key(const Ctx *c, int i, int cap) {
    return (c->mem_c[i] + cap * 2) * 16 + (cap + 1) * c->mem_w[i] * -10;
}
static int rest_key(int e) { return e < 7 ? -44 : e * 16 - 140; }

/* inner-node move generation */
static int gen_moves(const Ctx *c, const SS *s, int hash, MV *out) {
    int n = 0, e = s->e_me;
    BB T;
    int ei = e > 9 ? 9 : e;
    if (e < 0) memset(&T, 0, sizeof T);
    else T = bb_and(bb_not(s->opp), c->costbb[ei]);
    if (e >= 2) {
        int e2 = e - 2 > 9 ? 9 : e - 2;
        T = bb_or(T, bb_and(s->opp, c->costbb[e2]));
    }
    BB cand = bb_and(bb_and(c->open, nbr(s->me)), bb_and(bb_not(s->me), T));
    for (int k = 0; k < 4; k++) {
        uint64_t x = cand.w[k];
        while (x) {
            int i = k * 64 + __builtin_ctzll(x); x &= x - 1;
            int cap = bb_get(&s->opp, i);
            out[n].first = i; out[n].second = i; out[n].key = tile_key(c, i, cap); out[n].nothash = (hash != i); n++;
        }
    }
    out[n].first = -1; out[n].second = 225; out[n].key = rest_key(e); out[n].nothash = (hash != -1); n++;
    sort_moves(out, n);
    return n;
}

static void apply(const Ctx *c, const SS *s, int m, SS *o) {
    if (m < 0) {
        int e = s->e_me + 3; if (e > 9) e = 9;
        o->me = s->opp; o->opp = s->me;
        o->e_me = s->e_opp; o->e_opp = e;
        o->s_me = s->s_opp; o->s_opp = s->s_me;
    } else {
        int cap = bb_get(&s->opp, m);
        int w = c->mem_w[m], cost = c->mem_c[m];
        BB me = s->me, opp = s->opp;
        bb_set(&me, m); bb_clr(&opp, m);
        o->me = opp; o->opp = me;
        o->e_me = s->e_opp; o->e_opp = s->e_me - (cost + cap * 2);
        o->s_me = cap ? s->s_opp - w : s->s_opp; o->s_opp = s->s_me + w;
    }
    o->plies = s->plies - 1;
}

/* root moves come from the observation's legal list */
static MV root_moves_buf[260];
static int root_n;

static double qsearch(Ctx *c, double alpha, double beta, const SS *s, int qd) {
    c->nodes++;
    if (c->nodes > c->node_limit) longjmp(c->jb, 1);
    double stand = evaluate(c, s);
    if (s->plies == 0 || qd == 0) return stand;
    if (stand >= beta) return stand;
    if (stand > alpha) alpha = stand;
    int e = s->e_me;
    if (e < 2) return stand;
    int e2 = e - 2 > 9 ? 9 : e - 2;
    BB cand = bb_and(bb_and(c->open, nbr(s->me)), bb_and(s->opp, c->costbb[e2]));
    double best = stand;
    for (int k = 0; k < 4; k++) {
        uint64_t x = cand.w[k];
        while (x) {
            int i = k * 64 + __builtin_ctzll(x); x &= x - 1;
            SS ch; apply(c, s, i, &ch);
            double v = -qsearch(c, -beta, -alpha, &ch, qd - 1);
            if (v > best) best = v;
            if (v > alpha) alpha = v;
            if (alpha >= beta) return best;
        }
    }
    return best;
}

static double search(Ctx *c, double alpha, double beta, const SS *s, int depth, int root) {
    c->nodes++;
    if (c->nodes > c->node_limit) longjmp(c->jb, 1);
    if (s->plies == 0) return evaluate(c, s);
    if (depth == 0) {
        if (c->qdepth > 0 && c->ext == 2) { c->nodes--; return qsearch(c, alpha, beta, s, c->qdepth); }
        return evaluate(c, s);
    }
    double a = alpha, b = beta;
    int hash = -2;
    TTE *e = tt_find(c, s);
    if (e) {
        if (e->depth < depth) hash = e->move;
        else {
            double v = e->value;
            if (e->flag == 0) return v;
            if (e->flag == 1) a = (v <= alpha) ? alpha : v;
            else b = (beta <= v) ? beta : v;
            if (!(a < b)) return v;
            hash = e->move;
        }
    }
    MV mv[260];
    int n;
    if (root) {
        n = root_n;
        memcpy(mv, root_moves_buf, sizeof(MV) * n);
        for (int i = 0; i < n; i++) mv[i].nothash = (hash != mv[i].first);
        sort_moves(mv, n);
    } else n = gen_moves(c, s, hash, mv);
    if (c->omk > 0 && c->ext == 2 && ((c->root_plies - s->plies) & 1) == 1 && n > c->omk) {
        /* champion to move: keep its top-k moves by its own 1-ply evaluation */
        double sc[260]; int idx[260];
        Ctx tmp_unused; (void)tmp_unused;
        for (int i = 0; i < n; i++) {
            SS ch; apply(c, s, mv[i].first, &ch);
            /* champion eval of ch from the champion's perspective = -(its eval with ch's side to move) */
            Ctx *cc = (Ctx *)c;
            int ext0 = cc->ext; double E0 = cc->E, F0 = cc->F;
            cc->ext = 0; cc->E = c->cE; cc->F = c->cF;
            sc[i] = -evaluate(cc, &ch);
            cc->ext = ext0; cc->E = E0; cc->F = F0;
            idx[i] = i;
        }
        for (int i = 1; i < n; i++) { int x = idx[i]; int j = i - 1; while (j >= 0 && sc[idx[j]] < sc[x]) { idx[j + 1] = idx[j]; j--; } idx[j + 1] = x; }
        int keep[260]; memset(keep, 0, sizeof keep);
        for (int i = 0; i < c->omk; i++) keep[idx[i]] = 1;
        int m2 = 0; for (int i = 0; i < n; i++) if (keep[i]) mv[m2++] = mv[i];
        n = m2;
    }
    double best = NEG_INF; int bestm = -1;
    for (int i = 0; i < n; i++) {
        SS ch; apply(c, s, mv[i].first, &ch);
        double v = -search(c, -b, -a, &ch, depth - 1, 0);
        double a2 = (v <= a) ? a : v;
        if (best < v) { best = v; bestm = mv[i].first; }
        if (!(a2 < b)) break;
        a = a2;
    }
    TTE *t = tt_slot(c, s);
    t->depth = depth;
    t->flag = (alpha < best) ? (beta <= best ? 1 : 0) : 2;
    t->move = bestm;
    t->value = best;
    return best;
}

static Ctx CTX;
static const double *EXT_P = 0; /* set by search_decide_ext */
static const double *THETA = 0; /* set by search_decide_fit */
static int OMK = 0; static double OM_E = 160, OM_F = 9;
static int QDEPTH = 0;
void set_qdepth(int q) { QDEPTH = q; }
void set_opponent_model(int k, double E, double F) { OMK = k; OM_E = E; OM_F = F; }
double LAST_ROOT_VALUE;

/*
 * Champion decision.
 *  blocked[i], w[i], c[i]: true terrain (only the champion-visible part matters)
 *  owner[i]: true owner 0/1/-1
 *  energy[2], score[2], remaining: public state; seat: champion seat; profile 0..2
 *  mem_owner/mem_w/mem_c: champion memory (in/out); init -3/5/3 with starts set
 *  out_info (optional, 4 ints): nodes used, completed depth, root move count, tt size
 * Returns -1 (rest) or a tile index.
 */
int search_decide(const int *blocked, const int *w, const int *c, const int *owner, const int *energy,
                  const int *score, int remaining, int seat, double E, double F, int node_limit, int max_depth,
                  int *mem_owner, int *mem_w, int *mem_c, int *out_info) {
    init_masks();
    Ctx *x = &CTX;
    BB own; memset(&own, 0, sizeof own);
    for (int i = 0; i < NT; i++) if (owner[i] == seat) bb_set(&own, i);
    BB vis = bb_or(own, nbr(own));
    for (int i = 0; i < NT; i++) {
        if (bb_get(&vis, i)) {
            mem_owner[i] = blocked[i] ? -2 : (owner[i] == 0 ? 0 : (owner[i] == 1 ? 1 : -1));
            mem_w[i] = w[i]; mem_c[i] = c[i];
        } else if (mem_owner[i] == seat) mem_owner[i] = 1 - seat;
    }
    BB blk; memset(&blk, 0, sizeof blk);
    for (int k = 0; k < 10; k++) memset(&x->costbb[k], 0, sizeof(BB));
    for (int i = 0; i < NT; i++) {
        if (mem_owner[i] == -2) bb_set(&blk, i);
        int hv = EXT_P ? (int)(EXT_P[4] * mem_w[i] - EXT_P[5] * mem_c[i]) : mem_w[i] * 3 - mem_c[i] * 4;
        if (hv < 0) hv = 0;
        x->h[i] = hv;
        x->mem_w[i] = mem_w[i]; x->mem_c[i] = mem_c[i];
        int ci = mem_c[i];
        if (ci < 10) { if (ci < 0) ci = 0; for (int k = ci; k < 10; k++) bb_set(&x->costbb[k], i); }
    }
    x->open = bb_and(bb_not(bb_or(STARTS, blk)), VALID);
    x->E = E; x->F = F; x->node_limit = node_limit; x->ext = 0;
    x->root_plies = remaining;
    x->omk = OMK; x->cE = OM_E; x->cF = OM_F; x->qdepth = QDEPTH;
    if (THETA) { x->ext = 2; x->theta = THETA; }
    else if (EXT_P) {
        x->ext = 1; x->E = EXT_P[0]; x->Eopp = EXT_P[1]; x->F = EXT_P[2]; x->Fopp = EXT_P[2] * EXT_P[9];
        x->h2c = EXT_P[3]; x->d1 = EXT_P[6]; x->d2 = EXT_P[7]; x->capw = EXT_P[8];
    }
    SS r; memset(&r, 0, sizeof r);
    for (int i = 0; i < NT; i++) {
        if (mem_owner[i] == seat) bb_set(&r.me, i);
        else if (mem_owner[i] == 1 - seat) bb_set(&r.opp, i);
    }
    r.e_me = energy[seat]; r.e_opp = energy[1 - seat];
    r.plies = remaining; r.s_me = score[seat]; r.s_opp = score[1 - seat];
    /* legal list from the true state */
    BB opp_true; memset(&opp_true, 0, sizeof opp_true);
    BB blk_true; memset(&blk_true, 0, sizeof blk_true);
    for (int i = 0; i < NT; i++) {
        if (owner[i] == 1 - seat) bb_set(&opp_true, i);
        if (blocked[i]) bb_set(&blk_true, i);
    }
    BB lc = bb_and(bb_not(bb_or(bb_or(own, blk_true), STARTS)), nbr(own));
    root_n = 0;
    for (int k = 0; k < 4; k++) {
        uint64_t q = lc.w[k];
        while (q) {
            int i = k * 64 + __builtin_ctzll(q); q &= q - 1;
            int capt = bb_get(&opp_true, i);
            if (c[i] + capt * 2 <= energy[seat]) {
                int cap = bb_get(&r.opp, i);
                MV *m = &root_moves_buf[root_n++];
                m->first = i; m->second = i; m->key = tile_key(x, i, cap); m->nothash = 1;
            }
        }
    }
    MV *m = &root_moves_buf[root_n++];
    m->first = -1; m->second = 225; m->key = rest_key(r.e_me); m->nothash = 1;
    MV tmp[260]; memcpy(tmp, root_moves_buf, sizeof(MV) * root_n); sort_moves(tmp, root_n);
    volatile int best = tmp[0].first;
    tt_prepare(node_limit); x->tt_count = 0;
    x->nodes = 0;
    int maxd = remaining < max_depth ? remaining : max_depth;
    volatile int done = 0;
    for (int d = 1; d <= maxd; d++) {
        if (setjmp(x->jb)) break;
        search(x, NEG_INF, POS_INF, &r, d, 1);
        TTE *t = tt_find(x, &r);
        if (t) { best = t->move; LAST_ROOT_VALUE = t->value; }
        done = d;
    }
    if (out_info) { out_info[0] = x->nodes; out_info[1] = done; out_info[2] = root_n; out_info[3] = x->tt_count; }
    return best;
}

int champ_decide(const int *blocked, const int *w, const int *c, const int *owner, const int *energy,
                 const int *score, int remaining, int seat, int profile, int *mem_owner, int *mem_w, int *mem_c,
                 int *out_info) {
    return search_decide(blocked, w, c, owner, energy, score, remaining, seat, E_PROF[profile], F_PROF[profile],
                         2048, 4, mem_owner, mem_w, mem_c, out_info);
}

/* Our searcher with a tunable evaluation. p: E_me, E_opp, F, h2c, ha, hb, d1, d2, capw, Fopp_mult */
int search_decide_ext(const int *blocked, const int *w, const int *c, const int *owner, const int *energy,
                      const int *score, int remaining, int seat, const double *p, int node_limit, int max_depth,
                      int *mem_owner, int *mem_w, int *mem_c) {
    EXT_P = p;
    int a = search_decide(blocked, w, c, owner, energy, score, remaining, seat, 0, 0, node_limit, max_depth,
                          mem_owner, mem_w, mem_c, 0);
    EXT_P = 0;
    return a;
}

/* Our searcher with the fitted linear evaluation. hp: (ha, hb) for h = max(0, ha*w - hb*c). */
static double HP_FIT[10];
int search_decide_fit(const int *blocked, const int *w, const int *c, const int *owner, const int *energy,
                      const int *score, int remaining, int seat, const double *theta, double ha, double hb,
                      int node_limit, int max_depth, int *mem_owner, int *mem_w, int *mem_c) {
    memset(HP_FIT, 0, sizeof HP_FIT); HP_FIT[4] = ha; HP_FIT[5] = hb;
    EXT_P = HP_FIT; THETA = theta;
    int a = search_decide(blocked, w, c, owner, energy, score, remaining, seat, 0, 0, node_limit, max_depth,
                          mem_owner, mem_w, mem_c, 0);
    EXT_P = 0; THETA = 0;
    return a;
}

/* Features (our perspective) of the root position and of the position after `move`
 * (memory must already be updated for this observation). Returns bucket of root. */
int root_features(const int *blocked, const int *w, const int *c, const int *owner, const int *energy,
                  const int *score, int remaining, int seat, double ha, double hb, const int *mem_owner,
                  const int *mem_w, const int *mem_c, int move, double *f_root, double *f_child) {
    init_masks();
    Ctx *x = &CTX;
    (void)blocked; (void)w; (void)c; (void)owner;
    BB blk; memset(&blk, 0, sizeof blk);
    for (int i = 0; i < NT; i++) {
        if (mem_owner[i] == -2) bb_set(&blk, i);
        int hv = (int)(ha * mem_w[i] - hb * mem_c[i]); x->h[i] = hv < 0 ? 0 : hv;
        x->mem_w[i] = mem_w[i]; x->mem_c[i] = mem_c[i];
    }
    x->open = bb_and(bb_not(bb_or(STARTS, blk)), VALID);
    SS r; memset(&r, 0, sizeof r);
    for (int i = 0; i < NT; i++) {
        if (mem_owner[i] == seat) bb_set(&r.me, i);
        else if (mem_owner[i] == 1 - seat) bb_set(&r.opp, i);
    }
    r.e_me = energy[seat]; r.e_opp = energy[1 - seat]; r.plies = remaining; r.s_me = score[seat]; r.s_opp = score[1 - seat];
    features(x, r.me, r.opp, r.e_me, r.e_opp, r.s_me, r.s_opp, 1, f_root);
    SS ch; apply(x, &r, move, &ch);
    features(x, ch.opp, ch.me, ch.e_opp, ch.e_me, ch.s_opp, ch.s_me, 0, f_child);
    return bucket_of(remaining);
}
