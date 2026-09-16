import { ClientAPI } from "../production/client.api.js"

export const PriceAPI = {
  // Carregar partial de tabela de preços
  fetch_table_partial() {
    return ClientAPI.get({
      url: "/price/table/partial"
    })
  },

  // Definir ou atualizar o preço de uma combinação produto+etapa
  set_price(formData) {
    return ClientAPI.post({
      url: "/price/set",
      data: formData
    })
  }
}
