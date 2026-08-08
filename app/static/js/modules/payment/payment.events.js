import { PaymentActions } from "./payment.actions.js"

$(document).ready(function() {
  PaymentActions.handleUpdateSummary()

  $(".form-check-input").on(
    "change", 
    function() {
      PaymentActions.handleUpdateSummary()
    }
  )

	$("#formPaymentCreate").on(
    "submit", 
    function(event) {
  		event.preventDefault()
  		const formData = new FormData(this)
  		PaymentActions.handlePaymentCreate(formData)
  	}
  )

  // Atualizar o status de pagamento
	$(".btn-toggle-status").on(
    "click",
    function(event) {
	    event.preventDefault()
	    const paymentId = $(this).data("payment-id")
	    PaymentActions.handleToggleStatus(paymentId, this)
	  }
  )
})