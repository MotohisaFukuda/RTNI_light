from RTNI_light_source import *

Input =  ""

# One can customize by changing the following part.
rms = ("U","V")        
powers_dic = {"transpose":"+","conjugate":"-","adjoint":"*"}
limit = 4

readable, pythonic = RTNI_light(Input, rms=rms, powers_dic = powers_dic, limit = limit)
print("readable data\n",readable)
print("pythonic data\n",pythonic)