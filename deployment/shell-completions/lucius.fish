# lucius CLI fish completion (entity/action)

complete -c lucius -f

# Main command tokens
complete -c lucius -n "__fish_use_subcommand" -a "cf cfv custom-field custom-field-value custom-field-values custom-fields custom_field custom_field_value custom_field_values custom_fields defect defect-matcher defect-matchers defect_matcher defect_matchers defects df dm int integration integrations launch launches ln shared-step shared-steps shared_step shared_steps ss tc test-case test-cases test-layer test-layer-schema test-layer-schemas test-layers test-plan test-plans test-suite test-suites test_case test_cases test_layer test_layer_schema test_layer_schemas test_layers test_plan test_plans test_suite test_suites tl tls tp ts" -d "Entity"
complete -c lucius -n "__fish_use_subcommand" -a "--help -h --version -V help version auth list install-completions" -d "Global command"
complete -c lucius -n "__fish_seen_subcommand_from auth; and not __fish_seen_subcommand_from status" -a "status clear" -d "Auth command"
complete -c lucius -n "__fish_seen_subcommand_from auth; and not __fish_seen_subcommand_from status" -l url -r -d "Allure TestOps base URL"
complete -c lucius -n "__fish_seen_subcommand_from auth; and not __fish_seen_subcommand_from status" -l token -r -d "Allure API token"
complete -c lucius -n "__fish_seen_subcommand_from auth; and not __fish_seen_subcommand_from status" -l project -r -d "Default project ID"
complete -c lucius -n "__fish_seen_subcommand_from auth; and not __fish_seen_subcommand_from status" -l help -s h -d "Show auth help"

# install-completions options
# --shell --path --force --print --help -h
complete -c lucius -n "__fish_seen_subcommand_from install-completions" -l shell -r -x -a "bash zsh fish powershell" -d "Target shell"
complete -c lucius -n "__fish_seen_subcommand_from install-completions" -l path -r -d "Completion output path"
complete -c lucius -n "__fish_seen_subcommand_from install-completions" -l force -d "Overwrite existing completion file"
complete -c lucius -n "__fish_seen_subcommand_from install-completions" -l print -d "Print completion script"
complete -c lucius -n "__fish_seen_subcommand_from install-completions" -l help -s h -d "Show install-completions help"

complete -c lucius -n "__fish_seen_subcommand_from cf custom-field custom-fields custom_field custom_fields" -a "delete-unused delete_unused get list" -d "Action"
complete -c lucius -n "__fish_seen_subcommand_from cfv custom-field-value custom-field-values custom_field_value custom_field_values" -a "create delete list update" -d "Action"
complete -c lucius -n "__fish_seen_subcommand_from defect defects df" -a "create delete get link-test-case link_test_case list list-test-cases list_test_cases update" -d "Action"
complete -c lucius -n "__fish_seen_subcommand_from defect-matcher defect-matchers defect_matcher defect_matchers dm" -a "create delete list update" -d "Action"
complete -c lucius -n "__fish_seen_subcommand_from int integration integrations" -a "list" -d "Action"
complete -c lucius -n "__fish_seen_subcommand_from launch launches ln" -a "close create delete get list reopen" -d "Action"
complete -c lucius -n "__fish_seen_subcommand_from shared-step shared-steps shared_step shared_steps ss" -a "create delete delete-archived delete_archived link-test-case link_test_case list unlink-test-case unlink_test_case update" -d "Action"
complete -c lucius -n "__fish_seen_subcommand_from tc test-case test-cases test_case test_cases" -a "create delete delete-archived delete_archived get get-custom-fields get_custom_fields list search update" -d "Action"
complete -c lucius -n "__fish_seen_subcommand_from test-layer test-layers test_layer test_layers tl" -a "create delete list update" -d "Action"
complete -c lucius -n "__fish_seen_subcommand_from test-layer-schema test-layer-schemas test_layer_schema test_layer_schemas tls" -a "create delete list update" -d "Action"
complete -c lucius -n "__fish_seen_subcommand_from test-plan test-plans test_plan test_plans tp" -a "create delete list manage-content manage_content update" -d "Action"
complete -c lucius -n "__fish_seen_subcommand_from test-suite test-suites test_suite test_suites ts" -a "assign-test-cases assign_test_cases create delete list" -d "Action"

# Common action options
complete -c lucius -n "__fish_seen_subcommand_from assign-test-cases assign_test_cases close create delete delete-archived delete-unused delete_archived delete_unused get get-custom-fields get_custom_fields link-test-case link_test_case list list-test-cases list_test_cases manage-content manage_content reopen search unlink-test-case unlink_test_case update" -l args -s a -r -d "JSON arguments"
complete -c lucius -n "__fish_seen_subcommand_from assign-test-cases assign_test_cases close create delete delete-archived delete-unused delete_archived delete_unused get get-custom-fields get_custom_fields link-test-case link_test_case list list-test-cases list_test_cases manage-content manage_content reopen search unlink-test-case unlink_test_case update" -l format -s f -r -x -a "json table plain csv" -d "Output format"
complete -c lucius -n "__fish_seen_subcommand_from assign-test-cases assign_test_cases close create delete delete-archived delete-unused delete_archived delete_unused get get-custom-fields get_custom_fields link-test-case link_test_case list list-test-cases list_test_cases manage-content manage_content reopen search unlink-test-case unlink_test_case update" -l pretty -d "Pretty-print JSON output"
complete -c lucius -n "__fish_seen_subcommand_from assign-test-cases assign_test_cases close create delete delete-archived delete-unused delete_archived delete_unused get get-custom-fields get_custom_fields link-test-case link_test_case list list-test-cases list_test_cases manage-content manage_content reopen search unlink-test-case unlink_test_case update" -l help -s h -d "Show action help"
