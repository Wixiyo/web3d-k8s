#!/bin/bash
unzip -d /in in/huayi133
xvfb-run python3 a_sampling/MainGPU.py start_config.json
python3 b_analysis/Main.py start_config.json
