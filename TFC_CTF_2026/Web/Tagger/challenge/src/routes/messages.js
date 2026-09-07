const express = require("express");
const multer = require("multer");
const { Op } = require("sequelize");
const { Message, User } = require("../models");
const { requireAuth } = require("../middleware/auth");
const {
  areFriends,
  getFriendsWithLatestMessage,
} = require("../services/friendships");

const router = express.Router();
const messageHistoryCache = new Map();
const messageHistoryTtl = 60 * 1000;
const allowedTypes = new Set([
  "image/png",
  "image/jpeg",
  "image/gif",
  "image/webp",
]);
const upload = multer({
  storage: multer.memoryStorage(),
  limits: { fileSize: 5 * 1024 * 1024, files: 1 },
  fileFilter: (_req, file, callback) => {
    callback(
      allowedTypes.has(file.mimetype)
        ? null
        : Object.assign(new Error("Unsupported image type."), {
            status: 400,
            expose: true,
          }),
      allowedTypes.has(file.mimetype)
    );
  },
});


function messageRecord(body, defaults) {
  const protectedFields = new Set(["id", "fromUserId", "toUserId", "sentAt"]);
  const record = { ...defaults };

  for (const field of Object.keys(Message.getAttributes())) {
    if (!protectedFields.has(field) && body[field] !== undefined) {
      record[field] = body[field];
    }
  }

  if (typeof record.attributes === "string") {
    try {
      record.attributes = JSON.parse(record.attributes);
    } catch {
      record.attributes = {};
    }
  }

  return record;
}

function messageHistoryKey(firstUsername, secondUsername) {
  return `${firstUsername.trim()}:${secondUsername.trim()}`;
}

async function getMessageHistory(
  firstId,
  secondId,
  firstUsername,
  secondUsername
) {
  const key = messageHistoryKey(firstUsername, secondUsername);
  const cached = messageHistoryCache.get(key);

  if (cached && cached.expiresAt > Date.now()) return cached.messages;
  if (cached) messageHistoryCache.delete(key);

  const messages = Message.findAll({
    where: {
      [Op.or]: [
        { fromUserId: firstId, toUserId: secondId },
        { fromUserId: secondId, toUserId: firstId },
      ],
    },
    order: [["sentAt", "ASC"]],
    limit: 500,
  });

  messageHistoryCache.set(key, {
    expiresAt: Date.now() + messageHistoryTtl,
    messages,
  });

  try {
    return await messages;
  } catch (error) {
    if (messageHistoryCache.get(key)?.messages === messages) {
      messageHistoryCache.delete(key);
    }
    throw error;
  }
}

function invalidateMessageHistory(firstUsername, secondUsername) {
  messageHistoryCache.delete(messageHistoryKey(firstUsername, secondUsername));
}

function detectedImageType(buffer) {
  if (buffer.subarray(0, 8).equals(Buffer.from("89504e470d0a1a0a", "hex")))
    return "image/png";
  if (buffer.subarray(0, 3).equals(Buffer.from("ffd8ff", "hex")))
    return "image/jpeg";
  if (["GIF87a", "GIF89a"].includes(buffer.subarray(0, 6).toString("ascii")))
    return "image/gif";
  if (
    buffer.subarray(0, 4).toString("ascii") === "RIFF" &&
    buffer.subarray(8, 12).toString("ascii") === "WEBP"
  )
    return "image/webp";
  return null;
}

async function loadFriend(req, _res, next) {
  const friendId = Number(req.params.friendId);
  if (
    !Number.isInteger(friendId) ||
    !(await areFriends(req.user.id, friendId))
  ) {
    const error = new Error("You can only open chats with accepted friends.");
    error.status = 403;
    error.expose = true;
    return next(error);
  }
  req.friend = await User.findByPk(friendId, {
    attributes: ["id", "username"],
  });
  next();
}

router.get("/chat", requireAuth, async (req, res) => {
  const conversations = await getFriendsWithLatestMessage(req.user.id);
  res.render("chat/index", {
    title: "Chat",
    conversations,
    friend: null,
    messages: [],
  });
});

router.get("/chat/:friendId", requireAuth, loadFriend, async (req, res) => {
  const [conversations, messages] = await Promise.all([
    getFriendsWithLatestMessage(req.user.id),
    getMessageHistory(
      req.user.id,
      req.friend.id,
      req.user.username,
      req.friend.username
    ),
  ]);
  res.render("chat/index", {
    title: `Chat with ${req.friend.username}`,
    conversations,
    friend: req.friend,
    messages,
  });
});

router.post(
  "/chat/:friendId/message",
  requireAuth,
  loadFriend,
  upload.single("image"),
  async (req, res) => {
    const text = String(req.body.message || "").trim();
    if (req.file) {
      const mimeType = detectedImageType(req.file.buffer);
      if (!mimeType || mimeType !== req.file.mimetype) {
        const error = new Error(
          "The uploaded file is not a valid supported image."
        );
        error.status = 400;
        error.expose = true;
        throw error;
      }
      await Message.create(
        messageRecord(req.body, {
          tagName: "img",
          type: "image",
          attributes: { alt: "uploaded image" },
          content: `data:${mimeType};base64,${req.file.buffer.toString("base64")}`,
          fromUserId: req.user.id,
          toUserId: req.friend.id,
        })
      );
    } else if (text) {
      if (text.length > 4000) {
        return res.redirect(
          `/chat/${req.friend.id}?error=Message+is+too+long.`
        );
      }
      await Message.create(
        messageRecord(req.body, {
          tagName: "message",
          type: "text",
          attributes: {},
          content: text,
          fromUserId: req.user.id,
          toUserId: req.friend.id,
        })
      );
    } else {
      return res.redirect(
        `/chat/${req.friend.id}?error=Write+a+message+or+choose+an+image.`
      );
    }
    invalidateMessageHistory(req.user.username, req.friend.username);
    res.redirect(`/chat/${req.friend.id}`);
  }
);

module.exports = router;
