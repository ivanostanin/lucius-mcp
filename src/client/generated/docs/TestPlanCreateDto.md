# TestPlanCreateDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**base_rql** | **str** |  | [optional] 
**name** | **str** |  | 
**project_id** | **int** |  | 
**tree_id** | **int** |  | [optional] 
**tree_selection** | [**TreeSelectionDto**](TreeSelectionDto.md) |  | [optional] 

## Example

```python
from src.client.generated.models.test_plan_create_dto import TestPlanCreateDto

# TODO update the JSON string below
json = "{}"
# create an instance of TestPlanCreateDto from a JSON string
test_plan_create_dto_instance = TestPlanCreateDto.from_json(json)
# print the JSON string representation of the object
print(TestPlanCreateDto.to_json())

# convert the object into a dict
test_plan_create_dto_dict = test_plan_create_dto_instance.to_dict()
# create an instance of TestPlanCreateDto from a dict
test_plan_create_dto_from_dict = TestPlanCreateDto.from_dict(test_plan_create_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


