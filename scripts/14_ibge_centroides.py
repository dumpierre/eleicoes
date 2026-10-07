"""Centroides municipais (IBGE, API de malhas v3) para o mapa de pontos do video-resposta.

Uso (da raiz do projeto): python -P scripts/14_ibge_centroides.py .
Entrada: servicodados.ibge.gov.br/api/v3/malhas/paises/BR/metadados?intrarregiao=municipio
Saidas: data/raw/ibge/malhas_metadados_municipios.json (+ .sha256)
        data/derived/ibge_centroides_municipios.csv
        logs/14_ibge_centroides_log.json
Nunca sobrescreve: se a saida bruta ja existe, usa o arquivo local.
"""
import gzip, hashlib, json, sys, urllib.request
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

root = Path(sys.argv[1] if len(sys.argv) > 1 else ".")
URL = "https://servicodados.ibge.gov.br/api/v3/malhas/paises/BR/metadados?intrarregiao=municipio"
raw = root / "data/raw/ibge/malhas_metadados_municipios.json"
out = root / "data/derived/ibge_centroides_municipios.csv"
log_path = root / "logs/14_ibge_centroides_log.json"

if raw.exists():
    data = raw.read_bytes()
    baixado = False
else:
    with urllib.request.urlopen(URL, timeout=120) as r:
        data = r.read()
    if data[:2] == bytes([0x1F, 0x8B]):  # a API responde em gzip
        data = gzip.decompress(data)
    raw.write_bytes(data)
    baixado = True
sha = hashlib.sha256(data).hexdigest()
sha_path = raw.with_suffix(".json.sha256")
if not sha_path.exists():
    sha_path.write_text(f"{sha}  {raw.name}\n")

meta = json.loads(data)
cent = pd.DataFrame(
    {
        "cd_ibge7": int(m["id"]),
        "lon": m["centroide"]["longitude"],
        "lat": m["centroide"]["latitude"],
        "area_km2": float(m["area"]["dimensao"]),
    }
    for m in meta
)

base = pd.read_csv(root / "data/derived/base_analitica_emendas.csv", usecols=["cd_ibge7", "nome_tse", "uf"])
faltam = base.loc[~base.cd_ibge7.isin(cent.cd_ibge7), ["cd_ibge7", "nome_tse", "uf"]]
sobram = cent.loc[~cent.cd_ibge7.isin(base.cd_ibge7), "cd_ibge7"]

if out.exists():
    sys.exit(f"{out} ja existe; nao sobrescrevo.")
cent.sort_values("cd_ibge7").to_csv(out, index=False)

log = {
    "executado_em": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    "url": URL,
    "baixado_agora": baixado,
    "sha256": sha,
    "n_centroides": len(cent),
    "n_base": len(base),
    "base_sem_centroide": faltam.to_dict("records"),
    "centroide_fora_da_base": sobram.tolist(),
    "lon_min_max": [cent.lon.min(), cent.lon.max()],
    "lat_min_max": [cent.lat.min(), cent.lat.max()],
}
log_path.write_text(json.dumps(log, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps(log, ensure_ascii=False, indent=2))
