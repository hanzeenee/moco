const { defineConfig } = require("@vue/cli-service");
const path = require("path");

module.exports = defineConfig({
  transpileDependencies: ["vuetify"],
  publicPath: "/static/frontend/",
  outputDir: path.resolve(__dirname, "../backend/static/frontend"),
  assetsDir: "static",
  indexPath: path.resolve(__dirname, "../backend/templates/home.html"),
  productionSourceMap: false,
});
