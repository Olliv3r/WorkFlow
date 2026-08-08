import { ClientAPI } from "./client.api.js"

export const ProductionAPI = {
	production_create(formData) {
		return ClientAPI.post({
			url: "/production/create",
			data: formData
		})
	}
}
