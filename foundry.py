#!/usr/bin/python3
##
# @file foundry.py
# @author vikas.manavikrishnamurthy@aptiv.com


import sys
import os
import logging
import argparse
import traceback
import datetime
import pdb
import shutil

from typing import List,Dict,Optional,Union
from collections import OrderedDict
import numpy as np

from src.platforms.tidl.tidl import Tidl
from src.platforms.ambarella.ambarella import Ambarella
from src.utils.tensor import Tensor

from src.utils.onnxrt_api import OnnxWrapper
#FIXME Ambarella podman does not yet have the hdf5 library
from src.datahandler.hdf5_helper import Hdf5,H5Writer
from src.plugins.tensordiff import compare_hdf5
from src.utils.errors import (dir_present,
                              file_present,
                              remove_dir_contents,
                              is_dir_empty,
                              FoundryError,
                              FoundryErrorType)
from src.utils.logger import (get_logger,
                               setup_logger)

from src.utils.misc import write_to_json

def debug_excepthook(type, value, tb):
    traceback.print_exception(type, value, tb)
    print("\nEntering post-mortem debugging...")
    pdb.post_mortem(tb)


def _map_logger_verbosity(input_arg:str) -> int:
    """
    Maps a string representation of logging verbosity to its corresponding logging level.

    Parameters:
        input_arg (str): A string representing the desired logging verbosity level.
                         Valid values are 'info', 'warning', 'error', and 'debug' (case-sensitive).

    Returns:
        int: The corresponding logging level constant from the `logging` module.

    Raises:
        KeyError: If the input_arg is not one of the valid logging levels defined in the logger_dict.
    """
    logger_dict = {}
    try:
        logger_dict['info'] = logging.INFO
        logger_dict['warning'] = logging.WARNING
        logger_dict['error'] = logging.ERROR
        logger_dict['debug'] = logging.DEBUG
        return logger_dict[input_arg]
    except:
        logging.ERROR

class CustomFormatter(logging.Formatter):
    """
    Custom logging formatter to add color to log messages based on their level.
    """

    def format(self, record):
        """
        Format the specified record as text.

        Args:
            record (LogRecord): The log record to format.

        Returns:
            str: The formatted log message with appropriate color coding.
        """
        RED = '\033[31m'
        GREEN = '\033[32m'
        RESET = '\033[0m'

        log_fmt = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        formatter = logging.Formatter(log_fmt)
        if record.levelno == logging.INFO:
            log_fmt = f"{GREEN}{log_fmt}{RESET}"
        elif record.levelno == logging.ERROR:
            log_fmt = f"{RED}{log_fmt}{RESET}"
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)



