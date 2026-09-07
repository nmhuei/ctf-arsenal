const express = require("express");
const { Op } = require("sequelize");
const { FriendRequest, Friendship, User, sequelize } = require("../models");
const { requireAuth } = require("../middleware/auth");
const { areFriends, canonicalPair } = require("../services/friendships");

const router = express.Router();

router.get("/requests", requireAuth, async (req, res) => {
  const [incoming, outgoing] = await Promise.all([
    FriendRequest.findAll({
      where: { toUserId: req.user.id, status: "pending" },
      include: [{ model: User, as: "sender", attributes: ["id", "username"] }],
      order: [["created_at", "DESC"]],
    }),
    FriendRequest.findAll({
      where: { fromUserId: req.user.id, status: "pending" },
      include: [
        { model: User, as: "recipient", attributes: ["id", "username"] },
      ],
      order: [["created_at", "DESC"]],
    }),
  ]);
  res.render("friends/requests", {
    title: "Friend requests",
    incoming,
    outgoing,
  });
});

router.post("/friends/request/:userId", requireAuth, async (req, res) => {
  const toUserId = Number(req.params.userId);
  if (!Number.isInteger(toUserId) || toUserId === req.user.id) {
    return res.redirect("/discover?error=Invalid+friend+request.");
  }

  const target = await User.findOne({ where: { id: toUserId, hidden: false } });
  if (!target) {
    return res.redirect("/discover?error=That+user+is+not+available.");
  }
  if (await areFriends(req.user.id, toUserId)) {
    return res.redirect("/discover?error=You+are+already+friends.");
  }
  const pending = await FriendRequest.findOne({
    where: {
      status: "pending",
      [Op.or]: [
        { fromUserId: req.user.id, toUserId },
        { fromUserId: toUserId, toUserId: req.user.id },
      ],
    },
  });
  if (pending) {
    return res.redirect("/discover?error=A+friend+request+is+already+pending.");
  }

  await FriendRequest.create({ fromUserId: req.user.id, toUserId });
  res.redirect(
    `/discover?notice=Request+sent+to+${encodeURIComponent(target.username)}.`
  );
});

router.post("/friends/accept/:requestId", requireAuth, async (req, res) => {
  await sequelize.transaction(async (transaction) => {
    const request = await FriendRequest.findOne({
      where: {
        id: Number(req.params.requestId),
        toUserId: req.user.id,
        status: "pending",
      },
      transaction,
    });
    if (!request) {
      const error = new Error("That request is not addressed to you.");
      error.status = 403;
      error.expose = true;
      throw error;
    }
    await Friendship.findOrCreate({
      where: canonicalPair(request.fromUserId, request.toUserId),
      defaults: canonicalPair(request.fromUserId, request.toUserId),
      transaction,
    });
    await request.update({ status: "accepted" }, { transaction });
  });
  res.redirect("/requests?notice=Friend+request+accepted.");
});

router.post("/friends/reject/:requestId", requireAuth, async (req, res) => {
  const request = await FriendRequest.findOne({
    where: {
      id: Number(req.params.requestId),
      toUserId: req.user.id,
      status: "pending",
    },
  });
  if (!request) {
    const error = new Error("That request is not addressed to you.");
    error.status = 403;
    error.expose = true;
    throw error;
  }
  await request.update({ status: "rejected" });
  res.redirect("/requests?notice=Friend+request+rejected.");
});

module.exports = router;
