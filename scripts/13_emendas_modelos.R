# 13_emendas_modelos.R  (plano_analise_emendas_v1.md)
# Uso (da raiz do projeto): Rscript scripts/13_emendas_modelos.R
suppressPackageStartupMessages(library(rms))
options(width = 170)
sink("logs/13_emendas_modelos_saida.txt", split = TRUE)
b <- read.csv("data/derived/base_analitica_emendas.csv", colClasses = c(cd_ibge7 = "character", cod6 = "character", cd_tse = "character"))
b <- subset(b, !is.na(margem_22) & !is.na(renda_pc_mediana))
b$uf <- factor(b$uf)
b$log_pop <- log(b$pop_total)
b$log_renda <- log(b$renda_pc_mediana)
L <- function(x) log1p(x)
b$le <- L(b$emendas_municipal_pc); b$le_todos <- L(b$emendas_todos_favorecidos_pc)
b$le_ind <- L(b$emendas_municipal_individual_pc); b$le_col <- L(b$emendas_municipal_coletivas_pc)
b$le_pl <- L(b$emendas_municipal_ind_PL_pc); b$le_esq <- L(b$emendas_municipal_ind_esquerda_pc); b$le_dem <- L(b$emendas_municipal_ind_demais_pc)
cat("municípios:", nrow(b), "\n")
dd <- datadist(b); options(datadist = "dd")

# ---------- descritivo ----------
q <- function(x) cut(x, quantile(x, 0:5 / 5), include.lowest = TRUE, labels = paste0("Q", 1:5))
cat("\n=== Emendas a entes municipais (R$ per capita, jan/23-set/26) por quintil de margem PL 2022 ===\n")
b$qm22 <- q(b$margem_22)
print(aggregate(cbind(margem_22, emendas_municipal_pc, emendas_municipal_ind_PL_pc, emendas_municipal_ind_esquerda_pc, pop_total) ~ qm22, b, median))
cat("\n=== Deslocamento 2022->2026 (pontos, mediana) por quintil de emendas per capita ===\n")
b$qe <- q(b$emendas_municipal_pc)
print(aggregate(cbind(emendas_municipal_pc, delta_margem, margem_22, pop_total) ~ qe, b, median))
cat("\nCorrelação de Spearman: emendas pc x log pop =", round(cor(b$emendas_municipal_pc, b$pop_total, method = "spearman"), 2),
    "; emendas pc x margem 22 =", round(cor(b$emendas_municipal_pc, b$margem_22, method = "spearman"), 2),
    "; emendas pc x delta =", round(cor(b$emendas_municipal_pc, b$delta_margem, method = "spearman"), 2), "\n")

# ---------- modelos ----------
fit <- function(form, w = NULL) {
  f <- if (is.null(w)) ols(form, data = b, x = TRUE, y = TRUE) else ols(form, data = b, weights = w, x = TRUE, y = TRUE)
  list(rob = robcov(f), clu = robcov(f, cluster = b$uf), R2 = f$stats["R2"])
}
ctr <- function(m, var, rot) {
  qq <- quantile(b[[var]], c(.1, .9))
  do.call(rbind, lapply(c("rob", "clu"), function(k) {
    k_ <- contrast(m[[k]], setNames(list(qq[2]), var), setNames(list(qq[1]), var))
    data.frame(modelo = rot, var = var, p10 = round(qq[1], 2), p90 = round(qq[2], 2), ep = k,
               dif = round(k_$Contrast, 2), li = round(k_$Lower, 2), ls = round(k_$Upper, 2))
  }))
}
cens <- "+ rcs(log_renda, 4) + rcs(pct_evangelicas, 3) + rcs(pct_urbana, 3) + rcs(pct_60mais, 3) + rcs(alfabetizacao_15mais, 3)"
Fm <- function(s) as.formula(s)
w26 <- b$validos_26

