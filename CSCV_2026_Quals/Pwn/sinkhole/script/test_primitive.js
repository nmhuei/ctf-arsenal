// Construct a function with > 1024 blocks
let N_BLOCKS = 1200;
let lines = [];
lines.push("function trigger(x, arr, obj) {");
for (let i = 0; i < N_BLOCKS; i++) {
  lines.push(`  if (x === ${i}) return ${i};`);
}
// Preheader:
lines.push("  arr[0] = obj;");
// Loop:
lines.push("  for (let i = 0; i < 1; i++) {");
lines.push("    return arr[1];");
lines.push("  }");
lines.push("}");
lines.push("return trigger;");

let fn_code = lines.join("\n");
let trigger = new Function(fn_code)();

// Let's test warming up trigger
let dummy_obj = { a: 1 };
for (let i = 0; i < 1000; i++) {
  let a = [1.1, 2.2, 3.3];
  trigger(-1, a, dummy_obj);
}

// Now test with float array
let farr = [1.1, 2.2, 3.3];
let res = trigger(-1, farr, dummy_obj);
console.log("res:", res);
