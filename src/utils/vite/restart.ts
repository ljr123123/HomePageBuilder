/**
 * @name ConfigRestartPlugin
 * @description 监听配置文件修改后自动重启
 */
import ViteRestart from 'vite-plugin-restart'

const ViteRestartValue = () => {
    try {
        return ViteRestart({
            restart: ['*.config.[jt]s', '**/config/*.[jt]s']
        })
    } catch {
        return ViteRestart.default({
            restart: ['*.config.[jt]s', '**/config/*.[jt]s']
        })
    }
}

export const ConfigRestartPlugin = () => {
    return ViteRestartValue()
}
