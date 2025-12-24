import os
import json
import asyncio
import google.generativeai as genai
from typing import Any, Optional, Type
from google.adk.agents.context import google_api_key_var

class Agent:
    def __init__(self, name: str, model: str, description: str, instruction: str, 
                 tools: list = None, sub_agents: list = None, output_type: Optional[Type] = None, **kwargs):
        self.name = name
        self.model = model # e.g. "gemini-1.5-flash"
        self.description = description
        self.instruction = instruction
        self.tools = tools or []
        self.sub_agents = sub_agents or []
        self.output_type = output_type
        
        # Configure Gemini
        api_key = os.getenv("GOOGLE_API_KEY")
        if api_key:
            genai.configure(api_key=api_key)
        
    async def run(self, input_text: str, instruction: Optional[str] = None, google_api_key: Optional[str] = None) -> Any:
        """
        Executes the agent logic using Gemini.
        If output_type is set, it uses structured output.
        """
        # Use provided key, then context variable, then fallback to environment
        api_key = google_api_key or google_api_key_var.get() or os.getenv("GOOGLE_API_KEY")
        
        if not api_key:
            return f"[SIMULATED RESPONSE FROM {self.name}]\nI need a GOOGLE_API_KEY to actually call Gemini. Input: {input_text}"

        # Re-configure for this specific request if a new key is provided
        genai.configure(api_key=api_key)

        combined_instruction = f"{self.instruction}\n\nAdditional Instruction: {instruction}" if instruction else self.instruction
        
        model_kwargs = {}
        if self.output_type:
            model_kwargs["generation_config"] = {
                "response_mime_type": "application/json",
                "response_schema": self.output_type
            }

        model = genai.GenerativeModel(
            model_name=self.model,
            system_instruction=combined_instruction,
            **model_kwargs
        )

        try:
            # Use asyncio.to_thread for synchronous SDK call
            response = await asyncio.to_thread(model.generate_content, input_text)
            
            if self.output_type:
                try:
                    return json.loads(response.text)
                except json.JSONDecodeError:
                    return response.text
            return response.text
            
        except Exception as e:
            return f"Error calling Gemini in {self.name}: {str(e)}"
