import ctypes
import json
import platform
from datetime import datetime, timezone

import tensorrt as trt
from tensorrt_edgellm import runtime
from tensorrt_edgellm._native.detect import detect_platform

cuda = ctypes.CDLL("libcudart.so.13")
runtime_version = ctypes.c_int()
assert cuda.cudaRuntimeGetVersion(ctypes.byref(runtime_version)) == 0
pointer = ctypes.c_void_p()
assert cuda.cudaMalloc(ctypes.byref(pointer), 4096) == 0
assert cuda.cudaMemset(pointer, 42, 4096) == 0
host = (ctypes.c_ubyte * 4096)()
assert cuda.cudaMemcpy(host, pointer, 4096, 2) == 0
assert all(value == 42 for value in host)
assert cuda.cudaFree(pointer) == 0
print(json.dumps({"timestamp_utc": datetime.now(timezone.utc).isoformat(),
                  "python": platform.python_version(),
                  "tensorrt": trt.__version__,
                  "cuda_runtime": runtime_version.value,
                  "cuda_allocation_memset_copy": "passed",
                  "platform": detect_platform().as_dict()}, indent=2), flush=True)
native = runtime.load()
print("EDGELLM_NATIVE_RUNTIME_LOADED", native.__file__, flush=True)
