"""Build do site "Cidade não vota. Gente vota." (eleicoes.danielumpierre.com).

Rodar da raiz do projeto:  PYTHONUTF8=1 python -P site/build.py

Lê data/derived/, output/ e data/raw/ibge (só nomes e malha), calcula cada número da página,
registra a origem em site/registro_numeros.json e preenche site/src/index.html:
  {{chave}}   -> NUM[chave]["texto"]  (número com origem registrada)
  {{!bloco}}  -> HTML gerado aqui (lista por UF, tabelas), também só com números do registro
Saídas: site/dist/index.html, site/dist/dados.json, site/dist/CNAME, logs/site_build_log.json.
Nenhum número de dado é digitado no HTML nem no JS.
"""
import base64
import io
import json
import re
import sys
import unicodedata
from datetime import datetime
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / "site"
SRC, DIST = SITE / "src", SITE / "dist"

BASE = "data/derived/base_analitica_emendas.csv"
CENT = "data/derived/ibge_centroides_municipios.csv"
CONTR = "output/contrastes_p90_p10.csv"
EC123 = "data/derived/ec123_2022_beneficios.csv"
TSE_LOG = "logs/06_tse_2026_log.json"
LOCAL = "data/raw/ibge/localidades_municipios.json"
MALHA_UF = "data/raw/ibge/malha_uf_minima.geojson"
FONTS = ROOT / "video" / "assets" / "fonts"
DOMINIO = "eleicoes.danielumpierre.com"

NUM = {}


def br(x, casas=1, sinal=False):
    """pt-BR, arredondamento convencional (meio para longe do zero)."""
    q = Decimal(str(float(x))).quantize(Decimal(1).scaleb(-casas), rounding=ROUND_HALF_UP)
    s = f"{q:+.{casas}f}" if sinal else f"{q:.{casas}f}"
    s = s.replace("-", "−")
    inteiro, _, dec = s.partition(".")
    pre = ""
    if inteiro[0] in "+−":
        pre, inteiro = inteiro[0], inteiro[1:]
    inteiro = f"{int(inteiro):,}".replace(",", ".")
    return pre + inteiro + ("," + dec if dec else "")


def put(nome, valor, texto, fonte, como):
    if nome in NUM:
        raise KeyError(f"chave repetida: {nome}")
    NUM[nome] = {"valor": float(valor), "texto": texto, "fonte": fonte, "como": como}


def wcorr(x, y, w):
    x, y, w = map(np.asarray, (x, y, w))
    mx, my = np.average(x, weights=w), np.average(y, weights=w)
    return np.average((x - mx) * (y - my), weights=w) / np.sqrt(
        np.average((x - mx) ** 2, weights=w) * np.average((y - my) ** 2, weights=w))


def slug(s):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


def rcs_basis(x, knots):
    """Spline cúbica restrita (Harrell): colunas x e k-2 termos não lineares, escala (tk - t1)^2."""
    t = np.asarray(knots)
    k = len(t)
    pos = lambda u: np.clip(u, 0, None) ** 3
    cols = [x]
    for j in range(k - 2):
        cols.append((pos(x - t[j]) - pos(x - t[k - 2]) * (t[k - 1] - t[j]) / (t[k - 1] - t[k - 2])
                     + pos(x - t[k - 1]) * (t[k - 2] - t[j]) / (t[k - 1] - t[k - 2])) / (t[k - 1] - t[0]) ** 2)
    return np.column_stack(cols)


def carregar():
    base = pd.read_csv(ROOT / BASE, dtype={"venc_22": str, "venc_26": str})
    cent = pd.read_csv(ROOT / CENT)
    loc = json.loads((ROOT / LOCAL).read_text(encoding="utf-8"))
    nomes, ufs = {}, {}
    for m in loc:
        u = (m.get("microrregiao") or {}).get("mesorregiao", {}).get("UF") or m["regiao-imediata"]["regiao-intermediaria"]["UF"]
        nomes[m["id"]] = m["nome"]
        ufs[u["sigla"]] = (u["nome"], u["regiao"]["nome"])
    base["nome"] = base.cd_ibge7.map(nomes)
    assert base.nome.notna().all(), "município sem nome no IBGE"
    return base, cent, ufs


