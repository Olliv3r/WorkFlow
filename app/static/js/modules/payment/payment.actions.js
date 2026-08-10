import { PaymentAPI } from "./payment.api.js"
import { PaymentUI } from "./payment.ui.js"
import { UI } from "../core/ui.js"

export const PaymentActions = {
  // Carregar historico
  async handleHistoryPartial() {
    try {
      const response = await PaymentAPI.fetch_history_partial()
      
      PaymentUI.replaceHtml("#table-history", response)
      
    } finally {
      console.log("Partial de histórico carregado")
    }
  },

  // Calcular produções
  handleUpdateSummary() {
    PaymentUI.updateSummary()
  },

  // Criar pagamento
	async handlePaymentCreate(formData) {
		UI.setLoading("#formPaymentCreate #btnCreate", true)
	
		try {
			const response = await PaymentAPI.payment_create(formData)

			if (response.status === "success") {
        this.handleHistoryPartial()
				UI.reset("#formPaymentCreate")
			}

			const color = response.status === "success" ? "success" : "danger"

			UI.showAlert("#payment_alert", color, response.message)
			
		} finally {
			UI.setLoading("#formPaymentCreate #btnCreate", false)
		}
	},

	async handleToggleStatus(payment_id, button) {
		UI.setLoading(button, true)
    let response
		
		try {
		  response = await PaymentAPI.payment_toggle_status(payment_id)
      UI.setLoading(button, false)

      const color = response.status === "success" ? "success" : "danger"
    
      UI.showAlert("#payment_status", color, response.message)
  
      PaymentUI.updateButton(
        response.payment_status, 
        response.payment_date, 
        button
      )

		} finally {
			console.log("Status updated")
		}
	}
}
