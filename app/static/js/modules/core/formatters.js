export const DateFormatter = {
  fromNow(dataText) {
    return moment.utc(dataText).fromNow()
  }
}