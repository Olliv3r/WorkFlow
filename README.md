# WorkFlow

Sistema web em **Python + Flask** para registrar produções, organizar produtos e etapas, controlar preços e fechar pagamentos de produção.

![WorkFlow — Preview do sistema](assets/preview.png)

> [!IMPORTANT]
> ## Sobre a versão da branch principal
>
> O código disponível atualmente na **branch principal do repositório** ainda representa a versão que foi desenvolvida antes da pausa do projeto e pode não conter todas as correções e funcionalidades descritas nas versões mais recentes.
>
> **Para obter a versão mais atualizada do WorkFlow, consulte a seção _Releases_ do GitHub e baixe o pacote da release mais recente.**
>
> A branch principal poderá ser sincronizada com essas versões futuramente.

## Objetivo

O WorkFlow foi criado para substituir anotações e cálculos manuais no acompanhamento de produção. O fluxo principal é simples:

```text
Produzir → Registrar → Acompanhar → Fechar pagamento → Analisar
```

O projeto continua sendo um **monólito Flask e monousuário**. A prioridade é resolver bem o processo real de produção sem transformar o sistema em um ERP genérico.

## Tecnologias

- Python
- Flask
- Flask-SQLAlchemy / SQLAlchemy
- Flask-Migrate / Alembic
- SQLite (padrão atual)
- PostgreSQL (suporte opcional via `psycopg`)
- MySQL (suporte opcional via `PyMySQL`)
- Bootstrap-Flask / Bootstrap 5
- Jinja2
- JavaScript modularizado (ES Modules)
- jQuery

## Funcionalidades atuais

### Dashboard

A página inicial apresenta uma visão resumida da produção e dos pagamentos, incluindo indicadores do período atual e atalhos para as áreas principais.

Também inclui um gráfico de **produção dos últimos 30 dias**, com os dias sem produção representados como zero para preservar a leitura real da tendência.

### Produções

Cada produção registra:

- produto;
- etapa;
- data;
- quantidade em dúzias;
- preço por dúzia;
- valor total;
- observação;
- pagamento relacionado, quando houver.

Recursos:

- criação;
- edição;
- exclusão;
- filtros por período e produto;
- histórico;
- seleção para fechamento de pagamento;
- **Ver detalhes da produção**, com produto, furos, etapa, quantidade, preço, total, observação e pagamento relacionado.

#### Integridade de produções vinculadas

Uma `Production` já vinculada a um `Payment` **não pode ser editada nem excluída**. Isso evita alterar as bases de cálculo depois que o pagamento foi fechado.

Para corrigir uma produção vinculada a um pagamento ainda pendente, o fluxo esperado é:

1. excluir/desfazer o pagamento pendente;
2. corrigir a produção;
3. criar o pagamento novamente.

### Produtos

Produtos são formados por características como:

- família;
- material;
- qualidade;
- quantidade de furos;
- tipo de taco.

O módulo permite:

- listar produtos;
- criar novos produtos;
- impedir duplicatas equivalentes;
- ativar/desativar produtos sem apagar o histórico.

> As combinações específicas de família/material/furos/taco presentes no seed **ainda não são tratadas automaticamente como regras rígidas de domínio**. Elas só devem ser bloqueadas no backend quando essas regras forem formalmente confirmadas.

### Etapas

O seed atual cadastra oito etapas:

1. Amarração
2. Enchimento
3. Pinação
4. Pentiação
5. Aparação
6. Encabação
7. Pinação do cabo
8. Acabamento

> O nome **“Pentiação”** foi mantido exatamente como está no projeto. Uma eventual alteração para “Penteação” deve ser confirmada como regra/nomenclatura do processo antes de modificar dados existentes.

### Tabela de preços

O módulo de preços relaciona:

```text
Produto + Etapa → Preço por dúzia
```

O preço usado em uma produção é congelado na própria `Production`; alterar a tabela de preços depois **não altera produções antigas**.

No cadastro de uma nova produção:

- se existir preço configurado para `produto + etapa`, o backend usa esse preço como valor vigente;
- se não existir preço configurado, o comportamento atual preservado é permitir preço manual;
- nenhum valor padrão é assumido silenciosamente.

