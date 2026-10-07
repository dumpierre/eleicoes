"""06_tse_2026_resultados.py
Votação para Presidente, 1º turno 2026 (eleição 6257), por município, do sistema oficial de
divulgação de resultados do TSE (resultados.tse.jus.br). Os dados abertos (cdn.tse.jus.br) de 2026
ainda não trazem o cargo de Presidente (verificado em 2026-10-07).
- Correspondência TSE x IBGE: config/mun-e006257-cm.json (campos cd e cdi), arquivo oficial do TSE.
- Um JSON bruto por localidade em data/raw/tse/resultados_6257/<uf>/ (cache; idempotente).
Saídas: data/derived/tse_presidente_t1_2026_municipio.csv, data/derived/tse_ibge_crosswalk.csv
Uso: python -P scripts/06_tse_2026_resultados.py <raiz_do_projeto>
"""
import concurrent.futures as cf
import json
import sys
import time
import urllib.request
from pathlib import Path

import pandas as pd

ROOT = Path(sys.argv[1])
RAW = ROOT / "data/raw/tse/resultados_6257"
BASE = "https://resultados.tse.jus.br/oficial/ele2026/6257"
cfg = json.loads((RAW / "mun-e006257-cm.json").read_text(encoding="utf-8"))

locs = [(a["cd"], m["cd"], m["cdi"], m["nm"]) for a in cfg["abr"] for m in a["mu"]]
pd.DataFrame(locs, columns=["uf", "cd_tse", "cd_ibge7", "nome_tse"]).to_csv(ROOT / "data/derived/tse_ibge_crosswalk.csv", index=False)


def baixar(loc):
    uf, cd, _, _ = loc
    fp = RAW / uf / f"{uf}{cd}-c0001-e006257-u.json"
    if fp.exists() and fp.stat().st_size > 500:
        return fp, None
    fp.parent.mkdir(parents=True, exist_ok=True)
    url = f"{BASE}/dados/{uf}/{uf}{cd}-c0001-e006257-u.json"
    for t in range(5):
        try:
            with urllib.request.urlopen(url, timeout=60) as r:
                b = r.read()
            json.loads(b)
            fp.write_bytes(b)
            return fp, None
        except Exception as e:  # noqa: BLE001
            err = str(e)
            time.sleep(2 * (t + 1))
    return fp, err


erros = []
with cf.ThreadPoolExecutor(max_workers=8) as ex:
    for i, (fp, err) in enumerate(ex.map(baixar, locs)):
        if err:
            erros.append((str(fp), err))
        if i % 1000 == 0:
            print(f"{i}/{len(locs)}", flush=True)

rows = []
for uf, cd, cdi, nm in locs:
    fp = RAW / uf / f"{uf}{cd}-c0001-e006257-u.json"
    if not fp.exists():
        continue
    d = json.loads(fp.read_text(encoding="utf-8"))
    votos = {}
    for a in d["carg"][0]["agr"]:
        for p in a["par"]:
            for c in p["cand"]:
                votos[c["n"]] = int(c["vap"])
    v, e, s = d["v"], d["e"], d["s"]
    rows.append({
        "uf": uf.upper(), "cd_tse": cd, "cd_ibge7": cdi, "nome_tse": nm,
        "pct_secoes_totalizadas": s["pst"], "eleitorado": int(e["te"]), "comparecimento": int(e["c"]),
        "validos": int(v["vv"]), "brancos": int(v["vb"]), "nulos": int(v["tvn"]),
        "votos_13": votos.get("13", 0), "votos_22": votos.get("22", 0),
        "outros": int(v["vv"]) - votos.get("13", 0) - votos.get("22", 0),
        "data_totalizacao": f"{d['dt']} {d['ht']}",
    })
out = pd.DataFrame(rows)
out.to_csv(ROOT / "data/derived/tse_presidente_t1_2026_municipio.csv", index=False)

br = out[out["uf"] != "ZZ"]
tot = out[["validos", "votos_13", "votos_22", "outros"]].sum()
log = {
    "localidades_config": len(locs), "arquivos_lidos": len(out), "erros_download": erros[:20], "n_erros": len(erros),
    "municipios_brasil": int(len(br)), "localidades_exterior": int((out["uf"] == "ZZ").sum()),
    "pct_secoes_nao_100": out.loc[out["pct_secoes_totalizadas"] != "100,00", ["uf", "nome_tse", "pct_secoes_totalizadas"]].values.tolist()[:20],
    "validos_total": int(tot["validos"]), "pct_22": round(100 * tot["votos_22"] / tot["validos"], 2),
    "pct_13": round(100 * tot["votos_13"] / tot["validos"], 2),
    "diferenca_22_menos_13": int(tot["votos_22"] - tot["votos_13"]), "outros": int(tot["outros"]),
    "totalizacao_mais_recente": out["data_totalizacao"].max(),
}
(ROOT / "logs/06_tse_2026_log.json").write_text(json.dumps(log, indent=2, ensure_ascii=False), encoding="utf-8")
print(json.dumps(log, indent=2, ensure_ascii=False))
