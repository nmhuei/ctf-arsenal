const crypto = require("node:crypto");
const jwt = require("jsonwebtoken");
const { User } = require("../models");

const sessionSecret = crypto.randomBytes(64).toString("base64url");

function getSecret() {
  return sessionSecret;
}

async function loadUser(req, res, next) {
  req.user = null;
  const token = req.cookies?.tagger_session;

  if (token) {
    try {
      const payload = jwt.verify(token, getSecret());
      req.user = await User.findByPk(payload.userId, {
        attributes: ["id", "username", "hidden", "created_at"],
      });
    } catch (_error) {
      res.clearCookie("tagger_session");
    }
  }

  res.locals.currentUser = req.user;
  next();
}

function requireAuth(req, res, next) {
  if (!req.user) {
    return res.redirect("/login?error=Please+log+in+to+continue.");
  }
  next();
}

function requireGuest(req, res, next) {
  if (req.user) return res.redirect("/chat");
  next();
}

module.exports = { getSecret, loadUser, requireAuth, requireGuest };
