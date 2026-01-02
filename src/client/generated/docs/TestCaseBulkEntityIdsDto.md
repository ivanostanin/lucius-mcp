# TestCaseBulkEntityIdsDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**ids** | **List[int]** |  | 
**selection** | [**TestCaseTreeSelectionDto**](TestCaseTreeSelectionDto.md) |  | 

## Example

```python
from src.client.generated.models.test_case_bulk_entity_ids_dto import TestCaseBulkEntityIdsDto

# TODO update the JSON string below
json = "{}"
# create an instance of TestCaseBulkEntityIdsDto from a JSON string
test_case_bulk_entity_ids_dto_instance = TestCaseBulkEntityIdsDto.from_json(json)
# print the JSON string representation of the object
print(TestCaseBulkEntityIdsDto.to_json())

# convert the object into a dict
test_case_bulk_entity_ids_dto_dict = test_case_bulk_entity_ids_dto_instance.to_dict()
# create an instance of TestCaseBulkEntityIdsDto from a dict
test_case_bulk_entity_ids_dto_from_dict = TestCaseBulkEntityIdsDto.from_dict(test_case_bulk_entity_ids_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


