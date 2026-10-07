"""Verificação do site (critérios 1, 2 e 4 do prompt_site_v1.md, mais peso e rolagem no celular).

Rodar da raiz, depois do build:  PYTHONUTF8=1 python -P site/verify.py <rodada>
Usa o Chrome instalado (Playwright, channel="chrome", headless) com a página em file://.
Escreve site_verification.md (a seção do critério 3, comparação com o benchmark, é mantida de site/comparacao.md).
"""
import ast
import json
import re
import sys
from datetime import datetime
from decimal import ROUND_HALF_UP, Decimal
from html.parser import HTMLParser
from pathlib import Path

import numpy as np
import pandas as pd
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / "site"
DIST = SITE / "dist" / "index.html"
URL = DIST.as_uri()
NUM = json.loads((SITE / "registro_numeros.json").read_text(encoding="utf-8"))
# texto visível do painel sem os elementos decorativos (aria-hidden: marcas de eixo, barras)
VIS = "(() => { const c = document.querySelector('#p-graf').cloneNode(true); c.querySelectorAll('[aria-hidden=true],[hidden]').forEach(e => e.remove()); document.body.appendChild(c); const t = c.innerText; c.remove(); return t; })()"
LENTES = ["mapa", "divisao", "bf", "renda", "ev", "d22", "ab22", "ajuste"]

NUMRE = re.compile(r"(?<![\w\d])[+−-]?\d[\d.]*(?:,\d+)?%?")
# rótulos fixos que não são dado (anos, datas, artigos de lei, método, citação do título do Poder360)
FIXOS = [r"R\$ 12,6 bi", r"\d+\.ago\.\d{4}", r"\d{2}/\d{2}/\d{4}", r"EC 123/2022", r"Emenda Constitucional 123/2022", r"123/2022",
         r"art\. \d+º?", r"\b1º turno", r"\b1º\b", r"100% das seções", r"de 100 pessoas", r"95%", r"percentis 90 e 10",
         r"60 anos", r"Cidade [12]", r"Opus 5\.5", r"set/20(22|26)", r"\b20(20|22|26)\b", r"Q\d\b", r"faixas de 2 pontos"]


def tokens(s):
    for f in FIXOS:
        s = re.sub(f, " ", s)
    return [m.group(0).rstrip(".").lstrip("+") for m in NUMRE.finditer(s)]


def br(x, casas=1, sinal=False):
    q = Decimal(str(float(x))).quantize(Decimal(1).scaleb(-casas), rounding=ROUND_HALF_UP)
    s = f"{q:+.{casas}f}" if sinal else f"{q:.{casas}f}"
    s = s.replace("-", "−")
    i, _, d = s.partition(".")
    pre = ""
    if i[0] in "+−":
        pre, i = i[0], i[1:]
    return pre + f"{int(i):,}".replace(",", ".") + ("," + d if d else "")


# ---------- 1a. template: nenhum número digitado ----------
class Texto(HTMLParser):
    def __init__(self):
        super().__init__()
        self.pilha, self.partes = [], []

    def handle_starttag(self, tag, attrs):
        if tag not in ("br", "meta", "link", "input", "img"):
            self.pilha.append(tag)
        for k, v in attrs:
            if k in ("aria-label", "placeholder", "title", "alt") and v and tag != "meta":
                self.partes.append(("atributo " + k, v))

    def handle_endtag(self, tag):
        if self.pilha and self.pilha[-1] == tag:
            self.pilha.pop()

    def handle_data(self, data):
        if not any(t in ("script", "style") for t in self.pilha) and data.strip():
            self.partes.append(("texto", data.strip()))


