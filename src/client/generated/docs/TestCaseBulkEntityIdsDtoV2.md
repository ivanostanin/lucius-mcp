# TestCaseBulkEntityIdsDtoV2


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**ids** | **List[int]** |  | 
**selection** | [**TestCaseSelectionDtoV2**](TestCaseSelectionDtoV2.md) |  | 

## Example

```python
from src.client.generated.models.test_case_bulk_entity_ids_dto_v2 import TestCaseBulkEntityIdsDtoV2

# TODO update the JSON string below
json = "{}"
# create an instance of TestCaseBulkEntityIdsDtoV2 from a JSON string
test_case_bulk_entity_ids_dto_v2_instance = TestCaseBulkEntityIdsDtoV2.from_json(json)
# print the JSON string representation of the object
print(TestCaseBulkEntityIdsDtoV2.to_json())

# convert the object into a dict
test_case_bulk_entity_ids_dto_v2_dict = test_case_bulk_entity_ids_dto_v2_instance.to_dict()
# create an instance of TestCaseBulkEntityIdsDtoV2 from a dict
test_case_bulk_entity_ids_dto_v2_from_dict = TestCaseBulkEntityIdsDtoV2.from_dict(test_case_bulk_entity_ids_dto_v2_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


