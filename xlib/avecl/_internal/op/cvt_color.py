import numpy as np

from ..AShape import AShape
from ..backend import Kernel
from ..HKernel import HKernel
from ..SCacheton import SCacheton
from ..Tensor import Tensor


def cvt_color (input_t : Tensor, in_mode : str, out_mode : str, ch_axis=1, dtype=None):
    """
    converts color

     input_t        Tensor  (...,C,...) float16/32/64

     in_mode        str     'RGB', 'BGR', 'XYZ', 'LAB'

     out_mode       str     'RGB', 'BGR', 'XYZ', 'LAB'

     ch_axis(1)     int     num of axis contains channels
                            default 1 (assuming NCHW input)

     dtype          output_dtype    float16/32/64
    """
    op = SCacheton.get(_CvtColor32Op, input_t.shape, input_t.dtype, in_mode, dtype, out_mode, ch_axis)

    device = input_t.get_device()

    if op.output_same_as_input:
        output_t = input_t.copy()
        if dtype is not None:
            output_t = output_t.cast(dtype)
    else:
        output_t = Tensor(op.o_shape, op.o_dtype, device=device)

        device.run_kernel(op.forward_krn, output_t.get_buffer(), input_t.get_buffer(), op.krn_S0, op.krn_S1,
                        global_shape=op.global_shape )

    return output_t

_allowed_modes = ['RGB', 'BGR', 'XYZ', 'LAB']
_allowed_dtypes = [np.float16, np.float32]