def numeros(base, cent, ufs):
    log = {}
    # ---------- topo: resultado nacional oficial (Brasil + exterior, TSE eleição 6257) ----------
    t = json.loads((ROOT / TSE_LOG).read_text(encoding="utf-8"))
    put("n_mun", t["municipios_brasil"], br(t["municipios_brasil"], 0), TSE_LOG, "municipios_brasil")
    put("flavio_pct", t["pct_22"], br(t["pct_22"]) + "%", TSE_LOG, "pct_22 (Brasil + exterior, 100% das seções)")
    put("lula_pct", t["pct_13"], br(t["pct_13"]) + "%", TSE_LOG, "pct_13")
    put("dif_votos", t["diferenca_22_menos_13"], br(t["diferenca_22_menos_13"], 0), TSE_LOG, "diferenca_22_menos_13")
    put("dif_mi", t["diferenca_22_menos_13"] / 1e6, br(t["diferenca_22_menos_13"] / 1e6, 2) + " mi", TSE_LOG, "diferenca_22_menos_13 / 1e6")
    put("outros_mi", t["outros"] / 1e6, br(t["outros"] / 1e6, 2) + " mi", TSE_LOG, "outros / 1e6")

    # ---------- municípios do mapa: com 2022 e centroide (5.570) ----------
    d = base.merge(cent[["cd_ibge7", "lon", "lat"]], on="cd_ibge7", how="inner")
    d = d[d.validos_22.notna() & d.pct_ab_22.notna()].reset_index(drop=True)
    put("n_mapa", len(d), br(len(d), 0), f"{BASE} + {CENT}", "municípios com 2022, 2026 e centroide IBGE (sem Boa Esperança do Norte/MT)")
    d["pct_lula_22"] = 100 * d.lula_22 / d.validos_22
    d["pct_bols_22"] = 100 * d.bolsonaro_22 / d.validos_22

    l22, v22 = d.lula_22.sum(), d.validos_22.sum()
    put("lula_pct22", 100 * l22 / v22, br(100 * l22 / v22) + "%", BASE, "soma lula_22 / soma validos_22 (5.570 do mapa)")
    put("bols_pct22", 100 * d.bolsonaro_22.sum() / v22, br(100 * d.bolsonaro_22.sum() / v22) + "%", BASE, "soma bolsonaro_22 / soma validos_22")
    perda = (l22 - d.lula_26.sum()) / 1e6
    put("lula_perda_mi", perda, br(perda, 1) + " milhões", BASE, "(soma lula_22 − soma lula_26) / 1e6, 5.570 do mapa")
    caiu = 100 * (d.pct_lula_26 < d.pct_lula_22).mean()
    put("pct_cid_lula_caiu", caiu, br(caiu, 0) + "%", BASE, "% de municípios com pct_lula_26 < 100*lula_22/validos_22")
    g = d.groupby("uf")[["lula_22", "validos_22", "lula_26", "validos_26", "flavio_26", "bolsonaro_22"]].sum()
    n_uf = int((g.lula_26 / g.validos_26 < g.lula_22 / g.validos_22).sum())
    put("n_uf_lula_caiu", n_uf, br(n_uf, 0), BASE, "UFs em que a fatia de Lula (votos somados por UF) caiu")
    put("n_uf", len(g), br(len(g), 0), BASE, "número de UFs")

    vir = int(((d.venc_22 == "13") & (d.venc_26 == "22")).sum())
    inv = int(((d.venc_22 == "22") & (d.venc_26 == "13")).sum())
    put("viradas", vir, br(vir, 0), BASE, "venc_22 == 13 e venc_26 == 22")
    put("viradas_inv", inv, br(inv, 0), BASE, "venc_22 == 22 e venc_26 == 13")
    andou = 100 * (d.delta_margem > 0).mean()
    put("pct_andou_pl", andou, br(andou, 0) + "%", BASE, "% de municípios com delta_margem > 0 (margem PL − Lula subiu)")
    rm = wcorr(d.margem_22, d.margem_26, d.eleitorado_26)
    put("r_m22_m26", rm, br(rm, 2), BASE, "correlação ponderada por eleitorado_26, margem_22 x margem_26")
    mn22 = 100 * (d.bolsonaro_22.sum() - l22) / v22
    mn26 = 100 * (d.flavio_26.sum() - d.lula_26.sum()) / d.validos_26.sum()
    put("desloc_nac", mn26 - mn22, br(mn26 - mn22, 1) + " pontos", BASE,
        "margem nacional (PL − Lula, votos somados) 2026 menos 2022, 5.570 do mapa")

    # ---------- a divisão: cidades x eleitores ----------
    w = d.validos_26
    perto = d.margem_26.abs() < 5
    put("n_cid_perto", perto.sum(), br(perto.sum(), 0), BASE, "municípios com |margem_26| < 5 pontos")
    put("pct_cid_perto", 100 * perto.mean(), br(100 * perto.mean()) + "%", BASE, "% de municípios com |margem_26| < 5")
    put("pct_vot_perto", 100 * w[perto].sum() / w.sum(), br(100 * w[perto].sum() / w.sum()) + "%", BASE,
        "soma validos_26 dos municípios com |margem_26| < 5 / soma validos_26")
    peq = d.eleitorado_26 < 10000
    put("pct_cid_10k", 100 * peq.mean(), br(100 * peq.mean()) + "%", BASE, "% de municípios com eleitorado_26 < 10.000")
    put("pct_vot_10k", 100 * w[peq].sum() / w.sum(), br(100 * w[peq].sum() / w.sum(), 0) + "%", BASE,
        "soma validos_26 dos municípios com eleitorado_26 < 10.000 / soma validos_26")
    for lado, cond, nome in (("lula", d.margem_26 <= -20, "lula20"), ("flavio", d.margem_26 >= 20, "flavio20")):
        put(f"pct_cid_{nome}", 100 * cond.mean(), br(100 * cond.mean(), 0) + "%", BASE, f"% de municípios com margem_26 {'≤ −20' if lado == 'lula' else '≥ 20'}")
        put(f"pct_vot_{nome}", 100 * w[cond].sum() / w.sum(), br(100 * w[cond].sum() / w.sum(), 0) + "%", BASE,
            f"soma validos_26 desses municípios / soma validos_26")

    # ---------- pontas de 10% do eleitorado (mesmo corte do site original, que não o declara) ----------
    # municípios ordenados pela variável; a ponta reúne as cidades que somam 10% do eleitorado_26; votos somados
    def decil(col, ponta, cand):
        s = d.sort_values(col)
        cw = s.eleitorado_26.cumsum() / s.eleitorado_26.sum()
        sel = s[cw <= 0.1] if ponta == 1 else s[cw > 0.9]
        return 100 * sel[f"{cand}_26"].sum() / sel.validos_26.sum(), sel[col].min(), sel[col].max()

    for nome, col, ponta, cand in (("bf_d10_lula", "pct_bf_26", 10, "lula"), ("bf_d1_flavio", "pct_bf_26", 1, "flavio"),
                                   ("renda_d1_lula", "renda_pc_media", 1, "lula"), ("renda_d10_flavio", "renda_pc_media", 10, "flavio"),
                                   ("ev_d1_lula", "pct_evangelicas", 1, "lula"), ("ev_d10_flavio", "pct_evangelicas", 10, "flavio")):
        val, lo, hi = decil(col, ponta, cand)
        put(nome, val, br(val) + "%", BASE, f"ponta {'inferior' if ponta == 1 else 'superior'} de 10% do eleitorado_26, municípios ordenados por {col}; soma {cand}_26 / soma validos_26")
        log[nome + "_faixa"] = [float(lo), float(hi)]
        lim = hi if ponta == 1 else lo
        txt = ("R$ " + br(round(lim, -1), 0)) if col == "renda_pc_media" else (br(lim, 0) + "%")
        put(nome + "_lim", lim, txt, BASE, f"{'máximo' if ponta == 1 else 'mínimo'} de {col} na ponta ({'arredondado à dezena' if col == 'renda_pc_media' else 'inteiro'})")

    # ---------- parâmetros de texto (cortes escolhidos por nós; registrados para não haver número solto) ----------
    put("ponta", 10, "10%", "parâmetro do build", "fatia do eleitorado em cada ponta (mesmo corte do site original)")
    put("lim_empate", 5, "5", "parâmetro do build", "|margem_26| < 5 pontos = perto do empate")
    put("lim_peq", 10, "10", "parâmetro do build", "cidade pequena: eleitorado_26 < 10 mil")
    put("lim_bf_alto", 80, "80%", "parâmetro do build", "limite do eixo no site original")
    put("lim_bf_max", 100, "100%", "parâmetro do build", "população inteira")
    q5 = pd.qcut(d.pct_bf_26, 5, labels=False) == 4
    a5 = 100 * (d.delta_margem[q5] > 0).mean()
    put("pct_andou_q5", a5, br(a5, 0) + "%", BASE, "quinto de municípios com maior pct_bf_26: % com delta_margem > 0")

    # ---------- exemplo ilustrativo (Bonfim do Piauí, arredondado) ----------
    bon = d.loc[d.cd_ibge7 == 2201929].iloc[0]
    put("bonfim_bf", bon.pct_bf_26, br(bon.pct_bf_26) + "%", BASE, "linha cd_ibge7=2201929, pct_bf_26")
    put("bonfim_lula", bon.pct_lula_26, br(bon.pct_lula_26) + "%", BASE, "linha cd_ibge7=2201929, pct_lula_26")
    er, el_ = int(br(bon.pct_bf_26, 0)), int(br(bon.pct_lula_26, 0))
    put("ex_recebe", er, str(er), BASE, "exemplo ilustrativo: pct_bf_26 de Bonfim do Piauí arredondado")
    put("ex_lula", el_, str(el_), BASE, "exemplo ilustrativo: pct_lula_26 de Bonfim do Piauí arredondado")
    put("ex_outros", 100 - el_, str(100 - el_), BASE, "exemplo ilustrativo: 100 − ex_lula")

    # ---------- Bolsa Família e renda ----------
    r_rb = np.corrcoef(np.log(d.renda_pc_media), d.pct_bf_26)[0, 1]
    put("r_renda_bf", r_rb, br(r_rb, 2), BASE, "correlação de Pearson sem peso, log(renda_pc_media) x pct_bf_26")
    put("r_bf26", wcorr(d.pct_bf_26, d.margem_26, d.eleitorado_26), br(wcorr(d.pct_bf_26, d.margem_26, d.eleitorado_26), 2), BASE,
        "correlação ponderada por eleitorado_26, pct_bf_26 x margem_26")
    r_rm = wcorr(np.log(d.renda_pc_media), d.margem_26, d.eleitorado_26)
    put("r_renda26", r_rm, br(r_rm, 2), BASE, "correlação ponderada por eleitorado_26, log(renda_pc_media) x margem_26")
    put("n_bf80", (d.pct_bf_26 > 80).sum(), br((d.pct_bf_26 > 80).sum(), 0), BASE, "municípios com pct_bf_26 > 80")
    put("n_bf100", (d.pct_bf_26 > 100).sum(), br((d.pct_bf_26 > 100).sum(), 0), BASE, "municípios com pct_bf_26 > 100")
    put("bf_max", d.pct_bf_26.max(), br(d.pct_bf_26.max()) + "%", BASE, "máximo de pct_bf_26")
    put("n_ab100", (d.pct_ab_22 > 100).sum(), br((d.pct_ab_22 > 100).sum(), 0), BASE, "municípios com pct_ab_22 > 100")

    # ---------- renda: spline cúbica restrita ponderada (descritiva) ----------
    xr = np.log(d.renda_pc_media.values)
    knots = np.quantile(xr, [0.05, 0.275, 0.5, 0.725, 0.95])
    X = np.column_stack([np.ones(len(xr)), rcs_basis(xr, knots)])
    sw = np.sqrt(w.values)
    beta, *_ = np.linalg.lstsq(X * sw[:, None], d.margem_26.values * sw, rcond=None)
    grade = np.linspace(np.quantile(xr, 0.005), np.quantile(xr, 0.995), 120)
    yg = np.column_stack([np.ones(len(grade)), rcs_basis(grade, knots)]) @ beta
    ip = int(np.argmax(yg))
    put("renda_pico", np.exp(grade[ip]), "R$ " + br(round(np.exp(grade[ip]), -2), 0), BASE,
        "renda_pc_media no máximo da curva (spline cúbica restrita, 5 nós nos quantis 5/27,5/50/72,5/95% de log renda, mínimos quadrados ponderados por validos_26, margem_26), arredondada à centena")
    put("renda_pico_m", yg[ip], br(yg[ip], 0, sinal=True), BASE, "margem_26 prevista pela curva no máximo")
    put("renda_fim_m", yg[-1], br(yg[-1], 0, sinal=True), BASE, "margem_26 prevista pela curva no percentil 99,5 de renda")
    log["spline_renda"] = {"nos_log": knots.tolist(), "beta": beta.tolist()}
    curva_renda = [[round(float(np.exp(a)), 1), round(float(b), 2)] for a, b in zip(grade, yg)]

    # ---------- evangélicos ----------
    r_ev = wcorr(d.pct_evangelicas, d.margem_26, d.eleitorado_26)
    put("r_ev26", r_ev, br(r_ev, 2), BASE, "correlação ponderada por eleitorado_26, pct_evangelicas x margem_26")

    # ---------- 2022: Auxílio Brasil ----------
    r22 = wcorr(d.pct_ab_22, d.margem_22, d.eleitorado_26)
    put("r_ab22", r22, br(r22, 2), BASE, "correlação ponderada por eleitorado_26, pct_ab_22 x margem_22")
    r_abbf = np.corrcoef(d.pct_ab_22, d.pct_bf_26)[0, 1]
    put("r_ab_bf", r_abbf, br(r_abbf, 2), BASE, "correlação sem peso, pct_ab_22 x pct_bf_26")
    quint = {}
    for ano, expo, b_, nb in (("22", "pct_ab_22", "bolsonaro_22", "bolsonaro"), ("26", "pct_bf_26", "flavio_26", "flavio")):
        q = pd.qcut(d[expo], 5, labels=False)
        gq = d.groupby(q).agg(lo=(expo, "min"), hi=(expo, "max"), a=(f"lula_{ano}", "sum"), b=(b_, "sum"), v=(f"validos_{ano}", "sum"))
        quint[ano] = []
        for i in range(5):
            pa, pb = 100 * gq.a.iloc[i] / gq.v.iloc[i], 100 * gq.b.iloc[i] / gq.v.iloc[i]
            put(f"q{ano}_{i + 1}_lula", pa, br(pa) + "%", BASE, f"quintil {i + 1} de municípios (contagem igual) por {expo}; soma lula_{ano} / soma validos_{ano}")
            put(f"q{ano}_{i + 1}_{nb}", pb, br(pb) + "%", BASE, f"idem; soma {b_} / soma validos_{ano}")
            put(f"q{ano}_{i + 1}_lo", gq.lo.iloc[i], br(gq.lo.iloc[i], 0) + "%", BASE, f"quintil {i + 1}: mínimo de {expo}")
            put(f"q{ano}_{i + 1}_hi", gq.hi.iloc[i], br(gq.hi.iloc[i], 0) + "%", BASE, f"quintil {i + 1}: máximo de {expo}")
            quint[ano].append({"lula": f"q{ano}_{i + 1}_lula", "outro": f"q{ano}_{i + 1}_{nb}", "lo": f"q{ano}_{i + 1}_lo", "hi": f"q{ano}_{i + 1}_hi"})

    ec = pd.read_csv(ROOT / EC123, dtype={"inciso": str})
    ec_rows = []
    for k, lin in ec.iterrows():
        bi = lin.limite_reais / 1e9
        casas = 0 if bi == int(bi) else (1 if round(bi, 1) == bi else 2)
        put(f"ec_{lin.inciso}", bi, "R$ " + br(bi, casas) + " bi", EC123, f"linha {k + 2} (inciso {lin.inciso}, '{lin.rotulo}'), limite_reais / 1e9")
        if pd.notna(lin.mensal_reais):
            put(f"ec_{lin.inciso}_mensal", lin.mensal_reais, "R$ " + br(lin.mensal_reais, 0), EC123, f"linha {k + 2}, mensal_reais")
        if lin.inciso != "total":
            ec_rows.append((lin.inciso, lin.rotulo, bi))

    # ---------- ajuste: contrastes P90 x P10 (IC agrupado por UF) ----------
    c = pd.read_csv(ROOT / CONTR)
    contr = []
    for modelo, nome in (("A22: AB + UF", "a22"), ("B22: AB + UF + Censo", "aj22"), ("A26: BF + UF", "a26"), ("B26: BF + UF + Censo", "aj26")):
        m = (c.modelo == modelo) & (c.erro_padrao == "clu")
        lin, idx = c[m].iloc[0], c.index[m][0] + 2
        como = f"linha {idx} (modelo '{modelo}', IC 95% com erro agrupado por UF)"
        put(nome, lin.diff_margem_p90_menos_p10, br(lin.diff_margem_p90_menos_p10, 0, sinal=True), CONTR, como + ", diff_margem_p90_menos_p10")
        put(nome + "_li", lin.li, br(lin.li, 0, sinal=True), CONTR, como + ", li")
        put(nome + "_ls", lin.ls, br(lin.ls, 0, sinal=True), CONTR, como + ", ls")
        put(nome + "_p10", lin.p10, br(lin.p10, 0) + "%", CONTR, como + ", p10")
        put(nome + "_p90", lin.p90, br(lin.p90, 0) + "%", CONTR, como + ", p90")
        contr.append({"k": nome, "est": float(lin.diff_margem_p90_menos_p10), "li": float(lin.li), "ls": float(lin.ls)})
    for ano in ("22", "26"):
        red = 100 * (1 - NUM[f"aj{ano}"]["valor"] / NUM[f"a{ano}"]["valor"])
        put(f"red{ano}", red, br(red, 0) + "%", CONTR, f"1 − aj{ano} / a{ano} (estimativas pontuais)")

    # ---------- UFs (ordenadas pela margem 2026, Lula primeiro) ----------
    # 2026 por UF com os 5.571 municípios do TSE (inclui Boa Esperança do Norte/MT); 2022 só existe para os 5.570
    g26 = base.groupby("uf")[["flavio_26", "lula_26", "validos_26"]].sum()
    g["m26"] = 100 * (g26.flavio_26 - g26.lula_26) / g26.validos_26
    g["m22"] = 100 * (g.bolsonaro_22 - g.lula_22) / g.validos_22
    virs = d[(d.venc_22 == "13") & (d.venc_26 == "22")].groupby("uf").size()
    lista_uf = []
    for uf, lin in g.sort_values("m26").iterrows():
        nv = int(virs.get(uf, 0))
        cas = lambda m: 2 if abs(m) < 1 else 1  # margem abaixo de 1 ponto com duas casas (Amapá)
        put(f"uf_{uf}_m26", lin.m26, br(abs(lin.m26), cas(lin.m26)), BASE, f"UF {uf}: |soma flavio_26 − soma lula_26| / soma validos_26 (5.571 municípios)")
        put(f"uf_{uf}_m22", lin.m22, br(abs(lin.m22), cas(lin.m22)), BASE, f"UF {uf}: |soma bolsonaro_22 − soma lula_22| / soma validos_22")
        put(f"uf_{uf}_vir", nv, br(nv, 0), BASE, f"UF {uf}: municípios com venc_22 == 13 e venc_26 == 22")
        lista_uf.append({"uf": uf, "nome": ufs[uf][0], "m26": float(lin.m26), "m22": float(lin.m22)})
    return d, log, curva_renda, quint, ec_rows, contr, lista_uf


