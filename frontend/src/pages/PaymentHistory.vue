<script setup>
import { onMounted, ref } from 'vue'
import { getJSON } from '../api'
const items = ref([])
const detail = ref(null)
const err = ref('')
onMounted(async () => { items.value = (await getJSON('/api/history')).items })
const open = async (id) => {
  err.value = ''
  try { detail.value = await getJSON(`/api/history/${id}`) }
  catch (e) { err.value = '打开失败：' + e.message }
}
</script>
<template><div class="page"><h1>试算记录</h1>
<p v-if="err" class="err">{{ err }}</p>
<table>
  <tr><th>#</th><th>类型</th><th>时间</th><th></th></tr>
  <tr v-for="h in items" :key="h.id">
    <td>{{ h.id }}</td>
    <td>{{ h.kind === 'balloon' ? '气球尾款' : '等额本息' }}</td>
    <td>{{ h.created_at }}</td>
    <td><button class="ghost" @click="open(h.id)">打开</button></td>
  </tr>
</table>
<div v-if="detail" class="detail">
  <h2>记录 #{{ detail.id }} 快照</h2>
  <table class="compare">
    <tr><td>常规月供</td><td class="hero-num">{{ detail.result.monthly_payment }}</td></tr>
    <tr v-if="detail.kind === 'balloon'">
      <td>末期月供（第 {{ detail.result.balloon_period }} 期）</td>
      <td class="hero-num">{{ detail.result.balloon_payment }}</td>
    </tr>
    <tr><td>利息合计</td><td>{{ detail.result.total_interest }}</td></tr>
    <tr v-if="detail.kind === 'balloon'"><td>末期本金（写入值）</td><td>{{ detail.result.balloon_principal }}</td></tr>
  </table>
  <p class="hint">以下为写入时的入参快照，不随后续规则修改而变化：</p>
  <pre>{{ JSON.stringify(detail.input, null, 2) }}</pre>
</div>
</div></template>
