<template>
  <div class="main">

    <div class="play-panel">

      <button id='btn-play' class="primary circular centr" @click="togglePlay" style=": 70%;">
        <i>{{ play ? 'pause' : 'play_arrow' }}</i>
      </button>

      <button id='btn-forward' class="grey small centr" @click="forward" style=": 70%;">
        <i>keyboard_arrow_right</i>
      </button>

      <span id='stpsLbl'>Steps:</span> 
      <q-numeric id='nSteps' v-model='nSteps' />


    <div class="operation-display-container">
      <input readonly :value="data.instruction" class="bg-secondary">
    </div>


    </div>

    <div class="hit-miss-display">
      <span class="label bg-green text-white">{{ data.rates.hits }}
        <q-tooltip>Hits</q-tooltip>
      </span>
      <span class="label bg-red text-white">{{ data.rates.reads - data.rates.hits }}
        <q-tooltip>Misses</q-tooltip>
      </span>
      <span class="label bg-grey text-white">{{ data.rates.reads }}
        <q-tooltip>Total</q-tooltip>
      </span>
      <span id='percentageLbl' class="label bg-grey-9 text-white">{{ this.getSuccessPercentage() }}
        <q-tooltip>% of Success</q-tooltip>
      </span>

    </div>
  </div>
</template>

<script>
import { Loading } from 'quasar'

export default {
  data () {
    return {
      nSteps: 1,
      play: false
    }
  },
  props: ['forwardOnceURL', 'data'],
  methods: {
    forward () {
      Loading.show()
      this.req = new XMLHttpRequest()
      const fd = new FormData(document.getElementById('traceform'))
      this.req.addEventListener('load', this.forwardCB)
      this.req.open('GET', this.forwardOnceURL + '/' + this.nSteps)
      this.req.send(fd)
    },
    forwardCB () {
      Loading.hide()
      var jsn = JSON.parse(this.req.responseText)
      this.$emit('forward', jsn)
      if (jsn.last_step) {
        this.play = false
      }
    },
    getSuccessPercentage () {
      if (this.data.rates.reads <= 0) {
        return '0.00%'
      }
      const percentage = this.data.rates.hits / this.data.rates.reads
      return (percentage * 100).toFixed(2).toString() + '%'
    },
    runPlayStep () {
      if (this.play) {
        this.forward()
      }
    },
    togglePlay () {
      this.play ? this.play = false : this.play = true
    }
  },
  created () {
    setInterval(this.runPlayStep, 3700)
  }
}
</script>

<style>
  .main{
    width: 100%;
    vertical-align: middle;
    text-align: center;
  }
  .operation-display-container{
    display: inline-block;
    text-align: left;
    margin-right: 37px;
    margin-left: 37px;
  }
  .play-panel{
    display: inline-block;
    text-align: center;

  }
  .hit-miss-display{
    display: inline-block;
    text-align: right;
  }
  #stpsLbl{
    margin-left: 10px;
  }
  #nSteps{
    margin-right: 30px;
  }
  #percentageLbl{
    margin-left: 10px;
  }
</style>
