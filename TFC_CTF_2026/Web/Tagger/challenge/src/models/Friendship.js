const { DataTypes } = require("sequelize");
const sequelize = require("../config/database");

const Friendship = sequelize.define(
  "Friendship",
  {
    id: { type: DataTypes.INTEGER, autoIncrement: true, primaryKey: true },
    userId: {
      type: DataTypes.INTEGER,
      allowNull: false,
      field: "user_id",
      validate: {
        isLessThanFriend(value) {
          if (value >= this.friendId) {
            throw new Error("Friendships must use canonical user ID order.");
          }
        },
      },
    },
    friendId: {
      type: DataTypes.INTEGER,
      allowNull: false,
      field: "friend_id",
    },
  },
  {
    tableName: "friendships",
    createdAt: "created_at",
    updatedAt: false,
    indexes: [{ unique: true, fields: ["user_id", "friend_id"] }],
  }
);

module.exports = Friendship;
