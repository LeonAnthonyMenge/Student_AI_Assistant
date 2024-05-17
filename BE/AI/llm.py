import torch
from llama_index.legacy.llms import Ollama

#Apple Silicon Chip uses: mps
#https://pytorch.org/get-started/locally/
torch.set_default_device('mps')

llm = Ollama(model="llama3:instruct", request_timeout=100.0)

