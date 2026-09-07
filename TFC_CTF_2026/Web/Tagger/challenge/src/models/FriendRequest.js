const { DataTypes } = require("sequelize");
const sequelize = require("../config/database");

const FriendRequest = sequelize.define(
  "FriendRequest",
  {
    id: { type: DataTypes.INTEGER, autoIncrement: true, primaryKey: true },
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
    status: {
      type: DataTypes.ENUM("pending", "accepted", "rejected"),
      allowNull: false,
      defaultValue: "pending",
    },
  },
  {
    tableName: "friend_requests",
    createdAt: "created_at",
    updatedAt: "updated_at",
    indexes: [
      { fields: ["from_user_id", "to_user_id", "status"] },
      { fields: ["to_user_id", "status"] },
    ],
  }
);

module.exports = FriendRequest;
