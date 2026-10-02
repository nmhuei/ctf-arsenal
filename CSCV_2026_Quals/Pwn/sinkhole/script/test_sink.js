let code = 'function trigger(x, arr, val) {\n';
for (let i = 0; i < 1100; i++) {
  code += `  if (x === ${i}) return ${i};\n`;
}
code += `
  arr[0] = val;
  for (let i = 0; i < 1; i++) {
    return arr[1];
  }
}
`;

console.log("Generated code length:", code.length);
