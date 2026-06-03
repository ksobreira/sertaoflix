from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text  # Importante para ler as Views textuais do MySQL
from typing import List

import models
import schema
from database import get_db, engine

# Cria as tabelas caso elas não existam
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="SertaoFlix API")

# Configuração do CORS para permitir que o Vite acesse a API
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Bem-vindo à API SertaoFlix!"}


# --- 🎬 ENDPOINT DO CATÁLOGO (HOME) ---

@app.get("/filmes")
def listar_filmes(db: Session = Depends(get_db)):
    # Faz o JOIN automático das tabelas Filme e Sessao para trazer o Horário
    resultados = db.query(models.Filme, models.Sessao.Horario)\
                   .join(models.Sessao, models.Filme.sessao_id_Sessao == models.Sessao.id_Sessao)\
                   .all()
    
    lista_filmes = []
    for filme, horario in resultados:
        filme_dict = filme.__dict__.copy()
        filme_dict.pop('_sa_instance_state', None)  # Remove metadados internos do SQLAlchemy
        filme_dict["Horario"] = horario             # Injeta o horário esperado pelo Home.jsx
        lista_filmes.append(filme_dict)
        
    return lista_filmes


# --- 📊 ENDPOINTS DO DASHBOARD (VIEWS DO BANCO) ---

# 1. KPIs Gerais do Painel
@app.get("/api/stats")
def get_stats(db: Session = Depends(get_db)):
    total_cinemas = db.execute(text("SELECT COUNT(*) FROM cinema")).scalar() or 0
    total_filmes = db.execute(text("SELECT COUNT(*) FROM filme")).scalar() or 0
    total_clientes = db.execute(text("SELECT COUNT(*) FROM cliente")).scalar() or 0
    total_ingressos = db.execute(text("SELECT COUNT(*) FROM ingresso")).scalar() or 0
    receita_total = db.execute(text("SELECT SUM(Valor) FROM ingresso")).scalar() or 0
    
    return {
        "total_cinemas": total_cinemas,
        "total_filmes": total_filmes,
        "total_clientes": total_clientes,
        "total_ingressos": total_ingressos,
        "receita_total": float(receita_total)
    }

# 2. Faturamento por Unidade (View 6.3)
@app.get("/api/faturamento")
def get_faturamento(db: Session = Depends(get_db)):
    result = db.execute(text("SELECT Cinema, Total_Ingressos, Receita_Total FROM vw_faturamento_cinema"))
    return [dict(row._mapping) for row in result]

# 3. Ranking de Filmes por Nota (View 6.4)
@app.get("/api/ranking")
def get_ranking(db: Session = Depends(get_db)):
    result = db.execute(text("SELECT Titulo, Total_Avaliacoes, Nota_Media FROM vw_ranking_filmes"))
    return [dict(row._mapping) for row in result]

# 4. Distribuição do Programa de Fidelidade (Agrupado usando a View de Segurança 6.1)
@app.get("/api/fidelidade")
def get_fidelidade(db: Session = Depends(get_db)):
    query = """
        SELECT Nivel_fidelidade, COUNT(*) as Total 
        FROM vw_clientes_seguro 
        GROUP BY Nivel_fidelidade
    """
    result = db.execute(text(query))
    return [dict(row._mapping) for row in result]

# 5. Percentual de Ocupação das Salas (View 6.5)
@app.get("/api/ocupacao")
def get_ocupacao(db: Session = Depends(get_db)):
    query = """
        SELECT Cinema, Numero_Sala, Tipo, Capacidade, Vendidos, Ocupacao_pct 
        FROM vw_ocupacao_salas
    """
    result = db.execute(text(query))
    return [dict(row._mapping) for row in result]