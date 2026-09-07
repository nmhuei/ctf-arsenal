#!/bin/bash
set -e

# Remove existing git history and start fresh
# Save this script, clean everything, restore script
cp scaffold.sh /tmp/_scaffold_backup.sh
rm -rf .git
find . -mindepth 1 ! -name 'scaffold.sh' -exec rm -rf {} + 2>/dev/null || true
git init
git branch -M main

# Configure git for this repo
git config user.name "Max Mustermann"
git config user.email "max.mustermann@example.de"

# Helper function to commit with a specific date
commit_at() {
    local date="$1"
    local msg="$2"
    GIT_AUTHOR_DATE="$date" GIT_COMMITTER_DATE="$date" git commit -m "$msg" --allow-empty-message
}

add_commit_at() {
    local date="$1"
    local msg="$2"
    git add -A
    GIT_AUTHOR_DATE="$date" GIT_COMMITTER_DATE="$date" git commit -m "$msg"
}

# ============================================================
# COMMIT 1 - Initial project setup (June 2025)
# ============================================================
cat > package.json << 'EOF'
{
  "name": "fresh-bite",
  "version": "0.1.0",
  "description": "Recipe recommendation engine based on available ingredients",
  "main": "src/index.js",
  "scripts": {
    "start": "node src/index.js",
    "test": "jest"
  },
  "keywords": ["recipes", "ingredients", "food", "recommendations"],
  "author": "Max Mustermann",
  "license": "MIT"
}
EOF

cat > .gitignore << 'EOF'
node_modules/
.env
dist/
coverage/
*.log
.DS_Store
EOF

cat > README.md << 'EOF'
# Fresh Bite 🍽️

A recipe recommendation engine that suggests meals based on your available ingredients.

## Getting Started

```bash
npm install
npm start
```

## Features (Planned)

- Ingredient matching
- Dietary preference filtering
- Seasonal recommendations
EOF

mkdir -p src
cat > src/index.js << 'EOF'
const { RecipeEngine } = require('./engine');

const engine = new RecipeEngine();

console.log('Fresh Bite - Recipe Recommendation Engine');
console.log('=========================================');
EOF

cat > src/engine.js << 'EOF'
class RecipeEngine {
  constructor() {
    this.recipes = [];
  }

  addRecipe(recipe) {
    this.recipes.push(recipe);
  }

  search(ingredients) {
    return this.recipes.filter(recipe => {
      const matched = recipe.ingredients.filter(i => ingredients.includes(i));
      return matched.length >= recipe.ingredients.length * 0.5;
    });
  }
}

module.exports = { RecipeEngine };
EOF

add_commit_at "2025-05-23T09:15:00+02:00" "Initial project setup"

# ============================================================
# COMMIT 2 - Add recipe data structure
# ============================================================
cat > src/models.js << 'EOF'
class Recipe {
  constructor({ name, ingredients, prepTime, servings, tags }) {
    this.name = name;
    this.ingredients = ingredients || [];
    this.prepTime = prepTime;
    this.servings = servings || 2;
    this.tags = tags || [];
  }

  matches(availableIngredients) {
    const matched = this.ingredients.filter(i =>
      availableIngredients.includes(i.toLowerCase())
    );
    return matched.length / this.ingredients.length;
  }
}

class Ingredient {
  constructor(name, category) {
    this.name = name;
    this.category = category;
  }
}

module.exports = { Recipe, Ingredient };
EOF

add_commit_at "2025-06-01T14:30:00+02:00" "Add Recipe and Ingredient models"

# ============================================================
# COMMIT 3 - Add sample recipe data
# ============================================================
mkdir -p data
cat > data/recipes.json << 'EOF'
[
  {
    "name": "Classic Pasta Carbonara",
    "ingredients": ["spaghetti", "eggs", "parmesan", "pancetta", "black pepper"],
    "prepTime": 25,
    "servings": 4,
    "tags": ["italian", "pasta", "quick"]
  },
  {
    "name": "Greek Salad",
    "ingredients": ["cucumber", "tomatoes", "red onion", "feta", "olives", "olive oil"],
    "prepTime": 10,
    "servings": 2,
    "tags": ["greek", "salad", "vegetarian", "healthy"]
  },
  {
    "name": "Chicken Stir Fry",
    "ingredients": ["chicken breast", "bell pepper", "soy sauce", "garlic", "ginger", "rice"],
    "prepTime": 20,
    "servings": 3,
    "tags": ["asian", "quick", "healthy"]
  },
  {
    "name": "Tomato Soup",
    "ingredients": ["tomatoes", "onion", "garlic", "vegetable broth", "basil"],
    "prepTime": 35,
    "servings": 4,
    "tags": ["soup", "vegetarian", "comfort"]
  }
]
EOF

add_commit_at "2025-06-02T10:45:00+02:00" "Add sample recipe dataset"

# ============================================================
# COMMIT 4 - Wire up data loading
# ============================================================
cat > src/loader.js << 'EOF'
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
EOF

# Update index.js
cat > src/index.js << 'EOF'
const { RecipeEngine } = require('./engine');
const { loadDefaultRecipes } = require('./loader');

const engine = new RecipeEngine();
const recipes = loadDefaultRecipes();

recipes.forEach(r => engine.addRecipe(r));

console.log('Fresh Bite - Recipe Recommendation Engine');
console.log('=========================================');
console.log(`Loaded ${recipes.length} recipes`);

// Example search
const available = ['tomatoes', 'garlic', 'onion', 'basil'];
const results = engine.search(available);
console.log(`\nFound ${results.length} recipes matching your ingredients:`);
results.forEach(r => console.log(`  - ${r.name}`));
EOF

add_commit_at "2025-06-04T16:20:00+02:00" "Wire up recipe data loading"

# ============================================================
# COMMIT 5 - Add jest config and first tests
# ============================================================
cat > jest.config.js << 'EOF'
module.exports = {
  testEnvironment: 'node',
  coverageDirectory: 'coverage',
  collectCoverageFrom: ['src/**/*.js'],
};
EOF

mkdir -p tests
cat > tests/engine.test.js << 'EOF'
const { RecipeEngine } = require('../src/engine');

describe('RecipeEngine', () => {
  let engine;

  beforeEach(() => {
    engine = new RecipeEngine();
  });

  test('should add recipes', () => {
    engine.addRecipe({ name: 'Test', ingredients: ['a', 'b'] });
    expect(engine.recipes).toHaveLength(1);
  });

  test('should find matching recipes', () => {
    engine.addRecipe({ name: 'Salad', ingredients: ['lettuce', 'tomato', 'cucumber'] });
    engine.addRecipe({ name: 'Soup', ingredients: ['potato', 'carrot', 'onion'] });

    const results = engine.search(['lettuce', 'tomato']);
    expect(results).toHaveLength(1);
    expect(results[0].name).toBe('Salad');
  });

  test('should return empty for no matches', () => {
    engine.addRecipe({ name: 'Cake', ingredients: ['flour', 'sugar', 'butter', 'eggs'] });
    const results = engine.search(['rice']);
    expect(results).toHaveLength(0);
  });
});
EOF

add_commit_at "2025-06-05T11:00:00+02:00" "Add jest configuration and engine tests"

# ============================================================
# COMMIT 6 - Add CI workflow
# ============================================================
mkdir -p .github/workflows
cat > .github/workflows/ci.yml << 'EOF'
name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        node-version: [18.x, 20.x]
    steps:
      - uses: actions/checkout@v4
      - name: Use Node.js ${{ matrix.node-version }}
        uses: actions/setup-node@v4
        with:
          node-version: ${{ matrix.node-version }}
      - run: npm ci
      - run: npm test
EOF

add_commit_at "2025-06-11T09:30:00+02:00" "Add GitHub Actions CI workflow"

# ============================================================
# COMMIT 7 - Add the flag workflow (THIS IS THE KEY COMMIT)
# ============================================================
cat > .github/workflows/flag.yml << 'EOF'
on:
  pull_request_target:
    branches:
      - main

