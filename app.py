#!/usr/bin/env python3
import os
from flask import Flask, render_template, request, redirect, url_for, jsonify
from db_utils import init_db, get_session, Cliente, Produto, Pedido, ItemPedido
from sqlalchemy.exc import IntegrityError

app = Flask(__name__)

DATABASE_URL = os.environ.get(
    Server [localhost]: dpg-d43e2ommcj7s73b062jg-a.oregon-postgres.render.com
Database [postgres]: halldb
Port [5432]: 
Username [postgres]: halldb_user
Password for user halldb_user: dCu5hXO8okI8Qz0j9LK9i7AcZI3LYND0

)

init_db(DATABASE_URL)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/verificar_cpf', methods=['POST'])
def verificar_cpf():
    cpf = request.form.get('cpf', '').strip()
    session = get_session()
    cliente = session.query(Cliente).filter(Cliente.cpf == cpf).first()
    if cliente:
        produtos = session.query(Produto).all()
        session.close()
        return render_template('pedido.html', cliente=cliente, produtos=produtos)
    else:
        session.close()
        return redirect(url_for('cadastro', cpf=cpf))

@app.route('/cadastro')
def cadastro():
    cpf = request.args.get('cpf', '')
    return render_template('cadastro.html', cpf=cpf)

@app.route('/salvar_cliente', methods=['POST'])
def salvar_cliente():
    nome = request.form.get('nome')
    cpf = request.form.get('cpf', '')
    telefone = request.form.get('telefone', '')
    endereco = request.form.get('endereco', '')

    session = get_session()
    cliente = Cliente(nome=nome, cpf=cpf, telefone=telefone, endereco=endereco)
    session.add(cliente)
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        cliente = session.query(Cliente).filter(Cliente.cpf == cpf).first()
    cliente = session.query(Cliente).filter(Cliente.cpf == cpf).first()
    produtos = session.query(Produto).all()
    session.close()
    return render_template('pedido.html', cliente=cliente, produtos=produtos)

@app.route('/salvar_pedido', methods=['POST'])
def salvar_pedido():
    data = request.get_json() or request.form
    id_cliente = int(data.get('id_cliente'))
    itens = data.get('itens')
    tipo = data.get('tipo', 'Delivery')
    observacoes = data.get('observacoes', '')

    session = get_session()
    total = 0.0
    for it in itens:
        total += float(it['preco']) * int(it['qtd'])

    pedido = Pedido(id_cliente=id_cliente, tipo=tipo, valor_total=total, status='Pendente')
    session.add(pedido)
    session.commit()
    for it in itens:
        item = ItemPedido(id_pedido=pedido.id,
                          id_produto=int(it.get('id') or 0),
                          nome_produto=it['nome'],
                          quantidade=int(it['qtd']),
                          valor_unitario=float(it['preco']),
                          valor_total=float(it['preco'])*int(it['qtd']))
        session.add(item)
    session.commit()
    session.close()
    return jsonify({'status':'ok','pedido_id': pedido.id, 'mensagem':'Pedido criado'})

@app.route('/listar_pedidos')
def listar_pedidos():
    session = get_session()
    pedidos = session.query(Pedido).order_by(Pedido.id.desc()).all()
    out = []
    for p in pedidos:
        out.append({'id':p.id,'cliente':p.cliente.nome if p.cliente else None,'valor_total':p.valor_total,'status':p.status,'data_hora':p.data_hora.isoformat()})
    session.close()
    return jsonify(out)

if __name__ == '__main__':
    app.run()
