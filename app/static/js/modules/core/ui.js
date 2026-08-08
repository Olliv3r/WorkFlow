export const UI = {
  setLoading(selector, isLoading) {
    const $button = $(selector);

    //$button.prop("disabled", isLoading);

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
    $(selector).addClass("d-none").text("").removeClass(`alert alert-${type}`);
  },

  clearInput(inputEl) {
    $(inputEl).val("")
  },

  reset(formSelector) {
    $(formSelector)[0].reset();
  }
};
