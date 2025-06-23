# AIP Demo

## 🛠️ Setup

### 1. Create Virtual Environment
(Windows)
```bash
python -m venv venv
```

OR

(ITB Linux)
```bash
python3 -m venv venv
```

### 2. Configure API Keys in .env


### 3. Activate Virtual Environment
(Windows)
```bash
.\venv\Scripts\Activate
```

OR 

(ITB Linux)
```bash
source venv/bin/activate
```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```


## 🚀 Running the Scripts

#### OLLAMA BACK-END (localhost:8000) ---> ```bash start_ollama.sh```

```bash
export OLLAMA_MODELS=/home/ia-nsdas/models/
export OLLAMA_KEEP_ALIVE=4000
ollama serve
```

#### BACK-END (localhost:8000) ---> ```bash start_backend.sh```
```bash
fastapi run main.py 
```

OR (prefered)

```bash
uvicorn main:app --reload --no-access-log
```

#### FRONT-END (localhost:5501) ---> ```bash start_frontend.sh```
```bash
cd frontend | python -m http.server 5501
```

#### MONITOR (localhost:8501) ---> ```bash start_monitoring.sh```
```bash
streamlit run monitor.py
```




#### (ONLY WINDOWS) BACK-END + FRONT-END + MONITOR --> run start_demo.bat file (opens all)

#### Use the chat

At the end of each session delete temporary files with 'exit' in message prompt.

## To Visualize Graph Diagrams:

Paste the .mmd (Mermaid) file content in: https://mermaid.live/

# Clean pycache

```find . -name "*.pyc" -delete```
This will recursively remove all .pyc files.


```find . -type d -name "__pycache__" -exec rm -r {} +``` 
This will remove all __pycache__ directories in your working directory and subdirectories.