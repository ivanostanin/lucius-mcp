"""Runtime-safe shell completion generation for the Lucius CLI."""

from __future__ import annotations

from src.cli.local_commands import (
    AUTH_OPTIONS,
    AUTH_SUBCOMMANDS,
    CLI_LOCAL_COMMANDS,
    INSTALL_COMPLETIONS_OPTIONS,
)
from src.cli.route_matrix import (
    ACTION_ALIASES,
    CANONICAL_ROUTE_MATRIX,
    all_entities_with_aliases,
    normalize_token,
)

SUPPORTED_COMPLETION_SHELLS = ("bash", "zsh", "fish", "powershell")
FORMATS = ["json", "table", "plain", "csv"]
GLOBAL_TOKENS = ["--help", "-h", "--version", "-V", "help", "version", *CLI_LOCAL_COMMANDS]
ACTION_OPTIONS = ["--args", "-a", "--format", "-f", "--pretty", "--help", "-h"]


def completion_data() -> tuple[list[str], dict[str, str], dict[str, list[str]]]:
    """
    Return entity tokens, entity alias mapping, and action tokens by entity.

    CLI-local commands are deliberately excluded from the route matrix data and
    exposed separately through GLOBAL_TOKENS.
    """
    entity_aliases = all_entities_with_aliases()
    alias_to_canonical: dict[str, str] = {}
    all_entity_tokens: set[str] = set()
    actions_by_entity: dict[str, list[str]] = {}

    for canonical_entity, aliases in entity_aliases.items():
        for alias in aliases:
            alias_to_canonical[alias] = canonical_entity
            all_entity_tokens.add(alias)

        action_tokens: set[str] = set(CANONICAL_ROUTE_MATRIX[canonical_entity].keys())
        action_tokens.update(action.replace("_", "-") for action in list(action_tokens))

        for alias_action, canonical_action in ACTION_ALIASES.get(canonical_entity, {}).items():
            if canonical_action in CANONICAL_ROUTE_MATRIX[canonical_entity]:
                action_tokens.add(alias_action)
                action_tokens.add(alias_action.replace("_", "-"))

        actions_by_entity[canonical_entity] = sorted(action_tokens)

    return sorted(all_entity_tokens), alias_to_canonical, actions_by_entity


def _group_aliases_by_entity(alias_to_canonical: dict[str, str]) -> dict[str, list[str]]:
    grouped: dict[str, list[str]] = {}
    for alias, canonical in alias_to_canonical.items():
        grouped.setdefault(canonical, []).append(alias)
    for canonical in grouped:
        grouped[canonical] = sorted(grouped[canonical])
    return grouped


