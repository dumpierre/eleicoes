"""11_emendas_autores.py
Partido dos autores de emendas individuais pagas jan/2023-set/2026 (CGU, por favorecido).
Fontes oficiais: Câmara (dadosabertos.camara.leg.br, histórico por deputado) e Senado
(legis.senado.leg.br, filiações por senador). Casamento por nome parlamentar normalizado (+ UF quando ambíguo).
Partido principal = filiação em 01/02/2023 (legislatura 57) ou 31/01/2023 (quem só esteve na 56);
sensibilidade = filiação em 01/09/2026. Inclui legislaturas 56 e 57 (emendas antigas pagas a partir de 2023).
Desempate de nomes: registro com filiação encontrada; depois legislatura 57; depois Câmara.
Cache bruto em data/raw/cgu/parlamentares/. Saída: data/derived/emendas_autores_partido.csv e log.
Uso: python -P scripts/11_emendas_autores.py <raiz_do_projeto>
"""
import json
import re
import sys
import time
import unicodedata
import urllib.request
import zipfile
from pathlib import Path

import pandas as pd

ROOT = Path(sys.argv[1])
RAW = ROOT / "data/raw/cgu"
CACHE = RAW / "parlamentares"
CACHE.mkdir(exist_ok=True)
D_INI, D_FIM = "2023-02-01", "2026-09-01"


def norm(s):
    s = unicodedata.normalize("NFKD", str(s)).encode("ascii", "ignore").decode().upper()
    return re.sub(r"[^A-Z ]", " ", s).split() and " ".join(re.sub(r"[^A-Z ]", " ", s).split())


def get_json(url, fp):
    if fp.exists():
        return json.loads(fp.read_text(encoding="utf-8"))
    for t in range(4):
        try:
            req = urllib.request.Request(url, headers={"Accept": "application/json"})
            with urllib.request.urlopen(req, timeout=60) as r:
                b = r.read()
            fp.write_bytes(b)
            return json.loads(b)
        except Exception as e:  # noqa: BLE001
            err = e
            time.sleep(2 * (t + 1))
    raise RuntimeError(f"{url}: {err}")


# ---- emendas individuais pagas no período ----
z = zipfile.ZipFile(RAW / "EmendasParlamentares.zip")
f = pd.read_csv(z.open("EmendasParlamentares_PorFavorecido.csv"), sep=";", encoding="latin1", dtype=str)
f.columns = ["cod", "cod_autor", "autor", "num", "tipo", "anomes", "cod_fav", "fav", "natjur", "tipofav", "uf", "mun", "valor"]
f["v"] = pd.to_numeric(f["valor"].str.replace(".", "", regex=False).str.replace(",", ".", regex=False))
p = f[(f["anomes"] >= "202301") & (f["anomes"] <= "202609") & f["tipo"].str.startswith("Emenda Individual")]
autores = p.groupby(["cod_autor", "autor"], as_index=False)["v"].sum()
autores["nome_n"] = autores["autor"].map(norm)

# ---- Câmara (legislaturas 57 e 56) ----
def partido_em(hist, data):
    hs = sorted(hist, key=lambda h: h["dataHora"])
    sig = None
    for h in hs:
        if h["dataHora"][:10] <= data:
            sig = h["siglaPartido"]
    return sig or (hs[0]["siglaPartido"] if hs else None)

dep_rows = []
for leg, arqs in ((57, ["camara_deputados_leg57.json"]), (56, ["camara_deputados_leg56.json", "camara_deputados_leg56_p2.json"])):
    for a in arqs:
        for d in json.loads((RAW / a).read_text(encoding="utf-8"))["dados"]:
            dep_rows.append({"id": str(d["id"]), "nome_n": norm(d["nome"]), "leg": leg})
