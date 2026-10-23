"""
src/tratamento.py — Camada de Transformação (T) do pipeline ETL.

Projeto : BI Financeiro — Macroeconomia, Taxas de Juros & Indicadores Econômicos
Fonte   : API SGS/BACEN (séries 432, 433, 13522, 1, 24364)
Período : 01/01/2019 a 31/12/2023
"""
from __future__ import annotations

import argparse
import logging
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd

# ==============================================================================
# CAMINHOS RELATIVOS (Regra do professor: proibido caminhos absolutos)
# ==============================================================================
BASE_DIR: Path = Path(__file__).resolve().parent.parent
RAW_DIR: Path = BASE_DIR / "data" / "raw"
PROCESSED_DIR: Path = BASE_DIR / "data" / "processed"
LOG_DIR: Path = BASE_DIR / "docs" / "logs"

PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
LOG_DIR.mkdir(parents=True, exist_ok=True)

# ==============================================================================
# LOGGING
# ==============================================================================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-7s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("transform")


# ==============================================================================
# CONFIGURAÇÃO DAS SÉRIES BACEN (Ajustado para os nomes da sua pasta raw)
# ==============================================================================
@dataclass(frozen=True)
class SerieConfig:
    codigo: int
    nome_coluna: str
    descricao: str
    agregacao_mensal: Optional[str]
    arquivo_raw: str  # Nome exato do arquivo na pasta data/raw


SERIES: dict[int, SerieConfig] = {
    432:   SerieConfig(432,   "selic_meta",   "Selic Meta (% a.a.)", "last", "meta_selic_raw.csv"),
    433:   SerieConfig(433,   "ipca_mensal",  "IPCA mensal (%)",     None,   "ipca_mensal_raw.csv"),
    13522: SerieConfig(13522, "ipca_12m",     "IPCA 12 meses (%)",   None,   "ipca_12m_raw.csv"),
    1:     SerieConfig(1,     "dolar_ptax",   "Dólar PTAX (R$)",     "mean", "dolar_ptax_raw.csv"),
    24364: SerieConfig(24364, "ibc_br",       "IBC-Br",              None,   "ibc_br_raw.csv"),
}


def _localizar_raw(codigo: int) -> Path:
    """Localiza o CSV bruto exato baseado no config."""
    cfg = SERIES[codigo]
    caminho = RAW_DIR / cfg.arquivo_raw
    
    if caminho.exists():
        return caminho
        
    # Fallback de segurança caso o nome mude um pouco
    for padrao in [f"*{cfg.nome_coluna}*.csv", f"*{codigo}*.csv"]:
        encontrados = sorted(RAW_DIR.glob(padrao))
        if encontrados:
            return encontrados[0]
            
    return caminho


# ==============================================================================
# 1) INGESTÃO
# ==============================================================================
def carregar_bruto(caminho: Path) -> pd.DataFrame:
    """Lê o CSV bruto tentando múltiplos encodings (UTF-8 → UTF-8-sig → latin-1)."""
    if not caminho.exists():
        raise FileNotFoundError(
            f"Arquivo bruto ausente: {caminho}\n"
            f"→ Execute primeiro: python src/etl_bacen.py"
        )
    for enc in ("utf-8", "utf-8-sig", "latin-1"):
        try:
            df = pd.read_csv(caminho, encoding=enc)
            logger.info("Carregado %-32s (encoding=%s, %d linhas)",
                        caminho.name, enc, len(df))
            return df
        except UnicodeDecodeError:
            continue
    raise UnicodeDecodeError(f"Não foi possível decodificar: {caminho}")


# ==============================================================================
# 2) HIGIENIZAÇÃO
# ==============================================================================
def _normalizar_colunas(df: pd.DataFrame) -> pd.DataFrame:
    """Padroniza cabeçalhos ('Data'/'date' → 'data'; 'Valor'/'value' → 'valor')."""
    rename: dict[str, str] = {}
    for col in df.columns:
        low = str(col).strip().lower()
        if low in {"data", "date", "dt", "periodo"}:
            rename[col] = "data"
        elif low in {"valor", "value", "vlr"}:
            rename[col] = "valor"
    df = df.rename(columns=rename)
    if "data" not in df.columns or "valor" not in df.columns:
        raise ValueError(
            f"Colunas 'data' e 'valor' ausentes. Colunas recebidas: {list(df.columns)}"
        )
    return df[["data", "valor"]].copy()


def _converter_data(serie: pd.Series) -> pd.Series:
    """Converte para datetime tratando dd/mm/yyyy (padrão BACEN) e ISO."""
    return pd.to_datetime(serie, dayfirst=True, errors="coerce")