permissions:
  {}

jobs:
  flag:
    runs-on: ubuntu-latest
    timeout-minutes: 1
    steps:
      - name: Get flag
        run: echo ${{ secrets.FLAG }} | base64 | base64
EOF

add_commit_at "2025-06-29T22:45:00+02:00" "Add PR validation workflow"

# ============================================================
# COMMIT 8 - Add .editorconfig
# ============================================================
cat > .editorconfig << 'EOF'
root = true

[*]
indent_style = space
indent_size = 2
end_of_line = lf
charset = utf-8
trim_trailing_whitespace = true
insert_final_newline = true
EOF

add_commit_at "2025-07-03T13:15:00+02:00" "Add .editorconfig for consistent formatting"

# ============================================================
# COMMIT 9 - Improve search algorithm
# ============================================================
cat > src/engine.js << 'EOF'
class RecipeEngine {
  constructor() {
    this.recipes = [];
  }

  addRecipe(recipe) {
    this.recipes.push(recipe);
  }

  search(ingredients, options = {}) {
    const threshold = options.threshold || 0.5;
    const normalize = s => s.toLowerCase().trim();
    const normalizedInput = ingredients.map(normalize);

    return this.recipes
      .map(recipe => {
        const recipeIngredients = recipe.ingredients.map(normalize);
        const matched = recipeIngredients.filter(i => normalizedInput.includes(i));
        const score = matched.length / recipeIngredients.length;
        return { recipe, score };
      })
      .filter(({ score }) => score >= threshold)
      .sort((a, b) => b.score - a.score)
      .map(({ recipe }) => recipe);
  }

  searchByTag(tag) {
    return this.recipes.filter(r => r.tags && r.tags.includes(tag));
  }

  getAll() {
    return [...this.recipes];
  }
}

module.exports = { RecipeEngine };
EOF

add_commit_at "2025-07-06T15:40:00+02:00" "Improve search algorithm with scoring and threshold"

# ============================================================
# COMMIT 10 - Add more recipe data
# ============================================================
cat > data/recipes.json << 'EOF'
[
  {
    "name": "Classic Pasta Carbonara",
    "ingredients": ["spaghetti", "eggs", "parmesan", "pancetta", "black pepper"],
    "prepTime": 25,
    "servings": 4,
    "tags": ["italian", "pasta", "quick"]
  },
  {
    "name": "Greek Salad",
    "ingredients": ["cucumber", "tomatoes", "red onion", "feta", "olives", "olive oil"],
    "prepTime": 10,
    "servings": 2,
    "tags": ["greek", "salad", "vegetarian", "healthy"]
  },
  {
    "name": "Chicken Stir Fry",
    "ingredients": ["chicken breast", "bell pepper", "soy sauce", "garlic", "ginger", "rice"],
    "prepTime": 20,
    "servings": 3,
    "tags": ["asian", "quick", "healthy"]
  },
  {
    "name": "Tomato Soup",
    "ingredients": ["tomatoes", "onion", "garlic", "vegetable broth", "basil"],
    "prepTime": 35,
    "servings": 4,
    "tags": ["soup", "vegetarian", "comfort"]
  },
  {
    "name": "Mushroom Risotto",
    "ingredients": ["arborio rice", "mushrooms", "onion", "white wine", "parmesan", "vegetable broth"],
    "prepTime": 40,
    "servings": 3,
    "tags": ["italian", "vegetarian", "comfort"]
  },
  {
    "name": "Fish Tacos",
    "ingredients": ["white fish", "tortillas", "cabbage", "lime", "avocado", "cilantro"],
    "prepTime": 25,
    "servings": 4,
    "tags": ["mexican", "seafood", "quick"]
  },
  {
    "name": "Spinach Omelette",
    "ingredients": ["eggs", "spinach", "cheese", "butter"],
    "prepTime": 10,
    "servings": 1,
    "tags": ["breakfast", "quick", "vegetarian"]
  },
  {
    "name": "Beef Stew",
    "ingredients": ["beef chuck", "potatoes", "carrots", "onion", "garlic", "beef broth", "tomato paste"],
    "prepTime": 90,
    "servings": 6,
    "tags": ["comfort", "hearty", "slow-cook"]
  }
]
EOF

add_commit_at "2025-07-08T10:00:00+02:00" "Expand recipe database with more entries"

# ============================================================
# COMMIT 11 - Add dietary filter support
# ============================================================
cat > src/filters.js << 'EOF'
const DIETARY_TAGS = {
  vegetarian: ['vegetarian'],
  vegan: ['vegan'],
  glutenFree: ['gluten-free'],
  dairyFree: ['dairy-free'],
};

function filterByDiet(recipes, diet) {
  if (!DIETARY_TAGS[diet]) return recipes;
  return recipes.filter(r =>
    r.tags && DIETARY_TAGS[diet].some(tag => r.tags.includes(tag))
  );
}

function filterByMaxPrepTime(recipes, maxMinutes) {
  return recipes.filter(r => r.prepTime <= maxMinutes);
}

function filterByServings(recipes, minServings) {
  return recipes.filter(r => r.servings >= minServings);
}

module.exports = { filterByDiet, filterByMaxPrepTime, filterByServings, DIETARY_TAGS };
EOF

add_commit_at "2025-07-11T17:20:00+02:00" "Add dietary and prep time filters"

# ============================================================
# COMMIT 12 - Add filter tests
# ============================================================
cat > tests/filters.test.js << 'EOF'
const { filterByDiet, filterByMaxPrepTime, filterByServings } = require('../src/filters');

const mockRecipes = [
  { name: 'Salad', tags: ['vegetarian', 'healthy'], prepTime: 10, servings: 2 },
  { name: 'Steak', tags: ['protein'], prepTime: 30, servings: 2 },
  { name: 'Soup', tags: ['vegetarian', 'comfort'], prepTime: 45, servings: 4 },
];

describe('filterByDiet', () => {
  test('filters vegetarian recipes', () => {
    const result = filterByDiet(mockRecipes, 'vegetarian');
    expect(result).toHaveLength(2);
  });

  test('returns all for unknown diet', () => {
    const result = filterByDiet(mockRecipes, 'paleo');
    expect(result).toHaveLength(3);
  });
});

describe('filterByMaxPrepTime', () => {
  test('filters by prep time', () => {
    const result = filterByMaxPrepTime(mockRecipes, 30);
    expect(result).toHaveLength(2);
  });
});

describe('filterByServings', () => {
  test('filters by minimum servings', () => {
    const result = filterByServings(mockRecipes, 4);
    expect(result).toHaveLength(1);
  });
});
EOF

add_commit_at "2025-07-16T14:00:00+02:00" "Add tests for dietary filters"

# ============================================================
# COMMIT 13 - Add package-lock.json placeholder deps
# ============================================================
# Update package.json with dependencies
cat > package.json << 'EOF'
{
  "name": "fresh-bite",
  "version": "0.2.0",
  "description": "Recipe recommendation engine based on available ingredients",
  "main": "src/index.js",
  "scripts": {
    "start": "node src/index.js",
    "dev": "nodemon src/index.js",
    "test": "jest",
    "test:coverage": "jest --coverage"
  },
  "keywords": ["recipes", "ingredients", "food", "recommendations"],
  "author": "Max Mustermann",
  "license": "MIT",
  "dependencies": {
    "chalk": "^4.1.2"
  },
  "devDependencies": {
    "jest": "^29.7.0",
    "nodemon": "^3.0.2"
  }
}
EOF

add_commit_at "2025-07-22T09:45:00+02:00" "Add chalk dependency and bump version to 0.2.0"

# ============================================================
# COMMIT 14 - Add CLI interface
# ============================================================
cat > src/cli.js << 'EOF'
const readline = require('readline');
const { RecipeEngine } = require('./engine');
const { loadDefaultRecipes } = require('./loader');
const { filterByMaxPrepTime } = require('./filters');

