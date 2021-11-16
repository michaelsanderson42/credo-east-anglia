import numpy as np
from scipy import signal

a = np.array([[2,3,2,3,5,7,3,6,1],
              [2,3,2,7,3,1,3,6,2],
              [345,1345,45,2,6,1,0,1,1],
              [2,3,2,456,5,7,3,1,1],
              [2,789,2,8,5,7,3,6,1]])

# Filter for averaging 3 x 3 boxes, so centre box will be the average of the 3 x 3 block.
filter_size = 3
b = np.full((filter_size, filter_size), 1/(filter_size*filter_size), dtype=np.float)
 
c = signal.convolve2d(a,b,boundary='symm',mode='same')

print(a)
print(' ')
print(c)
