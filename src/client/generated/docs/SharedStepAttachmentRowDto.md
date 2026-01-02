# SharedStepAttachmentRowDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**content_length** | **int** |  | [optional] 
**content_type** | **str** |  | [optional] 
**id** | **int** |  | [optional] 
**missed** | **bool** |  | [optional] 
**name** | **str** |  | [optional] 

## Example

```python
from src.client.generated.models.shared_step_attachment_row_dto import SharedStepAttachmentRowDto

# TODO update the JSON string below
json = "{}"
# create an instance of SharedStepAttachmentRowDto from a JSON string
shared_step_attachment_row_dto_instance = SharedStepAttachmentRowDto.from_json(json)
# print the JSON string representation of the object
print(SharedStepAttachmentRowDto.to_json())

# convert the object into a dict
shared_step_attachment_row_dto_dict = shared_step_attachment_row_dto_instance.to_dict()
# create an instance of SharedStepAttachmentRowDto from a dict
shared_step_attachment_row_dto_from_dict = SharedStepAttachmentRowDto.from_dict(shared_step_attachment_row_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


