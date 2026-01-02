# AsyncJobWithStepsDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**created_date** | **int** |  | [optional] 
**id** | **int** |  | [optional] 
**last_modified_date** | **int** |  | [optional] 
**name** | **str** |  | [optional] 
**status** | [**AsyncJobStatusDto**](AsyncJobStatusDto.md) |  | [optional] 
**steps** | [**List[AsyncJobStepDto]**](AsyncJobStepDto.md) |  | [optional] 

## Example

```python
from src.client.generated.models.async_job_with_steps_dto import AsyncJobWithStepsDto

# TODO update the JSON string below
json = "{}"
# create an instance of AsyncJobWithStepsDto from a JSON string
async_job_with_steps_dto_instance = AsyncJobWithStepsDto.from_json(json)
# print the JSON string representation of the object
print(AsyncJobWithStepsDto.to_json())

# convert the object into a dict
async_job_with_steps_dto_dict = async_job_with_steps_dto_instance.to_dict()
# create an instance of AsyncJobWithStepsDto from a dict
async_job_with_steps_dto_from_dict = AsyncJobWithStepsDto.from_dict(async_job_with_steps_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


