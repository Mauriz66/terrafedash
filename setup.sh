#!/bin/bash

mkdir -p ~/.streamlit/

echo "[server]
headless = true
port = $PORT
enableCORS = false
enableXsrfProtection = false
" > ~/.streamlit/config.toml

echo "[theme]
primaryColor = \"#7E57C2\"
backgroundColor = \"#FFFFFF\"
secondaryBackgroundColor = \"#F0F2F6\"
textColor = \"#262730\"
font = \"sans serif\"
" >> ~/.streamlit/config.toml 