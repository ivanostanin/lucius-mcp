# TestPlanRowDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **int** |  | [optional] 
**name** | **str** |  | [optional] 
**test_cases_count** | **int** |  | [optional] 

## Example

```python
from src.client.generated.models.test_plan_row_dto import TestPlanRowDto

# TODO update the JSON string below
json = "{}"
# create an instance of TestPlanRowDto from a JSON string
test_plan_row_dto_instance = TestPlanRowDto.from_json(json)
# print the JSON string representation of the object
print(TestPlanRowDto.to_json())

# convert the object into a dict
test_plan_row_dto_dict = test_plan_row_dto_instance.to_dict()
# create an instance of TestPlanRowDto from a dict
test_plan_row_dto_from_dict = TestPlanRowDto.from_dict(test_plan_row_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


