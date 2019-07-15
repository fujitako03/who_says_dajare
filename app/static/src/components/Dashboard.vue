<template>
<div>
  <h1>オフトゥン・フライング・システム</h1>
  <div class='result'>
    <template v-if="result === null">
      <p>最高のダジャレを入力してくれ！！！</p>
    </template>
    <template v-else-if="result > 0">
      <p>{{ result }}点！！！</p>
      <canvas id="resultChart" width="400p" height="400px"></canvas>
    </template>
    <template v-else>
      <p>なんて？</p>
    </template>
  </div>
  <div>
    <p>
      <input type="text" v-model=dajare v-on:keyup.enter="evaluate">
    </p>
    <button @click="evaluate">採点</button>
  </div>
</div>
</template>

<script>
import axios from 'axios'
import Chart from 'chart.js'

export default {
  data () {
    return {
      dajare: null,
      result: null,
      feature: null,
      resultChart: null
    }
  },
  updated: function () {
    this.$nextTick(function () {
      this.render()
    })
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
        const data = res.data.data
        this.result = data.result
        this.feature = [
          data.f1,
          data.f2,
          data.f3,
          data.f4,
          data.f5,
          data.f6
        ]
      } catch (error) {
        console.error(error)
        console.error(error.response)
      }
    },

    render () {
      this.resultChart = new Chart('resultChart', {
        type: 'radar',
        data: {
          labels: ['破壊力', 'スピード', '射程距離', '持続力', '精密動作性', '成長性'],
          datasets: [{
            data: this.feature,
            backgroundColor: [
              'rgba(255, 99, 132, 0.2)'
            ],
            borderColor: [
              'rgba(255, 99, 132, 1)'
            ],
            borderWidth: 1
          }]
        },
        options: {
          responsive: false,
          legend: {
            display: false
          },
          scale: {
            pointLabels: {
              fontSize: 20
            },
            ticks: {
              min: 0,
              max: 5,
              stepSize: 1,
              beginAtZero: true
            }
          }
        }
      })
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

#resultChart {
  margin: auto;
}
</style>
