# Verificação: site “Cidade não vota. Gente vota.” (rodada 4)

- Gerado em 2026-10-07 18:50 por `site/verify.py`, sobre `site/dist/index.html` (883 kB, tudo embutido; sem requisições externas).
- Navegador: Chrome instalado, headless (Playwright), desktop 1366 × 900 e celular 400 × 860.
- Registro de números: `site/registro_numeros.json` (221 números; 201 usados na página).

## Critérios automáticos

| Critério | Resultado |
|---|---|
| 1. Números rastreáveis | OK |
| 2. Sem frases proibidas e sem travessão | OK |
| 4. Acessibilidade (contraste AA, textos alternativos, teclado) | OK |
| Celular 400 px sem rolagem horizontal | OK |
| Carregamento inicial < 1,5 MB | OK |
| Sem erro de JavaScript | OK |

**Resultado automático: APROVADO.**

## 1. Números

### 1a. Nenhum número digitado no HTML

Texto do template sem os marcadores `{{…}}`: 0 trecho(s) com número fora da lista de rótulos fixos.

Rótulos fixos permitidos (não são dado): anos, datas, “1º turno”, “art. 5º/120”, “EC 123/2022”, “100% das seções”, “de 100 pessoas” (exemplo ilustrativo), “95%”, “percentis 90 e 10”, “60 anos”, “Q1…Q5”, “faixas de 2 pontos” e o título citado do Poder360 (“R$ 12,6 bi”, conferido na captura `data/raw/fontes_beneficios_2022/poder360_2022-08-03_titulo.png`).

Strings do JavaScript com dígitos (rótulos de eixo e legendas; nenhum é dado):

- `#15161d`
- `#2a2c38`
- `#2c2e3a`
- `#3a3c48`
- `#5b5d68`
- `#6a6c78`
- `#7fb6fb`
- `#9a9ba6`
- `2d`
- `600 13px "Plex Cond", sans-serif`
- `http://www.w3.org/2000/svg`
- `rgba(28,29,38,.95)`

### 1b. Recomputação independente (pandas, sem usar o código do build)

| Chave | Recalculado | Na página | OK |
|---|---|---|---|
| flavio_pct | 47,0% | 47,0% | sim |
| lula_pct | 45,2% | 45,2% | sim |
| dif_mi | 2,22 mi | 2,22 mi | sim |
| n_mapa | 5.570 | 5.570 | sim |
| viradas | 711 | 711 | sim |
| viradas_inv | 0 | 0 | sim |
| pct_andou_pl | 99% | 99% | sim |
| lula_perda_mi | 3,4 milhões | 3,4 milhões | sim |
| pct_cid_lula_caiu | 98% | 98% | sim |
| r_m22_m26 | 0,98 | 0,98 | sim |
| n_cid_perto | 426 | 426 | sim |
| pct_vot_perto | 16,3% | 16,3% | sim |
| bf_d10_lula | 68,1% | 68,1% | sim |
| bf_d1_flavio | 63,5% | 63,5% | sim |
| renda_d1_lula | 69,5% | 69,5% | sim |
| renda_d10_flavio | 46,7% | 46,7% | sim |
| ev_d1_lula | 60,6% | 60,6% | sim |
| ev_d10_flavio | 54,3% | 54,3% | sim |
| r_renda_bf | −0,91 | −0,91 | sim |
| r_bf26 | −0,74 | −0,74 | sim |
| r_ab22 | −0,75 | −0,75 | sim |
| r_ev26 | 0,41 | 0,41 | sim |
| r_ab_bf | 0,98 | 0,98 | sim |
| n_bf80 | 19 | 19 | sim |
| bf_max | 100,6% | 100,6% | sim |
| q22_1_lula | 36,0% | 36,0% | sim |
| q22_1_bolsonaro | 54,4% | 54,4% | sim |
| q22_5_lula | 73,3% | 73,3% | sim |
| q22_5_bolsonaro | 21,9% | 21,9% | sim |
| q26_1_lula | 31,2% | 31,2% | sim |
| q26_1_flavio | 59,3% | 59,3% | sim |
| q26_5_lula | 68,1% | 68,1% | sim |
| q26_5_flavio | 27,9% | 27,9% | sim |
| a22 | −54 | −54 | sim |
| a22_li | −63 | −63 | sim |
| a22_ls | −46 | −46 | sim |
| aj22 | −34 | −34 | sim |
| aj22_li | −43 | −43 | sim |
| aj22_ls | −25 | −25 | sim |
| a26 | −48 | −48 | sim |
| a26_li | −58 | −58 | sim |
| a26_ls | −38 | −38 | sim |
| aj26 | −32 | −32 | sim |
| aj26_li | −44 | −44 | sim |
| aj26_ls | −19 | −19 | sim |
| ec_total | R$ 41,25 bi | R$ 41,25 bi | sim |

### 1c. Números da página renderizada sem origem no registro: 0


Valores do registro ausentes do HTML final: nenhum.

### 1d. Ficha da cidade (calculada no navegador a partir de `dados.json`) contra a base

| Cidade | Valores esperados | Faltando na ficha |
|---|---|---|
| pi/bonfim-do-piaui (2201929) | 88,7% · 8,6% · 57,1% · 62,5% · R$ 637 · 89,7% · 3,1 pontos | nenhum |
| rs/nova-padua (4313086) | 7,4% · 87,0% · 1,8% · 2,6% · R$ 2.242 · 10,3% · 6,0 pontos | nenhum |
| sp/sao-paulo (3550308) | 46,6% · 42,1% · 14,4% · 15,7% · R$ 2.713 · 47,5% · 5,1 pontos | nenhum |

