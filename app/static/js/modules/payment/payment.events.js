import { PaymentActions } from "./payment.actions.js"

$(document).ready(function() {
  // Carregar historico e calculo da produção
  PaymentActions.handleHistoryPartial()
  PaymentActions.handleUpdateSummary()

  // Calcular produção
  $(".form-check-input").on(
    "change", 
    function() {
      PaymentActions.handleUpdateSummary()
    }
  )

  // Criar pagamento
	$("#formPaymentCreate").on(
    "submit", 
    function(event) {
  		event.preventDefault()
  		const formData = new FormData(this)
  		PaymentActions.handlePaymentCreate(formData)
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