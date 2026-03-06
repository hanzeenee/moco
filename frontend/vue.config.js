// root/frontend/vue.config.js
const { defineConfig } = require("@vue/cli-service");
const path = require("path");

module.exports = defineConfig({
  // ✅ 반드시 배열이어야 함 (vuetify 트랜스파일)
  transpileDependencies: ["vuetify"],

  // ✅ Django 연동: build 산출물 자동 배치
  // - home.html  => root/backend/templates/home.html
  // - js/css/img => root/backend/static/frontend/static/...
  publicPath: "/static/frontend/",
  outputDir: path.resolve(__dirname, "../backend/static/frontend"),
  assetsDir: "static",
  indexPath: path.resolve(__dirname, "../backend/templates/home.html"),
  productionSourceMap: false,

  pluginOptions: {
    vuetify: {
      // vuetify-loader 옵션 자리
    },
  },
});