"""
CanvasXpress Configuration Generator

Generates CanvasXpress JSON configurations from natural language descriptions
using RAG (Retrieval Augmented Generation) with few-shot examples.

Supports multiple LLM and embedding providers:
- LLM: Azure OpenAI (BMS Proxy) or Google Gemini
- Embeddings: Local BGE-M3, Azure OpenAI, or Google Gemini

Based on the JOSS-published methodology (Smith & Neuhaus, 2025):
- 93% exact match accuracy
- 98% similarity score
- BGE-M3 embeddings for semantic search
- 25 most relevant examples per query
"""

import json
import os
import random
import requests
from pathlib import Path
from typing import Dict, List, Optional

from pymilvus import MilvusClient

# Conditional imports for providers
LLM_PROVIDER = os.environ.get("LLM_PROVIDER", "openai").lower()
EMBEDDING_PROVIDER = os.environ.get("EMBEDDING_PROVIDER", "local").lower()

# Import based on LLM provider (also needed for OpenAI embeddings)
if LLM_PROVIDER == "openai" or EMBEDDING_PROVIDER == "openai":
    from openai import AzureOpenAI
    import openai

if LLM_PROVIDER == "gemini" or EMBEDDING_PROVIDER == "gemini":
    import google.generativeai as genai

# Import based on embedding provider
if EMBEDDING_PROVIDER == "local":
    from FlagEmbedding import BGEM3FlagModel


