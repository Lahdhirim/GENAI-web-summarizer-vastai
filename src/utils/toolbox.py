from pathlib import Path

def load_prompt(prompt_path: str, **kwargs) -> str:
    """
    Load a prompt from a file.
    
    Args:
        prompt_path (str): Path to the prompt file.
        
    Returns:
        str: The content of the prompt file.
    """
    if not Path(prompt_path).exists():
        raise FileNotFoundError(f"Prompt file {prompt_path} does not exist.")
    
    prompt_path = Path(prompt_path)
    prompt_template = prompt_path.read_text(encoding="utf-8")
    return prompt_template.format(**kwargs)