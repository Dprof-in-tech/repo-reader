"""Hybrid LLM Manager for Local and Cloud Models"""

import os
import logging
from typing import Optional, Dict, Any, List
from langchain_core.messages import HumanMessage, AIMessage
from langchain_openai import ChatOpenAI

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class HybridLLMManager:
    """Manages local and cloud LLMs with intelligent fallback"""
    
    def __init__(self, 
                 local_model_path: Optional[str] = None,
                 openai_api_key: Optional[str] = None,
                 local_model_config: Optional[Dict[str, Any]] = None):
        """
        Initialize hybrid LLM manager
        
        Args:
            local_model_path: Path to local ChatGPT OSS 20B model file (.gguf)
            openai_api_key: OpenAI API key for fallback
            local_model_config: Configuration for local model
        """
        self.local_llm = None
        self.cloud_llm = None
        self.local_available = False
        self.cloud_available = False
        
        # Initialize local model
        if local_model_path and os.path.exists(local_model_path):
            self.local_llm = self._init_local_model(local_model_path, local_model_config or {})
        
        # Initialize cloud model
        api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        if api_key:
            self.cloud_llm = self._init_cloud_model(api_key)
        
        logger.info(f"LLM Manager initialized - Local: {self.local_available}, Cloud: {self.cloud_available}")
    
    def _init_local_model(self, model_path: str, config: Dict[str, Any]):
        """Initialize local GPT OSS 20B model"""
        try:
            # Try transformers pipeline approach first (recommended)
            return self._init_transformers_model(model_path, config)
        except Exception as e:
            logger.error(f"Failed to load transformers model: {e}")
            try:
                # Fallback to LlamaCpp for GGUF files
                return self._init_llamacpp_model(model_path, config)
            except Exception as e2:
                logger.error(f"Failed to load LlamaCpp model: {e2}")
        
        return None
    
    def _init_transformers_model(self, model_path: str, config: Dict[str, Any]):
        """Initialize GPT OSS 20B using transformers pipeline"""
        from transformers import pipeline
        import torch
        
        # Default config for GPT OSS 20B
        default_config = {
            "temperature": 0.7,
            "max_new_tokens": 512,
            "do_sample": True,
            "device_map": "auto" if torch.cuda.is_available() else "cpu",
            "torch_dtype": torch.float16 if torch.cuda.is_available() else torch.float32,
        }
        
        # Merge with user config
        final_config = {**default_config, **config}
        
        # Load the model
        if os.path.exists(model_path):
            # Local model path
            model_name = model_path
        else:
            # HuggingFace model name
            model_name = "openai/gpt-oss-20b"
        
        logger.info(f"Loading GPT OSS 20B from: {model_name}")
        
        # Create pipeline
        pipe = pipeline(
            "text-generation",
            model=model_name,
            device_map=final_config.pop("device_map"),
            torch_dtype=final_config.pop("torch_dtype"),
            trust_remote_code=True
        )
        
        # Wrap in a simple class for consistency
        class TransformersWrapper:
            def __init__(self, pipeline, config):
                self.pipeline = pipeline
                self.config = config
            
            def invoke(self, prompt: str) -> str:
                # Use harmony response format as recommended
                formatted_prompt = f"<|im_start|>user\n{prompt}<|im_end|>\n<|im_start|>assistant\n"
                
                result = self.pipeline(
                    formatted_prompt,
                    max_new_tokens=self.config.get("max_new_tokens", 512),
                    temperature=self.config.get("temperature", 0.7),
                    do_sample=self.config.get("do_sample", True),
                    pad_token_id=self.pipeline.tokenizer.eos_token_id
                )
                
                # Extract generated text (remove the prompt)
                generated = result[0]["generated_text"]
                response = generated[len(formatted_prompt):].strip()
                
                # Remove any end tokens
                if "<|im_end|>" in response:
                    response = response.split("<|im_end|>")[0].strip()
                
                return response
        
        wrapper = TransformersWrapper(pipe, final_config)
        
        # Test the model
        test_response = wrapper.invoke("Hello, can you help with code analysis?")
        if test_response and len(test_response.strip()) > 0:
            self.local_available = True
            logger.info(f"GPT OSS 20B loaded successfully using transformers")
            return wrapper
        
        return None
    
    def _init_llamacpp_model(self, model_path: str, config: Dict[str, Any]):
        """Fallback: Initialize using LlamaCpp for GGUF files"""
        from langchain_community.llms import LlamaCpp
        
        if not model_path.endswith('.gguf'):
            return None
        
        # Default configuration for GGUF models
        default_config = {
            "temperature": 0.7,
            "max_tokens": 2048,
            "n_ctx": 4096,
            "n_batch": 512,
            "n_gpu_layers": -1,
            "verbose": False,
            "n_threads": os.cpu_count(),
        }
        
        # Merge user config with defaults
        final_config = {**default_config, **config}
        
        llm = LlamaCpp(
            model_path=model_path,
            **final_config
        )
        
        # Test the model
        test_response = llm.invoke("Hello")
        if test_response:
            self.local_available = True
            logger.info(f"GGUF model loaded successfully: {model_path}")
            return llm
            
        return None
    
    def _init_cloud_model(self, api_key: str):
        """Initialize OpenAI cloud model"""
        try:
            llm = ChatOpenAI(
                model="gpt-5-nano",
                temperature=0.7,
                api_key=api_key
            )
            
            # Test the model
            test_response = llm.invoke([HumanMessage(content="Hello")])
            if test_response:
                self.cloud_available = True
                logger.info("Cloud model (GPT-5-nano) initialized successfully")
                return llm
                
        except Exception as e:
            logger.error(f"Failed to initialize cloud model: {e}")
            
        return None
    
    def invoke(self, messages: List, prefer_local: bool = True) -> Optional[Any]:
        """
        Invoke LLM with intelligent fallback
        
        Args:
            messages: List of messages (LangChain format)
            prefer_local: Whether to prefer local model first
            
        Returns:
            LLM response or None if both fail
        """
        # Determine order based on preference
        models_to_try = []
        
        if prefer_local:
            if self.local_available:
                models_to_try.append(("local", self.local_llm))
            if self.cloud_available:
                models_to_try.append(("cloud", self.cloud_llm))
        else:
            if self.cloud_available:
                models_to_try.append(("cloud", self.cloud_llm))
            if self.local_available:
                models_to_try.append(("local", self.local_llm))
        
        # Try each model in order
        for model_type, llm in models_to_try:
            try:
                logger.info(f"Attempting {model_type} model")
                
                if model_type == "local":
                    # Local model expects string input
                    if isinstance(messages, list) and messages:
                        # Extract content from HumanMessage objects
                        prompt = ""
                        for msg in messages:
                            if hasattr(msg, 'content'):
                                prompt += msg.content + "\n"
                            else:
                                prompt += str(msg) + "\n"
                        response = llm.invoke(prompt.strip())
                        
                        # Wrap in AIMessage-like object for consistency
                        class LocalResponse:
                            def __init__(self, content):
                                self.content = content
                                
                        return LocalResponse(response)
                else:
                    # Cloud model expects LangChain messages
                    response = llm.invoke(messages)
                    return response
                    
            except Exception as e:
                logger.warning(f"{model_type} model failed: {e}")
                continue
        
        logger.error("All LLM models failed")
        return None
    
    def get_status(self) -> Dict[str, Any]:
        """Get current status of all models"""
        return {
            "local_model": {
                "available": self.local_available,
                "type": "ChatGPT OSS 20B" if self.local_available else None
            },
            "cloud_model": {
                "available": self.cloud_available,
                "type": "GPT-5-nano" if self.cloud_available else None
            },
            "has_fallback": self.local_available and self.cloud_available
        }
    
    @classmethod
    def create_default(cls) -> 'HybridLLMManager':
        """Create manager with default configuration"""
        # Common paths where users might store the model
        default_paths = [
            "./models/chatgpt-oss-20b.gguf",
            "~/models/chatgpt-oss-20b.gguf",
            "/opt/models/chatgpt-oss-20b.gguf",
            os.getenv("CHATGPT_OSS_MODEL_PATH", "")
        ]
        
        local_model_path = None
        for path in default_paths:
            expanded_path = os.path.expanduser(path)
            if os.path.exists(expanded_path):
                local_model_path = expanded_path
                break
        
        return cls(
            local_model_path=local_model_path,
            openai_api_key=os.getenv("OPENAI_API_KEY")
        )