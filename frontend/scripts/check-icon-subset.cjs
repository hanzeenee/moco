// Validate the committed font against every current app icon and Vuetify default.
// A new icon must be included in the subset before deployment, never silently blank.
const fs = require('node:fs')
const path = require('node:path')
const crypto = require('node:crypto')
const frontend = path.resolve(__dirname, '..')
const assets = path.join(frontend, 'src/assets/fonts')
const normalizeLines = text => text.replace(/\r\n?/g, '\n')
const sourceCss = normalizeLines(fs.readFileSync(require.resolve('@mdi/font/css/materialdesignicons.css'), 'utf8'))
const sourceFont = path.resolve(path.dirname(require.resolve('@mdi/font/package.json')), 'fonts/materialdesignicons-webfont.woff2')
const hash = file => crypto.createHash('sha256').update(fs.readFileSync(file)).digest('hex')
const glyphRule = /\.(mdi-[a-z0-9-]+)::before\s*\{\s*content:\s*"\\([A-Fa-f0-9]+)";\s*\}/g
const available = new Map(Array.from(sourceCss.matchAll(glyphRule), match => [match[1], match[2].toUpperCase()]))

function findFiles(directory) {
  return fs.readdirSync(directory, { withFileTypes: true }).flatMap(entry => {
    const file = path.join(directory, entry.name)
    return entry.isDirectory() ? findFiles(file) : /\.(?:vue|[cm]?js)$/.test(entry.name) ? [file] : []
  })
}

function collectIcons() {
  const files = findFiles(path.join(frontend, 'src'))
  // Include aliases and component defaults, including legacy/labs controls.
  const vuetify = path.resolve(path.dirname(require.resolve('vuetify/package.json')), 'lib')
  const icons = new Set()
  for (const file of [...files, ...findFiles(vuetify)]) {
    const text = fs.readFileSync(file, 'utf8')
    for (const match of text.matchAll(/mdi-[a-z0-9-]+/g)) {
      if (available.has(match[0])) icons.add(match[0])
      // Other mdi-* tokens may be generic modifiers or source-map filenames.
      else if (file.startsWith(path.join(frontend, 'src')) && /["'`]/.test(text[match.index - 1] || '')) {
        throw new Error(`Unknown app icon ${match[0]} in ${path.relative(frontend, file)}`)
      }
    }
  }
  return Object.fromEntries([...icons].sort().map(name => [name, available.get(name)]))
}

function makeCss(icons) {
  // Keep the original pseudo-element metrics, sizes, rotations, flip and spin rules.
  return '/* Generated from @mdi/font 5.9.55; see README.md and LICENSE-mdi.txt. */\n' + sourceCss
    .replace(/@font-face\s*\{[^}]*\}/, `@font-face {
  font-family: "Material Design Icons";
  src: url("./moconix-icons.woff2") format("woff2");
  font-weight: normal;
  font-style: normal;
  font-display: block;
}`)
    .replace(glyphRule, (rule, name) => icons[name] ? rule : '')
    .replace(/\/\*# sourceMappingURL=[^*]+\*\//, '')
    .replace(/\r\n?/g, '\n')
    .replace(/\n{3,}/g, '\n\n')
}

const icons = collectIcons()
const manifestPath = path.join(assets, 'icons-manifest.json')
if (process.argv.includes('--prepare')) {
  fs.mkdirSync(assets, { recursive: true })
  fs.writeFileSync(manifestPath, JSON.stringify({ source: '@mdi/font@5.9.55', sourceSha256: hash(sourceFont), icons }, null, 2) + '\n')
  fs.writeFileSync(path.join(assets, 'icons.css'), makeCss(icons))
  console.log(`Prepared ${Object.keys(icons).length} app and Vuetify icons.`)
} else {
  const manifest = JSON.parse(fs.readFileSync(manifestPath, 'utf8'))
  const fail = message => { throw new Error(`${message}. Regenerate with python scripts/subset-icons.py (fonttools[woff] required).`) }
  if (manifest.sourceSha256 !== hash(sourceFont)) fail('The source icon font changed')
  if (JSON.stringify(manifest.icons) !== JSON.stringify(icons)) fail('App or Vuetify icon coverage changed')
  if (normalizeLines(fs.readFileSync(path.join(assets, 'icons.css'), 'utf8')) !== makeCss(icons)) fail('The icon styles changed')
  if (!manifest.subsetSha256 || manifest.subsetSha256 !== hash(path.join(assets, 'moconix-icons.woff2'))) fail('The icon font integrity check failed')
  console.log(`Validated ${Object.keys(icons).length} app and Vuetify icons and the original source font.`)
}