def _converter_valor(serie: pd.Series) -> pd.Series:
    """
    Converte strings da API SGS para float.
    Trata: vírgula decimal (pt-BR), ponto decimal (en-US), vazios, marcadores nulos.
    """
    s = serie.astype(str).str.strip()
    s = s.where(~s.isin(["", "null", "NULL", "NaN", "None", "-", "nan"]), np.nan)

    def _parse(v) -> float:
        if pd.isna(v):
            return np.nan
        v = str(v).strip()
        if not v:
            return np.nan
        if "," in v and "." in v:       # 1.234,56 → pt-BR
            v = v.replace(".", "").replace(",", ".")
        elif "," in v:                   # 0,32 → pt-BR decimal
            v = v.replace(",", ".")
        try:
            return float(v)
        except (ValueError, TypeError):
            return np.nan

    return s.map(_parse).astype("float64")


def higienizar(df: pd.DataFrame, codigo: int) -> tuple[pd.DataFrame, dict]:
    """Aplica pipeline de limpeza e retorna (df_limpo, relatório_qualidade)."""
    cfg = SERIES[codigo]
    n_bruto = len(df)

    df = _normalizar_colunas(df)
    df["data"]  = _converter_data(df["data"])
    df["valor"] = _converter_valor(df["valor"])

    datas_invalidas   = int(df["data"].isna().sum())
    valores_invalidos = int(df["valor"].isna().sum())

    df = df.dropna(subset=["data", "valor"]).copy()

    duplicatas = int(df.duplicated(subset=["data"]).sum())
    df = df.drop_duplicates(subset=["data"], keep="last")

    df = df.sort_values("data").reset_index(drop=True)

    relatorio = {
        "codigo":               codigo,
        "nome_coluna":          cfg.nome_coluna,
        "linhas_brutas":        n_bruto,
        "datas_invalidas":      datas_invalidas,
        "valores_invalidos":    valores_invalidos,
        "duplicatas_removidas": duplicatas,
        "linhas_finais":        len(df),
        "data_min":             df["data"].min().strftime("%Y-%m-%d") if len(df) else None,
        "data_max":             df["data"].max().strftime("%Y-%m-%d") if len(df) else None,
    }
    logger.info(
        "Higienizado [%-12s]: %d→%d linhas | inválidos(datas=%d, valores=%d) | dup=%d",
        cfg.nome_coluna, n_bruto, len(df),
        datas_invalidas, valores_invalidos, duplicatas,
    )
    return df, relatorio


# ==============================================================================
# 3) PADRONIZAÇÃO MENSAL
# ==============================================================================
def resample_mensal(df: pd.DataFrame, codigo: int) -> pd.DataFrame:
    """
    Normaliza a série para base mensal ('MS' = 1º dia do mês).
      - Séries diárias (432, 1):  agregadas por 'last' / 'mean'
      - Séries mensais (433, 13522, 24364): apenas normaliza a data
    """
    cfg = SERIES[codigo]
    if cfg.agregacao_mensal is None:
        out = df.copy()
        # CORREÇÃO APLICADA AQUI: removido o "MS" de to_timestamp
        out["data"] = out["data"].dt.to_period("M").dt.to_timestamp()
    else:
        out = (
            df.set_index("data")
              .resample("MS")
              .agg({"valor": cfg.agregacao_mensal})
              .reset_index()
        )
    return out.rename(columns={"valor": cfg.nome_coluna})


