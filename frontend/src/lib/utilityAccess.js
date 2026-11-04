import { createUtilityAccessClient } from './utilityTabAccess.mjs'

const client = createUtilityAccessClient()
export const csrfToken = client.csrfToken
export const utilityRequest = client.request
export const downloadUtilityFile = client.download