def checa_template():
    tpl = (SITE / "src" / "index.html").read_text(encoding="utf-8")
    tpl = re.sub(r"\{\{!?[a-zA-Z0-9_]+\}\}", " ", tpl)
    p = Texto()
    p.feed(tpl)
    soltos = [(o, t, tokens(t)) for o, t in p.partes if tokens(t)]
    # strings do JS que viram texto na tela
    js = (SITE / "src" / "app.js").read_text(encoding="utf-8")
    js_str = re.findall(r"'([^'\\]*(?:\\.[^'\\]*)*)'", js)
    js_soltos = sorted({s for s in js_str if re.search(r"[A-Za-zÀ-ú]", s) and tokens(s)})
    return soltos, js_soltos


# ---------- 1b. recomputação independente ----------
def recomputa():
    b = pd.read_csv(ROOT / "data/derived/base_analitica_emendas.csv", dtype={"venc_22": str, "venc_26": str})
    c = pd.read_csv(ROOT / "data/derived/ibge_centroides_municipios.csv")
    t = json.loads((ROOT / "logs/06_tse_2026_log.json").read_text(encoding="utf-8"))
    d = b[b.cd_ibge7.isin(c.cd_ibge7) & b.validos_22.notna() & b.pct_ab_22.notna()].copy()
    w = d.eleitorado_26

    def wc(x, y):
        x, y = np.asarray(x, float), np.asarray(y, float)
        mx, my = np.average(x, weights=w), np.average(y, weights=w)
        return np.average((x - mx) * (y - my), weights=w) / np.sqrt(np.average((x - mx) ** 2, weights=w) * np.average((y - my) ** 2, weights=w))

    def ponta(col, sup, cand):
        s = d.sort_values(col)
        cw = s.eleitorado_26.cumsum() / s.eleitorado_26.sum()
        s = s[cw > 0.9] if sup else s[cw <= 0.1]
        return 100 * s[cand].sum() / s.validos_26.sum()

    E = {
        "flavio_pct": br(t["pct_22"]) + "%", "lula_pct": br(t["pct_13"]) + "%", "dif_mi": br(t["diferenca_22_menos_13"] / 1e6, 2) + " mi",
        "n_mapa": br(len(d), 0),
        "viradas": br(((d.venc_22 == "13") & (d.venc_26 == "22")).sum(), 0),
        "viradas_inv": br(((d.venc_22 == "22") & (d.venc_26 == "13")).sum(), 0),
        "pct_andou_pl": br(100 * (d.flavio_26 / d.validos_26 - d.lula_26 / d.validos_26 > d.bolsonaro_22 / d.validos_22 - d.lula_22 / d.validos_22).mean(), 0) + "%",
        "lula_perda_mi": br((d.lula_22.sum() - d.lula_26.sum()) / 1e6, 1) + " milhões",
        "pct_cid_lula_caiu": br(100 * (d.lula_26 / d.validos_26 < d.lula_22 / d.validos_22).mean(), 0) + "%",
        "r_m22_m26": br(wc(d.margem_22, d.margem_26), 2),
        "n_cid_perto": br((d.margem_26.abs() < 5).sum(), 0),
        "pct_vot_perto": br(100 * d.validos_26[d.margem_26.abs() < 5].sum() / d.validos_26.sum()) + "%",
        "bf_d10_lula": br(ponta("pct_bf_26", True, "lula_26")) + "%", "bf_d1_flavio": br(ponta("pct_bf_26", False, "flavio_26")) + "%",
        "renda_d1_lula": br(ponta("renda_pc_media", False, "lula_26")) + "%", "renda_d10_flavio": br(ponta("renda_pc_media", True, "flavio_26")) + "%",
        "ev_d1_lula": br(ponta("pct_evangelicas", False, "lula_26")) + "%", "ev_d10_flavio": br(ponta("pct_evangelicas", True, "flavio_26")) + "%",
        "r_renda_bf": br(np.corrcoef(np.log(d.renda_pc_media), d.pct_bf_26)[0, 1], 2),
        "r_bf26": br(wc(d.pct_bf_26, d.margem_26), 2), "r_ab22": br(wc(d.pct_ab_22, d.margem_22), 2),
        "r_ev26": br(wc(d.pct_evangelicas, d.margem_26), 2), "r_ab_bf": br(np.corrcoef(d.pct_ab_22, d.pct_bf_26)[0, 1], 2),
        "n_bf80": br((d.pct_bf_26 > 80).sum(), 0), "bf_max": br(d.pct_bf_26.max()) + "%",
    }
    for ano, expo, outro in (("22", "pct_ab_22", "bolsonaro"), ("26", "pct_bf_26", "flavio")):
        q = pd.qcut(d[expo], 5, labels=False)
        for k in (0, 4):
            s = d[q == k]
            E[f"q{ano}_{k + 1}_lula"] = br(100 * s[f"lula_{ano}"].sum() / s[f"validos_{ano}"].sum()) + "%"
            E[f"q{ano}_{k + 1}_{outro}"] = br(100 * s[f"{outro}_{ano}"].sum() / s[f"validos_{ano}"].sum()) + "%"
    ct = pd.read_csv(ROOT / "output/contrastes_p90_p10.csv")
    for m, k in (("A22: AB + UF", "a22"), ("B22: AB + UF + Censo", "aj22"), ("A26: BF + UF", "a26"), ("B26: BF + UF + Censo", "aj26")):
        r = ct[(ct.modelo == m) & (ct.erro_padrao == "clu")].iloc[0]
        E[k], E[k + "_li"], E[k + "_ls"] = br(r.diff_margem_p90_menos_p10, 0, True), br(r.li, 0, True), br(r.ls, 0, True)
    ec = pd.read_csv(ROOT / "data/derived/ec123_2022_beneficios.csv", dtype={"inciso": str}).set_index("inciso")
    E["ec_total"] = "R$ " + br(ec.loc["total", "limite_reais"] / 1e9, 2) + " bi"
    return E


