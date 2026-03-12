#!/usr/bin/env python3
"""
Generate shell completion scripts for lucius CLI.

This script generates completion definitions for bash, zsh, fish, and PowerShell.
"""

import json
from pathlib import Path

# Path to static tool schemas
TOOL_SCHEMAS_PATH = Path(__file__).parent.parent.parent / "src" / "cli" / "data" / "tool_schemas.json"


def load_tool_names() -> list[str]:
    """Load tool names from static schemas."""
    if not TOOL_SCHEMAS_PATH.exists():
        raise FileNotFoundError(
            f"Tool schemas not found at {TOOL_SCHEMAS_PATH}. Run scripts/build_tool_schema.py first."
        )

    with TOOL_SCHEMAS_PATH.open() as f:
        schemas = json.load(f)

    return sorted(schemas.keys())


def generate_bash_completion(tool_names: list[str]) -> str:
    """Generate bash completion script."""
    tools_str = " ".join(tool_names)
    return f"""# lucius CLI bash completion
complete -W "list call version --help --version" lucius

# Tool name completion for 'call' command
_lucius_call_completion() {{
    local cur prev words cword
    _init_completion || return

    if [[ $cword -eq 1 ]]; then
        COMPREPLY=($(compgen -W "{tools_str}" -- "$cur"))
    elif [[ $cword -ge 2 ]]; then
        case ${{words[1]}} in
            call)
                if [[ ${{words[2]}} == "${{words[2]}}" ]]; then
                    case $prev in
                        --format|-f)
                            COMPREPLY=($(compgen -W "json table plain" -- "$cur"))
                            ;;
                        --args|-a)
                            # No completion for JSON arguments
                            ;;
                        *)
                            COMPREPLY=($(compgen -W "--args --format --show-help -a -f" -- "$cur"))
                            ;;
                    esac
                fi
                ;;
            list|list_tools)
                case $prev in
                    --format|-f)
                        COMPREPLY=($(compgen -W "json table plain" -- "$cur"))
                        ;;
                    *)
                        COMPREPLY=($(compgen -W "--format -f" -- "$cur"))
                        ;;
                esac
                ;;
        esac
    fi
}} &&

complete -F _lucius_call_completion lucius
"""


def generate_zsh_completion(tool_names: list[str]) -> str:
    """Generate zsh completion script."""
    tools_list = "\n    ".join(f'"{tool}"' for tool in tool_names)
    return f"""#compdef lucius

_lucius() {{
    local -a commands
    commands=(
        'list:List all available MCP tools'
        'call:Call an MCP tool by name'
        'version:Show version information'
        '--help:Show help information'
        '--version:Show version information'
    )

    if (( CURRENT == 2 )); then
        _describe -t commands 'lucius commands' commands
    else
        case $words[2] in
            call)
                if (( CURRENT == 3 )); then
                    _values 'tools' {tools_list}
                else
                    case ${{words[CURRENT-1]}} in
                        --format|-f)
                            _values 'format' json table plain
                            ;;
                        --args|-a)
                            # No completion for JSON
                            ;;
                        *)
                            _arguments \\
                                '--args[JSON arguments for tool]' \\
                                '--format[Output format]:format:(json table plain)' \\
                                '--show-help[Show tool-specific help]'
                            ;;
                    esac
                fi
                ;;
            list|list_tools)
                case ${{words[CURRENT-1]}} in
                    --format|-f)
                        _values 'format' json table plain
                        ;;
                    *)
                        _arguments \\
                            '--format[Output format]:format:(json table plain)'
                        ;;
                esac
                ;;
        esac
    fi
}}

_lucius "$@"
"""


def generate_fish_completion(tool_names: list[str]) -> str:
    """Generate fish completion script."""
    tools_str = " ".join(tool_names)
    return f"""# lucius CLI fish completion

complete -c lucius -f

# Main commands
complete -c lucius -n "__fish_use_subcommand" -a list -d "List all available MCP tools"
complete -c lucius -n "__fish_use_subcommand" -a call -d "Call an MCP tool by name"
complete -c lucius -n "__fish_use_subcommand" -a version -d "Show version information"

# list command options
complete -c lucius -n "__fish_seen_subcommand_from list" -l format -s f -r -d "Output format" -x -a "json table plain"

# call command - tool name completion
complete -c lucius -n "__fish_seen_subcommand_from call; and not __fish_seen_subcommand_from --show-help" -xa "{tools_str}"  # noqa: E501

# call command options
complete -c lucius -n "__fish_seen_subcommand_from call" -l args -s a -r -d "JSON arguments for tool"
complete -c lucius -n "__fish_seen_subcommand_from call" -l format -s f -r -d "Output format" -x -a "json table plain"
complete -c lucius -n "__fish_seen_subcommand_from call" -l show-help -d "Show tool-specific help"
"""


