from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey, DateTime, Text
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from sqlalchemy.sql import func

Base = declarative_base()

class Cliente(Base):
    __tablename__ = 'clientes'
    id = Column(Integer, primary_key=True)
    nome = Column(String, nullable=False)
    telefone = Column(String)
    endereco = Column(Text)
    cpf = Column(String, unique=True)

class Produto(Base):
    __tablename__ = 'produtos'
    id = Column(Integer, primary_key=True)
    nome = Column(String, nullable=False)
    categoria = Column(String, nullable=False)
    preco = Column(Float, nullable=False)
    imagem = Column(String)

class Pedido(Base):
    __tablename__ = 'pedidos'
    id = Column(Integer, primary_key=True)
    id_cliente = Column(Integer, ForeignKey('clientes.id'))
    cliente = relationship('Cliente', backref='pedidos')
    data_hora = Column(DateTime(timezone=True), server_default=func.now())
    valor_total = Column(Float, nullable=False, default=0.0)
    status = Column(String, default='Em preparo')
    tipo = Column(String, default='Delivery')

class ItemPedido(Base):
    __tablename__ = 'itens_pedido'
    id = Column(Integer, primary_key=True)
    id_pedido = Column(Integer, ForeignKey('pedidos.id'))
    id_produto = Column(Integer, ForeignKey('produtos.id'), nullable=True)
    nome_produto = Column(String)
    quantidade = Column(Integer, nullable=False)
    valor_unitario = Column(Float, nullable=False)
    valor_total = Column(Float, nullable=False)

_engine = None
_Session = None

def init_db(database_url):
    global _engine, _Session
    _engine = create_engine(database_url, echo=False, future=True)
    _Session = sessionmaker(bind=_engine, autoflush=False)
    Base.metadata.create_all(_engine)

def get_session():
    if _Session is None:
        raise RuntimeError("Call init_db() before get_session()")
    return _Session()
