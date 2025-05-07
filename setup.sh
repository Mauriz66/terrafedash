#!/bin/bash

mkdir -p ~/.streamlit/

echo "[general]
email = \"\"
" > ~/.streamlit/credentials.toml

echo "[server]
headless = true
enableCORS = false
enableXsrfProtection = false
port = $PORT
" > ~/.streamlit/config.toml

echo "[theme]
primaryColor = \"#7E57C2\"
backgroundColor = \"#FFFFFF\"
secondaryBackgroundColor = \"#F0F2F6\"
textColor = \"#262730\"
font = \"sans serif\"
" >> ~/.streamlit/config.toml 