#!/bin/bash
cd ~/projects/fez
# cheap guide on the GPU: train (fidelity check), then all synthetic prompts
( ./venv-gpu/bin/python run_guides.py --input train-input.csv --output train-cheap-gpu.csv --guides cheap --device gpu > log2-train-cheap.txt 2>&1
  ./venv-gpu/bin/python run_guides.py --input synth1.csv --output synth1-cheap-gpu.csv --guides cheap --device gpu > log2-s1-cheap.txt 2>&1
  ./venv-gpu/bin/python run_guides.py --input synth2.csv --output synth2-cheap-gpu.csv --guides cheap --device gpu > log2-s2-cheap.txt 2>&1 ) &
# expensive guide on the GPU, two lanes
( for i in 0 2; do ./venv-gpu/bin/python run_guides.py --input synth1_s$i.csv --output synth1_s$i-exp.csv --guides expensive --device gpu > log2-s1-$i-exp.txt 2>&1; done
  ./venv-gpu/bin/python run_guides.py --input synth2_s0.csv --output synth2_s0-exp.csv --guides expensive --device gpu > log2-s2-0-exp.txt 2>&1 ) &
( for i in 1 3; do ./venv-gpu/bin/python run_guides.py --input synth1_s$i.csv --output synth1_s$i-exp.csv --guides expensive --device gpu > log2-s1-$i-exp.txt 2>&1; done
  ./venv-gpu/bin/python run_guides.py --input synth2_s1.csv --output synth2_s1-exp.csv --guides expensive --device gpu > log2-s2-1-exp.txt 2>&1 ) &
wait
echo ALLDONE > done2.txt
