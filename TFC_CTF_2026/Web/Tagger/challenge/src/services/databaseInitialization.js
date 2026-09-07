const crypto = require("node:crypto");
const bcrypt = require("bcryptjs");
const { sequelize, Friendship, User } = require("../models");

let botCredentials;

function randomPassword() {
  return crypto.randomBytes(32).toString("base64url");
  // return "testtest";
}

function getBotCredentials() {
  if (!botCredentials) {
    throw new Error("Database initialization has not completed.");
  }
  return botCredentials;
}

async function initializeDatabase() {
  const tables = await sequelize.getQueryInterface().showAllTables();
  const isFirstInitialization = !tables.includes(User.getTableName());

  await sequelize.sync();
  if (botCredentials) return;

  const hackerPassword = randomPassword();
  const flagHolderPassword = randomPassword();
  const [hackerPasswordHash, flagHolderPasswordHash] = await Promise.all([
    bcrypt.hash(hackerPassword, 12),
    bcrypt.hash(flagHolderPassword, 12),
  ]);

  if (!isFirstInitialization) {
    const [hacker, flagHolder] = await Promise.all([
      User.findOne({ where: { username: "Hacker" } }),
      User.findOne({ where: { username: "FlagHolder" } }),
    ]);
    if (!hacker || !flagHolder) {
      throw new Error("The Hacker and FlagHolder bot accounts are missing.");
    }

    await sequelize.transaction(async (transaction) => {
      await Promise.all([
        hacker.update({ passwordHash: hackerPasswordHash }, { transaction }),
        flagHolder.update(
          { passwordHash: flagHolderPasswordHash },
          { transaction }
        ),
      ]);
    });
  } else {
    await sequelize.transaction(async (transaction) => {
      const hacker = await User.create(
        {
          username: "Hacker",
          passwordHash: hackerPasswordHash,
          hidden: true,
        },
        { transaction }
      );
      const flagHolder = await User.create(
        {
          username: "FlagHolder",
          passwordHash: flagHolderPasswordHash,
          hidden: true,
        },
        { transaction }
      );

      await Friendship.create(
        {
          userId: Math.min(hacker.id, flagHolder.id),
          friendId: Math.max(hacker.id, flagHolder.id),
        },
        { transaction }
      );
    });
  }

  botCredentials = Object.freeze({
    Hacker: hackerPassword,
    FlagHolder: flagHolderPassword,
  });
}

module.exports = { getBotCredentials, initializeDatabase };
