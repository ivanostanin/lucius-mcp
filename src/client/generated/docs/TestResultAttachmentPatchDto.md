# TestResultAttachmentPatchDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**content_type** | **str** |  | [optional] 
**name** | **str** |  | [optional] 

## Example

```python
from src.client.generated.models.test_result_attachment_patch_dto import TestResultAttachmentPatchDto

# TODO update the JSON string below
json = "{}"
# create an instance of TestResultAttachmentPatchDto from a JSON string
test_result_attachment_patch_dto_instance = TestResultAttachmentPatchDto.from_json(json)
# print the JSON string representation of the object
print(TestResultAttachmentPatchDto.to_json())

# convert the object into a dict
test_result_attachment_patch_dto_dict = test_result_attachment_patch_dto_instance.to_dict()
# create an instance of TestResultAttachmentPatchDto from a dict
test_result_attachment_patch_dto_from_dict = TestResultAttachmentPatchDto.from_dict(test_result_attachment_patch_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


