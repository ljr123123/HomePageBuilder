/**
 * @name ConfigPagesPlugin
 * @description 动态生成路由
 */
import Pages from 'vite-plugin-pages'

export const ConfigPagesPlugin = () => {
    return Pages({
        pagesDir: [{ dir: 'src/views', baseRoute: '' }],
        importMode: 'async',
        extensions: ['vue', 'md'],
        exclude: ['**/components/*.vue']
    })
}
