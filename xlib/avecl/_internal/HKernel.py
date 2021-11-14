import numpy as np

class HKernel:
    """
    Helper functions for Kernels
    """

    _np_dtype_to_cl = { np.bool_   : 'bool',
                        np.int8    : 'char',
                        np.uint8   : 'uchar',
                        np.int16   : 'short',
                        np.uint16  : 'ushort',
                        np.int32   : 'int',
                        np.uint32  : 'uint',
                        np.int64   : 'long',
                        np.uint64  : 'ulong',
                        np.float16 : 'half',
                        np.float32 : 'float'
                      }

    @staticmethod
    def np_dtype_to_cl(dtype : np.dtype):
        """
        returns string opencl type  from numpy dtype

        example np.float32  -> 'float'
                np.uint8    -> 'unsigned char'
        """
        return HKernel._np_dtype_to_cl[np.dtype(dtype).type]

    @staticmethod
    def define_scalar_func_arg(name, dtype : np.dtype):
        """
        """
        return f'{HKernel._np_dtype_to_cl[np.dtype(dtype).type]} {name}'

    @staticmethod
    def define_tensor_type(name, dtype : np.dtype):
        """
        Returns a definitions for operations with tensor

        example for 'O', np.float16:

        #define O_PTR_NAME p_O
        #define O_PTR_TYPE half
        #define O_PTR_TYPE2 half2
        #define O_PTR_TYPE3 half3
        #define O_PTR_TYPE4 half4
        #define O_PTR_TYPE8 half8
        #define O_PTR_TYPE16 half16
        #define O_TYPE float
        #define O_TYPE2 float2
        #define O_TYPE3 float3
        #define O_TYPE4 float4
        #define O_TYPE8 float8
        #define O_TYPE16 float16
        #define O_GLOBAL_LOAD(offset)   vload_half  (0, (const __global half*) (&O_PTR_NAME[(offset)]) )
        #define O_GLOBAL_LOAD2(offset)  vload_half2 (0, (const __global half*) (&O_PTR_NAME[(offset)]) )
        #define O_GLOBAL_LOAD3(offset)  vload_half3 (0, (const __global half*) (&O_PTR_NAME[(offset)]) )
        #define O_GLOBAL_LOAD4(offset)  vload_half4 (0, (const __global half*) (&O_PTR_NAME[(offset)]) )
        #define O_GLOBAL_LOAD8(offset)  vload_half8 (0, (const __global half*) (&O_PTR_NAME[(offset)]) )
        #define O_GLOBAL_LOAD16(offset) vload_half16(0, (const __global half*) (&O_PTR_NAME[(offset)]) )
        #define O_GLOBAL_STORE(offset,value)   vstore_half  ( (value), 0, (__global half*) (&O_PTR_NAME[(offset)]) )
        #define O_GLOBAL_STORE2(offset,value)  vstore_half2 ( (value), 0, (__global half*) (&O_PTR_NAME[(offset)]) )
        #define O_GLOBAL_STORE3(offset,value)  vstore_half3 ( (value), 0, (__global half*) (&O_PTR_NAME[(offset)]) )
        #define O_GLOBAL_STORE4(offset,value)  vstore_half4 ( (value), 0, (__global half*) (&O_PTR_NAME[(offset)]) )
        #define O_GLOBAL_STORE8(offset,value)  vstore_half8 ( (value), 0, (__global half*) (&O_PTR_NAME[(offset)]) )
        #define O_GLOBAL_STORE16(offset,value) vstore_half16( (value), 0, (__global half*) (&O_PTR_NAME[(offset)]) )
        #define O_TO_FLOATX(x) ((float)x)
        """
        name_upper = name.upper()

        dtype = np.dtype(dtype).type

        out = [f'#define {name.upper()}_PTR_NAME p_{name.upper()}']

        if dtype == np.float16:
            out += [f'#define {name_upper}_PTR_TYPE half']
            out += [f'#define {name_upper}_PTR_TYPE2 half2']
            out += [f'#define {name_upper}_PTR_TYPE3 half3']
            out += [f'#define {name_upper}_PTR_TYPE4 half4']
            out += [f'#define {name_upper}_PTR_TYPE8 half8']
            out += [f'#define {name_upper}_PTR_TYPE16 half16']
            out += [f'#define {name_upper}_TYPE {HKernel.np_dtype_to_cl(np.float32)}']
            out += [f'#define {name_upper}_TYPE2 {HKernel.np_dtype_to_cl(np.float32)}2']
            out += [f'#define {name_upper}_TYPE3 {HKernel.np_dtype_to_cl(np.float32)}3']
            out += [f'#define {name_upper}_TYPE4 {HKernel.np_dtype_to_cl(np.float32)}4']
            out += [f'#define {name_upper}_TYPE8 {HKernel.np_dtype_to_cl(np.float32)}8']
            out += [f'#define {name_upper}_TYPE16 {HKernel.np_dtype_to_cl(np.float32)}16']


            out += [f'#define {name_upper}_GLOBAL_LOAD(offset)   vload_half  (0, (const __global half*) (&{name_upper}_PTR_NAME[(offset)]) )']
            out += [f'#define {name_upper}_GLOBAL_LOAD2(offset)  vload_half2 (0, (const __global half*) (&{name_upper}_PTR_NAME[(offset)]) )']
            out += [f'#define {name_upper}_GLOBAL_LOAD3(offset)  vload_half3 (0, (const __global half*) (&{name_upper}_PTR_NAME[(offset)]) )']
            out += [f'#define {name_upper}_GLOBAL_LOAD4(offset)  vload_half4 (0, (const __global half*) (&{name_upper}_PTR_NAME[(offset)]) )']
            out += [f'#define {name_upper}_GLOBAL_LOAD8(offset)  vload_half8 (0, (const __global half*) (&{name_upper}_PTR_NAME[(offset)]) )']
            out += [f'#define {name_upper}_GLOBAL_LOAD16(offset) vload_half16(0, (const __global half*) (&{name_upper}_PTR_NAME[(offset)]) )']

            out += [f'#define {name_upper}_GLOBAL_STORE(offset,value)   vstore_half  ( (value), 0, (__global half*) (&{name_upper}_PTR_NAME[(offset)]) )']
            out += [f'#define {name_upper}_GLOBAL_STORE2(offset,value)  vstore_half2 ( (value), 0, (__global half*) (&{name_upper}_PTR_NAME[(offset)]) )']
            out += [f'#define {name_upper}_GLOBAL_STORE3(offset,value)  vstore_half3 ( (value), 0, (__global half*) (&{name_upper}_PTR_NAME[(offset)]) )']
            out += [f'#define {name_upper}_GLOBAL_STORE4(offset,value)  vstore_half4 ( (value), 0, (__global half*) (&{name_upper}_PTR_NAME[(offset)]) )']
            out += [f'#define {name_upper}_GLOBAL_STORE8(offset,value)  vstore_half8 ( (value), 0, (__global half*) (&{name_upper}_PTR_NAME[(offset)]) )']
            out += [f'#define {name_upper}_GLOBAL_STORE16(offset,value) vstore_half16( (value), 0, (__global half*) (&{name_upper}_PTR_NAME[(offset)]) )']

        else:
            out += [f'#define {name_upper}_PTR_TYPE {HKernel.np_dtype_to_cl(dtype)}']
            out += [f'#define {name_upper}_PTR_TYPE2 {HKernel.np_dtype_to_cl(dtype)}2']
            out += [f'#define {name_upper}_PTR_TYPE3 {HKernel.np_dtype_to_cl(dtype)}3']
            out += [f'#define {name_upper}_PTR_TYPE4 {HKernel.np_dtype_to_cl(dtype)}4']
            out += [f'#define {name_upper}_PTR_TYPE8 {HKernel.np_dtype_to_cl(dtype)}8']
            out += [f'#define {name_upper}_PTR_TYPE16 {HKernel.np_dtype_to_cl(dtype)}16']
            out += [f'#define {name_upper}_TYPE {HKernel.np_dtype_to_cl(dtype)}']
            out += [f'#define {name_upper}_TYPE2 {HKernel.np_dtype_to_cl(dtype)}2']
            out += [f'#define {name_upper}_TYPE3 {HKernel.np_dtype_to_cl(dtype)}3']
            out += [f'#define {name_upper}_TYPE4 {HKernel.np_dtype_to_cl(dtype)}4']
            out += [f'#define {name_upper}_TYPE8 {HKernel.np_dtype_to_cl(dtype)}8']
            out += [f'#define {name_upper}_TYPE16 {HKernel.np_dtype_to_cl(dtype)}16']

            out += [f'#define {name_upper}_GLOBAL_LOAD(offset)   {name_upper}_PTR_NAME[(offset)]']
            out += [f'#define {name_upper}_GLOBAL_LOAD2(offset)  {name_upper}_PTR_NAME[(offset)]']
            out += [f'#define {name_upper}_GLOBAL_LOAD3(offset)  {name_upper}_PTR_NAME[(offset)]']
            out += [f'#define {name_upper}_GLOBAL_LOAD4(offset)  {name_upper}_PTR_NAME[(offset)]']
            out += [f'#define {name_upper}_GLOBAL_LOAD8(offset)  {name_upper}_PTR_NAME[(offset)]']
            out += [f'#define {name_upper}_GLOBAL_LOAD16(offset) {name_upper}_PTR_NAME[(offset)]']

            out += [f'#define {name_upper}_GLOBAL_STORE(offset,value) {name_upper}_PTR_NAME[(offset)] = (value)']
            out += [f'#define {name_upper}_GLOBAL_STORE2(offset,value) {name_upper}_PTR_NAME[(offset)] = (value)']
            out += [f'#define {name_upper}_GLOBAL_STORE3(offset,value) {name_upper}_PTR_NAME[(offset)] = (value)']
            out += [f'#define {name_upper}_GLOBAL_STORE4(offset,value) {name_upper}_PTR_NAME[(offset)] = (value)']
            out += [f'#define {name_upper}_GLOBAL_STORE8(offset,value) {name_upper}_PTR_NAME[(offset)] = (value)']
            out += [f'#define {name_upper}_GLOBAL_STORE16(offset,value) {name_upper}_PTR_NAME[(offset)] = (value)']

        if dtype in [np.float32]:
            out += [f'#define {name_upper}_TO_FLOATX(x) x']
        elif dtype in [np.bool_, np.int8, np.uint8, np.int16, np.uint16, np.int32,np.uint32, np.float16]:
            out += [f'#define {name_upper}_TO_FLOATX(x) ((float)x)']
        elif dtype in [np.int64,np.uint64]:
            out += [f'#define {name_upper}_TO_FLOATX(x) ((double)x)']
        return '\n'.join(out)

    @staticmethod
    def define_ndim_idx(ndim):
        """
        define macro to calculate index for n-dim shape

        example for ndim=3

        #define NDIM3_IDX(t0,t1,t2,T0,T1,T2) (((size_t)(t0))*T1*T2+((size_t)(t1))*T2+((size_t)(t2)))
        #define NDIM3_IDX_MOD(t0,t1,t2,T0,T1,T2) (((size_t)(t0) % T0)*T1*T2+((size_t)(t1) % T1)*T2+((size_t)(t2) % T2))
        """

        out = [f'#define NDIM{ndim}_IDX(' + \
                ','.join([f't{i}' for i in range(ndim)] + [f'T{i}' for i in range(ndim)]) + \
                ') (' + '+'.join([f'((size_t)(t{i}))' + ''.join(f'*T{j}' for j in range(i+1,ndim)) for i in range(ndim) ]) + ')']

        out +=[f'#define NDIM{ndim}_IDX_MOD(' + \
                ','.join([f't{i}' for i in range(ndim)] + [f'T{i}' for i in range(ndim)]) + \
                ') (' + '+'.join([f'( (((size_t)(t{i}) % T{i}) + T{i}) % T{i} )    ' + ''.join(f'*T{j}' for j in range(i+1,ndim)) for i in range(ndim) ]) + ')']

        return '\n'.join(out)

    @staticmethod
    def define_tensor_shape(name, shape, axes_symbols=None):
        """
        Returns a definitions for operations with tensor shape

        example for 'O', (2,3),

        #define O0 2
        #define O1 3
        #define Om1 3
        #define Om2 2
        #define O_IDX(o0,o1) (((size_t)(o0))*3+((size_t)(o1)))
        #define O_IDX_MOD(o0,o1) (((size_t)(o0) % 2)*3+((size_t)(o1) % 3))
        """
        shape = tuple(shape)
        ndim = len(shape)
        name_upper = name.upper()
        name_lower = name.lower()

        if axes_symbols is None:
            axes_symbols = "".join([str(i) for i in range(ndim)])
        axes_symbols = axes_symbols.upper()

        out =  [f'#define {name_upper}{axes_symbols[i]} {shape[i]}' for i in range(ndim)]
        out += [f'#define {name_upper}m{i} {shape[-i]}' for i in range(1,ndim+1)]

        out += [f'#define {name_upper}_IDX({HKernel.axes_seq_enum(name, ndim)}) (' + \
                 '+'.join([f'((size_t)({name_lower}{i}))'              + ''.join(f'*{shape[j]}' for j in range(i+1,ndim)) for i in range(ndim)]) + ')']

        out += [f'#define {name_upper}_IDX_MOD({HKernel.axes_seq_enum(name, ndim)}) (' + \
                 '+'.join([f'( (( (size_t)({name_lower}{i}) % {shape[i]} ) + {shape[i]}) % {shape[i]} )' + ''.join(f'*{shape[j]}' for j in range(i+1,ndim)) for i in range(ndim)]) + ')']

        return '\n'.join(out)

    @staticmethod
    def define_tensor(name, shape, dtype : np.dtype, axes_symbols=None):
        """
        Returns a definitions for operations with tensor

        arguments

            name     text

            shape           Iterable

            dtype           np.dtype

            axes_symbols(None)  string of symbols.
                                None -> numeric symbols will be used

        example for 'O', (2,4), np.float16

        #define O_PTR_NAME p_O
        #define O_PTR_TYPE half
        #define O_PTR_TYPE2 half2
        #define O_PTR_TYPE3 half3
        #define O_PTR_TYPE4 half4
        #define O_PTR_TYPE8 half8
        #define O_PTR_TYPE16 half16
        #define O_TYPE float
        #define O_TYPE2 float2
        #define O_TYPE3 float3
        #define O_TYPE4 float4
        #define O_TYPE8 float8
        #define O_TYPE16 float16
        #define O_GLOBAL_LOAD(offset)   vload_half  (0, (const __global half*) (&O_PTR_NAME[(offset)]) )
        #define O_GLOBAL_LOAD2(offset)  vload_half2 (0, (const __global half*) (&O_PTR_NAME[(offset)]) )
        #define O_GLOBAL_LOAD3(offset)  vload_half3 (0, (const __global half*) (&O_PTR_NAME[(offset)]) )
        #define O_GLOBAL_LOAD4(offset)  vload_half4 (0, (const __global half*) (&O_PTR_NAME[(offset)]) )
        #define O_GLOBAL_LOAD8(offset)  vload_half8 (0, (const __global half*) (&O_PTR_NAME[(offset)]) )
        #define O_GLOBAL_LOAD16(offset) vload_half16(0, (const __global half*) (&O_PTR_NAME[(offset)]) )
        #define O_GLOBAL_STORE(offset,value)   vstore_half  ( (value), 0, (__global half*) (&O_PTR_NAME[(offset)]) )
        #define O_GLOBAL_STORE2(offset,value)  vstore_half2 ( (value), 0, (__global half*) (&O_PTR_NAME[(offset)]) )
        #define O_GLOBAL_STORE3(offset,value)  vstore_half3 ( (value), 0, (__global half*) (&O_PTR_NAME[(offset)]) )
        #define O_GLOBAL_STORE4(offset,value)  vstore_half4 ( (value), 0, (__global half*) (&O_PTR_NAME[(offset)]) )
        #define O_GLOBAL_STORE8(offset,value)  vstore_half8 ( (value), 0, (__global half*) (&O_PTR_NAME[(offset)]) )
        #define O_GLOBAL_STORE16(offset,value) vstore_half16( (value), 0, (__global half*) (&O_PTR_NAME[(offset)]) )
        #define O_TO_FLOATX(x) ((float)x)
        #define O0 2
        #define O1 4
        #define Om1 4
        #define Om2 2
        #define O_IDX(o0,o1) ( (size_t)(o0) )*4 +( o1 )
        #define O_IDX_MOD(o0,o1) ( (size_t)(o0) % 2 )*4 +( (o1) % 4 )
        """
        return'\n'.join([ HKernel.define_tensor_type(name, dtype),
                          HKernel.define_tensor_shape(name, shape, axes_symbols)
                        ])

    @staticmethod
    def define_axes_sizes(axis_letter, axes_sizes):
        """
        Returns definitions of axes sizes

        example for 'O', (4,512,512)
        #define O0 4
        #define O1 512
        #define O2 512
        """
        out = ""
        axes_sizes = tuple(axes_sizes)
        ndim = len(axes_sizes)
        for i in range(ndim):
            out += f'#define {axis_letter.upper()}{i} {axes_sizes[i]}\n'

        return out

    @staticmethod
    def decompose_idx_to_axes_idxs(var_name, tensor_name, ndim):
        """
        decompose a size_t variable to axes indexes.
        Keeps original variable untouched.

        Example for 'gid','O',2

        size_t gid_original = gid;
        size_t o1 = gid % O1; gid /= O1;
        #define om1 o1
        size_t o0 = gid % O0;
        #define om2 o0
        gid = gid_original;
        """
        name_lower = tensor_name.lower()
        name_upper = tensor_name.upper()

        out = [f'size_t {var_name}_original = {var_name};']

        for i in range(ndim-1,-1,-1):
            line = f'size_t {name_lower}{i} = {var_name} % {name_upper}{i};'
            if i > 0:
                line += f' {var_name} /= {name_upper}{i};'
            out += [line]
            out += [f'#define {name_lower}m{ndim-i} {name_lower}{i}']

        out += [f'{var_name} = {var_name}_original;']
        return '\n'.join(out)

    @staticmethod
    def axes_order_enum(tensor_name, axes_order):
        """
        returns axis enumeration with given order

        Example
         ('I', (1,2,0)) returns 'i1,i2,i0'
         ('I', 'HW') return 'ih,iw'
        """
        if isinstance(axes_order, str):
            axes_order = axes_order.lower()
        else:
            axes_order = tuple(axes_order)

        name_lower = tensor_name.lower()

        return ','.join( [ f'{name_lower}{axes_order[axis]}' for axis in range(len(axes_order)) ])

    @staticmethod
    def axes_seq_enum(tensor_name, ndim, new_axis=None, zero_axes=None, suffix=None):
        """
        returns axis sequental enumeration with given ndim

        Example

         ('I', 4) returns 'i0,i1,i2,i3'

         ('I', 4, new_axis=('name',1) ) returns 'i0,name,i1,i2,i3'

         ('I', 3, zero_axes=(1,) ) returns 'i0,0,i2'

         ('I', 2, suffix='ih,iw' ) returns 'i0,i1,ih,iw'
        """
        name_lower = tensor_name.lower()
        if zero_axes is not None:
            axes = [ '0' if axis in zero_axes else f'{name_lower}{axis}' for axis in range(ndim) ]
        else:
            axes = [ f'{name_lower}{axis}' for axis in range(ndim) ]

        if suffix is None:
            suffix = []
        else:
            suffix = [suffix]

        if new_axis is not None:
            name, axis = new_axis
            return','.join(axes[:axis] + [name] + axes[axis:] + suffix)
        else:
            return ','.join(axes+ suffix)

    @staticmethod
    def include_constants_pi():
        """
        defines PI constants

         PI_F
         PI_2_F
         PI_4_F
        """
        return f"""
#define  PI_F          3.14159274101257f
#define  PI_2_F        1.57079637050629f
#define  PI_4_F        0.78539818525314f
"""

    @staticmethod
    def include_hash():
        """
        returns hash functions:

         uint  hash_uint_uint(uint v)
         ulong hash_ulong_from_ulong(ulong x)
         float hash_float_from_uint(uint x)
         double hash_double_from_ulong(ulong x)
        """

        return f"""

#define UIF (1.0 / (float)(0xffffffffU))

//from Chris Wellons https://nullprogram.com/blog/2018/07/31/ https://www.shadertoy.com/view/WttXWX
uint hash_uint_from_uint(uint x)
{{
    x ^= x >> 17;
    x *= 0xed5ad4bbU;
    x ^= x >> 11;
    x *= 0xac4c1b51U;
    x ^= x >> 15;
    x *= 0x31848babU;
    x ^= x >> 14;
    return x;
}}

ulong hash_ulong_from_ulong(ulong x)
{{
    x ^= x >> 32;
    x *= 0xd6e8feb86659fd93U;
    x ^= x >> 32;
    x *= 0xd6e8feb86659fd93U;
    x ^= x >> 32;
    return x;
}}

float hash_float_from_uint(uint x)
{{
    return hash_uint_from_uint(x) / (float)(0xffffffffU);
}}

double hash_double_from_ulong(ulong x)
{{
    return (double)hash_ulong_from_ulong(x) / (double)(0xffffffffffffffffU);
}}

/*****************************
UNUSED CODE

//---------- PCG hashes from https://www.shadertoy.com/view/XlGcRh
uint hash_uint_uint(uint v)
{{
    uint state = v * 747796405u + 2891336453u;
    uint word = ((state >> ((state >> 28u) + 4u)) ^ state) * 277803737u;
    return (word >> 22u) ^ word;
}}

uint2 hash_uint2_uint2 (uint2 v)
{{
    v = v * 1664525u + 1013904223u;
    v.x += v.y * 1664525u;
    v.y += v.x * 1664525u;
    v ^= v>>16u;
    v.x += v.y * 1664525u;
    v.y += v.x * 1664525u;
    v ^= v>>16u;
    return v;
}}

uint3 hash_uint3_uint3(uint3 v)
{{
    v = v * 1664525u + 1013904223u;
    v.x += v.y*v.z;
    v.y += v.z*v.x;
    v.z += v.x*v.y;
    v ^= v >> 16u;
    v.x += v.y*v.z;
    v.y += v.z*v.x;
    v.z += v.x*v.y;
    return v;
}}

float hash_float_uint(uint v)
{{
	return (float)( hash_uint_uint(v) ) * UIF;
}}

float2 hash_float2_uint (uint v)
{{
    uint2 q = hash_uint2_uint2( (uint2)(v, 1) );
    return (float2)(q.x, q.y) * UIF;
}}

float3 hash_float3_uint (uint v)
{{
    uint3 q = hash_uint3_uint3( (uint3)(v, 1, 1) );
    return (float3)(q.x, q.y, q.z) * UIF;
}}

//---------- Classic hashes used in shaders

float hash_float_float(float p)
{{

    float x = sin(p*12.9898)*43758.5453;
    return x - floor(x);
}}

float hash_float_float2(float2 p)
{{
    float x = sin( dot(p, (float2)(12.9898, 78.233)) )*43758.5453;
    return x - floor(x);
}}

****************************/


"""

__all__ = ['HKernel']