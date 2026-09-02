document.addEventListener('DOMContentLoaded', () => {
	const desc = document.querySelector('[name="desc"]')
	const box = document.getElementById('preview')
	if (!desc || !box) return
	desc.addEventListener('input', () => {
		const clean = DOMPurify.sanitize(desc.value, { USE_PROFILES: { html: true } })
		box.innerHTML = clean || '<em>preview appears here</em>'
	})
})
