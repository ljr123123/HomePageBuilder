import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios'
import { useRouter } from 'vue-router'
import { errMessage } from './status'
import { IResponse } from './type'
import { REQUEST_TIME_OUT, VITE_OPEN_PROXY, API_TARGET_URL, API_BASE_URL } from '/@/config/constant'
import { usePublicStore } from '/@/store/index'
// 超时时间
axios.defaults.timeout = REQUEST_TIME_OUT
// 跨域请求是否需要凭证
axios.defaults.withCredentials = false
// 允许跨域
axios.defaults.headers.post['Access-Control-Allow-Origin-Type'] = '*'
const axiosInstance: AxiosInstance = axios.create({
    baseURL: VITE_OPEN_PROXY ? API_BASE_URL : API_TARGET_URL,
    headers: {
        'Content-Type': 'application/json'
    }
})

export interface IAxiosRequestConfig extends AxiosRequestConfig {
    showToast?: boolean
}

export interface IAxiosResponse extends AxiosResponse {
    config: IAxiosRequestConfig
}

axiosInstance.interceptors.response.use(
    (response: IAxiosResponse) => {
        const publicStore = usePublicStore()
        publicStore.setLoading(false)
        const {
            config: { showToast }
        } = response
        const { code, message } = response.data
        if (response.status === 200 && code === 200) {
            return Promise.resolve(response.data)
        } else if (code === 301) {
            const router = useRouter()
            router.replace('/login')
            return
        }
        // TODO: error toast

        return Promise.resolve(response)
    },
    (error: any) => {
        const publicStore = usePublicStore()
        publicStore.setLoading(false)
        const { response } = error
        if (response) {
            errMessage(response.status)
            return Promise.reject(response.data)
        }
        errMessage('网络连接错误，请稍后再试！')
    }
)

axiosInstance.interceptors.request.use(
    (config: IAxiosRequestConfig) => {
        const publicStore = usePublicStore()

        // TODO: Authorizations

        publicStore.setLoading(false)

        return config
    },
    (error: any) => {
        const publicStore = usePublicStore()
        publicStore.setLoading(false)
        return Promise.reject(error)
    }
)

const request = <T = any>(config: IAxiosRequestConfig): Promise<T> => {
    const conf = { ...config }
    return new Promise((resolve) => {
        axiosInstance
            .request<any, AxiosResponse<IResponse>>(conf)
            .then((res: AxiosResponse<IResponse>) => {
                resolve(res as T)
            })
    })
}

export function get<T = any>(config: IAxiosRequestConfig): Promise<T> {
    const { showToast = true } = config.params || {}
    return request({ ...config, showToast, method: 'GET' })
}

export function post<T = any>(config: IAxiosRequestConfig): Promise<T> {
    const { showToast = true } = config.params || {}
    return request({ ...config, showToast, method: 'POST' })
}

export default request
export type { AxiosInstance, AxiosResponse }
