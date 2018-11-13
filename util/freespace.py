import os
f = os.statvfs('/')
print(str(f[0] * f[3]))
