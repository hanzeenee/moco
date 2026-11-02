export function csrfToken() {
  const token = document.cookie.split('; ').find(row => row.startsWith('csrftoken='))
  return token ? decodeURIComponent(token.slice('csrftoken='.length)) : ''
}

export async function utilityRequest(path, options = {}) {
  const response = await fetch(`/api/utilities/${path}/`, { credentials: 'same-origin', cache: 'no-store', ...options })
  const body = await response.json().catch(() => ({}))
  if (!response.ok) {
    const error = new Error(body.detail || '요청을 처리하지 못했습니다. 잠시 후 다시 시도해 주세요.')
    error.status = response.status
    throw error
  }
  return body
}
