"""08_ibge_censo_indicadores.py
Indicadores municipais do Censo 2022 (IBGE, SIDRA API v3), por UF:
- 9537  religião: % da população de 10+ anos (var 13495) evangélica, católica, sem religião
- 9543  taxa de alfabetização 15+ anos (var 2513)
- 10295 rendimento domiciliar per capita médio (13431) e mediano (13534), R$ de 2022
- 10211 população residente total e urbana (var 93)
Saída bruta (formato longo): data/raw/ibge/censo2022_indicadores_mun.csv. Idempotente.
Uso: python -P scripts/08_ibge_censo_indicadores.py <raiz_do_projeto>
"""
import csv
import json
import sys
import time
import urllib.request
from pathlib import Path

ROOT = Path(sys.argv[1])
OUT = ROOT / "data/raw/ibge/censo2022_indicadores_mun.csv"
UFS = [11, 12, 13, 14, 15, 16, 17, 21, 22, 23, 24, 25, 26, 27, 28, 29, 31, 32, 33, 35, 41, 42, 43, 50, 51, 52, 53]
CONSULTAS = [
    ("9537", "13495", "2[6794]|58[95253]|133[95277,95263,2836]"),
    ("9543", "2513", "2[6794]|86[95251]|287[100362]"),
    ("10295", "13431|13534", "2[6794]|86[95251]|58[95253]"),
    ("10211", "93", "2661[32776]|1[6795,1]"),
]
if OUT.exists():
    sys.exit(f"já existe: {OUT}")

rows = []
for tab, var, cls in CONSULTAS:
    for uf in UFS:
        url = (f"https://servicodados.ibge.gov.br/api/v3/agregados/{tab}/periodos/2022/variaveis/{var}"
               f"?localidades=N6[N3[{uf}]]&classificacao={cls}")
        for t in range(4):
            try:
                with urllib.request.urlopen(url, timeout=180) as r:
                    data = json.load(r)
                break
            except Exception as e:  # noqa: BLE001
                print(f"{tab} UF {uf} tentativa {t + 1}: {e}")
                time.sleep(5)
        else:
            sys.exit(f"falha {tab} UF {uf}")
        for v in data:
            for res in v["resultados"]:
                cat = "|".join(f"{c['id']}={list(c['categoria'].values())[0]}" for c in res["classificacoes"])
                for s in res["series"]:
                    rows.append({"tabela": tab, "variavel": v["id"], "nome_variavel": v["variavel"], "categorias": cat,
                                 "cod_ibge7": s["localidade"]["id"], "valor": s["serie"]["2022"]})
    print(f"tabela {tab}: ok", flush=True)

OUT.parent.mkdir(parents=True, exist_ok=True)
with OUT.open("w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0]))
    w.writeheader()
    w.writerows(rows)
print(f"{len(rows)} linhas -> {OUT}")
