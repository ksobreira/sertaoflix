from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List

import models
import schema
from database import get_db, engine

# Cria as tabelas caso elas não existam (Geralmente controlado por migrações, mas útil para o início)
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="SertaoFlix API")

# Configuração do CORS para permitir que o Vite (geralmente na porta 5173) acesse a API
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

# Rota para listar todos os filmes (O React chamará esse endpoint)
@app.get("/filmes", response_model=List[schema.FilmeResponse])
def listar_filmes(db: Session = Depends(get_db)):
    filmes = db.query(models.Filme).all()
    return filmes

# Rota para buscar um filme específico por ID
@app.get("/filmes")
def listar_filmes(db: Session = Depends(get_db)):
    # Faz o JOIN automático das tabelas Filme e Sessao
    resultados = db.query(models.Filme, models.Sessao.Horario)\
                   .join(models.Sessao, models.Filme.sessao_id_Sessao == models.Sessao.id_Sessao)\
                   .all()
    
    lista_filmes = []
    for filme, horario in resultados:
        filme_dict = filme.__dict__
        filme_dict["Horario"] = horario # Injeta o horário no objeto do filme para o React lers
        lista_filmes.append(filme_dict)
        
    return lista_filmes