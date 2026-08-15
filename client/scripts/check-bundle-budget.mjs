import { existsSync, readdirSync, statSync } from 'node:fs'
import { join } from 'node:path'

const root = process.cwd()
const assetDirCandidates = [
  join(root, '.vercel/output/static/_nuxt'),
  join(root, '.output/public/_nuxt'),
  join(root, 'dist/_nuxt'),
  join(root, 'node_modules/.cache/nuxt/.nuxt/dist/client/_nuxt'),
  join(root, '.nuxt/dist/client/_nuxt'),
]

const assetDir = assetDirCandidates.find((candidate) => existsSync(candidate))

if (!assetDir) {
  console.error('Bundle budget check could not find Nuxt client assets. Run npm run build before this check.')
  process.exit(1)
}

function walk(dir, files = []) {
  for (const entry of readdirSync(dir, { withFileTypes: true })) {
    const fullPath = join(dir, entry.name)
    if (entry.isDirectory()) {
      walk(fullPath, files)
    } else {
      files.push(fullPath)
    }
  }
  return files
}

function kb(bytes) {
  return bytes / 1024
}

const budgets = {
  maxTotalJsKb: Number(process.env.BUNDLE_MAX_TOTAL_JS_KB || 1500),
  maxTotalCssKb: Number(process.env.BUNDLE_MAX_TOTAL_CSS_KB || 160),
  maxSingleJsChunkKb: Number(process.env.BUNDLE_MAX_JS_CHUNK_KB || 1100),
  maxEntryCssKb: Number(process.env.BUNDLE_MAX_ENTRY_CSS_KB || 80),
}

const assets = walk(assetDir).map((file) => ({
  file,
  name: file.replace(`${assetDir}\\`, '').replace(`${assetDir}/`, ''),
  size: statSync(file).size,
}))

const jsAssets = assets.filter((asset) => asset.name.endsWith('.js'))
const cssAssets = assets.filter((asset) => asset.name.endsWith('.css'))
const totalJsKb = kb(jsAssets.reduce((sum, asset) => sum + asset.size, 0))
const totalCssKb = kb(cssAssets.reduce((sum, asset) => sum + asset.size, 0))
const largestJs = [...jsAssets].sort((a, b) => b.size - a.size)[0]
const entryCss = cssAssets.find((asset) => asset.name.startsWith('entry.'))

let failed = false

console.log(`Bundle assets directory: ${assetDir}`)
console.log(`Total emitted JS: ${totalJsKb.toFixed(1)} KB`)
console.log(`Total emitted CSS: ${totalCssKb.toFixed(1)} KB`)

if (largestJs) {
  console.log(`Largest JS chunk: ${largestJs.name} (${kb(largestJs.size).toFixed(1)} KB)`)
}

if (entryCss) {
  console.log(`Entry CSS: ${entryCss.name} (${kb(entryCss.size).toFixed(1)} KB)`)
}

const topChunks = [...jsAssets]
  .sort((a, b) => b.size - a.size)
  .slice(0, 5)
  .map((asset) => `- ${asset.name}: ${kb(asset.size).toFixed(1)} KB`)

if (topChunks.length) {
  console.log(['Largest JS chunks:', ...topChunks].join('\n'))
}

if (totalJsKb > budgets.maxTotalJsKb) {
  console.error(`Total JS budget exceeded: ${totalJsKb.toFixed(1)} KB > ${budgets.maxTotalJsKb} KB`)
  failed = true
}

if (totalCssKb > budgets.maxTotalCssKb) {
  console.error(`Total CSS budget exceeded: ${totalCssKb.toFixed(1)} KB > ${budgets.maxTotalCssKb} KB`)
  failed = true
}

if (largestJs && kb(largestJs.size) > budgets.maxSingleJsChunkKb) {
  console.error(`Single JS chunk budget exceeded: ${kb(largestJs.size).toFixed(1)} KB > ${budgets.maxSingleJsChunkKb} KB`)
  failed = true
}

if (entryCss && kb(entryCss.size) > budgets.maxEntryCssKb) {
  console.error(`Entry CSS budget exceeded: ${kb(entryCss.size).toFixed(1)} KB > ${budgets.maxEntryCssKb} KB`)
  failed = true
}

if (failed) process.exit(1)

console.log('Bundle budget check passed.')