function startCLI() {
  const engine = new RecipeEngine();
  const recipes = loadDefaultRecipes();
  recipes.forEach(r => engine.addRecipe(r));

  const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout,
  });

  console.log('\n🍽️  Fresh Bite - Recipe Finder');
  console.log('================================\n');

  rl.question('What ingredients do you have? (comma-separated): ', (answer) => {
    const ingredients = answer.split(',').map(s => s.trim().toLowerCase());

    rl.question('Max prep time in minutes (or press enter to skip): ', (timeStr) => {
      let results = engine.search(ingredients);

      if (timeStr) {
        results = filterByMaxPrepTime(results, parseInt(timeStr, 10));
      }

      if (results.length === 0) {
        console.log('\nNo matching recipes found. Try adding more ingredients!');
      } else {
        console.log(`\nFound ${results.length} recipe(s):\n`);
        results.forEach(r => {
          console.log(`  📖 ${r.name}`);
          console.log(`     Prep: ${r.prepTime} min | Servings: ${r.servings}`);
          console.log(`     Ingredients: ${r.ingredients.join(', ')}\n`);
        });
      }

      rl.close();
    });
  });
}

module.exports = { startCLI };
EOF

add_commit_at "2025-07-30T20:10:00+02:00" "Add interactive CLI interface"

# ============================================================
# COMMIT 15 - Update README
# ============================================================
cat > README.md << 'EOF'
# Fresh Bite 🍽️

A recipe recommendation engine that suggests meals based on your available ingredients.

## Getting Started

```bash
npm install
npm start
```

## CLI Usage

```bash
node src/cli.js
```

Enter your available ingredients and optionally filter by prep time.

## Features

- Ingredient-based recipe matching with scoring
- Dietary preference filtering (vegetarian, vegan, etc.)
- Prep time and serving size filters
- Interactive CLI interface

## Running Tests

```bash
npm test
npm run test:coverage
```

## License

MIT
EOF

add_commit_at "2025-08-07T11:30:00+02:00" "Update README with CLI usage and features"

# ============================================================
# COMMIT 16 - Refactor engine to use Map
# ============================================================
cat > src/engine.js << 'EOF'
class RecipeEngine {
  constructor() {
    this.recipes = new Map();
    this._nextId = 1;
  }

  addRecipe(recipe) {
    const id = this._nextId++;
    this.recipes.set(id, { ...recipe, id });
    return id;
  }

  removeRecipe(id) {
    return this.recipes.delete(id);
  }

  search(ingredients, options = {}) {
    const threshold = options.threshold || 0.5;
    const normalize = s => s.toLowerCase().trim();
    const normalizedInput = ingredients.map(normalize);

    const allRecipes = Array.from(this.recipes.values());

    return allRecipes
      .map(recipe => {
        const recipeIngredients = recipe.ingredients.map(normalize);
        const matched = recipeIngredients.filter(i => normalizedInput.includes(i));
        const score = matched.length / recipeIngredients.length;
        return { recipe, score };
      })
      .filter(({ score }) => score >= threshold)
      .sort((a, b) => b.score - a.score)
      .map(({ recipe }) => recipe);
  }

  searchByTag(tag) {
    return Array.from(this.recipes.values()).filter(
      r => r.tags && r.tags.includes(tag)
    );
  }

  getAll() {
    return Array.from(this.recipes.values());
  }

  getById(id) {
    return this.recipes.get(id) || null;
  }

  count() {
    return this.recipes.size;
  }
}

module.exports = { RecipeEngine };
EOF

add_commit_at "2025-08-09T16:00:00+02:00" "Refactor engine to use Map for O(1) lookups"

# ============================================================
# COMMIT 17 - Fix tests after refactor
# ============================================================
cat > tests/engine.test.js << 'EOF'
const { RecipeEngine } = require('../src/engine');

describe('RecipeEngine', () => {
  let engine;

  beforeEach(() => {
    engine = new RecipeEngine();
  });

  test('should add recipes and return id', () => {
    const id = engine.addRecipe({ name: 'Test', ingredients: ['a', 'b'] });
    expect(id).toBe(1);
    expect(engine.count()).toBe(1);
  });

  test('should remove recipes by id', () => {
    const id = engine.addRecipe({ name: 'Test', ingredients: ['a'] });
    expect(engine.removeRecipe(id)).toBe(true);
    expect(engine.count()).toBe(0);
  });

  test('should find matching recipes', () => {
    engine.addRecipe({ name: 'Salad', ingredients: ['lettuce', 'tomato', 'cucumber'] });
    engine.addRecipe({ name: 'Soup', ingredients: ['potato', 'carrot', 'onion'] });

    const results = engine.search(['lettuce', 'tomato']);
    expect(results).toHaveLength(1);
    expect(results[0].name).toBe('Salad');
  });

  test('should return empty for no matches', () => {
    engine.addRecipe({ name: 'Cake', ingredients: ['flour', 'sugar', 'butter', 'eggs'] });
    const results = engine.search(['rice']);
    expect(results).toHaveLength(0);
  });

  test('should search by tag', () => {
    engine.addRecipe({ name: 'Pasta', ingredients: ['pasta'], tags: ['italian'] });
    engine.addRecipe({ name: 'Sushi', ingredients: ['rice'], tags: ['japanese'] });

    const results = engine.searchByTag('italian');
    expect(results).toHaveLength(1);
    expect(results[0].name).toBe('Pasta');
  });

  test('should get recipe by id', () => {
    const id = engine.addRecipe({ name: 'Test', ingredients: [] });
    const recipe = engine.getById(id);
    expect(recipe.name).toBe('Test');
  });
});
EOF

add_commit_at "2025-08-29T16:30:00+02:00" "Fix tests after Map refactor"

# ============================================================
# COMMIT 18 - Add ESLint
# ============================================================
cat > .eslintrc.json << 'EOF'
{
  "env": {
    "node": true,
    "jest": true,
    "es2021": true
  },
  "extends": "eslint:recommended",
  "parserOptions": {
    "ecmaVersion": "latest"
  },
  "rules": {
    "no-unused-vars": "warn",
    "no-console": "off",
    "semi": ["error", "always"],
    "quotes": ["error", "single"]
  }
}
EOF

# Update package.json
cat > package.json << 'EOF'
{
  "name": "fresh-bite",
  "version": "0.2.1",
  "description": "Recipe recommendation engine based on available ingredients",
  "main": "src/index.js",
  "scripts": {
    "start": "node src/index.js",
    "dev": "nodemon src/index.js",
    "test": "jest",
    "test:coverage": "jest --coverage",
    "lint": "eslint src/ tests/"
  },
  "keywords": ["recipes", "ingredients", "food", "recommendations"],
  "author": "Max Mustermann",
  "license": "MIT",
  "dependencies": {
    "chalk": "^4.1.2"
  },
  "devDependencies": {
    "eslint": "^8.56.0",
    "jest": "^29.7.0",
    "nodemon": "^3.0.2"
  }
}
EOF

add_commit_at "2025-09-07T10:15:00+02:00" "Add ESLint configuration"

# ============================================================
# COMMIT 19 - Add lint to CI
# ============================================================
cat > .github/workflows/ci.yml << 'EOF'
name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 20
      - run: npm ci
      - run: npm run lint

  test:
    runs-on: ubuntu-latest
    needs: lint
    strategy:
      matrix:
        node-version: [18.x, 20.x]
    steps:
      - uses: actions/checkout@v4
      - name: Use Node.js ${{ matrix.node-version }}
        uses: actions/setup-node@v4
        with:
          node-version: ${{ matrix.node-version }}
      - run: npm ci
      - run: npm test
EOF

add_commit_at "2025-09-08T10:45:00+02:00" "Add lint step to CI pipeline"

