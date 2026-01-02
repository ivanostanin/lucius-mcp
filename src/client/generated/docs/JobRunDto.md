# JobRunDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**created_by** | **str** |  | [optional] 
**created_date** | **int** |  | [optional] 
**error_message** | **str** |  | [optional] 
**external_id** | **str** |  | [optional] 
**id** | **int** |  | [optional] 
**job** | [**JobInfoDto**](JobInfoDto.md) |  | [optional] 
**last_modified_by** | **str** |  | [optional] 
**last_modified_date** | **int** |  | [optional] 
**launch_id** | **int** |  | [optional] 
**name** | **str** |  | [optional] 
**stage** | [**JobRunStageDto**](JobRunStageDto.md) |  | [optional] 
**status** | [**JobRunStatusDto**](JobRunStatusDto.md) |  | [optional] 
**url** | **str** |  | [optional] 

## Example

```python
from src.client.generated.models.job_run_dto import JobRunDto

# TODO update the JSON string below
json = "{}"
# create an instance of JobRunDto from a JSON string
job_run_dto_instance = JobRunDto.from_json(json)
# print the JSON string representation of the object
print(JobRunDto.to_json())

# convert the object into a dict
job_run_dto_dict = job_run_dto_instance.to_dict()
# create an instance of JobRunDto from a dict
job_run_dto_from_dict = JobRunDto.from_dict(job_run_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