O formulário aceita valores com ponto ou vírgula, por exemplo `2.50` e `2,50`. A normalização ocorre no backend antes da criação do `Decimal`.

> O fallback manual continua existindo por compatibilidade com o fluxo atual. Se futuramente o processo exigir que **toda** combinação possua preço cadastrado, essa regra deve ser confirmada antes de remover o fallback.

### Pagamentos

Um pagamento agrupa várias produções e registra:

- período inicial e final;
- total de dúzias;
- valor total;
- status (`pending` ou `paid`);
- data do pagamento;
- observação.

A relação atual é:

```text
Payment 1 ─────── N Production

Production.payment_id → payments.id
```

Cada `Production` possui apenas um `payment_id`, portanto pertence a no máximo um pagamento por vez.

Ao criar um pagamento, o backend:

1. recebe os IDs selecionados;
2. remove IDs duplicados;
3. busca novamente todas as produções no banco;
4. rejeita IDs inexistentes;
5. rejeita produções já vinculadas a outro pagamento;
6. recalcula `total_dozens` no servidor;
7. recalcula `total_amount` usando `dozens × price_per_dozen` persistidos;
8. cria o `Payment` e vincula as produções na mesma operação transacional.

O JavaScript não é considerado fonte confiável para os totais financeiros.

Recursos adicionais:

- períodos rápidos de fechamento;
- observação do pagamento;
- detalhes das produções que compõem cada pagamento;
- marcar como pago;
- reverter para pendente;
- excluir pagamento pendente e devolver suas produções à fila de fechamento.

A interface mantém **somente o botão de criação de pagamento no rodapé** do fluxo de seleção.

### Relatórios e Analytics

A área de relatórios permite analisar produção por:

- período;
- produto;
- etapa;
- dia.

A camada de Analytics adiciona:

- gráfico de evolução da produção ao longo do tempo, alternando entre dúzias e valor produzido;
- escala automática diária, mensal ou anual conforme o tamanho do período;
- ranking visual dos produtos mais produzidos;
- gráfico de produção por etapa;
- comparação entre o período atual e um período anterior de mesma duração;
- preenchimento explícito de períodos sem produção com valor zero, evitando tendências enganosas.

Os gráficos são renderizados localmente com JavaScript/SVG e **não dependem de CDN ou biblioteca externa de gráficos**, mantendo o WorkFlow utilizável offline.

Também há exportação para **CSV**, útil para Excel, Google Sheets, LibreOffice Calc ou análise com Python/Pandas.

### Backup

Quando o backend é SQLite, o WorkFlow oferece download direto de uma cópia do arquivo do banco.

Quando estiver conectado a PostgreSQL/MySQL, o botão de backup local é ocultado e o backup deve ser realizado pelo servidor/provedor do banco.

## Arquitetura

