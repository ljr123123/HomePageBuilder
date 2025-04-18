export const errMessage = (status: number | string): string => {
    let message = ''

    switch (status) {
        case 301:
            message = `需要登录(${status})`
            break
        case 400:
            message = `请求错误(${status})`
            break
        case 401:
            message = `未授权，请重新登录(${status})`
            break
        case 403:
            message = `拒绝访问(${status})`
            break
        case 404:
            message = `请求出错(${status})`
            break
        case 408:
            message = `请求超时(${status})`
            break
        case 500:
            message = `服务器错误(${status})`
            break
        case 501:
            message = `服务未实现(${status})`
            break
        case 502:
            message = `网络错误(${status})`
            break
        case 503:
            message = `服务不可用(${status})`
            break
        case 504:
            message = `网络超时(${status})`
            break
        case 505:
            message = `HTTP版本不受支持(${status})`
            break
        default:
            message = `连接出错(${status})`
    }

    return `${message}，请检查网络或联系管理员！`
}
