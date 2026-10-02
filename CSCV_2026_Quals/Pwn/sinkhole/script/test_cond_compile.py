from test_variants import test_body

test_body("cond_test", """
arr[0] = obj;
let res = null;
while ((res = arr[1]) !== null) {
  break;
}
return res;
""", "for (let i = 0; i < 20000; i++) fn(i, dummy_arr, dummy);")
