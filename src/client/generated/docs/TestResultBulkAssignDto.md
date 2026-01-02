# TestResultBulkAssignDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**assignees** | **List[str]** |  | [optional] 
**selection** | [**TestResultTreeSelectionDto**](TestResultTreeSelectionDto.md) |  | 

## Example

```python
from src.client.generated.models.test_result_bulk_assign_dto import TestResultBulkAssignDto

# TODO update the JSON string below
json = "{}"
# create an instance of TestResultBulkAssignDto from a JSON string
test_result_bulk_assign_dto_instance = TestResultBulkAssignDto.from_json(json)
# print the JSON string representation of the object
print(TestResultBulkAssignDto.to_json())

# convert the object into a dict
test_result_bulk_assign_dto_dict = test_result_bulk_assign_dto_instance.to_dict()
# create an instance of TestResultBulkAssignDto from a dict
test_result_bulk_assign_dto_from_dict = TestResultBulkAssignDto.from_dict(test_result_bulk_assign_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


