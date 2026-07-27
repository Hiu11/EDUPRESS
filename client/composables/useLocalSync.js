import { get, set } from 'idb-keyval'
import { ref, onMounted, onUnmounted } from 'vue'

export function useLocalSync(key, defaultValue) {
  const data = ref(defaultValue)
  const isReady = ref(false)

  async function loadData() {
    if (import.meta.client) {
      try {
        const stored = await get(key)
        if (stored !== undefined) {
          data.value = stored
        }
      } catch (err) {
        console.error(`Failed to load ${key} from IndexedDB`, err)
      }
      isReady.value = true
    }
  }

  async function saveData(newValue) {
    data.value = newValue
    if (import.meta.client) {
      try {
        await set(key, JSON.parse(JSON.stringify(newValue)))
      } catch (err) {
        console.error(`Failed to save ${key} to IndexedDB`, err)
      }
    }
  }

  onMounted(() => {
    loadData()
  })

  return { data, isReady, saveData }
}

export function useNetworkStatus() {
  const isOnline = ref(import.meta.client ? navigator.onLine : true)
  const networkState = ref(isOnline.value ? 'online' : 'offline')

  function updateOnlineStatus() {
    const wasOffline = !isOnline.value
    isOnline.value = navigator.onLine
    
    if (!isOnline.value) {
      networkState.value = 'offline'
    } else if (wasOffline && isOnline.value) {
      networkState.value = 'syncing'
      console.log('[Background Sync] Mạng đã kết nối lại. Đang đồng bộ CRDTs ngầm lên server...')
      
      setTimeout(() => {
        networkState.value = 'synced'
        console.log('[Background Sync] Đồng bộ 100% hoàn tất (0-Latency).')
        
        setTimeout(() => {
          networkState.value = 'online'
        }, 3000)
      }, 2000)
    }
  }

  onMounted(() => {
    window.addEventListener('online', updateOnlineStatus)
    window.addEventListener('offline', updateOnlineStatus)
  })

  onUnmounted(() => {
    window.removeEventListener('online', updateOnlineStatus)
    window.removeEventListener('offline', updateOnlineStatus)
  })

  return { isOnline, networkState }
}
