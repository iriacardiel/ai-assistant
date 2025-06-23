#!/bin/bash

export OLLAMA_MODELS=/home/ia-nsdas/models/
export OLLAMA_KEEP_ALIVE=4000
echo "OLLAMA_MODELS:" $OLLAMA_MODELS
echo "OLLAMA_KEEP_ALIVE:" $OLLAMA_KEEP_ALIVE
ollama serve

