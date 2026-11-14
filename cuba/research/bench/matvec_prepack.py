import time, numpy as np, onnx, onnxruntime as ort, sys
from onnx import helper, TensorProto
S = sys.argv[1]
packed = np.load("work/sub_v5/index/vectors.npy")
codes = np.empty((packed.shape[1] * 2, len(packed)), dtype=np.int8); codes[0::2] = (packed >> 4).T; codes[1::2] = (packed & 15).T
x = np.random.default_rng(0).integers(0, 255, (1, 768)).astype(np.uint8)
ref = (x.astype(np.int64) - 128) @ codes.astype(np.int64)
def graph(w_as_input, w_shape):
    ins = [helper.make_tensor_value_info("x", TensorProto.UINT8, [1, "dim"]), helper.make_tensor_value_info("xz", TensorProto.UINT8, [])]
    if w_as_input:
        ins.append(helper.make_tensor_value_info("W", TensorProto.INT8, ["dim", "n"]))
    g = helper.make_graph([helper.make_node("MatMulInteger", ["x", "W", "xz"], ["y"])], "matvec", ins,
        [helper.make_tensor_value_info("y", TensorProto.INT32, [1, "n"])],
        [helper.make_tensor("W", TensorProto.INT8, w_shape, [0] * int(np.prod(w_shape)))])
    m = helper.make_model(g, opset_imports=[helper.make_opsetid("", 13)]); m.ir_version = 8
    return m.SerializeToString()
import pickle
models = {}
for name, m in (("placeholder const, sev3", graph(False, [768, 1])), ("overridable input", graph(True, [768, 1]))):
    so = ort.SessionOptions(); so.intra_op_num_threads = 1; so.inter_op_num_threads = 1; so.log_severity_level = 3
    val = ort.OrtValue.ortvalue_from_numpy(codes); so.add_initializer("W", val)
    models[name] = m; s = ort.InferenceSession(m, so, providers=["CPUExecutionProvider"])
    ts = []
    for _ in range(60):
        t = time.process_time(); y = s.run(None, {"x": x, "xz": np.array(128, np.uint8)})[0]; ts.append(time.process_time() - t)
    print(f"{name:26s} inputs {[i.name for i in s.get_inputs()]} exact {bool((y == ref).all())} p50 {1e3*np.median(ts):.2f} ms")
pickle.dump(models, open(f"{S}/mmi4_models.pkl", "wb"))
