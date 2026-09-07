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
