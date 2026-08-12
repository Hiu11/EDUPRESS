const ASSET_BASE = '/legacy-assets/'
const GENERATED_BASE = '/generated-assets/'

export function useAssetPaths() {
  function asset(name) {
    return `${ASSET_BASE}${name}`
  }

  function generatedAsset(name) {
    return `${GENERATED_BASE}${name}`
  }

  function courseImage(course) {
    return generatedAsset(course.image)
  }

  return {
    asset,
    generatedAsset,
    courseImage,
  }
}
