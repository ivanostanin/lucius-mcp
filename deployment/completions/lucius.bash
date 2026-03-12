# lucius CLI bash completion
complete -W "list call version --help --version" lucius

# Tool name completion for 'call' command
_lucius_call_completion() {
    local cur prev words cword
    _init_completion || return

    if [[ $cword -eq 1 ]]; then
        COMPREPLY=($(compgen -W "assign_test_cases_to_suite close_launch create_custom_field_value create_defect create_defect_matcher create_launch create_shared_step create_test_case create_test_layer create_test_layer_schema create_test_plan create_test_suite delete_archived_shared_steps delete_archived_test_cases delete_custom_field_value delete_defect delete_defect_matcher delete_launch delete_shared_step delete_test_case delete_test_layer delete_test_layer_schema delete_test_suite delete_unused_custom_fields get_custom_fields get_defect get_launch get_test_case_custom_fields get_test_case_details link_defect_to_test_case link_shared_step list_custom_field_values list_defect_matchers list_defect_test_cases list_defects list_integrations list_launches list_shared_steps list_test_cases list_test_layer_schemas list_test_layers list_test_plans list_test_suites manage_test_plan_content reopen_launch search_test_cases unlink_shared_step update_custom_field_value update_defect update_defect_matcher update_shared_step update_test_case update_test_layer update_test_layer_schema update_test_plan" -- "$cur"))
    elif [[ $cword -ge 2 ]]; then
        case ${words[1]} in
            call)
                if [[ ${words[2]} == "${words[2]}" ]]; then
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
} &&

complete -F _lucius_call_completion lucius
