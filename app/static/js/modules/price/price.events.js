import { PriceActions } from "./price.actions.js"

$(document).ready(function() {
  // Carregar tabela de preços
  PriceActions.handleLoadTablePartial()

  // Abrir edição diretamente pela tabela
  $(document).on("click", ".btn-edit-price", function() {
    const button = $(this)
    $("#editPriceProductId").val(button.data("product-id"))
    $("#editPriceStageId").val(button.data("stage-id"))
    $("#editPriceProductLabel").text(button.data("product-label"))
    $("#editPriceStageLabel").text(button.data("stage-label"))
    $("#editPriceValue").val(String(button.data("price")).replace(".", ","))
    bootstrap.Modal.getOrCreateInstance(document.getElementById("modalEditPrice")).show()
  })

  $("#formEditPrice").on("submit", async function(event) {
    event.preventDefault()
    const ok = await PriceActions.handleSetPrice(new FormData(this), "#btnEditPrice", false)
    if (ok) bootstrap.Modal.getInstance(document.getElementById("modalEditPrice"))?.hide()
  })

  // Definir/atualizar preço
  $("#formSetPrice").on(
    "submit",
    function(event) {
      event.preventDefault()

      const formData = new FormData(this)
      PriceActions.handleSetPrice(formData)
    }
  )
})
