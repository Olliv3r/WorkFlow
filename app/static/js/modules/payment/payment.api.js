import { ClientAPI } from "./client.api.js"

export const PaymentAPI = {
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
