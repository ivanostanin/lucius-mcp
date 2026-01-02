# SharedStepAttachmentPatchDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**content_type** | **str** |  | [optional] 
**name** | **str** |  | [optional] 

## Example

```python
from src.client.generated.models.shared_step_attachment_patch_dto import SharedStepAttachmentPatchDto

# TODO update the JSON string below
json = "{}"
# create an instance of SharedStepAttachmentPatchDto from a JSON string
shared_step_attachment_patch_dto_instance = SharedStepAttachmentPatchDto.from_json(json)
# print the JSON string representation of the object
print(SharedStepAttachmentPatchDto.to_json())

# convert the object into a dict
shared_step_attachment_patch_dto_dict = shared_step_attachment_patch_dto_instance.to_dict()
# create an instance of SharedStepAttachmentPatchDto from a dict
shared_step_attachment_patch_dto_from_dict = SharedStepAttachmentPatchDto.from_dict(shared_step_attachment_patch_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


