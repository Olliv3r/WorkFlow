import { PriceAPI } from "./price.api.js"
import { PriceUI } from "./price.ui.js"
import { UI } from "../core/ui.js"

export const PriceActions = {
  // Carregar partial de tabela de preços
  async handleLoadTablePartial() {
    try {
      const response = await PriceAPI.fetch_table_partial()
      PriceUI.replaceHtml("#price-table", response)

    } catch (error) {
      console.error(error)

    } finally {
      console.log("Partial de tabela de preços carregado")
    }
  },

  // Definir/atualizar preço
  async handleSetPrice(formData, buttonSelector = "#formSetPrice #btnSetPrice", clearMainValue = true) {
    UI.setLoading(buttonSelector, true)

    try {
      const response = await PriceAPI.set_price(formData)

      if (response.status === "success") {
        this.handleLoadTablePartial()
        // Preço definido — mantém produto e etapa selecionados (útil
        // para conferir/ajustar em sequência), limpa só o valor.
        if (clearMainValue) $("#priceValue").val("")
      }

      const color = response.status === "success" ? "success" : "danger"
      UI.showAlert("#price_alert", color, response.message)
      return response.status === "success"

    } catch (error) {
      console.error(error)
      return false

    } finally {
      UI.setLoading(buttonSelector, false)
    }
  }
}
