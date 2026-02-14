import json

# Configuration
INPUT_FILE = "openapi/allure-testops-service/report-service.json"
OUTPUT_FILE = "openapi/allure-testops-service/filtered-report-service.json"

# Tags to keep (MVP + Essential Supporting Controllers)
KEEP_TAGS = {
    # Core Entities
    "test-case-controller",
    "shared-step-controller",
    "project-controller",
    "launch-controller",
    # Test Case Details
    "test-case-attachment-controller",
    "test-case-scenario-controller",
    "test-case-tag-controller",
    "test-case-overview-controller",
    "test-case-custom-field-controller",
    # Shared Step Details
    "shared-step-attachment-controller",
    "shared-step-scenario-controller",
    # Search & Bulk
    "test-case-search-controller",
    "launch-search-controller",
    "test-case-bulk-controller",
    # Project & Custom Field Management
    "custom-field-controller",
    "custom-field-project-controller",
    "custom-field-project-controller-v-2",
    "custom-field-schema-controller",
    "custom-field-value-controller",
    "custom-field-value-project-controller",
    "status-controller",
    # Test Layer Management
    "test-layer-controller",
    "test-layer-schema-controller",
    "integration-controller",
    # Test Plan Management
    "test-plan-controller",
    "test-case-test-plan-bulk-controller",
    # Defect Management
    "defect-controller",
    "defect-matcher-controller",
}


def filter_spec() -> None:
    print(f"Reading spec from {INPUT_FILE}...")
    with open(INPUT_FILE) as f:
        spec = json.load(f)

    original_paths_count = len(spec.get("paths", {}))
    print(f"Original paths: {original_paths_count}")

    # Filter paths
    filtered_paths = {}
    for path, methods in spec.get("paths", {}).items():
        new_methods = {}
        for method, operation in methods.items():
            if method == "parameters":  # Keep path-level parameters if any
                new_methods[method] = operation
                continue

            tags = operation.get("tags", [])
            # Check if any of the operation's tags are in our keep list
            if any(tag in KEEP_TAGS for tag in tags):
                new_methods[method] = operation

        if new_methods:
            filtered_paths[path] = new_methods

    spec["paths"] = filtered_paths

    # We are NOT filtering components/schemas aggressively because it's hard to trace
    # all dependencies (refs) without a full graph traversal.
    # openapi-python-client might be smart enough to only generate models that are used,
    # or we can accept the extra models as "future proofing" without the bloat of 100+ extra controllers.

    print(f"Filtered paths: {len(filtered_paths)}")
    print(f"Writing filtered spec to {OUTPUT_FILE}...")

    with open(OUTPUT_FILE, "w") as f:
        json.dump(spec, f, indent=2)


if __name__ == "__main__":
    filter_spec()
