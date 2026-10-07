# Verificacao cruzada do leitor .dbc proprio (01_sim_dbc_extract.js) com o pacote read.dbc 1.2.0
# (arquivo do CRAN, compilado com Rtools45).
# Uso (da raiz do projeto): Rscript scripts/15_sim_crosscheck_readdbc.R
# Entradas: data/raw/sim/DOBR{2020,2021,2022}.dbc; data/derived/sim_covid_{ano}.csv; logs/sim_{ano}_resumo.json
# Saida: logs/15_sim_crosscheck_log.json (nao altera nenhum dado)
# Mesma regra do script 01: COVID_BASICA = CAUSABAS contem B342|U071|U072|U109;
# COVID_QUALQUER = basica ou o codigo aparece em LINHAA..LINHAII ou ATESTADO (sem espacos, pontos e asteriscos).

suppressPackageStartupMessages({ library(read.dbc); library(jsonlite) })

covid_re <- "B342|U071|U072|U109"
keep <- c("DTOBITO", "CODMUNRES", "CODMUNOCOR", "IDADE", "SEXO", "CAUSABAS",
          "LINHAA", "LINHAB", "LINHAC", "LINHAD", "LINHAII", "ATESTADO")
chave <- function(d) do.call(paste, c(d[keep], sep = "|"))

res <- list(executado_em = format(Sys.time(), tz = "UTC", usetz = TRUE),
            read_dbc = as.character(packageVersion("read.dbc")), R = R.version.string, anos = list())

for (ano in 2020:2022) {
  t0 <- Sys.time()
  d <- read.dbc(sprintf("data/raw/sim/DOBR%d.dbc", ano), as.is = TRUE)
  d[] <- lapply(d, function(v) { v <- trimws(as.character(v)); v[is.na(v)] <- ""; v })
  linhas <- gsub("[[:space:].*]", "", do.call(paste, c(d[c("LINHAA", "LINHAB", "LINHAC", "LINHAD", "LINHAII", "ATESTADO")], sep = " ")))
  basica <- grepl(covid_re, d$CAUSABAS)
  qualquer <- basica | grepl(covid_re, linhas)

  js <- read.csv(sprintf("data/derived/sim_covid_%d.csv", ano), colClasses = "character", na.strings = NULL)
  js[] <- lapply(js, function(v) { v[is.na(v)] <- ""; v })
  resumo_js <- fromJSON(sprintf("logs/sim_%d_resumo.json", ano))

  r_sel <- d[qualquer, keep]
  k_r <- sort(chave(r_sel)); k_js <- sort(chave(js))
  so_r <- setdiff(k_r, k_js); so_js <- setdiff(k_js, k_r)

  mun_r <- table(d$CODMUNRES[basica]); mun_js <- table(js$CODMUNRES[js$COVID_BASICA == "1"])
  todos <- union(names(mun_r), names(mun_js))
  a <- as.integer(mun_r[todos]); a[is.na(a)] <- 0L
  b <- as.integer(mun_js[todos]); b[is.na(b)] <- 0L

  res$anos[[as.character(ano)]] <- list(
    registros_read_dbc = nrow(d),
    obitos_total_js = resumo_js$obitos_total,
    registros_header_js = resumo_js$registros_header,
    covid_basica = c(read_dbc = sum(basica), js = resumo_js$covid_causa_basica, js_csv = sum(js$COVID_BASICA == "1")),
    covid_qualquer = c(read_dbc = sum(qualquer), js = resumo_js$covid_qualquer_linha, js_csv = nrow(js)),
    registros_identicos = identical(k_r, k_js),
    registros_so_read_dbc = length(so_r), registros_so_js = length(so_js),
    exemplos_divergentes = head(c(so_r, so_js), 5),
    municipios_comparados = length(todos),
    municipios_com_contagem_basica_diferente = sum(a != b),
    segundos = round(as.numeric(difftime(Sys.time(), t0, units = "secs")), 1)
  )
  cat(ano, ": read.dbc", nrow(d), "registros; basica", sum(basica), "vs js", resumo_js$covid_causa_basica,
      "; identicos:", identical(k_r, k_js), "\n")
  rm(d, js, r_sel); invisible(gc())
}

res$aprovado <- all(vapply(res$anos, function(x) isTRUE(x$registros_identicos) &&
  x$municipios_com_contagem_basica_diferente == 0 &&
  x$registros_read_dbc == x$obitos_total_js, logical(1)))
writeLines(toJSON(res, auto_unbox = TRUE, pretty = TRUE), "logs/15_sim_crosscheck_log.json", useBytes = TRUE)
cat("aprovado:", res$aprovado, "\n")
