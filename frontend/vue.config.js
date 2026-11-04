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
    // Keep every responsive candidate as a file, so unselected image sizes are
    // not embedded in the initial JavaScript or prerendered HTML as base64.
    const responsiveImages = path.resolve(__dirname, "src/assets/brand/responsive");
    const imageRule = config.module.rule("images");
    imageRule.exclude.add(responsiveImages);
    config.module.rule("responsive-images")
      .test(/\.webp$/i)
      .include.add(responsiveImages).end()
      .set("type", "asset/resource")
      .set("generator", imageRule.get("generator"));
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