class EmbeddingProvider:
    """Abstract embedding provider supporting multiple backends."""
    
    def __init__(self, provider: str = "local"):
        self.provider = provider
        self.dimension = None
        
        if provider == "local":
            print("🔧 Initializing BGE-M3 embedding model (local)...")
            self.model = BGEM3FlagModel('BAAI/bge-m3', use_fp16=False)
            self.dimension = 1024
        elif provider == "openai":
            print("🔧 Initializing Azure OpenAI embeddings (API)...")
            self.api_key = os.environ.get("AZURE_OPENAI_KEY")
            if not self.api_key:
                raise ValueError("AZURE_OPENAI_KEY environment variable not set")
            self.api_version = os.environ.get("AZURE_OPENAI_API_VERSION", "2024-02-01")
            self.model_name = os.environ.get("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
            self.llm_environment = os.environ.get("LLM_ENVIRONMENT", "nonprod")
            # Fetch BMS endpoints for embeddings
            self.bms_openai_urls = self._fetch_bms_endpoints()
            self.dimension = 1536  # text-embedding-3-small dimension
        elif provider == "gemini":
            print("🔧 Initializing Gemini embeddings (API)...")
            api_key = os.environ.get("GOOGLE_API_KEY")
            if not api_key:
                raise ValueError("GOOGLE_API_KEY environment variable not set")
            genai.configure(api_key=api_key)
            self.model_name = os.environ.get("GEMINI_EMBEDDING_MODEL", "text-embedding-004")
            self.dimension = 768  # Gemini text-embedding-004 dimension
        else:
            raise ValueError(f"Unknown embedding provider: {provider}. Use 'local', 'openai', or 'gemini'.")
    
    def _fetch_bms_endpoints(self) -> dict:
        """Fetch BMS OpenAI endpoint configuration."""
        try:
            response = requests.get(
                'https://bms-openai-proxy-eus-prod.azu.bms.com/openai-urls.json',
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Failed to fetch BMS OpenAI endpoints: {e}")
    
    def _get_openai_endpoint(self) -> str:
        """Get a random Azure OpenAI endpoint for embeddings."""
        try:
            # Look for embedding model endpoints
            endpoints = self.bms_openai_urls.get(self.llm_environment, {}).get(self.model_name, [])
            if not endpoints:
                # Fall back to any available endpoint
                for model_name, model_endpoints in self.bms_openai_urls.get(self.llm_environment, {}).items():
                    if 'embedding' in model_name.lower():
                        endpoints = model_endpoints
                        self.model_name = model_name
                        break
            
            if not endpoints:
                raise ValueError(f"No embedding endpoints found for {self.llm_environment}")
            
            return random.choice(endpoints)['endpoint']
        except KeyError as e:
            raise ValueError(f"No deployments found: {e}")
    
    def encode(self, texts: List[str]) -> List[List[float]]:
        """Encode texts to embeddings."""
        if self.provider == "local":
            result = self.model.encode(texts)['dense_vecs']
            return [v.tolist() if hasattr(v, 'tolist') else v for v in result]
        elif self.provider == "openai":
            endpoint = self._get_openai_endpoint()
            client = AzureOpenAI(
                api_version=self.api_version,
                api_key=self.api_key,
                azure_endpoint=endpoint
            )
            # Batch embed (OpenAI supports up to 2048 texts)
            response = client.embeddings.create(
                model=self.model_name,
                input=texts
            )
            return [item.embedding for item in response.data]
        elif self.provider == "gemini":
            embeddings = []
            for text in texts:
                result = genai.embed_content(
                    model=f"models/{self.model_name}",
                    content=text,
                    task_type="retrieval_document"
                )
                embeddings.append(result['embedding'])
            return embeddings
    
    def encode_query(self, text: str) -> List[float]:
        """Encode a single query text."""
        if self.provider == "local":
            result = self.model.encode([text])['dense_vecs'][0]
            return result.tolist() if hasattr(result, 'tolist') else result
        elif self.provider == "openai":
            endpoint = self._get_openai_endpoint()
            client = AzureOpenAI(
                api_version=self.api_version,
                api_key=self.api_key,
                azure_endpoint=endpoint
            )
            response = client.embeddings.create(
                model=self.model_name,
                input=[text]
            )
            return response.data[0].embedding
        elif self.provider == "gemini":
            result = genai.embed_content(
                model=f"models/{self.model_name}",
                content=text,
                task_type="retrieval_query"
            )
            return result['embedding']


class LLMProvider:
    """Abstract LLM provider supporting multiple backends."""
    
    def __init__(self, provider: str = "openai", **kwargs):
        self.provider = provider
        
        if provider == "openai":
            self._init_openai(**kwargs)
        elif provider == "gemini":
            self._init_gemini(**kwargs)
        else:
            raise ValueError(f"Unknown LLM provider: {provider}")
    
    def _init_openai(self, llm_model: str = None, llm_environment: str = "nonprod", **kwargs):
        """Initialize Azure OpenAI (BMS Proxy)."""
        print(f"🔧 Initializing Azure OpenAI (BMS Proxy)...")
        self.llm_model = llm_model or os.environ.get("LLM_MODEL", "gpt-4o-mini-global")
        self.llm_environment = llm_environment
        self.model_version = self._get_model_version()
        self.api_version = os.environ.get("AZURE_OPENAI_API_VERSION", "2024-02-01")
        self.api_key = os.environ.get("AZURE_OPENAI_KEY")
        
        if not self.api_key:
            raise ValueError("AZURE_OPENAI_KEY environment variable not set")
        
        # Download BMS OpenAI endpoints
        print("🔧 Fetching BMS OpenAI endpoints...")
        self.bms_openai_urls = self._fetch_bms_endpoints()
    
    def _init_gemini(self, **kwargs):
        """Initialize Google Gemini."""
        print(f"🔧 Initializing Google Gemini...")
        api_key = os.environ.get("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY environment variable not set")
        
        genai.configure(api_key=api_key)
        self.llm_model = os.environ.get("GEMINI_MODEL", "gemini-2.0-flash-exp")
        self.model = genai.GenerativeModel(self.llm_model)
    
    def _get_model_version(self) -> str:
        """Get model version based on model name (OpenAI only)."""
        versions = {
            "gpt-4o-mini-global": "2024-07-18",
            "gpt-4o-global": "2024-05-13",
            "gpt-4-turbo-global": "turbo-2024-04-09"
        }
        return versions.get(self.llm_model, "2024-07-18")
    
    def _fetch_bms_endpoints(self) -> dict:
        """Fetch BMS OpenAI endpoint configuration."""
        try:
            response = requests.get(
                'https://bms-openai-proxy-eus-prod.azu.bms.com/openai-urls.json',
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Failed to fetch BMS OpenAI endpoints: {e}")
    
    def _get_endpoint(self) -> str:
        """Get a random Azure OpenAI endpoint from BMS proxy."""
        try:
            endpoints = [
                e for e in self.bms_openai_urls[self.llm_environment][self.llm_model]
                if self.model_version in e['model_version']
            ]
            
            if not endpoints:
                raise ValueError(
                    f"No endpoints found for: {self.llm_environment}, "
                    f"{self.llm_model}, {self.model_version}"
                )
            
            return random.choice(endpoints)['endpoint']
            
        except KeyError as e:
            raise ValueError(f"No deployments found for model: {e}")
    
    def generate(self, prompt: str, temperature: float = 0.0, max_retries: int = 3) -> str:
        """Generate text from prompt."""
        if self.provider == "openai":
            return self._generate_openai(prompt, temperature, max_retries)
        elif self.provider == "gemini":
            return self._generate_gemini(prompt, temperature, max_retries)
    
    def _generate_openai(self, prompt: str, temperature: float, max_retries: int) -> str:
        """Generate using Azure OpenAI."""
        messages = [{"role": "user", "content": prompt}]
        last_error = None
        
        for attempt in range(max_retries):
            try:
                endpoint = self._get_endpoint()
                client = AzureOpenAI(
                    api_version=self.api_version,
                    api_key=self.api_key,
                    azure_endpoint=endpoint
                )
                
                response = client.chat.completions.create(
                    model=self.llm_model,
                    max_tokens=4096,
                    temperature=temperature,
                    messages=messages
                )
                
                return response.choices[0].message.content
                
            except openai.APIConnectionError as e:
                last_error = f"Server unreachable: {e.__cause__}"
                print(f"⚠️  Attempt {attempt + 1}/{max_retries}: {last_error}")
            except openai.RateLimitError as e:
                last_error = f"Rate limit (HTTP 429): {e}"
                print(f"⚠️  Attempt {attempt + 1}/{max_retries}: {last_error}")
            except openai.APIStatusError as e:
                last_error = f"API error: {e}"
                print(f"⚠️  Attempt {attempt + 1}/{max_retries}: {last_error}")
        
        raise RuntimeError(f"Azure OpenAI call failed after {max_retries} attempts. Last error: {last_error}")
    
    def _generate_gemini(self, prompt: str, temperature: float, max_retries: int) -> str:
        """Generate using Google Gemini."""
        last_error = None
        
        generation_config = genai.GenerationConfig(
            temperature=temperature,
            max_output_tokens=4096
        )
        
        for attempt in range(max_retries):
            try:
                response = self.model.generate_content(
                    prompt,
                    generation_config=generation_config
                )
                return response.text
                
            except Exception as e:
                last_error = str(e)
                print(f"⚠️  Attempt {attempt + 1}/{max_retries}: {last_error}")
        
        raise RuntimeError(f"Gemini call failed after {max_retries} attempts. Last error: {last_error}")


class CanvasXpressGenerator:
    """Generate CanvasXpress configurations from English descriptions."""
    
    def __init__(
        self,
        data_dir: str = "/app/data",
        vector_db_path: str = "/root/.cache/canvasxpress_mcp.db",
        llm_model: Optional[str] = None,
        llm_environment: str = "nonprod"
    ):
        """
        Initialize the generator.
        
        Args:
            data_dir: Directory containing few-shot examples and schema
            vector_db_path: Path to store the Milvus vector database
            llm_model: Model name (for OpenAI: 'gpt-4o-mini-global', for Gemini: 'gemini-2.0-flash-exp')
            llm_environment: BMS environment ('nonprod' or 'prod') - only used for OpenAI
        """
        self.data_dir = Path(data_dir)
        self.vector_db_path = vector_db_path
        
        # Determine providers from environment
        self.llm_provider_name = os.environ.get("LLM_PROVIDER", "openai").lower()
        self.embedding_provider_name = os.environ.get("EMBEDDING_PROVIDER", "local").lower()
        
        # Load data files
        print("🔧 Loading few-shot examples...")
        self.examples = self._load_examples()
        
        print("🔧 Loading schema...")
        self.schema = self._load_schema()
        
        print("🔧 Loading prompt template...")
        self.prompt_template = self._load_prompt_template()
        
        # Initialize embedding provider
        self.embedding_provider = EmbeddingProvider(self.embedding_provider_name)
        
        # Initialize vector database
        print("🔧 Initializing vector database...")
        self.vector_db = MilvusClient(self.vector_db_path)
        self._setup_vector_db()
        
        # Initialize LLM provider
        self.llm_provider = LLMProvider(
            provider=self.llm_provider_name,
            llm_model=llm_model,
            llm_environment=llm_environment
        )
        
        print(f"📦 LLM Provider: {self.llm_provider_name} ({self.llm_provider.llm_model})")
        print(f"� Embedding Provider: {self.embedding_provider_name}")
        print("✅ CanvasXpress Generator initialized successfully!")
    
    def _load_examples(self) -> List[Dict]:
        """Load few-shot examples from JSON file."""
        examples_file = self.data_dir / "few_shot_examples.json"
        with open(examples_file) as f:
            return json.load(f)
    
    def _load_schema(self) -> str:
        """Load CanvasXpress schema documentation."""
        schema_file = self.data_dir / "schema.txt"
        with open(schema_file) as f:
            return f.read()
    
    def _load_prompt_template(self) -> str:
        """Load prompt template."""
        template_file = self.data_dir / "prompt_template.md"
        with open(template_file) as f:
            return f.read()
    
    def _setup_vector_db(self):
        """Set up vector database with few-shot examples."""
        collection_name = "few_shot_examples"
        
        # Check if collection exists
        if self.vector_db.has_collection(collection_name):
            print(f"   ✓ Vector database collection '{collection_name}' already exists")
            return
        
        print(f"   📊 Creating vector database collection...")
        
        # Create collection with appropriate dimension for the embedding provider
        self.vector_db.create_collection(
            collection_name=collection_name,
            dimension=self.embedding_provider.dimension
        )
        
        # Embed and insert examples
        print(f"   🔢 Embedding {len(self.examples)} examples...")
        data = []
        
        # Batch embed all descriptions
        descriptions = [ex['description'] for ex in self.examples]
        embeddings = self.embedding_provider.encode(descriptions)
        
        for example, embedding in zip(self.examples, embeddings):
            data.append({
                "id": example["id"],
                "vector": embedding,
                "description": example["description"],
                "config": json.dumps(example["config"]),
                "headers": example["headers"],
                "type": example["type"]
            })
        
        # Insert in batches
        self.vector_db.insert(collection_name=collection_name, data=data)
        print(f"   ✓ Inserted {len(data)} examples into vector database")
    
    def get_similar_examples(
        self,
        description: str,
        num_examples: int = 25
    ) -> List[Dict]:
        """
        Retrieve similar few-shot examples using semantic search.
        
        Args:
            description: Natural language description of desired visualization
            num_examples: Number of similar examples to retrieve
            
        Returns:
            List of similar example dictionaries
        """
        # Embed the query using the configured embedding provider
        query_vector = self.embedding_provider.encode_query(description)
        
        # Search vector database
        results = self.vector_db.search(
            collection_name="few_shot_examples",
            data=[query_vector],
            limit=num_examples,
            output_fields=["description", "config", "headers", "type"]
        )
        
        # Format results
        similar_examples = []
        for hits in results:
            for hit in hits:
                entity = hit["entity"]
                similar_examples.append({
                    "description": entity["description"],
                    "config": json.loads(entity["config"]),
                    "headers": entity["headers"],
                    "type": entity["type"],
                    "score": hit.get("distance", 0)
                })
        
        return similar_examples
    
    def build_prompt(
        self,
        description: str,
        headers: Optional[str] = None,
        similar_examples: Optional[List[Dict]] = None
    ) -> str:
        """
        Build the complete prompt for the LLM.
        
        Args:
            description: Natural language description
            headers: Column headers/names (optional)
            similar_examples: Pre-fetched similar examples (optional)
            
        Returns:
            Complete prompt string
        """
        # Get similar examples if not provided
        if similar_examples is None:
            similar_examples = self.get_similar_examples(description, num_examples=25)
        
        # Format few-shot examples
        few_shot_text = ""
        for i, ex in enumerate(similar_examples, 1):
            config_json = json.dumps(ex["config"], indent=2)
            few_shot_text += f"English Text: {ex['description']}; "
            few_shot_text += f"Headers/Column Names: {ex['headers']}, "
            few_shot_text += f"Answer: {config_json}\n"
        
        # Use headers if provided, otherwise empty
        headers_text = headers or ""
        
        # Build complete prompt using template
        prompt = self.prompt_template.format(
            canvasxpress_config_english=description,
            headers_column_names=headers_text,
            schema_info=self.schema,
            few_shot_examples=few_shot_text
        )
        
        return prompt
    
    def generate(
        self,
        description: str,
        headers: Optional[str] = None,
        temperature: float = 0.0,
        max_retries: int = 3
    ) -> Dict:
        """
        Generate CanvasXpress configuration from description.
        
        Args:
            description: Natural language description of visualization
            headers: Optional column headers/names
            temperature: LLM temperature (0.0 = deterministic)
            max_retries: Maximum number of endpoint retry attempts
            
        Returns:
            CanvasXpress configuration as dictionary
            
        Raises:
            json.JSONDecodeError: If LLM returns invalid JSON
            Exception: If all LLM call attempts fail
        """
        # Build prompt with RAG
        prompt = self.build_prompt(description, headers)
        
        # Generate using the configured LLM provider
        generated_text = self.llm_provider.generate(
            prompt=prompt,
            temperature=temperature,
            max_retries=max_retries
        )
        
        # Parse JSON response
        generated_text = generated_text.strip()
        if generated_text.startswith("```"):
            # Remove markdown code blocks
            lines = generated_text.split("\n")
            generated_text = "\n".join(lines[1:-1] if len(lines) > 2 else lines)
            generated_text = generated_text.replace("```json", "").replace("```", "").strip()
        
        config = json.loads(generated_text)
        return config