def parse_commandline_args():

    class LayerTracesAction(argparse.Action):
        def __call__(self, parser, namespace, values, option_string=None):
            if values is True:
                setattr(namespace, self.dest, True)
            else:
                layers = [layer.strip() for layer in values.split(',')]
                setattr(namespace, self.dest, layers)


    parser = argparse.ArgumentParser(
            prog="foundry",
            description="Deploy a given onnx model on to the specified platform")
    parser.add_argument("--platform",
                        help="[mandatory] target platform",choices=["TDA4VH","Ambarella"],required=True)
    parser.add_argument("--onnxfile",
                        help="[mandatory] onnx model",required=True)
    parser.add_argument("--workingdir",
                        help="[mandatory] workspace",required=True)
    parser.add_argument("--overwrite_workingdir",action='store_true',
                        help="[optional] Overwrites the contents of the workdir")
    parser.add_argument("--bitwidth",
                         help="[optional] Quantization bitwidth." \
                         "Defaults to 8 bits",choices=['8','16'],default='8')
    parser.add_argument("--compile_only", action='store_true',
                        help="[optional] Compiles the model for the given platform. Does not infer")
    parser.add_argument("--emulation_only", action='store_true',
                        help="[optional] Runs inference in host emulation. And not on target")
    parser.add_argument("--report_unsupported_ops",action='store_true',
                        help="[optional][Experimental feature] Analyzes the onnx graph and reports Unsupported ops for this platform")
    parser.add_argument("--target_ip",
                        help="[optional] user@targetipaddress",metavar='')
    parser.add_argument("--jump_host_ip",
                        help="[optional] user@jumphostip",metavar='')
    parser.add_argument("--calibration_data",
                        help="[optional] Data for model calibration [.h5]",metavar='')
    parser.add_argument("--inference_data",
                        help="[optional] Data for inference [.h5]",metavar='')
    parser.add_argument("--quantization_style",
                        help="[optional] Quantization style. TI defaults to TI.SYMMETRIC. Ambarella defaults to AMB.DRAV3",choices=['TI.SYMMETRIC','TI.ASYMMETRIC','AMB.DRAV2','AMB.DRAV3'],
                        )
    parser.add_argument("--mixed_precision_layers",
                        help="[optional] Comma seperated list of tensors to be in 16 bit" \
                        ,metavar='')
    parser.add_argument("--float_input_tensors",
                        help="[optional] List of input tensors that are consumed as " \
                        "float without quantization by the model",metavar='')
    parser.add_argument('--enable_layer_traces',
                        action=LayerTracesAction,
                        nargs='?',
                        const=True,
                        help='[optional] Enable layer traces. Can be used without arguments to enable all layers, or with a comma-separated list of tensor names.')
    parser.add_argument("--platform_sdk_root", help="[optional] Path to the platform sdk root",metavar='')
    parser.add_argument("--compare_with_onnx_file",
                        help="[optional] ONNX executable model to compare against",metavar='')
    parser.add_argument("--reference_h5",
                        help="[optional] Path to the reference h5. " \
                        "This is used for comparison of inference results",metavar='')
    parser.add_argument("--flash_fw", action='store_true',
                        help="[optional] Flashes the target with firmware\n")
    parser.add_argument("--verbosity",
                         choices=['info','warning','error','debug'], default='info',
                        help="[optional] Verbosity of the logging")
    parser.add_argument("--devmode", action='store_true',
                        help="[optional] Development mode. Only for developers of the sandbox \n")


    args = parser.parse_args()

    if args.platform.lower() not in ['tda4vh', 'ambarella']:
        parser.error("Invalid platform. Choose either 'TDA4VH' or 'Ambarella'.")

    if not os.path.isfile(args.onnxfile):
        parser.error(f"ONNX file '{args.onnxfile}' does not exist.")

    if args.bitwidth not in ['8', '16']:
        parser.error("Bitwidth must be either '8' or '16'.")

    if args.calibration_data and not os.path.isfile(args.calibration_data):
        parser.error(f"Calibration data file '{args.calibration_data}' does not exist.")

    if args.inference_data and not os.path.isfile(args.inference_data):
        parser.error(f"Inference data file '{args.inference_data}' does not exist.")

    if args.platform_sdk_root and not os.path.isdir(args.platform_sdk_root):
        parser.error(f"Platform SDK root '{args.platform_sdk_root}' does not exist.")

    if args.compare_with_onnx_file and not os.path.isfile(args.compare_with_onnx_file):
        parser.error(f"ONNX file for comparison '{args.compare_with_onnx_file}' does not exist.")

    if args.reference_h5 and not os.path.isfile(args.reference_h5):
        parser.error(f"Reference H5 file '{args.reference_h5}' does not exist.")

    return args

