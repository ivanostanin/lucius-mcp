# TestCaseBulkProjectChangeDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**cf_mapping** | **Dict[str, int]** |  | [optional] 
**selection** | [**TestCaseTreeSelectionDto**](TestCaseTreeSelectionDto.md) |  | 
**strategy** | [**TestCaseBulkCfMoveStrategy**](TestCaseBulkCfMoveStrategy.md) |  | [optional] 
**to_project_id** | **int** |  | 

## Example

```python
from src.client.generated.models.test_case_bulk_project_change_dto import TestCaseBulkProjectChangeDto

# TODO update the JSON string below
json = "{}"
# create an instance of TestCaseBulkProjectChangeDto from a JSON string
test_case_bulk_project_change_dto_instance = TestCaseBulkProjectChangeDto.from_json(json)
# print the JSON string representation of the object
print(TestCaseBulkProjectChangeDto.to_json())

# convert the object into a dict
test_case_bulk_project_change_dto_dict = test_case_bulk_project_change_dto_instance.to_dict()
# create an instance of TestCaseBulkProjectChangeDto from a dict
test_case_bulk_project_change_dto_from_dict = TestCaseBulkProjectChangeDto.from_dict(test_case_bulk_project_change_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


