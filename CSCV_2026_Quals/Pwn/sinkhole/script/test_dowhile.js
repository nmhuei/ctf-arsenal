let N_BLOCKS = 1200;
let lines = [];
lines.push("function trigger(x, arr, obj) {");
for (let i = 0; i < N_BLOCKS; i++) {
  lines.push(`  if (x === ${i}) return ${i};`);
}
// Preheader:
lines.push("  arr[0] = obj;");
// Loop:
lines.push("  do {");
lines.push("    return arr[1];");
lines.push("  } while (false);");
lines.push("}");
lines.push("return trigger;");

let fn_code = lines.join("\n");
let trigger = new Function(fn_code)();

let dummy_obj = { a: 1 };
for (let i = 0; i < 2000; i++) {
  let a = [1.1, 2.2, 3.3];
  trigger(-1, a, dummy_obj);
}

console.log("Trigger warmed up!");

let farr = [1.1, 2.2, 3.3];
let res = trigger(-1, farr, dummy_obj);
console.log("res type:", typeof res, "res:", res);
