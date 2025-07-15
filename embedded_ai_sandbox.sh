#**
# @file visualize.sh
# @Description
# @author vikas.manavikrishnamurthy@aptiv.com
# @version 1.0
# @date 2025-05-19
#/
#
#!/bin/bash
PORT=8080
python3 -m pip install streamlit &> /dev/null
/home/${USER}/.local/bin/streamlit run stream.py --server.port 8080
