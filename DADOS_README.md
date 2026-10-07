# Dados do projeto eleicoes

Regra: somente fontes oficiais. `data/raw/` nunca é sobrescrito; derivados em `data/derived/`; logs em `logs/`.
Scripts numerados em `scripts/`, rodados a partir da raiz do projeto.

## Eleições, transferências e base municipal (concluído 2026-10-07)

| Passo | Script | Fonte | Saída |
|---|---|---|---|
| 4 | `scripts/04_mds_transferencias.py` | MDS/SAGI API MI Social (ago-out/2022, ago-set/2026) | `data/raw/mds/misocial_{aaaamm}.csv` |
| 5 | `scripts/05_tse_presidente_municipio.py` | TSE dados abertos `votacao_candidato_munzona_2022.zip` (cdn.tse.jus.br; SHA-256 em `data/raw/tse/`) | `data/derived/tse_presidente_t1_2022_municipio.csv` |
| 6 | `scripts/06_tse_2026_resultados.py` | TSE resultados.tse.jus.br, eleição 6257 (Presidente 1º turno 2026), um JSON por localidade, totalização 05/10/2026 12:51 | `data/raw/tse/resultados_6257/`, `data/derived/tse_presidente_t1_2026_municipio.csv`, `data/derived/tse_ibge_crosswalk.csv` |
| 7 | `scripts/07_base_municipal.py` | saídas 3-6 | `data/derived/base_municipal.csv`, `logs/07_base_log.json` |

- Os dados abertos do TSE de 2026 (zip de 05/10/2026) só têm cargos estaduais (eleição 6259); Presidente (6257) veio do sistema de divulgação. Trocar pela base aberta quando publicada e conferir.
- Correspondência TSE x IBGE: arquivo oficial `config/mun-e006257-cm.json` (campos `cd`, `cdi`).
- Auxílio Brasil set/2022: pessoas = `cadunico_tot_pes_pbf_i`, famílias = `pab_qtd_fam_benef_i`. Bolsa Família set/2026: `qtd_pessoas_beneficiarias_bolsa_familia_i`, `qtd_familias_beneficiarias_bolsa_familia_i`. Totais: AB 20.653.849 famílias / 54.764.061 pessoas; BF 19.295.378 / 49.645.630.
- **Comparabilidade conferida (2026-10-07, `scripts/16_mds_comparabilidade.py`):** de mar/2023 a jun/2024 a API traz `cadunico_tot_pes_pbf_i` e `qtd_pessoas_beneficiarias_bolsa_familia_i` no mesmo mês. Em mar/2023, jun/2023 e dez/2023: correlação municipal de % da população 0,9995 a 0,9999; razão dos totais 0,995 a 1,001; razão municipal mediana 1,000 (P5-P95 de 0,97 a 1,05). As duas contagens medem a mesma coisa. Log: `logs/16_mds_comparabilidade_log.json`; brutos em `data/raw/mds/misocial_comparab_*.csv`.

## Mortalidade por COVID-19 (concluído 2026-10-07)

| Passo | Script | Entrada | Saída |
|---|---|---|---|
| 1 | `scripts/01_sim_dbc_extract.js` (Node) | `data/raw/sim/DOBR{2020,2021,2022}.dbc` | `data/derived/sim_covid_{ano}.csv`, `logs/sim_{ano}_resumo.json` |
| 2 | `scripts/02_ibge_pop_idade.py` | API SIDRA tabela 9514 | `data/raw/ibge/censo2022_pop_idade_mun.csv` |
| 3 | `scripts/03_covid_taxas_municipio.py` | saídas 1 e 2 | `data/derived/covid_mortalidade_municipio_2020_2022.csv`, `logs/03_covid_taxas_log.json` |

Comandos:
```
node --max-old-space-size=8000 scripts/01_sim_dbc_extract.js data/raw/sim/DOBR2020.dbc data/derived/sim_covid_2020.csv logs/sim_2020_resumo.json
python -P scripts/02_ibge_pop_idade.py .
python -P scripts/03_covid_taxas_municipio.py .
```

