const baseUrl = (import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000').replace(/\/$/, '')
const tokenKey = 'jobboard-session'

export function setToken(token) {
  if (token) sessionStorage.setItem(tokenKey, token)
  else sessionStorage.removeItem(tokenKey)
}

export async function api(path, { body, ...options } = {}) {
  const token = sessionStorage.getItem(tokenKey)
  let response
  try {
    response = await fetch(`${baseUrl}${path}`, {
      ...options,
      headers: {
        ...(body !== undefined ? { 'Content-Type': 'application/json' } : {}),
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
        ...options.headers,
      },
      ...(body !== undefined ? { body: JSON.stringify(body) } : {}),
    })
  } catch (error) {
    if (error.name === 'AbortError') throw error
    throw new Error('API inaccessible. Vérifiez que le backend est démarré et que VITE_API_URL est correct.', { cause: error })
  }
  if (response.status === 204) return null
  const data = await response.json().catch(() => null)
  if (!response.ok) {
    if (response.status === 401 && token) {
      setToken(null)
      window.dispatchEvent(new Event('session-expired'))
    }
    const detail = data?.detail
    throw new Error(Array.isArray(detail)
      ? detail.map((item) => `${item.loc.at(-1)} : ${item.msg}`).join(' ; ')
      : detail || `Erreur HTTP ${response.status}`)
  }
  return data
}
