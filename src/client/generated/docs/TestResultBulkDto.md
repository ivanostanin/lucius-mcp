# TestResultBulkDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**selection** | [**TestResultTreeSelectionDto**](TestResultTreeSelectionDto.md) |  | 

## Example

```python
from src.client.generated.models.test_result_bulk_dto import TestResultBulkDto

# TODO update the JSON string below
json = "{}"
# create an instance of TestResultBulkDto from a JSON string
test_result_bulk_dto_instance = TestResultBulkDto.from_json(json)
# print the JSON string representation of the object
print(TestResultBulkDto.to_json())

# convert the object into a dict
test_result_bulk_dto_dict = test_result_bulk_dto_instance.to_dict()
# create an instance of TestResultBulkDto from a dict
test_result_bulk_dto_from_dict = TestResultBulkDto.from_dict(test_result_bulk_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


