export async function getJSON(path) {
  const r = await fetch(path)
  if (!r.ok) throw new Error(await r.text())
  return r.json()
}
export async function sendJSON(path, method, body) {
  const r = await fetch(path, { method, headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) })
  if (!r.ok) throw new Error(await r.text())
  return r.json()
}
export const postJSON = (path, body) => sendJSON(path, 'POST', body)
export const putJSON = (path, body) => sendJSON(path, 'PUT', body)
export async function del(path) {
  const r = await fetch(path, { method: 'DELETE' })
  if (!r.ok) throw new Error(await r.text())
  return r.json()
}
