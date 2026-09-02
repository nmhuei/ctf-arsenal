console.log("Hello from pwn_3in1 guest!");
console.log("typeof gc:", typeof gc);
console.log("typeof console:", typeof console);
console.log("typeof JSON:", typeof JSON);
console.log("typeof ArrayBuffer:", typeof ArrayBuffer);
console.log("typeof Uint8Array:", typeof Uint8Array);
gc();
console.log("gc() works!");
try {
    var buf = new ArrayBuffer(16);
    var arr = new Uint8Array(buf);
    console.log("ArrayBuffer works!");
} catch(e) {
    console.log("ArrayBuffer error:", e.message);
}

















