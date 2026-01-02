# LaunchUploadResponseDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**files_count** | **int** |  | [optional] 
**launch_id** | **int** |  | [optional] 
**test_session_id** | **int** |  | [optional] 

## Example

```python
from src.client.generated.models.launch_upload_response_dto import LaunchUploadResponseDto

# TODO update the JSON string below
json = "{}"
# create an instance of LaunchUploadResponseDto from a JSON string
launch_upload_response_dto_instance = LaunchUploadResponseDto.from_json(json)
# print the JSON string representation of the object
print(LaunchUploadResponseDto.to_json())

# convert the object into a dict
launch_upload_response_dto_dict = launch_upload_response_dto_instance.to_dict()
# create an instance of LaunchUploadResponseDto from a dict
launch_upload_response_dto_from_dict = LaunchUploadResponseDto.from_dict(launch_upload_response_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


