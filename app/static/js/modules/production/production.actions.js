import { ProductionAPI } from "./production.api.js"
import { UI } from "../core/ui.js"

export const ProductionActions = {
	async handleProductionCreate(formData) {
		UI.setLoading("#formProductionAdd #btnAdd", true)
	
		try {
			const response = await ProductionAPI.production_create(formData)

			if (response.status === "success") {
				UI.reset("#formProductionAdd")
			}

			const color = response.status === "success" ? "success" : "danger"

			UI.showAlert("#production_alert", color, response.message)
			
		} finally {
			UI.setLoading("#formProductionAdd #btnAdd", false)
		}
	}
}
