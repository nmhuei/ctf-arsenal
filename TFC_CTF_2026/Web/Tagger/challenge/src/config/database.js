const path = require("path");
const { Sequelize } = require("sequelize");

const storage =
  process.env.DATABASE_STORAGE ||
  path.join(__dirname, "..", "data", "tagger.sqlite");

const sequelize = new Sequelize({
  dialect: "sqlite",
  storage,
  logging: false,
  define: {
    underscored: true,
    freezeTableName: true,
  },
});

module.exports = sequelize;
