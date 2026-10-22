import requests
import pandas as pd
import os
import time
from pathlib import Path

# 1. Definição dos caminhos seguros (Pathlib)
# __file__ é o caminho do script atual (src/etl.py). 
# .parent.parent sobe duas pastas: de src/ para a raiz do projeto.
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_RAW_DIR = BASE_DIR / "data" / "raw"
DATA_PROCESSED_DIR = BASE_DIR / "data" / "processed"

# Garante que as pastas existam
DATA_RAW_DIR.mkdir(parents=True, exist_ok=True)
DATA_PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

# 2. Séries obrigatórias do BACEN
SERIES = {
    432: "meta_selic",
    433: "ipca_mensal",
    13522: "ipca_12m",
    1: "dolar_ptax",
    24364: "ibc_br"
}

DATA_INICIAL = "01/01/2019"
DATA_FINAL = "31/12/2023"

def extrair_dados_bacen():
    for codigo, nome in SERIES.items():
        print(f"Baixando série {codigo} ({nome})...")
        url = f"https://api.bcb.gov.br/dados/serie/bcdata.sgs.{codigo}/dados?formato=json&dataInicial={DATA_INICIAL}&dataFinal={DATA_FINAL}"
        
        # 3. Lógica de Retry (tentar novamente)
        max_tentativas = 5
        sucesso = False
        
        for tentativa in range(max_tentativas):
            try:
                # Adicionado timeout para não travar caso o BACEN demore a responder
                response = requests.get(url, timeout=30)
                response.raise_for_status() # Verifica se deu erro HTTP (ex: 502, 404)
                sucesso = True
                break # Se deu certo, sai do loop de tentativas
            except requests.exceptions.RequestException as e:
                print(f"  -> Erro na tentativa {tentativa + 1}: {e}")
                if tentativa < max_tentativas - 1:
                    print("  -> Aguardando 5 segundos para tentar novamente...")
                    time.sleep(5)
                else:
                    print(f"  -> ❌ Falha definitiva ao baixar {nome} após {max_tentativas} tentativas.")
        
        # Se falhou todas as tentativas, pula para a próxima série
        if not sucesso:
            continue

        # 4. Tratamento dos dados
        df = pd.DataFrame(response.json())
        
        # Salva o dado bruto (como veio da API)
        caminho_raw = DATA_RAW_DIR / f"{nome}_raw.csv"
        df.to_csv(caminho_raw, index=False)
        
        # Limpeza: Converte data e substitui vírgcula por ponto nos valores
        df['data'] = pd.to_datetime(df['data'], format='%d/%m/%Y')
        df['valor'] = df['valor'].str.replace(',', '.').astype(float)
        
        # Remove duplicatas e ordena por data
        df = df.drop_duplicates(subset=['data']).sort_values('data')
        
        # Salva o dado tratado
        caminho_processed = DATA_PROCESSED_DIR / f"{nome}_processed.csv"
        df.to_csv(caminho_processed, index=False)
        
        print(f"  -> ✅ {nome} salvo com sucesso! ({len(df)} registros)")
        
        # Pausa de 1 segundo entre as requisições (boa prática para não sobrecarregar a API)
        time.sleep(1)

if __name__ == "__main__":
    print("Iniciando Extração de Dados do BACEN...")
    extrair_dados_bacen()
    print("\nETL concluído!")