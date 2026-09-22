# LaunchAttachmentRowDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **int** |  | [optional] 
**name** | **str** |  | [optional] 
**content_type** | **str** |  | [optional] 
**content_length** | **int** |  | [optional] 
**entity** | **str** |  | [optional] 

## Example

```python
from src.client.generated.models.launch_attachment_row_dto import LaunchAttachmentRowDto

# TODO update the JSON string below
json = "{}"
# create an instance of LaunchAttachmentRowDto from a JSON string
launch_attachment_row_dto_instance = LaunchAttachmentRowDto.from_json(json)
# print the JSON string representation of the object
print(LaunchAttachmentRowDto.to_json())

# convert the object into a dict
launch_attachment_row_dto_dict = launch_attachment_row_dto_instance.to_dict()
# create an instance of LaunchAttachmentRowDto from a dict
launch_attachment_row_dto_from_dict = LaunchAttachmentRowDto.from_dict(launch_attachment_row_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


