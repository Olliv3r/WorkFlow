import { ClientAPI } from "./client.api.js"

export const ProductionAPI = {
  // Carregar partial de cards de produção
  fetch_cards_partial() {
    return ClientAPI.get({
      url: "/production/cards/partial"
    })
  },
  
  // Carregar partial de tabela de produção
  fetch_table_partial() {
    return ClientAPI.get({
      url: "/production/table/partial"
    })
  },

  // Criar produção
	create(formData) {
		return ClientAPI.post({
			url: "/production/create",
			data: formData
		})
	},
  
  // Editar produção
	edit(formData, productionId) {
		return ClientAPI.post({
			url: `/production/${productionId}/edit`,
			data: formData
		})
	},

  // Conseguir dados de produção
  fetch_data(productionId) {
    return ClientAPI.get({
      url: `/production/${productionId}/data`
    })
  },
  
  // Conseguir produçõee
  fetch_products_options() {
    return ClientAPI.get({
      url: "/product/options"
    })
  },
  
  // Conseguir etapas
  fetch_stages_options() {
    return ClientAPI.get({
      url: "/stage/options"
    })
  },
  
  // Conseguir furos
  fetch_holes_options() {
    return ClientAPI.get({
      url: "/hole/options"
    })
  }
}
