#compdef lucius

_lucius() {
    local -a entities globals formats options
    entities=(custom-field custom-field-value custom-field-values custom-fields custom_field custom_field_value custom_field_values custom_fields defect defect-matcher defect-matchers defect_matcher defect_matchers defects integration integrations launch launches shared-step shared-steps shared_step shared_steps test-case test-cases test-layer test-layer-schema test-layer-schemas test-layers test-plan test-plans test-suite test-suites test_case test_cases test_layer test_layer_schema test_layer_schemas test_layers test_plan test_plans test_suite test_suites)
    globals=(--help -h --version -V help version)
    formats=(json table plain)
    options=(--args -a --format -f --help -h)

    if (( CURRENT == 2 )); then
        _describe -t entities 'lucius entities' entities
        _describe -t globals 'global commands' globals
        return 0
    fi

    local entity="${words[2]:l}"
    entity="${entity//-/_}"

    if (( CURRENT == 3 )); then
        case "$entity" in
            custom_field|custom_fields)
                local -a actions
                actions=(delete-unused delete_unused get list)
                _describe -t actions 'actions' actions
                ;;
            custom_field_value|custom_field_values)
                local -a actions
                actions=(create delete list update)
                _describe -t actions 'actions' actions
                ;;
            defect|defects)
                local -a actions
                actions=(create delete get link-test-case link_test_case list list-test-cases list_test_cases update)
                _describe -t actions 'actions' actions
                ;;
            defect_matcher|defect_matchers)
                local -a actions
                actions=(create delete list update)
                _describe -t actions 'actions' actions
                ;;
            integration|integrations)
                local -a actions
                actions=(list)
                _describe -t actions 'actions' actions
                ;;
            launch|launches)
                local -a actions
                actions=(close create delete get list reopen)
                _describe -t actions 'actions' actions
                ;;
            shared_step|shared_steps)
                local -a actions
                actions=(create delete delete-archived delete_archived link-test-case link_test_case list unlink-test-case unlink_test_case update)
                _describe -t actions 'actions' actions
                ;;
            test_case|test_cases)
                local -a actions
                actions=(create delete delete-archived delete_archived get get-custom-fields get_custom_fields list search update)
                _describe -t actions 'actions' actions
                ;;
            test_layer|test_layers)
                local -a actions
                actions=(create delete list update)
                _describe -t actions 'actions' actions
                ;;
            test_layer_schema|test_layer_schemas)
                local -a actions
                actions=(create delete list update)
                _describe -t actions 'actions' actions
                ;;
            test_plan|test_plans)
                local -a actions
                actions=(create delete list manage-content manage_content update)
                _describe -t actions 'actions' actions
                ;;
            test_suite|test_suites)
                local -a actions
                actions=(assign-test-cases assign_test_cases create delete list)
                _describe -t actions 'actions' actions
                ;;
            *)
                ;;
        esac
        return 0
    fi

    case "${words[CURRENT-1]}" in
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
}

_lucius "$@"
