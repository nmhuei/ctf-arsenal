import heapq
class Evil1:
    def __lt__(self, other):
        heap.clear()
        return False
heap = [Evil1()]
target = bytearray(b"DUMMYLEAK")
heapq.heappushpop(heap, target)
print("Pushpop done")
# Try to append to another list and see if it is corrupted
l = []
l.append(1)
print(l)
# Or maybe we can just read from the C API?
