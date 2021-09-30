import numpy as np

from ..AShape import AShape
from ..backend import Kernel
from ..HArgs import HArgs
from ..HKernel import HKernel
from ..HType import HType
from ..info import BroadcastInfo
from ..SCacheton import SCacheton
from ..Tensor import Tensor


def any_wise(op_text : str,
             *args,
             dtype : np.dtype = None,
             output_t:Tensor=None) -> Tensor:
    """
    operator for N-wise ops with N inputs

    arguments
        op_text     example: O=(2*I0*I1)+I2

        *args       List[ Tensor | number ]

        dtype

        output_t            compute result to this Tensor.
                            Tensor may be with different shape, but should match total size.
    """
    HArgs.check_zero_get_length(args)
    tensor_args = HArgs.filter_tensor(args, raise_on_empty=True)
    device = HArgs.check_get_same_device(tensor_args)

    shape_list, dtype_list, krn_args = HArgs.decompose(args)

    op = SCacheton.get(_AnyWiseOp, shape_list, dtype_list, dtype, op_text)

    if output_t is None:
        output_t = Tensor ( op.o_shape, op.o_dtype, device=device )
    elif output_t.shape.size != op.o_shape.size:
        raise ValueError(f'output_t must have size {op.o_shape.size}')

    device.run_kernel(op.forward_krn, output_t.get_buffer(), *krn_args)

    return output_t

class _AnyWiseOp:
    def __init__(self, shape_list, dtype_list, o_dtype, op_text : str):
        if len(shape_list) != len(dtype_list):
            raise ValueError('len(shape_list) != len(dtype_list)')

        self.o_dtype = o_dtype = o_dtype if o_dtype is not None else HType.get_most_weighted_dtype (dtype_list)

        if len(shape_list) == 1:
            # element-wise.
            i_shape, i_dtype = shape_list[0], dtype_list[0]
            self.o_shape = o_shape = i_shape

            self.forward_krn = Kernel(global_shape=(o_shape.size,), kernel_text=f"""
{HKernel.define_tensor('O', o_shape, o_dtype)}
{HKernel.define_tensor('IN', i_shape, i_dtype)}
__kernel void impl(__global O_PTR_TYPE* O_PTR_NAME, __global const IN_PTR_TYPE* IN_PTR_NAME)
{{
size_t gid = get_global_id(0);

O_TYPE O = O_GLOBAL_LOAD(gid);
IN_TYPE I0 = IN_GLOBAL_LOAD(gid);
{op_text};
O_GLOBAL_STORE(gid, O);
}}
""")
        else:
            # Multi arg.
            self.info = info = BroadcastInfo( [ shape if shape is not None else AShape((1,)) for shape in shape_list ])

            self.o_shape = o_shape = info.o_shape

            defs, arg_defs, impls = [], [], []
            for i, (t_shape, t_dtype) in enumerate(zip(shape_list, dtype_list)):
                t_name = f'I{i}'
                if t_shape is not None:
                    defs.append( HKernel.define_tensor(t_name, info.br_shapes[i], t_dtype) )
                    arg_defs.append( f", __global const {t_name}_PTR_TYPE* {t_name}_PTR_NAME" )
                    impls.append( f"{t_name}_TYPE {t_name} = {t_name}_GLOBAL_LOAD({t_name}_IDX_MOD({HKernel.axes_seq_enum('O', info.o_shape.ndim)}));")
                else:
                    arg_defs.append( f", {HKernel.define_scalar_func_arg(t_name, t_dtype)}" )

            defs, arg_defs, impls = '\n'.join(defs), '\n'.join(arg_defs), '\n'.join(impls)

            self.forward_krn = Kernel(global_shape=(o_shape.size,), kernel_text=f"""
{defs}
{HKernel.define_tensor('O', o_shape, o_dtype)}
__kernel void impl(__global O_PTR_TYPE* O_PTR_NAME{arg_defs})
{{
size_t gid = get_global_id(0);
{HKernel.decompose_idx_to_axes_idxs('gid', 'o', o_shape.ndim)}
{impls}
O_TYPE O;
{op_text};
O_GLOBAL_STORE(gid, O);
}}
""")

def add(a_t : Tensor, b_t : Tensor) -> Tensor: return any_wise('O=I0+I1', a_t, b_t)
def sub(a_t : Tensor, b_t : Tensor) -> Tensor: return any_wise('O=I0-I1', a_t, b_t)
def mul(a_t : Tensor, b_t : Tensor) -> Tensor: return any_wise('O=I0*I1', a_t, b_t)
def div(a_t : Tensor, b_t : Tensor) -> Tensor: return any_wise('O=I0/I1', a_t, b_t)
def min_(a_t : Tensor, b_t : Tensor) -> Tensor: return any_wise('O=fmin( I0_TO_FLOATX(I0), I1_TO_FLOATX(I1) )', a_t, b_t)
def max_(a_t : Tensor, b_t : Tensor) -> Tensor: return any_wise('O=fmax( I0_TO_FLOATX(I0), I1_TO_FLOATX(I1) )', a_t, b_t)
def square(a_t : Tensor) -> Tensor:  return any_wise('O=I0*I0', a_t)
def sqrt(a_t : Tensor) -> Tensor:    return any_wise('O=sqrt(I0_TO_FLOATX(I0))', a_t)
