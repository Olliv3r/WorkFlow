#!/bin/bash
# server.sh - Este program é um CLI wrapper em bash pra gerenciar o ciclo de vida de um app Flask dentro de um ambiente virtual Python isolado (~/toolmux-venv). Ele resolve um problema específico: evitar que o usuário precise digitar o caminho completo do venv toda vez que quiser rodar flask, e empacota duas operações do dia a dia — reset de migrações e execução de scripts dentro do contexto da aplicação.
#
# Site		: https://toolmux.pythonanywhere.com
# Autor 	: Olliv3r <oliveobom100@gmail.com>
# Manutenção	: Olliv3r <oliveobom100@gmail.com>
#
# Exemplos:
#
# $ ./server.sh flask run --debug
# $ ./server.sh context-run script.py
# $ ./server.sh reset
#
# Histórico:
#
# v0.0.1 2026-07-05, Olliv3r:
# 	- Adicionado suporte para apagar e criar migrações
# v0.0.2 2026-07-10, Olliv3r:
# 	- Adicionado suporte para gerenciar o ciclo de vida de um app Flask
# v0.0.3 2026-07-15, Olliv3r:
# 	- Adicionado suporte para executar scripts dentro do contexto do Flask
# v0.0.4 2026-07-20, Olliv3r:
# 	- Adicionado suporte para popular o banco de dados
# v0.0.5 2026-07-26, Olliv3r:
# 	- Adicionado suporte para repassar comandos para o python
#
#

export FLASK_APP=main  # Ponto de entrada (editável)

VENV=~/venv-wf/bin     # Ambiente virtual python (editável)
DB="dev.db"                 # Arquivo SQLITE (editável)
DIR_SEED="app/seed/seed.py" # Arquivo que popula o banco (editável)

# Cores
W="\e[0m"
R="\e[1;31m"
G="\e[1;32m"
Y="\e[1;33m"
B="\e[1;34m"
C="\e[1;35m"
M="\e[1;36m"

# Chaves de ativar funções
key_reset=0
key_seed=0

# Imprime a versão mais recente
showVersion() {
  local version=$(grep "^# v" "$0" | \
    cut -d " " -f2 | \
    tr -d "v" | tail -1)

  echo -e "Versão $version"
}

# Executa o Flask em um ambiente python isolado
flask() { "$VENV/flask" "$@"; }

# Executa comandos do Flask com menos repetição
flask_db() { flask db "$@" ;}

# Executa o servidor flask
run() { flask run "$@"; }

resetMigrations() {
  flask_db init
  flask_db migrate -m "Migrations initialized"
  flask_db upgrade
}

# Apaga e cria migrações
reset() {
  local force=0

  for arg in "$@"; do
    case "$arg" in
      --force) force=1;;
      *)
        echo "Opção inválida"
        force=0; verbose=0
	exit 0
	;;
    esac
  done

  if [ $force -ne 1 ]; then
    echo -ne "\n${R} ! ${W}Ação destrutiva (${R}PERIGOSO${W}) - ${G}ENTER ${W}pra continuar ou ${G}CTRL + C ${W}para cancelar...\n\n"
    read
  fi

  rm -rf migrations/ "$DB"
   
  resetMigrations
  return 0
}

# Constroi o script temporário para rodar no contexto do Flask
build_context_wrapper() {
  local script="$1"
  local temp=$(mktemp "./temp_XXXXXX.py")

  cat > "$temp" <<EOF
from app import create_app

app = create_app()

with app.app_context():
EOF

  sed 's/^/    /g' "$script" >> "$temp"
  echo "$temp"
}

# Popular banco com dados
seed() {
  local script="$DIR_SEED"
   
  if [ ! -f "$script" ]; then
	echo -e " ${R}! ${W}Erro: script ${Y}$script ${W}não encontrado.${W}" >&2
	return 1
  fi
  
  local temp=$(build_context_wrapper "$script") || return 1
  
  "$VENV/python" "$temp"
  rm -r "$temp"
}

# Executa comandos python
python() {
  "$VENV/python" "$@"
}

# Extrai requisitos de um ambiente virtual python
freeze() {
  "$VENV/pip" freeze > requirements.txt
}

# Executa o script temporário no contexto do Flask
context_run() {
  local script="$1"

  if [ ! -f "$script" ]; then
    echo -e " ${R}! ${W}Erro: script ${Y}$script ${W}não encontrado." >&2
    return 1
  fi

  local temp=$(build_context_wrapper "$script") || return 1
  "$VENV/python" "$temp"
  rm -r "$temp"
}

# Exibe auto ajuda
help_show() {
  echo -e "./$(basename "$0") <comando> <argumentos>\n"
  printf "  %-22s %s\n" "help, -h, --help" "Exibe uma tela de ajuda e sai"
  printf "  %-22s %s\n" "version, -v, --version" "Exibe a versão mais recente do programa"
  printf "  %-22s %s\n" "reset <options>" "Apaga migrações e cria novas (processo perigoso)"
  printf "  %-22s %s\n" "flask <args>" "Repassa comando para o flask do ambiente virtual python"
  printf "  %-22s %s\n" "context-run" "Executa script dentro do contexto da aplicação"
  printf "  %-22s %s\n" "seed" "Popula o banco de dados"
  printf "  %-22s %s\n" "python <args>" "Repassa o comando para o python do ambiente virtual python"
  printf "  %-22s %s\n" "freeze" "Gere uma lista de requisitos (requirements.txt)"
  printf "  %-22s %s\n" "run" "Executa o servidor Flask (equivalente ao flask run)"
}

# Verificar se executou o programa sem parâmetros
if [ -z "$1" ]; then
  help_show
  exit 1
fi

# Tratar opções
while [ -n "$1" ]; do
  case "$1" in
    -v|--version|version) showVersion; break;;
    flask)
      shift
      flask "$@"; break;;

    reset) key_reset=1 ;;

    run) run "$@"; break;;

    seed) key_seed=1;;
    
    python)
      shift
      python "$@"; break;;
  
    freeze) freeze; break;;
    
    context-run)
      shift
      script="$1"

      if [ -z "$script" ]; then
          echo "Erro: necessita do script para executar no contexto."
          exit 1
      fi
      context_run "$script"
      break
      ;;
  
    -h|--help|help) help_show; break;;
    *)
      echo "Erro: opção $1 inválida."
      exit 1
    ;;
  esac
  shift
done

# Verificar funcionalidades
[ $key_reset -eq 1 ] && reset "$@"
[ $key_seed -eq 1 ] && seed