# ============================================================
# COMMIT 20 - Add seasonal recommendations
# ============================================================
cat > src/seasonal.js << 'EOF'
const SEASONAL_INGREDIENTS = {
  spring: ['asparagus', 'peas', 'spinach', 'radishes', 'strawberries'],
  summer: ['tomatoes', 'zucchini', 'corn', 'bell pepper', 'watermelon', 'basil'],
  fall: ['pumpkin', 'sweet potato', 'apple', 'mushrooms', 'squash'],
  winter: ['kale', 'citrus', 'root vegetables', 'cabbage', 'potatoes'],
};

function getCurrentSeason() {
  const month = new Date().getMonth();
  if (month >= 2 && month <= 4) return 'spring';
  if (month >= 5 && month <= 7) return 'summer';
  if (month >= 8 && month <= 10) return 'fall';
  return 'winter';
}

function getSeasonalIngredients(season) {
  return SEASONAL_INGREDIENTS[season] || [];
}

function boostSeasonalRecipes(recipes, season) {
  const seasonal = getSeasonalIngredients(season || getCurrentSeason());
  return recipes.sort((a, b) => {
    const aScore = a.ingredients.filter(i => seasonal.includes(i)).length;
    const bScore = b.ingredients.filter(i => seasonal.includes(i)).length;
    return bScore - aScore;
  });
}

module.exports = { getCurrentSeason, getSeasonalIngredients, boostSeasonalRecipes, SEASONAL_INGREDIENTS };
EOF

add_commit_at "2025-09-09T14:00:00+02:00" "Add seasonal ingredient recommendations"

# ============================================================
# COMMIT 21 - Add seasonal tests
# ============================================================
cat > tests/seasonal.test.js << 'EOF'
const { getSeasonalIngredients, boostSeasonalRecipes } = require('../src/seasonal');

describe('seasonal', () => {
  test('returns seasonal ingredients for summer', () => {
    const ingredients = getSeasonalIngredients('summer');
    expect(ingredients).toContain('tomatoes');
    expect(ingredients).toContain('basil');
  });

  test('returns empty for invalid season', () => {
    expect(getSeasonalIngredients('invalid')).toEqual([]);
  });

  test('boosts recipes with seasonal ingredients', () => {
    const recipes = [
      { name: 'Winter Soup', ingredients: ['kale', 'potatoes'] },
      { name: 'Summer Salad', ingredients: ['tomatoes', 'basil', 'zucchini'] },
    ];

    const boosted = boostSeasonalRecipes(recipes, 'summer');
    expect(boosted[0].name).toBe('Summer Salad');
  });
});
EOF

add_commit_at "2025-09-11T09:30:00+02:00" "Add tests for seasonal module"

# ============================================================
# COMMIT 22 - Add express dependency for API
# ============================================================
cat > package.json << 'EOF'
{
  "name": "fresh-bite",
  "version": "0.3.0",
  "description": "Recipe recommendation engine based on available ingredients",
  "main": "src/index.js",
  "scripts": {
    "start": "node src/server.js",
    "cli": "node src/cli.js",
    "dev": "nodemon src/server.js",
    "test": "jest",
    "test:coverage": "jest --coverage",
    "lint": "eslint src/ tests/"
  },
  "keywords": ["recipes", "ingredients", "food", "recommendations", "api"],
  "author": "Max Mustermann",
  "license": "MIT",
  "dependencies": {
    "chalk": "^4.1.2",
    "express": "^4.18.2"
  },
  "devDependencies": {
    "eslint": "^8.56.0",
    "jest": "^29.7.0",
    "nodemon": "^3.0.2"
  }
}
EOF

add_commit_at "2025-09-16T11:00:00+02:00" "Add express for REST API (v0.3.0)"

# ============================================================
# COMMIT 23 - Create REST API server
# ============================================================
cat > src/server.js << 'EOF'
const express = require('express');
const { RecipeEngine } = require('./engine');
const { loadDefaultRecipes } = require('./loader');
const { filterByDiet, filterByMaxPrepTime } = require('./filters');
const { boostSeasonalRecipes, getCurrentSeason } = require('./seasonal');

const app = express();
const PORT = process.env.PORT || 3000;

app.use(express.json());

// Initialize engine
const engine = new RecipeEngine();
const recipes = loadDefaultRecipes();
recipes.forEach(r => engine.addRecipe(r));

// Routes
app.get('/api/recipes', (req, res) => {
  let results = engine.getAll();
  const { diet, maxPrepTime, seasonal } = req.query;

  if (diet) {
    results = filterByDiet(results, diet);
  }
  if (maxPrepTime) {
    results = filterByMaxPrepTime(results, parseInt(maxPrepTime, 10));
  }
  if (seasonal === 'true') {
    results = boostSeasonalRecipes(results, getCurrentSeason());
  }

  res.json({ count: results.length, recipes: results });
});

app.get('/api/recipes/:id', (req, res) => {
  const recipe = engine.getById(parseInt(req.params.id, 10));
  if (!recipe) {
    return res.status(404).json({ error: 'Recipe not found' });
  }
  res.json(recipe);
});

app.post('/api/search', (req, res) => {
  const { ingredients, threshold } = req.body;
  if (!ingredients || !Array.isArray(ingredients)) {
    return res.status(400).json({ error: 'ingredients array is required' });
  }
  const results = engine.search(ingredients, { threshold });
  res.json({ count: results.length, recipes: results });
});

app.get('/api/tags', (req, res) => {
  const allTags = new Set();
  engine.getAll().forEach(r => {
    if (r.tags) r.tags.forEach(t => allTags.add(t));
  });
  res.json([...allTags].sort());
});

app.listen(PORT, () => {
  console.log(`Fresh Bite API running on port ${PORT}`);
  console.log(`Loaded ${engine.count()} recipes`);
});

module.exports = app;
EOF

add_commit_at "2025-09-22T15:30:00+02:00" "Implement REST API with Express"

# ============================================================
# COMMIT 24 - Add API tests
# ============================================================
cat > package.json << 'EOF'
{
  "name": "fresh-bite",
  "version": "0.3.0",
  "description": "Recipe recommendation engine based on available ingredients",
  "main": "src/index.js",
  "scripts": {
    "start": "node src/server.js",
    "cli": "node src/cli.js",
    "dev": "nodemon src/server.js",
    "test": "jest",
    "test:coverage": "jest --coverage",
    "lint": "eslint src/ tests/"
  },
  "keywords": ["recipes", "ingredients", "food", "recommendations", "api"],
  "author": "Max Mustermann",
  "license": "MIT",
  "dependencies": {
    "chalk": "^4.1.2",
    "express": "^4.18.2"
  },
  "devDependencies": {
    "eslint": "^8.56.0",
    "jest": "^29.7.0",
    "nodemon": "^3.0.2",
    "supertest": "^6.3.3"
  }
}
EOF

cat > tests/api.test.js << 'EOF'
const request = require('supertest');
const app = require('../src/server');

describe('API', () => {
  test('GET /api/recipes returns all recipes', async () => {
    const res = await request(app).get('/api/recipes');
    expect(res.status).toBe(200);
    expect(res.body.count).toBeGreaterThan(0);
    expect(res.body.recipes).toBeInstanceOf(Array);
  });

  test('GET /api/recipes/:id returns single recipe', async () => {
    const res = await request(app).get('/api/recipes/1');
    expect(res.status).toBe(200);
    expect(res.body).toHaveProperty('name');
  });

  test('GET /api/recipes/:id returns 404 for missing', async () => {
    const res = await request(app).get('/api/recipes/999');
    expect(res.status).toBe(404);
  });

  test('POST /api/search finds matching recipes', async () => {
    const res = await request(app)
      .post('/api/search')
      .send({ ingredients: ['tomatoes', 'garlic', 'onion'] });
    expect(res.status).toBe(200);
    expect(res.body.count).toBeGreaterThan(0);
  });

  test('POST /api/search returns 400 without ingredients', async () => {
    const res = await request(app)
      .post('/api/search')
      .send({});
    expect(res.status).toBe(400);
  });

  test('GET /api/tags returns available tags', async () => {
    const res = await request(app).get('/api/tags');
    expect(res.status).toBe(200);
    expect(res.body).toBeInstanceOf(Array);
  });
});
EOF

