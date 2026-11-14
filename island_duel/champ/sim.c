/* Game simulator + opponent-model (OM) search on top of the champion clone.
 * Build: gcc -O2 -shared -fPIC -o libsim.so sim.c
 */
#include "champ.c"

typedef struct {
    int blocked[NT], w[NT], c[NT], owner[NT];
    int energy[2], score[2], remaining, cur;
    int cseat, cprof;
    int mo[NT], mw[NT], mc[NT];
} Game;

int game_size(void) { return (int)sizeof(Game); }

void g_init(Game *g, const int *blocked, const int *w, const int *c, int cseat, int cprof) {
    init_masks();
    memcpy(g->blocked, blocked, sizeof g->blocked);
    memcpy(g->w, w, sizeof g->w);
    memcpy(g->c, c, sizeof g->c);
    for (int i = 0; i < NT; i++) { g->owner[i] = -1; g->mo[i] = -3; g->mw[i] = 5; g->mc[i] = 3; }
    g->owner[0] = 0; g->owner[224] = 1;
    g->mo[0] = 0; g->mo[224] = 1; g->mw[0] = g->mw[224] = g->mc[0] = g->mc[224] = 0;
    g->energy[0] = g->energy[1] = 6; g->score[0] = g->score[1] = 0;
    g->remaining = 256; g->cur = 0; g->cseat = cseat; g->cprof = cprof;
}

static inline int adj_own(const Game *g, int i, int p) {
    int r = i / 15, q = i % 15;
    return (r > 0 && g->owner[i - 15] == p) || (r < 14 && g->owner[i + 15] == p) ||
           (q > 0 && g->owner[i - 1] == p) || (q < 14 && g->owner[i + 1] == p);
}

int g_legal(const Game *g, int *out) {
    int p = g->cur, n = 0;
    out[n++] = -1;
    for (int i = 0; i < NT; i++) {
        if (i == 0 || i == 224 || g->blocked[i] || g->owner[i] == p) continue;
        if (!adj_own(g, i, p)) continue;
        int cost = g->c[i] + (g->owner[i] == 1 - p ? 2 : 0);
        if (cost <= g->energy[p]) out[n++] = i;
    }
    return n;
}

void g_apply(Game *g, int a) {
    int p = g->cur;
    if (a < 0) { g->energy[p] += 3; if (g->energy[p] > 9) g->energy[p] = 9; }
    else {
        int cap = g->owner[a] == 1 - p;
        g->energy[p] -= g->c[a] + 2 * cap;
        g->score[p] += g->w[a];
        if (cap) g->score[1 - p] -= g->w[a];
        g->owner[a] = p;
    }
    g->cur = 1 - p;
    g->remaining--;
}

int g_champ(Game *g, int budget) {
    return search_decide(g->blocked, g->w, g->c, g->owner, g->energy, g->score, g->remaining, g->cseat,
                         E_PROF[g->cprof], F_PROF[g->cprof], budget, 4, g->mo, g->mw, g->mc, 0);
}

/* full-information negamax decision for the side to move (the clone's search, own weights) */
int g_negamax(Game *g, double E, double F, int budget, int depth) {
    int p = g->cur;
    int mo[NT], mw[NT], mc[NT];
    for (int i = 0; i < NT; i++) {
        mo[i] = g->blocked[i] ? -2 : g->owner[i];
        mw[i] = (i == 0 || i == 224) ? 0 : g->w[i];
        mc[i] = (i == 0 || i == 224) ? 0 : g->c[i];
    }
    return search_decide(g->blocked, g->w, g->c, g->owner, g->energy, g->score, g->remaining, p, E, F, budget,
                         depth, mo, mw, mc, 0);
}

/* leaf evaluation for player p with true terrain (same form as the champion's) */
static int H_TRUE[NT];
double g_eval(const Game *g, int p, double E, double F, double capw) {
    int diff = g->score[p] - g->score[1 - p];
    if (g->remaining == 0) return diff > 0 ? 1e6 + 100.0 * diff : (diff < 0 ? -1e6 + 100.0 * diff : 0.0);
    BB me, op, blk; memset(&me, 0, sizeof me); memset(&op, 0, sizeof op); memset(&blk, 0, sizeof blk);
    for (int i = 0; i < NT; i++) {
        if (g->owner[i] == p) bb_set(&me, i); else if (g->owner[i] == 1 - p) bb_set(&op, i);
        if (g->blocked[i]) bb_set(&blk, i);
        int hv = 3 * g->w[i] - 4 * g->c[i]; H_TRUE[i] = hv < 0 ? 0 : hv;
    }
    BB open = bb_and(bb_not(bb_or(STARTS, blk)), VALID);
    BB empty = bb_and(bb_not(bb_or(me, op)), open);
    Ctx tmp; /* only h used */
    memcpy(tmp.h, H_TRUE, sizeof H_TRUE);
    BB f1m = bb_and(empty, nbr(me)), f1o = bb_and(empty, nbr(op));
    BB f2m = bb_and(bb_and(empty, nbr(f1m)), bb_not(f1m)), f2o = bb_and(bb_and(empty, nbr(f1o)), bb_not(f1o));
    double front = 0.35 * (sum_h(&tmp, f2m) - sum_h(&tmp, f2o)) + (sum_h(&tmp, f1m) - sum_h(&tmp, f1o));
    /* exposure: own tiles adjacent to the enemy (capturable), weighted by value */
    double expo = 0;
    if (capw != 0) {
        BB ex = bb_and(me, nbr(op)), ex2 = bb_and(op, nbr(me));
        for (int i = 0; i < NT; i++) {
            if (bb_get(&ex, i)) expo -= g->w[i];
            if (bb_get(&ex2, i)) expo += g->w[i];
        }
    }
    double pl = g->remaining;
    double a = pl / 10.0; if (a > 1) a = 1;
    double b = pl / 24.0; if (b > 1) b = 1;
    return b * F * front + a * E * (g->energy[p] - g->energy[1 - p]) + 100.0 * diff + b * capw * expo;
}

