# JobRunUploadInfoDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**env_var_values** | [**List[EnvVarValueDto]**](EnvVarValueDto.md) |  | [optional] 

## Example

```python
from src.client.generated.models.job_run_upload_info_dto import JobRunUploadInfoDto

# TODO update the JSON string below
json = "{}"
# create an instance of JobRunUploadInfoDto from a JSON string
job_run_upload_info_dto_instance = JobRunUploadInfoDto.from_json(json)
# print the JSON string representation of the object
print(JobRunUploadInfoDto.to_json())

# convert the object into a dict
job_run_upload_info_dto_dict = job_run_upload_info_dto_instance.to_dict()
# create an instance of JobRunUploadInfoDto from a dict
job_run_upload_info_dto_from_dict = JobRunUploadInfoDto.from_dict(job_run_upload_info_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


