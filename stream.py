import sys
import streamlit as st
import subprocess
import os
import time
from collections import OrderedDict
import pandas as pd
import matplotlib.pyplot as plt
import json
from PIL import Image
# Import your original CLI application
# from your_cli_app import main_function
TARGET_IP = {"TDA4VH":"root@192.168.1.29",
             "Ambarella":"root@192.168.1.100"}
JUMP_HOST_IP ="nuc-user@10.233.52.61"

log_file_path = "foundry.log"  # Replace with your actual log file path

def add_to_dict(my_dict,key, val):
    if key not in my_dict:
        my_dict[key] = [val] # Create a new list if key doesn't exist
    else:
        my_dict[key].append(val) # Append to existing list


def display_images(image_directory):
# List all .png files in the directory
    if os.path.exists(image_directory):
        png_files = [f for f in os.listdir(image_directory) if f.lower().endswith(".png")]

        if png_files:
            for image_file in png_files:
                image_path = os.path.join(image_directory, image_file)
                image = Image.open(image_path)
                st.image(image, caption=image_file, use_container_width=True)
        else:
            st.warning("No PNG images found in the directory.")
    else:
        st.error(f"Directory '{image_directory}' does not exist.")
#
def tabulate_json(data_dict):
#     {
#   "frameid_0": {
#     "|model|od_grid|Pyramid|out_act|Relu_output_0": {
#       "REF_MAX": "0.49710545",
#       "REF_MIN": "0.0",
#       "QUANTIZED_MAX": "0.49710545",
#       "QUANTIZED_MIN": "0.0",
#       "MAE_NORM": "0.0037309285",
#       "MAX_ABS_DIFF": "0.061801597",
#       "MAX_ABS_DIFF_NORM": "0.12711687",
#       "SQNR(dB)": "23.28308239221258"
#     },
#     "EXECUTION_TIME_MICRO_SECONDS": 4124.4115600000005
#   },
#   "frameid_1": {
#     "|model|od_grid|Pyramid|out_act|Relu_output_0": {
#       "REF_MAX": "0.47352132",
#       "REF_MIN": "0.0",
#       "QUANTIZED_MAX": "0.47352132",
#       "QUANTIZED_MIN": "0.0",
#       "MAE_NORM": "0.0037959483",
#       "MAX_ABS_DIFF": "0.074206315",
#       "MAX_ABS_DIFF_NORM": "0.15508021",
#       "SQNR(dB)": "23.265455191016574"
#     },
#     "EXECUTION_TIME_MICRO_SECONDS": 4124.67148
#   },
#   "PLATFORM": "TDA4VH",
#   "BITWIDTH": "8",
#   "Quantization": "TI.SYMMETRIC"

    out_data_dict = OrderedDict()

    out_data_dict['PLATFORM'] = data_dict['PLATFORM']
    out_data_dict['BITWIDTH'] = data_dict['BITWIDTH']
    out_data_dict['Quantization'] = data_dict['Quantization']
    out_data_dict['tensor_info'] = OrderedDict()
    out_data_dict['EXECUTION_TIME_MICRO_SECONDS'] = data_dict['frameid_0']['EXECUTION_TIME_MICRO_SECONDS']
    num_frames_inferred = data_dict['num_frames_inferred']

    per_frame_dict = data_dict['frameid_0']

    for key,value in per_frame_dict.items():
        if key != 'EXECUTION_TIME_MICRO_SECONDS':
            out_data_dict['tensor_info'][key] = {}
            out_data_dict['tensor_info'][key]['SQNR'] = value['SQNR(dB)']

    return out_data_dict

def render_svg(svg_file_path):
    with open(svg_file_path, "r") as f:
        svg_content = f.read()

    # Embed the SVG directly in the HTML
    st.markdown(f"""
        <div style="display: flex; justify-content: center;">
            {svg_content}
        </div>
    """, unsafe_allow_html=True)
def run_bash_command(command):
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    stdout, stderr = process.communicate()
    return stdout, stderr, process.returncode

def debug_excepthook(type, value, tb):
    traceback.print_exception(type, value, tb)
    print("\nEntering post-mortem debugging...")
    pdb.post_mortem(tb)