def dados_cidades(d, ufs):
    r1 = lambda s: [None if pd.isna(x) else round(float(x), 1) for x in s]
    i0 = lambda s: [int(x) for x in s]
    return {
        "id": i0(d.cd_ibge7), "nome": d.nome.tolist(), "uf": d.uf.tolist(),
        "slug": [slug(n) for n in d.nome],
        "lon": [round(float(x), 3) for x in d.lon], "lat": [round(float(x), 3) for x in d.lat],
        "el": i0(d.eleitorado_26), "v26": i0(d.validos_26), "l26": i0(d.lula_26), "f26": i0(d.flavio_26),
        "v22": i0(d.validos_22), "l22": i0(d.lula_22), "b22": i0(d.bolsonaro_22),
        "bf": r1(d.pct_bf_26), "ab": r1(d.pct_ab_22), "rd": [int(round(x)) for x in d.renda_pc_media],
        "ev": r1(d.pct_evangelicas), "ur": r1(d.pct_urbana),
        "ufs": {k: {"nome": v[0], "regiao": v[1]} for k, v in ufs.items()},
    }


def malha_uf():
    g = json.loads((ROOT / MALHA_UF).read_text(encoding="utf-8"))
    out = []
    for ft in g["features"]:
        geom = ft["geometry"]
        polys = [geom["coordinates"]] if geom["type"] == "Polygon" else geom["coordinates"]
        for p in polys:
            anel = p[0]
            pts, last = [], None
            for lon, lat in anel:
                q = (round(lon, 2), round(lat, 2))
                if q != last:
                    pts.append(list(q))
                    last = q
            if len(pts) > 3:
                out.append(pts)
    return out


