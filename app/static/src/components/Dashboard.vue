<template>
<div>
  <h1>???WHO SAYS DAJARE???</h1>
  <p>{{ result }}</p>
  <input type="text" v-model=dajare>
</div>
</template>

<script>
import axios from 'axios'

export default {
  data () {
    return {
      dajare: null,
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
