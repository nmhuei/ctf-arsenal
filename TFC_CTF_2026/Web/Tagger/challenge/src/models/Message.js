const { DataTypes } = require("sequelize");
const sequelize = require("../config/database");

const Message = sequelize.define(
  "Message",
  {
    id: { type: DataTypes.INTEGER, autoIncrement: true, primaryKey: true },
    tagName: {
      type: DataTypes.STRING(16),
      allowNull: false,
      field: "tag_name",
    },
    type: {
      type: DataTypes.ENUM("text", "image"),
      allowNull: false,
    },
    attributes: { type: DataTypes.JSON, allowNull: false, defaultValue: {} },
    content: { type: DataTypes.TEXT, allowNull: false },
    fromUserId: {
      type: DataTypes.INTEGER,
      allowNull: false,
      field: "from_user_id",
    },
    toUserId: {
      type: DataTypes.INTEGER,
      allowNull: false,
      field: "to_user_id",
    },
    sentAt: {
      type: DataTypes.DATE,
      allowNull: false,
      defaultValue: DataTypes.NOW,
      field: "sent_at",
    },
  },
  {
    tableName: "messages",
    timestamps: false,
    indexes: [
      { fields: ["from_user_id", "to_user_id", "sent_at"] },
      { fields: ["to_user_id", "from_user_id", "sent_at"] },
    ],
  }
);

module.exports = Message;