### 1e. Origem de cada número da página

| Chave | Na página | Arquivo | Como |
|---|---|---|---|
| a22 | −54 | `output/contrastes_p90_p10.csv` | linha 7 (modelo 'A22: AB + UF', IC 95% com erro agrupado por UF), diff_margem_p90_menos_p10 |
| a22_li | −63 | `output/contrastes_p90_p10.csv` | linha 7 (modelo 'A22: AB + UF', IC 95% com erro agrupado por UF), li |
| a22_ls | −46 | `output/contrastes_p90_p10.csv` | linha 7 (modelo 'A22: AB + UF', IC 95% com erro agrupado por UF), ls |
| a26 | −48 | `output/contrastes_p90_p10.csv` | linha 3 (modelo 'A26: BF + UF', IC 95% com erro agrupado por UF), diff_margem_p90_menos_p10 |
| a26_li | −58 | `output/contrastes_p90_p10.csv` | linha 3 (modelo 'A26: BF + UF', IC 95% com erro agrupado por UF), li |
| a26_ls | −38 | `output/contrastes_p90_p10.csv` | linha 3 (modelo 'A26: BF + UF', IC 95% com erro agrupado por UF), ls |
| aj22 | −34 | `output/contrastes_p90_p10.csv` | linha 9 (modelo 'B22: AB + UF + Censo', IC 95% com erro agrupado por UF), diff_margem_p90_menos_p10 |
| aj22_li | −43 | `output/contrastes_p90_p10.csv` | linha 9 (modelo 'B22: AB + UF + Censo', IC 95% com erro agrupado por UF), li |
| aj22_ls | −25 | `output/contrastes_p90_p10.csv` | linha 9 (modelo 'B22: AB + UF + Censo', IC 95% com erro agrupado por UF), ls |
| aj26 | −32 | `output/contrastes_p90_p10.csv` | linha 5 (modelo 'B26: BF + UF + Censo', IC 95% com erro agrupado por UF), diff_margem_p90_menos_p10 |
| aj26_li | −44 | `output/contrastes_p90_p10.csv` | linha 5 (modelo 'B26: BF + UF + Censo', IC 95% com erro agrupado por UF), li |
| aj26_ls | −19 | `output/contrastes_p90_p10.csv` | linha 5 (modelo 'B26: BF + UF + Censo', IC 95% com erro agrupado por UF), ls |
| bf_d10_lula | 68,1% | `data/derived/base_analitica_emendas.csv` | ponta superior de 10% do eleitorado_26, municípios ordenados por pct_bf_26; soma lula_26 / soma validos_26 |
| bf_d10_lula_lim | 50% | `data/derived/base_analitica_emendas.csv` | mínimo de pct_bf_26 na ponta (inteiro) |
| bf_d1_flavio | 63,5% | `data/derived/base_analitica_emendas.csv` | ponta inferior de 10% do eleitorado_26, municípios ordenados por pct_bf_26; soma flavio_26 / soma validos_26 |
| bf_d1_flavio_lim | 9% | `data/derived/base_analitica_emendas.csv` | máximo de pct_bf_26 na ponta (inteiro) |
| bf_max | 100,6% | `data/derived/base_analitica_emendas.csv` | máximo de pct_bf_26 |
| bonfim_bf | 57,1% | `data/derived/base_analitica_emendas.csv` | linha cd_ibge7=2201929, pct_bf_26 |
| bonfim_lula | 88,7% | `data/derived/base_analitica_emendas.csv` | linha cd_ibge7=2201929, pct_lula_26 |
| desloc_nac | 7,1 pontos | `data/derived/base_analitica_emendas.csv` | margem nacional (PL − Lula, votos somados) 2026 menos 2022, 5.570 do mapa |
| dif_mi | 2,22 mi | `logs/06_tse_2026_log.json` | diferenca_22_menos_13 / 1e6 |
| ec_I | R$ 26 bi | `data/derived/ec123_2022_beneficios.csv` | linha 2 (inciso I, 'Auxílio Brasil'), limite_reais / 1e9 |
| ec_II | R$ 1,05 bi | `data/derived/ec123_2022_beneficios.csv` | linha 7 (inciso II, 'Auxílio Gás'), limite_reais / 1e9 |
| ec_III | R$ 5,4 bi | `data/derived/ec123_2022_beneficios.csv` | linha 3 (inciso III, 'Auxílio caminhoneiro'), limite_reais / 1e9 |
| ec_IV | R$ 2,5 bi | `data/derived/ec123_2022_beneficios.csv` | linha 5 (inciso IV, 'Transporte grátis de idosos'), limite_reais / 1e9 |
| ec_I_mensal | R$ 200 | `data/derived/ec123_2022_beneficios.csv` | linha 2, mensal_reais |
| ec_V | R$ 3,8 bi | `data/derived/ec123_2022_beneficios.csv` | linha 4 (inciso V, 'Etanol (ajuda aos estados)'), limite_reais / 1e9 |
| ec_VI | R$ 2 bi | `data/derived/ec123_2022_beneficios.csv` | linha 6 (inciso VI, 'Auxílio taxista'), limite_reais / 1e9 |
| ec_VII | R$ 0,5 bi | `data/derived/ec123_2022_beneficios.csv` | linha 8 (inciso VII, 'Alimenta Brasil'), limite_reais / 1e9 |
| ec_total | R$ 41,25 bi | `data/derived/ec123_2022_beneficios.csv` | linha 9 (inciso total, 'Total'), limite_reais / 1e9 |
| ev_d10_flavio | 54,3% | `data/derived/base_analitica_emendas.csv` | ponta superior de 10% do eleitorado_26, municípios ordenados por pct_evangelicas; soma flavio_26 / soma validos_26 |
| ev_d10_flavio_lim | 38% | `data/derived/base_analitica_emendas.csv` | mínimo de pct_evangelicas na ponta (inteiro) |
| ev_d1_lula | 60,6% | `data/derived/base_analitica_emendas.csv` | ponta inferior de 10% do eleitorado_26, municípios ordenados por pct_evangelicas; soma lula_26 / soma validos_26 |
| ev_d1_lula_lim | 15% | `data/derived/base_analitica_emendas.csv` | máximo de pct_evangelicas na ponta (inteiro) |
| ex_lula | 89 | `data/derived/base_analitica_emendas.csv` | exemplo ilustrativo: pct_lula_26 de Bonfim do Piauí arredondado |
| ex_outros | 11 | `data/derived/base_analitica_emendas.csv` | exemplo ilustrativo: 100 − ex_lula |
| ex_recebe | 57 | `data/derived/base_analitica_emendas.csv` | exemplo ilustrativo: pct_bf_26 de Bonfim do Piauí arredondado |
| flavio_pct | 47,0% | `logs/06_tse_2026_log.json` | pct_22 (Brasil + exterior, 100% das seções) |
| lim_bf_alto | 80% | `parâmetro do build` | limite do eixo no site original |
| lim_bf_max | 100% | `parâmetro do build` | população inteira |
| lim_empate | 5 | `parâmetro do build` | |margem_26| < 5 pontos = perto do empate |
| lim_peq | 10 | `parâmetro do build` | cidade pequena: eleitorado_26 < 10 mil |
| lula_pct | 45,2% | `logs/06_tse_2026_log.json` | pct_13 |
| lula_perda_mi | 3,4 milhões | `data/derived/base_analitica_emendas.csv` | (soma lula_22 − soma lula_26) / 1e6, 5.570 do mapa |
| n_bf100 | 1 | `data/derived/base_analitica_emendas.csv` | municípios com pct_bf_26 > 100 |
| n_bf80 | 19 | `data/derived/base_analitica_emendas.csv` | municípios com pct_bf_26 > 80 |
| n_cid_perto | 426 | `data/derived/base_analitica_emendas.csv` | municípios com |margem_26| < 5 pontos |
| n_mapa | 5.570 | `data/derived/base_analitica_emendas.csv + data/derived/ibge_centroides_municipios.csv` | municípios com 2022, 2026 e centroide IBGE (sem Boa Esperança do Norte/MT) |
| n_uf | 27 | `data/derived/base_analitica_emendas.csv` | número de UFs |
| n_uf_lula_caiu | 25 | `data/derived/base_analitica_emendas.csv` | UFs em que a fatia de Lula (votos somados por UF) caiu |
| pct_andou_pl | 99% | `data/derived/base_analitica_emendas.csv` | % de municípios com delta_margem > 0 (margem PL − Lula subiu) |
| pct_andou_q5 | 97% | `data/derived/base_analitica_emendas.csv` | quinto de municípios com maior pct_bf_26: % com delta_margem > 0 |
| pct_cid_10k | 52,8% | `data/derived/base_analitica_emendas.csv` | % de municípios com eleitorado_26 < 10.000 |
| pct_cid_lula_caiu | 98% | `data/derived/base_analitica_emendas.csv` | % de municípios com pct_lula_26 < 100*lula_22/validos_22 |
| pct_cid_perto | 7,6% | `data/derived/base_analitica_emendas.csv` | % de municípios com |margem_26| < 5 |
| pct_vot_10k | 10% | `data/derived/base_analitica_emendas.csv` | soma validos_26 dos municípios com eleitorado_26 < 10.000 / soma validos_26 |
| pct_vot_perto | 16,3% | `data/derived/base_analitica_emendas.csv` | soma validos_26 dos municípios com |margem_26| < 5 / soma validos_26 |
| ponta | 10% | `parâmetro do build` | fatia do eleitorado em cada ponta (mesmo corte do site original) |
| q22_1_bolsonaro | 54,4% | `data/derived/base_analitica_emendas.csv` | idem; soma bolsonaro_22 / soma validos_22 |
| q22_1_hi | 15% | `data/derived/base_analitica_emendas.csv` | quintil 1: máximo de pct_ab_22 |
| q22_1_lo | 1% | `data/derived/base_analitica_emendas.csv` | quintil 1: mínimo de pct_ab_22 |
| q22_1_lula | 36,0% | `data/derived/base_analitica_emendas.csv` | quintil 1 de municípios (contagem igual) por pct_ab_22; soma lula_22 / soma validos_22 |
| q22_2_bolsonaro | 46,6% | `data/derived/base_analitica_emendas.csv` | idem; soma bolsonaro_22 / soma validos_22 |
| q22_2_hi | 25% | `data/derived/base_analitica_emendas.csv` | quintil 2: máximo de pct_ab_22 |
| q22_2_lo | 15% | `data/derived/base_analitica_emendas.csv` | quintil 2: mínimo de pct_ab_22 |
| q22_2_lula | 43,6% | `data/derived/base_analitica_emendas.csv` | quintil 2 de municípios (contagem igual) por pct_ab_22; soma lula_22 / soma validos_22 |
| q22_3_bolsonaro | 41,1% | `data/derived/base_analitica_emendas.csv` | idem; soma bolsonaro_22 / soma validos_22 |
| q22_3_hi | 41% | `data/derived/base_analitica_emendas.csv` | quintil 3: máximo de pct_ab_22 |
| q22_3_lo | 25% | `data/derived/base_analitica_emendas.csv` | quintil 3: mínimo de pct_ab_22 |
| q22_3_lula | 51,1% | `data/derived/base_analitica_emendas.csv` | quintil 3 de municípios (contagem igual) por pct_ab_22; soma lula_22 / soma validos_22 |
| q22_4_bolsonaro | 27,8% | `data/derived/base_analitica_emendas.csv` | idem; soma bolsonaro_22 / soma validos_22 |
| q22_4_hi | 57% | `data/derived/base_analitica_emendas.csv` | quintil 4: máximo de pct_ab_22 |
| q22_4_lo | 41% | `data/derived/base_analitica_emendas.csv` | quintil 4: mínimo de pct_ab_22 |
| q22_4_lula | 66,7% | `data/derived/base_analitica_emendas.csv` | quintil 4 de municípios (contagem igual) por pct_ab_22; soma lula_22 / soma validos_22 |
| q22_5_bolsonaro | 21,9% | `data/derived/base_analitica_emendas.csv` | idem; soma bolsonaro_22 / soma validos_22 |
| q22_5_hi | 102% | `data/derived/base_analitica_emendas.csv` | quintil 5: máximo de pct_ab_22 |
| q22_5_lo | 57% | `data/derived/base_analitica_emendas.csv` | quintil 5: mínimo de pct_ab_22 |
| q22_5_lula | 73,3% | `data/derived/base_analitica_emendas.csv` | quintil 5 de municípios (contagem igual) por pct_ab_22; soma lula_22 / soma validos_22 |
| q26_1_flavio | 59,3% | `data/derived/base_analitica_emendas.csv` | idem; soma flavio_26 / soma validos_26 |
| q26_1_hi | 13% | `data/derived/base_analitica_emendas.csv` | quintil 1: máximo de pct_bf_26 |
| q26_1_lo | 0% | `data/derived/base_analitica_emendas.csv` | quintil 1: mínimo de pct_bf_26 |
| q26_1_lula | 31,2% | `data/derived/base_analitica_emendas.csv` | quintil 1 de municípios (contagem igual) por pct_bf_26; soma lula_26 / soma validos_26 |
| q26_2_flavio | 50,9% | `data/derived/base_analitica_emendas.csv` | idem; soma flavio_26 / soma validos_26 |
| q26_2_hi | 21% | `data/derived/base_analitica_emendas.csv` | quintil 2: máximo de pct_bf_26 |
| q26_2_lo | 13% | `data/derived/base_analitica_emendas.csv` | quintil 2: mínimo de pct_bf_26 |
| q26_2_lula | 39,8% | `data/derived/base_analitica_emendas.csv` | quintil 2 de municípios (contagem igual) por pct_bf_26; soma lula_26 / soma validos_26 |
| q26_3_flavio | 45,5% | `data/derived/base_analitica_emendas.csv` | idem; soma flavio_26 / soma validos_26 |
| q26_3_hi | 36% | `data/derived/base_analitica_emendas.csv` | quintil 3: máximo de pct_bf_26 |
| q26_3_lo | 21% | `data/derived/base_analitica_emendas.csv` | quintil 3: mínimo de pct_bf_26 |
| q26_3_lula | 47,0% | `data/derived/base_analitica_emendas.csv` | quintil 3 de municípios (contagem igual) por pct_bf_26; soma lula_26 / soma validos_26 |
| q26_4_flavio | 33,0% | `data/derived/base_analitica_emendas.csv` | idem; soma flavio_26 / soma validos_26 |
| q26_4_hi | 50% | `data/derived/base_analitica_emendas.csv` | quintil 4: máximo de pct_bf_26 |
| q26_4_lo | 36% | `data/derived/base_analitica_emendas.csv` | quintil 4: mínimo de pct_bf_26 |
| q26_4_lula | 61,9% | `data/derived/base_analitica_emendas.csv` | quintil 4 de municípios (contagem igual) por pct_bf_26; soma lula_26 / soma validos_26 |
| q26_5_flavio | 27,9% | `data/derived/base_analitica_emendas.csv` | idem; soma flavio_26 / soma validos_26 |
| q26_5_hi | 101% | `data/derived/base_analitica_emendas.csv` | quintil 5: máximo de pct_bf_26 |
| q26_5_lo | 50% | `data/derived/base_analitica_emendas.csv` | quintil 5: mínimo de pct_bf_26 |
| q26_5_lula | 68,1% | `data/derived/base_analitica_emendas.csv` | quintil 5 de municípios (contagem igual) por pct_bf_26; soma lula_26 / soma validos_26 |
| qn_1 | 1 | `rótulo` | número do quintil |
| qn_2 | 2 | `rótulo` | número do quintil |
| qn_3 | 3 | `rótulo` | número do quintil |
| qn_4 | 4 | `rótulo` | número do quintil |
| qn_5 | 5 | `rótulo` | número do quintil |
| r_ab22 | −0,75 | `data/derived/base_analitica_emendas.csv` | correlação ponderada por eleitorado_26, pct_ab_22 x margem_22 |
| r_bf26 | −0,74 | `data/derived/base_analitica_emendas.csv` | correlação ponderada por eleitorado_26, pct_bf_26 x margem_26 |
| r_ev26 | 0,41 | `data/derived/base_analitica_emendas.csv` | correlação ponderada por eleitorado_26, pct_evangelicas x margem_26 |
| r_m22_m26 | 0,98 | `data/derived/base_analitica_emendas.csv` | correlação ponderada por eleitorado_26, margem_22 x margem_26 |
| r_renda26 | 0,59 | `data/derived/base_analitica_emendas.csv` | correlação ponderada por eleitorado_26, log(renda_pc_media) x margem_26 |
| r_renda_bf | −0,91 | `data/derived/base_analitica_emendas.csv` | correlação de Pearson sem peso, log(renda_pc_media) x pct_bf_26 |
| red22 | 38% | `output/contrastes_p90_p10.csv` | 1 − aj22 / a22 (estimativas pontuais) |
| red26 | 34% | `output/contrastes_p90_p10.csv` | 1 − aj26 / a26 (estimativas pontuais) |
| renda_d10_flavio | 46,7% | `data/derived/base_analitica_emendas.csv` | ponta superior de 10% do eleitorado_26, municípios ordenados por renda_pc_media; soma flavio_26 / soma validos_26 |
| renda_d10_flavio_lim | R$ 2.710 | `data/derived/base_analitica_emendas.csv` | mínimo de renda_pc_media na ponta (arredondado à dezena) |
| renda_d1_lula | 69,5% | `data/derived/base_analitica_emendas.csv` | ponta inferior de 10% do eleitorado_26, municípios ordenados por renda_pc_media; soma lula_26 / soma validos_26 |
| renda_d1_lula_lim | R$ 730 | `data/derived/base_analitica_emendas.csv` | máximo de renda_pc_media na ponta (arredondado à dezena) |
| renda_fim_m | +11 | `data/derived/base_analitica_emendas.csv` | margem_26 prevista pela curva no percentil 99,5 de renda |
| renda_pico | R$ 1.700 | `data/derived/base_analitica_emendas.csv` | renda_pc_media no máximo da curva (spline cúbica restrita, 5 nós nos quantis 5/27,5/50/72,5/95% de log renda, mínimos quadrados ponderados por validos_26, margem_26), arredondada à centena |
| renda_pico_m | +19 | `data/derived/base_analitica_emendas.csv` | margem_26 prevista pela curva no máximo |
| uf_AC_m22 | 33,2 | `data/derived/base_analitica_emendas.csv` | UF AC: |soma bolsonaro_22 − soma lula_22| / soma validos_22 |
| uf_AC_m26 | 35,8 | `data/derived/base_analitica_emendas.csv` | UF AC: |soma flavio_26 − soma lula_26| / soma validos_26 (5.571 municípios) |
| uf_AC_vir | 1 | `data/derived/base_analitica_emendas.csv` | UF AC: municípios com venc_22 == 13 e venc_26 == 22 |
| uf_AL_m22 | 20,5 | `data/derived/base_analitica_emendas.csv` | UF AL: |soma bolsonaro_22 − soma lula_22| / soma validos_22 |
| uf_AL_m26 | 14,3 | `data/derived/base_analitica_emendas.csv` | UF AL: |soma flavio_26 − soma lula_26| / soma validos_26 (5.571 municípios) |
| uf_AL_vir | 8 | `data/derived/base_analitica_emendas.csv` | UF AL: municípios com venc_22 == 13 e venc_26 == 22 |
| uf_AM_m22 | 6,8 | `data/derived/base_analitica_emendas.csv` | UF AM: |soma bolsonaro_22 − soma lula_22| / soma validos_22 |
| uf_AM_m26 | 3,2 | `data/derived/base_analitica_emendas.csv` | UF AM: |soma flavio_26 − soma lula_26| / soma validos_26 (5.571 municípios) |
| uf_AM_vir | 4 | `data/derived/base_analitica_emendas.csv` | UF AM: municípios com venc_22 == 13 e venc_26 == 22 |
| uf_AP_m22 | 2,3 | `data/derived/base_analitica_emendas.csv` | UF AP: |soma bolsonaro_22 − soma lula_22| / soma validos_22 |
| uf_AP_m26 | 0,05 | `data/derived/base_analitica_emendas.csv` | UF AP: |soma flavio_26 − soma lula_26| / soma validos_26 (5.571 municípios) |
| uf_AP_vir | 1 | `data/derived/base_analitica_emendas.csv` | UF AP: municípios com venc_22 == 13 e venc_26 == 22 |
| uf_BA_m22 | 45,4 | `data/derived/base_analitica_emendas.csv` | UF BA: |soma bolsonaro_22 − soma lula_22| / soma validos_22 |
| uf_BA_m26 | 37,6 | `data/derived/base_analitica_emendas.csv` | UF BA: |soma flavio_26 − soma lula_26| / soma validos_26 (5.571 municípios) |
| uf_BA_vir | 2 | `data/derived/base_analitica_emendas.csv` | UF BA: municípios com venc_22 == 13 e venc_26 == 22 |
| uf_CE_m22 | 40,5 | `data/derived/base_analitica_emendas.csv` | UF CE: |soma bolsonaro_22 − soma lula_22| / soma validos_22 |
| uf_CE_m26 | 32,0 | `data/derived/base_analitica_emendas.csv` | UF CE: |soma flavio_26 − soma lula_26| / soma validos_26 (5.571 municípios) |
| uf_CE_vir | 1 | `data/derived/base_analitica_emendas.csv` | UF CE: municípios com venc_22 == 13 e venc_26 == 22 |
| uf_DF_m22 | 14,8 | `data/derived/base_analitica_emendas.csv` | UF DF: |soma bolsonaro_22 − soma lula_22| / soma validos_22 |
| uf_DF_m26 | 13,2 | `data/derived/base_analitica_emendas.csv` | UF DF: |soma flavio_26 − soma lula_26| / soma validos_26 (5.571 municípios) |
| uf_DF_vir | 0 | `data/derived/base_analitica_emendas.csv` | UF DF: municípios com venc_22 == 13 e venc_26 == 22 |
| uf_ES_m22 | 11,8 | `data/derived/base_analitica_emendas.csv` | UF ES: |soma bolsonaro_22 − soma lula_22| / soma validos_22 |
| uf_ES_m26 | 17,0 | `data/derived/base_analitica_emendas.csv` | UF ES: |soma flavio_26 − soma lula_26| / soma validos_26 (5.571 municípios) |
| uf_ES_vir | 7 | `data/derived/base_analitica_emendas.csv` | UF ES: municípios com venc_22 == 13 e venc_26 == 22 |
| uf_GO_m22 | 12,6 | `data/derived/base_analitica_emendas.csv` | UF GO: |soma bolsonaro_22 − soma lula_22| / soma validos_22 |
| uf_GO_m26 | 22,5 | `data/derived/base_analitica_emendas.csv` | UF GO: |soma flavio_26 − soma lula_26| / soma validos_26 (5.571 municípios) |
| uf_GO_vir | 69 | `data/derived/base_analitica_emendas.csv` | UF GO: municípios com venc_22 == 13 e venc_26 == 22 |
| uf_MA_m22 | 42,8 | `data/derived/base_analitica_emendas.csv` | UF MA: |soma bolsonaro_22 − soma lula_22| / soma validos_22 |
| uf_MA_m26 | 33,1 | `data/derived/base_analitica_emendas.csv` | UF MA: |soma flavio_26 − soma lula_26| / soma validos_26 (5.571 municípios) |
| uf_MA_vir | 3 | `data/derived/base_analitica_emendas.csv` | UF MA: municípios com venc_22 == 13 e venc_26 == 22 |
| uf_MG_m22 | 4,7 | `data/derived/base_analitica_emendas.csv` | UF MG: |soma bolsonaro_22 − soma lula_22| / soma validos_22 |
| uf_MG_m26 | 4,9 | `data/derived/base_analitica_emendas.csv` | UF MG: |soma flavio_26 − soma lula_26| / soma validos_26 (5.571 municípios) |
| uf_MG_vir | 178 | `data/derived/base_analitica_emendas.csv` | UF MG: municípios com venc_22 == 13 e venc_26 == 22 |
| uf_MS_m22 | 13,7 | `data/derived/base_analitica_emendas.csv` | UF MS: |soma bolsonaro_22 − soma lula_22| / soma validos_22 |
| uf_MS_m26 | 23,9 | `data/derived/base_analitica_emendas.csv` | UF MS: |soma flavio_26 − soma lula_26| / soma validos_26 (5.571 municípios) |
| uf_MS_vir | 15 | `data/derived/base_analitica_emendas.csv` | UF MS: municípios com venc_22 == 13 e venc_26 == 22 |
| uf_MT_m22 | 25,5 | `data/derived/base_analitica_emendas.csv` | UF MT: |soma bolsonaro_22 − soma lula_22| / soma validos_22 |
| uf_MT_m26 | 36,0 | `data/derived/base_analitica_emendas.csv` | UF MT: |soma flavio_26 − soma lula_26| / soma validos_26 (5.571 municípios) |
| uf_MT_vir | 15 | `data/derived/base_analitica_emendas.csv` | UF MT: municípios com venc_22 == 13 e venc_26 == 22 |
| uf_PA_m22 | 11,9 | `data/derived/base_analitica_emendas.csv` | UF PA: |soma bolsonaro_22 − soma lula_22| / soma validos_22 |
| uf_PA_m26 | 5,4 | `data/derived/base_analitica_emendas.csv` | UF PA: |soma flavio_26 − soma lula_26| / soma validos_26 (5.571 municípios) |
| uf_PA_vir | 16 | `data/derived/base_analitica_emendas.csv` | UF PA: municípios com venc_22 == 13 e venc_26 == 22 |
| uf_PB_m22 | 34,6 | `data/derived/base_analitica_emendas.csv` | UF PB: |soma bolsonaro_22 − soma lula_22| / soma validos_22 |
| uf_PB_m26 | 28,2 | `data/derived/base_analitica_emendas.csv` | UF PB: |soma flavio_26 − soma lula_26| / soma validos_26 (5.571 municípios) |
| uf_PB_vir | 0 | `data/derived/base_analitica_emendas.csv` | UF PB: municípios com venc_22 == 13 e venc_26 == 22 |
| uf_PE_m22 | 35,4 | `data/derived/base_analitica_emendas.csv` | UF PE: |soma bolsonaro_22 − soma lula_22| / soma validos_22 |
| uf_PE_m26 | 32,4 | `data/derived/base_analitica_emendas.csv` | UF PE: |soma flavio_26 − soma lula_26| / soma validos_26 (5.571 municípios) |
| uf_PE_vir | 0 | `data/derived/base_analitica_emendas.csv` | UF PE: municípios com venc_22 == 13 e venc_26 == 22 |
| uf_PI_m22 | 54,3 | `data/derived/base_analitica_emendas.csv` | UF PI: |soma bolsonaro_22 − soma lula_22| / soma validos_22 |
| uf_PI_m26 | 46,9 | `data/derived/base_analitica_emendas.csv` | UF PI: |soma flavio_26 − soma lula_26| / soma validos_26 (5.571 municípios) |
| uf_PI_vir | 0 | `data/derived/base_analitica_emendas.csv` | UF PI: municípios com venc_22 == 13 e venc_26 == 22 |
| uf_PR_m22 | 19,3 | `data/derived/base_analitica_emendas.csv` | UF PR: |soma bolsonaro_22 − soma lula_22| / soma validos_22 |
| uf_PR_m26 | 28,7 | `data/derived/base_analitica_emendas.csv` | UF PR: |soma flavio_26 − soma lula_26| / soma validos_26 (5.571 municípios) |
| uf_PR_vir | 91 | `data/derived/base_analitica_emendas.csv` | UF PR: municípios com venc_22 == 13 e venc_26 == 22 |
| uf_RJ_m22 | 10,4 | `data/derived/base_analitica_emendas.csv` | UF RJ: |soma bolsonaro_22 − soma lula_22| / soma validos_22 |
| uf_RJ_m26 | 13,6 | `data/derived/base_analitica_emendas.csv` | UF RJ: |soma flavio_26 − soma lula_26| / soma validos_26 (5.571 municípios) |
| uf_RJ_vir | 13 | `data/derived/base_analitica_emendas.csv` | UF RJ: municípios com venc_22 == 13 e venc_26 == 22 |
| uf_RN_m22 | 32,0 | `data/derived/base_analitica_emendas.csv` | UF RN: |soma bolsonaro_22 − soma lula_22| / soma validos_22 |
| uf_RN_m26 | 25,0 | `data/derived/base_analitica_emendas.csv` | UF RN: |soma flavio_26 − soma lula_26| / soma validos_26 (5.571 municípios) |
| uf_RN_vir | 1 | `data/derived/base_analitica_emendas.csv` | UF RN: municípios com venc_22 == 13 e venc_26 == 22 |
| uf_RO_m22 | 35,4 | `data/derived/base_analitica_emendas.csv` | UF RO: |soma bolsonaro_22 − soma lula_22| / soma validos_22 |
| uf_RO_m26 | 41,6 | `data/derived/base_analitica_emendas.csv` | UF RO: |soma flavio_26 − soma lula_26| / soma validos_26 (5.571 municípios) |
| uf_RO_vir | 0 | `data/derived/base_analitica_emendas.csv` | UF RO: municípios com venc_22 == 13 e venc_26 == 22 |
| uf_RR_m22 | 46,5 | `data/derived/base_analitica_emendas.csv` | UF RR: |soma bolsonaro_22 − soma lula_22| / soma validos_22 |
| uf_RR_m26 | 48,2 | `data/derived/base_analitica_emendas.csv` | UF RR: |soma flavio_26 − soma lula_26| / soma validos_26 (5.571 municípios) |
| uf_RR_vir | 0 | `data/derived/base_analitica_emendas.csv` | UF RR: municípios com venc_22 == 13 e venc_26 == 22 |
| uf_RS_m22 | 6,6 | `data/derived/base_analitica_emendas.csv` | UF RS: |soma bolsonaro_22 − soma lula_22| / soma validos_22 |
| uf_RS_m26 | 19,9 | `data/derived/base_analitica_emendas.csv` | UF RS: |soma flavio_26 − soma lula_26| / soma validos_26 (5.571 municípios) |
| uf_RS_vir | 133 | `data/derived/base_analitica_emendas.csv` | UF RS: municípios com venc_22 == 13 e venc_26 == 22 |
| uf_SC_m22 | 32,7 | `data/derived/base_analitica_emendas.csv` | UF SC: |soma bolsonaro_22 − soma lula_22| / soma validos_22 |
| uf_SC_m26 | 41,6 | `data/derived/base_analitica_emendas.csv` | UF SC: |soma flavio_26 − soma lula_26| / soma validos_26 (5.571 municípios) |
| uf_SC_vir | 27 | `data/derived/base_analitica_emendas.csv` | UF SC: municípios com venc_22 == 13 e venc_26 == 22 |
| uf_SE_m22 | 34,7 | `data/derived/base_analitica_emendas.csv` | UF SE: |soma bolsonaro_22 − soma lula_22| / soma validos_22 |
| uf_SE_m26 | 32,1 | `data/derived/base_analitica_emendas.csv` | UF SE: |soma flavio_26 − soma lula_26| / soma validos_26 (5.571 municípios) |
| uf_SE_vir | 0 | `data/derived/base_analitica_emendas.csv` | UF SE: municípios com venc_22 == 13 e venc_26 == 22 |
| uf_SP_m22 | 6,8 | `data/derived/base_analitica_emendas.csv` | UF SP: |soma bolsonaro_22 − soma lula_22| / soma validos_22 |
| uf_SP_m26 | 13,7 | `data/derived/base_analitica_emendas.csv` | UF SP: |soma flavio_26 − soma lula_26| / soma validos_26 (5.571 municípios) |
| uf_SP_vir | 89 | `data/derived/base_analitica_emendas.csv` | UF SP: municípios com venc_22 == 13 e venc_26 == 22 |
| uf_TO_m22 | 6,4 | `data/derived/base_analitica_emendas.csv` | UF TO: |soma bolsonaro_22 − soma lula_22| / soma validos_22 |
| uf_TO_m26 | 7,0 | `data/derived/base_analitica_emendas.csv` | UF TO: |soma flavio_26 − soma lula_26| / soma validos_26 (5.571 municípios) |
| uf_TO_vir | 37 | `data/derived/base_analitica_emendas.csv` | UF TO: municípios com venc_22 == 13 e venc_26 == 22 |
| viradas | 711 | `data/derived/base_analitica_emendas.csv` | venc_22 == 13 e venc_26 == 22 |
| viradas_inv | 0 | `data/derived/base_analitica_emendas.csv` | venc_22 == 22 e venc_26 == 13 |

