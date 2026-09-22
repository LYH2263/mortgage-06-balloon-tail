<script setup>
import { onMounted, ref } from 'vue'
import { getJSON, postJSON, putJSON } from '../api'

const blank = () => ({ name: '', balloon_period: 36, cap: 500000, enabled: true })
const items = ref([])
const form = ref(blank())
const editing = ref(null)
const error = ref('')

const load = async () => { items.value = (await getJSON('/api/balloon/rules')).items }
const save = async () => {
  error.value = ''
  try {
    if (editing.value) await putJSON(`/api/balloon/rules/${editing.value}`, form.value)
    else await postJSON('/api/balloon/rules', form.value)
    form.value = blank(); editing.value = null
    await load()
  } catch (e) { error.value = e.message }
}
const edit = (r) => {
  editing.value = r.id
  form.value = { name: r.name, balloon_period: r.balloon_period, cap: r.cap, enabled: r.enabled }
}
const cancel = () => { editing.value = null; form.value = blank(); error.value = '' }
const disable = async (r) => { await postJSON(`/api/balloon/rules/${r.id}/disable`, {}); await load() }
const enable = async (r) => { await putJSON(`/api/balloon/rules/${r.id}`, { enabled: true }); await load() }

onMounted(load)
</script>

<template>
  <div class="page">
    <h1>气球尾款规则</h1>
    <p>启用后前 B-1 期按整贷等额本息，第 B 期收齐剩余本金加当期利息；末期本金不得超过尾款上限，否则拒绝且不落库。</p>

    <table>
      <tr><th>#</th><th>名称</th><th>气球期序号 B</th><th>尾款上限</th><th>状态</th><th>操作</th></tr>
      <tr v-for="r in items" :key="r.id">
        <td>{{ r.id }}</td>
        <td>{{ r.name }}</td>
        <td>第 {{ r.balloon_period }} 期</td>
        <td>{{ r.cap }}</td>
        <td>{{ r.enabled ? '启用' : '停用' }}</td>
        <td>
          <button @click="edit(r)">编辑</button>
          <button v-if="r.enabled" @click="disable(r)">停用</button>
          <button v-else @click="enable(r)">启用</button>
        </td>
      </tr>
    </table>

    <h2>{{ editing ? `编辑规则 #${editing}` : '新建规则' }}</h2>
    <label>名称 <input v-model="form.name" /></label>
    <label>气球期序号 B <input type="number" v-model.number="form.balloon_period" /></label>
    <label>尾款上限 <input type="number" v-model.number="form.cap" /></label>
    <label>启用 <input type="checkbox" v-model="form.enabled" /></label>
    <button @click="save">{{ editing ? '保存' : '创建' }}</button>
    <button v-if="editing" @click="cancel">取消</button>
    <p v-if="error" class="error">{{ error }}</p>
  </div>
</template>
