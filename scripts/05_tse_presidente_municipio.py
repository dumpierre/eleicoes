"""05_tse_presidente_municipio.py
Extrai a votação para Presidente, 1º turno, 2022, por município (soma das zonas),
dos arquivos oficiais do TSE (votacao_candidato_munzona_{ano}.zip, arquivo _BRASIL.csv).
Exclui votos no exterior (SG_UF = ZZ). Votos válidos = soma de QT_VOTOS_NOMINAIS_VALIDOS dos candidatos.
Saída: data/derived/tse_presidente_t1_{ano}_municipio.csv (código TSE) e log com totais e candidatos.
Uso: python -P scripts/05_tse_presidente_municipio.py <raiz_do_projeto>
"""
import json
import sys
import zipfile
from pathlib import Path

import pandas as pd

ROOT = Path(sys.argv[1])
COLS = ["ANO_ELEICAO", "NR_TURNO", "CD_ELEICAO", "SG_UF", "CD_MUNICIPIO", "NM_MUNICIPIO", "NR_ZONA",
        "CD_CARGO", "NR_CANDIDATO", "NM_URNA_CANDIDATO", "SG_PARTIDO", "QT_VOTOS_NOMINAIS",
        "QT_VOTOS_NOMINAIS_VALIDOS", "NM_TIPO_DESTINACAO_VOTOS"]
log = {}
for ano in (2022,):  # 2026: Presidente ausente nos dados abertos; ver script 06
    zp = ROOT / f"data/raw/tse/votacao_candidato_munzona_{ano}.zip"
    with zipfile.ZipFile(zp) as z:
        nome = f"votacao_candidato_munzona_{ano}_BRASIL.csv"
        chunks = []
        with z.open(nome) as f:
            for ch in pd.read_csv(f, sep=";", encoding="latin1", usecols=COLS, dtype=str, chunksize=500_000):
                ch = ch[(ch["CD_CARGO"] == "1") & (ch["NR_TURNO"] == "1")]
                if len(ch):
                    chunks.append(ch)
    d = pd.concat(chunks, ignore_index=True)
    for c in ("QT_VOTOS_NOMINAIS", "QT_VOTOS_NOMINAIS_VALIDOS"):
        d[c] = pd.to_numeric(d[c])
    cand = (d.groupby(["NR_CANDIDATO", "NM_URNA_CANDIDATO", "SG_PARTIDO", "NM_TIPO_DESTINACAO_VOTOS"])
            [["QT_VOTOS_NOMINAIS", "QT_VOTOS_NOMINAIS_VALIDOS"]].sum().sort_values("QT_VOTOS_NOMINAIS_VALIDOS", ascending=False))
    tot_validos_com_exterior = int(d["QT_VOTOS_NOMINAIS_VALIDOS"].sum())
    br = d[d["SG_UF"] != "ZZ"]
    piv = br.pivot_table(index=["SG_UF", "CD_MUNICIPIO", "NM_MUNICIPIO"], columns="NR_CANDIDATO",
                         values="QT_VOTOS_NOMINAIS_VALIDOS", aggfunc="sum", fill_value=0)
    out = pd.DataFrame(index=piv.index)
    out["votos_13"] = piv.get("13", 0)
    out["votos_22"] = piv.get("22", 0)
    out["validos"] = piv.sum(axis=1)
    out["outros"] = out["validos"] - out["votos_13"] - out["votos_22"]
    out = out.reset_index()
    fp = ROOT / f"data/derived/tse_presidente_t1_{ano}_municipio.csv"
    out.to_csv(fp, index=False)
    n13, n22 = int(cand.xs("13", level=0)["QT_VOTOS_NOMINAIS_VALIDOS"].sum()), int(cand.xs("22", level=0)["QT_VOTOS_NOMINAIS_VALIDOS"].sum())
    log[ano] = {
        "cd_eleicao": sorted(d["CD_ELEICAO"].unique().tolist()),
        "candidatos": [f"{i[0]} {i[1]} ({i[2]}) [{i[3]}]: {int(v)}" for i, v in cand["QT_VOTOS_NOMINAIS_VALIDOS"].items()],
        "validos_total_com_exterior": tot_validos_com_exterior,
        "pct_13_com_exterior": round(100 * n13 / tot_validos_com_exterior, 2),
        "pct_22_com_exterior": round(100 * n22 / tot_validos_com_exterior, 2),
        "diferenca_22_menos_13_com_exterior": n22 - n13,
        "outros_com_exterior": tot_validos_com_exterior - n13 - n22,
        "municipios": int(len(out)),
        "validos_sem_exterior": int(out["validos"].sum()),
    }
(ROOT / "logs/05_tse_log.json").write_text(json.dumps(log, indent=2, ensure_ascii=False), encoding="utf-8")
print(json.dumps(log, indent=2, ensure_ascii=False))
