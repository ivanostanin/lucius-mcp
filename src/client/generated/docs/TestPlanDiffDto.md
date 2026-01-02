# TestPlanDiffDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**added** | **int** |  | [optional] 
**deleted** | **int** |  | [optional] 

## Example

```python
from src.client.generated.models.test_plan_diff_dto import TestPlanDiffDto

# TODO update the JSON string below
json = "{}"
# create an instance of TestPlanDiffDto from a JSON string
test_plan_diff_dto_instance = TestPlanDiffDto.from_json(json)
# print the JSON string representation of the object
print(TestPlanDiffDto.to_json())

# convert the object into a dict
test_plan_diff_dto_dict = test_plan_diff_dto_instance.to_dict()
# create an instance of TestPlanDiffDto from a dict
test_plan_diff_dto_from_dict = TestPlanDiffDto.from_dict(test_plan_diff_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


