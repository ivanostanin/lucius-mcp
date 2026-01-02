# JobRerunRequestDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**rql** | **str** |  | [optional] 

## Example

```python
from src.client.generated.models.job_rerun_request_dto import JobRerunRequestDto

# TODO update the JSON string below
json = "{}"
# create an instance of JobRerunRequestDto from a JSON string
job_rerun_request_dto_instance = JobRerunRequestDto.from_json(json)
# print the JSON string representation of the object
print(JobRerunRequestDto.to_json())

# convert the object into a dict
job_rerun_request_dto_dict = job_rerun_request_dto_instance.to_dict()
# create an instance of JobRerunRequestDto from a dict
job_rerun_request_dto_from_dict = JobRerunRequestDto.from_dict(job_rerun_request_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


