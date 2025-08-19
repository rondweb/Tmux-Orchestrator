from pydantic import BaseModel
from typing import Optional

# Esquema base para a anotação
class AnotacaoBase(BaseModel):
    titulo_livro: str
    isbn: Optional[str] = None
    localizacao: str
    comentario: str

# Esquema para criar uma nova anotação (herda do base)
class AnotacaoCreate(AnotacaoBase):
    pass

# Esquema para ler uma anotação (inclui o ID e permite o modo ORM)
class Anotacao(AnotacaoBase):
    id: int

    class Config:
        orm_mode = True