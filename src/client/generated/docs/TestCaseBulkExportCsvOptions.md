# TestCaseBulkExportCsvOptions


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**column_separator** | **str** |  | [optional] 
**mapping** | [**List[TestCaseBulkExportCsvOptionsMappingInner]**](TestCaseBulkExportCsvOptionsMappingInner.md) |  | [optional] 
**name** | **str** |  | [optional] 
**selection** | [**TestCaseSelectionDtoV2**](TestCaseSelectionDtoV2.md) |  | 
**with_headers** | **bool** |  | [optional] 

## Example

```python
from src.client.generated.models.test_case_bulk_export_csv_options import TestCaseBulkExportCsvOptions

# TODO update the JSON string below
json = "{}"
# create an instance of TestCaseBulkExportCsvOptions from a JSON string
test_case_bulk_export_csv_options_instance = TestCaseBulkExportCsvOptions.from_json(json)
# print the JSON string representation of the object
print(TestCaseBulkExportCsvOptions.to_json())

# convert the object into a dict
test_case_bulk_export_csv_options_dict = test_case_bulk_export_csv_options_instance.to_dict()
# create an instance of TestCaseBulkExportCsvOptions from a dict
test_case_bulk_export_csv_options_from_dict = TestCaseBulkExportCsvOptions.from_dict(test_case_bulk_export_csv_options_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