def generate_powershell_completion(tool_names: list[str]) -> str:
    """Generate PowerShell completion script."""
    tools_str = ", ".join(f'"{tool}"' for tool in tool_names)
    return f"""# lucius CLI PowerShell completion

Register-ArgumentCompleter -Native -CommandName lucius -ScriptBlock {{
    param($wordToComplete, $commandAst, $cursorPosition)

    $commands = @('list', 'call', 'version')
    $tools = @({tools_str})
    $formats = @('json', 'table', 'plain')

    if ($commandAst.CommandElements.Count -eq 1) {{
        # Complete main commands
        $commands | Where-Object {{ $_ -like "$wordToComplete*" }} | ForEach-Object {{ [System.Management.Automation.CompletionResult]::new($_, $_, 'ParameterValue', $_) }}  # noqa: E501
    }} elseif ($commandAst.CommandElements[1].Value -eq 'call') {{
        if ($commandAst.CommandElements.Count -eq 2) {{
            # Complete tool names
            $tools | Where-Object {{ $_ -like "$wordToComplete*" }} | ForEach-Object {{ [System.Management.Automation.CompletionResult]::new($_, $_, 'ParameterValue', $_) }}  # noqa: E501
        }} else {{
            # Complete options
            $options = @('--args', '-a', '--format', '-f', '--show-help')
            $options | Where-Object {{ $_ -like "$wordToComplete*" }} | ForEach-Object {{
                if ($_ -eq '--format' -or $_ -eq '-f') {{
                    $formats | ForEach-Object {{ [System.Management.Automation.CompletionResult]::new("$_", $_, 'ParameterValue', $_) }}  # noqa: E501
                }} else {{
                    [System.Management.Automation.CompletionResult]::new($_, $_, 'ParameterValue', $_)
                }}
            }}
        }}
    }} elseif ($commandAst.CommandElements[1].Value -eq 'list') {{
        $options = @('--format', '-f')
        $options | Where-Object {{ $_ -like "$wordToComplete*" }} | ForEach-Object {{
            if ($_ -eq '--format' -or $_ -eq '-f') {{
                $formats | ForEach-Object {{ [System.Management.Automation.CompletionResult]::new("$_", $_, 'ParameterValue', $_) }}  # noqa: E501
            }} else {{
                [System.Management.Automation.CompletionResult]::new($_, $_, 'ParameterValue', $_)
            }}
        }}
    }}
}}
"""


def main() -> None:
    """Generate all completion scripts."""
    print("Generating shell completion scripts...")

    tool_names = load_tool_names()
    print(f"Found {len(tool_names)} tools")

    # Create completion directory
    completion_dir = Path(__file__).parent / "completions"
    completion_dir.mkdir(parents=True, exist_ok=True)

    # Generate bash completion
    bash_completion = generate_bash_completion(tool_names)
    (completion_dir / "lucius.bash").write_text(bash_completion)
    print(f"✓ Generated: {completion_dir / 'lucius.bash'}")

    # Generate zsh completion
    zsh_completion = generate_zsh_completion(tool_names)
    (completion_dir / "lucius.zsh").write_text(zsh_completion)
    print(f"✓ Generated: {completion_dir / 'lucius.zsh'}")

    # Generate fish completion
    fish_completion = generate_fish_completion(tool_names)
    (completion_dir / "lucius.fish").write_text(fish_completion)
    print(f"✓ Generated: {completion_dir / 'lucius.fish'}")

    # Generate PowerShell completion
    ps_completion = generate_powershell_completion(tool_names)
    (completion_dir / "lucius.ps1").write_text(ps_completion)
    print(f"✓ Generated: {completion_dir / 'lucius.ps1'}")

    print("\\n✓ Shell completion scripts generated successfully!")
    print("\\nTo enable completion, add to your shell config:")
    print("  Bash:  source deployment/completions/lucius.bash")
    print("  Zsh:   source deployment/completions/lucius.zsh")
    print("  Fish:  source deployment/completions/lucius.fish")
    print("  PowerShell: . deployment/completions/lucius.ps1")


if __name__ == "__main__":
    main()
