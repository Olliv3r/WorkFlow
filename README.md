# WorkFlow

![Preview](assets/preview.png)

**Versão atual: v0.0.8**

O **WorkFlow** é um sistema web em **Python + Flask** criado para registrar produções, organizar produtos e preços, controlar diárias e vales, realizar fechamentos e acompanhar valores recebidos e pendentes.

A versão `v0.0.8` consolida a evolução mais recente do projeto e passa a ser a versão de referência da **branch principal**.

## Objetivo

O sistema foi criado para substituir anotações manuais e cálculos espalhados por um fluxo único e rastreável:

```text
Trabalho realizado
      ↓
Produções + Diárias
      ↓
Fechamento
      ↓
Vales / abatimentos
      ↓
Recebimentos
      ↓
Pendências e relatórios
```

O projeto continua sendo um **monólito Flask e monousuário**, focado no processo real de produção e pagamento.

## Principais recursos

### Dashboard

A tela inicial reúne indicadores e atalhos para as áreas principais do sistema, oferecendo uma visão rápida do trabalho registrado e da situação financeira.

### Produções

Cada produção registra:

- data;
- produto;
- etapa;
- quantidade em dúzias;
- preço por dúzia;
- valor total;
- observação;
- fechamento relacionado, quando houver.

As etapas usadas atualmente para produção são:

- **Amarração**;
- **Enchimento**.

Produções já vinculadas a um fechamento ficam protegidas contra alterações destrutivas que comprometam o histórico financeiro.

### Diárias

Serviços auxiliares são registrados como **Diárias**, separados das produções por dúzia.

Cada diária possui:

- data;
- período;
- descrição;
- valor informado manualmente;
- observação;
- fechamento relacionado, quando houver.

O valor é definido por ocorrência. O sistema não força uma diária inteira ou meia diária a seguir um preço fixo global.

### Produtos

Os produtos são formados por combinações de:

- família;
- material;
- qualidade, quando aplicável;
- quantidade de furos, quando aplicável;
- tipo de taco.

A **Capa Quadrada** não possui furos.

O catálogo padrão atual contempla:

| Produto | Furos |
| --- | --- |
| Básica | 16 |
| Extra | 16, 20 e 22 |
| Inovada | 20 |
| PET | 16 e 20 |
| Náilon | 16 e 20 |
| Cipó | 16 e 20 |
| Capa Quadrada | Sem furos |

### Preços

A tabela de preços usa a relação:

```text
Produto + Etapa → Preço por dúzia
```

O preço é usado para preencher automaticamente uma nova produção.

Depois que a produção é criada, o preço utilizado fica congelado em `Production.price_per_dozen`. Alterar a tabela de preços não modifica produções antigas.

A Capa Quadrada possui preços diferentes por etapa:

- Amarração: **R$ 1,50 por dúzia**;
- Enchimento: **R$ 2,50 por dúzia**.

### Cadastros auxiliares

A área de Cadastros centraliza:

- Famílias;
- Materiais;
- Qualidades;
- Furos;
- Tipos de taco;
- Etapas.

O seed usa chaves naturais para evitar duplicação de registros e pode ser executado novamente com segurança.

### Fechamentos

Um fechamento reúne trabalhos selecionados de um período:

```text
Produções selecionadas
+ Diárias selecionadas
= Valor bruto
- Vales aplicados
= Valor líquido a receber
```

Os totais são recalculados no backend a partir dos registros persistidos. Valores enviados pelo JavaScript não são tratados como fonte financeira confiável.

O fechamento é criado **antes** do recebimento real do dinheiro.

### Vales

Os vales preservam o valor original e possuem saldo calculado a partir dos abatimentos já realizados.

Status possíveis:

- `pending`: ainda não abatido;
- `partial`: parcialmente abatido;
- `discounted`: totalmente abatido.

Quando existem pendências, um novo vale possui **três modos**:

1. **Pagamento pendente mais recente** — aplica o vale somente à pendência mais recente.
2. **Escolher pagamento** — permite selecionar manualmente qual pendência será afetada.
3. **Próximo fechamento** — não altera pagamentos pendentes e deixa o vale reservado para um fechamento futuro.

Os três modos exibem confirmação antes da operação.

Quando o vale é maior que a pendência escolhida, o excedente não percorre outras pendências automaticamente. O saldo restante continua aguardando um fechamento futuro.

Vales sem abatimentos podem ser editados ou excluídos. Depois de qualquer abatimento, o histórico fica protegido e não há desfazer da movimentação financeira.

### Recebimentos e pendências

O WorkFlow separa dois conceitos:

```text
Fechamento = quanto foi apurado como devido
Recebimento = dinheiro efetivamente recebido
```

Um fechamento pode estar:

- aguardando recebimento;
- parcialmente recebido;
- quitado.

Recebimentos posteriores podem ser associados a um fechamento conhecido. Quando a origem não é conhecida, o sistema permite registrar o recebimento sem inventar automaticamente qual fechamento ele quitou.

A área de Pendências permite acompanhar os saldos ainda a receber por fechamento.

### Detalhes

As principais rotas seguem o mesmo padrão de consulta com a ação **Detalhes**, incluindo:

