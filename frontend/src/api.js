async function req(path, opts) {
  const r = await fetch(path, opts)
  if (!r.ok) {
    let msg = await r.text()
    try { msg = JSON.parse(msg).detail ?? msg } catch {}
    throw new Error(msg)
  }
  return r.json()
}
export function getJSON(path) { return req(path) }
export function postJSON(path, body) {
  return req(path, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) })
}
export function putJSON(path, body) {
  return req(path, { method: 'PUT', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) })
}
