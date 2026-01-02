# TestCaseBulkDragAndDropDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**path** | **List[int]** |  | 
**selection** | [**TestCaseTreeSelectionDto**](TestCaseTreeSelectionDto.md) |  | 

## Example

```python
from src.client.generated.models.test_case_bulk_drag_and_drop_dto import TestCaseBulkDragAndDropDto

# TODO update the JSON string below
json = "{}"
# create an instance of TestCaseBulkDragAndDropDto from a JSON string
test_case_bulk_drag_and_drop_dto_instance = TestCaseBulkDragAndDropDto.from_json(json)
# print the JSON string representation of the object
print(TestCaseBulkDragAndDropDto.to_json())

# convert the object into a dict
test_case_bulk_drag_and_drop_dto_dict = test_case_bulk_drag_and_drop_dto_instance.to_dict()
# create an instance of TestCaseBulkDragAndDropDto from a dict
test_case_bulk_drag_and_drop_dto_from_dict = TestCaseBulkDragAndDropDto.from_dict(test_case_bulk_drag_and_drop_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


