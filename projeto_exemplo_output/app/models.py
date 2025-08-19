from sqlalchemy import Column, Integer, String, Text
from .database import Base

class Anotacao(Base):
    __tablename__ = "anotacoes"

    id = Column(Integer, primary_key=True, index=True)
    titulo_livro = Column(String, index=True)
    isbn = Column(String, nullable=True)
    localizacao = Column(String)  # Ex: "Capítulo 5" ou "Página 42"
    comentario = Column(Text, nullable=False)