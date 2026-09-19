<script setup>
import { onMounted, ref } from 'vue'
import { getJSON } from '../api'
const items = ref([])
const detail = ref(null)
const lookupId = ref('')
const error = ref('')
const parseRow = (h) => ({ ...h, input: JSON.parse(h.input_json), result: JSON.parse(h.result_json) })
const loadList = async () => { items.value = (await getJSON('/api/history')).items }
onMounted(loadList)
const openById = async (id) => {
  error.value = ''
  if (id === '' || id === null || id === undefined) return
  try {
    detail.value = await getJSON(`/api/history/${id}`)
  } catch (e) {
    detail.value = null
    error.value = `记录 #${id} 打不开：${e.message}`
  }
}
const reset = () => { detail.value = null; error.value = '' }
</script>
<template>
  <div class="page">
    <h1>试算记录</h1>
    <div class="panel">
      按编号打开旧记录：
      <input v-model="lookupId" type="number" min="1" style="width:6rem" @keyup.enter="openById(lookupId)">
      <button @click="openById(lookupId)">打开</button>
    </div>
    <p v-if="error" class="muted">{{ error }}</p>
    <div v-if="detail" class="panel">
      <p><strong>记录 #{{ detail.id }}</strong> · {{ detail.created_at }} · {{ detail.input.start }} → {{ detail.input.end }}</p>
      <template v-if="detail.result.reachable">
        <table>
          <tr><td>基础票价</td><td>¥{{ detail.result.base_fare }}</td></tr>
          <tr v-for="(c, i) in detail.result.congestion_edges" :key="i">
            <td>当时拥挤边 · {{ c.a }}—{{ c.b }}（{{ c.level }}）</td>
            <td>+¥{{ c.surcharge }}</td>
          </tr>
          <tr v-if="!detail.result.congestion_edges.length"><td colspan="2" class="muted">当时途经区间无拥挤附加</td></tr>
          <tr><td>附加合计</td><td>+¥{{ detail.result.surcharge_total }}</td></tr>
          <tr><td>应付票价</td><td><span class="hero-num">¥{{ detail.result.payable }}</span></td></tr>
        </table>
      </template>
      <p v-else class="muted">不可达</p>
      <button @click="reset">返回列表</button>
    </div>
    <table v-else>
      <tr><th>#</th><th>时间</th><th>起讫</th><th></th></tr>
      <tr v-for="h in items" :key="h.id">
        <td>#{{ h.id }}</td>
        <td>{{ h.created_at }}</td>
        <td>{{ parseRow(h).input.start }} → {{ parseRow(h).input.end }}</td>
        <td><button @click="openById(h.id)">打开</button></td>
      </tr>
    </table>
  </div>
</template>
