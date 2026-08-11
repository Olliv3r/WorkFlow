import { PaymentActions } from "./payment.actions.js"

$(document).ready(function() {
  // Carregar cards, historico e calculo da produção
  PaymentActions.handleCardsPartial()
  PaymentActions.handleHistoryPartial()
  PaymentActions.handleUpdateSummary()

  // Calcular produção
  $("#cards").on(
    "change", 
    ".form-check-input",
    function() {
      PaymentActions.handleUpdateSummary()
    }
  )

  // Criar pagamento
	$("#cards").on(
    "submit", 
    "#formPaymentCreate", 
    function(event) {
  		event.preventDefault()
  		const formData = new FormData(this)
  		PaymentActions.handlePaymentCreate(formData)
  	}
  )

  // Excluir um pagamento
  $("#table-history").on(
    "click",
    ".btn-delete-payment",
    function(event) {
      event.preventDefault()
      const paymentId = $(this).data("payment-id")
      PaymentActions.handlePaymentDelete(paymentId, this)
    }
  )

  // Atualizar o status de pagamento
	$("#table-history").on(
    "click", 
    ".btn-toggle-status",
    function(event) {
	    event.preventDefault()
	    const paymentId = $(this).data("payment-id")
	    PaymentActions.handleToggleStatus(paymentId, this)
	  }
  )
})