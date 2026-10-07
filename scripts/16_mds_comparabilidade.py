"""16_mds_comparabilidade.py
Confere se as duas contagens de pessoas usadas para 2022 e 2026 medem a mesma coisa.
2022 (Auxilio Brasil): cadunico_tot_pes_pbf_i. 2026 (Bolsa Familia): qtd_pessoas_beneficiarias_bolsa_familia_i.
Em mar/2023 a jun/2024 a API do MI Social traz os dois campos no mesmo mes; comparamos municipio a municipio.
Saidas: data/raw/mds/misocial_comparab_{aaaamm}.csv (nao sobrescreve), logs/16_mds_comparabilidade_log.json
Uso: python -P scripts/16_mds_comparabilidade.py <raiz>
"""
import csv, json, sys, time, urllib.parse, urllib.request
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(sys.argv[1])
API = "https://aplicacoes.mds.gov.br/sagi/servicos/misocial"
FL = ["anomes_s", "codigo_ibge", "populacao_censo_2022_i", "cadunico_tot_pes_pbf_i",
      "qtd_pessoas_beneficiarias_bolsa_familia_i", "qtd_familias_beneficiarias_bolsa_familia_i"]
MESES = ["202303", "202306", "202312"]

res = {"campos": FL, "meses": {}}
for am in MESES:
    fp = ROOT / f"data/raw/mds/misocial_comparab_{am}.csv"
    if not fp.exists():
        rows, start = [], 0
        while True:
            q = urllib.parse.urlencode({"q": "*:*", "fq": f"anomes_s:{am}", "fl": ",".join(FL), "wt": "json",
                                        "rows": 1000, "start": start, "sort": "codigo_ibge asc"})
            for t in range(4):
                try:
                    with urllib.request.urlopen(f"{API}?{q}", timeout=180) as r:
                        resp = json.load(r)["response"]
                    break
                except Exception as e:  # noqa: BLE001
                    print(am, start, e); time.sleep(5)
            else:
                sys.exit(f"falha {am}")
            rows += resp["docs"]; start += 1000
            if start >= resp["numFound"]:
                break
        with fp.open("w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=FL, extrasaction="ignore"); w.writeheader(); w.writerows(rows)
    d = pd.read_csv(fp).dropna(subset=["cadunico_tot_pes_pbf_i", "qtd_pessoas_beneficiarias_bolsa_familia_i"])
    a, b, pop = d.cadunico_tot_pes_pbf_i, d.qtd_pessoas_beneficiarias_bolsa_familia_i, d.populacao_censo_2022_i
    razao = a / b
    pa, pb = 100 * a / pop, 100 * b / pop
    res["meses"][am] = {
        "n_municipios": int(len(d)),
        "total_cadunico_tot_pes_pbf": int(a.sum()), "total_qtd_pessoas_benef": int(b.sum()),
        "razao_totais": round(float(a.sum() / b.sum()), 4),
        "razao_municipal_p5_p50_p95": [round(float(x), 3) for x in razao.quantile([.05, .5, .95])],
        "dif_pct_pop_pontos_p5_p50_p95": [round(float(x), 2) for x in (pa - pb).quantile([.05, .5, .95])],
        "correlacao_pct_pop": round(float(np.corrcoef(pa, pb)[0, 1]), 4),
    }
out = ROOT / "logs/16_mds_comparabilidade_log.json"
out.write_text(json.dumps(res, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps(res, ensure_ascii=False, indent=2))
