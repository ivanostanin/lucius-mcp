# TestCaseCsvImportOptionsMappingInner


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**var_field** | [**TestCaseImportField**](TestCaseImportField.md) |  | 
**custom_field_id** | **int** |  | 
**items_separator** | **str** |  | [optional] 
**regex** | **bool** |  | [optional] 
**integration_id** | **int** |  | 
**name** | **str** |  | [optional] 
**type** | **str** |  | [optional] 
**role_id** | **int** |  | 
**prefix** | **str** |  | [optional] 

## Example

```python
from src.client.generated.models.test_case_csv_import_options_mapping_inner import TestCaseCsvImportOptionsMappingInner

# TODO update the JSON string below
json = "{}"
# create an instance of TestCaseCsvImportOptionsMappingInner from a JSON string
test_case_csv_import_options_mapping_inner_instance = TestCaseCsvImportOptionsMappingInner.from_json(json)
# print the JSON string representation of the object
print(TestCaseCsvImportOptionsMappingInner.to_json())

# convert the object into a dict
test_case_csv_import_options_mapping_inner_dict = test_case_csv_import_options_mapping_inner_instance.to_dict()
# create an instance of TestCaseCsvImportOptionsMappingInner from a dict
test_case_csv_import_options_mapping_inner_from_dict = TestCaseCsvImportOptionsMappingInner.from_dict(test_case_csv_import_options_mapping_inner_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