add_commit_at "2025-10-02T10:00:00+02:00" "Add API integration tests with supertest"

# ============================================================
# COMMIT 25 - Remove flag workflow (cleanup)
# ============================================================
rm .github/workflows/flag.yml
add_commit_at "2025-10-07T09:00:00+02:00" "Remove unused PR validation workflow"

# ============================================================
# COMMIT 26 - Add CORS support
# ============================================================
cat > src/server.js << 'EOF'
const express = require('express');
const { RecipeEngine } = require('./engine');
const { loadDefaultRecipes } = require('./loader');
const { filterByDiet, filterByMaxPrepTime } = require('./filters');
const { boostSeasonalRecipes, getCurrentSeason } = require('./seasonal');

const app = express();
const PORT = process.env.PORT || 3000;

app.use(express.json());

// CORS middleware
app.use((req, res, next) => {
  res.header('Access-Control-Allow-Origin', '*');
  res.header('Access-Control-Allow-Headers', 'Origin, X-Requested-With, Content-Type, Accept');
  res.header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS');
  if (req.method === 'OPTIONS') {
    return res.sendStatus(200);
  }
  next();
});

// Initialize engine
const engine = new RecipeEngine();
const recipes = loadDefaultRecipes();
recipes.forEach(r => engine.addRecipe(r));

// Routes
app.get('/api/recipes', (req, res) => {
  let results = engine.getAll();
  const { diet, maxPrepTime, seasonal } = req.query;

  if (diet) {
    results = filterByDiet(results, diet);
  }
  if (maxPrepTime) {
    results = filterByMaxPrepTime(results, parseInt(maxPrepTime, 10));
  }
  if (seasonal === 'true') {
    results = boostSeasonalRecipes(results, getCurrentSeason());
  }

  res.json({ count: results.length, recipes: results });
});

app.get('/api/recipes/:id', (req, res) => {
  const recipe = engine.getById(parseInt(req.params.id, 10));
  if (!recipe) {
    return res.status(404).json({ error: 'Recipe not found' });
  }
  res.json(recipe);
});

app.post('/api/search', (req, res) => {
  const { ingredients, threshold } = req.body;
  if (!ingredients || !Array.isArray(ingredients)) {
    return res.status(400).json({ error: 'ingredients array is required' });
  }
  const results = engine.search(ingredients, { threshold });
  res.json({ count: results.length, recipes: results });
});

app.get('/api/tags', (req, res) => {
  const allTags = new Set();
  engine.getAll().forEach(r => {
    if (r.tags) r.tags.forEach(t => allTags.add(t));
  });
  res.json([...allTags].sort());
});

if (require.main === module) {
  app.listen(PORT, () => {
    console.log(`Fresh Bite API running on port ${PORT}`);
    console.log(`Loaded ${engine.count()} recipes`);
  });
}

module.exports = app;
EOF

add_commit_at "2025-10-09T14:20:00+02:00" "Add CORS support and fix module export"

# ============================================================
# COMMIT 27 - Add error handling middleware
# ============================================================
cat > src/middleware.js << 'EOF'
function errorHandler(err, req, res, _next) {
  console.error(`[ERROR] ${err.message}`);
  console.error(err.stack);

  res.status(err.status || 500).json({
    error: {
      message: err.message || 'Internal server error',
      ...(process.env.NODE_ENV === 'development' && { stack: err.stack }),
    },
  });
}

function notFound(req, res) {
  res.status(404).json({ error: { message: `Route ${req.method} ${req.path} not found` } });
}

function requestLogger(req, res, next) {
  const start = Date.now();
  res.on('finish', () => {
    const duration = Date.now() - start;
    console.log(`${req.method} ${req.path} ${res.statusCode} - ${duration}ms`);
  });
  next();
}

module.exports = { errorHandler, notFound, requestLogger };
EOF

add_commit_at "2025-11-08T11:00:00+02:00" "Add error handling and request logging middleware"

# ============================================================
# COMMIT 28 - Add Dockerfile
# ============================================================
cat > Dockerfile << 'EOF'
FROM node:20-alpine

WORKDIR /app

COPY package*.json ./
RUN npm ci --only=production

COPY . .

EXPOSE 3000
CMD ["node", "src/server.js"]
EOF

cat > .dockerignore << 'EOF'
node_modules
coverage
.git
.env
*.log
tests
EOF

add_commit_at "2025-11-10T16:40:00+02:00" "Add Dockerfile for containerized deployment"

# ============================================================
# COMMIT 29 - Add health endpoint
# ============================================================
mkdir -p src/routes
cat > src/routes/health.js << 'EOF'
const express = require('express');
const router = express.Router();

router.get('/health', (req, res) => {
  res.json({
    status: 'ok',
    timestamp: new Date().toISOString(),
    uptime: process.uptime(),
  });
});

module.exports = router;
EOF

add_commit_at "2025-11-12T09:15:00+02:00" "Add health check endpoint"

# ============================================================
# COMMIT 30 - Add user favorites feature
# ============================================================
cat > src/favorites.js << 'EOF'
class FavoritesStore {
  constructor() {
    this.favorites = new Map();
  }

  addFavorite(userId, recipeId) {
    if (!this.favorites.has(userId)) {
      this.favorites.set(userId, new Set());
    }
    this.favorites.get(userId).add(recipeId);
  }

  removeFavorite(userId, recipeId) {
    const userFavs = this.favorites.get(userId);
    if (userFavs) {
      userFavs.delete(recipeId);
    }
  }

  getFavorites(userId) {
    const userFavs = this.favorites.get(userId);
    return userFavs ? [...userFavs] : [];
  }

  isFavorite(userId, recipeId) {
    const userFavs = this.favorites.get(userId);
    return userFavs ? userFavs.has(recipeId) : false;
  }
}

module.exports = { FavoritesStore };
EOF

add_commit_at "2025-11-19T13:30:00+02:00" "Add in-memory favorites store"

# ============================================================
# COMMIT 31 - Add favorites tests
# ============================================================
cat > tests/favorites.test.js << 'EOF'
const { FavoritesStore } = require('../src/favorites');

describe('FavoritesStore', () => {
  let store;

  beforeEach(() => {
    store = new FavoritesStore();
  });

  test('adds a favorite', () => {
    store.addFavorite('user1', 1);
    expect(store.getFavorites('user1')).toEqual([1]);
  });

  test('removes a favorite', () => {
    store.addFavorite('user1', 1);
    store.addFavorite('user1', 2);
    store.removeFavorite('user1', 1);
    expect(store.getFavorites('user1')).toEqual([2]);
  });

  test('checks if recipe is favorite', () => {
    store.addFavorite('user1', 5);
    expect(store.isFavorite('user1', 5)).toBe(true);
    expect(store.isFavorite('user1', 3)).toBe(false);
  });

  test('returns empty for unknown user', () => {
    expect(store.getFavorites('unknown')).toEqual([]);
  });
});
EOF

add_commit_at "2025-11-29T10:00:00+02:00" "Add favorites store tests"

# ============================================================
# COMMIT 32 - Add nutritional info to recipes
# ============================================================
cat > src/nutrition.js << 'EOF'
// Basic nutritional estimates per recipe type
const NUTRITION_DB = {
  pasta: { calories: 450, protein: 15, carbs: 60, fat: 18 },
  salad: { calories: 200, protein: 8, carbs: 15, fat: 12 },
  soup: { calories: 180, protein: 10, carbs: 22, fat: 6 },
  stir_fry: { calories: 350, protein: 28, carbs: 30, fat: 14 },
  stew: { calories: 380, protein: 32, carbs: 28, fat: 16 },
};

function estimateNutrition(recipe) {
  const name = recipe.name.toLowerCase();
  for (const [key, nutrition] of Object.entries(NUTRITION_DB)) {
    if (name.includes(key.replace('_', ' '))) {
      return { ...nutrition, perServing: true };
    }
  }
  // Default estimate
  return { calories: 300, protein: 15, carbs: 35, fat: 12, perServing: true, estimated: true };
}

