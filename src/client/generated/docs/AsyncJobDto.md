# AsyncJobDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**created_date** | **int** |  | [optional] 
**id** | **int** |  | [optional] 
**last_modified_date** | **int** |  | [optional] 
**name** | **str** |  | [optional] 
**status** | [**AsyncJobStatusDto**](AsyncJobStatusDto.md) |  | [optional] 

## Example

```python
from src.client.generated.models.async_job_dto import AsyncJobDto

# TODO update the JSON string below
json = "{}"
# create an instance of AsyncJobDto from a JSON string
async_job_dto_instance = AsyncJobDto.from_json(json)
# print the JSON string representation of the object
print(AsyncJobDto.to_json())

# convert the object into a dict
async_job_dto_dict = async_job_dto_instance.to_dict()
# create an instance of AsyncJobDto from a dict
async_job_dto_from_dict = AsyncJobDto.from_dict(async_job_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


