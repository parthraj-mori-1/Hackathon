from ddgs.exceptions import DDGSException, RatelimitException
from ddgs import DDGS
from strands import tool
import json

class WebSearchTool:
    """Simple DuckDuckGo web search tool."""

    def __init__(self, client, memory_id, app_context):
        self.client = client
        self.memory_id = memory_id
        self.session_id = app_context.session_id
        self.actor_id = app_context.actor_id

    @tool
    def websearch(self, keywords: str, region: str = "us-en", max_results: int = 5) -> str:
        """Search the web for updated information.
        
        Args:
            keywords: The search query keywords
            region: The search region (us-en, uk-en, etc.)
            max_results: Maximum number of results to return
            
        Returns:
            JSON string with search results
        """
        try:
            results = DDGS().text(keywords, region=region, max_results=max_results)
            
            if not results:
                return json.dumps({"error": "No results found"})
            self.client.create_event(
                    memory_id=self.memory_id,
                    actor_id=self.actor_id,
                    session_id=self.session_id,
                    messages=[(results, "ASSISTANT")]
                )
            return{
                "status": "success",
                "response": result,
                "message": "response generated successfully using specialized agent"
            }
            
        except RatelimitException:
            return {"error": "Rate limit reached"}
        except Exception as e:
            return {"error": f"Search failed: {str(e)}"}