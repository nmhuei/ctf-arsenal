import heapq
class Evil1:
    def __lt__(self, other):
        return False
heap = [Evil1()]
res = heapq.heappushpop(heap, bytearray(b"HELLO"))
print("Returns:", res)

class Evil2:
    def __lt__(self, other):
        return True
heap = [Evil2()]
res = heapq.heappushpop(heap, bytearray(b"HELLO"))
print("Returns:", res)
