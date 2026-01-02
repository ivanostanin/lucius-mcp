# AsyncJobStepDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**context** | **Dict[str, object]** |  | [optional] 
**created_date** | **int** |  | [optional] 
**id** | **int** |  | [optional] 
**job_id** | **int** |  | [optional] 
**last_modified_date** | **int** |  | [optional] 
**name** | **str** |  | [optional] 
**status** | [**AsyncJobStepStatusDto**](AsyncJobStepStatusDto.md) |  | [optional] 

## Example

```python
from src.client.generated.models.async_job_step_dto import AsyncJobStepDto

# TODO update the JSON string below
json = "{}"
# create an instance of AsyncJobStepDto from a JSON string
async_job_step_dto_instance = AsyncJobStepDto.from_json(json)
# print the JSON string representation of the object
print(AsyncJobStepDto.to_json())

# convert the object into a dict
async_job_step_dto_dict = async_job_step_dto_instance.to_dict()
# create an instance of AsyncJobStepDto from a dict
async_job_step_dto_from_dict = AsyncJobStepDto.from_dict(async_job_step_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


