# TestCaseCfBulkDeltaDtoV2


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**selection** | [**TestCaseSelectionDtoV2**](TestCaseSelectionDtoV2.md) |  | 
**to_project_id** | **int** |  | 

## Example

```python
from src.client.generated.models.test_case_cf_bulk_delta_dto_v2 import TestCaseCfBulkDeltaDtoV2

# TODO update the JSON string below
json = "{}"
# create an instance of TestCaseCfBulkDeltaDtoV2 from a JSON string
test_case_cf_bulk_delta_dto_v2_instance = TestCaseCfBulkDeltaDtoV2.from_json(json)
# print the JSON string representation of the object
print(TestCaseCfBulkDeltaDtoV2.to_json())

# convert the object into a dict
test_case_cf_bulk_delta_dto_v2_dict = test_case_cf_bulk_delta_dto_v2_instance.to_dict()
# create an instance of TestCaseCfBulkDeltaDtoV2 from a dict
test_case_cf_bulk_delta_dto_v2_from_dict = TestCaseCfBulkDeltaDtoV2.from_dict(test_case_cf_bulk_delta_dto_v2_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


