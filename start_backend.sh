#!/bin/bash

#fastapi run main.py
uvicorn main:app --reload --no-access-log
