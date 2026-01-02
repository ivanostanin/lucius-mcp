# TestCaseStatusBulkSetDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**selection** | [**TestCaseSelectionDtoV2**](TestCaseSelectionDtoV2.md) |  | 
**status_id** | **int** |  | 
**workflow_id** | **int** |  | 

## Example

```python
from src.client.generated.models.test_case_status_bulk_set_dto import TestCaseStatusBulkSetDto

# TODO update the JSON string below
json = "{}"
# create an instance of TestCaseStatusBulkSetDto from a JSON string
test_case_status_bulk_set_dto_instance = TestCaseStatusBulkSetDto.from_json(json)
# print the JSON string representation of the object
print(TestCaseStatusBulkSetDto.to_json())

# convert the object into a dict
test_case_status_bulk_set_dto_dict = test_case_status_bulk_set_dto_instance.to_dict()
# create an instance of TestCaseStatusBulkSetDto from a dict
test_case_status_bulk_set_dto_from_dict = TestCaseStatusBulkSetDto.from_dict(test_case_status_bulk_set_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


