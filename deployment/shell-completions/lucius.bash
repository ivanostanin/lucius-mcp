# lucius CLI bash completion (entity/action)

_lucius_completion() {
    local cur prev
    COMPREPLY=()
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"

    if [[ $COMP_CWORD -eq 1 ]]; then
        COMPREPLY=($(compgen -W "cf cfv custom-field custom-field-value custom-field-values custom-fields custom_field custom_field_value custom_field_values custom_fields defect defect-matcher defect-matchers defect_matcher defect_matchers defects df dm int integration integrations launch launches ln shared-step shared-steps shared_step shared_steps ss tc test-case test-cases test-layer test-layer-schema test-layer-schemas test-layers test-plan test-plans test-suite test-suites test_case test_cases test_layer test_layer_schema test_layer_schemas test_layers test_plan test_plans test_suite test_suites tl tls tp ts --help -h --version -V help version auth list install-completions" -- "$cur"))
        return 0
    fi

    local entity
    entity="${COMP_WORDS[1]//-/_}"

    if [[ $COMP_CWORD -eq 2 ]]; then
        if [[ $entity == "auth" ]]; then
            COMPREPLY=($(compgen -W "status clear --url --token --project --help -h" -- "$cur"))
            return 0
        fi
        if [[ ${COMP_WORDS[1]} == "install-completions" ]]; then
            COMPREPLY=($(compgen -W "--shell --path --force --print --help -h" -- "$cur"))
            return 0
        fi
        case "$entity" in
            cf|custom_field|custom_fields)
                COMPREPLY=($(compgen -W "delete-unused delete_unused get list" -- "$cur"))
                return 0
                ;;
            cfv|custom_field_value|custom_field_values)
                COMPREPLY=($(compgen -W "create delete list update" -- "$cur"))
                return 0
                ;;
            defect|defects|df)
                COMPREPLY=($(compgen -W "create delete get link-test-case link_test_case list list-test-cases list_test_cases update" -- "$cur"))
                return 0
                ;;
            defect_matcher|defect_matchers|dm)
                COMPREPLY=($(compgen -W "create delete list update" -- "$cur"))
                return 0
                ;;
            int|integration|integrations)
                COMPREPLY=($(compgen -W "list" -- "$cur"))
                return 0
                ;;
            launch|launches|ln)
                COMPREPLY=($(compgen -W "close create delete get list reopen" -- "$cur"))
                return 0
                ;;
            shared_step|shared_steps|ss)
                COMPREPLY=($(compgen -W "create delete delete-archived delete_archived link-test-case link_test_case list unlink-test-case unlink_test_case update" -- "$cur"))
                return 0
                ;;
            tc|test_case|test_cases)
                COMPREPLY=($(compgen -W "create delete delete-archived delete_archived get get-custom-fields get_custom_fields list search update" -- "$cur"))
                return 0
                ;;
            test_layer|test_layers|tl)
                COMPREPLY=($(compgen -W "create delete list update" -- "$cur"))
                return 0
                ;;
            test_layer_schema|test_layer_schemas|tls)
                COMPREPLY=($(compgen -W "create delete list update" -- "$cur"))
                return 0
                ;;
            test_plan|test_plans|tp)
                COMPREPLY=($(compgen -W "create delete list manage-content manage_content update" -- "$cur"))
                return 0
                ;;
            test_suite|test_suites|ts)
                COMPREPLY=($(compgen -W "assign-test-cases assign_test_cases create delete list" -- "$cur"))
                return 0
                ;;
            *)
                ;;
        esac
        return 0
    fi

    if [[ $entity == "auth" ]]; then
        if [[ $prev == "--url" || $prev == "--token" || $prev == "--project" ]]; then
            return 0
        fi
        if [[ ${COMP_WORDS[2]//-/_} == "status" ]]; then
            return 0
        fi
        COMPREPLY=($(compgen -W "status clear --url --token --project --help -h" -- "$cur"))
        return 0
    fi

    if [[ ${COMP_WORDS[1]} == "install-completions" ]]; then
        if [[ $prev == "--shell" ]]; then
            COMPREPLY=($(compgen -W "bash zsh fish powershell" -- "$cur"))
            return 0
        fi
        if [[ $prev == "--path" ]]; then
            return 0
        fi
        COMPREPLY=($(compgen -W "--shell --path --force --print --help -h" -- "$cur"))
        return 0
    fi

    case "$prev" in
        --format|-f)
            COMPREPLY=($(compgen -W "json table plain csv" -- "$cur"))
            return 0
            ;;
        --args|-a)
            return 0
            ;;
        *)
            COMPREPLY=($(compgen -W "--args -a --format -f --pretty --help -h" -- "$cur"))
            return 0
            ;;
    esac
}

complete -F _lucius_completion lucius
