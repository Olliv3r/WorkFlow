export const PaymentUI = {
  updateSummary() {
    let totalDozens = 0;
    let totalAmount = 0;

    $(".form-check-input:checked").each(function () {
      totalDozens += Number($(this).data("dozens"));
      totalAmount += Number($(this).data("amount"));
    });

    $("#formPaymentCreate #total_dozens").text(totalDozens);
    $("#formPaymentCreate #total_amount").text(totalAmount.toFixed(2));
  },

  updateButton(status, date, button) {
    const $button = $(button)
    const $row = $button.closest("tr")
    const $status = $row.find(".payment_status")
    const $date = $row.find(".payment_date")
    
    if (status === "paid") {
      $button
        .removeClass("is-pending")
        .addClass("is-paid")
        .html(`
          <i class="bi bi-arrow-counterclockwise"></i>
          Reverter p/ Pendente
        `)
      $status.html(`
        <span class="badge-paid">
          <i class="bi bi-check-circle-fill"></i> Pago
        </span
      `)
      
    } else if (status === "pending") {
      $button
        .removeClass("is-paid")
        .addClass("is-pending")
        .html(`
          <i class="bi bi-check2-circle"></i>
          Marcar como Pago
        `)
      $status.html(`
        <span class="badge-pending">
          <i class="bi bi-hourglass-split"></i>Pendente
        </span>
      `)
      
    } else {
      alert("Status inválido")
      $status.html(`
        <span class="badge-pending">
          ${status}
        </span>`
      )
      return
    }

    $date.text(date === null ? "-" : date)
  },

  replaceHtml(containerEl, content) {
    $(containerEl).html(content)
  }
};