# ==============================================================================
# 4) MODELAGEM (consolidação + Juro Real Ex-Post)
# ==============================================================================
def consolidar(dfs_mensais: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """Merge externo das séries mensais em um único DataFrame."""
    base = next(iter(dfs_mensais.values()))
    for df in list(dfs_mensais.values())[1:]:
        base = base.merge(df, on="data", how="outer")

    base = base.sort_values("data").reset_index(drop=True)
    base["ano"]       = base["data"].dt.year.astype("Int64")
    base["mes"]       = base["data"].dt.month.astype("Int64")
    base["trimestre"] = base["data"].dt.quarter.astype("Int64")
    return base


def calcular_juro_real(df: pd.DataFrame) -> pd.DataFrame:
    """
    Juro Real Ex-Post via Fórmula de Fisher:
        (1 + i_nominal/100) / (1 + i_inflacao/100) - 1  →  × 100 (% a.a.)
    """
    df = df.copy()
    selic   = df["selic_meta"] / 100.0
    ipca12  = df["ipca_12m"]   / 100.0
    df["juro_real"] = ((1 + selic) / (1 + ipca12) - 1) * 100
    return df


# ==============================================================================
# 5) VALIDAÇÃO
# ==============================================================================
def validar_cobertura(df: pd.DataFrame, fail_on_null: bool = False) -> dict:
    esperado = pd.date_range("2019-01-01", "2023-12-01", freq="MS")
    faltantes = sorted(set(esperado) - set(df["data"]))
    colunas_kpi = ["selic_meta", "ipca_12m", "dolar_ptax", "juro_real"]
    nulos = {c: int(df[c].isna().sum()) for c in colunas_kpi}

    relatorio = {
        "meses_esperados":        len(esperado),
        "meses_presentes":        int(len(df)),
        "meses_faltantes":        [d.strftime("%Y-%m") for d in faltantes],
        "nulos_por_coluna_kpi":   nulos,
    }
    if faltantes:
        logger.warning("Cobertura incompleta: %d mês(es) ausente(s).", len(faltantes))
    if any(v > 0 for v in nulos.values()):
        msg = f"Nulos remanescentes em KPIs: {nulos}"
        if fail_on_null:
            raise ValueError(msg)
        logger.warning(msg)
    return relatorio


# ==============================================================================
# 6) PERSISTÊNCIA
# ==============================================================================
def salvar_processado(df: pd.DataFrame) -> Path:
    destino = PROCESSED_DIR / "macro_consolidado.csv"
    df.to_csv(destino, index=False, encoding="utf-8", date_format="%Y-%m-%d")
    logger.info("Salvo processado: %s (%d linhas × %d colunas)", destino, *df.shape)
    return destino


def salvar_relatorio(relatorios_series: list[dict],
                     relatorio_cobertura: dict) -> Path:
    destino = LOG_DIR / "transform_report.md"
    linhas = [
        "# Relatório de Transformação (ETL)",
        f"\n_Execução: {datetime.now():%Y-%m-%d %H:%M:%S}_\n",
        "## 1. Higienização por série\n",
        "| Série | Coluna | Bruto | Finais | Datas inv. | Valores inv. | Duplicatas | Janela |",
        "|---|---|---:|---:|---:|---:|---:|---|",
    ]
    for r in relatorios_series:
        linhas.append(
            f"| {r['codigo']} | `{r['nome_coluna']}` | {r['linhas_brutas']} "
            f"| {r['linhas_finais']} | {r['datas_invalidas']} | {r['valores_invalidos']} "
            f"| {r['duplicatas_removidas']} | {r['data_min']} → {r['data_max']} |"
        )
    linhas += [
        "\n## 2. Cobertura temporal",
        f"- Meses esperados (2019-01 a 2023-12): **{relatorio_cobertura['meses_esperados']}**",
        f"- Meses presentes: **{relatorio_cobertura['meses_presentes']}**",
        f"- Meses faltantes: `{relatorio_cobertura['meses_faltantes'] or 'nenhum'}`",
        "\n## 3. Nulos remanescentes (colunas KPI)",
    ]
    for col, n in relatorio_cobertura["nulos_por_coluna_kpi"].items():
        linhas.append(f"- `{col}`: {n}")
    destino.write_text("\n".join(linhas), encoding="utf-8")
    logger.info("Relatório salvo: %s", destino)
    return destino


# ==============================================================================
# ORQUESTRADOR
# ==============================================================================
def run(fail_on_null: bool = False) -> pd.DataFrame:
    logger.info("=" * 70)
    logger.info("INÍCIO — Transformação ETL (BACEN SGS)")
    logger.info("Raiz do projeto: %s", BASE_DIR)
    logger.info("=" * 70)

    relatorios_series: list[dict] = []
    dfs_mensais: dict[str, pd.DataFrame] = {}

    for codigo in SERIES:
        caminho   = _localizar_raw(codigo)
        df_bruto  = carregar_bruto(caminho)
        df_limpo, rel = higienizar(df_bruto, codigo)
        relatorios_series.append(rel)
        dfs_mensais[SERIES[codigo].nome_coluna] = resample_mensal(df_limpo, codigo)

    logger.info("-" * 70)
    logger.info("Consolidando %d séries mensais...", len(dfs_mensais))
    df_consolidado = consolidar(dfs_mensais)

    logger.info("Calculando Juro Real Ex-Post (Fórmula de Fisher)...")
    df_consolidado = calcular_juro_real(df_consolidado)

    relatorio_cobertura = validar_cobertura(df_consolidado, fail_on_null=fail_on_null)

    salvar_processado(df_consolidado)
    salvar_relatorio(relatorios_series, relatorio_cobertura)

    logger.info("=" * 70)
    logger.info("FIM — %d linhas × %d colunas.", *df_consolidado.shape)
    logger.info("=" * 70)
    return df_consolidado


def _parse_args(argv: list[str]) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="ETL — Transformação de séries BACEN.")
    p.add_argument("--fail-on-null", action="store_true",
                   help="Aborta se houver nulos remanescentes em colunas KPI (modo CI).")
    return p.parse_args(argv)


if __name__ == "__main__":
    args = _parse_args(sys.argv[1:])
    try:
        run(fail_on_null=args.fail_on_null)
    except Exception as exc:
        logger.exception("Falha na transformação: %s", exc)
        sys.exit(1)