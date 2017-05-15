<template>
<div class="cache-layers-container"> 
  <big>Memory</big>
  <table class="q-table bordered striped">
    <thead>
      <tr>
        <th class="text-left">Address</th>
        <th class="text-right">Value</th>
      </tr>
    </thead>
    <tbody>
      <tr v-for="item in memory" :class="{ 'bg-secondary' : item[1].highlight }">
        <td class="text-left">{{ toHex(item[0]) }}</td>
        <td class="text-right">{{ item[1].value }}</td>
      </tr>
    </tbody>
  </table>
</div>
</template>
<script>
export default {
  data () {
    return {}
  },
  props: ['memory'],
  methods: {
    toHex (bin) {
      var hex = parseInt(bin, 2).toString(16).toUpperCase()
      while (hex.length < 8) {
        hex = '0' + hex
      }
      return '0x' + hex
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
