import { createPinia } from 'pinia'
import { usePublicStore } from './modules/public'

import piniaPluginPersistedstate from 'pinia-plugin-persistedstate'

const pinia = createPinia()
pinia.use(piniaPluginPersistedstate)

export { usePublicStore }

export default pinia
