import asyncio
import importlib.util
import json
import sys
from pathlib import Path


def validate_manifest(server_type: str):
    manifest_path = Path("deployment/mcpb") / f"manifest.{server_type}.json"
    if not manifest_path.exists():
        print(f"❌ {manifest_path} not found")
        sys.exit(1)

    try:
        with open(manifest_path) as f:
            manifest = json.load(f)
    except json.JSONDecodeError:
        print(f"❌ {manifest_path} is not valid JSON")
        sys.exit(1)

    required_fields = ["manifest_version", "name", "version", "server"]
    for field in required_fields:
        if field not in manifest:
            print(f"❌ Missing required field: {field}")
            sys.exit(1)

    print(f"✅ {manifest_path} structure looks correct")
    return manifest


def validate_server_entry_point(manifest):
    entry_point = manifest.get("server", {}).get("entry_point")
    if not entry_point:
        print("❌ Entry point not defined in manifest")
        sys.exit(1)

    module_name, func_name = entry_point.split(":")
    print(f"ℹ️  Checking entry point: {module_name}:{func_name}")

    try:
        spec = importlib.util.find_spec(module_name)
        if spec is None:
            print(f"❌ Module {module_name} not found")
            sys.exit(1)

        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)

        if not hasattr(module, func_name):
            print(f"❌ Function {func_name} not found in {module_name}")
            sys.exit(1)

        # Access the FastMCP instance
        # In src.main, 'mcp' is the FastMCP instance
        if hasattr(module, "mcp"):
            mcp_instance = module.mcp
            print("✅ Found FastMCP instance")
            return mcp_instance
        else:
            print("⚠️  'mcp' instance not found in module variables (cannot verify tools dynamically)")
            return None

    except Exception as e:
        print(f"❌ Error importing entry point: {e}")
        sys.exit(1)


def validate_tools(manifest, mcp_instance):
    if not mcp_instance:
        print("❌ Could not inspect FastMCP tools: no FastMCP instance found")
        sys.exit(1)

    manifest_tools = {t["name"] for t in manifest.get("tools", [])}
    # Use FastMCP's public async API. The former private _tool_manager registry
    # was removed in FastMCP 3.x.
    try:
        code_tools = {tool.name for tool in asyncio.run(mcp_instance.list_tools(run_middleware=False))}
    except Exception as e:
        print(f"❌ Could not inspect FastMCP tools: {e}")
        sys.exit(1)

    print(f"ℹ️  Manifest tools: {len(manifest_tools)}")
    print(f"ℹ️  Code tools: {len(code_tools)}")

    missing_in_manifest = code_tools - manifest_tools
    missing_in_code = manifest_tools - code_tools

    if missing_in_manifest:
        print(f"⚠️  Tools in code but not in manifest: {missing_in_manifest}")

    if missing_in_code:
        print(f"❌ Tools in manifest but not in code: {missing_in_code}")
        sys.exit(1)

    if not missing_in_code:
        print("✅ All manifest tools are present in the code")


if __name__ == "__main__":
    server_type = "uv"
    if len(sys.argv) > 1:
        server_type = sys.argv[1]

    if server_type not in {"uv", "python"}:
        print("❌ Invalid server type. Use: uv or python")
        sys.exit(1)

    print(f"🚀 Starting Bundle Validation ({server_type})")
    manifest = validate_manifest(server_type)
    mcp_instance = validate_server_entry_point(manifest)
    validate_tools(manifest, mcp_instance)
    print("🎉 Validation Successful")
