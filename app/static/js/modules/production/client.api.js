export class ClientAPI {
	static request({
		url,
		method = "GET",
		data = null,
		processData = false,
		contentType = false,
		headers = {}
	}) {
		return $.ajax({
			url,
			type: method,
			data,
			processData,
			contentType,
			headers
		})
	}

	static get(options = {}) {
		return this.request({
			method: "GET",
			...options
		})
	}

	static post(options = {}) {
		return this.request({
			method: "POST",
			...options
		})
	}
}