class DeploymentInfo:

    def __init__(self,
                 cmd_args,
                 logger
                ):
        self.info = dict()
        self.platform = cmd_args.platform
        self.working_dir = cmd_args.workingdir
        self.target_ip = cmd_args.target_ip

        self.supportedPlatforms = dict()
        self.supportedPlatforms["TDA4VH"]=True

        self.supportedPlatforms["Ambarella"]=True

        self.onnxFrontend =  OnnxWrapper(cmd_args.onnxfile)
        self.flash_firmware = cmd_args.flash_fw
        self.emulation_only = cmd_args.emulation_only
        self.jump_host_ip = cmd_args.jump_host_ip
        self.calibration_data_path = cmd_args.calibration_data
        self.inference_data_path = cmd_args.inference_data
        self.ref_onnx_frontend = OnnxWrapper(cmd_args.compare_with_onnx_file) if cmd_args.compare_with_onnx_file!=None else None
        self.bitwidth = 8 if cmd_args.bitwidth is None else cmd_args.bitwidth

        ################################################################################# Handle Layer traces
        self.intermediate_tensors = None
        self.trace_all_layers = False

        if cmd_args.enable_layer_traces is True:
            self.intermediate_tensors = False
            self.trace_all_layers = True

        elif isinstance(cmd_args.enable_layer_traces, list):
            self.intermediate_tensors = cmd_args.enable_layer_traces
        #If user wants to debug intermediate_tensors then add it in  both the platform onnx and the onnx executable

        if isinstance(self.intermediate_tensors, list):
            self.onnxFrontend.add_tensors_to_output(self.intermediate_tensors)
            if self.ref_onnx_frontend is not None:
                self.ref_onnx_frontend.add_tensors_to_output(self.intermediate_tensors)
        ################################################################################# Handle Layer traces

        self.platform_config_dict = dict()
        self.platform_config_dict['SDK'] = cmd_args.platform_sdk_root

        self.mixed_precision_layers = None if cmd_args.mixed_precision_layers is None else cmd_args.mixed_precision_layers.split(",")
        self.platform_sdk_root = cmd_args.platform_sdk_root
        self.reference_h5 = cmd_args.reference_h5
        self.report_unsupported_ops = cmd_args.report_unsupported_ops
        self.platform_config_dict['QUANT'] = cmd_args.quantization_style

        self.float_input_tensors = cmd_args.float_input_tensors.split(",") if cmd_args.float_input_tensors != None else None
        self.compile_only = cmd_args.compile_only if cmd_args.compile_only is True else False
        self.overwrite_workingdir = cmd_args.overwrite_workingdir if cmd_args.overwrite_workingdir is True else False

        if cmd_args.devmode is True:
            sys.excepthook = debug_excepthook

        self._handle_working_dir()

        self.info['PLATFORM'] = self.platform
        self.info['BITWIDTH'] = self.bitwidth
        self.info['Quantization'] = self.platform_config_dict['QUANT']
        return


    def _check_if_safe_workspace(self):
        """Validate that the workspace path is appropriate for deletion."""
        working_dir = self.working_dir

        # Check if path exists
        if not os.path.exists(working_dir):
            raise FoundryError(f"working_dir:{working_dir} Does not exist",FoundryErrorType.DIR_NOT_FOUND)

        # Check if path is a directory
        if not os.path.isdir(working_dir):
            raise FoundryError(f"{working_dir} is not a directory",FoundryErrorType.INCORRECT_CMD_LINE_ARGS)

        # Protect against deleting things in dangerous paths
        dangerous_paths = ['/', '/usr', '/etc', '/bin', '/home', '/var', '/tmp',
                          os.path.expanduser('~'), os.path.dirname(os.path.expanduser('~'))]

        # Normalize paths for comparison
        norm_workspace = os.path.normpath(os.path.abspath(working_dir))

        if norm_workspace in [os.path.normpath(os.path.abspath(p)) for p in dangerous_paths]:
            raise FoundryError(f"Cannot use {working_dir} as workspace - protected system path",FoundryErrorType.INCORRECT_CMD_LINE_ARGS)

        return


    def _initialize_workspace(self):
        foundry_marker_file = f"{self.working_dir}/foundry.mark"
        with open(foundry_marker_file, 'w') as f:
            utc_datetime = datetime.datetime.now(datetime.timezone.utc)
            f.write(f"Marker file created at UTC datetime: {utc_datetime}")

    def _delete_working_dir_contents(self):
        #Check if foundry.mark is found
        working_dir_was_created_by_foundry = file_present(f"{self.working_dir}/foundry.mark")

        self._check_if_safe_workspace()

        if working_dir_was_created_by_foundry:
            remove_dir_contents(self.working_dir)
        else:
            raise FoundryError(f"working_dir:{self.working_dir} does not have the mark of having been created by the foundry application. Please remove it manually",FoundryErrorType.CANNOT_REMOVE_WORK_DIR)


    def _handle_working_dir(self):
        """
        Handle the working directory for the deployment process.

        This method manages the working directory specified for the deployment,
        including creation, overwriting, and initialization.

        Parameters:
            None (uses self.working_dir and self.overwrite_workingdir)

        Returns:
            None

        Raises:
            FoundryError: If the working directory already exists and overwrite is not allowed,
                          or if there's an issue with directory creation or initialization.

        Behavior:
            - If the working directory exists and overwrite is not allowed, raises an error.
            - If the working directory exists and overwrite is allowed, it deletes the contents
              and reinitializes the workspace.
            - If the working directory doesn't exist, it creates the directory and initializes
              the workspace.
            - Updates the self.workingdir to the absolute path

        Note:
            - Uses helper methods _delete_working_dir_contents() and _initialize_workspace()
              for managing directory contents and initialization.
            - Logs warnings and info messages about directory operations.
        """


        if dir_present(self.working_dir) and self.overwrite_workingdir is False:
            raise FoundryError(f"working_dir:{self.working_dir} already exists.  Either remove it manually or use the --overwrite_workingdir option",FoundryErrorType.CANNOT_REMOVE_WORK_DIR)

        if dir_present(self.working_dir) and is_dir_empty(self.working_dir):
               logger.info(f'Using already available empty working dir {self.working_dir}')
               self._initialize_workspace()
        elif dir_present(self.working_dir) and self.overwrite_workingdir is True:
               logger.warning(f'Overwriting contents of working dir {self.working_dir}')
               self._delete_working_dir_contents()
               self._initialize_workspace()
        elif dir_present(self.working_dir) is False:
            os.mkdir(self.working_dir)
            self._initialize_workspace()
            logger.info('Working directory does Not Exist. Creating %s', self.working_dir)

        self.working_dir = os.path.abspath(self.working_dir)




    def data_preparation( self,
            onnxFrontend: OnnxWrapper,
        file_path: str) -> Optional[Dict[str,List[Tensor]]]:

        tensor_names = onnxFrontend.input_names
        input_shapes_dict = onnxFrontend.input_shapes_dict

        tensor_dict = OrderedDict({tensor_input:[]  for tensor_input in tensor_names})

        if file_path is None:
            #No data was given, we need to generate data on our own
            #We shall use 2 frames for calibration with randomized data
            num_frames = 2
            for frame in range(0,num_frames):
                for tensor_input in tensor_names:
                    tensor_shape = input_shapes_dict[tensor_input]
                    t = Tensor(tensor_shape,np.float32)
                    t.fill_with_random_data(41 + frame,min=-1.0,max=1.0)
                    tensor_dict[tensor_input].append(t)
        else:
            #Read the .h5 calibdata and prepare calib dictionary
            hf = Hdf5(file_path)

            num_frames = hf.get_number_of_frames()

            for tensor_input in tensor_names:

                tensor_shape = input_shapes_dict[tensor_input]

                for frame in range(0,num_frames):
                    raw_data = hf.get_tensor(tensor_input,frame)
                    dtype = np.int16 if raw_data.dtype==np.int64 else raw_data.dtype
                    raw_data = raw_data.astype(np.int16) if raw_data.dtype==np.int64 else raw_data
                    t = Tensor(tensor_shape,
                            raw_data.dtype,
                            scale=1.0,
                            data=raw_data)

                    tensor_dict[tensor_input].append(t)

        return tensor_dict


    def get_calibration_data_as_dict(self):
        """
        Retrieves calibration data as a dictionary.

        This method prepares and returns calibration data for the ONNX model. It uses the
        data preparation method to process either pre-existing calibration data or generate
        random data if no calibration data is provided.

        Returns:
        --------
        Dict[str, List[Tensor]]
            A dictionary where keys are input tensor names and values are lists of Tensor
            objects. Each list contains calibration data for the corresponding input tensor.

        Notes:
        ------
        - The method uses the ONNX frontend (self.onnxFrontend) to determine input tensor
          names and shapes.
        - If calibration_data_path is not provided, it generates random data for calibration.
        - The data preparation is handled by the self.data_preparation method, which is
          responsible for either loading data from a file or generating random data.
        - The returned dictionary is ordered, maintaining the order of input tensors as
          defined in the ONNX model.
        """

        if self.calibration_data_path is None:
            logger.warning("No calibration data given. Calibrating with random data")
        return self.data_preparation(self.onnxFrontend,
        self.calibration_data_path)

    def get_inference_data_as_dict(self):
        """
        Retrieves inference data as a dictionary.

        This method prepares and returns inference data for the ONNX model. It uses the
        data preparation method to process either pre-existing inference data or generate
        random data if no inference data is provided.

        Returns:
        --------
        Dict[str, List[Tensor]]
            A dictionary where keys are input tensor names and values are lists of Tensor
            objects. Each list contains inference data for the corresponding input tensor.

        Notes:
        ------
        - The method uses the ONNX frontend (self.onnxFrontend) to determine input tensor
          names and shapes.
        - If inference_data_path is not provided, it may generate random data for inference.
        - The data preparation is handled by the self.data_preparation method, which is
          responsible for either loading data from a file or generating random data.
        - The returned dictionary is ordered, maintaining the order of input tensors as
          defined in the ONNX model.
        - This method is similar to get_calibration_data_as_dict, but uses inference_data_path
          instead of calibration_data_path.
        """

        if self.inference_data_path is None:
            logger.warning("No inference data given. Generating random data for inference")
        return self.data_preparation(self.onnxFrontend,
        self.inference_data_path)

    def get_onnx_frontend(self)->OnnxWrapper:
        """
           Retrieves the ONNX frontend object.

           This method returns the ONNX frontend object that was initialized during the creation
           of the DeploymentInfo instance. The ONNX frontend provides an interface to interact
           with and analyze the ONNX model.

           Returns:
           -------
           OnnxWrapper
               An instance of the OnnxWrapper class that represents the ONNX model frontend.

        """

        return self.onnxFrontend

    def check_for_platform_support(self)->None:
        """
        Check if the current platform is supported.

        This method verifies whether the platform specified in the DeploymentInfo instance
        is supported by comparing it against a list of supported platforms.

        Raises:
        RuntimeError: If the specified platform is not in the list of supported platforms.
        """
        if self.platform not in self.supportedPlatforms:
            raise RuntimeError(f"Unsupported target_platform: {self.platform}.\n\nShould be one of {list(self.supportedPlatforms.keys())}")


    def get_platform_handler(self)->Union[None,Tidl,Ambarella]:
        """
        Retrieves the platform object for the specified target platform.

        This method creates and returns an instance of the appropriate platform class
        based on the platform specified in the DeploymentInfo instance.

        Returns:
        --------
        Union[None, Tidl, Ambarella]
            An instance of the platform-specific class (either Tidl or Ambarella).

        Raises:
        -------
        RuntimeError
            If an unsupported platform is specified.
        """
        handler = None

        self.check_for_platform_support()

        if self.platform == "TDA4VH":
            handler = Tidl()
        elif self.platform == "Ambarella":
            handler = Ambarella()

        return handler