## 2. Frases proibidas

Lista de `video/checagens.py` (4 padrões) aplicada a: texto inicial, os 8 painéis com as alternâncias, 3 fichas de cidade, todos os aria-label e as strings do JS.

Ocorrências: 0. Travessões (—): 0.

## 4. Acessibilidade

| Par de cores | Frente | Fundo | Contraste | AA (4,5) |
|---|---|---|---|---|
| texto | `#e6e7ec` | `#15161d` | 14.61 | sim |
| texto | `#e6e7ec` | `#0e0f14` | 15.50 | sim |
| secundário | `#9a9ba6` | `#15161d` | 6.54 | sim |
| secundário | `#9a9ba6` | `#0e0f14` | 6.94 | sim |
| secundário sobre caixa | `#9a9ba6` | `#1c1d26` | 6.08 | sim |
| Lula (texto) | `#fe5d48` | `#15161d` | 5.90 | sim |
| Flávio (texto) | `#3788ff` | `#15161d` | 5.26 | sim |
| Flávio (texto) no topo | `#3788ff` | `#0e0f14` | 5.59 | sim |
| âmbar | `#e2a632` | `#15161d` | 8.36 | sim |
| rótulo L do eixo | `#f08a7c` | `#15161d` | 7.41 | sim |
| rótulo F do eixo | `#7fb6fb` | `#15161d` | 8.58 | sim |
| aba ativa | `#0e0f14` | `#e6e7ec` | 15.50 | sim |

