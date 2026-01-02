# TestCaseBulkExportCsvOptionsMappingInner


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**var_field** | **object** |  | [optional] 
**name** | **str** |  | [optional] 
**custom_field_id** | **int** |  | 
**items_separator** | **str** |  | 
**examples_separator** | **str** |  | [optional] 
**name_value_separator** | **str** |  | [optional] 
**params_separator** | **str** |  | [optional] 
**integration_id** | **int** |  | 
**role_id** | **int** |  | 
**steps_indent** | **str** |  | [optional] 
**steps_separator** | **str** |  | 

## Example

```python
from src.client.generated.models.test_case_bulk_export_csv_options_mapping_inner import TestCaseBulkExportCsvOptionsMappingInner

# TODO update the JSON string below
json = "{}"
# create an instance of TestCaseBulkExportCsvOptionsMappingInner from a JSON string
test_case_bulk_export_csv_options_mapping_inner_instance = TestCaseBulkExportCsvOptionsMappingInner.from_json(json)
# print the JSON string representation of the object
print(TestCaseBulkExportCsvOptionsMappingInner.to_json())

# convert the object into a dict
test_case_bulk_export_csv_options_mapping_inner_dict = test_case_bulk_export_csv_options_mapping_inner_instance.to_dict()
# create an instance of TestCaseBulkExportCsvOptionsMappingInner from a dict
test_case_bulk_export_csv_options_mapping_inner_from_dict = TestCaseBulkExportCsvOptionsMappingInner.from_dict(test_case_bulk_export_csv_options_mapping_inner_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


