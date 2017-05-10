<template>
  <div class="side-menu-numeric-field">
    <label>{{ label }}:</label>
    <q-select
      type="list"
      v-model="value"
      :options="selectOptions"
    ></q-select>
  </div>
</template>

<script>
export default {
  data () {
    return {
      value: 'r',
      selectOptions: [{label: 'Read', value: 'r'},
                      {label: 'Write Through', value: 'w'},
                      {label: 'Copy Back', value: 'c'}]
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
