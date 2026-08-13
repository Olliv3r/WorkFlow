import { ProductionAPI } from "./production.api.js"
import { ProductionUI } from "./production.ui.js"
import { UI } from "../core/ui.js"

export const ProductionActions = {
  // Carrregar partial de cards de produção
  async handleLoadCardsPartial() {
    try {
  	  const response = await ProductionAPI.fetch_cards_partial()
      ProductionUI.replaceHtml("#production-cards", response)
      
    } catch (error) {
      console.erro(error)
      
    } finally {
    	console.log("Partial de cards de produção carregado")
    }
  },
  
  // Carrregar partial de tabela de produção
  async handleLoadTablePartial() {
    try {
  	  const response = await ProductionAPI.fetch_table_partial()
      ProductionUI.replaceHtml("#production-table", response)
      
    } catch (error) {
      console.erro(error)
      
    } finally {
    	console.log("Partial de tabela de produção carregado")
    }
  },

  // Criar produção
	async handleProductionCreate(formData) {
		UI.setLoading("#formNewProduction #btnCreate", true)
	
		try {
			const response = await ProductionAPI.create(formData)

			if (response.status === "success") {
				UI.reset("#formNewProduction")
        this.handleLoadCardsPartial()
        this.handleLoadTablePartial()
			}

			const color = response.status === "success" ? "success" : "danger"

			UI.showAlert("#production-alert", color, response.message)
			
		} finally {
			UI.setLoading("#formNewProduction #btnCreate", false)
		}
	},

  // Conseguir dados de produção  
  async handleGetData(productionId) {
    try {
      const response = await ProductionAPI.fetch_data(productionId)
      UI.fillFormFields("#formProductionEdit", response.production)
      
    } catch (error) {
    	console.error(error)
      
    } finally {
    	console.log("Dados de produção carregados")
    }
  },

  async handleOptions(productionId) {
    try {
    	const [
        production_res,
        product_res, 
        stage_res
      ] = await Promise.all([
        ProductionAPI.fetch_data(productionId),
        ProductionAPI.fetch_products_options(),
        ProductionAPI.fetch_stages_options(),
      ])

      const s_product = $("#product_id")
      const s_stage = $("#stage_id")
      
      UI.populateSelect(
        s_product, 
        product_res.products, 
        production_res.production.product_id,
        true
      )
      UI.populateSelect(
        s_stage,
        stage_res.stages, 
        production_res.production.stage_id,
        true
      )
      UI.fillFormFields(
        "#formProductionEdit", 
        production_res.production
      )
      
    } catch (error) {
    	console.error(error)
      
    } finally {
    	console.log("Opções carregadas")
    }
  }
}
