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
