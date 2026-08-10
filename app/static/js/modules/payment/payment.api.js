import { ClientAPI } from "./client.api.js"

export const PaymentAPI = {
  fetch_history_partial() {
    return ClientAPI.get({
      url: "/payment/history/partial"
    })
  },
  
	payment_create(formData) {
		return ClientAPI.post({
			url: "/payment/create",
			data: formData
		})
  },

  payment_toggle_status(paymentId) {
  	return ClientAPI.post({
  		url: `/payment/${paymentId}/toggle-status`,
  	})
  }
}
