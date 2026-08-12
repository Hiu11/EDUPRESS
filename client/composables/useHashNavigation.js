import { ref } from 'vue'

export function useHashNavigation({ onCourseDetail, onLeaveCourseDetail } = {}) {
  const route = ref('home')
  const selectedCourseId = ref('ai')

  function applyRoute(nextRoute, courseId) {
    route.value = nextRoute || 'home'
    if (courseId) selectedCourseId.value = courseId

    if (nextRoute === 'course-detail' && courseId) {
      onCourseDetail?.(courseId)
    } else {
      onLeaveCourseDetail?.()
    }
  }

  function executeNavigation(nextRoute, courseId) {
    applyRoute(nextRoute, courseId)
    window.location.hash = courseId ? `${nextRoute}/${courseId}` : nextRoute
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }

  function navigate(nextRoute, courseId) {
    if (document.startViewTransition) {
      document.startViewTransition(() => {
        executeNavigation(nextRoute, courseId)
      })
    } else {
      executeNavigation(nextRoute, courseId)
    }
  }

  function handleHashChange() {
    const hash = window.location.hash.replace('#', '')
    if (!hash) {
      applyRoute('home')
      return
    }

    const [nextRoute, courseId] = hash.split('/')
    applyRoute(nextRoute, courseId)
  }

  function syncHashRoute() {
    handleHashChange()
    window.addEventListener('hashchange', handleHashChange)
  }

  return {
    route,
    selectedCourseId,
    navigate,
    syncHashRoute,
  }
}
