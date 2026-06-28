const { createApp, ref, computed } = Vue

createApp({
    setup() {
        const file    = ref(null)
        const secteur = ref('Développement Fullstack')
        const loading = ref(false)
        const status  = ref('')
        const result  = ref(null)

        const base = computed(() => result.value
            ? Object.values(result.value.scores).reduce((s, c) => s + (c.score || 0), 0) : 0)
        const maxBase = computed(() => result.value
            ? Object.values(result.value.scores).reduce((s, c) => s + (c.max || 0), 0) : 0)

        const total = computed(() => result.value
            ? base.value + (result.value.bonus_points?.total || 0) - (result.value.deductions?.total || 0)
            : 0)
        const maxTotal = computed(() => maxBase.value + 20)

        const gaugePct = computed(() => maxTotal.value
            ? Math.max(0, Math.min(100, total.value / maxTotal.value * 100)) : 0)

        function pct(cat) { return cat.max ? Math.min(100, cat.score / cat.max * 100) : 0 }
        function round1(n) { return Math.round(n * 10) / 10 }

        function onFile(e) { file.value = e.target.files[0] }
        function reset() { result.value = null; file.value = null; status.value = '' }

        async function submit() {
            loading.value = true
            status.value = ''
            result.value = null
            const form = new FormData()
            form.append('file', file.value)
            form.append('secteur', secteur.value)
            try {
                const res = await fetch('/evaluate', { method: 'POST', body: form })
                if (!res.ok) throw new Error('Le serveur a refusé la requête (' + res.status + ')')
                const json = await res.json()
                result.value = json.score
            } catch (err) {
                status.value = 'Erreur : ' + err.message
            } finally {
                loading.value = false
            }
        }

        return {
            file, secteur, loading, status, result,
            total, maxTotal, gaugePct, pct, round1,
            onFile, submit, reset,
        }
    }
}).mount('#app')