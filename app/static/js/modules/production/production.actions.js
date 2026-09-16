import { ProductionAPI } from "./production.api.js"
import { ProductionUI } from "./production.ui.js"
import { UI } from "../core/ui.js"

// Lê o estado atual do form de filtro (#formProductionFilter) e
// devolve só os campos preenchidos — usado tanto no carregamento
// inicial (para refletir uma URL com querystring já presente, ex.
// after um reload) quanto a cada novo filtro aplicado.
function readProductionFilters() {
  const $form = $("#formProductionFilter")
  if (!$form.length) return {}

  return {
    start_date: $form.find("[name='start_date']").val() || undefined,
    end_date: $form.find("[name='end_date']").val() || undefined,
    product_id: $form.find("[name='product_id']").val() || undefined,
  }
}

export const ProductionActions = {
  // Carrregar partial de cards de produção
  async handleLoadCardsPartial(filters = readProductionFilters()) {
    try {
  	  const response = await ProductionAPI.fetch_cards_partial(filters)
      ProductionUI.replaceHtml("#production-cards", response)
      
    } catch (error) {
      console.error(error)
      
    } finally {
    	console.log("Partial de cards de produção carregado")
    }
  },
  
  // Carrregar partial de tabela de produção
  async handleLoadTablePartial(filters = readProductionFilters()) {
    try {
  	  const response = await ProductionAPI.fetch_table_partial(filters)
      ProductionUI.replaceHtml("#production-table", response)
      
    } catch (error) {
      console.error(error)
      
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
        // form.reset() nativo NÃO limpa a propriedade readOnly setada
        // via JS em handleAutoFillPrice — sem isto, criar uma
        // produção com preço automático deixaria o campo travado
        // (readonly, vazio) na próxima abertura do modal.
        $("#newProductionPrice").prop("readonly", false)
        $("#newProductionPriceHint").addClass("d-none")
        this.handleLoadCardsPartial()
        this.handleLoadTablePartial()
			}

			const color = response.status === "success" ? "success" : "danger"

			UI.showAlert("#production-alert", color, response.message)
			
		} finally {
			UI.setLoading("#formNewProduction #btnCreate", false)
		}
	},

  // Carrega dados padrão ao editar
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
        product_res.data, 
        production_res.data.product_id,
        true
      )
      UI.populateSelect(
        s_stage,
        stage_res.data, 
        production_res.data.stage_id,
        true
      )
      UI.fillFormFields(
        "#formProductionEdit", 
        production_res.data
      )
      
      ProductionUI.setAttr(
        "#formProductionEdit", 
        "data-production-id", 
        production_res.data.id
      )
      
    } catch (error) {
    	console.error(error)
      
    } finally {
    	console.log("Opções carregadas")
    }
  },

  // Editar produção
	async handleProductionEdit(formData, productionId) {
		UI.setLoading("#formProductionEdit #btnEdit", true)
    
		try {
			const response = await ProductionAPI.edit(formData, productionId)

			if (response.status === "success") {
        this.handleLoadCardsPartial()
        this.handleLoadTablePartial()
			}

			const color = response.status === "success" ? "success" : "danger"

			UI.showAlert("#production-edit-alert", color, response.message)
			
		} finally {
			UI.setLoading("#formProductionEdit #btnEdit", false)
		}
	},

  // Excluir produção
  async handleProductionDelete(productionId, button) {
    if (!confirm('Excluir esta produção permanentemente? Esta ação não pode ser desfeita.')) {
      return
    }

    UI.setLoading(button, true)

    try {
      const response = await ProductionAPI.delete(productionId)
      const color = response.status === "success" ? "success" : "danger"

      if (response.status === "success") {
        this.handleLoadCardsPartial()
        this.handleLoadTablePartial()
      }

      UI.showAlert("#production_alert", color, response.message)

    } catch (error) {
      console.error(error)

    } finally {
      UI.setLoading(button, false)
    }
  },

  // Aplicar o filtro de produções (submit de #formProductionFilter).
  // Não navega — busca os partials de novo com o filtro atual, sem
  // reload. A URL não é atualizada com a querystring (diferente de
  // um GET nativo), então recarregar a página manualmente perde o
  // filtro; isso é aceitável para o escopo desta implementação.
  handleFilterProductions() {
    const filters = readProductionFilters()
    this.handleLoadCardsPartial(filters)
    this.handleLoadTablePartial(filters)
  },

  // Limpar o filtro (clique no link "Limpar"). Reseta os campos do
  // form e recarrega sem nenhum filtro — sem reload de página.
  handleClearFilters() {
    $("#formProductionFilter")[0].reset()
    this.handleLoadCardsPartial({})
    this.handleLoadTablePartial({})
  },


  // Consultar o preço vigente para a combinação produto+etapa
  // selecionada no modal de nova produção, e preencher
  // newProductionPrice automaticamente quando encontrado. Ver
  // app/templates/production/_new_production_modal.html — o TODO
  // que descrevia este comportamento antes de ser implementado.
  async handleAutoFillPrice() {
    const productId = $("#newProductionProductId").val()
    const stageId = $("#newProductionStageId").val()
    const $price = $("#newProductionPrice")
    const $hint = $("#newProductionPriceHint")

    if (!productId || !stageId) {
      $price.prop("readonly", false)
      $hint.addClass("d-none")
      return
    }

    try {
      const response = await ProductionAPI.fetch_current_price(productId, stageId)

      if (response.status === "success" && response.found) {
        $price.val(response.price_per_dozen).prop("readonly", true)
        $hint.removeClass("d-none")
      } else {
        // Sem preço cadastrado para esta combinação — fallback para
        // digitação manual, não é um erro.
        $price.prop("readonly", false).val("")
        $hint.addClass("d-none")
      }

    } catch (error) {
      console.error(error)
      // Em caso de falha na consulta, não bloquear o usuário — libera
      // o campo para digitação manual em vez de deixá-lo travado.
      $price.prop("readonly", false)
      $hint.addClass("d-none")
    }
  }
}
