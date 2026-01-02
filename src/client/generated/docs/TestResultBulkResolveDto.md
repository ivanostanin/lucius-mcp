# TestResultBulkResolveDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**category_id** | **int** |  | [optional] 
**message** | **str** |  | [optional] 
**selection** | [**TestResultTreeSelectionDto**](TestResultTreeSelectionDto.md) |  | 
**status** | [**TestStatus**](TestStatus.md) |  | 

## Example

```python
from src.client.generated.models.test_result_bulk_resolve_dto import TestResultBulkResolveDto

# TODO update the JSON string below
json = "{}"
# create an instance of TestResultBulkResolveDto from a JSON string
test_result_bulk_resolve_dto_instance = TestResultBulkResolveDto.from_json(json)
# print the JSON string representation of the object
print(TestResultBulkResolveDto.to_json())

# convert the object into a dict
test_result_bulk_resolve_dto_dict = test_result_bulk_resolve_dto_instance.to_dict()
# create an instance of TestResultBulkResolveDto from a dict
test_result_bulk_resolve_dto_from_dict = TestResultBulkResolveDto.from_dict(test_result_bulk_resolve_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