def fontes_css():
    from fontTools import subset
    from fontTools.ttLib import TTFont
    faces = [("Plex Cond", 400, "IBMPlexSansCondensed-Regular.ttf"), ("Plex Cond", 600, "IBMPlexSansCondensed-SemiBold.ttf"),
             ("Plex Cond", 700, "IBMPlexSansCondensed-Bold.ttf"), ("Plex Mono", 500, "IBMPlexMono-Medium.ttf")]
    uni = list(range(0x20, 0x7F)) + list(range(0xA0, 0x100)) + [0x2013, 0x2014, 0x2018, 0x2019, 0x201C, 0x201D, 0x2022, 0x2026,
                                                               0x2190, 0x2191, 0x2192, 0x2193, 0x2212, 0x00D7, 0x2009, 0x202F, 0x2248, 0x2264, 0x2265]
    css = []
    for fam, peso, arq in faces:
        f = TTFont(FONTS / arq)
        opts = subset.Options()
        opts.flavor = "woff2"
        opts.layout_features = ["kern", "liga", "tnum", "lnum"]
        sub = subset.Subsetter(opts)
        sub.populate(unicodes=uni)
        sub.subset(f)
        buf = io.BytesIO()
        f.flavor = "woff2"
        f.save(buf)
        b64 = base64.b64encode(buf.getvalue()).decode()
        css.append(f"@font-face{{font-family:'{fam}';font-weight:{peso};font-style:normal;font-display:swap;"
                   f"src:url(data:font/woff2;base64,{b64}) format('woff2')}}")
    return "\n".join(css)


