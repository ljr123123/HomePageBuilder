/**
 * @name ConfigCompressPlugin
 * @description 开启.gz压缩
 */
import viteCompression from 'vite-plugin-compression'
import { SOURCE_COMPRESSION } from '../../config/constant'

export const ConfigCompressPlugin = () => {
    if (SOURCE_COMPRESSION) {
        return viteCompression({
            // 默认
            verbose: true,
            // false：开启压缩
            disable: false,
            // 删除源文件
            deleteOriginFile: false,
            // 压缩器最小文件大小
            threshold: 10240,
            // 压缩算法
            algorithm: 'gzip',
            // 文件类型
            ext: '.gz'
        })
    }
    return []
}
