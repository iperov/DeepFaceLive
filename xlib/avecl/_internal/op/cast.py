from ..Tensor import Tensor

from .any_wise import any_wise

def cast(input_t : Tensor, dtype, output_t:Tensor=None) -> Tensor:
    """
    cast operator

    arguments
        input_t

        dtype

        output_t            compute result to this Tensor.
                            Tensor may be with different shape, but should match total size.
    """
    return any_wise('O=I0', input_t, dtype=dtype, output_t=output_t)
