from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
import qrcode
import os
import PIL

app = Flask(__name__)
app.secret_key = "sua_chave_secreta"

produtos = [
    {"id": 1, "nome": 'Smartphone', "preço": float(2500.00), "imagem": 'smartphone.jpg'},
    {"id": 2, "nome": 'Notebook', "preço": float(3500.00), "imagem": 'notebook.jpg'},
    {"id": 3, "nome": 'Fone de Ouvido', "preço": float(200.00), "imagem": 'fone.jpg'}
]

QR_CODE_FOLDER = 'static/qrcodes'
os.makedirs(QR_CODE_FOLDER, exist_ok=True)

@app.route('/finalizar-compra', methods=['POST'])
def finalizar_compra():
    forma_pagamento = request.form.get('formaPagamento')
    if forma_pagamento == 'Cartão':
        numero_cartao = request.form.get('numeroCartao')
        nome_cartao = request.form.get('nomeCartao')
        validade = request.form.get('validade')
        cvv = request.form.get('cvv')
        if not all([numero_cartao, nome_cartao, validade, cvv]):
            flash('Todos os campos do cartão devem ser preenchidos.', 'erro')
            return redirect(url_for('checkout'))
    return render_template('pagamento_sucesso.html')


def gerar_qr_pix(valor):
    chave_pix = "exemplo@banco.com"
    pix_code = f"00020126330014BR.GOV.BCB.PIX0114{chave_pix}520400005303986540{valor}5802BR5920Loja Flask6008Cidade"
    qr_path = os.path.join(QR_CODE_FOLDER, "pix_qr.png")
    qr = qrcode.make(pix_code)
    qr.save(qr_path)
    return pix_code, qr_path

@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    total = 12200.00
    qr_code = None
    mensagem = None
    if request.method == 'POST':
        metodo_pagamento = request.form.get('metodo_pagamento')
        if metodo_pagamento == 'pix':
            _, qr_path = gerar_qr_pix(total)
            qr_code = f"/{qr_path}"
        elif metodo_pagamento == 'cartao':
            mensagem = "Pagamento com cartão aprovado!"
    return render_template('checkout.html', total=total, qr_code=qr_code, mensagem=mensagem)

@app.route('/')
def index():
    if 'carrinho' not in session:
        session['carrinho'] = []
    return render_template('index.html', produtos=produtos)

@app.route('/adicionar/<int:produto_id>')
def adicionar_ao_carrinho(produto_id):
    if 'carrinho' not in session:
        session['carrinho'] = []
    for produto in produtos:
        if produto['id'] == produto_id:
            session['carrinho'].append(produto)
            session.modified = True
            break
    return redirect(url_for('index'))

@app.route('/remover/<int:produto_id>')
def remover_do_carrinho(produto_id):
    if 'carrinho' in session:
        carrinho = session['carrinho']
        for i, produto in enumerate(carrinho):
            if produto['id'] == produto_id:
                del carrinho[i]
                break
        session['carrinho'] = carrinho
        session.modified = True
    return redirect(url_for('carrinho'))

@app.route('/carrinho')
def carrinho():
    total = sum(float(item['preço']) for item in session.get('carrinho', []))
    return render_template('carrinho.html', carrinho=session.get('carrinho', []), total=total)

if __name__ == '__main__':
   app.run(host='0.0.0.0', port=10000)
