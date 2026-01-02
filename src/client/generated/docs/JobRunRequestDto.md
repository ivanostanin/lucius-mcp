# JobRunRequestDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**env_var_value_sets** | [**List[EnvironmentSetDto]**](EnvironmentSetDto.md) |  | [optional] 
**issues** | [**List[IssueDto]**](IssueDto.md) |  | [optional] 
**launch_name** | **str** |  | 
**links** | [**List[ExternalLinkDto]**](ExternalLinkDto.md) |  | [optional] 
**parameters** | [**List[JobParameterDto]**](JobParameterDto.md) |  | [optional] 
**selection** | [**TreeSelectionDto**](TreeSelectionDto.md) |  | [optional] 
**tags** | [**List[LaunchTagDto]**](LaunchTagDto.md) |  | [optional] 

## Example

```python
from src.client.generated.models.job_run_request_dto import JobRunRequestDto

# TODO update the JSON string below
json = "{}"
# create an instance of JobRunRequestDto from a JSON string
job_run_request_dto_instance = JobRunRequestDto.from_json(json)
# print the JSON string representation of the object
print(JobRunRequestDto.to_json())

# convert the object into a dict
job_run_request_dto_dict = job_run_request_dto_instance.to_dict()
# create an instance of JobRunRequestDto from a dict
job_run_request_dto_from_dict = JobRunRequestDto.from_dict(job_run_request_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


