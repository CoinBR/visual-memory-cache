<template>
<q-layout>
  <!-- Header -->
  <div slot="header" class="toolbar">
    <!-- opens left-side drawer using its ref -->
    <button class="hide-on-drawer-visible" @click="$refs.leftDrawer.open()">
      <i>menu</i>
    </button>
    <q-toolbar-title :padding="1">
      Visual Memory Cache 
    </q-toolbar-title>
    </div>
 <!-- Left-side Drawer -->
  <q-drawer ref="leftDrawer">
    <side-options-menu :upload-url='uploadUrl' @got-forward-once-url='setForwardURL' @start-trace='updateTables' @toggle-show-tables='toggleShowTables' />
  </q-drawer>

  <!-- IF USING subRoutes only: -->
  <router-view class="layout-view"></router-view>
  <!-- OR ELSE, IF NOT USING subRoutes: -->
  <div class="layout-view" v-if="showTables">
    <memory :memory='data.memory' v-if='data.memory.items.length' />
    <cache :data='data.cache' v-if='data.cache.blocks.length' />
  </div>
   <!-- Footer -->
  <div slot="footer" class="toolbar">
    <cache-control-panel :forwardOnceURL='forwardOnceURL' :data='data' @forward='updateTables' />
  </div>
</q-layout>
</template>

<script>
import { Dialog } from 'quasar'

import SideOptionsMenu from './side-options-menu/main.vue'
import Memory from './memory.vue'
import Cache from './cache.vue'
import CacheControlPanel from './cache-control-panel.vue'

export default {
  data () {
    const hostUrl = 'http://localhost:5000/'

    return {
      uploadUrl: hostUrl + 'traces/',
      forwardOnceURL: null,
      showTables: true,
      data: {
        cache: {
          blocks: []
        },
        memory: {
          items: []
        },
        rates: {
          hits: 0,
          reads: 0
        }
      }
    }
  },
  methods: {
    updateTables (data) {
      this.data = data

      if (this.data.last_step) {
        Dialog.create({
          title: 'Trace Completed',
          message: 'You\'ve reached the End of the Trace'
        })
      }
    },
    toggleShowTables (b) {
      this.showTables = b
    },
    setForwardURL (url) {
      this.forwardOnceURL = url
    }
  },
  components: {
    SideOptionsMenu,
    Memory,
    Cache,
    CacheControlPanel
  }
}
</script>

<style>
table{
  margin: 30px 15px 15px 30px;
  float: left;
}

</style>