def html_uf(lista_uf):
    linhas = []
    for u in lista_uf:
        k = u["uf"]
        lado26 = "Lula" if u["m26"] < 0 else "Flávio"
        lado22 = "Lula" if u["m22"] < 0 else "Bolsonaro"
        nv = int(NUM[f"uf_{k}_vir"]["valor"])
        vir = ('<span class="lg">' + ("nenhuma virou" if nv == 0 else (f"{{{{uf_{k}_vir}}}} virou" if nv == 1 else f"{{{{uf_{k}_vir}}}} viraram"))
               + f'</span><span class="ab num">{{{{uf_{k}_vir}}}}</span>')
        linhas.append(
            f'<tr data-uf="{k.lower()}" data-m26="{round(u["m26"], 2)}" data-m22="{round(u["m22"], 2)}">'
            f'<th scope="row">{u["nome"]}</th>'
            f'<td class="uf-barra" aria-hidden="true"><span class="eixo"><i></i><b></b></span></td>'
            f'<td class="num {"c-lula" if u["m26"] < 0 else "c-pl"}"><span class="lg">{lado26} </span><span class="ab">{lado26[0]} </span>+{{{{uf_{k}_m26}}}}</td>'
            f'<td class="num sec"><span class="lg">{lado22} </span><span class="ab">{lado22[0]} </span>+{{{{uf_{k}_m22}}}}</td>'
            f'<td class="sec">{vir}</td></tr>')
    return "\n".join(linhas)


