<template>
  <div class="cache-layers-container">
    <div v-for="layer in fixedData.layers" class="layer-container">
      <big>Layer {{layer.n}}</big>
      <table class="q-table bordered striped">
        <thead>
          <tr>
            <th class="text-left">R
              <q-tooltip>
                the RANK of the Layer in this Block
              </q-tooltip>
            </th>
            <th class="text-left">V
              <q-tooltip>
                Is this entry VALID?
              </q-tooltip>
            </th>
            <th class="text-left">D
              <q-tooltip>
                Is this entry DIRTY?
              </q-tooltip>
            </th>
            <th class="text-right">Tag</th>
            <th class="text-right" v-for="word_num in layer.blocks[0].words.length">{{word_num - 1}}
               <q-tooltip>
                 Word #{{word_num - 1}}
              </q-tooltip>           
            </th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="block in layer.blocks">
            <td class="text-right">{{ block.rank }}</td>
            <td class="text-right">{{ block.valid }}</td>
            <td class="text-right">{{ block.dirty }}</td>
            <td class="text-left">{{ block.tag ? block.tag : emptyTag }}</td>
            <td class="text-right" v-for="word in block.words">{{ word }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>
<script>
export default {
  data () {
    return {
      emptyTag: '',
      fixedData: {
        layers: []
      }
    }
  },
  methods: {
    updateFixedData (data, oldData) {
      const nLayers = data.blocks[0].layers.length
      const nBlocks = data.blocks.length
      var fixedData = { layers: [] }

      var layer = null
      for (var layerN = 0; layerN < nLayers; layerN++) {
        layer = { blocks: [] }
        for (var blockN = 0; blockN < nBlocks; blockN++) {
          var subBlock = data.blocks[blockN].layers[layerN]
          layer.blocks.push(subBlock)
          layer['n'] = layerN
        }
        fixedData.layers.push(layer)
      }
      this.fixedData = fixedData
    }
  },
  props: ['data'],
  created: function () {
    this.updateFixedData(this.data, this.data)

    var block = null
    var layer = null
    for (var b in this.data.blocks) {
      block = this.data.blocks[b]
      for (var l in block.layers) {
        layer = block.layers[l]
        if (layer.tag) {
          for (var i = 0; i < layer.tag.length; i++) {
            this.emptyTag += '0'
          }
          return true
        }
      }
    }
  },
  watch: {
    'data' (data, oldData) {
      this.updateFixedData(data, oldData)
    }
  }
}
</script>

<style>
  .cache-layers-container{
    float: left;
  }
  .cache-layers-container big{
    padding: 50px 0px 0px 0px;
    text-align: center;
    width: 100%;
    clear: both;
    display: block;
  }
  table{
    clear: both;
  }
</style>
