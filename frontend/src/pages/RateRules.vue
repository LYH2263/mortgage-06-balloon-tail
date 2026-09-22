<script setup>
import { onMounted, ref } from 'vue'
import { getJSON, postJSON, patchJSON } from '../api'

const rules = ref([])
const form = ref({ balloon_period: 60, balloon_cap: 1000000, enabled: true })
const draft = ref({})
const err = ref('')

const load = async () => {
  rules.value = (await getJSON('/api/balloon-rules')).items
  draft.value = Object.fromEntries(rules.value.map(r =>
    [r.id, { balloon_period: r.balloon_period, balloon_cap: r.balloon_cap }]))
}
const create = async () => {
  err.value = ''
  try {
    await postJSON('/api/balloon-rules', { ...form.value })
    form.value = { balloon_period: 60, balloon_cap: 1000000, enabled: true }
    await load()
  } catch (e) { err.value = '创建失败：' + e.message }
}
const save = async (r) => {
  err.value = ''
  try {
    const d = draft.value[r.id]
    await patchJSON(`/api/balloon-rules/${r.id}`, { balloon_period: Number(d.balloon_period), balloon_cap: Number(d.balloon_cap) })
    await load()
  } catch (e) { err.value = `#${r.id} 更新失败：` + e.message }
}
const toggle = async (r) => {
  err.value = ''
  try {
    await patchJSON(`/api/balloon-rules/${r.id}`, { enabled: !r.enabled })
    await load()
  } catch (e) { err.value = `#${r.id} 启停失败：` + e.message }
}

onMounted(load)
</script>
<template><div class="page">
  <h1>气球尾款规则</h1>
  <p class="hint">启用后：前 B-1 期按整表等额本息月供还款，第 B 期一次性收齐剩余本金及当期利息；末期本金超过上限则拒绝试算。停用后回到整表等额本息。</p>
  <p v-if="err" class="err">{{ err }}</p>

  <table>
    <tr><th>#</th><th>气球期序号 B</th><th>尾款本金上限</th><th>状态</th><th>操作</th></tr>
    <tr v-for="r in rules" :key="r.id">
      <td>{{ r.id }}</td>
      <td><input v-model.number="draft[r.id].balloon_period" type="number" min="1" /></td>
      <td><input v-model.number="draft[r.id].balloon_cap" type="number" min="0" step="0.01" /></td>
      <td><span :class="r.enabled ? 'tag-on' : 'tag-off'">{{ r.enabled ? '启用中' : '已停用' }}</span></td>
      <td class="row-actions">
        <button @click="save(r)">保存</button>
        <button class="ghost" @click="toggle(r)">{{ r.enabled ? '停用' : '启用' }}</button>
      </td>
    </tr>
    <tr v-if="!rules.length"><td colspan="5">暂无规则，先在下方新建。</td></tr>
  </table>

  <h2>新建规则</h2>
  <div class="form-row">
    <label>气球期序号 B <input v-model.number="form.balloon_period" type="number" min="1" /></label>
    <label>尾款本金上限 <input v-model.number="form.balloon_cap" type="number" min="0" step="0.01" /></label>
    <label class="check"><input type="checkbox" v-model="form.enabled" /> 立即启用</label>
    <button @click="create">创建</button>
  </div>
</div></template>
