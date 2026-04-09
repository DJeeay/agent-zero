"""
UI Streamlit pour Hermes-3 Local
Interface de chat avec l'adaptateur FastAPI OpenAI-compatible
"""

import streamlit as st
import requests
import json
import time
from typing import Iterator

# Configuration
ADAPTER_URL = "http://localhost:9000"
DEFAULT_MODEL = "hermes-3"

# Page config
st.set_page_config(
    page_title="Hermes-3 Local Chat",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS custom
st.markdown("""
<style>
.chat-message {
    padding: 1rem;
    border-radius: 0.5rem;
    margin-bottom: 1rem;
    display: flex;
    flex-direction: column;
}
.chat-message.user {
    background-color: #e3f2fd;
    border-left: 4px solid #2196f3;
}
.chat-message.assistant {
    background-color: #f5f5f5;
    border-left: 4px solid #4caf50;
}
.chat-message .avatar {
    font-size: 1.5rem;
    margin-bottom: 0.5rem;
}
.chat-message .content {
    margin-left: 0;
}
.stStatus {
    position: fixed;
    top: 1rem;
    right: 1rem;
    z-index: 999;
}
</style>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.title("⚙️ Configuration")
    
    # Health check
    try:
        health = requests.get(f"{ADAPTER_URL}/health", timeout=5).json()
        if health["status"] == "ok" and health["llama_server"] == "reachable":
            st.success("✅ Adaptateur OK")
            st.caption(f"Llama server: {health['llama_server']}")
        else:
            st.warning("⚠️ Adaptateur dégradé")
    except Exception as e:
        st.error(f"❌ Adaptateur inaccessible\n```\n{e}\n```")
    
    st.divider()
    
    # Paramètres
    st.subheader("Paramètres LLM")
    
    temperature = st.slider(
        "Temperature",
        min_value=0.0,
        max_value=2.0,
        value=0.7,
        step=0.1,
        help="Créativité des réponses (0=précis, 2=créatif)"
    )
    
    max_tokens = st.slider(
        "Max Tokens",
        min_value=50,
        max_value=2048,
        value=512,
        step=50,
        help="Longueur maximale de la réponse"
    )
    
    top_p = st.slider(
        "Top P",
        min_value=0.0,
        max_value=1.0,
        value=0.9,
        step=0.05,
        help="Diversité des réponses"
    )
    
    stream_mode = st.toggle("Mode Streaming", value=True, 
                           help="Affiche la réponse en temps réel")
    
    st.divider()
    
    # Info système
    st.subheader("ℹ️ Système")
    st.caption(f"**Modèle:** {DEFAULT_MODEL}")
    st.caption(f"**Adaptateur:** {ADAPTER_URL}")
    st.caption(f"**Version:** Hermes-3-Llama-3.1-8B.Q4_K_M")
    
    # Bouton clear
    if st.button("🗑️ Effacer l'historique", type="secondary"):
        st.session_state.messages = []
        st.rerun()

# Main content
st.title("🤖 Hermes-3 Local Chat")
st.caption("Interface pour le modèle Hermes-3 via adaptateur FastAPI OpenAI-compatible")

# Initialiser l'historique
if "messages" not in st.session_state:
    st.session_state.messages = []

# Afficher l'historique
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Input utilisateur
if prompt := st.chat_input("💬 Votre message..."):
    # Ajouter le message utilisateur
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Afficher le message
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Préparer la requête
    messages = [{"role": m["role"], "content": m["content"]} 
                for m in st.session_state.messages]
    
    payload = {
        "model": DEFAULT_MODEL,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "top_p": top_p,
        "stream": stream_mode
    }
    
    # Générer la réponse
    with st.chat_message("assistant"):
        if stream_mode:
            # Mode streaming
            response_placeholder = st.empty()
            full_response = ""
            
            try:
                with requests.post(
                    f"{ADAPTER_URL}/v1/chat/completions",
                    headers={"Content-Type": "application/json"},
                    json=payload,
                    stream=True,
                    timeout=120
                ) as response:
                    response.raise_for_status()
                    
                    for line in response.iter_lines():
                        if line:
                            line = line.decode('utf-8')
                            if line.startswith('data: '):
                                data = line[6:]
                                if data == '[DONE]':
                                    break
                                try:
                                    chunk = json.loads(data)
                                    if chunk.get('choices'):
                                        delta = chunk['choices'][0].get('delta', {})
                                        content = delta.get('content', '')
                                        if content:
                                            full_response += content
                                            response_placeholder.markdown(full_response + "▌")
                                except json.JSONDecodeError:
                                    continue
                
                response_placeholder.markdown(full_response)
                
            except Exception as e:
                st.error(f"Erreur: {e}")
                full_response = f"*Erreur de connexion: {e}*"
        else:
            # Mode non-streaming
            try:
                with st.spinner("Hermes réfléchit..."):
                    response = requests.post(
                        f"{ADAPTER_URL}/v1/chat/completions",
                        headers={"Content-Type": "application/json"},
                        json=payload,
                        timeout=120
                    )
                    response.raise_for_status()
                    data = response.json()
                    full_response = data['choices'][0]['message']['content']
                    st.markdown(full_response)
            except Exception as e:
                st.error(f"Erreur: {e}")
                full_response = f"*Erreur de connexion: {e}*"
        
        # Ajouter à l'historique
        st.session_state.messages.append({
            "role": "assistant", 
            "content": full_response
        })

# Footer
st.divider()
left, center, right = st.columns(3)
with left:
    st.caption("🔗 [Adaptateur API](http://localhost:9000/docs)")
with center:
    st.caption("📊 [Health Check](http://localhost:9000/health)")
with right:
    st.caption("🦙 [Llama Server](http://localhost:8080)")
