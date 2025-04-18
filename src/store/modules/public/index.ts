import { defineStore } from 'pinia'
import piniaStore from '/@/store/index'
import { PublicState } from './types'

export const usePublicStore = defineStore('system', {
    persist: true,
    state: (): PublicState => ({
        loading: false
    }),
    actions: {
        setLoading(loading: boolean) {
            this.loading = loading
        }
    }
})

export function useAppOutsideStore() {
    return usePublicStore(piniaStore)
}
