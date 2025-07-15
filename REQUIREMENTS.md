## Requirements

#### Input Requirements
- REQ_1: input:mandatory onnx file to be converted
- REQ_2: input:mandatory target platform
- REQ_3: input:optional  board IP
- REQ_4: input:optional  mixed precision settings

#### Output Requirements
- REQ_5: Inference outputs in float
- REQ_6: Quantization style and quantization parameters chosen for each layer
- REQ_7: Execution time for the model as a whole
- REQ_8: Per layer Execution time
- REQ_9: Return back errors in conversion, if any

#### Functional requirements
- REQ_10: Shall support inference with ONNX models (onnxruntime=1.16)
- REQ_11: Shall support deployment of onnx models to TDA4VH-TIDL SDK10.1
