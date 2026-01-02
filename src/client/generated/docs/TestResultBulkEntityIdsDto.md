# TestResultBulkEntityIdsDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**ids** | **List[int]** |  | 
**selection** | [**TestResultTreeSelectionDto**](TestResultTreeSelectionDto.md) |  | 

## Example

```python
from src.client.generated.models.test_result_bulk_entity_ids_dto import TestResultBulkEntityIdsDto

# TODO update the JSON string below
json = "{}"
# create an instance of TestResultBulkEntityIdsDto from a JSON string
test_result_bulk_entity_ids_dto_instance = TestResultBulkEntityIdsDto.from_json(json)
# print the JSON string representation of the object
print(TestResultBulkEntityIdsDto.to_json())

# convert the object into a dict
test_result_bulk_entity_ids_dto_dict = test_result_bulk_entity_ids_dto_instance.to_dict()
# create an instance of TestResultBulkEntityIdsDto from a dict
test_result_bulk_entity_ids_dto_from_dict = TestResultBulkEntityIdsDto.from_dict(test_result_bulk_entity_ids_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


