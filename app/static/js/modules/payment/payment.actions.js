import { PaymentAPI } from "./payment.api.js"
import { PaymentUI } from "./payment.ui.js"
import { UI } from "../core/ui.js"

export const PaymentActions = {
  // Carregar cards
  async handleCardsPartial() {
    try {
      const response = await PaymentAPI.fetch_cards_partial()
      
      PaymentUI.replaceHtml("#cards", response)

    } catch (error) {
      console.error(error)
      
    } finally {
      console.log("Partial de cards carregado")
    }
  },
  
  // Carregar historico
  async handleHistoryPartial() {
    try {
      const response = await PaymentAPI.fetch_history_partial()
      
      PaymentUI.replaceHtml("#table-history", response)

    } catch (error) {
      console.error(error)
      
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
        this.handleCardsPartial()
        this.handleHistoryPartial()
				UI.reset("#formPaymentCreate")
			}

			const color = response.status === "success" ? "success" : "danger"

			UI.showAlert("#payment_alert", color, response.message)

    } catch (error) {
      console.error(error)
			
		} finally {
			UI.setLoading("#formPaymentCreate #btnCreate", false)
		}
	},

  // Excluir pagamento
  async handlePaymentDelete(paymentId, button) {
    if (!confirm('Excluir este pagamento permanentemente? As produções incluídas voltam a ficar disponíveis para um novo pagamento. Esta ação não pode ser desfeita.')) {
      return
    }
    
    UI.setLoading(button, true)

    try {
      const response = await PaymentAPI.payment_delete(paymentId)
      const color = response.status === "success" ? "success" : "danger"

      if (response.status === "success") {
        this.handleHistoryPartial()
        this.handleCardsPartial()
      }

      UI.showAlert("#history_alert", color, response.message)
    	
    } catch (error) {
    	console.error(error);
      
    } finally {
      UI.setLoading(button, false)
    }
  },

  // Atualizar o status de pagamento
	async handleToggleStatus(payment_id, button) {
		UI.setLoading(button, true)
    let response
		
		try {
		  response = await PaymentAPI.payment_toggle_status(payment_id)
      UI.setLoading(button, false)

      const color = response.status === "success" ? "success" : "danger"
    
      UI.showAlert("#history_alert", color, response.message)
  
      PaymentUI.updateButton(
        response.payment_status, 
        response.payment_date, 
        button
      )
      
    } catch (error) {
      console.error(error)

		} finally {
			console.log("Status updated")
		}
	}
}
