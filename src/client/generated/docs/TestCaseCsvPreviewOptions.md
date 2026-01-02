# TestCaseCsvPreviewOptions


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**auto_detect_format** | **bool** |  | [optional] 
**column_separator** | **str** |  | [optional] 
**escape_char** | **str** |  | [optional] 
**layer_id** | **int** |  | [optional] 
**mapping** | [**List[TestCaseCsvImportOptionsMappingInner]**](TestCaseCsvImportOptionsMappingInner.md) |  | [optional] 
**quote_char** | **str** |  | [optional] 
**row_num** | **int** |  | [optional] 
**status_id** | **int** |  | [optional] 
**with_headers** | **bool** |  | [optional] 
**workflow_id** | **int** |  | [optional] 

## Example

```python
from src.client.generated.models.test_case_csv_preview_options import TestCaseCsvPreviewOptions

# TODO update the JSON string below
json = "{}"
# create an instance of TestCaseCsvPreviewOptions from a JSON string
test_case_csv_preview_options_instance = TestCaseCsvPreviewOptions.from_json(json)
# print the JSON string representation of the object
print(TestCaseCsvPreviewOptions.to_json())

# convert the object into a dict
test_case_csv_preview_options_dict = test_case_csv_preview_options_instance.to_dict()
# create an instance of TestCaseCsvPreviewOptions from a dict
test_case_csv_preview_options_from_dict = TestCaseCsvPreviewOptions.from_dict(test_case_csv_preview_options_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