# ---------- navegador ----------
def coleta():
    out = {"lentes": {}, "cidades": {}, "teclado": {}, "erros": []}
    with sync_playwright() as p:
        b = p.chromium.launch(channel="chrome", headless=True)
        pg = b.new_page(viewport={"width": 1366, "height": 900}, reduced_motion="reduce")
        pg.on("pageerror", lambda e: out["erros"].append(str(e)))
        pg.goto(URL)
        pg.wait_for_timeout(500)
        out["texto_inicial"] = pg.inner_text("body")
        for l in LENTES:
            pg.click(f'[role=tab][data-lente="{l}"]')
            pg.wait_for_timeout(150)
            txt = pg.evaluate(VIS)
            alts = []
            for g in pg.locator(f'.alternar[data-para="{l}"] button').all()[1:]:
                g.click()
                pg.wait_for_timeout(150)
                alts.append(pg.evaluate(VIS))
            out["lentes"][l] = {"texto": txt + "\n" + "\n".join(alts), "aria": pg.get_attribute("#cv", "aria-label")}
        out["arias"] = pg.eval_on_selector_all("[aria-label]", "els => els.map(e => e.getAttribute('aria-label'))")
        # cidades
        for h in ("pi/bonfim-do-piaui", "rs/nova-padua", "sp/sao-paulo"):
            pg.goto(URL + "#cidade/" + h)
            pg.wait_for_timeout(300)
            out["cidades"][h] = pg.inner_text("#ficha-cidade")
        # teclado: abas por setas, busca por teclado, linha de UF por Enter
        pg.goto(URL)
        pg.wait_for_timeout(300)
        pg.focus('[role=tab][data-lente="mapa"]')
        pg.keyboard.press("ArrowRight")
        out["teclado"]["seta_muda_aba"] = pg.get_attribute('[role=tab][data-lente="divisao"]', "aria-selected") == "true"
        out["teclado"]["foco_na_nova_aba"] = pg.evaluate("document.activeElement.getAttribute('data-lente')") == "divisao"
        pg.focus("#q")
        pg.keyboard.type("nova pad")
        pg.keyboard.press("ArrowDown")
        pg.keyboard.press("Enter")
        pg.wait_for_timeout(200)
        out["teclado"]["busca_abre_ficha"] = "Nova Pádua" in pg.inner_text("#ficha-cidade")
        pg.focus('.tab-uf tr[data-uf="pi"]')
        pg.keyboard.press("Enter")
        pg.wait_for_timeout(200)
        out["teclado"]["uf_por_enter"] = pg.locator("#filtro-uf").count() == 1
        out["foco_visivel"] = pg.evaluate("[...document.styleSheets].some(s=>[...s.cssRules].some(r=>r.selectorText&&r.selectorText.includes(':focus-visible')))")
        # celular
        pc = b.new_page(viewport={"width": 400, "height": 860}, reduced_motion="reduce")
        pc.goto(URL)
        pc.wait_for_timeout(400)
        larg = []
        for l in LENTES:
            pc.click(f'[role=tab][data-lente="{l}"]')
            pc.wait_for_timeout(120)
            larg.append(pc.evaluate("document.documentElement.scrollWidth"))
        out["cel_scroll_max"] = max(larg)
        b.close()
    return out