O projeto é organizado por módulos de domínio. Em módulos de escrita, o fluxo preferido é:

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
SQLite
```

Responsabilidades:

- **Views**: HTTP, formulários e respostas;
- **DTOs/parsers**: conversão e validação de entrada;
- **Services**: regras de negócio e integridade;
- **Repositories**: persistência e consultas;
- **Models**: estrutura persistida e relacionamentos.

As consultas analíticas do Dashboard e de Relatórios são centralizadas em `ReportService` e `ReportRepository`, mantendo as views responsáveis principalmente por HTTP e renderização.

## Estrutura resumida

```text
WorkFlow/
├── app/
│   ├── main/
│   ├── production/
│   ├── payment/
│   ├── product/
│   ├── price/
│   ├── report/
│   ├── stage/
│   ├── hole/
│   ├── seed/
│   ├── common/
│   ├── core/
│   ├── models/
│   ├── templates/
│   └── static/
├── tests/
├── migrations/
├── assets/
├── config.py
├── main.py
├── requirements.txt
├── requirements-dev.txt
├── requirements-postgresql.txt
├── requirements-mysql.txt
├── DATABASES.md
├── server.sh
└── README.md
```

## Bancos de dados

O WorkFlow continua usando **SQLite por padrão**, mas a conexão agora é configurável por `DATABASE_URL`.

### SQLite

Nenhuma configuração adicional é necessária.

### PostgreSQL

```bash
pip install -r requirements-postgresql.txt
export DATABASE_URL='postgresql://usuario:senha@host:5432/workflow'
flask db upgrade
```

### MySQL

```bash
pip install -r requirements-mysql.txt
export DATABASE_URL='mysql://usuario:senha@host:3306/workflow'
flask db upgrade
```

URLs comuns são normalizadas para os drivers suportados pelo projeto (`psycopg` e `PyMySQL`). URLs explícitas do SQLAlchemy continuam aceitas.

> A compatibilidade de conexão **não migra automaticamente o conteúdo do `dev.db`**. A transferência de dados para outro SGBD deverá ser executada e validada quando a migração realmente acontecer. Consulte [`DATABASES.md`](DATABASES.md).

### Índices para histórico longo

A migration mais recente adiciona índices para as principais consultas históricas em:

- `Production.date`;
- `Production.product_id`;
- `Production.stage_id`;
- `Production.payment_id`;
- datas e status de `Payment`.

Esses índices não alteram regras nem valores; existem para manter relatórios eficientes conforme o histórico crescer.

## Instalação

```bash
git clone https://github.com/Olliv3r/WorkFlow.git
cd WorkFlow
python -m venv .venv
```

Linux / Termux / macOS:

```bash
source .venv/bin/activate
```

Windows:

```powershell
.venv\Scripts\activate
```

Instale as dependências:

```bash
pip install -r requirements.txt
```

Aplique as migrations quando necessário:

```bash
flask db upgrade
```

Popule um banco vazio com os dados iniciais:

```bash
./server.sh seed
```

Execute:

```bash
./server.sh flask run --debug
```

> `server.sh` usa por padrão o ambiente virtual configurado na variável `VENV`. Ajuste esse caminho ao seu ambiente local se necessário.

## Testes

A versão atual inclui testes automatizados para:

- seed em banco vazio e idempotência de `create_stages()`;
- parsing de datas;
- valores monetários com `2.50`, `2,50`, vazio, texto, zero e negativo;
- criação de produção;
- edição de produção;
- edição e validação da data;
- exclusão;
- bloqueio de edição/exclusão quando já há pagamento;
- uso do preço configurado no backend na criação;
- fallback manual quando não existe preço configurado;
- criação de pagamentos em intervalos semanais, quinzenais e mensais;
- tentativa de pagamento duplicado;
- recálculo de dúzias e valores no backend;
- filtros rápidos de pagamento;
- presença das principais telas;
- ausência do antigo botão superior de pagamento.

Instale as dependências de desenvolvimento:

```bash
pip install -r requirements-dev.txt
```

Execute:

```bash
python -m pytest -q
```

Ou execute a verificação de release, que também valida a sintaxe Python e os módulos JavaScript principais:

```bash
./scripts/verify_release.sh
```

## Seed

O seed completo executa, nesta ordem:

```text
Famílias
→ Materiais
→ Qualidades
→ Furos
→ Tipos de taco
→ Etapas
→ Produtos
```

O `stage_repository` utilizado por `SeedService.create_stages()` é importado de `app.stage.repositories`, onde a instância é exposta pelo `__init__.py`.

## Decisões que ainda precisam de confirmação de domínio

As seguintes mudanças **não foram impostas automaticamente** nesta versão:

- restringir combinações permitidas da família Inovada;
- restringir combinações da Capa quadrada;
- definir todas as combinações válidas de PET, Náilon e Cipó;
- transformar o conteúdo do seed em regra rígida de validação;
- remover totalmente o preço manual quando não existe preço cadastrado;
- renomear “Pentiação”;
- adicionar novas etapas apenas porque estavam planejadas.

Essas decisões devem ser confirmadas com base no processo real antes de virar validação de backend.

## Estado da versão

A linha de desenvolvimento desta atualização reforça primeiro integridade e testes antes de adicionar mais funcionalidades.

Para acompanhar os itens auditados e os pontos ainda pendentes, consulte `CHECKLIST_v0.0.3.md` incluído no pacote da release.

## Releases

**A versão mais atualizada é distribuída pela seção Releases.** Enquanto a branch principal não for sincronizada, baixar/clonar apenas `main` pode entregar uma versão anterior à apresentada neste README.

## Licença

Consulte o arquivo de licença do repositório, quando presente, para as condições de uso e distribuição.
