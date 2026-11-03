// Generate locale-specific initial HTML from the current build, never copied snapshots.
const fs = require('node:fs')
const path = require('node:path')
const { spawnSync } = require('node:child_process')

const frontend = path.resolve(__dirname, '..')
const templates = path.resolve(frontend, '../backend/templates')
const output = path.resolve(frontend, '.prerender')
const command = require.resolve('@vue/cli-service/bin/vue-cli-service.js')
const build = spawnSync(process.execPath, [command, 'build', '--mode', 'production'], {
  cwd: frontend,
  env: { ...process.env, NODE_ENV: 'production', MOCONIX_PRERENDER_BUILD: '1' },
  stdio: 'inherit',
})
if (build.error) throw build.error
if (build.status !== 0) process.exit(build.status || 1)

const { renderHome } = require(path.join(output, 'render.cjs'))
const base = fs.readFileSync(path.join(templates, 'home.html'), 'utf8')
const app = '<div id="app"></div>'
if (!base.includes(app)) throw new Error('Expected an empty base app shell; refusing a stale prerender build.')
const escape = value => value.replace(/&/g, '&amp;').replace(/"/g, '&quot;').replace(/</g, '&lt;').replace(/>/g, '&gt;')

async function generate() {
  for (const locale of ['ko', 'en']) {
    const page = await renderHome(locale)
    if (!page.html.includes('<h1') || !page.html.includes('service-list')) {
      throw new Error(`The ${locale} homepage did not render its public content.`)
    }
    const website = {
      '@context': 'https://schema.org',
      '@type': 'WebSite',
      name: 'MOCONIX',
      alternateName: '모코닉스',
      url: 'https://moconix.com/',
      inLanguage: locale,
    }
    const structured = JSON.stringify(website).replace(/</g, '\\u003c')
    const html = base
      .replace('<html lang="ko">', `<html lang="${locale}">`)
      .replace(/<title>[^<]*<\/title>/, `<title>${escape(page.title)}</title>`)
      .replace(/(<meta name="description" content=")[^"]*(")/, (_, before, after) => before + escape(page.description) + after)
      .replace('</head>', `<script id="moconix-website-data" type="application/ld+json">${structured}</script></head>`)
      .replace(app, `<div id="app" data-prerendered="${locale}">${page.html}</div>`)
    fs.writeFileSync(path.join(templates, `home-${locale}.html`), html, 'utf8')
    console.log(`Generated initial ${locale} homepage HTML from current Vue components.`)
  }
}
generate().catch(error => { console.error(error); process.exitCode = 1 })
