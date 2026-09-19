<script setup>
import { onMounted, ref } from 'vue'
import { getJSON, postJSON } from '../api'
const stations = ref([])
const start = ref('A1')
const end = ref('B2')
const out = ref(null)
const nameOf = (code) => stations.value.find(s => s.code === code)?.name || code
onMounted(async () => { stations.value = (await getJSON('/api/stations')).items })
const run = async () => { out.value = await postJSON('/api/quote', { start: start.value, end: end.value, persist: true }) }
</script>
<template>
  <div class="page"><h1>最短站数票价</h1>
    <div class="panel">
      <select v-model="start"><option v-for="s in stations" :key="s.code" :value="s.code">{{ s.name }}</option></select>
      →
      <select v-model="end"><option v-for="s in stations" :key="s.code" :value="s.code">{{ s.name }}</option></select>
      <button @click="run">试算</button>
    </div>
    <div v-if="out" class="panel">
      <template v-if="out.reachable">
        <p>站数 {{ out.hops }}</p>
        <p class="muted">路径：{{ out.path.map(nameOf).join(' → ') }}</p>
        <table>
          <tr><td>基础票价（分段计价）</td><td>¥{{ out.base_fare }}</td></tr>
          <template v-if="out.congestion_edges.length">
            <tr v-for="(c, i) in out.congestion_edges" :key="i">
              <td>拥挤附加 · {{ nameOf(c.a) }}—{{ nameOf(c.b) }}（{{ c.level }}）</td>
              <td>+¥{{ c.surcharge }}</td>
            </tr>
          </template>
          <tr v-else><td colspan="2" class="muted">途经区间均无拥挤附加</td></tr>
          <tr><td>附加合计</td><td>+¥{{ out.surcharge_total }}</td></tr>
          <tr><td>应付票价</td><td><span class="hero-num">¥{{ out.payable }}</span></td></tr>
        </table>
      </template>
      <p v-else class="muted">不可达</p>
    </div>
  </div>
</template>
