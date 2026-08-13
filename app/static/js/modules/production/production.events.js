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

  // Preencher dados de produção na modal
  $("#production-table").on(
    "click",
    ".btn-icon-action",
    function(event) {
      event.preventDefault()

      const productionId = $(this).data("production-id")
      ProductionActions.handleOptions(productionId)
      //ProductionActions.handleGetData(productionId)
    }
  )
})