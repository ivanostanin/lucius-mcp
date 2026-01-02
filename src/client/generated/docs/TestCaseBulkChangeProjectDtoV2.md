# TestCaseBulkChangeProjectDtoV2


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**cf_mapping** | **Dict[str, int]** |  | [optional] 
**selection** | [**TestCaseSelectionDtoV2**](TestCaseSelectionDtoV2.md) |  | 
**strategy** | [**TestCaseBulkCfMoveStrategy**](TestCaseBulkCfMoveStrategy.md) |  | [optional] 
**to_project_id** | **int** |  | 

## Example

```python
from src.client.generated.models.test_case_bulk_change_project_dto_v2 import TestCaseBulkChangeProjectDtoV2

# TODO update the JSON string below
json = "{}"
# create an instance of TestCaseBulkChangeProjectDtoV2 from a JSON string
test_case_bulk_change_project_dto_v2_instance = TestCaseBulkChangeProjectDtoV2.from_json(json)
# print the JSON string representation of the object
print(TestCaseBulkChangeProjectDtoV2.to_json())

# convert the object into a dict
test_case_bulk_change_project_dto_v2_dict = test_case_bulk_change_project_dto_v2_instance.to_dict()
# create an instance of TestCaseBulkChangeProjectDtoV2 from a dict
test_case_bulk_change_project_dto_v2_from_dict = TestCaseBulkChangeProjectDtoV2.from_dict(test_case_bulk_change_project_dto_v2_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


