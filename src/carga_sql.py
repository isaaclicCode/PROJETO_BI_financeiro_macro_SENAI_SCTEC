import pandas as pd
from sqlalchemy import create_engine
from pathlib import Path

# Caminhos
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data" / "processed"

# --- SECURITY ---
DB_USER = "postgres"
DB_PASS = "WaixEER97298F6pB" 
DB_HOST = "db.ctwazoujrfkcilucnper.supabase.co"
DB_PORT = "5432"
DB_NAME = "postgres"

def carregar_para_supabase():
    print("Conectando ao banco de dados Supabase...")
    
    # String de conexão (com +psycopg2 para garantir a compatibilidade)
    conn_string = f"postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    
    try:
        engine = create_engine(conn_string)
        
        print("Lendo base consolidada local...")
        # 1. CARREGA O DATAFRAME
        df = pd.read_csv(DATA_DIR / "macro_consolidado.csv")
        
        # 2. CORREÇÃO DA DATA (Converte de string para objeto de data real)
        df['data'] = pd.to_datetime(df['data']).dt.date
        
        print("Enviando dados para a nuvem (Tabela: macro_consolidado)...")
        # 3. ENVIA PARA O BANCO (O 'replace' recria a tabela com a data corrigida)
        df.to_sql('macro_consolidado', engine, if_exists='replace', index=False)
        
        print("✅ Tabela 'macro_consolidado' criada com sucesso no Supabase!")
        
    except Exception as e:
        print(f"❌ Erro na conexão: {e}")

if __name__ == "__main__":
    carregar_para_supabase()