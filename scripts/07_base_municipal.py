"""07_base_municipal.py
Base analítica municipal: votação presidencial 1º turno 2022 e 2026 (TSE), Auxílio Brasil set/2022 e
Bolsa Família set/2026 (MDS), mortalidade COVID-19 2020-2022 (SIM) e população Censo 2022 (IBGE).
Margem = (votos 22 - votos 13) / válidos x 100, em pontos dos votos válidos (positivo = PL na frente).
Em 2022 o 22 é Jair Bolsonaro; em 2026, Flávio Bolsonaro. 13 = Lula nos dois anos.
Saída: data/derived/base_municipal.csv e logs/07_base_log.json (inclui reprodução das viradas).
Uso: python -P scripts/07_base_municipal.py <raiz_do_projeto>
"""
import json
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(sys.argv[1])
DER = ROOT / "data/derived"

cw = pd.read_csv(DER / "tse_ibge_crosswalk.csv", dtype=str)
cw["cd_tse"] = cw["cd_tse"].str.zfill(5)

t22 = pd.read_csv(DER / "tse_presidente_t1_2022_municipio.csv", dtype={"CD_MUNICIPIO": str})
t22["cd_tse"] = t22["CD_MUNICIPIO"].str.zfill(5)
t22 = t22.rename(columns={"votos_13": "lula_22", "votos_22": "bolsonaro_22", "validos": "validos_22", "outros": "outros_22"})
t22 = t22[["cd_tse", "lula_22", "bolsonaro_22", "outros_22", "validos_22"]]

t26 = pd.read_csv(DER / "tse_presidente_t1_2026_municipio.csv", dtype={"cd_tse": str, "cd_ibge7": str})
t26 = t26[t26["uf"] != "ZZ"].copy()
t26["cd_tse"] = t26["cd_tse"].str.zfill(5)
t26 = t26.rename(columns={"votos_13": "lula_26", "votos_22": "flavio_26", "validos": "validos_26", "outros": "outros_26",
                          "eleitorado": "eleitorado_26"})

base = t26[["uf", "cd_tse", "cd_ibge7", "nome_tse", "eleitorado_26", "lula_26", "flavio_26", "outros_26", "validos_26"]]
n_t22_sem_par = int((~t22["cd_tse"].isin(base["cd_tse"])).sum())
base = base.merge(t22, on="cd_tse", how="left")
base["cod6"] = base["cd_ibge7"].str[:6]
base["margem_22"] = (base["bolsonaro_22"] - base["lula_22"]) / base["validos_22"] * 100
base["margem_26"] = (base["flavio_26"] - base["lula_26"]) / base["validos_26"] * 100
base["delta_margem"] = base["margem_26"] - base["margem_22"]
base["pct_lula_26"] = base["lula_26"] / base["validos_26"] * 100
base["pct_flavio_26"] = base["flavio_26"] / base["validos_26"] * 100

# vencedor entre os dois (o vencedor geral do município foi sempre 13 ou 22? verificado no log)
def venc(a, b):
    return pd.Series(pd.NA, index=a.index, dtype="object").mask(a > b, "13").mask(b > a, "22").mask((a == b) & a.notna(), "empate")
base["venc_22"] = venc(base["lula_22"], base["bolsonaro_22"])
base["venc_26"] = venc(base["lula_26"], base["flavio_26"])

# MDS
mds22 = pd.read_csv(ROOT / "data/raw/mds/misocial_202209.csv", dtype={"codigo_ibge": str})
mds26 = pd.read_csv(ROOT / "data/raw/mds/misocial_202609.csv", dtype={"codigo_ibge": str})
mds = mds26[["codigo_ibge", "populacao_censo_2022_i", "qtd_pessoas_beneficiarias_bolsa_familia_i",
             "qtd_familias_beneficiarias_bolsa_familia_i"]].merge(
    mds22[["codigo_ibge", "cadunico_tot_pes_pbf_i", "pab_qtd_fam_benef_i"]], on="codigo_ibge", how="left")
mds.columns = ["cod6", "pop_censo22_mds", "pessoas_bf_set26", "familias_bf_set26", "pessoas_ab_set22", "familias_ab_set22"]
base = base.merge(mds, on="cod6", how="left")

# COVID + população Censo
cov = pd.read_csv(DER / "covid_mortalidade_municipio_2020_2022.csv", dtype={"cod6": str, "cod_ibge7": str})
cov = cov[["cod6", "pop_total", "obitos_basica", "taxa_bruta_basica_100mil", "taxa_padr_direta_basica_100mil",
           "esperados_basica", "smr_basica"]]
base = base.merge(cov, on="cod6", how="left")
base["pct_bf_26"] = base["pessoas_bf_set26"] / base["pop_total"] * 100
base["pct_ab_22"] = base["pessoas_ab_set22"] / base["pop_total"] * 100

base.to_csv(DER / "base_municipal.csv", index=False, float_format="%.6f")

# ---- reprodução das afirmações do vídeo ----
comp = base.dropna(subset=["venc_22", "venc_26"])
viradas = comp[(comp["venc_22"] == "13") & (comp["venc_26"] == "22")]
contrarias = comp[(comp["venc_22"] == "22") & (comp["venc_26"] == "13")]
por_uf = viradas.groupby("uf").size().to_dict()
andaram_direita = (comp["delta_margem"] > 0).mean() * 100
log = {
    "municipios_2026": int(len(base)), "municipios_com_2022": int(len(comp)),
    "municipios_tse2022_sem_par_2026": n_t22_sem_par,
    "sem_2022": base.loc[base["validos_22"].isna(), ["uf", "nome_tse"]].values.tolist(),
    "viradas_lula_para_flavio": int(len(viradas)), "viradas_bolsonaro_para_lula": int(len(contrarias)),
    "empates_22": int((comp["venc_22"] == "empate").sum()), "empates_26": int((comp["venc_26"] == "empate").sum()),
    "viradas_por_uf": {k: int(v) for k, v in sorted(por_uf.items())},
    "pct_municipios_margem_andou_para_PL": round(andaram_direita, 2),
    "sem_mds": int(base["pessoas_bf_set26"].isna().sum()), "sem_ab22": int(base["pessoas_ab_set22"].isna().sum()),
    "sem_covid": int(base["obitos_basica"].isna().sum()),
    "casos_video": base[base["nome_tse"].isin(["NOVA PÁDUA", "BONFIM DO PIAUÍ"])][
        ["uf", "nome_tse", "pct_lula_26", "pct_flavio_26", "pct_bf_26", "pct_ab_22"]].round(1).to_dict("records"),
}
(ROOT / "logs/07_base_log.json").write_text(json.dumps(log, indent=2, ensure_ascii=False), encoding="utf-8")
print(json.dumps(log, indent=2, ensure_ascii=False))
