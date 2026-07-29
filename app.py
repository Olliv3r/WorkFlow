import os
import sqlite3
from datetime import datetime

from flask import Flask, g, jsonify, request, render_template

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "producao.db")

app = Flask(__name__)


# ---------------------------------------------------------------------------
# Conexão com o banco
# ---------------------------------------------------------------------------
def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


@app.teardown_appcontext
def close_db(exception=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


# Furos são um conjunto FIXO e FECHADO de 4 valores — confirmado pelo
# usuário que nunca vai aparecer um número fora desta lista. Se isso
# mudar no futuro, esta lista (e só ela) precisa ser editada.
FUROS_VALIDOS = [16, 20, 22, 30]


def ensure_schema():
    """Garante que as tabelas existem, mesmo se init_db.py não tiver sido rodado antes."""
    conn = sqlite3.connect(DB_PATH)
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS materiais (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL UNIQUE,
            ativo INTEGER NOT NULL DEFAULT 1,
            criado_em TEXT NOT NULL DEFAULT (datetime('now', 'localtime'))
        );

        CREATE TABLE IF NOT EXISTS tipos_servico (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL UNIQUE,
            descricao TEXT NOT NULL DEFAULT '',
            ativo INTEGER NOT NULL DEFAULT 1,
            criado_em TEXT NOT NULL DEFAULT (datetime('now', 'localtime'))
        );

        CREATE TABLE IF NOT EXISTS tabela_precos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            material_id INTEGER NOT NULL,
            furos INTEGER NOT NULL,
            valor_duzia REAL NOT NULL CHECK (valor_duzia >= 0),
            atualizado_em TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
            FOREIGN KEY (material_id) REFERENCES materiais(id),
            UNIQUE (material_id, furos)
        );

        CREATE TABLE IF NOT EXISTS registros (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tipo_produto TEXT NOT NULL,
            quantidade_duzias REAL NOT NULL CHECK (quantidade_duzias >= 0),
            tipo_servico_id INTEGER NOT NULL,
            tipo_servico_nome TEXT NOT NULL,
            material_id INTEGER NOT NULL,
            material_nome TEXT NOT NULL,
            furos INTEGER NOT NULL,
            valor_duzia_aplicado REAL NOT NULL,
            valor_total REAL NOT NULL,
            data TEXT NOT NULL,
            periodo TEXT NOT NULL,
            pagamento TEXT NOT NULL DEFAULT 'pendente' CHECK (pagamento IN ('pendente', 'quitado')),
            criado_em TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
            FOREIGN KEY (tipo_servico_id) REFERENCES tipos_servico(id),
            FOREIGN KEY (material_id) REFERENCES materiais(id)
        );

        CREATE INDEX IF NOT EXISTS idx_registros_data ON registros(data);
    """)
    conn.commit()
    conn.close()


PERIODOS_VALIDOS = {"dia", "semana", "quinzena", "mes", "ano"}
PAGAMENTOS_VALIDOS = {"pendente", "quitado"}


def erro(mensagem, status=400):
    return jsonify({"erro": mensagem}), status


# ---------------------------------------------------------------------------
# Página principal
# ---------------------------------------------------------------------------
@app.route("/")
def index():
    return render_template("index.html")


# ---------------------------------------------------------------------------
# API: Materiais
# ---------------------------------------------------------------------------
@app.route("/api/materiais", methods=["GET"])
def listar_materiais():
    apenas_ativos = request.args.get("apenas_ativos", "false").lower() == "true"
    db = get_db()
    if apenas_ativos:
        rows = db.execute("SELECT * FROM materiais WHERE ativo = 1 ORDER BY nome").fetchall()
    else:
        rows = db.execute("SELECT * FROM materiais ORDER BY nome").fetchall()
    return jsonify([dict(r) for r in rows])


# ---------------------------------------------------------------------------
# API: Furos válidos (lista fixa — não editável pelo usuário)
# ---------------------------------------------------------------------------
@app.route("/api/furos", methods=["GET"])
def listar_furos():
    return jsonify(FUROS_VALIDOS)


# ---------------------------------------------------------------------------
# API: Tipos de serviço (etapas do processo — SEM preço; preço vem de
# tabela_precos, cruzando material + furos)
# ---------------------------------------------------------------------------
@app.route("/api/tipos-servico", methods=["GET"])
def listar_tipos_servico():
    apenas_ativos = request.args.get("apenas_ativos", "false").lower() == "true"
    db = get_db()
    if apenas_ativos:
        rows = db.execute(
            "SELECT * FROM tipos_servico WHERE ativo = 1 ORDER BY nome"
        ).fetchall()
    else:
        rows = db.execute("SELECT * FROM tipos_servico ORDER BY nome").fetchall()
    return jsonify([dict(r) for r in rows])


@app.route("/api/tipos-servico", methods=["POST"])
def criar_tipo_servico():
    dados = request.get_json(silent=True) or {}
    nome = (dados.get("nome") or "").strip()
    descricao = (dados.get("descricao") or "").strip()

    if not nome:
        return erro("O nome da etapa é obrigatório.")

    db = get_db()
    try:
        cur = db.execute(
            "INSERT INTO tipos_servico (nome, descricao) VALUES (?, ?)",
            (nome, descricao),
        )
        db.commit()
    except sqlite3.IntegrityError:
        return erro(f'Já existe uma etapa chamada "{nome}".', 409)

    novo = db.execute("SELECT * FROM tipos_servico WHERE id = ?", (cur.lastrowid,)).fetchone()
    return jsonify(dict(novo)), 201


@app.route("/api/tipos-servico/<int:tipo_id>", methods=["PUT"])
def atualizar_tipo_servico(tipo_id):
    dados = request.get_json(silent=True) or {}
    db = get_db()
    existente = db.execute("SELECT * FROM tipos_servico WHERE id = ?", (tipo_id,)).fetchone()
    if existente is None:
        return erro("Etapa não encontrada.", 404)

    nome = dados.get("nome", existente["nome"])
    if isinstance(nome, str):
        nome = nome.strip()
    descricao = dados.get("descricao", existente["descricao"])
    if isinstance(descricao, str):
        descricao = descricao.strip()
    ativo = dados.get("ativo", existente["ativo"])

    if not nome:
        return erro("O nome da etapa é obrigatório.")

    try:
        db.execute(
            "UPDATE tipos_servico SET nome = ?, descricao = ?, ativo = ? WHERE id = ?",
            (nome, descricao, 1 if ativo else 0, tipo_id),
        )
        db.commit()
    except sqlite3.IntegrityError:
        return erro(f'Já existe uma etapa chamada "{nome}".', 409)

    atualizado = db.execute("SELECT * FROM tipos_servico WHERE id = ?", (tipo_id,)).fetchone()
    return jsonify(dict(atualizado))


@app.route("/api/tipos-servico/<int:tipo_id>", methods=["DELETE"])
def excluir_tipo_servico(tipo_id):
    db = get_db()
    existente = db.execute("SELECT * FROM tipos_servico WHERE id = ?", (tipo_id,)).fetchone()
    if existente is None:
        return erro("Etapa não encontrada.", 404)

    em_uso = db.execute(
        "SELECT COUNT(*) as total FROM registros WHERE tipo_servico_id = ?", (tipo_id,)
    ).fetchone()["total"]

    if em_uso > 0:
        db.execute("UPDATE tipos_servico SET ativo = 0 WHERE id = ?", (tipo_id,))
        db.commit()
        return jsonify({
            "acao": "desativado",
            "mensagem": (
                f'"{existente["nome"]}" já foi usada em {em_uso} registro(s) e não pode '
                "ser excluída. Foi desativada em vez disso — os registros antigos não "
                "são afetados."
            ),
        })

    db.execute("DELETE FROM tipos_servico WHERE id = ?", (tipo_id,))
    db.commit()
    return jsonify({"acao": "excluido"})


# ---------------------------------------------------------------------------
# API: Tabela de preços (Material × Furos → Valor/dúzia)
# ---------------------------------------------------------------------------
@app.route("/api/tabela-precos", methods=["GET"])
def listar_tabela_precos():
    """Retorna a matriz completa Material x Furos, incluindo combinações
    ainda SEM preço cadastrado (valor_duzia vem como null nesse caso —
    diferente de 0, que significaria 'preço cadastrado como zero')."""
    db = get_db()
    materiais = db.execute("SELECT * FROM materiais WHERE ativo = 1 ORDER BY nome").fetchall()
    precos_existentes = {
        (row["material_id"], row["furos"]): row
        for row in db.execute("SELECT * FROM tabela_precos").fetchall()
    }

    matriz = []
    for material in materiais:
        linha = {"material_id": material["id"], "material_nome": material["nome"], "precos": []}
        for furos in FUROS_VALIDOS:
            existente = precos_existentes.get((material["id"], furos))
            linha["precos"].append({
                "furos": furos,
                "valor_duzia": existente["valor_duzia"] if existente else None,
            })
        matriz.append(linha)

    return jsonify(matriz)


def buscar_ou_none_preco(db, material_id, furos):
    row = db.execute(
        "SELECT * FROM tabela_precos WHERE material_id = ? AND furos = ?",
        (material_id, furos),
    ).fetchone()
    return row["valor_duzia"] if row else None


@app.route("/api/tabela-precos", methods=["PUT"])
def definir_preco():
    """Cria ou sobrescreve o valor/dúzia de uma combinação (material, furos).
    Usado tanto pela tela de Gerenciar preços quanto pelo campo editável
    no formulário principal — ambos escrevem na mesma tabela."""
    dados = request.get_json(silent=True) or {}
    material_id = dados.get("material_id")
    furos = dados.get("furos")
    valor_duzia = dados.get("valor_duzia")

    try:
        material_id = int(material_id)
    except (TypeError, ValueError):
        return erro("Material inválido.")

    try:
        furos = int(furos)
    except (TypeError, ValueError):
        return erro("Quantidade de furos inválida.")
    if furos not in FUROS_VALIDOS:
        return erro(f"Quantidade de furos precisa ser uma destas: {FUROS_VALIDOS}.")

    try:
        valor_duzia = float(valor_duzia)
    except (TypeError, ValueError):
        return erro("O valor por dúzia precisa ser um número.")
    if valor_duzia < 0:
        return erro("O valor por dúzia não pode ser negativo.")

    db = get_db()
    material = db.execute("SELECT * FROM materiais WHERE id = ?", (material_id,)).fetchone()
    if material is None:
        return erro("Material não encontrado.", 404)

    db.execute(
        """
        INSERT INTO tabela_precos (material_id, furos, valor_duzia, atualizado_em)
        VALUES (?, ?, ?, datetime('now', 'localtime'))
        ON CONFLICT(material_id, furos)
        DO UPDATE SET valor_duzia = excluded.valor_duzia,
                      atualizado_em = excluded.atualizado_em
        """,
        (material_id, furos, valor_duzia),
    )
    db.commit()

    return jsonify({
        "material_id": material_id,
        "material_nome": material["nome"],
        "furos": furos,
        "valor_duzia": valor_duzia,
    })


# ---------------------------------------------------------------------------
# API: Registros de produção
# ---------------------------------------------------------------------------
@app.route("/api/registros", methods=["GET"])
def listar_registros():
    db = get_db()
    rows = db.execute("SELECT * FROM registros ORDER BY id DESC").fetchall()
    return jsonify([dict(r) for r in rows])


@app.route("/api/registros", methods=["POST"])
def criar_registro():
    dados = request.get_json(silent=True) or {}

    tipo_produto = (dados.get("tipo_produto") or "").strip()
    quantidade_duzias = dados.get("quantidade_duzias")
    tipo_servico_id = dados.get("tipo_servico_id")
    material_id = dados.get("material_id")
    furos = dados.get("furos")
    data = (dados.get("data") or "").strip()
    periodo = (dados.get("periodo") or "").strip()
    pagamento = (dados.get("pagamento") or "pendente").strip()
    # valor_duzia_manual: quando o formulário principal envia um valor
    # digitado na hora (porque a combinação não tinha preço, ou porque
    # o usuário optou por sobrescrever). Se None, usa o preço da tabela.
    valor_duzia_manual = dados.get("valor_duzia_manual")

    if not tipo_produto:
        return erro("O tipo de produto é obrigatório.")

    try:
        quantidade_duzias = float(quantidade_duzias)
    except (TypeError, ValueError):
        return erro("A quantidade (em dúzias) precisa ser um número.")
    if quantidade_duzias <= 0:
        return erro("A quantidade precisa ser maior que zero.")

    if tipo_servico_id is None:
        return erro("Selecione a etapa (função) realizada.")
    try:
        tipo_servico_id = int(tipo_servico_id)
    except (TypeError, ValueError):
        return erro("Etapa inválida.")

    if material_id is None:
        return erro("Selecione o material.")
    try:
        material_id = int(material_id)
    except (TypeError, ValueError):
        return erro("Material inválido.")

    if furos is None:
        return erro("Selecione a quantidade de furos do taco.")
    try:
        furos = int(furos)
    except (TypeError, ValueError):
        return erro("Quantidade de furos inválida.")
    if furos not in FUROS_VALIDOS:
        return erro(f"Quantidade de furos precisa ser uma destas: {FUROS_VALIDOS}.")

    if not data:
        return erro("A data é obrigatória.")
    try:
        datetime.strptime(data, "%Y-%m-%d")
    except ValueError:
        return erro("Data inválida. Use o formato AAAA-MM-DD.")

    if periodo not in PERIODOS_VALIDOS:
        return erro("Selecione um período de referência válido.")

    if pagamento not in PAGAMENTOS_VALIDOS:
        return erro("Estado de pagamento inválido.")

    db = get_db()

    tipo_servico = db.execute(
        "SELECT * FROM tipos_servico WHERE id = ?", (tipo_servico_id,)
    ).fetchone()
    if tipo_servico is None:
        return erro("Etapa não encontrada.", 404)

    material = db.execute("SELECT * FROM materiais WHERE id = ?", (material_id,)).fetchone()
    if material is None:
        return erro("Material não encontrado.", 404)

    # Resolve o valor/dúzia: prioriza o valor manual enviado pelo formulário
    # (o usuário digitou/sobrescreveu na hora); senão busca da tabela_precos.
    if valor_duzia_manual is not None:
        try:
            valor_duzia_aplicado = float(valor_duzia_manual)
        except (TypeError, ValueError):
            return erro("O valor por dúzia informado precisa ser um número.")
        if valor_duzia_aplicado < 0:
            return erro("O valor por dúzia não pode ser negativo.")

        # Um valor digitado no formulário principal também atualiza a
        # tabela de preços — confirmado explicitamente pelo usuário.
        db.execute(
            """
            INSERT INTO tabela_precos (material_id, furos, valor_duzia, atualizado_em)
            VALUES (?, ?, ?, datetime('now', 'localtime'))
            ON CONFLICT(material_id, furos)
            DO UPDATE SET valor_duzia = excluded.valor_duzia,
                          atualizado_em = excluded.atualizado_em
            """,
            (material_id, furos, valor_duzia_aplicado),
        )
    else:
        preco_existente = buscar_ou_none_preco(db, material_id, furos)
        if preco_existente is None:
            return erro(
                f'Não há preço cadastrado para "{material["nome"]}" com {furos} furos. '
                "Informe o valor por dúzia neste registro ou cadastre-o em Gerenciar preços."
            )
        valor_duzia_aplicado = preco_existente

    valor_total = round(quantidade_duzias * valor_duzia_aplicado, 2)

    cur = db.execute(
        """
        INSERT INTO registros (
            tipo_produto, quantidade_duzias, tipo_servico_id, tipo_servico_nome,
            material_id, material_nome, furos,
            valor_duzia_aplicado, valor_total, data, periodo, pagamento
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            tipo_produto,
            quantidade_duzias,
            tipo_servico_id,
            tipo_servico["nome"],
            material_id,
            material["nome"],
            furos,
            valor_duzia_aplicado,
            valor_total,
            data,
            periodo,
            pagamento,
        ),
    )
    db.commit()

    novo = db.execute("SELECT * FROM registros WHERE id = ?", (cur.lastrowid,)).fetchone()
    return jsonify(dict(novo)), 201


