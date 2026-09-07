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
