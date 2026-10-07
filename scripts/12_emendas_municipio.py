"""12_emendas_municipio.py
Emendas parlamentares pagas jan/2023-set/2026 por município (CGU, arquivo por favorecido), conforme
plano_analise_emendas_v1.md.
- Município do favorecido (UF + nome) -> código IBGE pela lista oficial de localidades do IBGE (nome normalizado).
- Principal: favorecidos "Município" e "Fundo Público da Administração Direta Municipal".
- Sensibilidade: todos os favorecidos sediados no município.
- Por tipo (individual; bancada/comissão/relator) e, nas individuais, por bloco do partido do autor em 2023.
Saída: data/derived/emendas_municipio.csv; data/derived/base_analitica_emendas.csv; log.
Uso: python -P scripts/12_emendas_municipio.py <raiz_do_projeto>
"""
import json
import re
import sys
import unicodedata
import zipfile
from pathlib import Path

import pandas as pd

ROOT = Path(sys.argv[1])
RAW = ROOT / "data/raw/cgu"
MUNICIPAIS = {"Município", "Fundo Público da Administração Direta Municipal"}
PL = {"PL"}
ESQ = {"PT", "PCdoB", "PV", "PSOL", "REDE", "PSB", "PDT"}


def norm(s):
    s = unicodedata.normalize("NFKD", str(s)).encode("ascii", "ignore").decode().upper()
    return " ".join(re.sub(r"[^A-Z ]", " ", s.replace("'", "")).split())


z = zipfile.ZipFile(RAW / "EmendasParlamentares.zip")
f = pd.read_csv(z.open("EmendasParlamentares_PorFavorecido.csv"), sep=";", encoding="latin1", dtype=str)
f.columns = ["cod", "cod_autor", "autor", "num", "tipo", "anomes", "cod_fav", "fav", "natjur", "tipofav", "uf", "mun", "valor"]
f["v"] = pd.to_numeric(f["valor"].str.replace(".", "", regex=False).str.replace(",", ".", regex=False))
p = f[(f["anomes"] >= "202301") & (f["anomes"] <= "202609")].copy()

# município -> IBGE
loc = json.loads((ROOT / "data/raw/ibge/localidades_municipios.json").read_text(encoding="utf-8"))
ib = pd.DataFrame([{"cd_ibge7": str(m["id"]), "uf": m["microrregiao"]["mesorregiao"]["UF"]["sigla"] if m.get("microrregiao") else m["regiao-imediata"]["regiao-intermediaria"]["UF"]["sigla"],
                    "mun_n": norm(m["nome"])} for m in loc])
p["mun_n"] = p["mun"].map(norm)
# nomes sem par exato: similaridade dentro da UF (difflib, corte 0,75), todas as correspondências no log
import difflib
exatos = set(zip(ib["uf"], ib["mun_n"]))
# renomeações e grafias conhecidas, aplicadas antes da similaridade (destinos conferidos na lista do IBGE)
MANUAL = {("RN", "ACU"): "ASSU", ("SP", "EMBU"): "EMBU DAS ARTES", ("RN", "PRESIDENTE JUSCELINO"): "SERRA CAIADA",
          ("RN", "AUGUSTO SEVERO"): "CAMPO GRANDE", ("TO", "FORTALEZA DO TABOCAO"): "TABOCAO",
          ("PB", "SERIDO"): "SAO VICENTE DO SERIDO"}
assert all((k[0], v) in exatos for k, v in MANUAL.items())
p["mun_n"] = [MANUAL.get((u, m), m) for u, m in zip(p["uf"], p["mun_n"])]
fuzzy = {}
for uf_, mn in set(zip(p["uf"], p["mun_n"])) - exatos:
    opts = ib.loc[ib["uf"] == uf_, "mun_n"].tolist()
    hit = difflib.get_close_matches(mn, opts, n=1, cutoff=0.75)
    if not hit:  # prefixo: EMBU -> EMBU DAS ARTES
        pre = [o for o in opts if o.startswith(mn + " ")]
        hit = pre[:1] if len(pre) == 1 else []
    if hit:
        fuzzy[(uf_, mn)] = hit[0]
