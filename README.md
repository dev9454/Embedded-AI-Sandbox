# Introduction


![image](./media/Foundry.png)

**Embedded AI Sandbox** is a tool to enable sandbox-style experiments by making it easy for developers
to import->quantize->infer their models on various HW platforms.


## Setup

### Clone the release branch
``` bash
git clone --branch <release tag> ssh://git@gitlab.aptiv.today:2289/embedded-ai-factory/tools/foundry.git --depth 1
```

### Docker environment

##### First time Docker setup


1. Update contents of /etc/docker/daemon.json to add this gitlab server to insecure registeries
```bash
{
  "insecure-registries": ["gitlab.aptiv.today:4567"]
}
```

2. Ensure that your **user** is part of the **docker** group. If not, run the below command to do so.
```bash
sudo usermod -aG docker $USER
```
If this is not done, you may see an error like this: `permission denied while trying to connect to the Docker daemon socket at unix:///var/run/docker.sock`

3. Log-out and restart the docker daemon

```bash
docker logout && sudo systemctl restart docker
```

4. Re-login and pull the docker image

 ```bash
docker login gitlab.aptiv.today:4567
docker pull gitlab.aptiv.today:4567/embedded-ai-factory/tools/foundry/ti:latest
docker logout
```

4. Start docker
```bash
docker/start_docker.sh
```

### Usage
```bash
$ python3 foundry.py -h

usage: foundry [-h] --platform {TDA4VH,Ambarella} --onnxfile ONNXFILE
               --workingdir WORKINGDIR [--overwrite_workingdir]
               [--bitwidth {8,16}] [--compile_only] [--emulation_only]
               [--report_unsupported_ops] [--target_ip] [--jump_host_ip]
               [--calibration_data] [--inference_data]
               [--quantization_style {TI.SYMMETRIC,TI.ASYMMETRIC,AMB.DRAV2,AMB.DRAV3}]
               [--mixed_precision_layers] [--float_input_tensors]
               [--enable_layer_traces [ENABLE_LAYER_TRACES]]
               [--platform_sdk_root] [--compare_with_onnx_file]
               [--reference_h5] [--flash_fw]
               [--verbosity {info,warning,error,debug}] [--devmode]

Deploy a given onnx model on to the specified platform

options:
  -h, --help            show this help message and exit
  --platform {TDA4VH,Ambarella}
                        [mandatory] target platform
  --onnxfile ONNXFILE   [mandatory] onnx model
  --workingdir WORKINGDIR
                        [mandatory] workspace
  --overwrite_workingdir
                        [optional] Overwrites the contents of the workdir
  --bitwidth {8,16}     [optional] Quantization bitwidth.Defaults to 8 bits
  --compile_only        [optional] Compiles the model for the given platform.
                        Does not infer
  --emulation_only      [optional] Runs inference in host emulation. And not
                        on target
  --report_unsupported_ops
                        [optional][Experimental feature] Analyzes the onnx
                        graph and reports Unsupported ops for this platform
  --target_ip           [optional] user@targetipaddress
  --jump_host_ip        [optional] user@jumphostip
  --calibration_data    [optional] Data for model calibration [.h5]
  --inference_data      [optional] Data for inference [.h5]
  --quantization_style {TI.SYMMETRIC,TI.ASYMMETRIC,AMB.DRAV2,AMB.DRAV3}
                        [optional] Quantization style. TI defaults to
                        TI.SYMMETRIC. Ambarella defaults to AMB.DRAV3
  --mixed_precision_layers
                        [optional] Comma seperated list of tensors to be in 16
                        bit
  --float_input_tensors
                        [optional] List of input tensors that are consumed as
                        float without quantization by the model
  --enable_layer_traces [ENABLE_LAYER_TRACES]
                        [optional] Enable layer traces. Can be used without
                        arguments to enable all layers, or with a comma-
                        separated list of tensor names.
  --platform_sdk_root   [optional] Path to the platform sdk root
  --compare_with_onnx_file
                        [optional] ONNX executable model to compare against
  --reference_h5        [optional] Path to the reference h5. This is used for
                        comparison of inference results
  --flash_fw            [optional] Flashes the target with firmware
  --verbosity {info,warning,error,debug}
                        [optional] Verbosity of the logging
  --devmode             [optional] Development mode. Only for developers of
                        the embedded ai sandbox
```
### TIDL

```
docker/start_docker.sh # Enter docker environment for TI


### TI example
``` bash
~/projects/foundry$ cat examples/ti_example.sh

python3 foundry.py --platform TDA4VH \
--workingdir ti_test \
--onnxfile models/conv3_add.onnx \
--bitwidth 8 \
--emulation_only \
--compare_with_onnx_file models/conv3_add.onnx \
--overwrite_workingdir \
--verbosity warning \


vikas@4b98159ef0b2:~/projects/foundry$ examples/ti_example.sh

```

#### Artifacts
```
On successful conversion and inference on target we can see inside the artifacts directory for the following

- model files : tidl_io_8bit.bin, tidl_net_8bit.bin
- svg :  Svg file containing the tidl converted graph representation, tensor shapes, scale and data type information
- layer benchmarks : trace/tidl_infer_tda4.txt_perf_processed.csv ( if run on the actual target. Not generated in emulation mode)
- if compare_with_onnx_file was enabled, the tool also generates a per frame tensor analysis json file,
```

#### Per layer benchmarks

The layer benchmarks csv will look something like this 

|  Layer |      Layer Cycles | SourceMem  | DestMem    |
|--------|-------------------|------------|------------|
| OutA   | 287304            |        DDR |        DDR |
| OutB   | 268219            |        DDR |        DDR |
| OutApB | 162784            |        DDR |       MSMC |
| OutC   | 269042            |        DDR |        DDR |
| OutBpC | 217114            |        DDR |        DDR |
| OutABC | 193057            |        DDR |        DDR |

- The Layer name specifies the output tensor name for that layer
- Layer Cycles are the cycles taken by that layer. for a 1 GHz devices, this is in Nano seconds
- Source memory and Dest memory indicate which kind of memory this tensor is placed in . DDR is slower and MSMC is faster.


### Ambarella

TBD


## Change request / BUG report

- If you have a bug to report or a feature that you think would be interesting
please submit a [ticket](https://gitlab.aptiv.today/embedded-ai-factory/tools/foundry/-/issues/new)
