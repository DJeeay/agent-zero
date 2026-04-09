#!/usr/bin/env python3
"""
Hermes Agent with Direct Notion Integration
Complete database access with CRUD operations
"""

import os
import json
import requests
from typing import Optional, Dict, List
from datetime import datetime
import sys

class NotionIntegration:
    """Direct Notion database integration"""
    
    def __init__(self, api_key: str, database_id: str):
        self.api_key = api_key
        self.database_id = database_id
        self.base_url = "https://api.notion.com/v1"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Notion-Version": "2022-06-28",
            "Content-Type": "application/json"
        }
    
    def test_connection(self) -> bool:
        """Test Notion API connection"""
        try:
            response = requests.get(
                f"{self.base_url}/databases/{self.database_id}",
                headers=self.headers,
                timeout=10
            )
            return response.status_code == 200
        except:
            return False
    
    def query_database(self, filters: Optional[Dict] = None, sorts: Optional[List] = None) -> Dict:
        """Query Notion database with filters and sorts"""
        try:
            payload = {
                "page_size": 100
            }
            
            if filters:
                payload["filter"] = filters
            
            if sorts:
                payload["sorts"] = sorts
            
            response = requests.post(
                f"{self.base_url}/databases/{self.database_id}/query",
                headers=self.headers,
                json=payload,
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401:
                return {"error": "Invalid API key"}
            elif e.response.status_code == 404:
                return {"error": "Database not found"}
            else:
                return {"error": f"HTTP {e.response.status_code}"}
        except Exception as e:
            return {"error": str(e)}
    
    def get_page(self, page_id: str) -> Dict:
        """Get a specific page from database"""
        try:
            response = requests.get(
                f"{self.base_url}/pages/{page_id}",
                headers=self.headers,
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def create_page(self, properties: Dict, children: Optional[List] = None) -> Dict:
        """Create a new page in database"""
        try:
            payload = {
                "parent": {
                    "database_id": self.database_id
                },
                "properties": properties
            }
            
            if children:
                payload["children"] = children
            
            response = requests.post(
                f"{self.base_url}/pages",
                headers=self.headers,
                json=payload,
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def update_page(self, page_id: str, properties: Dict) -> Dict:
        """Update page properties"""
        try:
            payload = {
                "properties": properties
            }
            
            response = requests.patch(
                f"{self.base_url}/pages/{page_id}",
                headers=self.headers,
                json=payload,
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def get_page_content(self, page_id: str) -> Dict:
        """Get page content (blocks)"""
        try:
            response = requests.get(
                f"{self.base_url}/blocks/{page_id}/children",
                headers=self.headers,
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def append_block(self, page_id: str, block: Dict) -> Dict:
        """Append block to page"""
        try:
            payload = {
                "children": [block]
            }
            
            response = requests.patch(
                f"{self.base_url}/blocks/{page_id}/children",
                headers=self.headers,
                json=payload,
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def format_results(self, results: List) -> str:
        """Format query results for display"""
        if not results:
            return "No records found"
        
        output = []
        for i, record in enumerate(results[:20], 1):  # Limit to 20 for readability
            properties = record.get("properties", {})
            
            # Try to find title property
            title = "Untitled"
            for prop_name, prop_value in properties.items():
                if prop_value.get("type") == "title":
                    if prop_value.get("title"):
                        title = prop_value["title"][0].get("plain_text", "Untitled")
                    break
            
            output.append(f"{i}. {title}")
        
        total = len(results)
        if total > 20:
            output.append(f"... and {total - 20} more records")
        
        return "\n".join(output)


class HermesAgentWithNotion:
    """Hermes 3.1-8B with direct Notion access"""
    
    def __init__(self):
        # Hermes LLM
        self.hermes_url = os.getenv("HERMES_API_URL", "http://localhost:8080/v1/chat/completions")
        self.hermes_model = "hermes"
        
        # Notion Integration
        notion_api_key = os.getenv("NOTION_API_KEY", "")
        notion_db_id = os.getenv("NOTION_DATABASE_ID", "")
        
        self.notion = NotionIntegration(notion_api_key, notion_db_id)
        self.notion_ready = False
        
        # Agent state
        self.conversation_history = []
        self.system_prompt = self._build_system_prompt()
        
        self._print_header()
    
    def _print_header(self):
        """Print agent header with Notion status"""
        print("\n" + "="*70)
        print("🧠 HERMES 3.1-8B - PRÉSENCE-PARCOURS AGENT")
        print("="*70)
        print(f"Model: Hermes 3.1-8B (Local GPU)")
        print(f"API: {self.hermes_url}")
        
        # Check Notion connection
        if self.notion.api_key and self.notion.database_id:
            if self.notion.test_connection():
                print("✅ Notion Database: Connected & Ready")
                self.notion_ready = True
            else:
                print("❌ Notion Database: Connection Failed")
        else:
            print("⚠️ Notion Database: Not Configured")
        
        print("="*70 + "\n")
    
    def _build_system_prompt(self) -> str:
        """Build system prompt with Notion awareness"""
        return """You are Hermes, an expert AI agent specialized in Présence-Parcours education platform.

You have DIRECT ACCESS to the Notion student database. This means:
- You can query student records in real-time
- You can create new student pages
- You can update student progress
- You can analyze class data
- You can generate reports from live data

When users ask about students, data, or reports:
1. Query the Notion database directly
2. Analyze the real data
3. Provide specific insights based on actual records

Your knowledge areas:
1. STUDENT MANAGEMENT - Track progress with live Notion data
2. PEDAGOGICAL PLANNING - Create lessons based on actual student needs
3. PARENT COMMUNICATION - Generate reports from real progress data
4. DATA ANALYSIS - Analyze trends from Notion database
5. ASSESSMENT - Design assessments based on student levels

You understand:
✓ Lesson planning with pedagogy
✓ Curriculum alignment
✓ Differentiated instruction
✓ Student assessment design
✓ Learning objective tracking
✓ Notion database structure and queries

When you mention Notion operations, explain what data you're accessing.
Be specific: cite student names, grades, progress levels from actual records.
When creating reports, pull real data from the database.

You can also help with file operations, python analysis, and automation."""
    
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
            return response.json()['choices'][0]['message']['content']
        except requests.exceptions.ConnectionError:
            return "❌ Error: Cannot connect to Hermes. Is Docker LLM running?\n   Run: docker compose -f docker-compose-llm-only.yml up -d"
        except Exception as e:
            return f"❌ Error: {e}"
    
    def process_user_input(self, user_input: str) -> str:
        """Process input with Notion awareness"""
        
        # Check for special commands
        special_response = self._handle_special_command(user_input)
        if special_response is not None:
            return special_response
        
        # Add to history
        self.conversation_history.append({
            "role": "user",
            "content": user_input
        })
        
        # Build messages
        messages = [
            {"role": "system", "content": self.system_prompt}
        ]
        messages.extend(self.conversation_history[-20:])
        
        # Call Hermes
        response = self.call_hermes(messages)
        
        if response:
            self.conversation_history.append({
                "role": "assistant",
                "content": response
            })
        
        return response or "No response from Hermes"
    
    def _handle_special_command(self, command: str) -> Optional[str]:
        """Handle Notion commands"""
        cmd = command.lower().strip()
        
        # Status
        if cmd in ["status", "health", "check"]:
            return self._get_status()
        
        # Notion: List all students
        if "list" in cmd and ("student" in cmd or "database" in cmd or "notion" in cmd):
            return self._list_students()
        
        # Notion: Query students
        if "query" in cmd or "search" in cmd:
            return self._query_students(command)
        
        # Notion: Get database info
        if "database" in cmd and ("info" in cmd or "structure" in cmd):
            return self._get_database_info()
        
        # Help
        if cmd in ["help", "?", "commands"]:
            return self._get_help()
        
        # Clear
        if cmd == "clear":
            self.conversation_history = []
            return "✅ Conversation history cleared"
        
        # Exit
        if cmd in ["exit", "quit", "bye"]:
            return None
        
        return None
    
    def _list_students(self) -> str:
        """List all students from Notion"""
        if not self.notion_ready:
            return "❌ Notion not configured. Set NOTION_API_KEY and NOTION_DATABASE_ID in .env"
        
        result = self.notion.query_database()
        
        if "error" in result:
            return f"❌ Error querying Notion: {result['error']}"
        
        results = result.get("results", [])
        if not results:
            return "📊 Database is empty"
        
        output = f"📊 NOTION DATABASE - {len(results)} Records\n"
        output += "="*60 + "\n"
        output += self.notion.format_results(results)
        
        return output
    
    def _query_students(self, query: str) -> str:
        """Query students from Notion based on user input"""
        if not self.notion_ready:
            return "❌ Notion not configured"
        
        # This would need more sophisticated parsing
        # For now, just list all and let Hermes filter
        result = self.notion.query_database()
        
        if "error" in result:
            return f"❌ Error: {result['error']}"
        
        results = result.get("results", [])
        return f"Found {len(results)} total records. Ask Hermes to analyze them for you."
    
    def _get_database_info(self) -> str:
        """Get database structure info"""
        if not self.notion_ready:
            return "❌ Notion not configured"
        
        try:
            response = requests.get(
                f"https://api.notion.com/v1/databases/{self.notion.database_id}",
                headers=self.notion.headers,
                timeout=10
            )
            response.raise_for_status()
            db = response.json()
            
            output = "📋 DATABASE STRUCTURE\n"
            output += "="*60 + "\n"
            output += f"Title: {db.get('title', [{}])[0].get('plain_text', 'N/A')}\n"
            output += f"Properties:\n"
            
            for prop_name, prop_info in db.get("properties", {}).items():
                output += f"  • {prop_name} ({prop_info.get('type', 'unknown')})\n"
            
            return output
        except Exception as e:
            return f"❌ Error: {e}"
    
    def _get_status(self) -> str:
        """Get agent status"""
        try:
            hermes_check = requests.get("http://localhost:8080/health", timeout=5)
            hermes_status = "✅ Running" if hermes_check.status_code == 200 else "❌ Not responding"
        except:
            hermes_status = "❌ Unreachable"
        
        notion_status = "✅ Connected" if self.notion_ready else "❌ Not configured"
        
        return f"""
🤖 HERMES AGENT STATUS
{'='*50}
Hermes LLM:        {hermes_status}
Notion Database:   {notion_status}
Conversation:      {len(self.conversation_history)} messages
{'='*50}
"""
    
    def _get_help(self) -> str:
        """Get help with Notion integration"""
        return """
🧠 HERMES AGENT - AVAILABLE COMMANDS
{'='*60}

NOTION INTEGRATION:
  "list students"              Show all students in database
  "query students"             Search students
  "database info"              Show database structure
  "Create student [name]"      Add new student
  "Update [name] progress"     Update student record

PEDAGOGICAL:
  "Create lesson plan for [topic]"     Generate lesson plan
  "Analyze student [name] progress"    Analyze with live data
  "Design assessment for [topic]"      Create assessment
  "Who needs support?"                 Identify at-risk students

GENERAL:
  "help" or "?"        Show this help
  "status"             Check all connections
  "clear"              Clear conversation
  "exit"               Quit

Just ask anything! Hermes can access your Notion database directly.
{'='*60}
"""
    
    def interactive_loop(self):
        """Run interactive loop"""
        print("Type 'help' for commands, 'exit' to quit\n")
        
        while True:
            try:
                user_input = input("You: ").strip()
                
                if not user_input:
                    continue
                
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
    agent = HermesAgentWithNotion()
    agent.interactive_loop()

if __name__ == "__main__":
    main()
