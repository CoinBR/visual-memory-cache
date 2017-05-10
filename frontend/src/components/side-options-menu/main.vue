<template lang="pug">
div(class='side-menu')
  form(id='traceform' method='POST' :action='urls.uploadTrace' enctype="multipart/form-data" ) 
    div(v-for="lbl in ['Blocks', 'Words', 'Layers']")
      pow2-field(:label='lbl' @value-change='updateHiddenField')
      input(type='hidden' :name='"n_" + lbl.toLowerCase()' :value='fields["n" + lbl]')
    label Method:
    q-select(type='list' v-model='method' :options='meths') 
    label
      q-checkbox(v-model="showTables" @input='toggleShowTables')
      |ShowTables
    input(type='hidden' name='method' :value='method')
    input(type='file' name='tracefile')
  div(id='submitBtnContainer')
      button(id='submitBtn' class='primary circular submit-btn' @click='sendForm')
        i check
    
  
</template>

<script>
import { Loading } from 'quasar'

import Pow2Field from './pow2-field.vue'

export default {
  data () {
    const HOST_URL = 'http://localhost:5000/'
    const UPLOAD_TRACE_URL = HOST_URL + 'traces/'
    return {
      method: 'r',
      showTables: true,
      urls: {
        host: HOST_URL,
        uploadTrace: UPLOAD_TRACE_URL
      },
      fields: {
        nBlocks: 2,
        nWords: 2,
        nLayers: 2
      },
      meths: [
        {
          label: 'Read',
          value: 'r'
        },
        {
          label: 'Write Through',
          value: 'w'
        },
        {
          label: 'Copy Back',
          value: 'c'
        }
      ]
    }
  },
  methods: {
    updateHiddenField (lst) {
      this.fields[lst[0]] = lst[1]
    },
    sendForm () {
      document.getElementById('submitBtn').style.visibility = 'hidden'
      Loading.show()

      this.req = new XMLHttpRequest()
      const fd = new FormData(document.getElementById('traceform'))
      this.req.addEventListener('load', this.startTrace)
      this.req.open('POST', this.urls.uploadTrace)
      this.req.send(fd)
    },
    startTrace () {
      const id = JSON.parse(this.req.responseText).id

      this.$emit('got-forward-once-url', this.getForwardOnceUrl(id))
      console.log(this.getForwardOnceUrl(id))

      this.req2 = new XMLHttpRequest()
      this.req2.addEventListener('load', this.forwardOnceCB)
      this.req2.open('GET', this.getForwardOnceUrl(id))
      this.req2.send()
    },
    forwardOnceCB () {
      Loading.hide()
      document.getElementById('submitBtn').style.visibility = 'visible'
      this.$emit('start-trace', JSON.parse(this.req2.responseText))
    },
    getForwardOnceUrl (id) {
      return this.urls.uploadTrace + id + '/forward'
    },
    toggleShowTables () {
      this.$emit('toggle-show-tables', this.showTables)
    }
  },
  components: {
    Pow2Field
  }
}
</script>

<style>
.side-menu{
  width: 100%;
  text-align: center;
}
#submitBtnContainer{
  margin-top: 30px;
  text-align: center;   
}
label{
  display: block;
  float: left;
  width: 44%;
  padding-top: 6%;
  font-weight: bold;
  margin-bottom: 30px;
}
</style>
