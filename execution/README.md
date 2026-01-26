# Execution Scripts

This directory contains deterministic Python scripts that perform actual work.

## Purpose

Scripts here should be:

- **Deterministic**: Same input → same output
- **Reliable**: Handle errors gracefully
- **Testable**: Can be tested independently
- **Fast**: Optimized for performance
- **Well-commented**: Clear documentation

## Structure

Each script should:

1. Accept clear inputs (CLI args, files, env vars)
2. Perform one specific task
3. Return clear outputs (files, stdout, exit codes)
4. Log errors appropriately
5. Include docstrings and comments

## Example Template

```python
#!/usr/bin/env python3
"""
Script Name: example_script.py
Purpose: Brief description of what this does
Author: Auto-generated
"""

import argparse
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main(input_file: Path, output_file: Path) -> None:
    """
    Main function description.

    Args:
        input_file: Path to input file
        output_file: Path to output file
    """
    try:
        # Your logic here
        logger.info("Processing started")
        # ...
        logger.info("Processing completed")
    except Exception as e:
        logger.error(f"Error: {e}")
        raise


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Script description")
    parser.add_argument("input", type=Path, help="Input file path")
    parser.add_argument("output", type=Path, help="Output file path")
    args = parser.parse_args()

    main(args.input, args.output)
```

## Dependencies

Add required packages to `requirements.txt` in this directory.

## Environment Variables

Access via `os.getenv()` from the `.env` file in the project root.
