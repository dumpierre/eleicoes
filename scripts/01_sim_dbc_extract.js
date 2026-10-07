// 01_sim_dbc_extract.js
// Lê DOBRyyyy.dbc (SIM/DATASUS), descomprime (PKWare DCL implode; port de blast.c, Mark Adler,
// mesmo algoritmo usado pelo pacote R read.dbc), interpreta o DBF e grava um CSV enxuto
// com os óbitos em que COVID-19 aparece como causa básica ou em qualquer linha do atestado.
// Uso: node 01_sim_dbc_extract.js <entrada.dbc> <saida.csv> <resumo.json>
'use strict';
const fs = require('fs');

// ---------- blast (DCL implode) ----------
const MAXBITS = 13;
const LITLEN = [11, 124, 8, 7, 28, 7, 188, 13, 76, 4, 10, 8, 12, 10, 12, 10, 8, 23, 8,
  9, 7, 6, 7, 8, 7, 6, 55, 8, 23, 24, 12, 11, 7, 9, 11, 12, 6, 7, 22, 5,
  7, 24, 6, 11, 9, 6, 7, 22, 7, 11, 38, 7, 9, 8, 25, 11, 8, 11, 9, 12,
  8, 12, 5, 38, 5, 38, 5, 11, 7, 5, 6, 21, 6, 10, 53, 8, 7, 24, 10, 27,
  44, 253, 253, 253, 252, 252, 252, 13, 12, 45, 12, 45, 12, 61, 12, 45,
  44, 173];
const LENLEN = [2, 35, 36, 53, 38, 23];
const DISTLEN = [2, 20, 53, 230, 247, 151, 248];
const BASE = [3, 2, 4, 5, 6, 7, 8, 9, 10, 12, 16, 24, 40, 72, 136, 264];
const EXTRA = [0, 0, 0, 0, 0, 0, 0, 0, 1, 2, 3, 4, 5, 6, 7, 8];

function construct(rep, n) {
  const length = [];
  for (const b of rep) {
    const len = b & 15;
    let r = (b >> 4) + 1;
    while (r--) length.push(len);
  }
  if (length.length !== n) throw new Error(`tabela com ${length.length} símbolos, esperado ${n}`);
  const count = new Array(MAXBITS + 1).fill(0);
  for (const l of length) count[l]++;
  const offs = new Array(MAXBITS + 1).fill(0);
  for (let len = 1; len < MAXBITS; len++) offs[len + 1] = offs[len] + count[len];
  const symbol = new Array(n);
  for (let s = 0; s < n; s++) if (length[s] !== 0) symbol[offs[length[s]]++] = s;
  return { count, symbol };
}
const LITCODE = construct(LITLEN, 256);
const LENCODE = construct(LENLEN, 16);
const DISTCODE = construct(DISTLEN, 64);

function blast(input, start, sizeHint) {
  let pos = start, bitbuf = 0, bitcnt = 0;
  let out = Buffer.allocUnsafe(sizeHint), op = 0;
  function bits(need) {
    while (bitcnt < need) {
      if (pos >= input.length) throw new Error('fim inesperado da entrada');
      bitbuf |= input[pos++] << bitcnt;
      bitcnt += 8;
    }
    const v = bitbuf & ((1 << need) - 1);
    bitbuf >>>= need;
    bitcnt -= need;
    return v;
  }
  function decode(h) {
    let code = 0, first = 0, index = 0;
    for (let len = 1; len <= MAXBITS; len++) {
      code |= bits(1) ^ 1; // códigos invertidos
      const count = h.count[len];
      if (code < first + count) return h.symbol[index + (code - first)];
      index += count; first += count; first <<= 1; code <<= 1;
    }
    throw new Error('código Huffman inválido');
  }
  function ensure(extra) {
    if (op + extra > out.length) {
      const nb = Buffer.allocUnsafe(Math.max(out.length * 2, op + extra));
      out.copy(nb, 0, 0, op);
      out = nb;
    }
  }
  const lit = bits(8);
  if (lit > 1) throw new Error('flag de literal inválida');
  const dict = bits(8);
  if (dict < 4 || dict > 6) throw new Error('tamanho de dicionário inválido');
  for (;;) {
    if (bits(1)) {
      let symbol = decode(LENCODE);
      const len = BASE[symbol] + bits(EXTRA[symbol]);
      if (len === 519) break; // código de fim
      symbol = len === 2 ? 2 : dict;
      let dist = decode(DISTCODE) << symbol;
      dist += bits(symbol);
      dist++;
      if (dist > op) throw new Error('distância além do início da saída');
      ensure(len);
      for (let i = 0; i < len; i++, op++) out[op] = out[op - dist];
    } else {
      const symbol = lit ? decode(LITCODE) : bits(8);
      ensure(1);
      out[op++] = symbol;
    }
  }
  return out.subarray(0, op);
}

