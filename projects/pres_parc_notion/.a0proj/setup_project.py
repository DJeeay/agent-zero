import os

# Structure des dossiers
folders = [
    "agent/core",
    "agent/tools",
    "config",
    "docs",
    "scripts",
    "logs",
    "docker",
    "data/rag_index"
]

# Contenu des fichiers
files = {
    "config/settings.yaml": """# Notion Database Mapping
notion:
  base_eleves_id: "${DB_BASE_ELEVES}"
  teacher_databases:
    seances: "${DB_TEACHER_SEANCES}"
    absences: "${DB_TEACHER_ABSENCES}"
    comptes_rendus: "${DB_TEACHER_CR}"
    objectifs: "${DB_TEACHER_OBJECTIFS}"
  parent_databases:
    seances: "${DB_PARENT_SEANCES}"
    absences: "${DB_PARENT_ABSENCES}"
    comptes_rendus: "${DB_PARENT_CR}"
    objectifs: "${DB_PARENT_OBJECTIFS}"

llm:
  base_url: "http://llamacpp:8080/v1"
  model_name: "nanbeige4.1-3b-q4_k_m.gguf"
""",

    ".env": "NOTION_TOKEN=secret_votre_token_ici",

    "docker-compose.yml": """services:
  agent:
    build:
      context: .
      dockerfile: ./docker/Dockerfile.agent
    container_name: presence_agent
    volumes:
      - .:/a0/usr/projects/Projet_Presence-Parcours
    env_file: .env
    environment:
      - TZ=Asia/Ho_Chi_Minh
    networks:
      - presence-net
    ports:
      - "32775:80"

  llamacpp:
    image: localai/localai:latest-aio-gpu-nvidia-cuda-12
    container_name: presence_llamacpp
    hostname: llamacpp
    volumes:
      - D:/llm_models:/models
    environment:
      - MODELS_PATH=/models
      - DEBUG=true
      - THREADS=4
    command: ["--models-path", "/models", "--address", "0.0.0.0:8080"]
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
    networks:
      - presence-net
    ports:
      - "8080:8080"

networks:
  presence-net:
    driver: bridge
""",

    "docker/Dockerfile.agent": """FROM python:3.11-slim
ENV PYTHONUNBUFFERED=1
WORKDIR /app
ENV PYTHONPATH=/app
RUN apt-get update && apt-get install -y build-essential curl && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["python", "scripts/run_sync.py"]
""",

    "requirements.txt": """notion-client==2.2.1
pyyaml==6.0.1
python-dotenv==1.0.1
pytz==2024.1
requests==2.31.0
openai==1.12.0
""",

    "scripts/run_sync.py": """import os, yaml, sys
from dotenv import load_dotenv
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from agent.core.sync_engine import SyncEngine

def main():
    load_dotenv()
    with open("config/settings.yaml", "r") as f:
        config = yaml.safe_load(f)

    try:
        engine = SyncEngine(config)
        engine.run()
        print("✅ Sync terminée.")
    except Exception as e:
        print(f"❌ Erreur : {e}")

if __name__ == "__main__":
    main()
"""
}

def setup():
    print("🏗️ Création de l'arborescence...")
    for folder in folders:
        os.makedirs(folder, exist_ok=True)

    print("📝 Génération des fichiers...")
    for path, content in files.items():
        with open(path, "w", encoding="utf-8") as f:
            f.write(content.strip())

    print("🚀 Setup terminé ! N'oubliez pas de remplir votre .env et settings.yaml.")

if __name__ == "__main__":
    setup()
