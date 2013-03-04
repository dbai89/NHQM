####################################################
# Now this is working and the code is significantly faster.
# I haven't tried on the CPU, but this code generates a
# 1000x1000 matrix and integrals in each element in ~0.55
# on my computer. Should be able to produce matrices we can
# use in a few seconds. The current technique is a 10th order
# Gauss-Lagendre integration.
####################################################
import pyopencl as cl
import pyopencl.array as cl_array
import numpy
import numpy.linalg as la
import scipy as sp
from pyopencl.elementwise import ElementwiseKernel
import time

# Make shure we use the GPU for computations.
platform=cl.get_platforms()
gpu_devices=platform[0].get_devices(device_type=cl.device_type.GPU)
ctx=cl.Context(devices=gpu_devices) # Context
queue = cl.CommandQueue(ctx) # Queue

# Timing, to see how fast the code is now.
t1=time.time()

# Create all the necessary arrays.
end_val=10.0
start_val=0.0
side_length=1000
x_vector=numpy.array([i%side_length for i in range(side_length**2)])
y_vector=numpy.array([(i-i%side_length)/side_length for i in range(side_length**2)])
gpu_matrix_x=cl_array.to_device(ctx,queue,(x_vector).astype(numpy.float32))
gpu_matrix_y=cl_array.to_device(ctx,queue,(y_vector).astype(numpy.float32))
gpu_matrix_res=cl_array.empty_like(gpu_matrix_x)

# Kernel to generate an identity matrix.
krnl_identity_matrix=ElementwiseKernel(ctx,"int *x, int *y, float *res",
    "res[i]=get_element(x[i],y[i])",preamble="""
    float get_element(int x, int y)
    {
        return x==y;
    }
    """)
# Kernel to generate a matrix through integrals depending on row and column. 
# The integrand is given in the C-function f().
krnl_gaussian_matrix=ElementwiseKernel(ctx,"float *x, float *y, float start, float end, float step, float *res",
    "res[i]=get_element(x[i],y[i],start,end,step)",
    preamble="#define PI 3.14159f\n"+
    "".join(open("bessel.cl",'r').readlines())+
    "".join(open("potential.cl",'r').readlines())+
    """
    float get_elemen2(float x, float y, float start, float end, float step)
    {
        return x+y;
    }
    float get_element(float x, float y, float start, float end,float step)
    {
        float mass=0.019272;
        float w[20]={0.1527533871307258	,
	0.1527533871307258	,
	0.1491729864726037	,
0.1491729864726037	,
	0.1420961093183820	,
	0.1420961093183820	,
	0.1316886384491766	,
	0.1316886384491766	,
	0.1181945319615184	,
	0.1181945319615184	,
	0.1019301198172404	,
	0.1019301198172404	,
	0.0832767415767048	,
	0.0832767415767048	,
	0.0626720483341091	,
	0.0626720483341091	,
	0.0406014298003869	,
	0.0406014298003869	,
	0.0176140071391521	,
	0.0176140071391521	};
        float xx[20]={-0.0765265211334973,
	0.0765265211334973,
	-0.2277858511416451,
	0.2277858511416451,
	-0.3737060887154195,
0.3737060887154195,
-0.5108670019508271,
0.5108670019508271,
-0.6360536807265150,
		0.6360536807265150,
		-0.7463319064601508,
		0.7463319064601508,
		-0.8391169718222188,
		0.8391169718222188,
		-0.9122344282513259,
		0.9122344282513259,
		-0.9639719272779138,
		0.9639719272779138,
	-0.9931285991850949,
	0.9931285991850949};
        
        /*float w[10]={0.2955242247147529,0.2955242247147529,0.2692667193099963,0.2692667193099963,
            0.2190863625159820,	0.2190863625159820,	0.1494513491505806,	0.1494513491505806,
            0.0666713443086881,	0.0666713443086881};
        float xx[10]={-0.1488743389816312,0.1488743389816312,-0.4333953941292472,0.4333953941292472,
            -0.6794095682990244,0.6794095682990244,-0.8650633666889845,0.8650633666889845,
            -0.9739065285171717,0.9739065285171717};*/
        float sum=0.0;
        for (int i=0;i<20;i++)
            sum += (w[i] * integrand( ((end-start)/2.0)*xx[i] + (start+end)/2.0, x, y, step));
        float integral=(end-start)*sum/2.0;
        float diagonal=((x+0.0)*(x+0.0)*step*step)/(2*mass)*(fabs(x-y)<0.001);
        return diagonal+2*((y+0.0)*(y+0.0)*step*step)*step*integral/PI;
    }
    """)
    
# Chose which kernel to execute.
#krnl_identity_matrix(gpu_matrix_x,gpu_matrix_y,gpu_matrix_res)
krnl_gaussian_matrix(gpu_matrix_x,gpu_matrix_y,start_val,end_val,(end_val-start_val)/side_length,gpu_matrix_res)

# Reshape to matrix.
shape=(side_length,side_length)
# Calculate eigenvalues of the matrix.

#print gpu_matrix_res.get()

[eigs,_]=la.eig(gpu_matrix_res.get().reshape(shape))
indexes = eigs.argsort()
eigs = sp.real_if_close(eigs[indexes])
print eigs[0:5] # Print eigenvalues.
#gpu_matrix_res.get()

# Timing, again.
t2=time.time()
print "Time: ", (t2-t1)