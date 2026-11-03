const { defineConfig } = require("@vue/cli-service");
const path = require("path");

const prerenderBuild = process.env.MOCONIX_PRERENDER_BUILD === "1";

module.exports = defineConfig({
  transpileDependencies: ["vuetify"],
  publicPath: "/static/frontend/",
  outputDir: path.resolve(__dirname, prerenderBuild ? ".prerender" : "../backend/static/frontend"),
  assetsDir: "static",
  indexPath: prerenderBuild ? "index.html" : path.resolve(__dirname, "../backend/templates/home.html"),
  productionSourceMap: false,
  chainWebpack(config) {
    if (!prerenderBuild) return;
    // Compile the same SFCs in production mode, retaining their CSS scope IDs.
    config.target("node");
    config.entry("app").clear().add("./src/entry-prerender.js");
    config.output.filename("render.cjs").chunkFilename("[name].cjs").libraryTarget("commonjs2");
    config.optimization.splitChunks(false).runtimeChunk(false).minimize(false);
    config.plugins.delete("html");
    config.plugins.delete("preload");
    config.plugins.delete("prefetch");
    config.plugins.delete("copy");
  },
});
