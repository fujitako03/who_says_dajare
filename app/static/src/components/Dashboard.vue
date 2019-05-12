<template>
<div>
  <h1>オフトゥン・フライング・システム</h1>
  <div class='result'>
    <template v-if="result === null">
      <p>最高のダジャレを入力してくれ！！！</p>
    </template>
    <template v-else-if="result > 0">
      <p>{{ result }}点！！！</p>
    </template>
    <template v-else>
      <p>なんて？</p>
    </template>
  </div>
  <div>
    <p>
      <input type="text" v-model=dajare>
    </p>
    <button @click="evaluate">布団を飛ばす</button>
  </div>
</div>
</template>

<script>
import axios from 'axios'

export default {
  data () {
    return {
      dajare: null,
      result: null
    }
  },
  methods: {
    async evaluate () {
      if (this.dajare === null || this.dajare === '') {
        this.result = null
        return
      }

      try {
        const res = await axios.get('/api/evaluate', {
          params: {
            dajare: this.dajare
          }
        })
        this.result = res.data.data.result
      } catch (error) {
        console.error(error)
        console.error(error.response)
      }
    }
  }
}
</script>

<style>
.result {
  font-size: 25px;
}

input {
  width: 500px;
  font-size: 25px;
}

button {
  font-size: 25px;
}
</style>
