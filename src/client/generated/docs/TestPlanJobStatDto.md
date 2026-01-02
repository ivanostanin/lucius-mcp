# TestPlanJobStatDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**job** | [**JobDto**](JobDto.md) |  | [optional] 
**test_cases_count** | **int** |  | [optional] 

## Example

```python
from src.client.generated.models.test_plan_job_stat_dto import TestPlanJobStatDto

# TODO update the JSON string below
json = "{}"
# create an instance of TestPlanJobStatDto from a JSON string
test_plan_job_stat_dto_instance = TestPlanJobStatDto.from_json(json)
# print the JSON string representation of the object
print(TestPlanJobStatDto.to_json())

# convert the object into a dict
test_plan_job_stat_dto_dict = test_plan_job_stat_dto_instance.to_dict()
# create an instance of TestPlanJobStatDto from a dict
test_plan_job_stat_dto_from_dict = TestPlanJobStatDto.from_dict(test_plan_job_stat_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


