# Cidade não vota. Gente vota.

Site: https://eleicoes.danielumpierre.com

Resposta, painel por painel, ao site "O Brasil dividido" (eleicoes.tonycelestino.com/2026), com dados oficiais por município do 1º turno de 2022 e 2026. Todos os dados são municipais: mostram como votaram as cidades, não cada eleitor.

## O que há aqui
| Caminho | Conteúdo |
|---|---|
| `index.html`, `dados.json`, `CNAME` | o site publicado (GitHub Pages) e a base por município usada nele, com dicionário dos campos |
| `site/` | `build.py` (gera o site e registra a origem de cada número em `registro_numeros.json`), `verify.py` (checagens), `src/` (HTML, CSS, JS) |
| `site_verification.md` | resultado das checagens: cada número da página com arquivo e coluna de origem, frases proibidas, acessibilidade |
| `scripts/` | scripts numerados que baixam e processam as fontes oficiais (Python, R, Node) |
| `data/derived/` | bases municipais derivadas das fontes oficiais |
| `data/raw/ibge/` | nomes, malha das UFs e SHA-256 dos arquivos do IBGE usados no build |
| `output/`, `logs/` | saídas dos modelos e logs de cada script |
| `DADOS_README.md` | fontes, comandos e controles de qualidade |

Os arquivos brutos grandes (TSE, MDS, SIM, CGU) não estão no repositório; os scripts os baixam das fontes oficiais. Microdados de óbito do SIM não são publicados aqui, só agregados por município.

## Fontes oficiais
- TSE: resultados do 1º turno de 2026 (resultados.tse.jus.br, eleição 6257) e dados abertos de 2022 (dadosabertos.tse.jus.br).
- MDS: MI Social, Auxílio Brasil (set/2022) e Bolsa Família (set/2026).
- IBGE: Censo 2022 (SIDRA), malhas e localidades (servicodados.ibge.gov.br).
- Emenda Constitucional 123/2022 (planalto.gov.br).
- Ministério da Saúde, SIM; CGU, emendas parlamentares (análises exploratórias, fora do site).

## Reproduzir o site
```
PYTHONUTF8=1 python -P site/build.py        # gera site/dist/ a partir de data/derived, output e logs
PYTHONUTF8=1 python -P site/verify.py 1     # checagens (Chrome instalado + Playwright)
```

Análise: Daniel Umpierre · Desenvolvimento: Claude Opus 5.5 (outubro, 2026). Fontes IBM Plex sob a SIL Open Font License.