- Preços;
- Cadastros;
- Produtos;
- Pendências;
- Vales;
- Pagamentos/Fechamentos;
- Diárias.

### Relatórios e exportação

A área de relatórios permite acompanhar produção e movimentações financeiras por período.

A exportação completa gera um **ZIP** com arquivos CSV separados:

```text
producoes.csv
diarias.csv
fechamentos.csv
vales.csv
abatimentos_vales.csv
recebimentos.csv
alocacoes_recebimentos.csv
```

Os relatórios de vales diferenciam:

- abatimento realizado durante um fechamento;
- vale aplicado posteriormente a uma pendência;
- saldo restante;
- vale aguardando fechamento futuro.

A exportação antiga em CSV continua disponível para compatibilidade.

### Backup e atualização do banco

SQLite continua sendo o banco padrão.

Para atualizar uma base existente, use:

```bash
python scripts/upgrade_database.py
```

O script:

1. cria uma cópia de segurança do `dev.db` local;
2. executa as migrations existentes;
3. interrompe o processo caso o upgrade falhe.

> Para dados reais, mantenha sempre uma cópia externa confiável antes de testar uma nova versão.

## Arquitetura

O fluxo principal da aplicação segue:

```text
HTTP / Form
    ↓
View
    ↓
DTO / parsing
    ↓
Service
    ↓
Repository
    ↓
SQLAlchemy
    ↓
Banco de dados
```

Responsabilidades principais:

- **Views**: requisições HTTP, formulários e respostas;
- **DTOs/parsers**: conversão e validação de entrada;
- **Services**: regras de negócio e transações;
- **Repositories**: persistência e consultas;
- **Models**: estrutura persistida e relacionamentos.

## Tecnologias

- Python
- Flask
- Flask-SQLAlchemy / SQLAlchemy
- Flask-Migrate / Alembic
- SQLite
- PostgreSQL opcional
- MySQL opcional
- Jinja2
- Bootstrap 5 / Bootstrap-Flask
- JavaScript modularizado
- jQuery

## Estrutura resumida

```text
WorkFlow/
├── app/
│   ├── advance/
│   ├── daily_work/
│   ├── main/
│   ├── payment/
│   ├── price/
│   ├── product/
│   ├── production/
│   ├── registry/
│   ├── report/
│   ├── seed/
│   ├── models/
│   ├── templates/
│   └── static/
├── migrations/
├── scripts/
│   └── upgrade_database.py
├── tests/
├── assets/
├── config.py
├── main.py
├── server.sh
└── README.md
```

## Instalação

Clone o projeto:

```bash
git clone https://github.com/Olliv3r/WorkFlow.git
cd WorkFlow
```

Crie e ative um ambiente virtual Python.

Linux, Termux ou macOS:

```bash
python -m venv ~/venv-wf
source ~/venv-wf/bin/activate
```

Windows:

```powershell
python -m venv .venv
.venv\Scripts\activate
```

Instale as dependências:

```bash
pip install -r requirements.txt
```

Aplique as migrations:

```bash
python scripts/upgrade_database.py
```

Popule os dados iniciais:

```bash
./server.sh seed
```

Inicie o servidor:

```bash
./server.sh flask run --debug
```

> O caminho do ambiente virtual usado por `server.sh` pode ser ajustado na variável `VENV` do próprio script.

## Seed

O seed atual exibe o resultado de cada categoria processada:

```text
Famílias
Materiais
Qualidades
Furos
Tipos de taco
Etapas
Produtos
Preços
```

Ele cadastra apenas registros ausentes e preserva preços existentes que tenham sido alterados posteriormente.

## Outros bancos de dados

A conexão pode ser configurada pela variável `DATABASE_URL`.

### PostgreSQL

```bash
pip install -r requirements-postgresql.txt
export DATABASE_URL='postgresql://usuario:senha@host:5432/workflow'
python scripts/upgrade_database.py
```

### MySQL

```bash
pip install -r requirements-mysql.txt
export DATABASE_URL='mysql://usuario:senha@host:3306/workflow'
python scripts/upgrade_database.py
```

A configuração de outro SGBD não transfere automaticamente os dados existentes do SQLite. Consulte [`DATABASES.md`](DATABASES.md) antes de uma migração real.

## Testes

Instale as dependências de desenvolvimento:

```bash
pip install -r requirements-dev.txt
```

Execute:

```bash
python -m pytest -q
```

Para a verificação de release:

```bash
./scripts/verify_release.sh
```

## Versão v0.0.8

Esta versão consolida na branch principal as evoluções de domínio e interface desenvolvidas após a versão anterior, incluindo:

- diárias com valor manual;
- separação entre fechamento e recebimento;
- controle de pendências;
- vales com histórico de abatimentos e três modos de destino;
- catálogo e preços atualizados;
- Capa Quadrada sem furos;
- produção limitada a Amarração e Enchimento;
- exportação financeira completa;
- telas de Detalhes padronizadas;
- seed idempotente incluindo preços;
- correções de navegação mobile;
- atualização segura do banco com backup prévio.

## Licença

Consulte o arquivo de licença do repositório, quando presente, para as condições de uso e distribuição.