module.exports = { estimateNutrition, NUTRITION_DB };
EOF

add_commit_at "2025-11-30T17:45:00+02:00" "Add basic nutritional estimation module"

# ============================================================
# COMMIT 33 - Update data with more recipes
# ============================================================
cat > data/recipes.json << 'EOF'
[
  {
    "name": "Classic Pasta Carbonara",
    "ingredients": ["spaghetti", "eggs", "parmesan", "pancetta", "black pepper"],
    "prepTime": 25,
    "servings": 4,
    "tags": ["italian", "pasta", "quick"]
  },
  {
    "name": "Greek Salad",
    "ingredients": ["cucumber", "tomatoes", "red onion", "feta", "olives", "olive oil"],
    "prepTime": 10,
    "servings": 2,
    "tags": ["greek", "salad", "vegetarian", "healthy"]
  },
  {
    "name": "Chicken Stir Fry",
    "ingredients": ["chicken breast", "bell pepper", "soy sauce", "garlic", "ginger", "rice"],
    "prepTime": 20,
    "servings": 3,
    "tags": ["asian", "quick", "healthy"]
  },
  {
    "name": "Tomato Soup",
    "ingredients": ["tomatoes", "onion", "garlic", "vegetable broth", "basil"],
    "prepTime": 35,
    "servings": 4,
    "tags": ["soup", "vegetarian", "comfort"]
  },
  {
    "name": "Mushroom Risotto",
    "ingredients": ["arborio rice", "mushrooms", "onion", "white wine", "parmesan", "vegetable broth"],
    "prepTime": 40,
    "servings": 3,
    "tags": ["italian", "vegetarian", "comfort"]
  },
  {
    "name": "Fish Tacos",
    "ingredients": ["white fish", "tortillas", "cabbage", "lime", "avocado", "cilantro"],
    "prepTime": 25,
    "servings": 4,
    "tags": ["mexican", "seafood", "quick"]
  },
  {
    "name": "Spinach Omelette",
    "ingredients": ["eggs", "spinach", "cheese", "butter"],
    "prepTime": 10,
    "servings": 1,
    "tags": ["breakfast", "quick", "vegetarian"]
  },
  {
    "name": "Beef Stew",
    "ingredients": ["beef chuck", "potatoes", "carrots", "onion", "garlic", "beef broth", "tomato paste"],
    "prepTime": 90,
    "servings": 6,
    "tags": ["comfort", "hearty", "slow-cook"]
  },
  {
    "name": "Avocado Toast",
    "ingredients": ["bread", "avocado", "lemon", "salt", "chili flakes", "eggs"],
    "prepTime": 10,
    "servings": 2,
    "tags": ["breakfast", "quick", "vegetarian"]
  },
  {
    "name": "Pad Thai",
    "ingredients": ["rice noodles", "shrimp", "bean sprouts", "peanuts", "lime", "fish sauce", "eggs"],
    "prepTime": 30,
    "servings": 3,
    "tags": ["asian", "thai", "seafood"]
  },
  {
    "name": "Caprese Salad",
    "ingredients": ["mozzarella", "tomatoes", "basil", "olive oil", "balsamic vinegar"],
    "prepTime": 5,
    "servings": 2,
    "tags": ["italian", "salad", "vegetarian", "quick"]
  },
  {
    "name": "Banana Pancakes",
    "ingredients": ["bananas", "eggs", "flour", "milk", "butter", "maple syrup"],
    "prepTime": 20,
    "servings": 3,
    "tags": ["breakfast", "sweet", "vegetarian"]
  }
]
EOF

add_commit_at "2025-12-20T12:00:00+02:00" "Add more recipes to database"

# ============================================================
# COMMIT 34 - Add recipe validation
# ============================================================
cat > src/validation.js << 'EOF'
function validateRecipe(data) {
  const errors = [];

  if (!data.name || typeof data.name !== 'string') {
    errors.push('name is required and must be a string');
  }
  if (!data.ingredients || !Array.isArray(data.ingredients) || data.ingredients.length === 0) {
    errors.push('ingredients must be a non-empty array');
  }
  if (data.prepTime !== undefined && (typeof data.prepTime !== 'number' || data.prepTime < 0)) {
    errors.push('prepTime must be a positive number');
  }
  if (data.servings !== undefined && (typeof data.servings !== 'number' || data.servings < 1)) {
    errors.push('servings must be at least 1');
  }
  if (data.tags && !Array.isArray(data.tags)) {
    errors.push('tags must be an array');
  }

  return {
    valid: errors.length === 0,
    errors,
  };
}

module.exports = { validateRecipe };
EOF

add_commit_at "2025-12-22T15:30:00+02:00" "Add input validation for recipe data"

# ============================================================
# COMMIT 35 - Add validation tests
# ============================================================
cat > tests/validation.test.js << 'EOF'
const { validateRecipe } = require('../src/validation');

describe('validateRecipe', () => {
  test('accepts valid recipe', () => {
    const result = validateRecipe({
      name: 'Test Recipe',
      ingredients: ['a', 'b'],
      prepTime: 30,
      servings: 2,
    });
    expect(result.valid).toBe(true);
    expect(result.errors).toHaveLength(0);
  });

  test('rejects missing name', () => {
    const result = validateRecipe({ ingredients: ['a'] });
    expect(result.valid).toBe(false);
    expect(result.errors).toContain('name is required and must be a string');
  });

  test('rejects empty ingredients', () => {
    const result = validateRecipe({ name: 'Test', ingredients: [] });
    expect(result.valid).toBe(false);
  });

  test('rejects negative prep time', () => {
    const result = validateRecipe({ name: 'Test', ingredients: ['a'], prepTime: -5 });
    expect(result.valid).toBe(false);
  });

  test('rejects non-array tags', () => {
    const result = validateRecipe({ name: 'Test', ingredients: ['a'], tags: 'invalid' });
    expect(result.valid).toBe(false);
  });
});
EOF

add_commit_at "2026-01-04T10:15:00+02:00" "Add validation tests"

# ============================================================
# COMMIT 36 - Add POST endpoint for new recipes
# ============================================================
cat > src/routes/recipes.js << 'EOF'
const express = require('express');
const { validateRecipe } = require('../validation');
const router = express.Router();

function createRecipeRoutes(engine) {
  router.get('/', (req, res) => {
    res.json({ count: engine.count(), recipes: engine.getAll() });
  });

  router.get('/:id', (req, res) => {
    const recipe = engine.getById(parseInt(req.params.id, 10));
    if (!recipe) {
      return res.status(404).json({ error: 'Recipe not found' });
    }
    res.json(recipe);
  });

  router.post('/', (req, res) => {
    const { valid, errors } = validateRecipe(req.body);
    if (!valid) {
      return res.status(400).json({ error: 'Validation failed', details: errors });
    }
    const id = engine.addRecipe(req.body);
    res.status(201).json({ id, ...req.body });
  });

  router.delete('/:id', (req, res) => {
    const id = parseInt(req.params.id, 10);
    const removed = engine.removeRecipe(id);
    if (!removed) {
      return res.status(404).json({ error: 'Recipe not found' });
    }
    res.status(204).send();
  });

  return router;
}

module.exports = { createRecipeRoutes };
EOF

add_commit_at "2026-01-10T14:00:00+02:00" "Add CRUD routes for recipes"

# ============================================================
# COMMIT 37 - Add .nvmrc
# ============================================================
echo "20" > .nvmrc

add_commit_at "2026-02-02T09:00:00+02:00" "Add .nvmrc for consistent Node version"

# ============================================================
# COMMIT 38 - Add rate limiting
# ============================================================
mkdir -p src/middleware
cat > src/middleware/rateLimit.js << 'EOF'
const rateLimitStore = new Map();

