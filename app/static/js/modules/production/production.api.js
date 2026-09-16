import { ClientAPI } from "./client.api.js"

// ClientAPI usa processData:false/contentType:false (padrão pensado
// para POST de FormData) — testado isoladamente: com processData:false,
// o jQuery NÃO serializa um objeto passado em `data` na querystring,
// nem em GET. Por isso os métodos com filtro montam a query string
// manualmente e anexam na própria url, em vez de usar `data`.
function buildQuery(params) {
  const parts = Object.entries(params)
    .filter(([, value]) => value !== undefined && value !== null && value !== "")
    .map(([key, value]) => `${encodeURIComponent(key)}=${encodeURIComponent(value)}`)
  return parts.length ? `?${parts.join("&")}` : ""
}

export const ProductionAPI = {
  // Carregar partial de cards de produção — filters é opcional
  // ({start_date, end_date, product_id}), usado pelo filtro da página.
  fetch_cards_partial(filters = {}) {
    return ClientAPI.get({
      url: `/production/cards/partial${buildQuery(filters)}`
    })
  },
  
  // Carregar partial de tabela de produção — mesmo princípio acima
  fetch_table_partial(filters = {}) {
    return ClientAPI.get({
      url: `/production/table/partial${buildQuery(filters)}`
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

  // Excluir produção
  delete(productionId) {
    return ClientAPI.post({
      url: `/production/${productionId}/delete`
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
  },

  // Consultar preço vigente para uma combinação produto+etapa —
  // usado para preencher price_per_dozen automaticamente no modal de
  // nova produção. Retorna {status, found, price_per_dozen}; found
  // false não é erro, é "sem preço cadastrado, digite manualmente".
  fetch_current_price(productId, stageId) {
    return ClientAPI.get({
      url: `/price/current${buildQuery({ product_id: productId, stage_id: stageId })}`
    })
  }
}
