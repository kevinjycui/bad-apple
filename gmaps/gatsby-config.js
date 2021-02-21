const path = require(`path`);

module.exports = {
  siteMetadata: {
    title: "Bad Apple",
  },
  plugins: [
    {
      resolve: `gatsby-source-filesystem`,
      options: {
        path: path.join(__dirname, `src`, `images`),
      },
    },
    `gatsby-plugin-sharp`,
    `gatsby-transformer-sharp`,
  ],
  flags: {
    DEV_SSR: false
  }
};