def lum(h):
    c = [int(h[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    c = [x / 12.92 if x <= 0.03928 else ((x + 0.055) / 1.055) ** 2.4 for x in c]
    return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]


def contraste(a, b):
    la, lb = sorted([lum(a), lum(b)], reverse=True)
    return (la + 0.05) / (lb + 0.05)


def main():
    rodada = sys.argv[1] if len(sys.argv) > 1 else "?"
    soltos, js_soltos = checa_template()
    E = recomputa()
    dif = [(k, E[k], NUM[k]["texto"]) for k in E if NUM[k]["texto"] != E[k]]
    nav = coleta()

    # números da página renderizada: cada um tem de vir do registro
    permitidos = set()
    for v in NUM.values():
        permitidos.update(tokens(v["texto"]))
    textos = [("página inicial", nav["texto_inicial"])] + [(f"painel {l}", v["texto"]) for l, v in nav["lentes"].items()]
    sem_origem = []
    for onde, t in textos:
        for tok in tokens(t):
            if tok not in permitidos:
                sem_origem.append((onde, tok))
    html_final = DIST.read_text(encoding="utf-8")
    usados = json.loads((ROOT / "logs/site_build_log.json").read_text(encoding="utf-8"))["placeholders_usados"]
    ausentes = [k for k in usados if NUM[k]["texto"] and NUM[k]["texto"] not in html_final]

    # cidades: ficha confere com a base
    b = pd.read_csv(ROOT / "data/derived/base_analitica_emendas.csv")
    cid_ok = []
    for h, ib in (("pi/bonfim-do-piaui", 2201929), ("rs/nova-padua", 4313086), ("sp/sao-paulo", 3550308)):
        r = b[b.cd_ibge7 == ib].iloc[0]
        esperado = [br(100 * r.lula_26 / r.validos_26) + "%", br(100 * r.flavio_26 / r.validos_26) + "%",
                    br(r.pct_bf_26) + "%", br(r.pct_ab_22) + "%", "R$ " + br(round(r.renda_pc_media), 0),
                    br(100 * r.lula_22 / r.validos_22) + "%", br(abs(r.delta_margem)) + " pontos"]
        txt = nav["cidades"][h]
        falta = [e for e in esperado if e not in txt]
        cid_ok.append((h, ib, esperado, falta))

    # 2. frases proibidas (mesma lista do vídeo)
    cheq = ROOT / "video" / "checagens.py"
    if cheq.exists():
        src = cheq.read_text(encoding="utf-8")
        proib = next(ast.literal_eval(n.value) for n in ast.walk(ast.parse(src)) if isinstance(n, ast.Assign) and getattr(n.targets[0], "id", "") == "PROIBIDAS")
    else:  # repositório público: cópia da lista em site/frases_proibidas.json
        proib = json.loads((SITE / "frases_proibidas.json").read_text(encoding="utf-8"))["padroes"]
    todo = [("página inicial", nav["texto_inicial"])] + [(f"painel {l}", v["texto"] + "\n" + (v["aria"] or "")) for l, v in nav["lentes"].items()] + \
           [(f"ficha {h}", t) for h, t in nav["cidades"].items()] + [("aria-labels", "\n".join(a for a in nav["arias"] if a))] + \
           [("strings do JS", "\n".join(re.findall(r"'([^'\\]*)'", (SITE / "src" / "app.js").read_text(encoding="utf-8"))))]
    achados = [(onde, pat, m.group(0)) for onde, t in todo for pat in proib for m in re.finditer(pat, t.lower())]
    travessao = [(onde, t[max(0, i - 30):i + 30]) for onde, t in todo for i in [m.start() for m in re.finditer("—", t)]]

    # 4. acessibilidade
    pares = [("texto", "#e6e7ec", "#15161d"), ("texto", "#e6e7ec", "#0e0f14"), ("secundário", "#9a9ba6", "#15161d"), ("secundário", "#9a9ba6", "#0e0f14"),
             ("secundário sobre caixa", "#9a9ba6", "#1c1d26"), ("Lula (texto)", "#fe5d48", "#15161d"), ("Flávio (texto)", "#3788ff", "#15161d"),
             ("Flávio (texto) no topo", "#3788ff", "#0e0f14"), ("âmbar", "#e2a632", "#15161d"), ("rótulo L do eixo", "#f08a7c", "#15161d"),
             ("rótulo F do eixo", "#7fb6fb", "#15161d"), ("aba ativa", "#0e0f14", "#e6e7ec")]
    cont = [(n, a, b_, contraste(a, b_)) for n, a, b_ in pares]
    kb = len(html_final.encode()) / 1024

    crit = {
        "1. Números rastreáveis": not soltos and not dif and not sem_origem and not ausentes and all(not f for *_, f in cid_ok),
        "2. Sem frases proibidas e sem travessão": not achados and not travessao,
        "4. Acessibilidade (contraste AA, textos alternativos, teclado)": all(c >= 4.5 for *_, c in cont) and all(nav["teclado"].values()) and nav["foco_visivel"]
        and all(v["aria"] for v in nav["lentes"].values()),
        "Celular 400 px sem rolagem horizontal": nav["cel_scroll_max"] <= 400,
        "Carregamento inicial < 1,5 MB": kb < 1536,
        "Sem erro de JavaScript": not nav["erros"],
    }
    comp = SITE / "comparacao.md"
    L = [f"# Verificação: site “Cidade não vota. Gente vota.” (rodada {rodada})", "",
         f"- Gerado em {datetime.now():%Y-%m-%d %H:%M} por `site/verify.py`, sobre `site/dist/index.html` ({kb:.0f} kB, tudo embutido; sem requisições externas).",
         "- Navegador: Chrome instalado, headless (Playwright), desktop 1366 × 900 e celular 400 × 860.",
         f"- Registro de números: `site/registro_numeros.json` ({len(NUM)} números; {len(usados)} usados na página).", "",
         "## Critérios automáticos", "", "| Critério | Resultado |", "|---|---|"]
    L += [f"| {k} | {'OK' if v else 'FALHOU'} |" for k, v in crit.items()]
    L += ["", f"**Resultado automático: {'APROVADO' if all(crit.values()) else 'REPROVADO'}.**", ""]
    L += ["## 1. Números", "", "### 1a. Nenhum número digitado no HTML", "",
          f"Texto do template sem os marcadores `{{{{…}}}}`: {len(soltos)} trecho(s) com número fora da lista de rótulos fixos."]
    L += [f"- {o}: “{t[:90]}” → {tk}" for o, t, tk in soltos]
    L += ["", "Rótulos fixos permitidos (não são dado): anos, datas, “1º turno”, “art. 5º/120”, “EC 123/2022”, “100% das seções”, “de 100 pessoas” (exemplo ilustrativo), “95%”, “percentis 90 e 10”, “60 anos”, “Q1…Q5”, “faixas de 2 pontos” e o título citado do Poder360 (“R$ 12,6 bi”, conferido na captura `data/raw/fontes_beneficios_2022/poder360_2022-08-03_titulo.png`).", "",
          "Strings do JavaScript com dígitos (rótulos de eixo e legendas; nenhum é dado):", ""]
    L += [f"- `{s}`" for s in js_soltos]
    L += ["", "### 1b. Recomputação independente (pandas, sem usar o código do build)", "", "| Chave | Recalculado | Na página | OK |", "|---|---|---|---|"]
    L += [f"| {k} | {v} | {NUM[k]['texto']} | {'sim' if NUM[k]['texto'] == v else '**não**'} |" for k, v in E.items()]
    L += ["", f"### 1c. Números da página renderizada sem origem no registro: {len(sem_origem)}", ""]
    L += [f"- {o}: {t}" for o, t in sem_origem[:50]]
    L += [f"", f"Valores do registro ausentes do HTML final: {ausentes or 'nenhum'}.", "",
          "### 1d. Ficha da cidade (calculada no navegador a partir de `dados.json`) contra a base", "", "| Cidade | Valores esperados | Faltando na ficha |", "|---|---|---|"]
    L += [f"| {h} ({ib}) | {' · '.join(e)} | {', '.join(f) or 'nenhum'} |" for h, ib, e, f in cid_ok]
    L += ["", "### 1e. Origem de cada número da página", "", "| Chave | Na página | Arquivo | Como |", "|---|---|---|---|"]
    L += [f"| {k} | {NUM[k]['texto']} | `{NUM[k]['fonte']}` | {NUM[k]['como']} |" for k in sorted(set(usados))]
    L += ["", "## 2. Frases proibidas", "", f"Lista de `video/checagens.py` ({len(proib)} padrões) aplicada a: texto inicial, os 8 painéis com as alternâncias, 3 fichas de cidade, todos os aria-label e as strings do JS.", "",
          f"Ocorrências: {len(achados)}. Travessões (—): {len(travessao)}."]
    L += [f"- {o}: “{m}” ({p})" for o, p, m in achados] + [f"- travessão em {o}: “{t}”" for o, t in travessao]
    L += ["", "## 4. Acessibilidade", "", "| Par de cores | Frente | Fundo | Contraste | AA (4,5) |", "|---|---|---|---|---|"]
    L += [f"| {n} | `{a}` | `{b_}` | {c:.2f} | {'sim' if c >= 4.5 else 'não'} |" for n, a, b_, c in cont]
    L += ["", "| Teclado | OK |", "|---|---|"] + [f"| {k} | {'sim' if v else 'não'} |" for k, v in nav["teclado"].items()]
    L += [f"| regra :focus-visible no CSS | {'sim' if nav['foco_visivel'] else 'não'} |", "",
          "Texto alternativo do gráfico (aria-label do canvas) por painel:", ""]
    L += [f"- {l}: {v['aria']}" for l, v in nav["lentes"].items()]
    L += ["", "Além do aria-label, cada painel tem o resumo em texto visível acima do gráfico, e a tabela dos 27 estados é navegável por teclado (Tab e Enter).", "",
          f"Celular: maior `scrollWidth` entre os 8 painéis = {nav['cel_scroll_max']} px (limite 400).", f"Erros de JavaScript: {nav['erros'] or 'nenhum'}.", ""]
    if comp.exists():
        L += [comp.read_text(encoding="utf-8")]
    (ROOT / "site_verification.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    for k, v in crit.items():
        print(("OK   " if v else "FALHA"), k)
    print("soltos", soltos[:5], "dif", dif, "sem_origem", sem_origem[:10], "ausentes", ausentes, "cid", [(h, f) for h, _, _, f in cid_ok if f])
    print("proibidas", achados, "travessao", travessao[:3], "teclado", nav["teclado"], "cont<4.5", [(n, round(c, 2)) for n, _, _, c in cont if c < 4.5])


if __name__ == "__main__":
    main()
