# UploadTestResultAttachmentStepDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**attachment** | [**UploadAttachmentDto**](UploadAttachmentDto.md) |  | [optional] 
**duration** | **int** |  | [optional] 
**start** | **int** |  | [optional] 
**status** | [**UploadTestStatus**](UploadTestStatus.md) |  | [optional] 
**stop** | **int** |  | [optional] 

## Example

```python
from src.client.generated.models.upload_test_result_attachment_step_dto import UploadTestResultAttachmentStepDto

# TODO update the JSON string below
json = "{}"
# create an instance of UploadTestResultAttachmentStepDto from a JSON string
upload_test_result_attachment_step_dto_instance = UploadTestResultAttachmentStepDto.from_json(json)
# print the JSON string representation of the object
print(UploadTestResultAttachmentStepDto.to_json())

# convert the object into a dict
upload_test_result_attachment_step_dto_dict = upload_test_result_attachment_step_dto_instance.to_dict()
# create an instance of UploadTestResultAttachmentStepDto from a dict
upload_test_result_attachment_step_dto_from_dict = UploadTestResultAttachmentStepDto.from_dict(upload_test_result_attachment_step_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


