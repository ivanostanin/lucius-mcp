# JobCreateDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**can_run** | **bool** |  | [optional] 
**external_id** | **str** |  | [optional] 
**integration_id** | **int** |  | 
**project_id** | **int** |  | 

## Example

```python
from src.client.generated.models.job_create_dto import JobCreateDto

# TODO update the JSON string below
json = "{}"
# create an instance of JobCreateDto from a JSON string
job_create_dto_instance = JobCreateDto.from_json(json)
# print the JSON string representation of the object
print(JobCreateDto.to_json())

# convert the object into a dict
job_create_dto_dict = job_create_dto_instance.to_dict()
# create an instance of JobCreateDto from a dict
job_create_dto_from_dict = JobCreateDto.from_dict(job_create_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


