// Optional asset-generation tool, never part of deployment builds.
// Requires Sharp 0.33.2; set MOCONIX_SHARP_MODULE to an existing installation.
// Full-resolution originals are immutable. Only responsive/ is regenerated.
const fs = require('node:fs')
const path = require('node:path')
const crypto = require('node:crypto')
const assert = require('node:assert/strict')
let sharp
try {
  sharp = require(process.env.MOCONIX_SHARP_MODULE || 'sharp')
} catch (error) {
  throw new Error('Install the optional Sharp 0.33.2 tool or set MOCONIX_SHARP_MODULE to an existing installation. ' + error.message)
}
assert.equal(sharp.versions.sharp, '0.33.2', 'Use the documented Sharp 0.33.2 generator to reproduce these assets.')

const frontend = path.resolve(__dirname, '..')
const brand = path.join(frontend, 'src/assets/brand')
const output = path.join(brand, 'responsive')
const assets = [
  { name: 'wordmark', file: 'moconix-wordmark', widths: [512, 1024, 1536], fullDensity: 4 },
  { name: 'youtube', file: 'youtube-wordmark', widths: [400], fullDensity: 2 },
  { name: 'mark', file: 'moconix-mark-transparent', widths: [192, 384, 576, 768], fullDensity: 5 },
  { name: 'kakaotalk', file: 'kakaotalk-mark', widths: [64, 128, 192, 256], fullDensity: 5 },
  { name: 'kmong', file: 'kmong-mark', widths: [64, 128, 192, 256], fullDensity: 5 },
  { name: 'infinox', file: 'infinox-mark', widths: [128, 256, 384, 512], fullDensity: 5 },
  { name: 'utility', file: 'utility-indicator', widths: [96, 192, 288, 384], fullDensity: 5 },
  { name: 'telegram', file: 'telegram-color-mark', widths: [64, 128, 192, 256], fullDensity: 5 },
]
const hash = file => crypto.createHash('sha256').update(fs.readFileSync(file)).digest('hex')
const originals = [
  ...fs.readdirSync(brand).filter(name => /\.(?:png|webp|svg)$/i.test(name)).map(name => path.join(brand, name)),
  ...fs.readdirSync(path.join(frontend, 'public')).filter(name => /^favicon(?:[-.]|$)/.test(name)).map(name => path.join(frontend, 'public', name)),
]
const originalHashes = Object.fromEntries(originals.map(file => [path.relative(frontend, file).replace(/\\/g, '/'), { bytes: fs.statSync(file).size, sha256: hash(file) }]))