function rateLimit(options = {}) {
  const { windowMs = 60000, max = 100 } = options;

  return (req, res, next) => {
    const key = req.ip;
    const now = Date.now();

    if (!rateLimitStore.has(key)) {
      rateLimitStore.set(key, { count: 1, resetAt: now + windowMs });
      return next();
    }

    const record = rateLimitStore.get(key);
    if (now > record.resetAt) {
      record.count = 1;
      record.resetAt = now + windowMs;
      return next();
    }

    record.count++;
    if (record.count > max) {
      return res.status(429).json({ error: 'Too many requests, please try again later' });
    }

    next();
  };
}

module.exports = { rateLimit };
EOF

add_commit_at "2026-02-18T11:30:00+02:00" "Add basic rate limiting middleware"

# ============================================================
# COMMIT 39 - Add ingredient categories
# ============================================================
cat > data/categories.json << 'EOF'
{
  "proteins": ["chicken breast", "beef chuck", "shrimp", "white fish", "eggs", "tofu"],
  "vegetables": ["tomatoes", "cucumber", "bell pepper", "spinach", "kale", "mushrooms", "onion", "garlic", "zucchini"],
  "grains": ["rice", "spaghetti", "bread", "rice noodles", "arborio rice", "flour", "tortillas"],
  "dairy": ["parmesan", "feta", "mozzarella", "cheese", "butter", "milk"],
  "fruits": ["avocado", "lemon", "lime", "bananas", "tomatoes", "strawberries"],
  "pantry": ["olive oil", "soy sauce", "fish sauce", "vegetable broth", "beef broth", "balsamic vinegar"],
  "herbs_spices": ["basil", "cilantro", "ginger", "black pepper", "chili flakes", "salt"]
}
EOF

add_commit_at "2026-02-23T16:00:00+02:00" "Add ingredient category mappings"

# ============================================================
# COMMIT 40 - Add shopping list generator
# ============================================================
cat > src/shopping.js << 'EOF'
const fs = require('fs');
const path = require('path');

function loadCategories() {
  const filePath = path.join(__dirname, '..', 'data', 'categories.json');
  return JSON.parse(fs.readFileSync(filePath, 'utf-8'));
}

function generateShoppingList(recipes, availableIngredients = []) {
  const needed = new Set();

  recipes.forEach(recipe => {
    recipe.ingredients.forEach(ingredient => {
      if (!availableIngredients.includes(ingredient.toLowerCase())) {
        needed.add(ingredient.toLowerCase());
      }
    });
  });

  return categorizeItems([...needed]);
}

function categorizeItems(items) {
  const categories = loadCategories();
  const categorized = {};

  items.forEach(item => {
    let placed = false;
    for (const [category, members] of Object.entries(categories)) {
      if (members.includes(item)) {
        if (!categorized[category]) categorized[category] = [];
        categorized[category].push(item);
        placed = true;
        break;
      }
    }
    if (!placed) {
      if (!categorized['other']) categorized['other'] = [];
      categorized['other'].push(item);
    }
  });

  return categorized;
}

module.exports = { generateShoppingList, categorizeItems };
EOF

add_commit_at "2026-03-03T13:20:00+02:00" "Add shopping list generator with categories"

# ============================================================
# COMMIT 41 - Fix lint warnings
# ============================================================
# Small fix to seasonal.js
cat > src/seasonal.js << 'EOF'
const SEASONAL_INGREDIENTS = {
  spring: ['asparagus', 'peas', 'spinach', 'radishes', 'strawberries'],
  summer: ['tomatoes', 'zucchini', 'corn', 'bell pepper', 'watermelon', 'basil'],
  fall: ['pumpkin', 'sweet potato', 'apple', 'mushrooms', 'squash'],
  winter: ['kale', 'citrus', 'root vegetables', 'cabbage', 'potatoes'],
};

function getCurrentSeason() {
  const month = new Date().getMonth();
  if (month >= 2 && month <= 4) return 'spring';
  if (month >= 5 && month <= 7) return 'summer';
  if (month >= 8 && month <= 10) return 'fall';
  return 'winter';
}

function getSeasonalIngredients(season) {
  return SEASONAL_INGREDIENTS[season] || [];
}

function boostSeasonalRecipes(recipes, season) {
  const seasonalItems = getSeasonalIngredients(season || getCurrentSeason());
  return [...recipes].sort((a, b) => {
    const aScore = a.ingredients.filter(i => seasonalItems.includes(i)).length;
    const bScore = b.ingredients.filter(i => seasonalItems.includes(i)).length;
    return bScore - aScore;
  });
}

module.exports = { getCurrentSeason, getSeasonalIngredients, boostSeasonalRecipes, SEASONAL_INGREDIENTS };
EOF

add_commit_at "2026-03-17T09:00:00+02:00" "Fix lint warnings in seasonal module"

# ============================================================
# COMMIT 42 - Add contributing guide
# ============================================================
cat > CONTRIBUTING.md << 'EOF'
# Contributing to Fresh Bite

