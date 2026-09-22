<script setup>
import { onMounted, ref } from 'vue'
import { getJSON } from '../api'

const items = ref([])
const detail = ref(null)
const error = ref('')

onMounted(async () => { items.value = (await getJSON('/api/history')).items })

const open = async (h) => {
  error.value = ''
  try { detail.value = await getJSON(`/api/history/${h.id}`) }
  catch (e) { error.value = e.message }
}
</script>

<template>
  <div class="page">
    <h1>试算记录</h1>
    <table>
      <tr><th>#</th><th>类型</th><th>时间</th><th></th></tr>
      <tr v-for="h in items" :key="h.id">
        <td>#{{ h.id }}</td><td>{{ h.kind }}</td><td>{{ h.created_at }}</td>
        <td><button @click="open(h)">打开</button></td>
      </tr>
    </table>
    <p v-if="error" class="error">{{ error }}</p>

    <section v-if="detail">
      <h2>记录 #{{ detail.id }}（{{ detail.kind }}）</h2>
      <p>打开的是落库时的写入值，之后改规则不影响本记录。</p>
      <table>
        <tr><th>模式</th><td>{{ detail.result.mode ?? '—' }}</td></tr>
        <tr><th>常规月供</th><td>{{ detail.result.monthly_payment }}</td></tr>
        <tr v-if="detail.result.mode === 'balloon'"><th>末期月供</th><td>{{ detail.result.final_payment }}</td></tr>
        <tr v-if="detail.result.mode === 'balloon'"><th>末期本金</th><td class="hero-num">{{ detail.result.final_principal }}</td></tr>
        <tr><th>利息合计</th><td>{{ detail.result.total_interest }}</td></tr>
      </table>
      <h3>入参</h3>
      <pre>{{ detail.input }}</pre>
    </section>
  </div>
</template>
