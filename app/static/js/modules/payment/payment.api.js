import { ClientAPI } from "./client.api.js"

export const PaymentAPI = {
  // Carregar partial de cards
  fetch_cards_partial() {
    return ClientAPI.get({
      url: "/payment/cards/partial"
    })
  },

  // Carregar partial de historico
  fetch_history_partial() {
    return ClientAPI.get({
      url: "/payment/history/partial"
    })
  },

  // Criar pagamento
	payment_create(formData) {
		return ClientAPI.post({
			url: "/payment/create",
			data: formData
		})
  },

  // Atualizar status do pagamento
  payment_toggle_status(paymentId) {
  	return ClientAPI.post({
  		url: `/payment/${paymentId}/toggle-status`
  	})
  },

  // Excluir pagamento
  payment_delete(paymentId) {
    return ClientAPI.post({
      url: `/payment/${paymentId}/delete`
    })
  }
}
