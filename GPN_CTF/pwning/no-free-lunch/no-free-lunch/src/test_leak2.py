import heapq
class Evil1:
    def __lt__(self, other):
        print("In __lt__")
        heap.clear()
        return False
heap = [Evil1()]
print("Before:", heap)
try: heapq.heappushpop(heap, bytearray(b"HELLO"))
except Exception as e: print("Exception:", e)
print("After")