def generate_bash_completion(
    entities: list[str],
    alias_to_canonical: dict[str, str],
    actions_by_entity: dict[str, list[str]],
) -> str:
    """Generate bash completion script for entity/action CLI."""
    entity_groups = _group_aliases_by_entity(alias_to_canonical)
    case_blocks: list[str] = []
    for canonical, aliases in sorted(entity_groups.items()):
        normalized_aliases = sorted({normalize_token(alias) for alias in aliases})
        pattern = "|".join(normalized_aliases)
        actions = " ".join(actions_by_entity[canonical])
        case_blocks.append(
            f"""            {pattern})
                COMPREPLY=($(compgen -W "{actions}" -- "$cur"))
                return 0
                ;;
"""
        )

    entity_tokens = " ".join(entities)
    global_tokens = " ".join(GLOBAL_TOKENS)
    formats = " ".join(FORMATS)
    action_options = " ".join(ACTION_OPTIONS)
    auth_options = " ".join(AUTH_OPTIONS)
    auth_subcommands = " ".join(AUTH_SUBCOMMANDS)
    install_options = " ".join(INSTALL_COMPLETIONS_OPTIONS)
    cases = "".join(case_blocks)

    return f"""# lucius CLI bash completion (entity/action)

_lucius_completion() {{
    local cur prev
    COMPREPLY=()
    cur="${{COMP_WORDS[COMP_CWORD]}}"
    prev="${{COMP_WORDS[COMP_CWORD-1]}}"

    if [[ $COMP_CWORD -eq 1 ]]; then
        COMPREPLY=($(compgen -W "{entity_tokens} {global_tokens}" -- "$cur"))
        return 0
    fi

    local entity
    entity="${{COMP_WORDS[1]//-/_}}"

    if [[ $COMP_CWORD -eq 2 ]]; then
        if [[ $entity == "auth" ]]; then
            COMPREPLY=($(compgen -W "{auth_subcommands} {auth_options}" -- "$cur"))
            return 0
        fi
        if [[ ${{COMP_WORDS[1]}} == "install-completions" ]]; then
            COMPREPLY=($(compgen -W "{install_options}" -- "$cur"))
            return 0
        fi
        case "$entity" in
{cases}            *)
                ;;
        esac
        return 0
    fi

    if [[ $entity == "auth" ]]; then
        if [[ $prev == "--url" || $prev == "--token" || $prev == "--project" ]]; then
            return 0
        fi
        if [[ ${{COMP_WORDS[2]//-/_}} == "status" ]]; then
            return 0
        fi
        COMPREPLY=($(compgen -W "{auth_subcommands} {auth_options}" -- "$cur"))
        return 0
    fi

    if [[ ${{COMP_WORDS[1]}} == "install-completions" ]]; then
        if [[ $prev == "--shell" ]]; then
            COMPREPLY=($(compgen -W "bash zsh fish powershell" -- "$cur"))
            return 0
        fi
        if [[ $prev == "--path" ]]; then
            return 0
        fi
        COMPREPLY=($(compgen -W "{install_options}" -- "$cur"))
        return 0
    fi

    case "$prev" in
        --format|-f)
            COMPREPLY=($(compgen -W "{formats}" -- "$cur"))
            return 0
            ;;
        --args|-a)
            return 0
            ;;
        *)
            COMPREPLY=($(compgen -W "{action_options}" -- "$cur"))
            return 0
            ;;
    esac
}}

complete -F _lucius_completion lucius
"""


def generate_zsh_completion(
    entities: list[str],
    alias_to_canonical: dict[str, str],
    actions_by_entity: dict[str, list[str]],
) -> str:
    """Generate zsh completion script for entity/action CLI."""
    entity_groups = _group_aliases_by_entity(alias_to_canonical)
    case_blocks: list[str] = []
    for canonical, aliases in sorted(entity_groups.items()):
        normalized_aliases = sorted({normalize_token(alias) for alias in aliases})
        pattern = "|".join(normalized_aliases)
        actions = " ".join(actions_by_entity[canonical])
        case_blocks.append(
            f"""            {pattern})
                local -a actions
                actions=({actions})
                _describe -t actions 'actions' actions
                ;;
"""
        )

    entity_values = " ".join(entities)
    global_values = " ".join(GLOBAL_TOKENS)
    format_values = " ".join(FORMATS)
    option_values = " ".join(ACTION_OPTIONS)
    auth_option_values = " ".join(AUTH_OPTIONS)
    auth_subcommand_values = " ".join(AUTH_SUBCOMMANDS)
    install_option_values = " ".join(INSTALL_COMPLETIONS_OPTIONS)
    cases = "".join(case_blocks)

    return f"""#compdef lucius

_lucius() {{
    local -a entities globals formats options authOptions authSubcommands authTokens installOptions shells
    entities=({entity_values})
    globals=({global_values})
    formats=({format_values})
    options=({option_values})
    authOptions=({auth_option_values})
    authSubcommands=({auth_subcommand_values})
    authTokens=($authSubcommands $authOptions)
    installOptions=({install_option_values})
    shells=(bash zsh fish powershell)

    if (( CURRENT == 2 )); then
        _describe -t entities 'lucius entities' entities
        _describe -t globals 'global commands' globals
        return 0
    fi

    local entity="${{words[2]:l}}"
    entity="${{entity//-/_}}"

    if (( CURRENT == 3 )); then
        if [[ "$entity" == "auth" ]]; then
            _describe -t auth 'auth commands' authTokens
            return 0
        fi
        if [[ "${{words[2]:l}}" == "install-completions" ]]; then
            _describe -t install-completions 'install-completions options' installOptions
            return 0
        fi
        case "$entity" in
{cases}            *)
                ;;
        esac
        return 0
    fi

    if [[ "$entity" == "auth" ]]; then
        if (( CURRENT > 3 )) && [[ "${{words[3]:l}}" == "status" ]]; then
            return 0
        fi
        case "${{words[CURRENT-1]}}" in
            --url|--token|--project)
                return 0
                ;;
            *)
                _describe -t auth 'auth commands' authTokens
                return 0
                ;;
        esac
    fi

    if [[ "${{words[2]:l}}" == "install-completions" ]]; then
        case "${{words[CURRENT-1]}}" in
            --shell)
                _describe -t shells 'supported shells' shells
                return 0
                ;;
            --path)
                return 0
                ;;
            *)
                _describe -t install-completions 'install-completions options' installOptions
                return 0
                ;;
        esac
    fi

    case "${{words[CURRENT-1]}}" in
        --format|-f)
            _describe -t formats 'output formats' formats
            return 0
            ;;
        --args|-a)
            return 0
            ;;
        *)
            _describe -t options 'action options' options
            return 0
            ;;
    esac
}}

_lucius "$@"
"""