| Teclado | OK |
|---|---|
| seta_muda_aba | sim |
| foco_na_nova_aba | sim |
| busca_abre_ficha | sim |
| uf_por_enter | sim |
| regra :focus-visible no CSS | sim |

Texto alternativo do gráfico (aria-label do canvas) por painel:

- mapa: Mapa de pontos do Brasil, um por município, colorido pela margem. Nordeste e Norte em vermelho (Lula), Sul, Sudeste e Centro-Oeste em azul.
- divisao: Histograma da margem de 2026 por município.
- bf: Dispersão: % no Bolsa Família contra a margem. Cidades com mais programa ficam mais para o lado de Lula.
- renda: Dispersão: renda média contra a margem, com curva que sobe e depois desce nas cidades mais ricas.
- ev: Dispersão: % de evangélicos contra a margem, nuvem larga.
- d22: Dispersão: margem de 2022 contra margem de 2026; quase todos os pontos acima da diagonal.
- ab22: Dispersão: % no programa contra a margem, em 2022 com o Auxílio Brasil e em 2026 com o Bolsa Família; o desenho é o mesmo.
- ajuste: Gráfico de estimativas com intervalos.

Além do aria-label, cada painel tem o resumo em texto visível acima do gráfico, e a tabela dos 27 estados é navegável por teclado (Tab e Enter).