def html_quintis(quint):
    linhas = []
    for i in range(5):
        a, b = quint["22"][i], quint["26"][i]
        rot = ["menos programa", "", "", "", "mais programa"][i]
        linhas.append(
            f'<tr><th scope="row">Q{{{{qn_{i + 1}}}}}<span class="sec"> {rot}</span></th>'
            f'<td class="num sec">{{{{{a["lo"]}}}}}–{{{{{a["hi"]}}}}}</td>'
            f'<td><div class="qb"><span class="qb-l" data-v="{{{{{a["lula"]}}}}}"></span><span class="qb-o" data-v="{{{{{a["outro"]}}}}}"></span></div>'
            f'<span class="num c-lula">{{{{{a["lula"]}}}}}</span> <span class="num c-pl">{{{{{a["outro"]}}}}}</span></td>'
            f'<td class="num sec">{{{{{b["lo"]}}}}}–{{{{{b["hi"]}}}}}</td>'
            f'<td><div class="qb"><span class="qb-l" data-v="{{{{{b["lula"]}}}}}"></span><span class="qb-o" data-v="{{{{{b["outro"]}}}}}"></span></div>'
            f'<span class="num c-lula">{{{{{b["lula"]}}}}}</span> <span class="num c-pl">{{{{{b["outro"]}}}}}</span></td></tr>')
    return "\n".join(linhas)