def generate_fish_completion(
    entities: list[str],
    alias_to_canonical: dict[str, str],
    actions_by_entity: dict[str, list[str]],
) -> str:
    """Generate fish completion script for entity/action CLI."""
    entity_groups = _group_aliases_by_entity(alias_to_canonical)
    lines: list[str] = [
        "# lucius CLI fish completion (entity/action)",
        "",
        "complete -c lucius -f",
        "",
        "# Main command tokens",
        f'complete -c lucius -n "__fish_use_subcommand" -a "{" ".join(entities)}" -d "Entity"',
        (f'complete -c lucius -n "__fish_use_subcommand" -a "{" ".join(GLOBAL_TOKENS)}" -d "Global command"'),
        (
            f'complete -c lucius -n "__fish_seen_subcommand_from auth; and not __fish_seen_subcommand_from status" '
            f'-a "{" ".join(AUTH_SUBCOMMANDS)}" -d "Auth command"'
        ),
        (
            'complete -c lucius -n "__fish_seen_subcommand_from auth; and not __fish_seen_subcommand_from status" '
            '-l url -r -d "Allure TestOps base URL"'
        ),
        (
            'complete -c lucius -n "__fish_seen_subcommand_from auth; and not __fish_seen_subcommand_from status" '
            '-l token -r -d "Allure API token"'
        ),
        (
            'complete -c lucius -n "__fish_seen_subcommand_from auth; and not __fish_seen_subcommand_from status" '
            '-l project -r -d "Default project ID"'
        ),
        (
            'complete -c lucius -n "__fish_seen_subcommand_from auth; and not __fish_seen_subcommand_from status" '
            '-l help -s h -d "Show auth help"'
        ),
        "",
        "# install-completions options",
        "# --shell --path --force --print --help -h",
        (
            'complete -c lucius -n "__fish_seen_subcommand_from install-completions" '
            '-l shell -r -x -a "bash zsh fish powershell" -d "Target shell"'
        ),
        (
            'complete -c lucius -n "__fish_seen_subcommand_from install-completions" '
            '-l path -r -d "Completion output path"'
        ),
        (
            'complete -c lucius -n "__fish_seen_subcommand_from install-completions" '
            '-l force -d "Overwrite existing completion file"'
        ),
        'complete -c lucius -n "__fish_seen_subcommand_from install-completions" -l print -d "Print completion script"',
        (
            'complete -c lucius -n "__fish_seen_subcommand_from install-completions" '
            '-l help -s h -d "Show install-completions help"'
        ),
        "",
    ]

    all_action_tokens: set[str] = set()
    for canonical, aliases in sorted(entity_groups.items()):
        alias_tokens = " ".join(aliases)
        action_tokens = " ".join(actions_by_entity[canonical])
        all_action_tokens.update(actions_by_entity[canonical])
        lines.append(
            f'complete -c lucius -n "__fish_seen_subcommand_from {alias_tokens}" -a "{action_tokens}" -d "Action"'
        )

    all_actions = " ".join(sorted(all_action_tokens))
    lines.extend(
        [
            "",
            "# Common action options",
            (f'complete -c lucius -n "__fish_seen_subcommand_from {all_actions}" -l args -s a -r -d "JSON arguments"'),
            (
                f'complete -c lucius -n "__fish_seen_subcommand_from {all_actions}" '
                f'-l format -s f -r -x -a "{" ".join(FORMATS)}" -d "Output format"'
            ),
            (
                f'complete -c lucius -n "__fish_seen_subcommand_from {all_actions}" '
                '-l pretty -d "Pretty-print JSON output"'
            ),
            (f'complete -c lucius -n "__fish_seen_subcommand_from {all_actions}" -l help -s h -d "Show action help"'),
            "",
        ]
    )

    return "\n".join(lines)


