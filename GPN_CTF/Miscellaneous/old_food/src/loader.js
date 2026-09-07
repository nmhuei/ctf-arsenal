const fs = require('fs');
const path = require('path');
const { Recipe } = require('./models');

function loadRecipes(filePath) {
  const raw = fs.readFileSync(filePath, 'utf-8');
  const data = JSON.parse(raw);
  return data.map(r => new Recipe(r));
}

function loadDefaultRecipes() {
  const defaultPath = path.join(__dirname, '..', 'data', 'recipes.json');
  return loadRecipes(defaultPath);
}

module.exports = { loadRecipes, loadDefaultRecipes };
