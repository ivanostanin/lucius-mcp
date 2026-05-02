# lucius CLI PowerShell completion (entity/action)

Register-ArgumentCompleter -Native -CommandName lucius -ScriptBlock {
    param($wordToComplete, $commandAst, $cursorPosition)

    $entities = @("custom-field", "custom-field-value", "custom-field-values", "custom-fields", "custom_field", "custom_field_value", "custom_field_values", "custom_fields", "defect", "defect-matcher", "defect-matchers", "defect_matcher", "defect_matchers", "defects", "integration", "integrations", "launch", "launches", "shared-step", "shared-steps", "shared_step", "shared_steps", "test-case", "test-cases", "test-layer", "test-layer-schema", "test-layer-schemas", "test-layers", "test-plan", "test-plans", "test-suite", "test-suites", "test_case", "test_cases", "test_layer", "test_layer_schema", "test_layer_schemas", "test_layers", "test_plan", "test_plans", "test_suite", "test_suites")
    $globalTokens = @("--help", "-h", "--version", "-V", "help", "version", "auth", "list")
    $formats = @("json", "table", "plain", "csv")
    $options = @("--args", "-a", "--format", "-f", "--pretty", "--help", "-h")
    $authOptions = @("--url", "--token", "--project", "--help", "-h")
    $authSubcommands = @("status", "clear")
    $listOptions = @("--help", "-h")
    $aliasToCanonical = @{
        "custom_field" = "custom_field"
        "custom_field_value" = "custom_field_value"
        "custom_field_values" = "custom_field_value"
        "custom_fields" = "custom_field"
        "defect" = "defect"
        "defect_matcher" = "defect_matcher"
        "defect_matchers" = "defect_matcher"
        "defects" = "defect"
        "integration" = "integration"
        "integrations" = "integration"
        "launch" = "launch"
        "launches" = "launch"
        "shared_step" = "shared_step"
        "shared_steps" = "shared_step"
        "test_case" = "test_case"
        "test_cases" = "test_case"
        "test_layer" = "test_layer"
        "test_layer_schema" = "test_layer_schema"
        "test_layer_schemas" = "test_layer_schema"
        "test_layers" = "test_layer"
        "test_plan" = "test_plan"
        "test_plans" = "test_plan"
        "test_suite" = "test_suite"
        "test_suites" = "test_suite"
    }
    $actionsByEntity = @{
        "custom_field" = @("delete-unused", "delete_unused", "get", "list")
        "custom_field_value" = @("create", "delete", "list", "update")
        "defect" = @("create", "delete", "get", "link-test-case", "link_test_case", "list", "list-test-cases", "list_test_cases", "update")
        "defect_matcher" = @("create", "delete", "list", "update")
        "integration" = @("list")
        "launch" = @("close", "create", "delete", "get", "list", "reopen")
        "shared_step" = @("create", "delete", "delete-archived", "delete_archived", "link-test-case", "link_test_case", "list", "unlink-test-case", "unlink_test_case", "update")
        "test_case" = @("create", "delete", "delete-archived", "delete_archived", "get", "get-custom-fields", "get_custom_fields", "list", "search", "update")
        "test_layer" = @("create", "delete", "list", "update")
        "test_layer_schema" = @("create", "delete", "list", "update")
        "test_plan" = @("create", "delete", "list", "manage-content", "manage_content", "update")
        "test_suite" = @("assign-test-cases", "assign_test_cases", "create", "delete", "list")
    }

    if ($commandAst.CommandElements.Count -le 1) {
        ($entities + $globalTokens) |
            Where-Object { $_ -like "$wordToComplete*" } |
            ForEach-Object { [System.Management.Automation.CompletionResult]::new($_, $_, 'ParameterValue', $_) }
        return
    }

    if ($commandAst.CommandElements.Count -eq 2) {
        ($entities + $globalTokens) |
            Where-Object { $_ -like "$wordToComplete*" } |
            ForEach-Object { [System.Management.Automation.CompletionResult]::new($_, $_, 'ParameterValue', $_) }
        return
    }

    $entityToken = $commandAst.CommandElements[1].Value.ToLower().Replace('-', '_')
    if ($entityToken -eq 'auth') {
        $lastToken = $commandAst.CommandElements[$commandAst.CommandElements.Count - 1].Value
        if ($lastToken -eq '--url' -or $lastToken -eq '--token' -or $lastToken -eq '--project') {
            return
        }
        if ($commandAst.CommandElements.Count -gt 3 -and $commandAst.CommandElements[2].Value -eq 'status') {
            return
        }
        ($authSubcommands + $authOptions) |
            Where-Object { $_ -like "$wordToComplete*" } |
            ForEach-Object { [System.Management.Automation.CompletionResult]::new($_, $_, 'ParameterValue', $_) }
        return
    }

    if ($entityToken -eq 'list') {
        if ($commandAst.CommandElements.Count -gt 3) {
            return
        }
        $listOptions |
            Where-Object { $_ -like "$wordToComplete*" } |
            ForEach-Object { [System.Management.Automation.CompletionResult]::new($_, $_, 'ParameterValue', $_) }
        return
    }

    $canonicalEntity = $null
    if ($aliasToCanonical.ContainsKey($entityToken)) {
        $canonicalEntity = $aliasToCanonical[$entityToken]
    }

    if ($commandAst.CommandElements.Count -eq 3 -and $canonicalEntity) {
        $actionsByEntity[$canonicalEntity] |
            Where-Object { $_ -like "$wordToComplete*" } |
            ForEach-Object { [System.Management.Automation.CompletionResult]::new($_, $_, 'ParameterValue', $_) }
        return
    }

    $lastToken = $commandAst.CommandElements[$commandAst.CommandElements.Count - 1].Value

    if ($lastToken -eq '--format' -or $lastToken -eq '-f') {
        $formats |
            Where-Object { $_ -like "$wordToComplete*" } |
            ForEach-Object { [System.Management.Automation.CompletionResult]::new($_, $_, 'ParameterValue', $_) }
        return
    }

    if ($lastToken -eq '--args' -or $lastToken -eq '-a') {
        return
    }

    $options |
        Where-Object { $_ -like "$wordToComplete*" } |
        ForEach-Object { [System.Management.Automation.CompletionResult]::new($_, $_, 'ParameterValue', $_) }
}
