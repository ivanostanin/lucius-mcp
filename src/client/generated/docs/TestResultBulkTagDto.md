# TestResultBulkTagDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**selection** | [**TestResultTreeSelectionDto**](TestResultTreeSelectionDto.md) |  | 
**tags** | [**List[TestTagDto]**](TestTagDto.md) |  | 

## Example

```python
from src.client.generated.models.test_result_bulk_tag_dto import TestResultBulkTagDto

# TODO update the JSON string below
json = "{}"
# create an instance of TestResultBulkTagDto from a JSON string
test_result_bulk_tag_dto_instance = TestResultBulkTagDto.from_json(json)
# print the JSON string representation of the object
print(TestResultBulkTagDto.to_json())

# convert the object into a dict
test_result_bulk_tag_dto_dict = test_result_bulk_tag_dto_instance.to_dict()
# create an instance of TestResultBulkTagDto from a dict
test_result_bulk_tag_dto_from_dict = TestResultBulkTagDto.from_dict(test_result_bulk_tag_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