dep = pd.DataFrame(dep_rows).sort_values("leg", ascending=False).drop_duplicates(["id", "nome_n"])
part = {}
for i in dep["id"].unique():
    h = get_json(f"https://dadosabertos.camara.leg.br/api/v2/deputados/{i}/historico", CACHE / f"camara_{i}_historico.json")["dados"]
    part[i] = h
dep["partido_2023"] = [partido_em(part[i], "2023-02-01" if leg == 57 else "2023-01-31") for i, leg in zip(dep["id"], dep["leg"])]
dep["partido_2026"] = [partido_em(part[i], D_FIM) if leg == 57 else None for i, leg in zip(dep["id"], dep["leg"])]
dep["casa"] = "Câmara"

# ---- Senado (legislaturas 57 e 56) ----
rows = []
for leg in (57, 56):
    sen = json.loads((RAW / f"senado_senadores_leg{leg}.json").read_text(encoding="utf-8"))["ListaParlamentarLegislatura"]["Parlamentares"]["Parlamentar"]
    for s_ in sen:
        ip = s_["IdentificacaoParlamentar"]
        cod = ip["CodigoParlamentar"]
        fil = get_json(f"https://legis.senado.leg.br/dadosabertos/senador/{cod}/filiacoes", CACHE / f"senado_{cod}_filiacoes.json")
        try:
            fl = fil["FiliacaoParlamentar"]["Parlamentar"]["Filiacoes"]["Filiacao"]
            fl = fl if isinstance(fl, list) else [fl]
        except (KeyError, TypeError):
            fl = []
        def em(data):
            sig = None
            for x in sorted(fl, key=lambda x: x.get("DataFiliacao", "")):
                if x.get("DataFiliacao", "9999")[:10] <= data and (not x.get("DataDesfiliacao") or x["DataDesfiliacao"][:10] >= data):
                    sig = x["Partido"]["SiglaPartido"]
            return sig
        rows.append({"id": "S" + cod, "nome_n": norm(ip["NomeParlamentar"]), "leg": leg,
                     "partido_2023": em("2023-02-01" if leg == 57 else "2023-01-31"),
                     "partido_2026": em(D_FIM) if leg == 57 else None, "casa": "Senado"})
sen_df = pd.DataFrame(rows).drop_duplicates(["id", "nome_n"])

parl = pd.concat([dep, sen_df], ignore_index=True)
parl["tem_partido"] = parl["partido_2023"].notna()
parl = parl.sort_values(["tem_partido", "leg", "casa"], ascending=[False, False, True])
n_ids = parl[parl["tem_partido"]].groupby("nome_n")["partido_2023"].nunique()  # ambíguo só se os partidos divergem
cand = parl.drop_duplicates("nome_n")[["nome_n", "id", "casa", "leg", "partido_2023", "partido_2026"]]
cand["n"] = cand["nome_n"].map(n_ids).fillna(1)
m = autores.merge(cand, on="nome_n", how="left")
m["status"] = m["n"].map(lambda n: "sem_par" if pd.isna(n) else ("ambiguo" if n > 1 else "ok"))
m.to_csv(ROOT / "data/derived/emendas_autores_partido.csv", index=False)
tot = m["v"].sum()
log = {
    "autores": len(m), "valor_total_individuais_bi": round(tot / 1e9, 2),
    "pct_valor_por_status": (m.groupby("status")["v"].sum() / tot * 100).round(2).to_dict(),
    "sem_par_maiores": m[m["status"] != "ok"].nlargest(25, "v")[["autor", "v", "status"]].assign(v=lambda d: (d.v / 1e6).round(1)).values.tolist(),
    "valor_por_partido_2023_bi": (m[m.status == "ok"].groupby("partido_2023")["v"].sum() / 1e9).round(2).sort_values(ascending=False).to_dict(),
}
(ROOT / "logs/11_autores_log.json").write_text(json.dumps(log, indent=2, ensure_ascii=False), encoding="utf-8")
print(json.dumps(log, indent=2, ensure_ascii=False))
