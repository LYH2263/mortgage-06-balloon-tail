<script setup>
import { computed, onMounted, ref } from 'vue'
import { getJSON, postJSON } from '../api'

const principal = ref(800000)
const annual_rate = ref(4.2)
const months = ref(360)
const persist = ref(true)
const mode = ref('off')           // off | rule | inline
const rules = ref([])
const ruleId = ref(null)
const balloonPeriod = ref(36)
const cap = ref(600000)
const out = ref(null)
const error = ref('')

const enabledRules = computed(() => rules.value.filter(r => r.enabled))

onMounted(async () => { rules.value = (await getJSON('/api/balloon/rules')).items })

const run = async () => {
  error.value = ''; out.value = null
  const body = { principal: principal.value, annual_rate: annual_rate.value, months: months.value, persist: persist.value }
  if (mode.value === 'rule' && ruleId.value) body.rule_id = ruleId.value
  else if (mode.value === 'inline') Object.assign(body, { balloon_period: balloonPeriod.value, cap: cap.value, enabled: true })
  else body.enabled = false
  try { out.value = await postJSON('/api/balloon/schedule', body) }
  catch (e) { error.value = e.message }
}
</script>

<template>
  <div class="page">
    <h1>月供试算</h1>
    <label>本金 <input type="number" v-model.number="principal" /></label>
    <label>年利率% <input type="number" step="0.01" v-model.number="annual_rate" /></label>
    <label>月数 <input type="number" v-model.number="months" /></label>

    <fieldset>
      <legend>气球尾款</legend>
      <label><input type="radio" value="off" v-model="mode" /> 停用（整表等额本息）</label>
      <label><input type="radio" value="rule" v-model="mode" /> 按已存规则
        <select v-model.number="ruleId" :disabled="mode !== 'rule'">
          <option :value="null" disabled>选择规则</option>
          <option v-for="r in enabledRules" :key="r.id" :value="r.id">
            {{ r.name }}（第 {{ r.balloon_period }} 期 / 上限 {{ r.cap }}）
          </option>
        </select>
      </label>
      <label><input type="radio" value="inline" v-model="mode" /> 临时参数
        第 <input type="number" v-model.number="balloonPeriod" :disabled="mode !== 'inline'" style="width:5rem" /> 期，
        上限 <input type="number" v-model.number="cap" :disabled="mode !== 'inline'" />
      </label>
    </fieldset>

    <label>落库 <input type="checkbox" v-model="persist" /></label>
    <button @click="run">计算</button>
    <p v-if="error" class="error">{{ error }}</p>

    <template v-if="out">
      <table v-if="out.mode === 'balloon'" class="compare">
        <tr><th></th><th>常规月供（1–{{ out.final_period - 1 }} 期）</th><th>末期月供（第 {{ out.final_period }} 期）</th></tr>
        <tr><td>月供</td><td class="hero-num">{{ out.monthly_payment }}</td><td class="hero-num">{{ out.final_payment }}</td></tr>
        <tr><td>其中本金</td><td>—</td><td>{{ out.final_principal }}</td></tr>
      </table>
      <p v-else>月供 <span class="hero-num">{{ out.monthly_payment }}</span>（整表等额本息，共 {{ out.row_count }} 期）</p>
      <p>利息合计 {{ out.total_interest }} · 还款总额 {{ out.total_payment }}<span v-if="out.run_id"> · 已落库 #{{ out.run_id }}</span></p>
    </template>
  </div>
</template>
