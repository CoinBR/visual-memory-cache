<template>
  <div class="side-menu-numeric-field">
    <label>{{ label }}:</label>
    <q-numeric
      v-model="number"
      :min="1"
      :max="17"
    ></q-numeric>
  </div>
</template>

<script>
export default {
  data () {
    return {}
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
