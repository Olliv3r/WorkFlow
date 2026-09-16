import { PaymentAPI } from "./payment.api.js"
import { PaymentUI } from "./payment.ui.js"
import { UI } from "../core/ui.js"

// Lê o estado atual do form de filtro (#formPaymentFilter) — mesmo
// princípio de production.actions.js:readProductionFilters().
function readPaymentFilters() {
  const $form = $("#formPaymentFilter")
  if (!$form.length) return {}

  return {
    start_date: $form.find("[name='start_date']").val() || undefined,
    end_date: $form.find("[name='end_date']").val() || undefined,
  }
}

export const PaymentActions = {
  // Carregar cards
  async handleCardsPartial(filters = readPaymentFilters()) {
    try {
      const response = await PaymentAPI.fetch_cards_partial(filters)
      
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
	},

  // Aplicar o filtro de período (submit de #formPaymentFilter). Só
  // recarrega os cards (produções disponíveis para novo pagamento) —
  // o histórico de pagamentos já criados não é afetado por este
  // filtro, que é sobre produções ainda não pagas.
  handleFilterPayments() {
    const filters = readPaymentFilters()
    this.handleCardsPartial(filters)
  },

  handleQuickPeriod(quick) {
    if (quick === "all") {
      $("#formPaymentFilter")[0].reset()
      this.handleCardsPartial({})
      return
    }
    this.handleCardsPartial({ quick })
  },

  // Limpar filtro
  handleClearPaymentFilters() {
    $("#formPaymentFilter")[0].reset()
    this.handleCardsPartial({})
  }
}
