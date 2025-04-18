/**
 * @name ConfigProgressPlugin
 * @description 构建项目时显示进度条
 */

import progress from 'vite-plugin-progress'

export const ConfigProgressPlugin = () => {
    return progress()
}
