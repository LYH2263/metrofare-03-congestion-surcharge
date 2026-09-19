<script setup>
import { onMounted, ref } from 'vue'
import { getJSON, putJSON, del } from '../api'

const LEVELS = [
  { value: 'low', label: '轻度 +¥1' },
  { value: 'medium', label: '中度 +¥2' },
  { value: 'high', label: '重度 +¥3' },
]
const SURCHARGE = { low: 1, medium: 2, high: 3 }
const LEVEL_LABEL = Object.fromEntries(LEVELS.map(l => [l.value, l.label]))

const edges = ref([])
const congestion = ref([])
const stations = ref([])
const picks = ref({})
const error = ref('')

const keyOf = (a, b) => (a <= b ? `${a}|${b}` : `${b}|${a}`)
const nameOf = (code) => stations.value.find(s => s.code === code)?.name || code
const levelOf = (a, b) => congestion.value.find(e => keyOf(e.a, e.b) === keyOf(a, b))?.level || ''

const load = async () => {
  const [e, c, st] = await Promise.all([
    getJSON('/api/edges'),
    getJSON('/api/congestion'),
    getJSON('/api/stations'),
  ])
  edges.value = e.items
  congestion.value = c.items
  stations.value = st.items
  for (const x of c.items) picks.value[keyOf(x.a, x.b)] = x.level
}

const save = async (a, b) => {
  error.value = ''
  try {
    await putJSON('/api/congestion', { a, b, level: picks.value[keyOf(a, b)] })
    await load()
  } catch (e2) { error.value = `保存失败：${e2.message}` }
}

const clear = async (a, b) => {
  error.value = ''
  try {
    await del(`/api/congestion?a=${encodeURIComponent(a)}&b=${encodeURIComponent(b)}`)
    picks.value[keyOf(a, b)] = ''
    await load()
  } catch (e2) { error.value = `清除失败：${e2.message}` }
}

onMounted(load)
</script>
<template>
  <div class="page">
    <h1>邻接区间 · 拥挤附加</h1>
    <p class="muted">给相邻区间打拥挤等级，试算会沿最短路把途经区间的加价加总。</p>
    <p v-if="error" class="muted">{{ error }}</p>
    <table>
      <tr><th>区间</th><th>拥挤等级</th><th>当前</th><th></th></tr>
      <tr v-for="(e, i) in edges" :key="i">
        <td>{{ nameOf(e.a) }}（{{ e.a }}）— {{ nameOf(e.b) }}（{{ e.b }}）</td>
        <td>
          <select v-model="picks[keyOf(e.a, e.b)]">
            <option value="">（无）</option>
            <option v-for="l in LEVELS" :key="l.value" :value="l.value">{{ l.label }}</option>
          </select>
        </td>
        <td>
          <span v-if="levelOf(e.a, e.b)">¥{{ SURCHARGE[levelOf(e.a, e.b)] }} · {{ LEVEL_LABEL[levelOf(e.a, e.b)] }}</span>
          <span v-else class="muted">—</span>
        </td>
        <td>
          <button @click="save(e.a, e.b)">设置</button>
          <button @click="clear(e.a, e.b)" style="margin-left:.4rem">清除</button>
        </td>
      </tr>
    </table>
  </div>
</template>
