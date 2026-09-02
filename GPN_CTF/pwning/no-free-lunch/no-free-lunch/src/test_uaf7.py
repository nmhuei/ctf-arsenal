import heapq
import sys

class Target:
    def __lt__(self, other):
        heap[0] = None
        print('First getrefcount:', sys.getrefcount(self))
        print('Second getrefcount:', sys.getrefcount(self))
        return False

    def __del__(self):
        print('Target deleted!')

heap = [Target()]
print('Calling heappushpop...')
try:
    heapq.heappushpop(heap, b"some item")
except Exception as e:
    print('Exception:', e)
print('Done')