class _CvtColor32Op():
    def __init__(self, i_shape : AShape, i_dtype, in_mode, o_dtype, out_mode, ch_axis):
        self.o_dtype = o_dtype = o_dtype if o_dtype is not None else i_dtype

        if in_mode not in _allowed_modes:
            raise ValueError(f'in_mode {in_mode} not in allowed modes: {_allowed_modes}')
        if out_mode not in _allowed_modes:
            raise ValueError(f'out_mode {out_mode} not in allowed modes: {_allowed_modes}')
        if i_dtype not in _allowed_dtypes:
            raise Exception(f'input dtype not in {_allowed_dtypes}')
        if o_dtype not in _allowed_dtypes:
            raise Exception(f'output dtype not in {_allowed_dtypes}')

        in_ch  = 3 if in_mode in ['RGB', 'BGR', 'XYZ', 'LAB'] else None
        out_ch = 3 if in_mode in ['RGB', 'BGR', 'XYZ', 'LAB'] else None
        if i_shape[ch_axis] != in_ch:
            raise ValueError(f'input ch_axis must have size {in_ch} for {in_mode} mode')

        self.o_shape = i_shape.replaced_axes([ch_axis], [out_ch])

        s0_shape, s1_shape = i_shape.split(ch_axis)
        s1_shape = s1_shape[1:]

        self.krn_S0 = np.int64(s0_shape.size)
        self.krn_S1 = np.int64(s1_shape.size)

        self.global_shape = (s0_shape.size*s1_shape.size,)

        self.output_same_as_input = in_mode == out_mode

        if not self.output_same_as_input:

            key = (_CvtColor32Op, in_mode, out_mode, i_dtype, o_dtype)
            krn = SCacheton.get_var(key)
            if krn is None:
                body = None

                if in_mode in ['RGB','XYZ','LAB']:
                    in_args = ['I0','I1','I2']
                elif in_mode == 'BGR':
                    in_args = ['I2','I1','I0']

                if out_mode in ['RGB','XYZ','LAB']:
                    out_args = ['O0','O1','O2']
                elif out_mode == 'BGR':
                    out_args = ['O2','O1','O0']

                get_body_func = _modes_to_body_func.get( (in_mode, out_mode), None )
                if get_body_func is None:
                    raise ValueError(f'{in_mode} -> {out_mode} is not supported.')

                body = get_body_func( *(in_args+out_args) )

                krn = Kernel(kernel_text=_CvtColor32Op.fused_kernel(in_ch, i_dtype, out_ch, o_dtype, body=body))
                SCacheton.set_var(key, krn)

            self.forward_krn = krn

    @staticmethod
    def get_RGB_to_LAB_body(R,G,B,L,a,b, declare_out_type=False) -> str:
        return f"""
{_CvtColor32Op.get_sRGB_to_XYZ_body(R,G,B,'X','Y','Z', declare_out_type=True)}
{_CvtColor32Op.get_XYZ_to_LAB_body('X','Y','Z',L,a,b, declare_out_type=declare_out_type)}
"""

    @staticmethod
    def get_LAB_to_RGB_body(L,a,b,R,G,B, declare_out_type=False) -> str:
        return f"""
{_CvtColor32Op.get_LAB_to_XYZ_body(L,a,b,'X','Y','Z', declare_out_type=True)}
{_CvtColor32Op.get_XYZ_to_sRGB_body('X','Y','Z',R,G,B, declare_out_type=declare_out_type)}
"""

    @staticmethod
    def get_sRGB_to_XYZ_body(R,G,B,X,Y,Z, declare_out_type=False) -> str:
        return f"""
{R} = ({R} > 0.04045)*( pow( ({R}+0.055)/1.055, 2.4) ) + ({R} <= 0.04045)*({R} / 12.92);
{G} = ({G} > 0.04045)*( pow( ({G}+0.055)/1.055, 2.4) ) + ({G} <= 0.04045)*({G} / 12.92);
{B} = ({B} > 0.04045)*( pow( ({B}+0.055)/1.055, 2.4) ) + ({B} <= 0.04045)*({B} / 12.92);

{_CvtColor32Op.get_RGB_to_XYZ_body(R,G,B,X,Y,Z,declare_out_type=declare_out_type) }
"""

    @staticmethod
    def get_RGB_to_XYZ_body(R,G,B,X,Y,Z, declare_out_type=False) -> str:
        return f"""
{'float' if declare_out_type else ''} {X} = {R}*0.412453 + {G}*0.357580 + {B}*0.180423;
{'float' if declare_out_type else ''} {Y} = {R}*0.212671 + {G}*0.715160 + {B}*0.072169;
{'float' if declare_out_type else ''} {Z} = {R}*0.019334 + {G}*0.119193 + {B}*0.950227;
"""

    @staticmethod
    def get_XYZ_to_sRGB_body(X,Y,Z,R,G,B, declare_out_type=False) -> str:
        return f"""
{_CvtColor32Op.get_XYZ_to_RGB_body(X,Y,Z,R,G,B,declare_out_type=declare_out_type) }
{R} = ({R} > 0.0031308)*( 1.055*pow({R},1.0/2.4)-0.055 ) + ({R} <= 0.0031308)*({R} * 12.92);
{G} = ({G} > 0.0031308)*( 1.055*pow({G},1.0/2.4)-0.055 ) + ({G} <= 0.0031308)*({G} * 12.92);
{B} = ({B} > 0.0031308)*( 1.055*pow({B},1.0/2.4)-0.055 ) + ({B} <= 0.0031308)*({B} * 12.92);
"""

    @staticmethod
    def get_XYZ_to_RGB_body(X,Y,Z,R,G,B, declare_out_type=False) -> str:
        return f"""
{'float' if declare_out_type else ''} {R} = clamp( {X}* 3.240479 + {Y}*-1.53715  + {Z}*-0.498535, 0.0, 1.0 );
{'float' if declare_out_type else ''} {G} = clamp( {X}*-0.969256 + {Y}* 1.875991 + {Z}* 0.041556, 0.0, 1.0 );
{'float' if declare_out_type else ''} {B} = clamp( {X}* 0.055648 + {Y}*-0.204043 + {Z}* 1.057311, 0.0, 1.0 );
"""

    @staticmethod
    def get_RGB_to_BGR_body(R,G,B,b,g,r, declare_out_type=False) -> str:
        return f"""
{'float' if declare_out_type else ''} {b} = {R};
{'float' if declare_out_type else ''} {g} = {G};
{'float' if declare_out_type else ''} {r} = {B};
"""

    @staticmethod
    def get_BGR_to_RGB_body(B,G,R,r,g,b, declare_out_type=False) -> str:
        return f"""
{'float' if declare_out_type else ''} {r} = {B};
{'float' if declare_out_type else ''} {g} = {G};
{'float' if declare_out_type else ''} {b} = {R};
"""

    @staticmethod
    def get_XYZ_to_LAB_body(X,Y,Z,L,A,B, declare_out_type=False) -> str:
        beta3 = '((6.0/29.0)*(6.0/29.0)*(6.0/29.0))'
        xyz_xn = '(0.950456)'
        xyz_zn = '(1.088754)'
        return f"""
{X} /= {xyz_xn};
{Z} /= {xyz_zn};

{X} = ({X} > {beta3})*rootn({X}, 3) + ({X} <= {beta3})*(7.787*{X}+4.0/29.0);
{Y} = ({Y} > {beta3})*rootn({Y}, 3) + ({Y} <= {beta3})*(7.787*{Y}+4.0/29.0);
{Z} = ({Z} > {beta3})*rootn({Z}, 3) + ({Z} <= {beta3})*(7.787*{Z}+4.0/29.0);

{'float' if declare_out_type else ''} {L} = 116.0*{Y}-16.0;
{'float' if declare_out_type else ''} {A} = 500.0*({X}-{Y});
{'float' if declare_out_type else ''} {B} = 200.0*({Y}-{Z});
"""
    @staticmethod
    def get_LAB_to_XYZ_body(L,A,B,X,Y,Z, declare_out_type=False) -> str:
        beta = '(6.0/29.0)'
        beta2 = '((6.0/29.0)*(6.0/29.0))'
        xyz_xn = '(0.950456)'
        xyz_zn = '(1.088754)'
        return f"""
{'float' if declare_out_type else ''} {Y} = ({L} + 16.0) / 116.0;
{'float' if declare_out_type else ''} {X} = {Y} + {A} / 500.0;
{'float' if declare_out_type else ''} {Z} = {Y} - {B} / 200.0;

{Y} = ({Y} > {beta})*({Y}*{Y}*{Y})          + ({Y} <= {beta})*({Y}-16.0/116.0)*3*{beta2};
{X} = ({X} > {beta})*({X}*{X}*{X}*{xyz_xn}) + ({X} <= {beta})*({X}-16.0/116.0)*3*{beta2}*{xyz_xn};
{Z} = ({Z} > {beta})*({Z}*{Z}*{Z}*{xyz_zn}) + ({Z} <= {beta})*({Z}-16.0/116.0)*3*{beta2}*{xyz_zn};
"""

    @staticmethod
    def fused_kernel(i_ch : int, i_dtype, o_ch : int, o_dtype, body : str) -> str:
        line_sep = '\n'
        return f"""
{HKernel.define_ndim_idx(o_ch)}
{HKernel.define_ndim_idx(i_ch)}
{HKernel.define_tensor_type('O', o_dtype)}
{HKernel.define_tensor_type('I', i_dtype)}

__kernel void impl(__global O_PTR_TYPE* O_PTR_NAME, __global const I_PTR_TYPE* I_PTR_NAME, long S0, long S1)
{{
size_t gid = get_global_id(0);
{HKernel.decompose_idx_to_axes_idxs('gid', 'S', 2)}

{line_sep.join([f'size_t i_idx{i} = NDIM{i_ch}_IDX(s0, {i}, s1, S0, {i_ch}, S1);' for i in range(i_ch)])}
{line_sep.join([f'size_t o_idx{o} = NDIM{o_ch}_IDX(s0, {o}, s1, S0, {o_ch}, S1);' for o in range(o_ch)])}

{line_sep.join([f'float I{i} = I_GLOBAL_LOAD(i_idx{i});' for i in range(i_ch)])}
{line_sep.join([f'float O{o};' for o in range(o_ch)])}

{body}

{line_sep.join([f'O_GLOBAL_STORE(o_idx{o}, O{o});' for o in range(o_ch)])}
}}
"""

_modes_to_body_func = {
        ('RGB','BGR') : _CvtColor32Op.get_RGB_to_BGR_body,
        ('BGR','RGB') : _CvtColor32Op.get_BGR_to_RGB_body,

        ('RGB','XYZ') : _CvtColor32Op.get_RGB_to_XYZ_body,
        ('RGB','LAB') : _CvtColor32Op.get_RGB_to_LAB_body,
        ('BGR','XYZ') : _CvtColor32Op.get_RGB_to_XYZ_body,
        ('BGR','LAB') : _CvtColor32Op.get_RGB_to_LAB_body,

        ('XYZ','RGB') : _CvtColor32Op.get_XYZ_to_RGB_body,
        ('LAB','RGB') : _CvtColor32Op.get_LAB_to_RGB_body,
        ('XYZ','BGR') : _CvtColor32Op.get_XYZ_to_RGB_body,
        ('LAB','BGR') : _CvtColor32Op.get_LAB_to_RGB_body,

        ('XYZ','LAB') : _CvtColor32Op.get_XYZ_to_LAB_body,
        ('LAB','XYZ') : _CvtColor32Op.get_LAB_to_XYZ_body,
    }
