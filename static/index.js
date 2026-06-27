const { createApp, ref } = Vue

createApp({
    setup() {
        const file    = ref(null)
        const secteur = ref('Développement Fullstack')
        const loading = ref(false)
        const status  = ref('')

        function onFile(e) {
            file.value = e.target.files[0]
        }

        async function submit() {
            loading.value = true
            status.value = ''
            const form = new FormData()
            form.append('file', file.value)
            form.append('secteur', secteur.value)
            try {
                const res = await fetch('http://localhost:8000/api/evaluate/', {
                    method: 'POST',
                    body: form,
                })
                const data = await res.json()
                status.value = 'Évaluation lancée · job ' + data.job_id
            } catch (err) {
                status.value = 'Erreur : ' + err.message
            } finally {
                loading.value = false
            }
        }

        return { file, secteur, loading, status, onFile, submit }
    }
}).mount('#app')