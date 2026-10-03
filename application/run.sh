#!/bin/bash

echo "============================================"
echo " ROBOT CONTROL + AI DETECTION SYSTEM"
echo "============================================"
echo ""

echo "[1/3] Checking Python..."
python3 --version
if [ $? -ne 0 ]; then
    echo "ERROR: Python3 not found!"
    echo "Please install Python 3.8 or higher"
    exit 1
fi

echo ""
echo "[2/3] Installing dependencies..."
pip3 install -r requirements.txt

echo ""
echo "[3/3] Starting server..."
echo ""
echo "============================================"
echo " Server will start at http://localhost:5000"
echo "============================================"
echo ""

python3 app.py
