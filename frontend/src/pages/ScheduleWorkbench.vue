<script setup>
import { onMounted, ref } from 'vue'
import { getJSON, postJSON } from '../api'
const principal = ref(800000)
const annual_rate = ref(4.2)
const months = ref(360)
const rules = ref([])
const ruleId = ref('')
const out = ref(null)
const err = ref('')

const loadRules = async () => {
  rules.value = (await getJSON('/api/balloon-rules')).items
}
const run = async () => {
  err.value = ''
  out.value = null
  const body = {
    principal: principal.value,
    annual_rate: annual_rate.value,
    months: months.value,
    persist: true,
    balloon_rule_id: ruleId.value === '' ? null : Number(ruleId.value),
  }
  try {
    out.value = await postJSON('/api/schedule', body)
  } catch (e) {
    try {
      const d = JSON.parse(e.message)
      if (d.error === 'balloon_cap_exceeded') {
        err.value = `末期本金 ${d.balloon_principal} 超过上限 ${d.balloon_cap}，已拒绝且未写入记录。`
        return
      }
    } catch { /* 非结构化错误，走通用提示 */ }
    err.value = '试算失败：' + e.message
  }
}
onMounted(loadRules)
</script>
<template><div class="page"><h1>月供试算</h1>
<label>本金 <input v-model.number="principal" type="number" /></label>
<label>年利率% <input v-model.number="annual_rate" type="number" step="0.01" /></label>
<label>月数 <input v-model.number="months" type="number" /></label>
<label>规则
  <select v-model="ruleId">
    <option value="">整表等额本息（不使用气球规则）</option>
    <option v-for="r in rules" :key="r.id" :value="r.id" :disabled="!r.enabled">
      #{{ r.id }} B={{ r.balloon_period }} 上限 {{ r.balloon_cap }}{{ r.enabled ? '' : '（已停用）' }}
    </option>
  </select>
</label>
<button @click="run">计算</button>
<p v-if="err" class="err">{{ err }}</p>
<div v-if="out">
  <table class="compare">
    <tr><th></th><th>金额</th></tr>
    <tr><td>常规月供</td><td class="hero-num">{{ out.monthly_payment }}</td></tr>
    <tr v-if="out.kind === 'balloon'">
      <td>末期月供（第 {{ out.balloon_period }} 期）</td>
      <td class="hero-num">{{ out.balloon_payment }}</td>
    </tr>
    <tr><td>利息合计</td><td>{{ out.total_interest }}</td></tr>
    <tr v-if="out.kind === 'balloon'"><td>末期本金</td><td>{{ out.balloon_principal }}</td></tr>
  </table>
  <p v-if="out.run_id" class="hint">已写入试算记录 #{{ out.run_id }}</p>
  <h2>摊还预览</h2>
  <table>
    <tr v-for="r in out.preview" :key="r.period" :class="{ 'row-final': out.kind === 'balloon' && r.period === out.balloon_period }">
      <td>第{{ r.period }}期</td><td>{{ r.payment }}</td><td>{{ r.principal }}</td><td>{{ r.interest }}</td><td>{{ r.balance }}</td>
    </tr>
  </table>
</div>
</div></template>
