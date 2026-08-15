export const ProductionUI = {
  replaceHtml(containerEl, content) {
    $(containerEl).html(content)
  },

  setAttr(el, name_attr, value) {
    $(el).attr(name_attr, value)
  },

  getAttr(el, name_attr) {
    return $(el).data(name_attr)
  }
}