p["mun_n"] = [fuzzy.get((u, m), m) for u, m in zip(p["uf"], p["mun_n"])]
p = p.merge(ib, on=["uf", "mun_n"], how="left")
sem = p[p["cd_ibge7"].isna()]

# autores e blocos
aut = pd.read_csv(ROOT / "data/derived/emendas_autores_partido.csv", dtype=str)
aut = aut[aut["status"] == "ok"][["cod_autor", "autor", "partido_2023"]].drop_duplicates(["cod_autor", "autor"])
p = p.merge(aut, on=["cod_autor", "autor"], how="left")
indiv = p["tipo"].str.startswith("Emenda Individual")
p["bloco"] = "coletiva"
p.loc[indiv, "bloco"] = p.loc[indiv, "partido_2023"].map(lambda s: "PL" if s in PL else ("esquerda" if s in ESQ else ("demais" if isinstance(s, str) else "sem_partido_identificado")))
p["municipal"] = p["natjur"].isin(MUNICIPAIS)

ok = p[p["cd_ibge7"].notna()]
g = lambda d: d.groupby("cd_ibge7")["v"].sum()
mm = ok[ok["municipal"]]
out = pd.DataFrame({
    "emendas_municipal": g(mm),
    "emendas_todos_favorecidos": g(ok),
    "emendas_municipal_individual": g(mm[mm["tipo"].str.startswith("Emenda Individual")]),
    "emendas_municipal_coletivas": g(mm[~mm["tipo"].str.startswith("Emenda Individual")]),
    "emendas_municipal_pix": g(mm[mm["tipo"] == "Emenda Individual - Transferências Especiais"]),
    "emendas_municipal_ind_PL": g(mm[mm["bloco"] == "PL"]),
    "emendas_municipal_ind_esquerda": g(mm[mm["bloco"] == "esquerda"]),
    "emendas_municipal_ind_demais": g(mm[mm["bloco"] == "demais"]),
}).fillna(0)
out.index.name = "cd_ibge7"
out.reset_index().to_csv(ROOT / "data/derived/emendas_municipio.csv", index=False, float_format="%.2f")

base = pd.read_csv(ROOT / "data/derived/base_analitica.csv", dtype={"cd_ibge7": str, "cod6": str, "cd_tse": str})
base = base.merge(out.reset_index(), on="cd_ibge7", how="left")
for c in out.columns:
    base[c] = base[c].fillna(0)
    base[c + "_pc"] = base[c] / base["pop_total"]
base.to_csv(ROOT / "data/derived/base_analitica_emendas.csv", index=False, float_format="%.6f")

tot = p["v"].sum()
log = {
    "valor_periodo_bi": round(tot / 1e9, 2),
    "valor_municipal_bi": round(p.loc[p["municipal"], "v"].sum() / 1e9, 2),
    "pct_valor_sem_codigo_ibge": round(100 * sem["v"].sum() / tot, 3),
    "correspondencias_manuais": {f"{k[0]} {k[1]}": v for k, v in MANUAL.items()},
    "correspondencias_por_similaridade": {f"{k[0]} {k[1]}": v for k, v in sorted(fuzzy.items())},
    "sem_codigo_exemplos": sem.groupby(["uf", "mun"])["v"].sum().nlargest(15).round(0).to_dict().__repr__(),
    "municipal_por_bloco_bi": (p[p["municipal"]].groupby("bloco")["v"].sum() / 1e9).round(2).to_dict(),
    "municipios_com_emenda_municipal": int((out["emendas_municipal"] > 0).sum()),
    "pc_municipal_resumo": base["emendas_municipal_pc"].describe().round(1).to_dict(),
}
(ROOT / "logs/12_emendas_municipio_log.json").write_text(json.dumps(log, indent=2, ensure_ascii=False), encoding="utf-8")
print(json.dumps(log, indent=2, ensure_ascii=False))
