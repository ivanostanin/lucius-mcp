# TestCaseBulkDtoV2


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**selection** | [**TestCaseSelectionDtoV2**](TestCaseSelectionDtoV2.md) |  | 

## Example

```python
from src.client.generated.models.test_case_bulk_dto_v2 import TestCaseBulkDtoV2

# TODO update the JSON string below
json = "{}"
# create an instance of TestCaseBulkDtoV2 from a JSON string
test_case_bulk_dto_v2_instance = TestCaseBulkDtoV2.from_json(json)
# print the JSON string representation of the object
print(TestCaseBulkDtoV2.to_json())

# convert the object into a dict
test_case_bulk_dto_v2_dict = test_case_bulk_dto_v2_instance.to_dict()
# create an instance of TestCaseBulkDtoV2 from a dict
test_case_bulk_dto_v2_from_dict = TestCaseBulkDtoV2.from_dict(test_case_bulk_dto_v2_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


