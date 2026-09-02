import heapq, sys
class Evil1:
    def __lt__(self, other):
        heap.clear()
        return False
heap = [Evil1()]
target = bytearray(b"HELLO")
heapq.heappushpop(heap, target)

# Check if another empty list has target as its first element?!
# Wait, no ctypes. Let's just create an empty list and append!
l2 = []
l2.append(1) # maybe it was corrupted?
print(l2)
