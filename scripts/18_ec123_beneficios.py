"""18_ec123_beneficios.py
Extrai do texto oficial da EC 123/2022 (Planalto, salvo em data/raw/fontes_beneficios_2022/emc123_planalto.htm)
o limite de despesa de cada medida do art. 5º, incisos I a VII. Os valores saem do texto, não são digitados.
Saídas: data/derived/ec123_2022_beneficios.csv e logs/18_ec123_beneficios_log.json
Uso: python -P scripts/18_ec123_beneficios.py <raiz_do_projeto>
"""
import csv
import html
import json
import re
import sys
from pathlib import Path

ROOT = Path(sys.argv[1])
SRC = ROOT / "data/raw/fontes_beneficios_2022/emc123_planalto.htm"
txt = html.unescape(re.sub(r"<[^>]+>", " ", SRC.read_bytes().decode("latin-1")))
txt = re.sub(r"\s+", " ", txt)

art5 = txt[txt.index("Art. 5º Observado"):txt.index("§ 1º O acréscimo mensal extraordinário")]
# rótulo curto para a tela, por inciso (só o nome; todo valor vem do texto)
ROTULO = {"I": "Auxílio Brasil", "II": "Auxílio Gás", "III": "Auxílio caminhoneiro",
          "IV": "Transporte grátis de idosos", "V": "Etanol (ajuda aos estados)", "VI": "Auxílio taxista",
          "VII": "Alimenta Brasil"}
partes = re.split(r" (I|II|III|IV|V|VI|VII) - ", art5)
linhas = []
for num, corpo in zip(partes[1::2], partes[2::2]):
    valores = re.findall(r"R\$ ?([\d.]+),00", corpo)
    # o limite global de cada inciso é o maior valor citado (o inciso V também cita a parcela mensal)
    v = max(int(x.replace(".", "")) for x in valores if len(x.replace(".", "")) >= 9)
    # valor mensal por pessoa/família, quando o inciso fixa um (I: acréscimo de R$ 200; III: R$ 1.000 mensais)
    m = re.search(r"R\$ ?([\d.]+),00 \([^)]*\)(?: mensais|, no período)", corpo)
    mensal = int(m[1].replace(".", "")) if m and len(m[1].replace(".", "")) < 7 else ""
    linhas.append({"inciso": num, "rotulo": ROTULO[num], "limite_reais": v, "mensal_reais": mensal, "trecho": corpo[:160]})
assert [x["inciso"] for x in linhas] == list(ROTULO), linhas
total = sum(x["limite_reais"] for x in linhas)
linhas.sort(key=lambda x: -x["limite_reais"])

out = ROOT / "data/derived/ec123_2022_beneficios.csv"
with out.open("w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=["inciso", "rotulo", "limite_reais", "mensal_reais"], extrasaction="ignore")
    w.writeheader()
    w.writerows(linhas)
    w.writerow({"inciso": "total", "rotulo": "Total", "limite_reais": total})
(ROOT / "logs/18_ec123_beneficios_log.json").write_text(json.dumps(
    {"fonte": str(SRC.relative_to(ROOT)), "promulgacao": "2022-07-14", "linhas": linhas, "total": total,
     "teto": "art. 120, par. único, I, b, ADCT: despesas não consideradas no limite do art. 107 do ADCT"},
    ensure_ascii=False, indent=1), encoding="utf-8")
for x in linhas:
    print(x["inciso"], x["rotulo"], x["limite_reais"], x["mensal_reais"])
print("total", total)
