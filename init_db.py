"""
Inicializa o banco de dados SQLite com o schema da Ficha de Produção,
pré-cadastra os 4 materiais, as 9 etapas do processo (sem preço — preço
vem da tabela_precos) e os 4 valores de preço já confirmados (Material
x 20 furos).

Rodar uma vez: python init_db.py
Se o banco já existir, este script NÃO apaga dados nem duplica
registros já cadastrados — é seguro rodar mais de uma vez.

MODELO DE PREÇO (importante entender antes de usar):
O preço de um registro depende de (Material, Quantidade de furos do
taco) — NÃO da etapa/função. "Amarrar" e "Pentear" custam o mesmo
valor por dúzia se usarem o mesmo material e a mesma quantidade de
furos. A etapa (tipos_servico) é só o rótulo de "o que foi feito",
sem efeito no cálculo.

Furos é um conjunto FECHADO de 4 valores: 16, 20, 22, 30. Não existe
"faixa" (tipo "20 ou mais") — são 4 quantidades exatas e distintas,
cada uma com seu próprio preço por material.

Hoje só a combinação "20 furos" tem preço cadastrado (Pete R$5,00,
Cipó R$3,00, Nailon R$3,00, Piaçaba R$2,00). As combinações com 16,
22 e 30 furos ficam sem preço até você preenchê-las — pela tela
"Gerenciar preços" ou digitando o valor direto no formulário
principal na hora de registrar (o que você digitar ali também
atualiza a tabela de preços para a próxima vez).

Nota sobre "Pinar" vs "Pinar cabo": são duas etapas distintas do
processo. "Pinar" fixa o pino no corpo do produto (após amarrar e
encher); "Pinar cabo" fixa o pino que prende o cabo já pronto ao
corpo montado.
"""
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "producao.db")

FUROS_VALIDOS = [16, 20, 22, 30]

SCHEMA = """
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
"""

MATERIAIS_INICIAIS = ["Pete", "Cipó", "Nailon", "Piaçaba"]

ETAPAS_INICIAIS = [
    ("Amarrar", "Fazer as trouxinhas para encher em cada furo do taco"),
    ("Encher", ""),
    ("Pinar", "Fixar o pino no corpo do produto, após amarrar e encher"),
    ("Pentear", ""),
    ("Aparar pontas", ""),
    ("Pintar", ""),
    ("Encabar", "Encaixar a cabeça (taco já enchido) no cabo"),
    ("Pinar cabo", "Fixar o pino que prende o cabo já pronto ao corpo montado"),
    ("Plugar", "Colocar o plug na ponta do cabo para pendurar o produto"),
]

# Preços já confirmados: (material, furos) -> valor por dúzia.
# Só "20 furos" está preenchido até agora — 16, 22 e 30 ficam para você
# completar depois, pela tela "Gerenciar preços" ou digitando na hora
# do registro.
PRECOS_INICIAIS = [
    ("Pete", 20, 5.00),
    ("Cipó", 20, 3.00),
    ("Nailon", 20, 3.00),
    ("Piaçaba", 20, 2.00),
]


def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.executescript(SCHEMA)

    materiais_inseridos = 0
    for nome in MATERIAIS_INICIAIS:
        cur = conn.execute("INSERT OR IGNORE INTO materiais (nome) VALUES (?)", (nome,))
        if cur.rowcount > 0:
            materiais_inseridos += 1

    etapas_inseridas = 0
    for nome, descricao in ETAPAS_INICIAIS:
        cur = conn.execute(
            "INSERT OR IGNORE INTO tipos_servico (nome, descricao) VALUES (?, ?)",
            (nome, descricao),
        )
        if cur.rowcount > 0:
            etapas_inseridas += 1

    precos_inseridos = 0
    for nome_material, furos, valor in PRECOS_INICIAIS:
        material_row = conn.execute(
            "SELECT id FROM materiais WHERE nome = ?", (nome_material,)
        ).fetchone()
        if material_row is None:
            continue
        material_id = material_row[0]
        cur = conn.execute(
            "INSERT OR IGNORE INTO tabela_precos (material_id, furos, valor_duzia) VALUES (?, ?, ?)",
            (material_id, furos, valor),
        )
        if cur.rowcount > 0:
            precos_inseridos += 1

    conn.commit()
    conn.close()

    print(f"Banco inicializado em: {DB_PATH}")
    print(f"{materiais_inseridos} material(is) novo(s), {etapas_inseridas} etapa(s) nova(s), "
          f"{precos_inseridos} preço(s) novo(s) cadastrado(s).")
    print(f"Furos válidos: {FUROS_VALIDOS} (lista fixa, definida no código).")
    print('Faltam preços para 16, 22 e 30 furos em todos os materiais — preencha em "Gerenciar preços" '
          "ou digite direto no formulário ao registrar produção.")


if __name__ == "__main__":
    init_db()