typedef struct { double E, F, capw; int budget, width; } OMP;
static Game STK[8];

static double om(Game *g, int depth, int p, const OMP *o);

static double om_child(const Game *g, int m, int depth, int p, const OMP *o) {
    Game *h = &STK[depth];
    *h = *g;
    g_apply(h, m);
    if (h->remaining > 0) g_apply(h, g_champ(h, o->budget));
    return om(h, depth - 1, p, o);
}

static double om(Game *g, int depth, int p, const OMP *o) {
    if (g->remaining == 0 || depth == 0) return g_eval(g, p, o->E, o->F, o->capw);
    int mv[260]; int n = g_legal(g, mv);
    double best = -1e300;
    for (int i = 0; i < n; i++) {
        double v = om_child(g, mv[i], depth, p, o);
        if (v > best) best = v;
    }
    return best;
}

/* OM search: our move -> exact champion reply, depth our-moves deep. Returns best move;
 * vals (optional, size 260) receives the root move values in g_legal order. */
int g_om(Game *g, int depth, double E, double F, double capw, int budget, double *vals, int *moves, int *nmoves) {
    OMP o = {E, F, capw, budget, 0};
    int p = g->cur;
    int mv[260]; int n = g_legal(g, mv);
    double best = -1e300; int bm = -1;
    for (int i = 0; i < n; i++) {
        double v = om_child(g, mv[i], depth, p, &o);
        if (vals) vals[i] = v;
        if (moves) moves[i] = mv[i];
        if (v > best) { best = v; bm = mv[i]; }
    }
    if (nmoves) *nmoves = n;
    return bm;
}

/* Hybrid: our move -> exact champion reply -> our negamax value (depth/budget) of the result. */
int g_om_nm(Game *g, double E, double F, int budget, int depth, double *vals, int *moves, int *nmoves) {
    int p = g->cur;
    int mv[260]; int n = g_legal(g, mv);
    double best = -1e300; int bm = -1;
    for (int i = 0; i < n; i++) {
        Game h = *g;
        g_apply(&h, mv[i]);
        double v;
        if (h.remaining > 0) g_apply(&h, g_champ(&h, 2048));
        if (h.remaining == 0) v = g_eval(&h, p, E, F, 0);
        else { g_negamax(&h, E, F, budget, depth); v = LAST_ROOT_VALUE; }
        if (vals) vals[i] = v;
        if (moves) moves[i] = mv[i];
        if (v > best) { best = v; bm = mv[i]; }
    }
    if (nmoves) *nmoves = n;
    return bm;
}

/* Play `first` for the side to move, then negamax (us) vs exact champion to the end.
 * Returns the final margin for the side that played `first`. */
int g_rollout(const Game *g0, int first, double E, double F, int budget, int depth) {
    Game h = *g0;
    int p = h.cur;
    g_apply(&h, first);
    while (h.remaining > 0) {
        int a = (h.cur == p) ? g_negamax(&h, E, F, budget, depth) : g_champ(&h, 2048);
        g_apply(&h, a);
    }
    return h.score[p] - h.score[1 - p];
}

/* Truncated rollout: like g_rollout but stops after H plies; returns eval/100 for the mover. */
double g_rollout_h(const Game *g0, int first, double E, double F, int budget, int depth, int H) {
    Game h = *g0;
    int p = h.cur;
    g_apply(&h, first);
    int k = 1;
    while (h.remaining > 0 && k < H) {
        int a = (h.cur == p) ? g_negamax(&h, E, F, budget, depth) : g_champ(&h, 2048);
        g_apply(&h, a);
        k++;
    }
    if (h.remaining == 0) return h.score[p] - h.score[1 - p];
    return g_eval(&h, p, E, F, 0) / 100.0;
}