import logging


if __name__ == "__main__":

    args = parse_commandline_args()

    logger_verbosity = _map_logger_verbosity(args.verbosity)

    setup_logger("foundry.log",
				logger_verbosity)

    logger = get_logger()

    di = DeploymentInfo(args,logger)
    platform = di.get_platform_handler()



    calibration_tensor_dict = di.get_calibration_data_as_dict()

    try:
        logger.info(f"Model compilation to {di.platform} in progress")

        platform.compile(di.onnxFrontend,
                di.working_dir,
                calibration_tensor_dict,
                di.bitwidth,
                di.platform_config_dict,
                di.mixed_precision_layers,
                di.float_input_tensors
                )

    except Exception as e:
        logger.error(f" {e}")
        error_msg = traceback.format_exc()
        logger.error(f'Traceback\nf{error_msg}')
        logger.error(f"Model compilation failed ")
        if(di.report_unsupported_ops == True):
         logger.info(f"Now scanning the model for unsupported ops")
         unsupported_ops = platform.check_for_unsupported_ops(di.onnxFrontend,
                 di.working_dir)
         if(len(unsupported_ops) > 0):
             logger.info("****************************************************")
             logger.info(f"The following ops seem to be unsupported on {di.platform}")
             logger.info("****************************************************")

             [print(op) for op in unsupported_ops]

             logger.info(f"Per node artifacts are available at {di.working_dir}/unsupported_ops_check")
             logger.info("*****************************************")
        sys.exit(-1)

    logger.info(f"Model compilation successful. Model artifacts are written to directory {di.working_dir}")

    #If compile_only flag is enabled, then stop here
    if (di.compile_only == True):
            logger.info(f"Stopped at compilation stage because of the --compile_only flag")
            logger.info(f"END")
            sys.exit(0)

    platform.prepare_hw(di.target_ip,
                        di.jump_host_ip,
            di.flash_firmware,
            di.emulation_only)

    #FIXME: prepare_data_for_inference should take data from the input file
    inference_feed_dict = None

    logger.info(f"Running model inference on {di.platform} target : {di.target_ip}")

    #FIXME: For now give calibration data itself for inference. This is because for Ambarella flow that we are aware of,
    #we need to specify inference data at compile time and we dont do that currently. We are using the calib data itself
    inference_tensor_dict = di.get_inference_data_as_dict() if di.platform != "Ambarella" else di.get_calibration_data_as_dict()

    num_frames_for_inferences = len(inference_tensor_dict[list(inference_tensor_dict.keys())[0]])

    platform_infer_filename = f"{di.working_dir}/{di.platform}_output.h5"
    platform_trace_filename = f"{di.working_dir}/trace_{di.platform}_output.h5"

    onnx_output_filename = f"{di.working_dir}/ONNX_output.h5" if di.ref_onnx_frontend != None else None
    onnx_trace_filename = f"{di.working_dir}/trace_ONNX_output.h5" if di.ref_onnx_frontend != None else None

    platform_infer_file = H5Writer(platform_infer_filename)
    platform_trace_file = H5Writer(platform_trace_filename)

    onnx_infer_file = H5Writer(onnx_output_filename) if di.ref_onnx_frontend != None else None
    onnx_trace_file = H5Writer(onnx_trace_filename) if di.ref_onnx_frontend != None else None
    exec_times = []
    SQNRS = []

    for infer_frame_id in range(0,num_frames_for_inferences):
        logger.info(f"Infering frame [{infer_frame_id}]")

        #Create a feed dictionary for inference
        infer_feed_dict = {tensor_name:inference_tensor_dict[tensor_name][infer_frame_id] for tensor_name in inference_tensor_dict.keys() }

        #run inference on platform
        infer_results_dict,trace_dict,run_time_stats = platform.run_inference(infer_feed_dict,di.trace_all_layers)

        logger.info(f"Avg Execution in microseconds {run_time_stats}")

        exec_times.append(run_time_stats)


        #run inference on onnx
        onnx_infer_results_dict = di.ref_onnx_frontend.inference(infer_feed_dict) if di.ref_onnx_frontend != None else None
        onnx_trace_dict = {}
        if(di.trace_all_layers == True):
            onnx_trace_dict = di.ref_onnx_frontend.inference_save_traces(infer_feed_dict) if di.ref_onnx_frontend != None else None


        #Write platform inference results to a file in the working_dir
        for tensor_name,tensor in infer_results_dict.items():
            platform_infer_file.write_dataset(tensor_name,
                    np.expand_dims(tensor.dequantized_data(None),axis=0))
        for tensor_name,tensor in trace_dict.items():
            platform_trace_file.write_dataset(tensor_name,
                    np.expand_dims(tensor.dequantized_data(None),axis=0))


        #Write onnx inference results to a file in the working_dir
        if(di.ref_onnx_frontend!=None):
            for tensor_name,tensor in onnx_infer_results_dict.items():
                onnx_infer_file.write_dataset(tensor_name,
                        np.expand_dims(tensor.dequantized_data(None),axis=0))
            for tensor_name,tensor in onnx_trace_dict.items():
               onnx_trace_file.write_dataset(tensor_name,
                       np.expand_dims(tensor.dequantized_data(None),axis=0))

    #END OF INFERENCE LOOPS

    #Analysis of the inference starts here
    logger.info(f"{di.platform} Platform inference data written to {platform_infer_filename}")

    if(di.reference_h5 != None):
        logger.info(f"Comparing inference with provided reference h5 ...")
        logger.info(f"Tensor comparisons written to {di.working_dir}/tensor_comparison.json")
        dict_compare = compare_hdf5(filename,di.reference_h5,di.working_dir)
        write_to_json(dict_compare,f"{di.working_dir}/tensor_comparison.json")

    #Compare and plot the output tensors

    if(di.ref_onnx_frontend != None):
        logger.info(f"Onnx inference data written to {onnx_output_filename}")
        logger.info(f"Tensor comparisons written to {di.working_dir}/tensor_comparison.json")
        dict_comparison = compare_hdf5(platform_infer_filename,onnx_output_filename,di.working_dir,platform_name=f"{di.platform}")
        for frame_idx,time in enumerate(exec_times):
            dict_comparison[f'frameid_{frame_idx}']['EXECUTION_TIME_MICRO_SECONDS'] = time

        dict_comparison['PLATFORM'] = di.info['PLATFORM']
        dict_comparison['BITWIDTH'] = di.info['BITWIDTH']
        dict_comparison['Quantization'] = di.info['Quantization']
        dict_comparison['num_frames_inferred'] = infer_frame_id + 1

        write_to_json(dict_comparison,f"{di.working_dir}/output_tensor_comparison.json")

        if(di.trace_all_layers == True):
            dict_comparison = compare_hdf5(platform_trace_filename,onnx_trace_filename,di.working_dir,f"{di.working_dir}/trace_tensor_comparison.json","trace_output",platform_name=f"{di.platform}")
            write_to_json(dict_comparison,f"{di.working_dir}/trace_tensor_comparison.json")

    logger.info('END')
    sys.exit(0)
