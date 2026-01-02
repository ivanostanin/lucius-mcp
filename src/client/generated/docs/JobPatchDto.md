# JobPatchDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**can_run** | **bool** |  | [optional] 
**integration_id** | **int** |  | [optional] 
**name** | **str** |  | [optional] 
**parameters** | [**List[JobParameterDto]**](JobParameterDto.md) |  | [optional] 

## Example

```python
from src.client.generated.models.job_patch_dto import JobPatchDto

# TODO update the JSON string below
json = "{}"
# create an instance of JobPatchDto from a JSON string
job_patch_dto_instance = JobPatchDto.from_json(json)
# print the JSON string representation of the object
print(JobPatchDto.to_json())

# convert the object into a dict
job_patch_dto_dict = job_patch_dto_instance.to_dict()
# create an instance of JobPatchDto from a dict
job_patch_dto_from_dict = JobPatchDto.from_dict(job_patch_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