def generate_powershell_completion(
    entities: list[str],
    alias_to_canonical: dict[str, str],
    actions_by_entity: dict[str, list[str]],
) -> str:
    """Generate PowerShell completion script for entity/action CLI."""
    entity_values = ", ".join(f'"{entity}"' for entity in entities)
    global_values = ", ".join(f'"{token}"' for token in GLOBAL_TOKENS)
    format_values = ", ".join(f'"{fmt}"' for fmt in FORMATS)
    option_values = ", ".join(f'"{opt}"' for opt in ACTION_OPTIONS)
    auth_option_values = ", ".join(f'"{opt}"' for opt in AUTH_OPTIONS)
    auth_subcommand_values = ", ".join(f'"{token}"' for token in AUTH_SUBCOMMANDS)
    list_option_values = '"--help", "-h"'
    install_option_values = ", ".join(f'"{opt}"' for opt in INSTALL_COMPLETIONS_OPTIONS)
    shell_values = '"bash", "zsh", "fish", "powershell"'

    normalized_alias_to_canonical: dict[str, str] = {}
    for alias, canonical in sorted(alias_to_canonical.items()):
        normalized_alias_to_canonical.setdefault(normalize_token(alias), canonical)

    alias_entries = "\n".join(
        f'        "{alias}" = "{canonical}"' for alias, canonical in sorted(normalized_alias_to_canonical.items())
    )
    action_lines: list[str] = []
    for canonical, actions in sorted(actions_by_entity.items()):
        rendered_actions = ", ".join(f'"{action}"' for action in actions)
        action_lines.append(f'        "{canonical}" = @({rendered_actions})')
    action_entries = "\n".join(action_lines)

    return f"""# lucius CLI PowerShell completion (entity/action)

Register-ArgumentCompleter -Native -CommandName lucius -ScriptBlock {{
    param($wordToComplete, $commandAst, $cursorPosition)

    $entities = @({entity_values})
    $globalTokens = @({global_values})
    $formats = @({format_values})
    $options = @({option_values})
    $authOptions = @({auth_option_values})
    $authSubcommands = @({auth_subcommand_values})
    $listOptions = @({list_option_values})
    $installOptions = @({install_option_values})
    $shells = @({shell_values})
    $aliasToCanonical = @{{
{alias_entries}
    }}
    $actionsByEntity = @{{
{action_entries}
    }}

    if ($commandAst.CommandElements.Count -le 1) {{
        ($entities + $globalTokens) |
            Where-Object {{ $_ -like "$wordToComplete*" }} |
            ForEach-Object {{ [System.Management.Automation.CompletionResult]::new($_, $_, 'ParameterValue', $_) }}
        return
    }}

    if ($commandAst.CommandElements.Count -eq 2) {{
        ($entities + $globalTokens) |
            Where-Object {{ $_ -like "$wordToComplete*" }} |
            ForEach-Object {{ [System.Management.Automation.CompletionResult]::new($_, $_, 'ParameterValue', $_) }}
        return
    }}

    $entityToken = $commandAst.CommandElements[1].Value.ToLower().Replace('-', '_')
    if ($entityToken -eq 'auth') {{
        $lastToken = $commandAst.CommandElements[$commandAst.CommandElements.Count - 1].Value
        if ($lastToken -eq '--url' -or $lastToken -eq '--token' -or $lastToken -eq '--project') {{
            return
        }}
        if ($commandAst.CommandElements.Count -gt 3 -and $commandAst.CommandElements[2].Value -eq 'status') {{
            return
        }}
        ($authSubcommands + $authOptions) |
            Where-Object {{ $_ -like "$wordToComplete*" }} |
            ForEach-Object {{ [System.Management.Automation.CompletionResult]::new($_, $_, 'ParameterValue', $_) }}
        return
    }}

    if ($entityToken -eq 'list') {{
        if ($commandAst.CommandElements.Count -gt 3) {{
            return
        }}
        $listOptions |
            Where-Object {{ $_ -like "$wordToComplete*" }} |
            ForEach-Object {{ [System.Management.Automation.CompletionResult]::new($_, $_, 'ParameterValue', $_) }}
        return
    }}

    if ($commandAst.CommandElements[1].Value -eq 'install-completions') {{
        $lastToken = $commandAst.CommandElements[$commandAst.CommandElements.Count - 1].Value
        if ($lastToken -eq '--shell') {{
            $shells |
                Where-Object {{ $_ -like "$wordToComplete*" }} |
                ForEach-Object {{ [System.Management.Automation.CompletionResult]::new($_, $_, 'ParameterValue', $_) }}
            return
        }}
        if ($lastToken -eq '--path') {{
            return
        }}
        $installOptions |
            Where-Object {{ $_ -like "$wordToComplete*" }} |
            ForEach-Object {{ [System.Management.Automation.CompletionResult]::new($_, $_, 'ParameterValue', $_) }}
        return
    }}

    $canonicalEntity = $null
    if ($aliasToCanonical.ContainsKey($entityToken)) {{
        $canonicalEntity = $aliasToCanonical[$entityToken]
    }}

    if ($commandAst.CommandElements.Count -eq 3 -and $canonicalEntity) {{
        $actionsByEntity[$canonicalEntity] |
            Where-Object {{ $_ -like "$wordToComplete*" }} |
            ForEach-Object {{ [System.Management.Automation.CompletionResult]::new($_, $_, 'ParameterValue', $_) }}
        return
    }}

    $lastToken = $commandAst.CommandElements[$commandAst.CommandElements.Count - 1].Value

    if ($lastToken -eq '--format' -or $lastToken -eq '-f') {{
        $formats |
            Where-Object {{ $_ -like "$wordToComplete*" }} |
            ForEach-Object {{ [System.Management.Automation.CompletionResult]::new($_, $_, 'ParameterValue', $_) }}
        return
    }}

    if ($lastToken -eq '--args' -or $lastToken -eq '-a') {{
        return
    }}

    $options |
        Where-Object {{ $_ -like "$wordToComplete*" }} |
        ForEach-Object {{ [System.Management.Automation.CompletionResult]::new($_, $_, 'ParameterValue', $_) }}
}}
"""


def generate_completion(shell: str) -> str:
    """Generate one completion script by normalized shell name."""
    entities, alias_to_canonical, actions_by_entity = completion_data()
    if shell == "bash":
        return generate_bash_completion(entities, alias_to_canonical, actions_by_entity)
    if shell == "zsh":
        return generate_zsh_completion(entities, alias_to_canonical, actions_by_entity)
    if shell == "fish":
        return generate_fish_completion(entities, alias_to_canonical, actions_by_entity)
    if shell == "powershell":
        return generate_powershell_completion(entities, alias_to_canonical, actions_by_entity)
    raise ValueError(f"unsupported completion shell: {shell}")


def generate_all_completions() -> dict[str, str]:
    """Generate completion scripts for all supported shells."""
    return {shell: generate_completion(shell) for shell in SUPPORTED_COMPLETION_SHELLS}
