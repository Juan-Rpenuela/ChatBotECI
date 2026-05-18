model = VitsModel.load_from_checkpoint(
    args.checkpoint, dataset=None, weights_only=False
)

cambair en el modelo export.onnx.py

from torch.serialization import add_safe_globals
from pathlib import PosixPath
add_safe_globals([PosixPath])

poner detras de la linea de generacion