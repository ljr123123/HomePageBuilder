/**
 * @name AutoRegistryComponents
 * @description 自动引入组件
 */
import Components from 'unplugin-vue-components/vite'

export const AutoRegistryComponents = () => {
    return Components({
        dirs: ['src/components'],
        extensions: ['vue'],
        deep: true,
        dts: 'types/components.d.ts',
        directoryAsNamespace: false,
        globalNamespaces: [],
        directives: true,
        importPathTransform: (v) => v,
        allowOverrides: false,
        include: [/\.vue$/, /\.vue\?vue/],
        exclude: [/[\\/]node_modules[\\/]/, /[\\/]\.git[\\/]/, /[\\/]\.nuxt[\\/]/]
    })
}
