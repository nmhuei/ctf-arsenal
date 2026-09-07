const express = require("express");
const { Op } = require("sequelize");
const { FriendRequest, Friendship, User } = require("../models");
const { requireAuth } = require("../middleware/auth");

const router = express.Router();

router.get("/discover", requireAuth, async (req, res) => {
  const q = String(req.query.q || "")
    .trim()
    .slice(0, 64);
  const users = await User.findAll({
    where: {
      hidden: false,
      id: { [Op.ne]: req.user.id },
      ...(q ? { username: { [Op.like]: `%${q}%` } } : {}),
    },
    attributes: ["id", "username", "created_at"],
    order: [["username", "ASC"]],
    limit: 50,
  });

  const [friendships, pendingRequests] = await Promise.all([
    Friendship.findAll({
      where: {
        [Op.or]: [{ userId: req.user.id }, { friendId: req.user.id }],
      },
    }),
    FriendRequest.findAll({
      where: {
        status: "pending",
        [Op.or]: [{ fromUserId: req.user.id }, { toUserId: req.user.id }],
      },
    }),
  ]);
  const friendIds = new Set(
    friendships.map((item) =>
      item.userId === req.user.id ? item.friendId : item.userId
    )
  );
  const requestByUserId = new Map();
  pendingRequests.forEach((request) => {
    const otherId =
      request.fromUserId === req.user.id
        ? request.toUserId
        : request.fromUserId;
    requestByUserId.set(otherId, request);
  });

  res.render("friends/discover", {
    title: "Discover",
    q,
    users,
    friendIds,
    requestByUserId,
  });
});

module.exports = router;
