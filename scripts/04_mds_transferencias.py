"""04_mds_transferencias.py
Baixa da API oficial do MDS (SAGI, MI Social) dados municipais de transferência de renda:
- set/2022: Programa Auxílio Brasil (governo Bolsonaro)
- set/2026: Programa Bolsa Família
Também guarda ago e out para checar estabilidade. Saída bruta em data/raw/mds/ (um CSV por mês).
Idempotente: pula meses já baixados.
Uso: python -P scripts/04_mds_transferencias.py <raiz_do_projeto>
"""
import csv
import json
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(sys.argv[1])
OUTDIR = ROOT / "data/raw/mds"
API = "https://aplicacoes.mds.gov.br/sagi/servicos/misocial"
BASE = ["anomes_s", "codigo_ibge", "municipio", "sigla_uf", "tipo_s",
        "populacao_censo_2022_i", "populacao_estimada_ibge_ano_i",
        "cadun_qtd_pessoas_cadastradas_i", "cadun_qtd_pessoas_cadastradas_pobreza_pbf_i",
        "cadun_qtd_pessoas_cadastradas_baixa_renda_i"]
CAMPOS = {
    "2022": BASE + ["pab_qtd_fam_benef_i", "cadunico_tot_pes_pbf_i", "pab_valor_pago_d", "pab_valor_medio_d"],
    "2026": BASE + ["qtd_familias_beneficiarias_bolsa_familia_i", "qtd_pessoas_beneficiarias_bolsa_familia_i",
                    "valor_repassado_bolsa_familia_f", "pbf_vlr_medio_benef_f"],
}
MESES = ["202208", "202209", "202210", "202608", "202609"]

OUTDIR.mkdir(parents=True, exist_ok=True)
for am in MESES:
    fp = OUTDIR / f"misocial_{am}.csv"
    if fp.exists():
        print(f"já existe: {fp}")
        continue
    fl = CAMPOS[am[:4]]
    rows, start = [], 0
    while True:
        q = urllib.parse.urlencode({"q": "*:*", "fq": f"anomes_s:{am}", "fl": ",".join(fl),
                                    "wt": "json", "rows": 1000, "start": start, "sort": "codigo_ibge asc"})
        for t in range(4):
            try:
                with urllib.request.urlopen(f"{API}?{q}", timeout=180) as r:
                    resp = json.load(r)["response"]
                break
            except Exception as e:  # noqa: BLE001
                print(f"{am} start={start} tentativa {t + 1}: {e}")
                time.sleep(5)
        else:
            sys.exit(f"falha em {am}")
        rows += resp["docs"]
        start += 1000
        if start >= resp["numFound"]:
            break
    with fp.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fl, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)
    print(f"{am}: {len(rows)} linhas (numFound {resp['numFound']}) -> {fp}")
(OUTDIR / "FONTE.txt").write_text(
    f"MDS/SAGI MI Social, API {API}\nBaixado em {time.strftime('%Y-%m-%d %H:%M:%S')} (hora local)\n", encoding="utf-8")
