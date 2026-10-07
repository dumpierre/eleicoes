"""17_mds_auxilio_serie2022.py
Série mensal nacional do Programa Auxílio Brasil em 2022 (jan a dez), da API oficial do MDS (SAGI, MI Social).
Uso no vídeo v2: mostrar, com dado oficial, o salto do benefício médio (EC 123/2022, +R$ 200 de ago a dez/2022).
Saídas:
- data/raw/mds/misocial_2022MM.csv (um por mês; pula os que já existem, nunca sobrescreve)
- data/derived/auxilio_brasil_serie_2022.csv (soma nacional por mês)
- logs/17_mds_auxilio_serie2022_log.json
Uso: python -P scripts/17_mds_auxilio_serie2022.py <raiz_do_projeto>
"""
import csv
import json
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(sys.argv[1])
RAW = ROOT / "data/raw/mds"
API = "https://aplicacoes.mds.gov.br/sagi/servicos/misocial"
FL = ["anomes_s", "codigo_ibge", "municipio", "sigla_uf", "tipo_s",
      "populacao_censo_2022_i", "populacao_estimada_ibge_ano_i",
      "cadun_qtd_pessoas_cadastradas_i", "cadun_qtd_pessoas_cadastradas_pobreza_pbf_i",
      "cadun_qtd_pessoas_cadastradas_baixa_renda_i",
      "pab_qtd_fam_benef_i", "cadunico_tot_pes_pbf_i", "pab_valor_pago_d", "pab_valor_medio_d"]
MESES = [f"2022{m:02d}" for m in range(1, 13)]

RAW.mkdir(parents=True, exist_ok=True)
log = {"api": API, "baixados": [], "ja_existiam": []}
for am in MESES:
    fp = RAW / f"misocial_{am}.csv"
    if fp.exists():
        log["ja_existiam"].append(am)
        continue
    rows, start = [], 0
    while True:
        q = urllib.parse.urlencode({"q": "*:*", "fq": f"anomes_s:{am}", "fl": ",".join(FL),
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
        w = csv.DictWriter(f, fieldnames=FL, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)
    log["baixados"].append({"mes": am, "linhas": len(rows), "numFound": resp["numFound"],
                            "em": time.strftime("%Y-%m-%d %H:%M:%S")})
    print(f"{am}: {len(rows)} linhas -> {fp}")

serie = []
for am in MESES:
    fam = pago = pes = 0.0
    n = 0
    with (RAW / f"misocial_{am}.csv").open(encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["tipo_s"] != "mes_mu":
                continue
            n += 1
            fam += float(r["pab_qtd_fam_benef_i"] or 0)
            pago += float(r["pab_valor_pago_d"] or 0)
            pes += float(r["cadunico_tot_pes_pbf_i"] or 0)
    serie.append({"anomes": am, "municipios": n, "familias": int(fam), "pessoas": int(pes),
                  "valor_pago_reais": round(pago, 2), "valor_medio_familia": round(pago / fam, 2) if fam else None})

out = ROOT / "data/derived/auxilio_brasil_serie_2022.csv"
with out.open("w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(serie[0]))
    w.writeheader()
    w.writerows(serie)
log["serie"] = serie
(ROOT / "logs/17_mds_auxilio_serie2022_log.json").write_text(json.dumps(log, ensure_ascii=False, indent=1), encoding="utf-8")
for s in serie:
    print(s)
