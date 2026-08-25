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
    if (!course || !course.image) return generatedAsset('course-web-bg.png')
    if (typeof course.image === 'string' && (course.image.startsWith('http') || course.image.startsWith('/'))) {
      return course.image
    }
    return generatedAsset(course.image)
  }

  return {
    asset,
    generatedAsset,
    courseImage,
  }
}
