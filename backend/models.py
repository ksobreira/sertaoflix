from sqlalchemy import Column, Integer, String, Date, DateTime, Numeric, ForeignKey, Enum
from database import Base

class Sessao(Base):
    __tablename__ = "sessao"

    id_Sessao = Column(Integer, primary_key=True, index=True)
    Duracao_da_sala = Column(Integer)
    Horario = Column(DateTime)
    Valor_Ingresso = Column(Integer)
    Desconto = Column(Integer)

class Filme(Base):
    __tablename__ = "filme"

    id_FIlme = Column(Integer, primary_key=True, autoincrement=True, index=True)
    Titulo = Column(String(150))
    Sinopse = Column(String)
    Duracao_min = Column(Integer, default=0)
    Data_lancamento = Column(Date) # Atualizado conforme seu ALTER TABLE
    Orcamento = Column(Numeric(15, 2), default=0.00)
    Bilheteria = Column(Numeric(15, 2), default=0.00)
    Poster_path = Column(String(255))
    Nota_media = Column(Numeric(3, 1), default=0.0)
    Total_votos = Column(Integer, default=0)
    Classificacao_indicativa = Column(String(10))
    sessao_id_Sessao = Column(Integer, ForeignKey("sessao.id_Sessao"), nullable=False)

class Cliente(Base):
    __tablename__ = "cliente"

    id_Cliente = Column(Integer, primary_key=True, autoincrement=True, index=True)
    Nome = Column(String(150))
    Nascimento = Column(Date)
    Nivel_fidelidade = Column(Enum('Bronze', 'Prata', 'Ouro'))
    Email = Column(String(100))
    Data_Virou_Prata = Column(DateTime)
    Total_ingresso = Column(Integer, default=0) # Atualizado conforme seu ALTER TABLE