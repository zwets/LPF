import time
from multiprocessing.managers import SharedMemoryManager
smm = SharedMemoryManager()
smm.start()
sl = smm.ShareableList(range(4))

#sl = smm.ShareableList([1,1,1,100], name = "mosssemaphore")

time.sleep(300)

smm.shutdown()