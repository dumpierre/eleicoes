# 10_modelos.R
# Modelos pré-especificados em plano_analise_v1.md. Nível municipal; estimandos municipais.
# Uso (da raiz do projeto): Rscript scripts/10_modelos.R
suppressPackageStartupMessages(library(rms))
options(width = 160)
dir.create("output", showWarnings = FALSE)
sink("logs/10_modelos_saida.txt", split = TRUE)

b <- read.csv("data/derived/base_analitica.csv", colClasses = c(cd_ibge7 = "character", cod6 = "character", cd_tse = "character"))
b <- subset(b, !is.na(margem_22) & !is.na(renda_pc_mediana))
b$uf <- factor(b$uf)
b$log_renda <- log(b$renda_pc_mediana)
cat("municípios:", nrow(b), "\n")
dd <- datadist(b); options(datadist = "dd")

ajusta <- function(form, w) {
  f <- ols(form, data = b, weights = w, x = TRUE, y = TRUE)
  list(fit = f, rob = robcov(f), clu = robcov(f, cluster = b$uf))
}
contraste <- function(m, var, rotulo) {
  q <- quantile(b[[var]], c(.1, .9), na.rm = TRUE)
  out <- lapply(c("rob", "clu"), function(k) {
    a <- setNames(list(q[2]), var); r <- setNames(list(q[1]), var)
    k_ <- contrast(m[[k]], a, r)
    data.frame(modelo = rotulo, exposicao = var, p10 = q[1], p90 = q[2], erro_padrao = k,
               diff_margem_p90_menos_p10 = k_$Contrast, li = k_$Lower, ls = k_$Upper)
  })
  do.call(rbind, out)
}

w26 <- b$validos_26; w22 <- b$validos_22
mods <- list(
  A26 = ajusta(margem_26 ~ rcs(pct_bf_26, 4) + uf, w26),
  B26 = ajusta(margem_26 ~ rcs(pct_bf_26, 4) + uf + rcs(log_renda, 4) + rcs(alfabetizacao_15mais, 3) +
                 rcs(pct_evangelicas, 3) + rcs(pct_urbana, 3) + rcs(pct_60mais, 3), w26),
  A22 = ajusta(margem_22 ~ rcs(pct_ab_22, 4) + uf, w22),
  B22 = ajusta(margem_22 ~ rcs(pct_ab_22, 4) + uf + rcs(log_renda, 4) + rcs(alfabetizacao_15mais, 3) +
                 rcs(pct_evangelicas, 3) + rcs(pct_urbana, 3) + rcs(pct_60mais, 3), w22),
  # simétrico: renda como exposição, sem e com o programa
  R26 = ajusta(margem_26 ~ rcs(log_renda, 4) + uf, w26),
  RB26 = ajusta(margem_26 ~ rcs(log_renda, 4) + uf + rcs(pct_bf_26, 4) + rcs(alfabetizacao_15mais, 3) +
                  rcs(pct_evangelicas, 3) + rcs(pct_urbana, 3) + rcs(pct_60mais, 3), w26),
  # exploratório: COVID
  C22 = ajusta(margem_22 ~ rcs(smr_basica, 4) + uf, w22),
  CB22 = ajusta(margem_22 ~ rcs(smr_basica, 4) + uf + rcs(pct_ab_22, 4) + rcs(log_renda, 4) + rcs(alfabetizacao_15mais, 3) +
                  rcs(pct_evangelicas, 3) + rcs(pct_urbana, 3) + rcs(pct_60mais, 3), w22)
)

res <- rbind(
  contraste(mods$A26, "pct_bf_26", "A26: BF + UF"), contraste(mods$B26, "pct_bf_26", "B26: BF + UF + Censo"),
  contraste(mods$A22, "pct_ab_22", "A22: AB + UF"), contraste(mods$B22, "pct_ab_22", "B22: AB + UF + Censo"),
  contraste(mods$R26, "log_renda", "R26: renda + UF"), contraste(mods$RB26, "log_renda", "RB26: renda + UF + BF + Censo"),
  contraste(mods$C22, "smr_basica", "C22 (expl.): COVID SMR + UF"), contraste(mods$CB22, "smr_basica", "CB22 (expl.): COVID SMR + AB + UF + Censo")
)
res$p10 <- round(res$p10, 3); res$p90 <- round(res$p90, 3)
num <- c("diff_margem_p90_menos_p10", "li", "ls"); res[num] <- round(res[num], 1)
write.csv(res, "output/contrastes_p90_p10.csv", row.names = FALSE)
cat("\n=== Diferença de margem PL-Lula (pontos), P90 vs P10 da exposição ===\n"); print(res, row.names = FALSE)

cat("\n=== R2 ===\n")
print(sapply(mods, function(m) round(m$fit$stats["R2"], 3)))

cat("\n=== anova (erro padrão robusto) dos modelos B: chi2 - gl por bloco ===\n")
for (k in c("B26", "B22", "CB22")) {
  a <- anova(mods[[k]]$rob, test = "Chisq")
  cat("\n--", k, "\n"); print(round(cbind(chi2 = a[, "Chi-Square"], gl = a[, "d.f."], chi2_menos_gl = a[, "Chi-Square"] - a[, "d.f."]), 1))
}

png("output/efeito_parcial_bf_ab.png", width = 1600, height = 1000, res = 150)
pr <- function(m, v, rot) { d <- as.data.frame(Predict(m, name = v)); data.frame(x = d[[v]], yhat = d$yhat, lower = d$lower, upper = d$upper, modelo = rot) }
pp <- rbind(pr(mods$A26$rob, "pct_bf_26", "2026 BF: só UF"), pr(mods$B26$rob, "pct_bf_26", "2026 BF: + Censo"),
            pr(mods$A22$rob, "pct_ab_22", "2022 AB: só UF"), pr(mods$B22$rob, "pct_ab_22", "2022 AB: + Censo"))
write.csv(pp, "output/efeito_parcial_bf_ab.csv", row.names = FALSE)
par(mfrow = c(1, 2), mar = c(4.5, 4.5, 3, 1))
for (ano in c("2022 AB", "2026 BF")) {
  s <- pp[startsWith(pp$modelo, ano), ]
  plot(NA, xlim = range(s$x), ylim = range(c(s$lower, s$upper)), xlab = paste("% da população no", ifelse(ano == "2022 AB", "Auxílio Brasil (set/2022)", "Bolsa Família (set/2026)")),
       ylab = "Margem PL - Lula prevista (pontos)", main = ano)
  abline(h = 0, lty = 3)
  cols <- c("#c0392b", "#2c3e50"); i <- 0
  for (m in unique(s$modelo)) { i <- i + 1; t <- s[s$modelo == m, ]
    polygon(c(t$x, rev(t$x)), c(t$lower, rev(t$upper)), col = adjustcolor(cols[i], .2), border = NA)
    lines(t$x, t$yhat, col = cols[i], lwd = 2) }
  legend("topright", legend = unique(s$modelo), col = cols, lwd = 2, bty = "n")
}
dev.off()
sink()
