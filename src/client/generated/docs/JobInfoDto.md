# JobInfoDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **int** |  | [optional] 
**name** | **str** |  | [optional] 
**type** | [**IntegrationTypeDto**](IntegrationTypeDto.md) |  | [optional] 
**url** | **str** |  | [optional] 

## Example

```python
from src.client.generated.models.job_info_dto import JobInfoDto

# TODO update the JSON string below
json = "{}"
# create an instance of JobInfoDto from a JSON string
job_info_dto_instance = JobInfoDto.from_json(json)
# print the JSON string representation of the object
print(JobInfoDto.to_json())

# convert the object into a dict
job_info_dto_dict = job_info_dto_instance.to_dict()
# create an instance of JobInfoDto from a dict
job_info_dto_from_dict = JobInfoDto.from_dict(job_info_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


