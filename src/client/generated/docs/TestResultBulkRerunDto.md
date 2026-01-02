# TestResultBulkRerunDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**assignees** | **List[str]** |  | [optional] 
**force_manual** | **bool** |  | [optional] 
**rql** | **str** |  | [optional] 
**selection** | [**TestResultTreeSelectionDto**](TestResultTreeSelectionDto.md) |  | 

## Example

```python
from src.client.generated.models.test_result_bulk_rerun_dto import TestResultBulkRerunDto

# TODO update the JSON string below
json = "{}"
# create an instance of TestResultBulkRerunDto from a JSON string
test_result_bulk_rerun_dto_instance = TestResultBulkRerunDto.from_json(json)
# print the JSON string representation of the object
print(TestResultBulkRerunDto.to_json())

# convert the object into a dict
test_result_bulk_rerun_dto_dict = test_result_bulk_rerun_dto_instance.to_dict()
# create an instance of TestResultBulkRerunDto from a dict
test_result_bulk_rerun_dto_from_dict = TestResultBulkRerunDto.from_dict(test_result_bulk_rerun_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


