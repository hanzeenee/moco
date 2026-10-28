export const serviceLinks = {
  development: 'https://open.kakao.com/o/sIPFiqUi',
  reviews: 'https://kmong.com/gig/607495',
  infinox: '',
}

export const businessContacts = {
  email: 'mailto:moconix95@gmail.com',
  telegram: 'https://t.me/moconix',
}

export function serviceUrl(key) {
  const value = serviceLinks[key]?.trim() || ''
  return /^https?:\/\//i.test(value) ? value : ''
}
