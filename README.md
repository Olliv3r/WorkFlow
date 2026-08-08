# WorkFlow

Sistema web para gerenciamento e acompanhamento de produção, desenvolvido com Flask e SQLAlchemy.

O WorkFlow foi criado para organizar o registro da produção, produtos, materiais, valores e pagamentos em um único sistema, reduzindo controles manuais e facilitando o acompanhamento financeiro da produção.

## 🚀 Tecnologias

- Python
- Flask
- SQLAlchemy
- Flask-Migrate / Alembic
- SQLite
- Jinja2
- Bootstrap
- JavaScript / jQuery

## 📋 Funcionalidades

Produção

- Registro das produções realizadas
- Associação da produção a um produto
- Registro da quantidade produzida em dúzias
- Registro do valor por dúzia
- Cálculo do valor total da produção
- Observações sobre a produção
- Consulta do histórico de produção

## Produtos

O sistema permite cadastrar produtos a partir de suas características, evitando a necessidade de recriar as mesmas combinações durante o registro da produção.

Os produtos podem ser definidos de acordo com características como:

- Família do produto
- Material
- Qualidade
- Quantidade de furos
- Tipo de taco
- Outras características específicas

## Pagamentos

O WorkFlow também permite organizar os pagamentos com base em períodos de produção.

Um pagamento pode possuir:

- Data inicial do período
- Data final do período
- Data do pagamento
- Valor total
- Status
- Observação

O valor do pagamento é baseado nas produções pertencentes ao período selecionado.

## 🏗️ Arquitetura

O projeto utiliza uma arquitetura organizada em camadas, buscando separar responsabilidades e facilitar a manutenção do código.

Uma visão simplificada:

```html
Request
   │
   ▼
Routes / Controllers
   │
   ▼
Services
   │
   ▼
Repositories
   │
   ▼
SQLAlchemy Models
   │
   ▼
Database
```

## Responsabilidades

Routes / Controllers:

Responsáveis por receber as requisições, validar o fluxo HTTP e retornar as respostas adequadas.

Services:

Concentram as regras de negócio da aplicação.

Repositories:

Responsáveis pelo acesso aos dados e pelas operações relacionadas ao banco de dados.

Models:

Representam as entidades persistidas no banco através do SQLAlchemy.

DTOs:

Utilizados para transportar e validar dados entre as diferentes partes da aplicação.

## 📁 Estrutura

A estrutura do projeto segue uma organização semelhante a:

```bash
WorkFlow/
│
├── app/
│   ├── models/
│   ├── repositories/
│   ├── services/
│   ├── dto/
│   ├── routes/
│   ├── templates/
│   ├── static/
│   └── extensions.py
│
├── migrations/
│
├── tests/
│
├── config.py
├── run.py
├── requirements.txt
└── README.md
```
A separação por responsabilidade permite localizar mais facilmente onde uma alteração deve ser realizada.

Por exemplo:

```html
Regra de negócio
      ↓
   Service

Consulta ao banco
      ↓
  Repository

Estrutura da tabela
      ↓
    Model

Interface
      ↓
Template / JavaScript
```

## ⚙️ Instalação

Clone o repositório:

```
git clone https://github.com/Olliv3r/WorkFlow.git
cd WorkFlow
```

Crie um ambiente virtual:

```
python -m venv .venv
```

Ative o ambiente virtual.

Linux / macOS

```
source .venv/bin/activate
```

Windows

```
.venv\Scripts\activate
```

Instale as dependências:

```
pip install -r requirements.txt
```

Configure as variáveis de ambiente necessárias para o projeto.

Depois, inicialize o banco de dados/migrações conforme a configuração do projeto.

Execute a aplicação:

```
flask run
```

## 🗄️ Banco de dados

O projeto utiliza SQLAlchemy como ORM.

Durante o desenvolvimento, o banco utilizado é o SQLite.

As alterações estruturais do banco são controladas através de migrations com Alembic/Flask-Migrate.

Exemplo:
```bash
flask db migrate -m "description"
flask db upgrade
```

## 🔄 Fluxo de produção

O fluxo principal do sistema pode ser representado da seguinte maneira:

```html
Produto
   │
   ▼
Registro da produção
   │
   ├── Data
   ├── Produto
   ├── Dúzias
   ├── Valor por dúzia
   └── Observação
   │
   ▼
Produção armazenada
   │
   ▼
Seleção de produções
   │
   ▼
Período de pagamento
   │
   ▼
Total a receber
```

Isso permite que as produções sejam registradas individualmente e posteriormente agrupadas em um período para pagamento.

## 🎯 Objetivo do projeto

O principal objetivo do WorkFlow é transformar um processo que depende de anotações e cálculos manuais em um sistema organizado, confiável e fácil de utilizar.

Além de resolver o problema específico para o qual foi desenvolvido, o projeto também serve como aplicação prática de conceitos de desenvolvimento web com Python, incluindo:

- Arquitetura de aplicações Flask
- ORM com SQLAlchemy
- Repository Pattern
- Service Layer
- DTOs
- Migrations
- Relacionamentos entre entidades
- Validação de dados
- Desenvolvimento de interfaces web
- JavaScript para interações dinâmicas

## 📌 Status

🚧 Em desenvolvimento

O projeto ainda está passando por mudanças na arquitetura e implementação de funcionalidades.

Novas funcionalidades e melhorias serão adicionadas conforme o desenvolvimento avançar.

👨‍💻 Autor

Desenvolvido por Olliv3r.

📄 Licença

Este projeto ainda não possui uma licença definida.
