# Bancos de dados no WorkFlow

O WorkFlow usa SQLAlchemy e mantém **SQLite como banco padrão**, mas a aplicação também está preparada para receber uma URL de PostgreSQL ou MySQL através de `DATABASE_URL`.

> Esta atualização adiciona compatibilidade de conexão. Ela **não transfere automaticamente os dados do `dev.db` para outro banco**. A migração dos dados deve ser feita separadamente quando for necessária.

## SQLite — padrão atual

Sem definir `DATABASE_URL`, o sistema usa:

```text
sqlite:///.../dev.db
```

Nenhuma configuração adicional é necessária.

## PostgreSQL

Instale o driver opcional:

```bash
pip install -r requirements-postgresql.txt
```

Configure a conexão:

```bash
export DATABASE_URL='postgresql://usuario:senha@host:5432/workflow'
```

O WorkFlow normaliza essa URL para o driver `psycopg` usado pelo SQLAlchemy.

Também é possível informar explicitamente:

```bash
export DATABASE_URL='postgresql+psycopg://usuario:senha@host:5432/workflow'
```

Depois, em um banco vazio:

```bash
flask db upgrade
./server.sh seed
```

## MySQL

Instale o driver opcional:

```bash
pip install -r requirements-mysql.txt
```

Configure:

```bash
export DATABASE_URL='mysql://usuario:senha@host:3306/workflow'
```

O WorkFlow converte essa URL para `mysql+pymysql://...`.

Também é possível informar explicitamente:

```bash
export DATABASE_URL='mysql+pymysql://usuario:senha@host:3306/workflow'
```

Em um banco vazio:

```bash
flask db upgrade
./server.sh seed
```

## Migrations

O schema continua sendo controlado por **Flask-Migrate/Alembic**. Isso é importante para que futuras mudanças de estrutura possam ser aplicadas tanto no SQLite quanto em bancos servidor.

Use:

```bash
flask db upgrade
```

antes de iniciar uma versão que contenha novas migrations.

## Backup

O botão **Baixar backup** do WorkFlow copia diretamente o arquivo `.db` e, portanto, só aparece quando o backend é SQLite.

Em PostgreSQL/MySQL, backup é responsabilidade do servidor/provedor do banco, por exemplo com ferramentas do próprio SGBD ou snapshots do serviço hospedado.

## Migração futura do SQLite

Quando chegar a hora de migrar o histórico existente, o fluxo recomendado será:

```text
1. Fazer backup do dev.db
2. Criar o banco PostgreSQL/MySQL
3. Executar flask db upgrade no destino
4. Transferir e validar os dados
5. Comparar contagens e totais financeiros
6. Alterar DATABASE_URL
7. Só então colocar o novo banco em uso
```

Não descarte o SQLite antigo até a validação completa dos dados migrados.
