# TestCaseBulkStatusDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**selection** | [**TestCaseTreeSelectionDto**](TestCaseTreeSelectionDto.md) |  | 
**status_id** | **int** |  | 
**workflow_id** | **int** |  | 

## Example

```python
from src.client.generated.models.test_case_bulk_status_dto import TestCaseBulkStatusDto

# TODO update the JSON string below
json = "{}"
# create an instance of TestCaseBulkStatusDto from a JSON string
test_case_bulk_status_dto_instance = TestCaseBulkStatusDto.from_json(json)
# print the JSON string representation of the object
print(TestCaseBulkStatusDto.to_json())

# convert the object into a dict
test_case_bulk_status_dto_dict = test_case_bulk_status_dto_instance.to_dict()
# create an instance of TestCaseBulkStatusDto from a dict
test_case_bulk_status_dto_from_dict = TestCaseBulkStatusDto.from_dict(test_case_bulk_status_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


