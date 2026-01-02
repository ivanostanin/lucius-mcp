# TestCaseBulkTagDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**selection** | [**TestCaseTreeSelectionDto**](TestCaseTreeSelectionDto.md) |  | 
**tags** | [**List[TestTagDto]**](TestTagDto.md) |  | 

## Example

```python
from src.client.generated.models.test_case_bulk_tag_dto import TestCaseBulkTagDto

# TODO update the JSON string below
json = "{}"
# create an instance of TestCaseBulkTagDto from a JSON string
test_case_bulk_tag_dto_instance = TestCaseBulkTagDto.from_json(json)
# print the JSON string representation of the object
print(TestCaseBulkTagDto.to_json())

# convert the object into a dict
test_case_bulk_tag_dto_dict = test_case_bulk_tag_dto_instance.to_dict()
# create an instance of TestCaseBulkTagDto from a dict
test_case_bulk_tag_dto_from_dict = TestCaseBulkTagDto.from_dict(test_case_bulk_tag_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


