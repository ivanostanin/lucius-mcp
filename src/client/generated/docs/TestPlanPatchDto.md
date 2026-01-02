# TestPlanPatchDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**base_rql** | **str** |  | [optional] 
**name** | **str** |  | [optional] 
**tree_id** | **int** |  | [optional] 
**tree_selection** | [**TreeSelectionDto**](TreeSelectionDto.md) |  | [optional] 

## Example

```python
from src.client.generated.models.test_plan_patch_dto import TestPlanPatchDto

# TODO update the JSON string below
json = "{}"
# create an instance of TestPlanPatchDto from a JSON string
test_plan_patch_dto_instance = TestPlanPatchDto.from_json(json)
# print the JSON string representation of the object
print(TestPlanPatchDto.to_json())

# convert the object into a dict
test_plan_patch_dto_dict = test_plan_patch_dto_instance.to_dict()
# create an instance of TestPlanPatchDto from a dict
test_plan_patch_dto_from_dict = TestPlanPatchDto.from_dict(test_plan_patch_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


