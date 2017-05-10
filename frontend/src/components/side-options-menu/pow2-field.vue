<template>
  <div class="side-menu-numeric-field">
    <label>{{ label }}:</label>
    <q-numeric
      v-model="value"
      v-bind:min="2"
      v-bind:max="8192"
      v-on:input="valueChange"
    ></q-numeric>
  </div>
</template>

<script>
export default {
  data () {
    return {
      value: 2,
      oldValue: 2
    }
  },
  methods: {
    valueChange () {
      if (this.oldValue < this.value) {
        this.value = this.oldValue * 2
      }
      else {
        this.value = this.oldValue / 2
      }
      this.oldValue = this.value
      this.$emit('value-change', ['n' + this.label, this.value])
    }
  },
  props: ['label']
}
</script>

<style>
.side-menu-numeric-field{
  margin: 20px;
  width: 100%;
}

.side-menu-numeric-field label{
  display: block;
  float: left;
  width: 30%;
  padding-top: 6%;
  font-weight: bold;
}
</style>
