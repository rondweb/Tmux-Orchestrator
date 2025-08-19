from sqlalchemy.orm import Session
from . import models, schemas

# Função para obter todas as anotações
def get_anotacoes(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Anotacao).offset(skip).limit(limit).all()

# Função para criar uma nova anotação
def create_anotacao(db: Session, anotacao: schemas.AnotacaoCreate):
    db_anotacao = models.Anotacao(
        titulo_livro=anotacao.titulo_livro,
        isbn=anotacao.isbn,
        localizacao=anotacao.localizacao,
        comentario=anotacao.comentario,
    )
    db.add(db_anotacao)
    db.commit()
    db.refresh(db_anotacao)
    return db_anotacao