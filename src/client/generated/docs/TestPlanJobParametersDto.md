# TestPlanJobParametersDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**job_id** | **int** |  | 
**parameters** | [**List[JobParameterDto]**](JobParameterDto.md) |  | [optional] 

## Example

```python
from src.client.generated.models.test_plan_job_parameters_dto import TestPlanJobParametersDto

# TODO update the JSON string below
json = "{}"
# create an instance of TestPlanJobParametersDto from a JSON string
test_plan_job_parameters_dto_instance = TestPlanJobParametersDto.from_json(json)
# print the JSON string representation of the object
print(TestPlanJobParametersDto.to_json())

# convert the object into a dict
test_plan_job_parameters_dto_dict = test_plan_job_parameters_dto_instance.to_dict()
# create an instance of TestPlanJobParametersDto from a dict
test_plan_job_parameters_dto_from_dict = TestPlanJobParametersDto.from_dict(test_plan_job_parameters_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


