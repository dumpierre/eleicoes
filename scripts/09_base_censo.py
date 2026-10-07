"""09_base_censo.py
Junta à base municipal os indicadores do Censo 2022: renda domiciliar per capita (média, mediana),
alfabetização 15+, % evangélicos/católicos/sem religião (10+), % urbana, % 60+ anos.
Saída: data/derived/base_analitica.csv
Uso: python -P scripts/09_base_censo.py <raiz_do_projeto>
"""
import json
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(sys.argv[1])
base = pd.read_csv(ROOT / "data/derived/base_municipal.csv", dtype={"cd_ibge7": str, "cod6": str, "cd_tse": str})

ind = pd.read_csv(ROOT / "data/raw/ibge/censo2022_indicadores_mun.csv", dtype=str)
ind["v"] = pd.to_numeric(ind["valor"], errors="coerce")
def pega(tab, var, cat_sub):
    m = (ind["tabela"] == tab) & (ind["variavel"] == var) & (ind["categorias"] == cat_sub)
    return ind[m].set_index("cod_ibge7")["v"]
cen = pd.DataFrame({
    "renda_pc_media": pega("10295", "13431", "2=Total|86=Total|58=Total"),
    "renda_pc_mediana": pega("10295", "13534", "2=Total|86=Total|58=Total"),
    "alfabetizacao_15mais": pega("9543", "2513", "2=Total|86=Total|287=Total"),
    "pop_10211_total": pega("10211", "93", "2661=Total|1=Total"),
    "pop_urbana": pega("10211", "93", "2661=Total|1=Urbana"),
})
cen["pct_urbana"] = cen["pop_urbana"] / cen["pop_10211_total"] * 100

rel = pd.read_csv(ROOT / "data/raw/ibge/censo2022_religiao_mun.csv", dtype=str)
rel["n"] = pd.to_numeric(rel["pessoas_10mais"].replace("-", "0"))
rw = rel.pivot(index="cod_ibge7", columns="religiao", values="n")
for c in ("evangelicas", "catolica", "sem_religiao"):
    cen[f"pct_{c}"] = rw[c] / rw["total"] * 100

pop = pd.read_csv(ROOT / "data/raw/ibge/censo2022_pop_idade_mun.csv", dtype=str)
pop["p"] = pd.to_numeric(pop["pop"].replace("", "0"))
idosos = pop[pop["faixa"].isin(["60-64", "65-69", "70-74", "75-79", "80-84", "85-89", "90-94", "95-99", "100+"])].groupby("cod_ibge7")["p"].sum()
tot = pop[pop["faixa"] == "total"].set_index("cod_ibge7")["p"]
cen["pct_60mais"] = idosos / tot * 100
cen.index.name = "cd_ibge7"

out = base.merge(cen.reset_index(), on="cd_ibge7", how="left")
out.to_csv(ROOT / "data/derived/base_analitica.csv", index=False, float_format="%.6f")
cols = ["renda_pc_mediana", "renda_pc_media", "alfabetizacao_15mais", "pct_urbana", "pct_evangelicas", "pct_60mais",
        "pct_bf_26", "pct_ab_22", "smr_basica", "margem_22", "margem_26"]
log = {"linhas": len(out), "faltantes": {c: int(out[c].isna().sum()) for c in cols},
       "resumo": out[cols].describe().round(2).to_dict()}
(ROOT / "logs/09_base_censo_log.json").write_text(json.dumps(log, indent=2, ensure_ascii=False), encoding="utf-8")
print(json.dumps(log["faltantes"], indent=1))
print(out[cols].describe().round(1).T[["mean", "min", "50%", "max"]].to_string())
print(out[cols].corr().round(2).to_string())
