#!/usr/bin/env python3
"""
Hermes-Based Présence-Parcours Agent
Uses Hermes 3.1-8B as the intelligent agent (no middleware)
"""

import os
import json
import requests
from typing import Optional, Dict, List
from datetime import datetime
import sys

class HermesAgent:
    """Hermes 3.1-8B as the primary intelligent agent"""
    
    def __init__(self):
        # Hermes LLM Configuration
        self.hermes_url = os.getenv("HERMES_API_URL", "http://localhost:8080/v1/chat/completions")
        self.hermes_model = "hermes"
        
        # Notion Configuration
        self.notion_api_key = os.getenv("NOTION_API_KEY", "")
        self.notion_db_id = os.getenv("NOTION_DATABASE_ID", "")
        self.notion_api_url = "https://api.notion.com/v1"
        
        # Agent state
        self.conversation_history = []
        self.system_prompt = self._build_system_prompt()
        
        self._print_header()
    
    def _print_header(self):
        """Print agent header"""
        print("\n" + "="*70)
        print("🧠 HERMES 3.1-8B - PRÉSENCE-PARCOURS AGENT")
        print("="*70)
        print(f"Model: Hermes 3.1-8B (Local GPU)")
        print(f"API: {self.hermes_url}")
        print(f"Notion: {'✅ Connected' if self.notion_api_key else '⚠️ Not configured'}")
        print("="*70 + "\n")
    
    def _build_system_prompt(self) -> str:
        """Build comprehensive system prompt for Hermes"""
        return """You are Hermes, an expert AI agent specialized in Présence-Parcours education platform.

You have extensive knowledge of:
1. STUDENT MANAGEMENT
   - Student progress tracking and analysis
   - Learning objective definition and monitoring
   - Individual education plans (IEP)
   - Competency assessment

2. PEDAGOGICAL PLANNING
   - Lesson planning using modern pedagogy
   - Curriculum alignment
   - Differentiated instruction
   - Assessment design

3. PARENT COMMUNICATION
   - Progress reports generation
   - Achievement summaries
   - Recommendations for home support
   - Concern responses

4. DATA ANALYSIS
   - Student performance trends
   - Learning pattern identification
   - Risk identification and intervention suggestions
   - Cohort analysis

5. NOTION DATABASE INTEGRATION
   - Student record management
   - Database queries and synchronization
   - Automated report generation

Your approach:
✓ Be pedagogically sound and evidence-based
✓ Provide specific, actionable recommendations
✓ Consider individual student needs
✓ Maintain professional, warm communication
✓ Respect confidentiality (GDPR compliant)
✓ Be concise but comprehensive

When users ask about Notion integration, offer to help sync data.
When asked about lesson plans, provide structured, detailed plans.
When analyzing progress, identify specific strengths and areas for improvement.

You can also help with:
- File operations (reading/writing documents)
- System commands for automation
- Python-based calculations and analysis
- General educational questions

Always ask clarifying questions if you need more information to provide quality responses."""
    
    def call_hermes(self, messages: List[Dict]) -> Optional[str]:
        """Call Hermes LLM"""
        try:
            response = requests.post(
                self.hermes_url,
                json={
                    "model": self.hermes_model,
                    "messages": messages,
                    "temperature": 0.7,
                    "top_p": 0.9,
                    "max_tokens": 2048,
                    "stream": False
                },
                timeout=120
            )
            response.raise_for_status()
            content = response.json()['choices'][0]['message']['content']
            return content
        except requests.exceptions.ConnectionError:
            return "❌ Error: Cannot connect to Hermes (http://localhost:8080). Is the LLM server running?\n   Run: docker compose -f docker-compose-llm-only.yml up -d"
        except requests.exceptions.Timeout:
            return "❌ Error: Hermes took too long to respond. Try again."
        except Exception as e:
            return f"❌ Error calling Hermes: {e}"
    
    def query_notion(self, action: str = "list") -> Dict:
        """Query Notion database"""
        if not self.notion_api_key or not self.notion_db_id:
            return {
                "error": "Notion not configured",
                "help": "Set NOTION_API_KEY and NOTION_DATABASE_ID in .env"
            }
        
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
            data = response.json()
            return {
                "status": "success",
                "record_count": len(data.get('results', [])),
                "data": data
            }
        except requests.exceptions.ConnectionError:
            return {"error": "Cannot connect to Notion API"}
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401:
                return {"error": "Invalid Notion API key"}
            elif e.response.status_code == 404:
                return {"error": "Database not found. Check NOTION_DATABASE_ID"}
            else:
                return {"error": f"Notion API error: {e.response.status_code}"}
        except Exception as e:
            return {"error": f"Error querying Notion: {e}"}
    
    def process_user_input(self, user_input: str) -> str:
        """Process user input and generate Hermes response"""
        
        # Check for special commands
        if self._handle_special_command(user_input):
            return self._handle_special_command(user_input)
        
        # Add to conversation history
        self.conversation_history.append({
            "role": "user",
            "content": user_input
        })
        
        # Build messages with system prompt and history
        messages = [
            {"role": "system", "content": self.system_prompt}
        ]
        
        # Add conversation history (last 20 messages to manage context)
        messages.extend(self.conversation_history[-20:])
        
        # Call Hermes
        response = self.call_hermes(messages)
        
        if response:
            # Add to history
            self.conversation_history.append({
                "role": "assistant",
                "content": response
            })
        
        return response or "No response from Hermes"
    
    def _handle_special_command(self, command: str) -> Optional[str]:
        """Handle special commands"""
        cmd = command.lower().strip()
        
        # Status
        if cmd in ["status", "health", "check"]:
            return self._get_status()
        
        # Help
        if cmd in ["help", "?", "commands"]:
            return self._get_help()
        
        # Notion sync
        if "notion" in cmd and ("sync" in cmd or "database" in cmd or "query" in cmd):
            result = self.query_notion("list")
            if "error" in result:
                return f"❌ Notion Error: {result['error']}\n💡 {result.get('help', '')}"
            else:
                return f"✅ Notion Database Synced\n📊 Found {result['record_count']} records"
        
        # Clear history
        if cmd == "clear":
            self.conversation_history = []
            return "✅ Conversation history cleared"
        
        # Exit
        if cmd in ["exit", "quit", "bye"]:
            return None
        
        return None
    
    def _get_status(self) -> str:
        """Get agent status"""
        try:
            hermes_response = requests.get("http://localhost:8080/health", timeout=5)
            hermes_status = "✅ Running" if hermes_response.status_code == 200 else "❌ Not responding"
        except:
            hermes_status = "❌ Unreachable (http://localhost:8080)"
        
        notion_status = "✅ Configured" if self.notion_api_key else "⚠️ Not configured"
        
        return f"""
🤖 HERMES AGENT STATUS
{'='*50}
Hermes LLM:        {hermes_status}
Notion Integration: {notion_status}
Conversation:      {len(self.conversation_history)} messages
Uptime:            {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
{'='*50}
"""
    
    def _get_help(self) -> str:
        """Get help text"""
        return """
🧠 HERMES AGENT - AVAILABLE COMMANDS
{'='*60}

GENERAL COMMANDS:
  "help" or "?"        Show this help
  "status"             Show agent status
  "clear"              Clear conversation history
  "exit"               Close agent

NOTION OPERATIONS:
  "Sync Notion database"          Fetch all student records
  "What students are in my DB?"   List students
  "Show Notion data"              Display database contents

PEDAGOGICAL:
  "Create lesson plan for [topic]"     Generate lesson plan
  "Analyze student [name] progress"    Detailed analysis
  "Design assessment for [topic]"      Create assessment
  "Suggest intervention for [issue]"   Get recommendations

ANALYSIS:
  "What are common learning patterns?"      Trend analysis
  "Identify at-risk students"               Risk identification
  "Compare cohort performance"              Group analysis
  "Generate parent report"                  Create report

GENERAL EDUCATION:
  "Explain [topic] for Grade [X]"          Teaching explanation
  "What are best practices for [...]"      Pedagogical advice
  "Help me understand [concept]"           Concept explanation

Just ask anything about Présence-Parcours, student management,
lesson planning, or assessment!

Type 'exit' to quit
{'='*60}
"""
    
    def interactive_loop(self):
        """Run interactive Hermes agent"""
        print("Type 'help' for commands, 'exit' to quit\n")
        
        while True:
            try:
                user_input = input("You: ").strip()
                
                if not user_input:
                    continue
                
                # Process input
                response = self.process_user_input(user_input)
                
                if response is None:
                    print("\n👋 Goodbye!\n")
                    break
                
                print(f"\n🧠 Hermes: {response}\n")
                
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!\n")
                break
            except Exception as e:
                print(f"❌ Error: {e}\n")
                continue

def main():
    """Main entry point"""
    agent = HermesAgent()
    agent.interactive_loop()

if __name__ == "__main__":
    main()