def html_ec(ec_rows):
    mx = max(r[2] for r in ec_rows)
    return "\n".join(
        f'<div class="ec-l"><span class="ec-r">{rot}</span><span class="ec-b"><i style="width:{100 * bi / mx:.1f}%"></i></span>'
        f'<span class="num">{{{{ec_{inc}}}}}</span></div>' for inc, rot, bi in ec_rows)


def html_contr(contr):
    rot = {"a22": ("2022 · Auxílio Brasil", "só o estado"), "aj22": ("2022 · Auxílio Brasil", "cidades parecidas"),
           "a26": ("2026 · Bolsa Família", "só o estado"), "aj26": ("2026 · Bolsa Família", "cidades parecidas")}
    out = []
    for c in contr:
        k = c["k"]
        out.append(f'<div class="ct-l {"ct-aj" if k.startswith("aj") else ""}" data-est="{c["est"]}" data-li="{c["li"]}" data-ls="{c["ls"]}">'
                   f'<span class="ct-r">{rot[k][0]}<br><span class="sec">{rot[k][1]}</span></span>'
                   f'<span class="ct-g" aria-hidden="true"><i class="ct-ic"></i><b class="ct-pt"></b></span>'
                   f'<span class="num">{{{{{k}}}}} <span class="sec">({{{{{k}_li}}}} a {{{{{k}_ls}}}})</span></span></div>')
    return "\n".join(out)


