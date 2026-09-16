import { ClientAPI } from "./client.api.js"

// Mesma constatação testada em production.api.js: com
// processData:false/contentType:false, o jQuery não serializa um
// objeto `data` na querystring, nem em GET — a query precisa ser
// montada manualmente e anexada na url.
function buildQuery(params) {
  const parts = Object.entries(params)
    .filter(([, value]) => value !== undefined && value !== null && value !== "")
    .map(([key, value]) => `${encodeURIComponent(key)}=${encodeURIComponent(value)}`)
  return parts.length ? `?${parts.join("&")}` : ""
}

export const PaymentAPI = {
  // Carregar partial de cards — filters é opcional
  // ({start_date, end_date}), usado pelo filtro da página.
  fetch_cards_partial(filters = {}) {
    return ClientAPI.get({
      url: `/payment/cards/partial${buildQuery(filters)}`
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