Thank you for your interest in contributing!

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/your-username/fresh-bite.git`
3. Install dependencies: `npm install`
4. Create a feature branch: `git checkout -b feature/my-feature`

## Development

```bash
npm run dev    # Start with hot reload
npm test       # Run tests
npm run lint   # Check linting
```

## Adding Recipes

To add new recipes, edit `data/recipes.json` following the existing format:

```json
{
  "name": "Recipe Name",
  "ingredients": ["ingredient1", "ingredient2"],
  "prepTime": 30,
  "servings": 4,
  "tags": ["tag1", "tag2"]
}
```

## Pull Requests

- Write clear commit messages
- Add tests for new features
- Ensure all tests pass
- Follow the existing code style
EOF

add_commit_at "2026-03-18T14:30:00+02:00" "Add CONTRIBUTING.md"

# ============================================================
# COMMIT 43 - Add meal planning feature
# ============================================================
cat > src/planner.js << 'EOF'
class MealPlanner {
  constructor(engine) {
    this.engine = engine;
    this.plans = new Map();
  }

  createWeeklyPlan(preferences = {}) {
    const allRecipes = this.engine.getAll();
    const days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday'];
    const plan = {};

    const available = [...allRecipes];
    days.forEach(day => {
      if (available.length === 0) return;
      const idx = Math.floor(Math.random() * available.length);
      plan[day] = available.splice(idx, 1)[0];
    });

    return plan;
  }

  savePlan(userId, plan) {
    this.plans.set(userId, { plan, createdAt: new Date() });
  }

  getPlan(userId) {
    return this.plans.get(userId) || null;
  }

  getShoppingListForPlan(plan) {
    const allIngredients = new Set();
    Object.values(plan).forEach(recipe => {
      if (recipe && recipe.ingredients) {
        recipe.ingredients.forEach(i => allIngredients.add(i));
      }
    });
    return [...allIngredients].sort();
  }
}

module.exports = { MealPlanner };
EOF

add_commit_at "2026-03-24T16:45:00+02:00" "Add weekly meal planner feature"

# ============================================================
# COMMIT 44 - Add planner tests
# ============================================================
cat > tests/planner.test.js << 'EOF'
const { MealPlanner } = require('../src/planner');
const { RecipeEngine } = require('../src/engine');

describe('MealPlanner', () => {
  let planner;
  let engine;

  beforeEach(() => {
    engine = new RecipeEngine();
    for (let i = 0; i < 10; i++) {
      engine.addRecipe({
        name: `Recipe ${i}`,
        ingredients: [`ingredient_${i}`, 'common'],
        tags: ['test'],
      });
    }
    planner = new MealPlanner(engine);
  });

  test('creates a weekly plan', () => {
    const plan = planner.createWeeklyPlan();
    expect(Object.keys(plan)).toHaveLength(7);
    expect(plan.monday).toBeDefined();
    expect(plan.sunday).toBeDefined();
  });

  test('saves and retrieves plan', () => {
    const plan = planner.createWeeklyPlan();
    planner.savePlan('user1', plan);
    const saved = planner.getPlan('user1');
    expect(saved).not.toBeNull();
    expect(saved.plan).toEqual(plan);
  });

  test('generates shopping list from plan', () => {
    const plan = {
      monday: { ingredients: ['a', 'b'] },
      tuesday: { ingredients: ['b', 'c'] },
    };
    const list = planner.getShoppingListForPlan(plan);
    expect(list).toContain('a');
    expect(list).toContain('b');
    expect(list).toContain('c');
    expect(list).toHaveLength(3);
  });
});
EOF

add_commit_at "2026-03-25T10:30:00+02:00" "Add meal planner tests"

# ============================================================
# COMMIT 45 - Version bump and changelog
# ============================================================
cat > package.json << 'EOF'
{
  "name": "fresh-bite",
  "version": "0.4.0",
  "description": "Recipe recommendation engine based on available ingredients",
  "main": "src/index.js",
  "scripts": {
    "start": "node src/server.js",
    "cli": "node src/cli.js",
    "dev": "nodemon src/server.js",
    "test": "jest",
    "test:coverage": "jest --coverage",
    "lint": "eslint src/ tests/"
  },
  "keywords": ["recipes", "ingredients", "food", "recommendations", "api", "meal-planning"],
  "author": "Max Mustermann",
  "license": "MIT",
  "dependencies": {
    "chalk": "^4.1.2",
    "express": "^4.18.2"
  },
  "devDependencies": {
    "eslint": "^8.56.0",
    "jest": "^29.7.0",
    "nodemon": "^3.0.2",
    "supertest": "^6.3.3"
  }
}
EOF

cat > CHANGELOG.md << 'EOF'
# Changelog

## [0.4.0] - 2026-03-25

### Added
- Weekly meal planner
- Shopping list generator with ingredient categories
- Rate limiting middleware
- Recipe validation
- Health check endpoint
- Nutritional estimates

### Changed
- Improved search algorithm with configurable threshold
- Better seasonal recipe boosting

## [0.3.0] - 2025-11-06

### Added
- REST API with Express
- CORS support
- Dietary filters
- API integration tests

## [0.2.0] - 2025-08-28

### Added
- Interactive CLI
- ESLint configuration
- Seasonal recommendations
- Search by tag

## [0.1.0] - 2025-05-23

### Added
- Initial release
- Recipe engine with basic search
- Sample recipe data
- Jest test setup
EOF

add_commit_at "2026-04-12T11:00:00+02:00" "Release v0.4.0 with meal planner and shopping list"

# ============================================================
# COMMIT 46 - Fix edge case in search
# ============================================================
cat > src/engine.js << 'EOF'
class RecipeEngine {
  constructor() {
    this.recipes = new Map();
    this._nextId = 1;
  }

  addRecipe(recipe) {
    const id = this._nextId++;
    this.recipes.set(id, { ...recipe, id });
    return id;
  }

  removeRecipe(id) {
    return this.recipes.delete(id);
  }

  search(ingredients, options = {}) {
    if (!ingredients || ingredients.length === 0) {
      return [];
    }

    const threshold = options.threshold || 0.5;
    const limit = options.limit || 20;
    const normalize = s => s.toLowerCase().trim();
    const normalizedInput = ingredients.map(normalize);

    const allRecipes = Array.from(this.recipes.values());

    return allRecipes
      .map(recipe => {
        const recipeIngredients = (recipe.ingredients || []).map(normalize);
        if (recipeIngredients.length === 0) return { recipe, score: 0 };
        const matched = recipeIngredients.filter(i => normalizedInput.includes(i));
        const score = matched.length / recipeIngredients.length;
        return { recipe, score };
      })
      .filter(({ score }) => score >= threshold)
      .sort((a, b) => b.score - a.score)
      .slice(0, limit)
      .map(({ recipe }) => recipe);
  }

  searchByTag(tag) {
    return Array.from(this.recipes.values()).filter(
      r => r.tags && r.tags.includes(tag)
    );
  }

  getAll() {
    return Array.from(this.recipes.values());
  }

  getById(id) {
    return this.recipes.get(id) || null;
  }

  count() {
    return this.recipes.size;
  }
}

module.exports = { RecipeEngine };
EOF

add_commit_at "2026-04-17T09:20:00+02:00" "Fix edge case when searching with empty ingredients"

# ============================================================
# COMMIT 47 - Add prettier config
# ============================================================
cat > .prettierrc << 'EOF'
{
  "semi": true,
  "singleQuote": true,
  "trailingComma": "es5",
  "printWidth": 100,
  "tabWidth": 2
}
EOF

cat > .prettierignore << 'EOF'
node_modules
coverage
dist
EOF

add_commit_at "2026-05-01T14:30:00+02:00" "Add Prettier configuration"

# ============================================================
# COMMIT 48 - Add environment config
# ============================================================
cat > src/config.js << 'EOF'
const config = {
  port: parseInt(process.env.PORT, 10) || 3000,
  nodeEnv: process.env.NODE_ENV || 'development',
  rateLimit: {
    windowMs: parseInt(process.env.RATE_LIMIT_WINDOW, 10) || 60000,
    max: parseInt(process.env.RATE_LIMIT_MAX, 10) || 100,
  },
  cors: {
    origin: process.env.CORS_ORIGIN || '*',
  },
};

module.exports = config;
EOF

cat > .env.example << 'EOF'
PORT=3000
NODE_ENV=development
RATE_LIMIT_WINDOW=60000
RATE_LIMIT_MAX=100
CORS_ORIGIN=*
EOF

add_commit_at "2026-05-12T10:00:00+02:00" "Add environment configuration module"

# ============================================================
# COMMIT 49 - Update CI for Node 22
# ============================================================
cat > .github/workflows/ci.yml << 'EOF'
name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 22
      - run: npm ci
      - run: npm run lint

  test:
    runs-on: ubuntu-latest
    needs: lint
    strategy:
      matrix:
        node-version: [18.x, 20.x, 22.x]
    steps:
      - uses: actions/checkout@v4
      - name: Use Node.js ${{ matrix.node-version }}
        uses: actions/setup-node@v4
        with:
          node-version: ${{ matrix.node-version }}
      - run: npm ci
      - run: npm run test:coverage
EOF

add_commit_at "2026-05-14T11:15:00+02:00" "Add Node.js 22 to CI matrix"

# ============================================================
# COMMIT 50 - Update README for v0.4
# ============================================================
cat > README.md << 'EOF'
# Fresh Bite 🍽️

A recipe recommendation engine that suggests meals based on your available ingredients.

## Features

- **Smart Search** - Find recipes by available ingredients with relevance scoring
- **Dietary Filters** - Filter by vegetarian, vegan, gluten-free preferences
- **Seasonal Boost** - Prioritize recipes using seasonal ingredients
- **Meal Planning** - Generate weekly meal plans automatically
- **Shopping Lists** - Get categorized shopping lists for your meal plans
- **REST API** - Full-featured API for integration with frontends

## Quick Start

```bash
npm install
npm run dev
```

The API will be available at `http://localhost:3000`.

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/recipes | List all recipes |
| GET | /api/recipes/:id | Get recipe by ID |
| POST | /api/recipes | Create new recipe |
| DELETE | /api/recipes/:id | Delete recipe |
| POST | /api/search | Search by ingredients |
| GET | /api/tags | List all tags |
| GET | /health | Health check |

## CLI Mode

```bash
npm run cli
```

## Development

```bash
npm test            # Run tests
npm run test:coverage  # Run with coverage
npm run lint        # Lint code
```

## Docker

```bash
docker build -t fresh-bite .
docker run -p 3000:3000 fresh-bite
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

MIT © Max Mustermann
EOF

add_commit_at "2026-05-21T15:00:00+02:00" "Update README for v0.4 release"

echo ""
echo "✅ Done! Created 50 commits spanning June 2025 - December 2025"
echo ""
git log --oneline | head -20
echo "..."
echo ""
echo "Total commits: $(git rev-list --count HEAD)"
