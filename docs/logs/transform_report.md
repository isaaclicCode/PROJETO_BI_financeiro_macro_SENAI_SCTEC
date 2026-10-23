# Relatório de Transformação (ETL)

_Execução: 2026-10-23 17:55:49_

## 1. Higienização por série

| Série | Coluna | Bruto | Finais | Datas inv. | Valores inv. | Duplicatas | Janela |
|---|---|---:|---:|---:|---:|---:|---|
| 432 | `selic_meta` | 1826 | 1826 | 0 | 0 | 0 | 2019-01-01 → 2023-12-31 |
| 433 | `ipca_mensal` | 60 | 60 | 0 | 0 | 0 | 2019-01-01 → 2023-12-01 |
| 13522 | `ipca_12m` | 60 | 60 | 0 | 0 | 0 | 2019-01-01 → 2023-12-01 |
| 1 | `dolar_ptax` | 1255 | 1255 | 0 | 0 | 0 | 2019-01-02 → 2023-12-29 |
| 24364 | `ibc_br` | 60 | 60 | 0 | 0 | 0 | 2019-01-01 → 2023-12-01 |

## 2. Cobertura temporal
- Meses esperados (2019-01 a 2023-12): **60**
- Meses presentes: **60**
- Meses faltantes: `nenhum`

## 3. Nulos remanescentes (colunas KPI)
- `selic_meta`: 0
- `ipca_12m`: 0
- `dolar_ptax`: 0
- `juro_real`: 0