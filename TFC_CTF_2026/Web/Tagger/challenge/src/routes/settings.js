const express = require("express");
const { requireAuth } = require("../middleware/auth");

const router = express.Router();

router.get("/settings", requireAuth, (req, res) => {
  res.render("settings/index", { title: "Settings" });
});

router.post("/settings/visibility", requireAuth, async (req, res) => {
  const hidden = req.body?.hidden === "on";
  await req.user.update({ hidden });
  res.redirect(
    `/settings?notice=Profile+is+now+${hidden ? "hidden" : "visible"}.`
  );
});

module.exports = router;
