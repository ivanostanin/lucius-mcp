# TestCaseBulkDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**selection** | [**TestCaseTreeSelectionDto**](TestCaseTreeSelectionDto.md) |  | 

## Example

```python
from src.client.generated.models.test_case_bulk_dto import TestCaseBulkDto

# TODO update the JSON string below
json = "{}"
# create an instance of TestCaseBulkDto from a JSON string
test_case_bulk_dto_instance = TestCaseBulkDto.from_json(json)
# print the JSON string representation of the object
print(TestCaseBulkDto.to_json())

# convert the object into a dict
test_case_bulk_dto_dict = test_case_bulk_dto_instance.to_dict()
# create an instance of TestCaseBulkDto from a dict
test_case_bulk_dto_from_dict = TestCaseBulkDto.from_dict(test_case_bulk_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


