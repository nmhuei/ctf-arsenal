import heapq

class Evil1:
    def __eq__(self, other):
        print('In Evil1.__eq__')
        heap.clear()
        return True
    def __del__(self):
        print('In Evil1.__del__')

class Evil2:
    def __gt__(self, other):
        print('In Evil2.__gt__')
        return True

heap = [[Evil1(), 0, 0, 0, 0, 0, 0, 0]]

print('Calling heappushpop...')
try:
    heapq.heappushpop(heap, [0, Evil2(), 0, 0, 0, 0, 0, 0])
except Exception as e:
    print('Exception:', e)
print('Done')
