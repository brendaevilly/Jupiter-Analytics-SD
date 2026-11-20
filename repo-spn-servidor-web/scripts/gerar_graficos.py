#!/usr/bin/env python3
"""Gera figE1, figE1b, figE2, figE3, figE4 (.pdf) e tabela_resultados.tex a partir de resultados/resultados_consolidados.csv"""
import csv, sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

import os
HERE = os.path.dirname(os.path.abspath(__file__))
CSV = os.path.join(HERE, "..", "resultados", "resultados_consolidados.csv")
OUT = os.path.join(HERE, "..", "figuras")
os.makedirs(OUT, exist_ok=True)
rows = list(csv.DictReader(open(CSV, newline="")))
metrics = ["TP", "DP", "MRT", "MQT", "U"]

faltando = [f"{r['exp']} {r['cenario']}: {m}" for r in rows for m in metrics if not r[m].strip()]
if faltando:
    sys.exit("Preencha com os resultados do Jupiter antes de gerar:\n  " + "\n  ".join(faltando))

def num(r, k):
    return float(r[k]) if r.get(k, "").strip() else 0.0

# conferencia de conservacao: vazao + taxa de perda = taxa de chegada
for r in rows:
    if r.get("LOSS_RATE", "").strip():
        lam, tp, loss = float(r["lambda"]), float(r["TP"]), float(r["LOSS_RATE"])
        if abs(tp + loss - lam) / lam > 0.03:
            print(f"AVISO: {r['exp']} {r['cenario']}: TP+LOSS={tp+loss:.2f} difere de lambda={lam}")

plt.rcParams.update({"font.size": 8, "axes.labelsize": 8, "legend.fontsize": 7, "font.family": "serif"})
comma = FuncFormatter(lambda v, _: f"{v:g}".replace(".", ","))

def twin(exp, xkey, xlabel, ykeyL, ylabL, ykeyR, ylabR, fname, xs_label=None):
    rs = [r for r in rows if r["exp"] == exp]
    xs = [xs_label(r) if xs_label else float(r[xkey]) for r in rs]
    fig, a1 = plt.subplots(figsize=(3.4, 2.3))
    a2 = a1.twinx()
    pos = list(range(len(rs))) if xs_label else xs
    l1 = a1.errorbar(pos, [float(r[ykeyL]) for r in rs], yerr=[num(r, ykeyL + "_ci") for r in rs],
                     marker="o", color="tab:blue", capsize=2, label=ylabL)
    l2 = a2.errorbar(pos, [float(r[ykeyR]) for r in rs], yerr=[num(r, ykeyR + "_ci") for r in rs],
                     marker="s", ls="--", color="tab:red", capsize=2, label=ylabR)
    a1.set_xlabel(xlabel); a1.set_ylabel(ylabL); a2.set_ylabel(ylabR)
    if xs_label: a1.set_xticks(pos); a1.set_xticklabels(xs)
    else: a1.set_xticks(xs)
    for a in (a1, a2): a.yaxis.set_major_formatter(comma)
    a1.grid(alpha=0.3)
    a1.legend([l1, l2], [ylabL, ylabR], loc="upper left", frameon=False)
    fig.tight_layout(); fig.savefig(os.path.join(OUT, fname)); plt.close(fig)

twin("E1", "lambda", "Taxa de chegada (req/s)", "MRT", "Tempo médio de resposta (ms)", "DP", "Prob. de descarte (%)", "figE1.pdf")
twin("E1", "lambda", "Taxa de chegada (req/s)", "TP", "Vazão (req/s)", "U", "Utilização (%)", "figE1b.pdf")
twin("E2", "C", "Número de servidores", "MRT", "Tempo médio de resposta (ms)", "U", "Utilização (%)", "figE2.pdf")
twin("E3", "K", "Capacidade do sistema (requisições)", "MQT", "Tempo médio de fila (ms)", "DP", "Prob. de descarte (%)", "figE3.pdf")
twin("E4", None, "Cenário (taxa em req/s, servidores)", "TP", "Vazão (req/s)", "MRT", "Tempo médio de resposta (ms)", "figE4.pdf",
     xs_label=lambda r: f"({int(float(r['lambda']))}, {r['C']})")

def cell(r, m, d):
    v = float(r[m]); ci = num(r, m + "_ci")
    s = f"{v:.{d}f}".replace(".", ",")
    return s + (f" $\\pm$ {ci:.{d}f}".replace(".", ",") if ci else "")

with open(os.path.join(OUT, "tabela_resultados.tex"), "w", encoding="utf-8") as f:
    f.write("\\begin{tabular}{|c|c|c|c|c|c|c|c|c|}\n\\hline\n")
    f.write("\\textbf{Exp.} & \\textbf{$\\lambda$ (req/s)} & \\textbf{$C$} & \\textbf{$K$} & \\textbf{TP (req/s)} & \\textbf{MRT (ms)} & \\textbf{MQT (ms)} & \\textbf{U (\\%)} & \\textbf{DP (\\%)} \\\\\n\\hline\n")
    for r in rows:
        f.write(f"{r['exp']} & {int(float(r['lambda']))} & {r['C']} & {r['K']} & {cell(r,'TP',2)} & {cell(r,'MRT',1)} & {cell(r,'MQT',1)} & {cell(r,'U',1)} & {cell(r,'DP',2)} \\\\\n")
    f.write("\\hline\n\\end{tabular}\n")
print("Gerados: figE1.pdf figE1b.pdf figE2.pdf figE3.pdf figE4.pdf tabela_resultados.tex")
