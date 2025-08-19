from fastapi import FastAPI, Request, Depends, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from . import crud, models, schemas
from .database import SessionLocal, engine

# Cria as tabelas no banco de dados (se não existirem)
models.Base.metadata.create_all(bind=engine)

# Instancia o aplicativo FastAPI
app = FastAPI()

# Monta o diretório 'static' para servir arquivos estáticos (CSS, JS)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Configura o diretório de templates para o Jinja2
templates = Jinja2Templates(directory="templates")

# Dependência para obter a sessão do banco de dados
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/", response_class=HTMLResponse)
def read_root(request: Request, db: Session = Depends(get_db)):
    """
    Renderiza a página principal com a lista de anotações existentes.
    """
    anotacoes = crud.get_anotacoes(db)
    return templates.TemplateResponse("index.html", {"request": request, "anotacoes": anotacoes})


@app.post("/anotacoes/", response_class=RedirectResponse)
def create_anotacao_from_form(
    titulo_livro: str = Form(...),
    isbn: str = Form(None),
    localizacao: str = Form(...),
    comentario: str = Form(...),
    db: Session = Depends(get_db)
):
    """
    Recebe os dados do formulário HTML e cria uma nova anotação.
    Após a criação, redireciona o usuário para a página principal.
    """
    nova_anotacao = schemas.AnotacaoCreate(
        titulo_livro=titulo_livro,
        isbn=isbn,
        localizacao=localizacao,
        comentario=comentario
    )
    crud.create_anotacao(db=db, anotacao=nova_anotacao)
    # Redireciona para a página inicial para ver a nova anotação
    return RedirectResponse(url="/", status_code=303)