def main():
    t0 = datetime.now()
    base, cent, ufs = carregar()
    d, log, curva_renda, quint, ec_rows, contr, lista_uf = numeros(base, cent, ufs)
    for i in range(5):  # rótulo do quintil (1 a 5), contagem e não dado
        NUM[f"qn_{i + 1}"] = {"valor": i + 1, "texto": str(i + 1), "fonte": "rótulo", "como": "número do quintil"}

    cid = dados_cidades(d, ufs)
    payload = {"c": cid, "uf_geo": malha_uf(), "curva_renda": curva_renda}
    dados_txt = json.dumps(payload, ensure_ascii=False, separators=(",", ":"))

    tpl = (SRC / "index.html").read_text(encoding="utf-8")
    css = (SRC / "style.css").read_text(encoding="utf-8")
    js = (SRC / "app.js").read_text(encoding="utf-8")
    blocos = {"uf_lista": html_uf(lista_uf), "quintis": html_quintis(quint), "ec_barras": html_ec(ec_rows),
              "contrastes": html_contr(contr)}
    for k, v in blocos.items():
        tpl = tpl.replace("{{!" + k + "}}", v)

    usados = []

    def sub(m):
        k = m.group(1)
        if k not in NUM:
            raise KeyError(f"placeholder sem número registrado: {k}")
        usados.append(k)
        return NUM[k]["texto"]

    html = re.sub(r"\{\{([a-zA-Z0-9_]+)\}\}", sub, tpl)
    sobra = re.findall(r"\{\{[^}]*\}\}", html)
    if sobra:
        raise ValueError(f"placeholders não resolvidos: {sobra[:5]}")
    html = (html.replace("/*__FONTES__*/", fontes_css()).replace("/*__CSS__*/", css)
            .replace("/*__DADOS__*/", dados_txt).replace("/*__APP__*/", js))
    DIST.mkdir(parents=True, exist_ok=True)
    (DIST / "index.html").write_text(html, encoding="utf-8")
    dic = {"campos": {"id": "código IBGE", "nome": "nome IBGE", "uf": "UF", "lon/lat": "centroide IBGE", "el": "eleitorado 2026 (TSE)",
                      "v26/l26/f26": "válidos, Lula, Flávio, 1º turno 2026 (TSE)", "v22/l22/b22": "válidos, Lula, Bolsonaro, 1º turno 2022 (TSE)",
                      "bf": "% da população em famílias do Bolsa Família, set/2026 (MDS ÷ Censo 2022)",
                      "ab": "% da população em famílias do Auxílio Brasil, set/2022 (MDS ÷ Censo 2022)",
                      "rd": "renda média domiciliar per capita, R$ (IBGE, Censo 2022)", "ev": "% evangélicos (Censo 2022)",
                      "ur": "% população urbana (Censo 2022)"},
           "gerado_em": t0.strftime("%Y-%m-%d %H:%M")}
    (DIST / "dados.json").write_text(json.dumps({"dicionario": dic, **cid}, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    (DIST / "CNAME").write_text(DOMINIO + "\n", encoding="utf-8")
    (SITE / "registro_numeros.json").write_text(json.dumps(NUM, ensure_ascii=False, indent=1), encoding="utf-8")
    log.update({"executado_em": t0.isoformat(timespec="seconds"), "n_numeros": len(NUM), "placeholders_usados": sorted(set(usados)),
                "n_placeholders": len(usados), "html_kb": round(len(html.encode()) / 1024, 1), "dados_kb": round(len(dados_txt.encode()) / 1024, 1)})
    (ROOT / "logs" / "site_build_log.json").write_text(json.dumps(log, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"ok: {len(NUM)} números, {len(set(usados))} usados; index.html {log['html_kb']} kB (dados {log['dados_kb']} kB)")
    for k in ("flavio_pct", "lula_pct", "dif_votos", "viradas", "pct_andou_pl", "bf_d10_lula", "bf_d1_flavio", "renda_d1_lula",
              "ev_d1_lula", "ev_d10_flavio", "renda_d10_flavio", "n_cid_perto", "pct_cid_perto", "pct_vot_perto", "r_renda_bf",
              "renda_pico", "renda_pico_m", "renda_fim_m", "r_m22_m26", "desloc_nac", "r_ev26", "r_renda26", "red22", "red26"):
        print(f"  {k:18s} {NUM[k]['texto']}")


if __name__ == "__main__":
    sys.exit(main())
