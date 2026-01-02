# TestResultAttachmentStepDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**attachment** | [**TestResultAttachmentStepDtoAllOfAttachment**](TestResultAttachmentStepDtoAllOfAttachment.md) |  | [optional] 
**attachment_id** | **int** |  | [optional] 
**duration** | **int** |  | [optional] 
**start** | **int** |  | [optional] 
**status** | [**TestStatus**](TestStatus.md) |  | [optional] 
**stop** | **int** |  | [optional] 

## Example

```python
from src.client.generated.models.test_result_attachment_step_dto import TestResultAttachmentStepDto

# TODO update the JSON string below
json = "{}"
# create an instance of TestResultAttachmentStepDto from a JSON string
test_result_attachment_step_dto_instance = TestResultAttachmentStepDto.from_json(json)
# print the JSON string representation of the object
print(TestResultAttachmentStepDto.to_json())

# convert the object into a dict
test_result_attachment_step_dto_dict = test_result_attachment_step_dto_instance.to_dict()
# create an instance of TestResultAttachmentStepDto from a dict
test_result_attachment_step_dto_from_dict = TestResultAttachmentStepDto.from_dict(test_result_attachment_step_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


