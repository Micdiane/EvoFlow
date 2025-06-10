"""
文本生成Agent
"""
import httpx
from typing import Dict, Any
from decimal import Decimal

from .base import BaseAgent, AgentResult, AgentError
from ..config import settings


class TextWritingAgent(BaseAgent):
    """文本生成Agent"""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(
            name="TextWritingAgent",
            agent_type="text",
            capabilities=["text_generation", "creative_writing", "summarization"],
            config=config
        )
        self.max_tokens = self.config.get("max_tokens", 2000)
        self.temperature = self.config.get("temperature", 0.7)
        self.model = self.config.get("model", "deepseek-chat")
    
    async def execute(self, input_data: Dict[str, Any], context: Dict[str, Any]) -> AgentResult:
        """执行文本生成"""
        prompt = input_data.get("prompt", "")
        task_type = input_data.get("task_type", "general")  # general, summary, creative, etc.
        max_tokens = input_data.get("max_tokens", self.max_tokens)
        temperature = input_data.get("temperature", self.temperature)
        
        try:
            # 根据任务类型调整提示词
            system_prompt = self._get_system_prompt(task_type)
            
            # 调用DeepSeek API
            generated_text = await self._call_deepseek_api(
                system_prompt=system_prompt,
                user_prompt=prompt,
                max_tokens=max_tokens,
                temperature=temperature
            )
            
            return AgentResult(
                success=True,
                data={
                    "prompt": prompt,
                    "generated_text": generated_text,
                    "task_type": task_type,
                    "token_count": len(generated_text.split())  # 简化的token计数
                },
                metadata={
                    "model": self.model,
                    "max_tokens": max_tokens,
                    "temperature": temperature
                }
            )
            
        except Exception as e:
            raise AgentError(f"Text generation failed: {str(e)}")
    
    def _get_system_prompt(self, task_type: str) -> str:
        """根据任务类型获取系统提示词"""
        prompts = {
            "general": "你是一个专业的文本生成助手，请根据用户的要求生成高质量的文本内容。",
            "summary": "你是一个专业的文本摘要助手，请为用户提供准确、简洁的内容摘要。",
            "creative": "你是一个富有创意的写作助手，请发挥想象力创作有趣、引人入胜的内容。",
            "business": "你是一个商务写作专家，请生成专业、正式的商务文档内容。",
            "technical": "你是一个技术写作专家，请生成准确、清晰的技术文档内容。"
        }
        return prompts.get(task_type, prompts["general"])
    
    async def _call_deepseek_api(
        self, 
        system_prompt: str, 
        user_prompt: str, 
        max_tokens: int, 
        temperature: float
    ) -> str:
        """调用DeepSeek API"""
        headers = {
            "Authorization": f"Bearer {settings.deepseek_api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "max_tokens": max_tokens,
            "temperature": temperature,
            "stream": False
        }
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            try:
                response = await client.post(
                    f"{settings.deepseek_base_url}/v1/chat/completions",
                    headers=headers,
                    json=payload
                )
                response.raise_for_status()
                
                result = response.json()
                if "choices" in result and len(result["choices"]) > 0:
                    return result["choices"][0]["message"]["content"]
                else:
                    raise AgentError("No response from DeepSeek API")
                    
            except httpx.TimeoutException:
                raise AgentError("DeepSeek API request timed out")
            except httpx.HTTPStatusError as e:
                raise AgentError(f"DeepSeek API error: {e.response.status_code}")
            except Exception as e:
                raise AgentError(f"DeepSeek API call failed: {str(e)}")
    
    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """验证输入数据"""
        if not isinstance(input_data, dict):
            return False
        
        prompt = input_data.get("prompt")
        if not prompt or not isinstance(prompt, str) or len(prompt.strip()) == 0:
            return False
        
        max_tokens = input_data.get("max_tokens", self.max_tokens)
        if not isinstance(max_tokens, int) or max_tokens <= 0 or max_tokens > 4000:
            return False
        
        temperature = input_data.get("temperature", self.temperature)
        if not isinstance(temperature, (int, float)) or temperature < 0 or temperature > 2:
            return False
        
        return True
    
    def get_cost_estimate(self, input_data: Dict[str, Any]) -> Decimal:
        """获取成本估算"""
        # DeepSeek API按token计费
        max_tokens = input_data.get("max_tokens", self.max_tokens)
        prompt_tokens = len(input_data.get("prompt", "").split()) * 1.3  # 估算token数
        
        # DeepSeek价格（示例）：输入$0.14/1M tokens，输出$0.28/1M tokens
        input_cost = Decimal(str(prompt_tokens)) * Decimal("0.00000014")
        output_cost = Decimal(str(max_tokens)) * Decimal("0.00000028")
        
        return input_cost + output_cost