async function generate() {
  fs.mkdirSync(output, { recursive: true })
  const variants = []
  const imports = []
  const exports = []
  for (const asset of assets) {
    const source = path.join(brand, asset.file + '.webp')
    const metadata = await sharp(source).metadata()
    const choices = []
    imports.push(`import ${asset.name}Original from '../${asset.file}.webp'`)
    for (const [index, width] of asset.widths.entries()) {
      assert.ok(width < metadata.width, `${asset.name}: every new size must be smaller than its original`)
      // No crop, automatic trim, color edit or sharpening. Resize the complete
      // original canvas once; preserve its transparency and aspect ratio.
      const resized = await sharp(source)
        .resize({ width, kernel: sharp.kernel.lanczos3, withoutEnlargement: true })
        .ensureAlpha()
        .raw()
        .toBuffer({ resolveWithObject: true })
      const filename = `${asset.file}-${width}.webp`
      const destination = path.join(output, filename)
      await sharp(resized.data, { raw: { width: resized.info.width, height: resized.info.height, channels: 4 } })
        .webp({ lossless: true, effort: 6 })
        .toFile(destination)
      const decoded = await sharp(destination).ensureAlpha().raw().toBuffer({ resolveWithObject: true })
      assert.equal(decoded.info.width, resized.info.width)
      assert.equal(decoded.info.height, resized.info.height)
      assert.equal(decoded.data.length, resized.data.length)
      let hiddenRgbDifferences = 0
      for (let offset = 0; offset < resized.data.length; offset += 4) {
        assert.equal(decoded.data[offset + 3], resized.data[offset + 3], `${filename}: alpha changed`)
        for (let channel = 0; channel < 3; channel++) {
          if (resized.data[offset + 3] > 0) assert.equal(decoded.data[offset + channel], resized.data[offset + channel], `${filename}: visible RGB changed`)
          else if (decoded.data[offset + channel] !== resized.data[offset + channel]) hiddenRgbDifferences++
        }
      }
      const variable = `${asset.name}${width}`
      imports.push(`import ${variable} from './${filename}'`)
      choices.push({ variable, density: index + 1 })
      variants.push({ name: asset.name, filename, width: resized.info.width, height: resized.info.height, density: index + 1,
        bytes: fs.statSync(destination).size, sha256: hash(destination), alphaExact: true, visibleRgbExact: true, hiddenRgbDifferences })
    }
    choices.push({ variable: `${asset.name}Original`, density: asset.fullDensity })
    exports.push(`export const ${asset.name} = {\n  src: ${asset.name}Original,\n  srcset: ` + '`' + choices.map(choice => '${' + choice.variable + '} ' + choice.density + 'x').join(', ') + '`' + ',\n}')
  }
  fs.writeFileSync(path.join(output, 'index.js'), '// Generated by scripts/generate-responsive-brand.cjs. Preserve original fallbacks.\n' + imports.join('\n') + '\n\n' + exports.join('\n\n') + '\n')
  for (const file of originals) assert.equal(hash(file), originalHashes[path.relative(frontend, file).replace(/\\/g, '/')].sha256, `Original changed: ${file}`)
  const eaButtonBytes = fs.statSync(path.join(brand, 'ea-experience-button.webp')).size
  const initialNames = ['wordmark', 'youtube', 'mark', 'kmong', 'infinox', 'utility']
  const initialTotals = {}
  for (const locale of ['ko', 'en']) {
    const names = [...initialNames, locale === 'ko' ? 'kakaotalk' : 'telegram']
    initialTotals[locale] = { fullResolution: eaButtonBytes + names.reduce((sum, name) => sum + fs.statSync(path.join(brand, assets.find(asset => asset.name === name).file + '.webp')).size, 0), densities: {} }
    for (const density of [1, 2, 3, 4]) {
      initialTotals[locale].densities[density] = eaButtonBytes + names.reduce((sum, name) => {
        const asset = assets.find(candidate => candidate.name === name)
        const choice = variants.find(candidate => candidate.name === name && candidate.density === density)
        return sum + (choice ? choice.bytes : fs.statSync(path.join(brand, asset.file + '.webp')).size)
      }, 0)
    }
  }
  const report = { generator: { sharp: sharp.versions.sharp, vips: sharp.versions.vips, webp: sharp.versions.webp, kernel: 'lanczos3', losslessWebp: true },
    originalsUnchanged: true, originalHashes, variants, initialTotals,
    note: 'DPR totals are nominal srcset choices, not measured requests. Browsers may reuse a cached larger candidate or adapt to network conditions. Resampling is intentional; lossless refers to preserving the resized pixels during WebP encoding.' }
  const reportIndex = process.argv.indexOf('--report-dir')
  if (reportIndex !== -1) {
    const reportDirectory = path.resolve(process.argv[reportIndex + 1])
    fs.mkdirSync(reportDirectory, { recursive: true })
    fs.writeFileSync(path.join(reportDirectory, 'responsive-image-report.json'), JSON.stringify(report, null, 2) + '\n')
  }
  console.log(JSON.stringify({ variants: variants.length, generatedBytes: variants.reduce((sum, item) => sum + item.bytes, 0), originalFilesUnchanged: originals.length, initialTotals }, null, 2))
}
generate().catch(error => { console.error(error); process.exitCode = 1 })
