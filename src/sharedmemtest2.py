import time
from multiprocessing.managers import SharedMemoryManager, shared_memory
existing_shm = shared_memory.SharedMemory(name='mosssemaphore')
print (existing_shm)