@app.route("/api/registros/<int:registro_id>", methods=["PATCH"])
def atualizar_pagamento_registro(registro_id):
    """Atualização parcial — hoje só usada para alternar Pendente/Quitado."""
    dados = request.get_json(silent=True) or {}
    pagamento = (dados.get("pagamento") or "").strip()

    if pagamento not in PAGAMENTOS_VALIDOS:
        return erro("Estado de pagamento inválido.")

    db = get_db()
    existente = db.execute("SELECT * FROM registros WHERE id = ?", (registro_id,)).fetchone()
    if existente is None:
        return erro("Registro não encontrado.", 404)

    db.execute("UPDATE registros SET pagamento = ? WHERE id = ?", (pagamento, registro_id))
    db.commit()

    atualizado = db.execute("SELECT * FROM registros WHERE id = ?", (registro_id,)).fetchone()
    return jsonify(dict(atualizado))


@app.route("/api/registros/<int:registro_id>", methods=["DELETE"])
def excluir_registro(registro_id):
    db = get_db()
    existente = db.execute("SELECT * FROM registros WHERE id = ?", (registro_id,)).fetchone()
    if existente is None:
        return erro("Registro não encontrado.", 404)

    db.execute("DELETE FROM registros WHERE id = ?", (registro_id,))
    db.commit()
    return jsonify({"acao": "excluido"})


# ---------------------------------------------------------------------------
# API: Resumo do dia (total da diária somando produtos/materiais diferentes)
# ---------------------------------------------------------------------------
@app.route("/api/resumo-dia", methods=["GET"])
def resumo_dia():
    data = request.args.get("data")
    if not data:
        return erro("Informe o parâmetro ?data=AAAA-MM-DD.")

    db = get_db()
    rows = db.execute("SELECT * FROM registros WHERE data = ? ORDER BY id", (data,)).fetchall()

    total_duzias = sum(r["quantidade_duzias"] for r in rows)
    total_valor = round(sum(r["valor_total"] for r in rows), 2)
    total_quitado = round(sum(r["valor_total"] for r in rows if r["pagamento"] == "quitado"), 2)
    total_pendente = round(total_valor - total_quitado, 2)

    return jsonify({
        "data": data,
        "total_registros": len(rows),
        "total_duzias": total_duzias,
        "total_valor": total_valor,
        "total_quitado": total_quitado,
        "total_pendente": total_pendente,
        "registros": [dict(r) for r in rows],
    })


if __name__ == "__main__":
    ensure_schema()
    app.run(host="0.0.0.0", port=5000, debug=True)
