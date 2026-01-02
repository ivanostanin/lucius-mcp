# TestPlanDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**base_rql** | **str** |  | [optional] 
**created_by** | **str** |  | [optional] 
**created_date** | **int** |  | [optional] 
**id** | **int** |  | [optional] 
**last_modified_by** | **str** |  | [optional] 
**last_modified_date** | **int** |  | [optional] 
**name** | **str** |  | [optional] 
**project_id** | **int** |  | [optional] 
**test_cases_count** | **int** |  | [optional] 
**tree** | [**IdAndNameOnlyDto**](IdAndNameOnlyDto.md) |  | [optional] 
**tree_selection** | [**TreeSelectionDto**](TreeSelectionDto.md) |  | [optional] 

## Example

```python
from src.client.generated.models.test_plan_dto import TestPlanDto

# TODO update the JSON string below
json = "{}"
# create an instance of TestPlanDto from a JSON string
test_plan_dto_instance = TestPlanDto.from_json(json)
# print the JSON string representation of the object
print(TestPlanDto.to_json())

# convert the object into a dict
test_plan_dto_dict = test_plan_dto_instance.to_dict()
# create an instance of TestPlanDto from a dict
test_plan_dto_from_dict = TestPlanDto.from_dict(test_plan_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