# Q1 alocação: desfecho = log(1 + R$ pc); contraste = diferença no log (≈ razão de gasto - 1 para valores grandes)
m <- list(
  Q1a = fit(Fm("le ~ rcs(margem_22, 4) + rcs(log_pop, 4) + uf")),
  Q1b = fit(Fm(paste("le ~ rcs(margem_22, 4) + rcs(log_pop, 4) + uf", cens))),
  Q1_semPop = fit(Fm("le ~ rcs(margem_22, 4) + uf")),
  Q1_pop_pond = fit(Fm("le ~ rcs(margem_22, 4) + rcs(log_pop, 4) + uf"), b$pop_total),
  Q1_todos = fit(Fm("le_todos ~ rcs(margem_22, 4) + rcs(log_pop, 4) + uf")),
  Q1_ind = fit(Fm("le_ind ~ rcs(margem_22, 4) + rcs(log_pop, 4) + uf")),
  Q1_col = fit(Fm("le_col ~ rcs(margem_22, 4) + rcs(log_pop, 4) + uf")),
  Q3_PL = fit(Fm("le_pl ~ rcs(margem_22, 4) + rcs(log_pop, 4) + uf")),
  Q3_esq = fit(Fm("le_esq ~ rcs(margem_22, 4) + rcs(log_pop, 4) + uf")),
  Q3_dem = fit(Fm("le_dem ~ rcs(margem_22, 4) + rcs(log_pop, 4) + uf")),
  # Q2 efeito: desfecho = deslocamento da margem 2022->2026 (pontos)
  Q2a = fit(Fm("delta_margem ~ rcs(le, 4) + rcs(margem_22, 4) + rcs(log_pop, 4) + uf"), w26),
  Q2b = fit(Fm(paste("delta_margem ~ rcs(le, 4) + rcs(margem_22, 4) + rcs(log_pop, 4) + uf", cens)), w26),
  Q2b_sempeso = fit(Fm(paste("delta_margem ~ rcs(le, 4) + rcs(margem_22, 4) + rcs(log_pop, 4) + uf", cens))),
  Q2_todos = fit(Fm(paste("delta_margem ~ rcs(le_todos, 4) + rcs(margem_22, 4) + rcs(log_pop, 4) + uf", cens)), w26),
  Q2_PL = fit(Fm(paste("delta_margem ~ rcs(le_pl, 4) + rcs(margem_22, 4) + rcs(log_pop, 4) + uf", cens)), w26),
  Q2_esq = fit(Fm(paste("delta_margem ~ rcs(le_esq, 4) + rcs(margem_22, 4) + rcs(log_pop, 4) + uf", cens)), w26)
)
res <- rbind(
  ctr(m$Q1a, "margem_22", "Q1a aloc: emendas ~ margem22 + pop + UF"),
  ctr(m$Q1b, "margem_22", "Q1b aloc: + Censo"),
  ctr(m$Q1_semPop, "margem_22", "Q1 sens: sem pop"),
  ctr(m$Q1_pop_pond, "margem_22", "Q1 sens: ponderado por pop"),
  ctr(m$Q1_todos, "margem_22", "Q1 sens: todos favorecidos"),
  ctr(m$Q1_ind, "margem_22", "Q1 sens: só individuais"),
  ctr(m$Q1_col, "margem_22", "Q1 sens: só bancada/comissão/relator"),
  ctr(m$Q3_PL, "margem_22", "Q3: individuais de autores do PL"),
  ctr(m$Q3_esq, "margem_22", "Q3: individuais PT/PCdoB/PV/PSOL/Rede/PSB/PDT"),
  ctr(m$Q3_dem, "margem_22", "Q3: individuais demais partidos"),
  ctr(m$Q2a, "le", "Q2a efeito: delta ~ emendas + margem22 + pop + UF"),
  ctr(m$Q2b, "le", "Q2b efeito: + Censo"),
  ctr(m$Q2b_sempeso, "le", "Q2 sens: sem peso"),
  ctr(m$Q2_todos, "le_todos", "Q2 sens: todos favorecidos"),
  ctr(m$Q2_PL, "le_pl", "Q2: individuais do PL"),
  ctr(m$Q2_esq, "le_esq", "Q2: individuais esquerda")
)
write.csv(res, "output/emendas_contrastes.csv", row.names = FALSE)
cat("\n=== Contrastes P90 vs P10 ===\nQ1/Q3: diferença em log(1 + R$ pc) entre municípios no P90 e no P10 da margem PL 2022 (exp(dif) ≈ razão)\nQ2: diferença no deslocamento 2022->2026 (pontos) entre P90 e P10 de log(1 + emendas pc)\n")
print(res, row.names = FALSE)
cat("\nR2:\n"); print(round(sapply(m, `[[`, "R2"), 3))
cat("\nAnova robusta Q1a e Q2b (chi2 - gl):\n")
for (k in c("Q1a", "Q2b")) { a <- anova(m[[k]]$rob, test = "Chisq"); cat("--", k, "\n"); print(round(cbind(chi2 = a[, "Chi-Square"], gl = a[, "d.f."], chi2_gl = a[, "Chi-Square"] - a[, "d.f."]), 1)) }

pr <- function(mm, v, rot) { d <- as.data.frame(Predict(mm$rob, name = v)); data.frame(x = d[[v]], yhat = d$yhat, lower = d$lower, upper = d$upper, modelo = rot) }
pp <- rbind(pr(m$Q1a, "margem_22", "Q1 todas"), pr(m$Q3_PL, "margem_22", "Q3 PL"), pr(m$Q3_esq, "margem_22", "Q3 esquerda"))
write.csv(pp, "output/emendas_efeito_parcial_q1.csv", row.names = FALSE)
png("output/emendas_q1_q2.png", width = 1700, height = 900, res = 150)
par(mfrow = c(1, 2), mar = c(4.5, 4.5, 3, 1))
cols <- c("Q1 todas" = "#2c3e50", "Q3 PL" = "#2471a3", "Q3 esquerda" = "#c0392b")
plot(NA, xlim = range(pp$x), ylim = range(c(pp$lower, pp$upper)), xlab = "Margem PL - Lula no 1º turno 2022 (pontos)",
     ylab = "log(1 + R$ per capita) previsto", main = "Q1/Q3: para onde foi a verba (2023-2026)")
for (k in names(cols)) { t <- pp[pp$modelo == k, ]; polygon(c(t$x, rev(t$x)), c(t$lower, rev(t$upper)), col = adjustcolor(cols[k], .2), border = NA); lines(t$x, t$yhat, col = cols[k], lwd = 2) }
legend("topleft", c("Todas (entes municipais)", "Individuais de autores do PL", "Individuais PT e aliados"), col = cols, lwd = 2, bty = "n", cex = .8)
p2 <- pr(m$Q2b, "le", "Q2b")
plot(p2$x, p2$yhat, type = "n", ylim = range(c(p2$lower, p2$upper)), xlab = "log(1 + R$ per capita em emendas, 2023-2026)",
     ylab = "Deslocamento previsto 2022->2026 (pontos para o PL)", main = "Q2: verba e deslocamento (ajustado)")
polygon(c(p2$x, rev(p2$x)), c(p2$lower, rev(p2$upper)), col = adjustcolor("#2c3e50", .2), border = NA); lines(p2$x, p2$yhat, lwd = 2)
dev.off()
sink()
