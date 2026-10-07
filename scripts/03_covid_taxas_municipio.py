"""03_covid_taxas_municipio.py
Mortalidade por COVID-19 (causa básica B34.2, SIM) 2020-2022 por município de residência,
bruta e padronizada por idade, com população do Censo 2022 (SIDRA 9514).

Definições
- Óbito COVID: CAUSABAS = B342 (convenção do SIM para COVID-19). Sensibilidade: COVID em qualquer linha.
- Numerador: óbitos acumulados 2020-2022, por município de residência (CODMUNRES, 6 dígitos).
- Denominador: população residente Censo 2022 (data de referência 1/8/2022). Taxa = óbitos acumulados
  por 100 mil habitantes (não é taxa anual).
- Padronização direta: taxas específicas por faixa quinquenal (80+ agregado) x população padrão = Brasil, Censo 2022.
- Padronização indireta: SMR = observados / esperados, esperados = soma(pop_mun_faixa x taxa_Brasil_faixa).
  SMR é preferível em municípios pequenos; a taxa direta é instável quando há poucos óbitos.
- Idade SIM: 1º dígito unidade (0-3 = <1 ano; 4 = anos; 5 = 100 + anos); 999 ignorado.

Uso: python -I scripts/03_covid_taxas_municipio.py <raiz_do_projeto>
"""
import json
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(sys.argv[1])
DER = ROOT / "data/derived"
FAIXAS = ["00-04", "05-09", "10-14", "15-19", "20-24", "25-29", "30-34", "35-39", "40-44", "45-49",
          "50-54", "55-59", "60-64", "65-69", "70-74", "75-79", "80+"]


def idade_anos(s: str):
    if not s or len(s) != 3 or not s.isdigit():
        return None
    u, v = int(s[0]), int(s[1:])
    if u <= 3:
        return 0
    if u == 4:
        return v
    if u == 5:
        return 100 + v
    return None


def faixa(a):
    if a is None:
        return None
    return "80+" if a >= 80 else FAIXAS[a // 5]


# ---------- óbitos ----------
frames = []
for ano in (2020, 2021, 2022):
    d = pd.read_csv(DER / f"sim_covid_{ano}.csv", dtype=str, keep_default_na=False)
    d["ano"] = ano
    frames.append(d)
ob = pd.concat(frames, ignore_index=True)
ob["COVID_BASICA"] = ob["COVID_BASICA"].astype(int)
ob["COVID_QUALQUER"] = ob["COVID_QUALQUER"].astype(int)
ob["faixa"] = ob["IDADE"].map(lambda s: faixa(idade_anos(s)))
ob["cod6"] = ob["CODMUNRES"].str[:6]

# ---------- população ----------
pop = pd.read_csv(ROOT / "data/raw/ibge/censo2022_pop_idade_mun.csv", dtype=str, keep_default_na=False)
pop["pop"] = pd.to_numeric(pop["pop"].replace("", "0"))
pop["cod6"] = pop["cod_ibge7"].str[:6]
pop_tot = pop[pop["faixa"] == "total"][["cod6", "cod_ibge7", "municipio", "pop"]].rename(columns={"pop": "pop_total"})
p = pop[pop["faixa"] != "total"].copy()
p["faixa"] = p["faixa"].where(p["faixa"].isin(FAIXAS), "80+")
p = p.groupby(["cod6", "faixa"], as_index=False)["pop"].sum()
pw = p.pivot(index="cod6", columns="faixa", values="pop").reindex(columns=FAIXAS).fillna(0)

log = {}
for defin, col in (("basica", "COVID_BASICA"), ("qualquer", "COVID_QUALQUER")):
    o = ob[ob[col] == 1]
    log[f"{defin}_total"] = int(len(o))
    log[f"{defin}_por_ano"] = {int(k): int(v) for k, v in o.groupby("ano").size().items()}
    log[f"{defin}_idade_ignorada"] = int(o["faixa"].isna().sum())
    sem_mun = ~o["cod6"].isin(pw.index)
    log[f"{defin}_sem_municipio_valido"] = int(sem_mun.sum())
    log[f"{defin}_exemplos_cod_invalidos"] = o.loc[sem_mun, "cod6"].value_counts().head(10).to_dict()

    ok = o[~sem_mun]
    obs_tot = ok.groupby("cod6").size().reindex(pw.index, fill_value=0)
    ow = ok.dropna(subset=["faixa"]).groupby(["cod6", "faixa"]).size().unstack(fill_value=0)
    ow = ow.reindex(index=pw.index, columns=FAIXAS, fill_value=0)

    # taxas nacionais por faixa (óbitos com idade e município válidos)
    br_rate = ow.sum() / pw.sum()
    std = pw.sum() / pw.sum().sum()  # pesos padrão Brasil 2022
    esperado = (pw * br_rate).sum(axis=1)
    taxa_faixa = ow / pw.where(pw > 0)
    direta = (taxa_faixa.fillna(0) * std).sum(axis=1) * 1e5
    res = pd.DataFrame({
        f"obitos_{defin}": obs_tot,
        f"obitos_{defin}_idade_conhecida": ow.sum(axis=1),
        f"taxa_bruta_{defin}_100mil": obs_tot / pw.sum(axis=1) * 1e5,
        f"taxa_padr_direta_{defin}_100mil": direta,
        f"esperados_{defin}": esperado,
        f"smr_{defin}": ow.sum(axis=1) / esperado,
    })
    if defin == "basica":
        out = res
        log["taxa_brasil_por_faixa_100mil_basica"] = {k: round(v * 1e5, 1) for k, v in br_rate.items()}
        log["taxa_bruta_brasil_100mil_basica"] = round(obs_tot.sum() / pw.values.sum() * 1e5, 1)
    else:
        out = out.join(res)
    # por ano (causa básica, bruta)
for ano in (2020, 2021, 2022):
    o = ob[(ob["COVID_BASICA"] == 1) & (ob["ano"] == ano) & ob["cod6"].isin(pw.index)]
    out[f"obitos_basica_{ano}"] = o.groupby("cod6").size().reindex(out.index, fill_value=0)

out = pop_tot.set_index("cod6").join(out, how="right").reset_index()
cols_first = ["cod_ibge7", "cod6", "municipio", "pop_total"]
out = out[cols_first + [c for c in out.columns if c not in cols_first]]
fp = DER / "covid_mortalidade_municipio_2020_2022.csv"
out.to_csv(fp, index=False, float_format="%.4f")
log["municipios"] = int(len(out))
log["municipios_zero_obitos_basica"] = int((out["obitos_basica"] == 0).sum())
log["saida"] = str(fp)
(ROOT / "logs/03_covid_taxas_log.json").write_text(json.dumps(log, indent=2, ensure_ascii=False), encoding="utf-8")
print(json.dumps(log, indent=2, ensure_ascii=False))
print(out.describe().T[["mean", "50%", "min", "max"]].round(2).to_string())
