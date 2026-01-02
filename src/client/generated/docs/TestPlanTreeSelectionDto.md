# TestPlanTreeSelectionDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**groups_exclude** | **List[List[int]]** |  | [optional] 
**groups_include** | **List[List[int]]** |  | [optional] 
**inverted** | **bool** |  | [optional] 
**job_id** | **int** |  | [optional] 
**leafs_exclude** | **List[int]** |  | [optional] 
**leafs_include** | **List[int]** |  | [optional] 
**manual** | **bool** |  | [optional] 
**path** | **List[int]** |  | [optional] 
**username** | **str** |  | [optional] 

## Example

```python
from src.client.generated.models.test_plan_tree_selection_dto import TestPlanTreeSelectionDto

# TODO update the JSON string below
json = "{}"
# create an instance of TestPlanTreeSelectionDto from a JSON string
test_plan_tree_selection_dto_instance = TestPlanTreeSelectionDto.from_json(json)
# print the JSON string representation of the object
print(TestPlanTreeSelectionDto.to_json())

# convert the object into a dict
test_plan_tree_selection_dto_dict = test_plan_tree_selection_dto_instance.to_dict()
# create an instance of TestPlanTreeSelectionDto from a dict
test_plan_tree_selection_dto_from_dict = TestPlanTreeSelectionDto.from_dict(test_plan_tree_selection_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


