export const LIBRARY_PAGE_SIZE = 9

function searchText(value) { return String(value ?? '').normalize('NFKC').toLowerCase().trim().replace(/\s+/g, ' ') }

export function libraryPage(items, type = 'ea', requestedPage = 1, query = '', translate = value => value) {
  const terms = searchText(query).split(' ').filter(Boolean)
  const filteredItems = items.filter(item => {
    if (item.type !== type || (type !== 'ea' && type !== 'indicator')) return false
    if (!terms.length) return true
    const fields = [item.title, item.description].filter(Boolean)
    const text = searchText([...fields, ...fields.map(translate)].join(' '))
    const compact = text.replace(/\s/g, '')
    return terms.every(term => text.includes(term) || compact.includes(term))
  })
  const pageCount = Math.ceil(filteredItems.length / LIBRARY_PAGE_SIZE)
  const requested = Number.isFinite(requestedPage) ? Math.floor(requestedPage) : 1
  const page = Math.max(1, Math.min(Math.max(1, pageCount), requested))
  return { filteredItems, pageCount, page, items: filteredItems.slice((page - 1) * LIBRARY_PAGE_SIZE, page * LIBRARY_PAGE_SIZE) }
}

export function libraryPageLinks(page, count) {
  const pages = new Set([1, count])
  for (let number = Math.max(1, page - 1); number <= Math.min(count, page + 1); number += 1) pages.add(number)
  const result = []
  for (const number of [...pages].filter(number => number >= 1 && number <= count).sort((a, b) => a - b)) {
    const previous = result[result.length - 1]
    if (previous && number - previous === 2) result.push(previous + 1)
    else if (previous && number - previous > 2) result.push(null)
    result.push(number)
  }
  return result
}