Celular: maior `scrollWidth` entre os 8 painéis = 400 px (limite 400).
Erros de JavaScript: nenhum.

## 3. Comparação com o benchmark (rodada 4)

Notas de 1 a 5 (clareza / visual / interação), dadas pelo desenvolvimento a partir das capturas lado a lado: benchmark em 2026-10-07 (desktop no Chrome, celular 400 px headless) e nosso site nas rodadas 3 e 4 (desktop 1366 px e celular 400 px). As capturas ficaram no scratchpad da sessão, fora do Dropbox. É um julgamento, não uma medida: o usuário deve revisar.

| Painel | Benchmark (C / V / I) | Nosso (C / V / I) | ≥ benchmark? | Observação |
|---|---|---|---|---|
| Topo | 4 / 5 / 4 | 5 / **4** / 4 | **não (visual)** | O benchmark tem o vídeo ao lado do título; o nosso deixa o lado direito vazio. Nosso topo reconhece a queda de Lula |
| Mapa | 4 / 5 / 4 | 5 / 5 / 5 | sim | Rodada 4: cor mais saturada e brilho discreto. Alternância 2022/2026 e filtro por estado |
| A divisão | 3 / 4 / 3 | 5 / 4 / 4 | sim | Alternância cidades/votos e exemplo ilustrativo |
| Bolsa Família | 3 / 4 / 4 | 5 / 4 / 5 | sim | Corte declarado, eixo completo, troca para renda |
| Renda | 4 / 4 / 4 | 5 / 4 / 4 | sim | Curva descritiva |
| Evangélicos | 3 / 4 / 4 | 4 / 4 / 4 | sim | Correlações comparadas |
| 2022 → 2026 | 4 / 4 / 4 | 5 / 4 / 4 | sim | No celular, o rótulo “andou para o PL” encosta nos pontos |
| 2022: Auxílio Brasil | não existe | 5 / 4 / 4 | painel novo | Quintis 2022 x 2026 e EC 123/2022 |
| O que os dados não dizem | não existe | 4 / 4 / 3 | painel novo | Estimativas com intervalo; sem interação além da leitura |
| Ficha da cidade | 4 / 4 / 5 | 5 / 4 / 5 | sim | Linha de 2022, Auxílio Brasil, critério das cidades parecidas |
| Os 27 estados | 4 / 4 / 4 | 4 / 4 / 4 | sim | Linha clicável filtra o mapa |
| Rodapé e método | 2 / 3 / 1 | 5 / 4 / 4 | sim | Fontes com link e data, método, download dos dados |
| Acessibilidade (geral) | 2 | 4 | sim | Contraste AA, texto alternativo, teclado |

**Resultado do critério 3 na rodada 4 (autorizada pelo usuário além do limite de 3): falta só o visual do topo** (o benchmark tem o vídeo ao lado do título). Depende da escolha da versão do vídeo pelo usuário.

Rodada 4 também corrigiu a margem por estado em 2026 (5.571 municípios): as 27 UFs, margens e viradas, conferem com a lista do benchmark (`site_tonycelestino_notas.md`).

