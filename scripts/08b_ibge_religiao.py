"""08b_ibge_religiao.py
Religião, Censo 2022 (SIDRA 9537): contagem de pessoas de 10+ anos (var 140) por religião e total.
Substitui a var 13495 baixada no script 08, que não é a distribuição por religião no município
(vale 100 em todas as categorias). Proporções calculadas no script 09.
Saída: data/raw/ibge/censo2022_religiao_mun.csv. Idempotente.
Uso: python -P scripts/08b_ibge_religiao.py <raiz_do_projeto>
"""
import csv
import json
import sys
import time
import urllib.request
from pathlib import Path

ROOT = Path(sys.argv[1])
OUT = ROOT / "data/raw/ibge/censo2022_religiao_mun.csv"
UFS = [11, 12, 13, 14, 15, 16, 17, 21, 22, 23, 24, 25, 26, 27, 28, 29, 31, 32, 33, 35, 41, 42, 43, 50, 51, 52, 53]
CATS = {"95278": "total", "95277": "evangelicas", "95263": "catolica", "2836": "sem_religiao"}
if OUT.exists():
    sys.exit(f"já existe: {OUT}")
rows = []
for uf in UFS:
    url = ("https://servicodados.ibge.gov.br/api/v3/agregados/9537/periodos/2022/variaveis/140"
           f"?localidades=N6[N3[{uf}]]&classificacao=2[6794]|58[95253]|133[{','.join(CATS)}]")
    for t in range(4):
        try:
            with urllib.request.urlopen(url, timeout=180) as r:
                data = json.load(r)
            break
        except Exception as e:  # noqa: BLE001
            print(f"UF {uf} tentativa {t + 1}: {e}")
            time.sleep(5)
    else:
        sys.exit(f"falha UF {uf}")
    for res in data[0]["resultados"]:
        c133 = [c for c in res["classificacoes"] if c["id"] == "133"][0]
        cod = list(c133["categoria"])[0]
        for s in res["series"]:
            rows.append({"cod_ibge7": s["localidade"]["id"], "religiao": CATS[cod], "pessoas_10mais": s["serie"]["2022"]})
OUT.parent.mkdir(parents=True, exist_ok=True)
with OUT.open("w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=["cod_ibge7", "religiao", "pessoas_10mais"])
    w.writeheader()
    w.writerows(rows)
print(f"{len(rows)} linhas -> {OUT}")
