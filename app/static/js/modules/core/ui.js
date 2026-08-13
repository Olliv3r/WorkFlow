export const UI = {
  setLoading(selector, isLoading) {
    const $button = $(selector);
    
    if (isLoading) {
      $button.data("content", $button.html());
      $button
        .prop("disabled", true)
        .html(`
          <span class="spinner-border spinner-border-sm me-1"></span> 
          Processando...
        `);
    } else {
      $button
        .prop("disabled", false)
        .html($button.data("content"));
    }
  },

  showAlert(selector, type, text) {
    $(selector)
      .addClass(`alert alert-${type}`)
      .text(text)
      .removeClass("d-none");

    // Esconder alerta apôs os 6 segundos
    setTimeout(() => {
      this.hideAlert(selector, type);
    }, 6000);
  },

  hideAlert(selector, type) {
    $(selector)
      .addClass("d-none")
      .text("")
      .removeClass(`alert alert-${type}`);
  },

  clearInput(inputEl) {
    $(inputEl).val("")
  },

  reset(formSelector) {
    $(formSelector)[0].reset();
  },

  // Montar um select 
  populateSelect(
    selectId,
    data, 
    defaultId=null, 
    includeEmptyOption=false
  ) {
    const select = $(selectId).empty()
  
    if(includeEmptyOption) {
      select.append($("<option>", {
        value: "",
        text: "Selecione uma opção",
        disabled: true,
        selected: !defaultId
      }))
    }
    
    const options = data.map(item => 
      $("<option>", {
        value: item.id,
        text: item.entity !== "stage" ? `${item.family_name} - ${item.material_name} - ${item.hole_quantity} furos` : item.name,
        selected: item.id === defaultId
      })
    )
    
    select.append(options)
    
    if(defaultId !== null) {
      selectId.val(defaultId)
    }
  }, 
  
  // Preencher um formulário
  fillFormFields(
    formSelector, 
    data
  ) {
    Object.entries(data).forEach(([key, value]) => {
      const $el = $(`${formSelector} #${key}`)
      
      if(!$el.length) return
      
      if($el.is(":checkbox")) {
         $el.prop("checked", !!value)
      } else {
        $el.val(value)
      }
    })
  }
}