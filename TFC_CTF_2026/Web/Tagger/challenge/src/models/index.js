const sequelize = require("../config/database");
const User = require("./User");
const FriendRequest = require("./FriendRequest");
const Friendship = require("./Friendship");
const Message = require("./Message");

FriendRequest.belongsTo(User, { as: "sender", foreignKey: "fromUserId" });
FriendRequest.belongsTo(User, { as: "recipient", foreignKey: "toUserId" });
User.hasMany(FriendRequest, { as: "sentRequests", foreignKey: "fromUserId" });
User.hasMany(FriendRequest, {
  as: "receivedRequests",
  foreignKey: "toUserId",
});

Message.belongsTo(User, { as: "sender", foreignKey: "fromUserId" });
Message.belongsTo(User, { as: "recipient", foreignKey: "toUserId" });

Friendship.belongsTo(User, { as: "firstUser", foreignKey: "userId" });
Friendship.belongsTo(User, { as: "secondUser", foreignKey: "friendId" });

module.exports = { sequelize, User, FriendRequest, Friendship, Message };
