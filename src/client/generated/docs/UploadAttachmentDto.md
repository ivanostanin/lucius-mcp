# UploadAttachmentDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**content_length** | **int** |  | [optional] 
**content_type** | **str** |  | [optional] 
**name** | **str** |  | [optional] 
**optional** | **bool** |  | [optional] 
**original_file_name** | **str** |  | [optional] 

## Example

```python
from src.client.generated.models.upload_attachment_dto import UploadAttachmentDto

# TODO update the JSON string below
json = "{}"
# create an instance of UploadAttachmentDto from a JSON string
upload_attachment_dto_instance = UploadAttachmentDto.from_json(json)
# print the JSON string representation of the object
print(UploadAttachmentDto.to_json())

# convert the object into a dict
upload_attachment_dto_dict = upload_attachment_dto_instance.to_dict()
# create an instance of UploadAttachmentDto from a dict
upload_attachment_dto_from_dict = UploadAttachmentDto.from_dict(upload_attachment_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


