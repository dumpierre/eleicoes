"""02_ibge_pop_idade.py
Baixa do SIDRA/IBGE (API v3) a população residente do Censo 2022 por município e faixa etária
quinquenal (tabela 9514, variável 93, sexo total, forma de declaração total).
Saída: data/raw/ibge/censo2022_pop_idade_mun.csv (bruto, uma linha por município x faixa).
Idempotente: não baixa de novo se o arquivo existir.
Uso: python -I scripts/02_ibge_pop_idade.py <raiz_do_projeto>
"""
import csv
import json
import sys
import time
import urllib.request
from pathlib import Path

ROOT = Path(sys.argv[1])
OUT = ROOT / "data/raw/ibge/censo2022_pop_idade_mun.csv"
FAIXAS = {
    "93070": "00-04", "93084": "05-09", "93085": "10-14", "93086": "15-19", "93087": "20-24",
    "93088": "25-29", "93089": "30-34", "93090": "35-39", "93091": "40-44", "93092": "45-49",
    "93093": "50-54", "93094": "55-59", "93095": "60-64", "93096": "65-69", "93097": "70-74",
    "93098": "75-79", "49108": "80-84", "49109": "85-89", "60040": "90-94", "60041": "95-99",
    "6653": "100+", "100362": "total",
}
UFS = [11, 12, 13, 14, 15, 16, 17, 21, 22, 23, 24, 25, 26, 27, 28, 29, 31, 32, 33, 35, 41, 42, 43, 50, 51, 52, 53]

if OUT.exists():
    print(f"já existe: {OUT}")
    sys.exit(0)

cats = ",".join(FAIXAS)
rows = []
for uf in UFS:
    url = (
        "https://servicodados.ibge.gov.br/api/v3/agregados/9514/periodos/2022/variaveis/93"
        f"?localidades=N6[N3[{uf}]]&classificacao=2[6794]|286[113635]|287[{cats}]"
    )
    for tentativa in range(4):
        try:
            with urllib.request.urlopen(url, timeout=120) as r:
                data = json.load(r)
            break
        except Exception as e:  # noqa: BLE001
            print(f"UF {uf} tentativa {tentativa + 1}: {e}")
            time.sleep(5)
    else:
        sys.exit(f"falha na UF {uf}")
    for res in data[0]["resultados"]:
        cat287 = [c for c in res["classificacoes"] if c["id"] == "287"][0]
        cod = list(cat287["categoria"].keys())[0]
        for s in res["series"]:
            v = s["serie"]["2022"]
            rows.append({
                "cod_ibge7": s["localidade"]["id"],
                "municipio": s["localidade"]["nome"],
                "faixa": FAIXAS[cod],
                "pop": "" if v in ("-", "...", "X") else v,
            })
    print(f"UF {uf}: ok")

OUT.parent.mkdir(parents=True, exist_ok=True)
with OUT.open("w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=["cod_ibge7", "municipio", "faixa", "pop"])
    w.writeheader()
    w.writerows(rows)
print(f"{len(rows)} linhas -> {OUT}")