### Fontes
- SIM, Declarações de Óbito, Brasil, arquivos finais: `ftp://ftp.datasus.gov.br/dissemin/publicos/SIM/CID10/DORES/` (datas no FTP: 2020 = 01/04/2022; 2021 = 28/04/2023; 2022 = 22/12/2023). SHA-256 em `data/raw/sim/SHA256SUMS.txt`.
- IBGE, Censo 2022, SIDRA tabela 9514 (população residente por idade), via `servicodados.ibge.gov.br/api/v3`.

### Leitor .dbc
O pacote R `read.dbc` foi arquivado no CRAN. O script 1 porta para JavaScript o descompressor `blast.c` (Mark Adler), o mesmo usado pelo `read.dbc`.
Validação: bytes descomprimidos = registros × tamanho do registro + 1 (marcador de fim 0x1A) nos três anos, e a soma das larguras dos campos é igual ao tamanho do registro (490).
**Verificação cruzada concluída (2026-10-07):** `scripts/15_sim_crosscheck_readdbc.R` lê os três anos com `read.dbc` 1.2.0 (arquivo do CRAN, compilado com Rtools45) e aplica a mesma regra. Resultado idêntico ao leitor JavaScript: mesmo número de registros (1.556.824; 1.832.649; 1.544.266), mesmos óbitos COVID por causa básica e em qualquer linha, registros extraídos idênticos campo a campo e nenhuma diferença na contagem por município de residência. Log: `logs/15_sim_crosscheck_log.json`.

### Definições
- Óbito COVID: causa básica B34.2 (convenção do SIM para COVID-19). Sensibilidade: B34.2/U07.1/U07.2/U10.9 em qualquer linha do atestado (`*_qualquer`).
- Taxas: óbitos acumulados 2020-2022 por 100 mil habitantes do Censo 2022. Não são taxas anuais.
- Padronização direta pela população Brasil 2022 (17 faixas, 80+ agregado). SMR indireto com taxas nacionais por faixa.
- Município de residência = 6 primeiros dígitos do código IBGE.

### Resultados de controle
| Item | 2020 | 2021 | 2022 | Total |
|---|---|---|---|---|
| Óbitos totais (SIM) | 1.556.824 | 1.832.649 | 1.544.266 | |
| COVID causa básica | 212.706 | 424.461 | 65.764 | 702.931 |
| COVID qualquer linha | 224.725 | 445.312 | 76.023 | 746.060 |

- 158 óbitos COVID (causa básica) com município "ignorado" (código UF+0000) ficam fora das taxas municipais; 70 com idade ignorada ficam fora das taxas por idade.
- Taxa bruta Brasil: 346,1 por 100 mil (acumulada 2020-2022).
- 5.570 municípios (Censo 2022). Boa Esperança do Norte (MT), criado depois, não tem população no Censo 2022 nem óbitos próprios em 2020-2022 (a verificar: de quais municípios foi desmembrado, para o pareamento com os dados eleitorais de 2026).
- 8 municípios sem nenhum óbito COVID por causa básica.

### Cuidados para a análise
- Em municípios pequenos a taxa direta é instável; preferir SMR, com suavização (ex.: Bayes empírico) ou ponderação pelo tamanho.
- Os totais do SIM diferem dos do Painel COVID do Ministério da Saúde: o SIM é por data do óbito, codificado e consolidado; o Painel é por notificação.
- Mortalidade por COVID também é variável ecológica: herda a mesma limitação criticada no vídeo.

## Centroides municipais para o mapa do vídeo (2026-10-07)
| Passo | Script | Fonte | Saída |
|---|---|---|---|
| 14 | `scripts/14_ibge_centroides.py` | IBGE, API de malhas v3, `paises/BR/metadados?intrarregiao=municipio` | `data/raw/ibge/malhas_metadados_municipios.json` (+ SHA-256), `data/derived/ibge_centroides_municipios.csv`, `logs/14_ibge_centroides_log.json` |

- 5.570 centroides. Boa Esperança do Norte (MT, 5101837) não tem malha na API e fica fora do mapa.
