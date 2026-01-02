# LaunchExistingUploadDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**env_var_values** | [**List[EnvVarValueDto]**](EnvVarValueDto.md) |  | [optional] 

## Example

```python
from src.client.generated.models.launch_existing_upload_dto import LaunchExistingUploadDto

# TODO update the JSON string below
json = "{}"
# create an instance of LaunchExistingUploadDto from a JSON string
launch_existing_upload_dto_instance = LaunchExistingUploadDto.from_json(json)
# print the JSON string representation of the object
print(LaunchExistingUploadDto.to_json())

# convert the object into a dict
launch_existing_upload_dto_dict = launch_existing_upload_dto_instance.to_dict()
# create an instance of LaunchExistingUploadDto from a dict
launch_existing_upload_dto_from_dict = LaunchExistingUploadDto.from_dict(launch_existing_upload_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


