import { ProductionActions } from "./production.actions.js"

$(document).ready(function() {
  // Carregar partial de cards e tabela
  ProductionActions.handleLoadCardsPartial()
  ProductionActions.handleLoadTablePartial()

  // Criar produção
	$("#formNewProduction").on(
    "submit", 
    function(event) {
      event.preventDefault()

		  const formData = new FormData(this)
        ProductionActions.handleProductionCreate(formData)
	  }
  )

  // Preencher dados de produção na modal (apenas botão de editar,
  // não o de excluir — os dois compartilhavam .btn-icon-action e o
  // clique em excluir disparava esta mesma lógica sem efeito real)
  $("#production-table").on(
    "click",
    ".btn-icon-action.is-edit",
    function(event) {
      event.preventDefault()
      const productionId = $(this).data("production-id")
      ProductionActions.handleOptions(productionId)
    }
  )


  // Excluir produção
  $("#production-table").on(
    "click",
    ".btn-icon-action.is-danger",
    function(event) {
      event.preventDefault()

      const productionId = $(this).data("production-id")
      ProductionActions.handleProductionDelete(productionId, this)
    }
  )

  // Editar produção
	$("#formProductionEdit").on(
    "submit", 
    function(event) {
      event.preventDefault()

      const productionId = $(this).data("production-id")
		  const formData = new FormData(this)
        ProductionActions.handleProductionEdit(formData, productionId)
	  }
  )

  // Filtrar produções (submit de #formProductionFilter). O form é
  // GET nativo por padrão (funcionaria mesmo sem isto, com reload);
  // interceptamos para manter o padrão "sem reload" do resto do
  // sistema.
  $("#formProductionFilter").on(
    "submit",
    function(event) {
      event.preventDefault()
      ProductionActions.handleFilterProductions()
    }
  )

  // Limpar filtro — o link "Limpar" aponta para request.path (a
  // própria URL sem querystring), que funcionaria via reload nativo;
  // interceptado pelo mesmo motivo acima.
  $("#filterCard").on(
    "click",
    ".btn-filter-clear",
    function(event) {
      event.preventDefault()
      ProductionActions.handleClearFilters()
    }
  )

  // Preencher preço automaticamente ao selecionar produto ou etapa
  // no modal de nova produção (ver
  // ProductionActions.handleAutoFillPrice e o TODO que este código
  // substitui em _new_production_modal.html).
  $("#modalNewProduction").on(
    "change",
    "#newProductionProductId, #newProductionStageId",
    function() {
      ProductionActions.handleAutoFillPrice()
    }
  )
})