// ---------- DBC -> DBF ----------
function dbcToDbf(buf) {
  const hsize = buf.readUInt16LE(8);
  const header = buf.subarray(0, hsize);
  const nrec = header.readUInt32LE(4);
  const reclen = header.readUInt16LE(10);
  const body = blast(buf, hsize + 4, nrec * reclen + 1024);
  return { header, body, nrec, reclen, hsize };
}

function parseFields(header) {
  const fields = [];
  let off = 1;
  for (let p = 32; p < header.length && header[p] !== 0x0d; p += 32) {
    const name = header.toString('latin1', p, p + 11).replace(/\0.*$/, '').trim();
    const len = header[p + 16];
    fields.push({ name, type: String.fromCharCode(header[p + 11]), off, len });
    off += len;
  }
  return fields;
}

// ---------- principal ----------
const [, , inPath, outCsv, outJson] = process.argv;
if (!inPath || !outCsv || !outJson) { console.error('uso: node 01_sim_dbc_extract.js in.dbc out.csv resumo.json'); process.exit(2); }
const raw = fs.readFileSync(inPath);
const t0 = Date.now();
const { header, body, nrec, reclen } = dbcToDbf(raw);
const fields = parseFields(header);
const sumLen = fields.reduce((a, f) => a + f.len, 0) + 1;
const resumo = {
  arquivo: inPath, registros_header: nrec, tamanho_registro: reclen, soma_campos: sumLen,
  bytes_descomprimidos: body.length, bytes_esperados: nrec * reclen,
  segundos_descompressao: (Date.now() - t0) / 1000, campos: fields.map(f => f.name),
};
if (sumLen !== reclen) throw new Error('soma dos campos difere do tamanho do registro');
if (body.length < nrec * reclen) throw new Error('corpo descomprimido menor que o esperado');

const keep = ['DTOBITO', 'CODMUNRES', 'CODMUNOCOR', 'IDADE', 'SEXO', 'CAUSABAS', 'LINHAA', 'LINHAB', 'LINHAC', 'LINHAD', 'LINHAII', 'ATESTADO'];
const fmap = Object.fromEntries(fields.map(f => [f.name, f]));
const miss = keep.filter(k => !fmap[k]);
resumo.campos_ausentes = miss;
const kf = keep.filter(k => fmap[k]).map(k => fmap[k]);
const covidRe = /(B342|U071|U072|U109)/;
const lines = [kf.map(f => f.name).join(',') + ',COVID_BASICA,COVID_QUALQUER'];
let nDel = 0, nBasica = 0, nQualquer = 0, nTotal = 0;
const cbCount = {};
for (let r = 0; r < nrec; r++) {
  const base = r * reclen;
  if (body[base] === 0x2a) { nDel++; continue; } // registro apagado
  nTotal++;
  const get = f => body.toString('latin1', base + f.off, base + f.off + f.len).trim();
  const causabas = get(fmap.CAUSABAS);
  const linhas = ['LINHAA', 'LINHAB', 'LINHAC', 'LINHAD', 'LINHAII', 'ATESTADO'].filter(k => fmap[k]).map(k => get(fmap[k])).join(' ').replace(/[\s.*]/g, '');
  const basica = covidRe.test(causabas);
  const qualquer = basica || covidRe.test(linhas);
  if (basica) { nBasica++; cbCount[causabas] = (cbCount[causabas] || 0) + 1; }
  if (qualquer) {
    nQualquer++;
    lines.push(kf.map(f => '"' + get(f).replace(/"/g, '""') + '"').join(',') + `,${basica ? 1 : 0},${qualquer ? 1 : 0}`);
  }
}
fs.writeFileSync(outCsv, lines.join('\n') + '\n', 'utf8');
Object.assign(resumo, { registros_apagados: nDel, obitos_total: nTotal, covid_causa_basica: nBasica, covid_qualquer_linha: nQualquer, causabas_covid_por_codigo: cbCount });
fs.writeFileSync(outJson, JSON.stringify(resumo, null, 2), 'utf8');
console.log(JSON.stringify(resumo, null, 2));
