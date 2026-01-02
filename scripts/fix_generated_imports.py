import os
from pathlib import Path

ROOT_DIR = Path("src/client/generated")
PACKAGE_NAME = "allure_testops_client"


def fix_imports() -> None:
    for root, _dirs, files in os.walk(ROOT_DIR):
        for file in files:
            if not file.endswith(".py"):
                continue

            file_path = Path(root) / file

            # Calculate relative depth from ROOT_DIR
            rel_path = file_path.relative_to(ROOT_DIR)
            depth = len(rel_path.parts) - 1

            # Determine replacement prefix
            if depth == 0:
                prefix = "."
            else:
                prefix = "." * (depth + 1)

            # Read content
            with open(file_path) as f:
                content = f.read()

            # Replace imports
            # Case 1: "from allure_testops_client." -> "from {prefix}"
            # Example: "from allure_testops_client.api" -> "from .api" (if prefix=".")
            new_content = content.replace(f"from {PACKAGE_NAME}.", f"from {prefix}")

            # Case 2: "from allure_testops_client " -> "from {prefix} "
            # Example: "from allure_testops_client import" -> "from . import"
            new_content = new_content.replace(f"from {PACKAGE_NAME} ", f"from {prefix} ")

            # Case 3: "import allure_testops_client.models"
            if f"import {PACKAGE_NAME}.models" in new_content:
                new_content = new_content.replace(f"import {PACKAGE_NAME}.models", f"from {prefix} import models")

            if new_content != content:
                print(f"Fixing imports in {file_path}")
                with open(file_path, "w") as f:
                    f.write(new_content)


if __name__ == "__main__":
    fix_imports()
