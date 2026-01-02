# TestResultCsvExportOptions


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**column_separator** | **str** |  | [optional] 
**mapping** | [**List[TestResultCsvExportOptionsMappingInner]**](TestResultCsvExportOptionsMappingInner.md) |  | [optional] 
**name** | **str** |  | [optional] 
**selection** | [**TestResultTreeSelectionDto**](TestResultTreeSelectionDto.md) |  | [optional] 
**with_headers** | **bool** |  | [optional] 

## Example

```python
from src.client.generated.models.test_result_csv_export_options import TestResultCsvExportOptions

# TODO update the JSON string below
json = "{}"
# create an instance of TestResultCsvExportOptions from a JSON string
test_result_csv_export_options_instance = TestResultCsvExportOptions.from_json(json)
# print the JSON string representation of the object
print(TestResultCsvExportOptions.to_json())

# convert the object into a dict
test_result_csv_export_options_dict = test_result_csv_export_options_instance.to_dict()
# create an instance of TestResultCsvExportOptions from a dict
test_result_csv_export_options_from_dict = TestResultCsvExportOptions.from_dict(test_result_csv_export_options_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


