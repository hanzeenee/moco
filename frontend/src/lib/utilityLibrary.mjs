export const LIBRARY_PAGE_SIZE = 9

export function libraryPage(items, type = 'ea', requestedPage = 1) {
  const filteredItems = items.filter(item => item.type === type && (type === 'ea' || type === 'indicator'))
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
