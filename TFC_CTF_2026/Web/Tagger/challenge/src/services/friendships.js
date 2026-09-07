const { Op } = require("sequelize");
const { Friendship, Message, User } = require("../models");

function canonicalPair(firstId, secondId) {
  const ids = [Number(firstId), Number(secondId)].sort((a, b) => a - b);
  return { userId: ids[0], friendId: ids[1] };
}

async function areFriends(firstId, secondId, transaction) {
  if (Number(firstId) === Number(secondId)) return false;
  return Boolean(
    await Friendship.findOne({
      where: canonicalPair(firstId, secondId),
      transaction,
    })
  );
}

async function getFriendsWithLatestMessage(userId) {
  const friendships = await Friendship.findAll({
    where: { [Op.or]: [{ userId }, { friendId: userId }] },
    include: [
      { model: User, as: "firstUser", attributes: ["id", "username"] },
      { model: User, as: "secondUser", attributes: ["id", "username"] },
    ],
    order: [["created_at", "DESC"]],
  });

  return Promise.all(
    friendships.map(async (friendship) => {
      const friend =
        friendship.userId === userId
          ? friendship.secondUser
          : friendship.firstUser;
      const latestMessage = await Message.findOne({
        where: {
          [Op.or]: [
            { fromUserId: userId, toUserId: friend.id },
            { fromUserId: friend.id, toUserId: userId },
          ],
        },
        order: [["sentAt", "DESC"]],
      });
      return { friend, latestMessage };
    })
  ).then((items) =>
    items.sort((a, b) => {
      if (!a.latestMessage && !b.latestMessage) {
        return a.friend.username.localeCompare(b.friend.username);
      }
      if (!a.latestMessage) return 1;
      if (!b.latestMessage) return -1;
      return b.latestMessage.sentAt - a.latestMessage.sentAt;
    })
  );
}

module.exports = { areFriends, canonicalPair, getFriendsWithLatestMessage };
