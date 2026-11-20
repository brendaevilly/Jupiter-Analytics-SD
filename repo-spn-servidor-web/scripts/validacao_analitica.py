#!/usr/bin/env python3
"""Solucao analitica M/M/c/K para conferir os resultados do Jupiter.
NAO substitui a simulacao: serve so para validar o modelo (os numeros do artigo vem do Jupiter)."""
import csv, math

def mmck(lam, s, c, K):
    mu = 1.0 / s
    a = lam / mu
    w = [a**n / math.factorial(n) if n <= c else a**c / math.factorial(c) * (a / c)**(n - c) for n in range(K + 1)]
    p0 = 1.0 / sum(w)
    p = [x * p0 for x in w]
    pk = p[K]
    lam_eff = lam * (1 - pk)
    L = sum(n * p[n] for n in range(K + 1))
    Lq = sum((n - c) * p[n] for n in range(c + 1, K + 1))
    busy = lam_eff / mu
    return {"TP_req_s": lam_eff, "DP_pct": 100 * pk, "MRT_ms": 1000 * L / lam_eff,
            "MQT_ms": 1000 * Lq / lam_eff, "U_pct": 100 * busy / c, "MPT_ms": 1000 * s}

S, C0, K0, L0 = 0.1, 4, 16, 30
rows = []
for lam in (10, 20, 30, 40, 50):
    rows.append(("E1", f"lambda={lam}", lam, C0, K0))
for c in (2, 4, 6):
    rows.append(("E2", f"C={c}", L0, c, K0))
for k in (8, 16, 24):
    rows.append(("E3", f"K={k}", L0, C0, k))
for lam, c in ((15, 2), (30, 4), (45, 6)):
    rows.append(("E4", f"lambda={lam},C={c}", lam, c, K0))

import os
with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "resultados", "validacao_analitica.csv"), "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["exp", "cenario", "lambda_req_s", "C", "K", "TP_req_s", "DP_pct", "MRT_ms", "MQT_ms", "U_pct", "MPT_ms"])
    for e, nome, lam, c, k in rows:
        r = mmck(lam, S, c, k)
        w.writerow([e, nome, lam, c, k] + [f"{r[m]:.4f}" for m in ("TP_req_s", "DP_pct", "MRT_ms", "MQT_ms", "U_pct", "MPT_ms")])
        print(f"{e} {nome:18s} TP={r['TP_req_s']:6.2f} DP={r['DP_pct']:6.2f}% MRT={r['MRT_ms']:7.1f}ms MQT={r['MQT_ms']:7.1f}ms U={r['U_pct']:5.1f}%")
