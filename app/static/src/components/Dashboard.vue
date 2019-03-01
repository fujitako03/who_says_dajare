<template>
<div>
  <h1>???WHO SAYS DAJARE???</h1>
  <p>{{ result }}</p>
</div>
</template>

<script>
import axios from 'axios'

export default {
  data () {
    return {
      result: null,
      test: 'test'
    }
  },
  async mounted () {
    await this.fetch()
  },
  methods: {
    async fetch () {
      const res = await axios.get('/api/hello')
      this.result = res.data.data
    }
  }
}
</script>
