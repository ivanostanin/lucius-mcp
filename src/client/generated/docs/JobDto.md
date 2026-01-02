# JobDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **int** |  | [optional] 
**name** | **str** |  | [optional] 
**parameters** | [**List[JobParameterDto]**](JobParameterDto.md) |  | [optional] 
**type** | [**IntegrationTypeDto**](IntegrationTypeDto.md) |  | [optional] 
**url** | **str** |  | [optional] 

## Example

```python
from src.client.generated.models.job_dto import JobDto

# TODO update the JSON string below
json = "{}"
# create an instance of JobDto from a JSON string
job_dto_instance = JobDto.from_json(json)
# print the JSON string representation of the object
print(JobDto.to_json())

# convert the object into a dict
job_dto_dict = job_dto_instance.to_dict()
# create an instance of JobDto from a dict
job_dto_from_dict = JobDto.from_dict(job_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