def run_app():
    sys.excepthook = debug_excepthook

    # Hide Streamlit style
    hide_streamlit_style = """
     <style>
     #MainMenu {visibility: hidden;}
     footer {visibility: hidden;}
     header {visibility: hidden;}
     </style>
     """
    st.markdown(hide_streamlit_style, unsafe_allow_html=True)

    st.set_page_config(
     page_title="Embedded AI Sandbox", # This changes the browser tab title
     page_icon="",# Optional: adds an emoji/icon to the tab
     layout="wide",# Optional: sets layout to wide
     initial_sidebar_state="expanded" # Optional: expands sidebar by default
            )


    st.image(Image.open("media/Foundry.png"))
    st.title("Embedded AI Sandbox")

    st.sidebar.header("Configuration")

    # Convert CLI arguments to Streamlit inputs

    onnx_file = st.sidebar.selectbox(
        "ONNX Model File",
        options=["./models/HourglassPyramid_radarml-v3p3p1.onnx","models/conv3_add_amba.onnx"],
        help="Select  ONNX model file"
    )

 # Required arguments
    platform = st.sidebar.selectbox(
        "Platform",
        options=["TDA4VH", "Ambarella"],
        help="Select the target platform"
    )

    # Optional arguments with defaults
    bitwidth = st.sidebar.selectbox(
        "Bit Width",
        options=["8", "16"],
        index=0,
        help="Select bit width (default: 8)"
    )

    quantization = st.sidebar.selectbox(
        "Quantization stype",
        options=['TI.SYMMETRIC','TI.ASYMMETRIC','AMB.DRAV2','AMB.DRAV3'],
        help="Select Quantization style"
    )

    # Optional arguments with defaults
    compile_only = st.sidebar.checkbox(
            "compile_only",
            help="Compiles only. Does not attempt inference"
        )

    # Validation before processing
    proceed = True
    if not quantization:
        st.sidebar.error("Quantization style is required")
        proceed = False
    if not platform:
        st.sidebar.error("Platform is required")
        proceed = False
    else:
        if platform == 'TDA4VH':
            ti_valid_q_list = ['TI.SYMMETRIC','TI.ASYMMETRIC']
            if quantization not in ti_valid_q_list:
                st.sidebar.error(f"Invalid Quantization style {quantization} chosen for {platform} platform")
                proceed = False
        elif platform == "Ambarella" :
            amb_valid_q_list = [ 'AMB.DRAV2','AMB.DRAV3']
            if quantization not in amb_valid_q_list:
                st.sidebar.error(f"Invalid Quantization style {quantization} chosen for {platform} platform")
                proceed = False


    if onnx_file is None:
        st.sidebar.error("ONNX file is required")
        proceed = False

        # Process button
    if st.sidebar.button("Compile and infer"):
        if proceed:
            # Save uploaded ONNX file to working directory if provided
            onnx_path = onnx_file

            # Build command arguments as a dictionary
            args = {
                "platform": platform,
                "onnxfile": onnx_path,
                "bitwidth": bitwidth,
                "quantization_style": quantization
            }

            onnxfile_name = onnx_path.split('/')[-1][:-5]
            workingdir = f'{os.getcwd()}/ARTIFACTS_{onnxfile_name}_{platform}_bitwidth_{bitwidth}_q_{quantization}'
            args["workingdir"] =  workingdir

            # Add optional arguments if provided
            if compile_only:
                args["compile_only"] =" --compile_only"

            args["target_ip"] = TARGET_IP[platform]

            args["jump_host_ip"] = JUMP_HOST_IP

            # Display the command that would be executed
            cmd_preview = "python3.10 foundry.py "
            for key, value in args.items():
                cmd_preview += f"--{key} {value} "
            cmd_preview += f" --compare_with_onnx_file {onnx_path}"
            cmd_preview += " --overwrite_workingdir"

            st.code(cmd_preview.replace("--","\n--"), language="bash")

            col1, col2 = st.columns(2)

            with col1:
            # Execute the command
                st.header("Compile - > Inference pipeline")
                with st.spinner("Model compilation in progress ..."):
                    st.info("Starting compilation with the provided parameters")
                    try:

                        os.remove(log_file_path)
                        stdout,stderr,ret_code = run_bash_command(cmd_preview)
                        st.success("Model compilation : success!")
                        with open(f"{workingdir}/output_tensor_comparison.json",'r') as output_json:
                            st.subheader(f"{platform} {bitwidth} bit quantized model vs ONNX float32")
                            st.json(tabulate_json(json.load(output_json)))

                    except Exception as e:
                        st.error(f"An error occurred: {type(e).__name__}: {e}")
            with col2:
                st.header("Plots:Platform vs ONNX")
                display_images(workingdir)



        else:
            st.sidebar.warning("Please fill in all required fields before processing.")





if __name__ == "__main__":
    run_app()
