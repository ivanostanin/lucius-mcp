# FileUploadResponseDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**files_count** | **int** |  | [optional] 

## Example

```python
from src.client.generated.models.file_upload_response_dto import FileUploadResponseDto

# TODO update the JSON string below
json = "{}"
# create an instance of FileUploadResponseDto from a JSON string
file_upload_response_dto_instance = FileUploadResponseDto.from_json(json)
# print the JSON string representation of the object
print(FileUploadResponseDto.to_json())

# convert the object into a dict
file_upload_response_dto_dict = file_upload_response_dto_instance.to_dict()
# create an instance of FileUploadResponseDto from a dict
file_upload_response_dto_from_dict = FileUploadResponseDto.from_dict(file_upload_response_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


