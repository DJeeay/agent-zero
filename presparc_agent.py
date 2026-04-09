#!/usr/bin/env python3
"""
Présence-Parcours Docker Agent
Local AI orchestrator using Hermes LLM + Notion integration
"""

import os
import json
import requests
from typing import Optional
from datetime import datetime

class PresarcAgent:
    """AI agent for Présence-Parcours educational management"""
    
    def __init__(self):
        # LLM Configuration
        self.llm_url = "http://localhost:8080/v1/chat/completions"
        self.llm_model = "hermes"  # Local model
        
        # Notion Configuration
        self.notion_api_key = os.getenv("NOTION_API_KEY", "")
        self.notion_db_id = os.getenv("NOTION_DATABASE_ID", "")
        self.notion_api_url = "https://api.notion.com/v1"
        
        # Agent state
        self.conversation_history = []
        self.memory = {}
        
        print("✅ Présence-Parcours Agent initialized")
        print(f"   LLM: {self.llm_url}")
        print(f"   Notion: {'configured' if self.notion_api_key else 'not configured'}")
    
    def call_llm(self, messages: list) -> str:
        """Call local Hermes LLM"""
        try:
            response = requests.post(
                self.llm_url,
                json={
                    "model": self.llm_model,
                    "messages": messages,
                    "temperature": 0.7,
                    "max_tokens": 2048,
                    "stream": False
                },
                timeout=60
            )
            response.raise_for_status()
            return response.json()['choices'][0]['message']['content']
        except Exception as e:
            return f"Error calling LLM: {e}"
    
    def query_notion(self, query: str) -> dict:
        """Query Notion database"""
        if not self.notion_api_key or not self.notion_db_id:
            return {"error": "Notion not configured. Set NOTION_API_KEY and NOTION_DATABASE_ID"}
        
        try:
            headers = {
                "Authorization": f"Bearer {self.notion_api_key}",
                "Notion-Version": "2022-06-28",
                "Content-Type": "application/json"
            }
            
            response = requests.post(
                f"{self.notion_api_url}/databases/{self.notion_db_id}/query",
                headers=headers,
                json={"page_size": 100},
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": f"Notion query failed: {e}"}
    
    def process_command(self, user_input: str) -> str:
        """Process user command and generate response"""
        
        # Add to history
        self.conversation_history.append({
            "role": "user",
            "content": user_input
        })
        
        # System prompt
        system_prompt = """You are an expert AI assistant for Présence-Parcours education platform.
You help with:
- Student management and progress tracking
- Lesson planning and scheduling
- Parent communications
- Learning objective tracking
- Progress analysis and reporting

Be concise, professional, and pedagogically sound."""
        
        # Prepare messages for LLM
        messages = [
            {"role": "system", "content": system_prompt}
        ]
        
        # Add last few messages from history
        messages.extend(self.conversation_history[-10:])
        
        # Call LLM
        response = self.call_llm(messages)
        
        # Add response to history
        self.conversation_history.append({
            "role": "assistant",
            "content": response
        })
        
        return response
    
    def handle_special_command(self, command: str) -> Optional[str]:
        """Handle special commands"""
        command_lower = command.lower().strip()
        
        # Notion sync
        if "notion" in command_lower and ("sync" in command_lower or "database" in command_lower):
            result = self.query_notion("sync")
            if "error" in result:
                return f"❌ {result['error']}"
            else:
                return f"✅ Synced {len(result.get('results', []))} records from Notion"
        
        # Status
        if command_lower in ["status", "health", "check"]:
            return self._get_status()
        
        # Help
        if command_lower in ["help", "?"]:
            return self._get_help()
        
        # Exit
        if command_lower in ["exit", "quit", "bye"]:
            return None
        
        return None
    
    def _get_status(self) -> str:
        """Get agent status"""
        try:
            llm_response = requests.get("http://localhost:8080/health", timeout=5)
            llm_status = "✅ Running" if llm_response.status_code == 200 else "❌ Not responding"
        except:
            llm_status = "❌ Unreachable"
        
        notion_status = "✅ Configured" if self.notion_api_key else "⚠️ Not configured"
        
        return f"""
Agent Status:
  LLM Server: {llm_status}
  Notion Integration: {notion_status}
  Memory: {len(self.conversation_history)} messages
  Uptime: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
    
    def _get_help(self) -> str:
        """Get help text"""
        return """
Présence-Parcours Agent Commands:

General:
  "help" or "?" - Show this help
  "status" - Show agent status
  "exit" - Close agent
  "clear" - Clear conversation history

Notion Operations:
  "sync Notion database" - Fetch student records
  "create lesson plan" - Generate lesson plan
  "analyze student progress" - Analyze performance

Any other text will be processed by the AI agent.
"""
    
    def interactive_loop(self):
        """Run interactive chat loop"""
        print(f"\n{'='*60}")
        print("🤖 Présence-Parcours Docker Agent - Interactive Mode")
        print(f"{'='*60}\n")
        print("Type 'help' for commands, 'exit' to quit\n")
        
        while True:
            try:
                user_input = input("You: ").strip()
                
                if not user_input:
                    continue
                
                # Check for special commands
                special_response = self.handle_special_command(user_input)
                
                if special_response is None:
                    if user_input.lower() in ["exit", "quit", "bye"]:
                        print("\nGoodbye! 👋")
                        break
                    elif user_input.lower() == "clear":
                        self.conversation_history = []
                        print("Conversation cleared.")
                        continue
                    else:
                        # Normal AI response
                        response = self.process_command(user_input)
                else:
                    response = special_response
                
                print(f"\nAgent: {response}\n")
                
            except KeyboardInterrupt:
                print("\n\nGoodbye! 👋")
                break
            except Exception as e:
                print(f"Error: {e}")
                continue

if __name__ == "__main__":
    agent = PresarcAgent()
    agent.interactive_loop()
