from typing import Dict, Any, List


def validate_config(config_data: Dict[str, Any]) -> List[str]:
    errors = []

    required_sections = ['sources', 'rag', 'agent', 'llm', 'embedding', 'storage']
    for section in required_sections:
        if section not in config_data:
            errors.append(f"Missing required config section: {section}")

    if 'rag' in config_data:
        rag_config = config_data['rag']
        if 'chunk_size' in rag_config and rag_config['chunk_size'] <= 0:
            errors.append("rag.chunk_size must be positive")
        if 'top_k' in rag_config and rag_config['top_k'] <= 0:
            errors.append("rag.top_k must be positive")

    return errors
