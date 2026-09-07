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
