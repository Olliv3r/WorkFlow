import { ProductionActions } from "./production.actions.js"

$(document).ready(function() {
	$("#formProductionAdd").on("submit", function(event) {
		event.preventDefault()

		const formData = new FormData(this)

		ProductionActions.handleProductionCreate(formData)
	})
})
