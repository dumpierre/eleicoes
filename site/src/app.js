(function () {
  'use strict';
  // Nenhum número de dado é escrito aqui: tudo vem de #dados (gerado por site/build.py) ou do texto da página.
  var D = JSON.parse(document.getElementById('dados').textContent);
  var C = D.c, N = C.id.length;
  var RGB = { lula: [236, 109, 93], pl: [90, 165, 251], neutro: [91, 93, 104] };
  var TXT = '#e6e7ec', SEC = '#9a9ba6', GRADE = '#262833', BORDA = '#2a2c38', AMBAR = '#e2a632', BG2 = '#15161d';
  var RM = window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches;

  // ---------- derivados ----------
  var m26 = new Float32Array(N), m22 = new Float32Array(N), lrd = new Float32Array(N), maxEl = 0;
  for (var i = 0; i < N; i++) {
    m26[i] = 100 * (C.f26[i] - C.l26[i]) / C.v26[i];
    m22[i] = 100 * (C.b22[i] - C.l22[i]) / C.v22[i];
    lrd[i] = Math.log(C.rd[i]);
    if (C.el[i] > maxEl) maxEl = C.el[i];
  }
  var semAcento = function (s) { return s.normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase(); };
  var nomeN = C.nome.map(semAcento);

  function fmt(x, c) {
    if (c === undefined) c = 1;
    return x.toLocaleString('pt-BR', { minimumFractionDigits: c, maximumFractionDigits: c }).replace('-', '−');
  }
  function margemTxt(m, ano) {
    var r = Math.round(Math.abs(m) * 10) / 10;
    if (r === 0) return 'empate';
    return (m < 0 ? 'Lula' : (ano === '22' ? 'Bolsonaro' : 'Flávio')) + ' +' + fmt(Math.abs(m));
  }
  function pct(a, b) { return 100 * a / b; }

  // ---------- estado ----------
  var st = { lente: 'mapa', alt: { mapa: '26', divisao: 'cid', bf: 'bf', ab22: '22' }, sel: -1, uf: null, hover: -1 };
  var cv = document.getElementById('cv'), ctx = cv.getContext('2d');
  var caixa = cv.parentNode, dica = document.getElementById('dica');
  var W = 0, H = 0, DPR = 1, PAD = { l: 52, r: 12, t: 26, b: 42 };
  var cur = { x: new Float32Array(N), y: new Float32Array(N), r: new Float32Array(N), c: new Float32Array(N * 3), a: new Float32Array(N) };
  var de = null, para = null, t0 = 0, anim = false, prog = 1, extra = {};

  function medir() {
    W = caixa.clientWidth;
    var celular = W < 560;
    H = Math.round(Math.max(320, Math.min(celular ? W * 1.05 : W * 0.72, 560)));
    DPR = Math.min(window.devicePixelRatio || 1, 2);
    cv.width = Math.round(W * DPR); cv.height = Math.round(H * DPR);
    cv.style.height = H + 'px';
    PAD = celular ? { l: 50, r: 8, t: 26, b: 56 } : { l: 56, r: 14, t: 28, b: 44 };
  }

  function corMargem(m, out, k, piso) {
    var p0 = piso === undefined ? 0.3 : piso;
    var t = Math.min(Math.abs(m) / 45, 1), base = m < 0 ? RGB.lula : RGB.pl, f = p0 + (1 - p0) * t;
    for (var j = 0; j < 3; j++) out[k + j] = RGB.neutro[j] + (base[j] - RGB.neutro[j]) * f;
  }
  function raio(i, maxR) { return Math.max(0.9, Math.sqrt(C.el[i] / maxEl) * maxR); }

  // ---------- escalas ----------
  var ESC = {};
  function escala(d0, d1, r0, r1) { return function (v) { return r0 + (v - d0) / (d1 - d0) * (r1 - r0); }; }
  function absMax(arr) { var m = 0; for (var i = 0; i < arr.length; i++) m = Math.max(m, Math.abs(arr[i])); return Math.ceil(m / 10) * 10; }
  var YMAX = Math.max(absMax(m26), absMax(m22));

  // ---------- layouts ----------
  function alvo() {
    var L = { x: new Float32Array(N), y: new Float32Array(N), r: new Float32Array(N), c: new Float32Array(N * 3), a: new Float32Array(N) };
    var pw = W - PAD.l - PAD.r, ph = H - PAD.t - PAD.b, celular = W < 560;
    var maxR = celular ? 7 : 10, alfa = 0.78;
    extra = {};
    var l = st.lente, i;
    if (l === 'mapa') {
      var ano = st.alt.mapa, mm = ano === '22' ? m22 : m26;
      var kx = Math.cos(-15 * Math.PI / 180), lon0 = -74, lon1 = -34.5, lat0 = -34, lat1 = 5.4;
      var s = Math.min((W - 16) / ((lon1 - lon0) * kx), (H - 16) / (lat1 - lat0));
      var ox = (W - (lon1 - lon0) * kx * s) / 2, oy = (H - (lat1 - lat0) * s) / 2;
      ESC.lon = function (v) { return ox + (v - lon0) * kx * s; };
      ESC.lat = function (v) { return oy + (lat1 - v) * s; };
      for (i = 0; i < N; i++) {
        L.x[i] = ESC.lon(C.lon[i]); L.y[i] = ESC.lat(C.lat[i]); L.r[i] = raio(i, celular ? 11 : 16);
        corMargem(mm[i], L.c, i * 3, 0.5); L.a[i] = 0.95;
      }
    } else if (l === 'divisao') {
      var lo = -YMAX, larg = 2, nb = Math.round(2 * YMAX / larg), cont = new Array(nb).fill(0), vot = new Array(nb).fill(0);
      var bin = new Int16Array(N);
      for (i = 0; i < N; i++) { var b = Math.min(nb - 1, Math.max(0, Math.floor((m26[i] - lo) / larg))); bin[i] = b; cont[b]++; vot[b] += C.v26[i]; }
      var maxC = Math.max.apply(null, cont), maxV = Math.max.apply(null, vot);
      ESC.x = escala(-YMAX, YMAX, PAD.l, PAD.l + pw);
      var base = PAD.t + ph, ds = ph / maxC, rr = Math.max(0.8, Math.min(ds * 0.55, (pw / nb) * 0.38, 2.4));
      var ordem = Array.from({ length: N }, function (_, k) { return k; }).sort(function (a, b) { return m26[a] - m26[b]; });
      var pilha = new Array(nb).fill(0), modoVot = st.alt.divisao === 'vot';
      ordem.forEach(function (k) {
        var b = bin[k], cx = ESC.x(lo + (b + 0.5) * larg);
        L.x[k] = cx;
        L.y[k] = modoVot ? base - (vot[b] / maxV) * ph * ((pilha[b] + 0.5) / cont[b]) : base - (pilha[b] + 0.5) * ds;
        pilha[b]++;
        L.r[k] = rr; corMargem(m26[k], L.c, k * 3); L.a[k] = modoVot ? 0 : 0.95;
      });
      extra.hist = { nb: nb, larg: larg, lo: lo, vot: vot, maxV: maxV, maxC: maxC, modoVot: modoVot };
    } else {
      var xv, yv, x0, x1, ano2 = '26';
      if (l === 'bf' && st.alt.bf === 'bf') { xv = C.bf; x0 = 0; x1 = 105; }
      else if (l === 'bf') { xv = lrd; x0 = Math.log(4500); x1 = Math.log(250); }
      else if (l === 'renda') { xv = lrd; x0 = Math.log(250); x1 = Math.log(4500); }
      else if (l === 'ev') { xv = C.ev; x0 = 0; x1 = 90; }
      else if (l === 'd22') { xv = m22; x0 = -YMAX; x1 = YMAX; }
      else if (l === 'ab22' && st.alt.ab22 === '22') { xv = C.ab; x0 = 0; x1 = 105; ano2 = '22'; }
      else { xv = C.bf; x0 = 0; x1 = 105; }
      yv = ano2 === '22' ? m22 : m26;
      ESC.x = escala(x0, x1, PAD.l, PAD.l + pw);
      ESC.y = escala(YMAX, -YMAX, PAD.t, PAD.t + ph);
      for (i = 0; i < N; i++) {
        L.x[i] = ESC.x(xv[i]); L.y[i] = ESC.y(yv[i]); L.r[i] = raio(i, maxR);
        corMargem(yv[i], L.c, i * 3); L.a[i] = alfa;
      }
      extra.ano = ano2;
    }
    if (st.uf) for (i = 0; i < N; i++) if (C.uf[i] !== st.uf) L.a[i] *= 0.12;
    if (l === 'ajuste') for (i = 0; i < N; i++) L.a[i] = 0;
    return L;
  }

  // ---------- eixos ----------
  function texto(s, x, y, cor, al, bl, tam) {
    ctx.fillStyle = cor || SEC; ctx.textAlign = al || 'left'; ctx.textBaseline = bl || 'middle';
    ctx.font = (tam || 11) + 'px "Plex Mono", ui-monospace, monospace';
    ctx.fillText(s, x, y);
  }
  function linha(x0, y0, x1, y1, cor, tr) {
    ctx.strokeStyle = cor; ctx.lineWidth = 1; ctx.setLineDash(tr ? [4, 4] : []);
    ctx.beginPath(); ctx.moveTo(x0, y0); ctx.lineTo(x1, y1); ctx.stroke(); ctx.setLineDash([]);
  }
  function eixoY(ano) {
    var x0 = PAD.l, x1 = W - PAD.r;
    [-80, -40, 0, 40, 80].forEach(function (v) {
      if (Math.abs(v) > YMAX) return;
      var y = ESC.y(v);
      linha(x0, y, x1, y, v === 0 ? '#3a3c48' : GRADE, v === 0);
      texto(v === 0 ? 'empate' : (v < 0 ? 'L +' : (ano === '22' ? 'B +' : 'F +')) + Math.abs(v), x0 - 6, y, v < 0 ? '#f08a7c' : (v > 0 ? '#7fb6fb' : SEC), 'right');
    });
    texto('↑ ' + (ano === '22' ? 'Bolsonaro' : 'Flávio') + ' na frente', x0 + 4, PAD.t - 12, '#7fb6fb');
    texto('↓ Lula na frente', x0 + 4, H - PAD.b + (W < 560 ? 46 : 30), '#f08a7c');
  }
  function eixoX(ticks, rotulo, fmtT) {
    var yb = H - PAD.b;
    ticks.forEach(function (v) {
      var x = ESC.x(v);
      linha(x, PAD.t, x, yb, GRADE);
      texto(fmtT(v), x, yb + 12, SEC, 'center');
    });
    texto(rotulo, W - PAD.r, yb + 30, SEC, 'right');
  }
  var rendaTicks = [300, 500, 1000, 2000, 4000];
  var fmtR = function (v) { return 'R$ ' + Math.round(Math.exp(v)).toLocaleString('pt-BR'); };
  var fmtP = function (v) { return v + '%'; };

  function decoracao() {
    var l = st.lente, celular = W < 560;
    if (l === 'mapa') {
      ctx.strokeStyle = '#2c2e3a'; ctx.lineWidth = 0.8;
      D.uf_geo.forEach(function (anel) {
        ctx.beginPath();
        anel.forEach(function (p, k) { var x = ESC.lon(p[0]), y = ESC.lat(p[1]); if (k) ctx.lineTo(x, y); else ctx.moveTo(x, y); });
        ctx.closePath(); ctx.stroke();
      });
      return;
    }
    if (l === 'ajuste') return;
    if (l === 'divisao') {
      var h = extra.hist, yb = H - PAD.b;
      ESC.y = null;
      [-80, -40, -20, 0, 20, 40, 80].forEach(function (v) {
        if (Math.abs(v) > YMAX) return;
        var x = ESC.x(v);
        linha(x, PAD.t, x, yb, v === 0 ? '#3a3c48' : GRADE, v === 0);
        texto(v === 0 ? 'empate' : (v < 0 ? 'L +' : 'F +') + Math.abs(v), x, yb + 12, v < 0 ? '#f08a7c' : (v > 0 ? '#7fb6fb' : SEC), 'center');
      });
      texto('← Lula vence por mais', ESC.x(-YMAX) + 2, PAD.t - 12, '#f08a7c');
      texto('Flávio vence por mais →', W - PAD.r, PAD.t - 12, '#7fb6fb', 'right');
      texto(h.modoVot ? 'altura: votos válidos na faixa' : 'altura: número de cidades na faixa', W - PAD.r, yb + 30, SEC, 'right');
      if (h.modoVot && prog > 0.2) {
        var ph = H - PAD.t - PAD.b, bw = (W - PAD.l - PAD.r) / h.nb;
        ctx.globalAlpha = Math.min(1, (prog - 0.2) / 0.6);
        for (var b = 0; b < h.nb; b++) {
          var c = h.lo + (b + 0.5) * h.larg, alt = h.vot[b] / h.maxV * ph, cc = [0, 0, 0];
          corMargem(c, cc, 0);
          ctx.fillStyle = 'rgb(' + cc.map(Math.round).join(',') + ')';
          ctx.fillRect(ESC.x(h.lo + b * h.larg) + 1, yb - alt, Math.max(1, bw - 2), alt);
        }
        ctx.globalAlpha = 1;
      }
      return;
    }
    var ano = extra.ano || '26';
    eixoY(ano);
    if (l === 'bf' && st.alt.bf === 'bf') eixoX([0, 20, 40, 60, 80, 100], 'população em famílias do Bolsa Família →', fmtP);
    else if (l === 'bf') eixoX(rendaTicks.map(Math.log), celular ? '← mais rica · renda · mais pobre →' : '← cidade mais rica · renda média por pessoa (log) · mais pobre →', fmtR);
    else if (l === 'renda') eixoX(rendaTicks.map(Math.log), 'renda média por pessoa (escala log) →', fmtR);
    else if (l === 'ev') eixoX([0, 15, 30, 45, 60, 75, 90], 'evangélicos na população →', fmtP);
    else if (l === 'ab22') eixoX([0, 20, 40, 60, 80, 100], ano === '22' ? 'população em famílias do Auxílio Brasil, 2022 →' : 'população em famílias do Bolsa Família, 2026 →', fmtP);
    else if (l === 'd22') {
      eixoX([-80, -40, 0, 40, 80].filter(function (v) { return Math.abs(v) <= YMAX; }), '2022: Lula × Bolsonaro →', function (v) { return v === 0 ? 'empate' : (v < 0 ? 'L +' : 'B +') + Math.abs(v); });
      linha(ESC.x(-YMAX), ESC.y(-YMAX), ESC.x(YMAX), ESC.y(YMAX), '#6a6c78', true);
      linha(ESC.x(0), PAD.t, ESC.x(0), H - PAD.b, '#3a3c48', true);
      texto(celular ? '↖ andou para o PL' : 'acima da diagonal: andou para o PL', ESC.x(YMAX) - 4, ESC.y(YMAX * (celular ? 0.6 : 0.92)), SEC, 'right');
      texto(celular ? 'viraram para Flávio' : 'Lula em 2022, Flávio em 2026', ESC.x(-YMAX * 0.5), ESC.y(YMAX * 0.7), TXT, 'center');
      texto(celular ? 'viraram para Lula' : 'Bolsonaro em 2022, Lula em 2026', ESC.x(YMAX * 0.5), ESC.y(-YMAX * 0.7), TXT, 'center');
    }
  }

  function curvaRenda() {
    if (st.lente !== 'renda') return;
    ctx.globalAlpha = prog; ctx.strokeStyle = AMBAR; ctx.lineWidth = 2.5; ctx.lineJoin = 'round';
    ctx.beginPath();
    D.curva_renda.forEach(function (p, k) { var x = ESC.x(Math.log(p[0])), y = ESC.y(p[1]); if (k) ctx.lineTo(x, y); else ctx.moveTo(x, y); });
    ctx.stroke(); ctx.globalAlpha = 1;
    var u = D.curva_renda[D.curva_renda.length - 1];
    texto('curva', ESC.x(Math.log(u[0])) - 2, ESC.y(u[1]) - 12, AMBAR, 'right');
  }

  // ---------- desenho ----------
  function desenhar() {
    ctx.setTransform(DPR, 0, 0, DPR, 0, 0);
    ctx.clearRect(0, 0, W, H);
    if (st.lente === 'ajuste') return;
    decoracao();
    if (st.lente === 'mapa') {  // brilho: halo largo e fraco sob cada ponto
      for (var h = 0; h < N; h++) {
        if (cur.a[h] < 0.02) continue;
        ctx.globalAlpha = cur.a[h] * 0.09;
        ctx.fillStyle = 'rgb(' + (cur.c[h * 3] | 0) + ',' + (cur.c[h * 3 + 1] | 0) + ',' + (cur.c[h * 3 + 2] | 0) + ')';
        ctx.beginPath(); ctx.arc(cur.x[h], cur.y[h], Math.min(cur.r[h] * 1.8 + 1.2, cur.r[h] + 5), 0, 6.2832); ctx.fill();
      }
    }
    for (var i = 0; i < N; i++) {
      var a = cur.a[i];
      if (a < 0.02) continue;
      ctx.globalAlpha = a;
      ctx.fillStyle = 'rgb(' + (cur.c[i * 3] | 0) + ',' + (cur.c[i * 3 + 1] | 0) + ',' + (cur.c[i * 3 + 2] | 0) + ')';
      ctx.beginPath(); ctx.arc(cur.x[i], cur.y[i], cur.r[i], 0, 6.2832); ctx.fill();
    }
    ctx.globalAlpha = 1;
    curvaRenda();
    [st.hover, st.sel].forEach(function (k, n) {
      if (k < 0 || (n === 0 && k === st.sel)) return;
      ctx.strokeStyle = n ? AMBAR : TXT; ctx.lineWidth = 2;
      ctx.beginPath(); ctx.arc(cur.x[k], cur.y[k], cur.r[k] + 4, 0, 6.2832); ctx.stroke();
      if (n) {
        var rot = C.nome[k] + ' (' + C.uf[k] + ')';
        ctx.font = '600 13px "Plex Cond", sans-serif';
        var w = ctx.measureText(rot).width + 12, x = Math.min(Math.max(cur.x[k] - w / 2, 2), W - w - 2), y = cur.y[k] - cur.r[k] - 30;
        if (y < 2) y = cur.y[k] + cur.r[k] + 8;
        ctx.fillStyle = 'rgba(28,29,38,.95)'; ctx.fillRect(x, y, w, 22);
        ctx.strokeStyle = AMBAR; ctx.lineWidth = 1; ctx.strokeRect(x + .5, y + .5, w - 1, 21);
        ctx.fillStyle = TXT; ctx.textAlign = 'left'; ctx.textBaseline = 'middle'; ctx.fillText(rot, x + 6, y + 11);
      }
    });
  }

  var ease = function (t) { return t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2; };
  function quadro(agora) {
    prog = Math.min(1, (agora - t0) / 1000);
    for (var i = 0; i < N; i++) {
      var d0 = (i % 97) / 97 * 0.25, t = ease(Math.min(1, Math.max(0, (prog - d0) / 0.75)));
      cur.x[i] = de.x[i] + (para.x[i] - de.x[i]) * t;
      cur.y[i] = de.y[i] + (para.y[i] - de.y[i]) * t;
      cur.r[i] = de.r[i] + (para.r[i] - de.r[i]) * t;
      cur.a[i] = de.a[i] + (para.a[i] - de.a[i]) * t;
      for (var j = 0; j < 3; j++) cur.c[i * 3 + j] = de.c[i * 3 + j] + (para.c[i * 3 + j] - de.c[i * 3 + j]) * t;
    }
    desenhar();
    if (prog < 1) requestAnimationFrame(quadro); else anim = false;
  }
  function copiar(L) { cur.x.set(L.x); cur.y.set(L.y); cur.r.set(L.r); cur.c.set(L.c); cur.a.set(L.a); }
  function atualizar(animar) {
    var L = alvo();
    if (!animar || RM) { copiar(L); prog = 1; desenhar(); return; }
    de = { x: cur.x.slice(), y: cur.y.slice(), r: cur.r.slice(), c: cur.c.slice(), a: cur.a.slice() };
    para = L; t0 = performance.now(); prog = 0;
    if (!anim) { anim = true; requestAnimationFrame(quadro); }
  }

  // ---------- textos por painel ----------
  var LEG = {
    mapa: function () { return 'Cor: margem em ' + (st.alt.mapa === '22' ? '2022 (vermelho, Lula; azul, Bolsonaro)' : '2026 (vermelho, Lula; azul, Flávio)') + '. Tamanho: eleitorado.'; },
    divisao: function () { return 'Margem em 2026, em faixas de 2 pontos. ' + (st.alt.divisao === 'vot' ? 'Altura: votos válidos dados nas cidades da faixa.' : 'Cada pontinho: uma cidade.'); },
    bf: function () { return (st.alt.bf === 'bf' ? 'Horizontal: % da população em famílias do Bolsa Família (set/2026).' : 'Horizontal: renda média por pessoa, da cidade mais rica (esquerda) para a mais pobre (direita).') + ' Vertical: margem em 2026. Tamanho: eleitorado.'; },
    renda: function () { return 'Horizontal: renda média por pessoa (Censo 2022, escala log). Vertical: margem em 2026. Linha âmbar: curva descritiva.'; },
    ev: function () { return 'Horizontal: % de evangélicos (Censo 2022). Vertical: margem em 2026. Tamanho: eleitorado.'; },
    d22: function () { return 'Horizontal: margem em 2022 (Lula × Bolsonaro). Vertical: margem em 2026 (Lula × Flávio). Tracejado: sem mudança.'; },
    ab22: function () { return st.alt.ab22 === '22' ? 'Horizontal: % da população em famílias do Auxílio Brasil (set/2022). Vertical: margem em 2022 (Lula × Bolsonaro).' : 'Horizontal: % da população em famílias do Bolsa Família (set/2026). Vertical: margem em 2026 (Lula × Flávio).'; },
    ajuste: function () { return 'Aqui não há pontos de cidades: são estimativas de um modelo feito com os dados das cidades.'; }
  };
  var FONTE = {
    mapa: 'TSE, 1º turno 2022 e 2026 · IBGE, malhas.', divisao: 'TSE, 1º turno 2026.',
    bf: 'TSE 2026 · MDS, Bolsa Família set/2026 · IBGE, Censo 2022.', renda: 'TSE 2026 · IBGE, Censo 2022.', ev: 'TSE 2026 · IBGE, Censo 2022.',
    d22: 'TSE, 1º turno 2022 e 2026.', ab22: 'TSE 2022 e 2026 · MDS, Auxílio Brasil set/2022 e Bolsa Família set/2026 · IBGE, Censo 2022 · EC 123/2022.',
    ajuste: 'Modelos sobre dados do TSE, MDS e IBGE (método no fim da página).'
  };
  var ARIA = {
    mapa: 'Mapa de pontos do Brasil, um por município, colorido pela margem. Nordeste e Norte em vermelho (Lula), Sul, Sudeste e Centro-Oeste em azul.',
    divisao: 'Histograma da margem de 2026 por município.',
    bf: 'Dispersão: % no Bolsa Família contra a margem. Cidades com mais programa ficam mais para o lado de Lula.',
    renda: 'Dispersão: renda média contra a margem, com curva que sobe e depois desce nas cidades mais ricas.',
    ev: 'Dispersão: % de evangélicos contra a margem, nuvem larga.',
    d22: 'Dispersão: margem de 2022 contra margem de 2026; quase todos os pontos acima da diagonal.',
    ab22: 'Dispersão: % no programa contra a margem, em 2022 com o Auxílio Brasil e em 2026 com o Bolsa Família; o desenho é o mesmo.',
    ajuste: 'Gráfico de estimativas com intervalos.'
  };

  var abas = Array.prototype.slice.call(document.querySelectorAll('[role=tab]'));
  function mostrar(sel, lente) {
    document.querySelectorAll(sel).forEach(function (el) {
      var alvoL = el.getAttribute('data-lente') || el.getAttribute('data-para');
      el.hidden = alvoL !== lente;
    });
  }
  function setLente(l, foco) {
    st.lente = l;
    abas.forEach(function (b) {
      var on = b.getAttribute('data-lente') === l;
      b.setAttribute('aria-selected', on); b.tabIndex = on ? 0 : -1;
      if (on && foco) b.focus();
      if (on) { document.getElementById('p-graf').setAttribute('aria-labelledby', b.id); b.scrollIntoView({ block: 'nearest', inline: 'nearest' }); }
    });
    mostrar('.lente-texto', l); mostrar('.lente-mais', l); mostrar('.alternar', l); mostrar('.extra', l); mostrar('.contrastes', l);
    cv.hidden = l === 'ajuste';
    textos();
    atualizar(true);
  }
  function textos() {
    document.getElementById('legenda-lente').textContent = LEG[st.lente]();
    document.getElementById('fonte-lente').textContent = FONTE[st.lente];
    cv.setAttribute('aria-label', ARIA[st.lente]);
    var fb = document.getElementById('filtro-uf');
    if (st.uf) {
      if (!fb) {
        fb = document.createElement('button'); fb.id = 'filtro-uf'; fb.className = 'botao';
        fb.addEventListener('click', function () { st.uf = null; textos(); atualizar(true); });
        document.querySelector('.ressalva').appendChild(fb);
      }
      fb.textContent = 'Mostrando ' + D.c.ufs[st.uf].nome + ' · ver o Brasil inteiro';
    } else if (fb) fb.remove();
  }
  abas.forEach(function (b, k) {
    b.addEventListener('click', function () { setLente(b.getAttribute('data-lente')); });
    b.addEventListener('keydown', function (e) {
      var n = { ArrowRight: k + 1, ArrowLeft: k - 1, Home: 0, End: abas.length - 1 }[e.key];
      if (n === undefined) return;
      e.preventDefault(); n = (n + abas.length) % abas.length;
      setLente(abas[n].getAttribute('data-lente'), true);
    });
  });
  document.querySelectorAll('.alternar').forEach(function (g) {
    var l = g.getAttribute('data-para');
    g.querySelectorAll('button').forEach(function (b) {
      b.addEventListener('click', function () {
        st.alt[l] = b.getAttribute('data-v');
        g.querySelectorAll('button').forEach(function (x) { x.setAttribute('aria-pressed', x === b); });
        textos(); atualizar(true);
      });
    });
  });

  // ---------- dica e seleção ----------
  function maisPerto(px, py, tol) {
    var melhor = -1, dm = Infinity;
    for (var i = 0; i < N; i++) {
      if (cur.a[i] < 0.05) continue;
      var dx = cur.x[i] - px, dy = cur.y[i] - py, d = dx * dx + dy * dy, lim = Math.max(cur.r[i] + 3, tol);
      if (d < lim * lim && d < dm) { dm = d; melhor = i; }
    }
    return melhor;
  }
  function valorX(i) {
    var l = st.lente;
    if (l === 'bf') return st.alt.bf === 'bf' ? 'Bolsa Família: ' + fmt(C.bf[i]) + '%' : 'Renda média: R$ ' + C.rd[i].toLocaleString('pt-BR');
    if (l === 'renda') return 'Renda média: R$ ' + C.rd[i].toLocaleString('pt-BR');
    if (l === 'ev') return 'Evangélicos: ' + fmt(C.ev[i]) + '%';
    if (l === 'd22' || l === 'mapa') return '2022: ' + margemTxt(m22[i], '22');
    if (l === 'ab22') return st.alt.ab22 === '22' ? 'Auxílio Brasil: ' + fmt(C.ab[i]) + '%' : 'Bolsa Família: ' + fmt(C.bf[i]) + '%';
    return 'Eleitorado: ' + C.el[i].toLocaleString('pt-BR');
  }
  function posDica(i, px, py) {
    var ano = (st.lente === 'ab22' && st.alt.ab22 === '22') || (st.lente === 'mapa' && st.alt.mapa === '22') ? '22' : '26';
    var m = ano === '22' ? m22[i] : m26[i];
    dica.innerHTML = '<div class="n"></div><div class="s"></div><div class="s"></div>';
    dica.children[0].textContent = C.nome[i] + ' (' + C.uf[i] + ')';
    dica.children[1].textContent = (ano === '22' ? '2022: ' : '2026: ') + margemTxt(m, ano);
    dica.children[2].textContent = (st.lente === 'mapa' && ano === '22') ? '2026: ' + margemTxt(m26[i], '26') : valorX(i);
    dica.hidden = false;
    var w = dica.offsetWidth, h = dica.offsetHeight;
    dica.style.left = Math.min(Math.max(px + 14, 0), W - w) + 'px';
    dica.style.top = Math.max(py - h - 10, 0) + 'px';
  }
  function xy(e) { var r = cv.getBoundingClientRect(); return [e.clientX - r.left, e.clientY - r.top]; }
  cv.addEventListener('pointermove', function (e) {
    if (e.pointerType === 'touch') return;
    var p = xy(e), k = maisPerto(p[0], p[1], 8);
    if (k !== st.hover) { st.hover = k; if (!anim) desenhar(); }
    if (k >= 0) posDica(k, p[0], p[1]); else dica.hidden = true;
  });
  cv.addEventListener('pointerleave', function () { st.hover = -1; dica.hidden = true; if (!anim) desenhar(); });
  cv.addEventListener('click', function (e) {
    var p = xy(e), k = maisPerto(p[0], p[1], 16);
    if (k >= 0) selecionar(k, true);
  });

  // ---------- ficha da cidade ----------
  var Z = (function () {
    var vars = [lrd, C.bf, C.ev, C.ur], out = [];
    vars.forEach(function (v) {
      var m = 0, s = 0, i;
      for (i = 0; i < N; i++) m += v[i]; m /= N;
      for (i = 0; i < N; i++) s += (v[i] - m) * (v[i] - m); s = Math.sqrt(s / N);
      out.push(Array.prototype.map.call(v, function (x) { return (x - m) / s; }));
    });
    return out;
  })();
  function parecidas(k, n) {
    var d = [];
    for (var i = 0; i < N; i++) {
      if (i === k) continue;
      var s = 0;
      for (var j = 0; j < Z.length; j++) { var t = Z[j][i] - Z[j][k]; s += t * t; }
      d.push([s, i]);
    }
    d.sort(function (a, b) { return a[0] - b[0]; });
    return d.slice(0, n).map(function (x) { return x[1]; });
  }
  function percentil(v, k) { var c = 0; for (var i = 0; i < N; i++) if (v[i] < v[k]) c++; return Math.round(100 * c / N); }
  function el(tag, cls, txt) { var e = document.createElement(tag); if (cls) e.className = cls; if (txt !== undefined) e.textContent = txt; return e; }
  function linhaF(rot, val, perc) {
    var d = el('div', 'linha'), a = el('span', '', rot), b = el('span', 'num', val);
    if (perc !== undefined) a.appendChild(el('span', 'perc', 'acima de ' + perc + '% das cidades'));
    d.appendChild(a); d.appendChild(b); return d;
  }
  function endereco(k) { return '#cidade/' + C.uf[k].toLowerCase() + '/' + C.slug[k]; }

  function ficha(k) {
    var f = document.getElementById('ficha-cidade');
    f.innerHTML = '';
    var fe = el('button', 'fechar', '✕'); fe.setAttribute('aria-label', 'Fechar a ficha da cidade');
    fe.addEventListener('click', function () { selecionar(-1, false); });
    f.appendChild(fe);
    f.appendChild(el('h2', '', C.nome[k]));
    var u = D.c.ufs[C.uf[k]];
    f.appendChild(el('p', 'sec', u.nome + ' · ' + u.regiao));
    f.appendChild(el('p', 'kicker', '1º turno 2026'));
    var pl = pct(C.l26[k], C.v26[k]), pf = pct(C.f26[k], C.v26[k]);
    var barra = el('div', 'barra-res'); barra.setAttribute('aria-hidden', 'true');
    var i1 = el('i', 'b-lula'), i2 = el('i', 'b-out'), i3 = el('i', 'b-pl');
    i1.style.width = pl + '%'; i3.style.width = pf + '%';
    barra.appendChild(i1); barra.appendChild(i2); barra.appendChild(i3); f.appendChild(barra);
    var r1 = el('div', 'res2'); r1.appendChild(el('span', 'c-lula grande', fmt(pl) + '%')); r1.appendChild(el('span', 'c-pl grande', fmt(pf) + '%')); f.appendChild(r1);
    var r2 = el('div', 'res2 sec'); r2.appendChild(el('span', '', 'Lula · ' + C.l26[k].toLocaleString('pt-BR'))); r2.appendChild(el('span', '', 'Flávio · ' + C.f26[k].toLocaleString('pt-BR'))); f.appendChild(r2);
    var b1 = el('div', 'bloco');
    b1.appendChild(el('p', 'kicker', 'Desde 2022'));
    b1.appendChild(el('p', '', '2022: Lula ' + fmt(pct(C.l22[k], C.v22[k])) + '% × Bolsonaro ' + fmt(pct(C.b22[k], C.v22[k])) + '%'));
    var dm = m26[k] - m22[k];
    b1.appendChild(el('p', '', 'A margem andou ' + fmt(Math.abs(dm)) + ' pontos para ' + (dm >= 0 ? 'o PL' : 'Lula') + '.'));
    f.appendChild(b1);
    var b2 = el('div', 'bloco');
    b2.appendChild(el('p', 'kicker', 'A cidade'));
    b2.appendChild(linhaF('Bolsa Família, set/2026', fmt(C.bf[k]) + '%', percentil(C.bf, k)));
    b2.appendChild(linhaF('Auxílio Brasil, set/2022', fmt(C.ab[k]) + '%'));
    b2.appendChild(linhaF('Renda média por pessoa', 'R$ ' + C.rd[k].toLocaleString('pt-BR'), percentil(C.rd, k)));
    b2.appendChild(linhaF('Evangélicos', fmt(C.ev[k]) + '%', percentil(C.ev, k)));
    b2.appendChild(linhaF('População urbana', fmt(C.ur[k]) + '%'));
    f.appendChild(b2);
    var b3 = el('div', 'bloco');
    b3.appendChild(el('p', 'kicker', 'Cidades parecidas'));
    b3.appendChild(el('p', 'sec pequeno', 'As mais próximas em renda, % no Bolsa Família, % de evangélicos e % urbana, em todo o país.'));
    var ul = el('ul', 'pareca');
    parecidas(k, 3).forEach(function (j) {
      var li = el('li'), bt = el('button', '', C.nome[j] + ' (' + C.uf[j] + ')');
      bt.addEventListener('click', function () { selecionar(j, true); });
      li.appendChild(bt); li.appendChild(el('span', 'num', margemTxt(m26[j], '26')));
      ul.appendChild(li);
    });
    b3.appendChild(ul); f.appendChild(b3);
    var rs = el('p', 'ressalva pequeno'); rs.appendChild(el('b', '', 'Uma cidade, não um eleitor. ')); rs.appendChild(document.createTextNode('Os números descrevem o município inteiro.'));
    f.appendChild(rs);
    var ac = el('div', 'acoes'), cp = el('button', '', 'Copiar link');
    var url = location.origin + location.pathname + endereco(k);
    cp.addEventListener('click', function () {
      if (navigator.clipboard) navigator.clipboard.writeText(url).then(function () { cp.textContent = 'Link copiado'; });
    });
    var wa = el('a', '', 'WhatsApp');
    wa.href = 'https://wa.me/?text=' + encodeURIComponent(C.nome[k] + ' (' + C.uf[k] + '): ' + url);
    wa.target = '_blank'; wa.rel = 'noopener';
    ac.appendChild(cp); ac.appendChild(wa); f.appendChild(ac);
  }

  function selecionar(k, mudarEnd) {
    st.sel = k;
    var fb = document.getElementById('ficha-brasil'), fc = document.getElementById('ficha-cidade');
    if (k < 0) {
      fb.hidden = false; fc.hidden = true;
      if (location.hash.indexOf('#cidade/') === 0) history.replaceState(null, '', location.pathname);
      document.title = 'Cidade não vota. Gente vota. · Eleições 2026';
    } else {
      ficha(k); fb.hidden = true; fc.hidden = false;
      if (mudarEnd) history.replaceState(null, '', endereco(k));
      document.title = C.nome[k] + ' (' + C.uf[k] + ') · Cidade não vota. Gente vota.';
    }
    if (!anim) desenhar();
  }
  function lerEndereco() {
    var h = decodeURIComponent(location.hash);
    if (h.indexOf('#cidade/') !== 0) return;
    var p = h.slice(8).split('/');
    for (var i = 0; i < N; i++) if (C.uf[i].toLowerCase() === p[0] && C.slug[i] === p[1]) { selecionar(i, false); return; }
  }

  // ---------- busca ----------
  var q = document.getElementById('q'), sug = document.getElementById('sugestoes'), res = [], ativo = -1;
  function buscar() {
    var t = semAcento(q.value.trim());
    res = [];
    if (t.length >= 2) {
      var ini = [], meio = [];
      for (var i = 0; i < N; i++) { var p = nomeN[i].indexOf(t); if (p === 0) ini.push(i); else if (p > 0) meio.push(i); }
      var porEl = function (a, b) { return C.el[b] - C.el[a]; };
      res = ini.sort(porEl).concat(meio.sort(porEl)).slice(0, 8);
    }
    sug.innerHTML = ''; ativo = -1;
    res.forEach(function (k, n) {
      var li = el('li'); li.id = 'sug-' + n; li.setAttribute('role', 'option'); li.setAttribute('aria-selected', 'false');
      li.appendChild(el('span', '', C.nome[k])); li.appendChild(el('span', 'uf', C.uf[k]));
      li.addEventListener('mousedown', function (e) { e.preventDefault(); escolher(k); });
      sug.appendChild(li);
    });
    if (t.length >= 2 && !res.length) { var v = el('li', 'sec', 'Nenhuma cidade encontrada'); sug.appendChild(v); }
    sug.hidden = !sug.children.length; q.setAttribute('aria-expanded', !sug.hidden);
  }
  function marcar(n) {
    ativo = n;
    Array.prototype.forEach.call(sug.children, function (li, j) { li.setAttribute('aria-selected', j === n); });
    if (n >= 0) q.setAttribute('aria-activedescendant', 'sug-' + n); else q.removeAttribute('aria-activedescendant');
  }
  function escolher(k) {
    q.value = ''; sug.hidden = true; q.setAttribute('aria-expanded', 'false');
    selecionar(k, true);
    if (W < 900) document.getElementById('ficha').scrollIntoView({ behavior: RM ? 'auto' : 'smooth', block: 'start' });
  }
  q.addEventListener('input', buscar);
  q.addEventListener('keydown', function (e) {
    if (e.key === 'ArrowDown') { e.preventDefault(); if (res.length) marcar((ativo + 1) % res.length); }
    else if (e.key === 'ArrowUp') { e.preventDefault(); if (res.length) marcar((ativo - 1 + res.length) % res.length); }
    else if (e.key === 'Enter') { e.preventDefault(); if (res.length) escolher(res[Math.max(ativo, 0)]); }
    else if (e.key === 'Escape') { sug.hidden = true; q.setAttribute('aria-expanded', 'false'); }
  });
  q.addEventListener('blur', function () { setTimeout(function () { sug.hidden = true; q.setAttribute('aria-expanded', 'false'); }, 150); });
  document.querySelectorAll('[data-foco-busca]').forEach(function (a) {
    a.addEventListener('click', function () { setTimeout(function () { q.focus({ preventScroll: true }); }, RM ? 0 : 450); });
  });

  // ---------- elementos estáticos: barras, tabela por UF, contrastes, exemplo ----------
  var num = function (s) { return parseFloat(String(s).replace(/[^\d,−-]/g, '').replace('−', '-').replace(',', '.')); };
  document.querySelectorAll('.barra-res[data-l]').forEach(function (b) {
    b.querySelector('.b-lula').style.width = num(b.getAttribute('data-l')) + '%';
    b.querySelector('.b-pl').style.width = num(b.getAttribute('data-f')) + '%';
  });
  document.querySelectorAll('.qb span').forEach(function (s) { s.style.width = num(s.getAttribute('data-v')) + '%'; });
  document.querySelectorAll('.tab-uf tr[data-uf]').forEach(function (tr) {
    var m = parseFloat(tr.getAttribute('data-m26')), m2 = parseFloat(tr.getAttribute('data-m22'));
    var i = tr.querySelector('.eixo i'), b = tr.querySelector('.eixo b');
    i.style.left = (50 + Math.min(m, 0)) + '%'; i.style.width = Math.abs(m) + '%';
    i.style.background = m < 0 ? 'var(--lula-pt)' : 'var(--pl-pt)';
    b.style.left = (50 + Math.max(-50, Math.min(50, m2))) + '%';
    tr.tabIndex = 0;
    var ir = function () {
      var uf = tr.getAttribute('data-uf').toUpperCase();
      st.uf = st.uf === uf ? null : uf;
      if (st.lente === 'ajuste' || st.lente === 'divisao') setLente('mapa'); else { textos(); atualizar(true); }
      document.getElementById('painel').scrollIntoView({ behavior: RM ? 'auto' : 'smooth' });
    };
    tr.addEventListener('click', ir);
    tr.addEventListener('keydown', function (e) { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); ir(); } });
  });
  (function contrastes() {
    var lin = document.querySelectorAll('.ct-l'), lo = 0, hi = 0;
    lin.forEach(function (l) { lo = Math.min(lo, parseFloat(l.getAttribute('data-li'))); hi = Math.max(hi, parseFloat(l.getAttribute('data-ls'))); });
    lo = Math.floor(lo / 10) * 10; hi = Math.max(0, Math.ceil(hi / 10) * 10) + 5;
    var x = function (v) { return (v - lo) / (hi - lo) * 100; };
    lin.forEach(function (l) {
      var li = parseFloat(l.getAttribute('data-li')), ls = parseFloat(l.getAttribute('data-ls')), e = parseFloat(l.getAttribute('data-est'));
      var ic = l.querySelector('.ct-ic'); ic.style.left = x(li) + '%'; ic.style.width = (x(ls) - x(li)) + '%';
      l.querySelector('.ct-pt').style.left = x(e) + '%';
      var z = document.createElement('i'); z.className = 'ct-zero'; z.style.left = x(0) + '%'; l.querySelector('.ct-g').appendChild(z);
    });
    var ei = document.querySelector('.ct-eixo');
    for (var v = 0; v >= lo; v -= 20) { var s = document.createElement('span'); s.style.left = x(v) + '%'; s.textContent = v === 0 ? '0' : '−' + Math.abs(v); ei.appendChild(s); }
  })();
  (function ilustra() {
    var box = document.querySelector('.ilustra'); if (!box) return;
    var rec = parseInt(box.getAttribute('data-recebe'), 10), lula = parseInt(box.getAttribute('data-lula'), 10), out = 100 - lula;
    var ns = 'http://www.w3.org/2000/svg';
    box.querySelectorAll('svg').forEach(function (svg) {
      var caso = svg.getAttribute('data-caso'), pessoas = [];
      if (caso === '1') { for (var i = 0; i < 100; i++) pessoas.push({ r: i < rec, l: i < lula }); }
      else { for (var j = 0; j < 100; j++) pessoas.push({ r: j < rec, l: j >= out }); }
      pessoas.forEach(function (p, n) {
        var q2 = document.createElementNS(ns, 'rect');
        q2.setAttribute('x', (n % 10) * 10 + 1.5); q2.setAttribute('y', Math.floor(n / 10) * 10 + 1.5);
        q2.setAttribute('width', 7); q2.setAttribute('height', 7); q2.setAttribute('rx', 1.2);
        q2.setAttribute('fill', p.l ? '#ec6d5d' : '#5b5d68');
        if (p.r) { q2.setAttribute('stroke', AMBAR); q2.setAttribute('stroke-width', 0.8); }
        svg.appendChild(q2);
      });
    });
  })();

  // ---------- início ----------
  function iniciar() { medir(); atualizar(false); }
  iniciar();
  textos();
  lerEndereco();
  window.addEventListener('hashchange', lerEndereco);
  var rt;
  window.addEventListener('resize', function () { clearTimeout(rt); rt = setTimeout(function () { var w = caixa.clientWidth; if (w !== W && w > 0) iniciar(); }, 120); });
  if (document.fonts && document.fonts.ready) document.fonts.ready.then(function () { if (!anim) desenhar(); });
})();
