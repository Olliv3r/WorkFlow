# WorkFlow

Sistema web para gerenciamento e acompanhamento de produção, desenvolvido com Flask e SQLAlchemy.

O WorkFlow foi criado para organizar o registro da produção, produtos, materiais, valores e pagamentos em um único sistema, reduzindo controles manuais e facilitando o acompanhamento financeiro da produção.

![WorkFlow — Preview do sistema](docs/preview.png)

## 🚀 Tecnologias

- Python
- Flask
- SQLAlchemy
- Flask-Migrate / Alembic
- Bootstrap-Flask
- SQLite
- Jinja2
- Bootstrap 5
- JavaScript modularizado (ES Modules) / jQuery

## 📋 Funcionalidades

### Produção

- Registro das produções realizadas
- Associação da produção a um produto e a uma etapa
- Registro da quantidade produzida em dúzias
- Registro do valor por dúzia
- Cálculo do valor total da produção
- Observações sobre a produção
- Consulta do histórico de produção

### Produtos

O sistema permite cadastrar produtos a partir de suas características, evitando a necessidade de recriar as mesmas combinações durante o registro da produção.

Os produtos podem ser definidos de acordo com características como:

- Família do produto
- Material
- Qualidade
- Quantidade de furos
- Tipo de taco

> ⚠️ O cadastro de novos produtos já está disponível na interface, mas a criação ainda não foi implementada no backend (`ProductService.product_create` está pendente).

### Pagamentos

O WorkFlow permite organizar os pagamentos com base em períodos de produção.

Um pagamento possui:

- Data inicial e final do período
- Data do pagamento
- Valor total e total de dúzias
- Status (`pending` ou `paid`)
- Observação

O valor do pagamento é calculado a partir das produções ainda não vinculadas a nenhum pagamento (`payment_id` nulo) dentro do período selecionado. Ao criar um pagamento, todas as produções escolhidas são vinculadas a ele.

Ações disponíveis por pagamento:

- **Marcar como Pago** / **Reverter para Pendente** — alterna o status e ajusta `payment_date` automaticamente
- **Excluir** — permitido apenas para pagamentos com status `pending`; ao excluir, as produções vinculadas são automaticamente desvinculadas (`payment_id = None`) e voltam a ficar disponíveis para um novo pagamento

## 🏗️ Arquitetura

O projeto é organizado **por módulo de domínio** (blueprint), e não por camada técnica global. Cada módulo (`production`, `payment`, `product`) contém suas próprias subpastas de `repositories/`, `services/` e `dtos/`, mantendo a lógica de cada domínio isolada.

Fluxo de uma requisição:

```
Request
   │
   ▼
Views (Blueprint) ── recebe a requisição, monta o DTO a partir do form
   │
   ▼
Service ── validação e regra de negócio
   │
   ▼
Repository ── acesso ao banco de dados
   │
   ▼
SQLAlchemy Models
   │
   ▼
Database
```

### Responsabilidades

**Views (por blueprint):**
Recebem as requisições HTTP, extraem os dados do formulário/request, montam o DTO correspondente e retornam a resposta (renderização de template ou JSON, dependendo da rota).

**Services:**
Concentram as regras de negócio — validação de DTO, busca de entidades relacionadas, cálculo de totais, e as regras de transição de estado (ex.: um pagamento só pode ser excluído se ainda estiver `pending`).

**Repositories:**
Responsáveis pelo acesso aos dados. Todos herdam de `CommonRepository` (`app/common/repositories/`), que concentra as operações básicas (`all`, `filter_by`, `add`, `commit`, `delete`), e cada módulo estende isso com consultas específicas do seu domínio.

**Models:**
Entidades persistidas via SQLAlchemy, em `app/models/` — compartilhadas entre todos os módulos, já que produção, produto e pagamento se relacionam entre si.

**DTOs:**
Estruturas (`dataclasses`) usadas para transportar e validar dados vindos do formulário antes de chegar à camada de serviço, com um método `is_valid()` próprio de validação.

**Core (`app/core/`):**
Hierarquia de exceções da aplicação (`AppException` e subclasses como `NotFoundError`, `ValidationError`, `ConflictError`, `PermissionError`), cada uma associada a um `status_code` HTTP, usada pelos services para sinalizar erros de forma consistente entre módulos.

## 📁 Estrutura

A estrutura real do projeto:

```
WorkFlow/
│
├── app/
│   ├── production/
│   │   ├── repositories/     (production, stage, family, material, hole, stick, quality)
│   │   ├── services/
│   │   ├── dtos/
│   │   └── views.py
│   │
│   ├── payment/
│   │   ├── repositories/
│   │   ├── services/
│   │   ├── dtos/
│   │   └── views.py
│   │
│   ├── product/
│   │   ├── repositories/
│   │   ├── services/
│   │   ├── dtos/
│   │   └── views.py
│   │
│   ├── main/
│   │   └── views.py
│   │
│   ├── seed/
│   │   ├── repositories/
│   │   ├── services/
│   │   └── seed_dict.py      (dados de seed: famílias, materiais, tacos, etapas, produtos)
│   │
│   ├── common/
│   │   └── repositories/     (CommonRepository — base para todos os repositories)
│   │
│   ├── core/
│   │   └── exceptions.py     (hierarquia de exceções da aplicação)
│   │
│   ├── models/                (models SQLAlchemy compartilhados)
│   ├── templates/
│   │   ├── base.html
│   │   ├── sidebar.html
│   │   ├── production/
│   │   └── payment/           (payments.html + _cards_partial.html + _history_table.html)
│   │
│   ├── static/
│   │   ├── css/
│   │   └── js/
│   │       └── modules/       (production/ e payment/, cada um com api.js, events.js, actions.js, ui.js)
│   │
│   └── extensions.py
│
├── migrations/
├── docs/
│   └── preview.png
│
├── config.py
├── main.py
├── requirements.txt
└── README.md
```

A separação por domínio (em vez de por camada global) significa que uma alteração na regra de pagamento, por exemplo, fica contida em `app/payment/`, sem tocar em `app/production/` ou `app/product/`.

## ⚙️ Instalação

Clone o repositório:

```bash
git clone https://github.com/Olliv3r/WorkFlow.git
cd WorkFlow
```

Crie um ambiente virtual:

```bash
python -m venv .venv
```

Ative o ambiente virtual.

Linux / macOS:

```bash
source .venv/bin/activate
```

Windows:

```bash
.venv\Scripts\activate
```

Instale as dependências:

```bash
pip install -r requirements.txt
```

Inicialize o banco de dados com as migrations:

```bash
flask db upgrade
```

(Opcional) Popule o banco com dados iniciais de família, material, taco, etapa e produtos:

```bash
./server.sh seed
```

Execute a aplicação:

```bash
flask run
```

## 🗄️ Banco de dados

O projeto utiliza SQLAlchemy como ORM. Durante o desenvolvimento, o banco utilizado é o SQLite.

As alterações estruturais do banco são controladas através de migrations com Alembic/Flask-Migrate.

```bash
flask db migrate -m "descrição da alteração"
flask db upgrade
```

Valores monetários (`price_per_dozen`, `total_amount`) são armazenados como `Numeric(12, 2)`, não como float — evitando os erros de arredondamento comuns em cálculos financeiros com ponto flutuante.

## 🔄 Fluxo de produção

```
Produto (cadastrado previamente)
   │
   ▼
Registro da produção
   │
   ├── Data
   ├── Produto
   ├── Etapa
   ├── Dúzias
   ├── Valor por dúzia
   └── Observação
   │
   ▼
Produção armazenada (payment_id = null)
   │
   ▼
Seleção de produções não pagas dentro de um período
   │
   ▼
Criação do pagamento (agrupa as produções selecionadas)
   │
   ▼
Pagamento pending → paid (ação manual, registra payment_date)
```

Isso permite que as produções sejam registradas individualmente, ao longo do tempo, e agrupadas posteriormente em um período para pagamento — sem que uma produção possa ser paga duas vezes, já que uma vez vinculada a um pagamento ela deixa de aparecer como pendente.

## 🎯 Objetivo do projeto

O principal objetivo do WorkFlow é transformar um processo que depende de anotações e cálculos manuais em um sistema organizado, confiável e fácil de utilizar.

Além de resolver o problema específico para o qual foi desenvolvido, o projeto também serve como aplicação prática de conceitos de desenvolvimento web com Python, incluindo:

- Arquitetura modular por domínio em Flask
- ORM com SQLAlchemy e tipos `Numeric` para valores monetários
- Repository Pattern com base compartilhada (`CommonRepository`)
- Service Layer com hierarquia de exceções própria
- DTOs com validação (`dataclasses`)
- Migrations
- Relacionamentos entre entidades (produto ↔ produção ↔ pagamento)
- JavaScript modularizado (ES Modules) para interações dinâmicas, sem recarregar a página

## 📌 Status

🚧 Em desenvolvimento

O projeto ainda está passando por mudanças na arquitetura e implementação de funcionalidades. Pontos conhecidos em aberto:

- Criação de produto (`ProductService.product_create`) ainda não implementada
- Links de "Cadastro de Preço" e "Relatórios" no menu lateral ainda não têm rota associada

Novas funcionalidades e melhorias serão adicionadas conforme o desenvolvimento avançar.

## 👨‍💻 Autor

Desenvolvido por [Olliv3r](https://github.com/Olliv3r).

## 📄 Licença

Este projeto ainda não possui uma licença definida.
