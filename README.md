# Ficha de Produção

Formulário de registro de produção com cálculo automático de valor por
dúzia, persistido em SQLite via Flask.

## Como rodar

```bash
pip install -r requirements.txt --break-system-packages
python init_db.py
python app.py
```

Depois abra `http://localhost:5000` no navegador. Enquanto o processo
`python app.py` estiver rodando em um terminal, o formulário funciona.
Se você fechar o terminal ou matar o processo, o formulário para de
responder — os dados já salvos continuam intactos no arquivo
`producao.db`, mas você precisa rodar `python app.py` de novo para
acessá-los.

Em Termux, o comando é o mesmo. Se quiser acessar de outro
dispositivo na mesma rede (celular acessando o servidor rodando no
PC, por exemplo), troque `localhost` pelo IP da máquina que está
rodando o Flask.

## Primeiro uso

Rode `python init_db.py` antes de `python app.py` na primeira vez.
Isso cria o banco já com:

- Os 4 materiais: Pete, Cipó, Nailon, Piaçaba
- As 9 etapas do processo: Amarrar, Encher, Pinar, Pentear, Aparar
  pontas, Pintar, Encabar, Pinar cabo, Plugar
- 4 preços já preenchidos — Pete R$5,00, Cipó R$3,00, Nailon R$3,00,
  Piaçaba R$2,00, todos para tacos de **20 furos**

Rodar `python init_db.py` mais de uma vez é seguro — não duplica
nada nem apaga registros já salvos.

Se você pular esse passo e rodar `python app.py` direto na primeira
vez, o banco nasce vazio (sem materiais, etapas ou preços) e você
precisa cadastrar tudo manualmente pela tela.

## Como o preço funciona (leia antes de usar)

**O preço por dúzia depende só de Material + Quantidade de furos do
taco — a Etapa/Função realizada NÃO afeta o valor.** Amarrar 5 dúzias
de Pete com 20 furos custa o mesmo por dúzia que Pentear 5 dúzias de
Pete com 20 furos. A etapa é só o rótulo de "o que foi feito" no
registro — não entra no cálculo.

**Furos é uma lista fechada de 4 valores exatos: 16, 20, 22, 30.**
Não existe "20 ou mais" — são 4 quantidades específicas, cada uma com
seu próprio preço por material. Se algum dia aparecer uma quantidade
de furos fora dessas 4, o sistema vai rejeitar o registro; a lista
está fixada no código (`FUROS_VALIDOS` em `app.py`) e precisa ser
editada manualmente se isso mudar.

**Ao registrar produção, você escolhe Etapa + Material + Furos.** Só
Material e Furos determinam o preço:

- Se a combinação **já tem preço** cadastrado, o campo "Valor por
  dúzia" se preenche sozinho — mas continua editável. Você pode
  sobrescrever ali mesmo a qualquer momento.
- Se a combinação **ainda não tem preço**, o campo aparece vazio e
  destacado, pedindo que você digite o valor antes de salvar.
- **Em ambos os casos, o que você digitar no formulário principal
  também atualiza a tabela de preços** — da próxima vez que essa
  combinação aparecer (mesmo em outro dia), o valor já vem
  preenchido automaticamente.

**Atenção:** como o valor pode ser sobrescrito a qualquer momento
direto no formulário principal, um erro de digitação ali (ex:
R$50,00 em vez de R$5,00) muda o preço daquela combinação
permanentemente, sem confirmação extra — até você notar e corrigir.
Isso foi uma escolha deliberada para manter o fluxo rápido; se
preferir uma confirmação antes de mudanças bruscas de valor, é um
ajuste a pedir depois.

## Decisões de schema que você precisa saber

- **O valor de cada registro é congelado no momento em que ele é
  criado.** Se você editar o preço de Pete/20furos depois (de R$5,00
  para R$6,00), os registros antigos continuam valendo R$5,00 — eles
  não recalculam. Histórico financeiro não muda retroativamente
  quando você reajusta um preço no presente.

- **"Pinar" e "Pinar cabo" são etapas diferentes, de propósito.**
  "Pinar" fixa o pino no corpo do produto, depois de Amarrar e
  Encher. "Pinar cabo" fixa o pino que prende o cabo já pronto ao
  corpo montado. Cada uma tem uma descrição cadastrada (visível no
  select do formulário e na aba "Etapas do processo") para reduzir o
  risco de selecionar a errada.

- **Excluir uma Etapa ou um Material que já foi usado em algum
  registro não apaga de verdade** — o sistema desativa
  automaticamente (some das opções do formulário, mas continua
  aparecendo marcado como "Inativo" na tela de gerenciamento). Isso
  evita quebrar a referência dos registros antigos.

- **Quantidade é em dúzias, aceita decimais** (ex: `2.5` = duas
  dúzias e meia).

- **O campo Data controla qual "dia" o resumo da diária (barra no
  topo) está somando.** Mudar a data no formulário recalcula o
  resumo para aquele dia específico — não é um total geral.

- **Data, Período, Material e Furos permanecem preenchidos depois de
  salvar um registro** — só Tipo de produto, Quantidade e Etapa são
  limpos. Isso existe porque seu uso típico é registrar vários
  produtos seguidos no mesmo dia, muitas vezes com o mesmo material
  e mesma quantidade de furos, passando por etapas diferentes.

## O que ainda não existe

- Autenticação — qualquer um com acesso à URL vê e edita tudo.
  Irrelevante se só você usa isso na sua própria máquina; relevante
  se for exposto em rede compartilhada.
- Backup automático do `producao.db`. É um arquivo único no disco —
  faça cópia dele periodicamente se os dados importam de verdade.
- Confirmação antes de sobrescrever um preço já existente com um
  valor muito diferente (ex: dobrar ou reduzir à metade sem querer).
- Relatório por semana/quinzena/mês/ano agregando o campo "Período
  de referência" — hoje esse campo só fica salvo por registro, mas
  não existe uma tela que soma "todos os registros da quinzena X".
  O resumo automático que existe hoje é só por dia.
