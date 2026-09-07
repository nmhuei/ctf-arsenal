const express = require("express");
const bcrypt = require("bcryptjs");
const jwt = require("jsonwebtoken");
const { UniqueConstraintError } = require("sequelize");
const { User } = require("../models");
const { getSecret, requireGuest } = require("../middleware/auth");

const router = express.Router();
const usernamePattern = /^[a-zA-Z0-9_ ]{3,32}$/;

function setSession(res, user) {
  const token = jwt.sign(
    { userId: user.id, username: user.username },
    getSecret(),
    { expiresIn: "7d" }
  );
  res.cookie("tagger_session", token, {
    httpOnly: true,
    sameSite: "lax",
    maxAge: 7 * 24 * 60 * 60 * 1000,
  });
}

router.get("/login", requireGuest, (req, res) => {
  res.render("auth/login", { title: "Log in" });
});

router.post("/login", requireGuest, async (req, res) => {
  const username = String(req.body.username || "");
  const password = String(req.body.password || "");
  const user = await User.findOne({ where: { username } });

  if (!user || !(await bcrypt.compare(password, user.passwordHash))) {
    return res.status(401).render("auth/login", {
      title: "Log in",
      error: "Invalid username or password.",
      form: { username },
    });
  }

  setSession(res, user);
  res.redirect("/chat");
});

router.get("/register", requireGuest, (req, res) => {
  res.render("auth/register", { title: "Register" });
});

router.post("/register", requireGuest, async (req, res) => {
  const username = String(req.body.username || "");
  const password = String(req.body.password || "");
  const confirmPassword = String(req.body.confirmPassword || "");

  if (!usernamePattern.test(username)) {
    return res.status(400).render("auth/register", {
      title: "Register",
      error: "Use 3–32 letters, numbers, or underscores for your username.",
      form: { username },
    });
  }
  if (password.length < 8) {
    return res.status(400).render("auth/register", {
      title: "Register",
      error: "Your password must be at least 8 characters.",
      form: { username },
    });
  }
  if (password !== confirmPassword) {
    return res.status(400).render("auth/register", {
      title: "Register",
      error: "Those passwords do not match.",
      form: { username },
    });
  }

  try {
    const passwordHash = await bcrypt.hash(password, 12);
    const user = await User.create({ username, passwordHash });
    setSession(res, user);
    res.redirect("/chat?notice=Welcome+to+Tagger!");
  } catch (error) {
    if (error instanceof UniqueConstraintError) {
      return res.status(409).render("auth/register", {
        title: "Register",
        error: "That username is already taken.",
        form: { username },
      });
    }
    throw error;
  }
});

router.post("/logout", (req, res) => {
  res.clearCookie("tagger_session", {
    httpOnly: true,
    sameSite: "lax"
  });
  res.redirect("/login?notice=You+are+now+offline.");
});

module.exports = router;
