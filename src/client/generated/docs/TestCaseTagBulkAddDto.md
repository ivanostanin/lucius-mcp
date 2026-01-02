# TestCaseTagBulkAddDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**selection** | [**TestCaseSelectionDtoV2**](TestCaseSelectionDtoV2.md) |  | 
**tags** | [**List[TestTagDto]**](TestTagDto.md) |  | 

## Example

```python
from src.client.generated.models.test_case_tag_bulk_add_dto import TestCaseTagBulkAddDto

# TODO update the JSON string below
json = "{}"
# create an instance of TestCaseTagBulkAddDto from a JSON string
test_case_tag_bulk_add_dto_instance = TestCaseTagBulkAddDto.from_json(json)
# print the JSON string representation of the object
print(TestCaseTagBulkAddDto.to_json())

# convert the object into a dict
test_case_tag_bulk_add_dto_dict = test_case_tag_bulk_add_dto_instance.to_dict()
# create an instance of TestCaseTagBulkAddDto from a dict
test_case_tag_bulk_add_dto_from_dict = TestCaseTagBulkAddDto.from_dict(test_case_tag_bulk_add_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


