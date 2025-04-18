export interface RequestOptions {
    isTransformResponse?: boolean
}

/**
 * @description 请求的响应结果
 */
export interface IResponse<T = any> {
    code: number | string
    result: T
    message: string
    status: string | number
}

/**
 * @description 登录参数
 */
export interface ILogin {
    username: string
    password: string
}
