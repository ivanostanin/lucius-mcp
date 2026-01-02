# TestResultAttachmentStepDtoAllOfAttachment


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**content_length** | **int** |  | [optional] 
**content_type** | **str** |  | [optional] 
**entity** | **str** |  | 
**id** | **int** |  | [optional] 
**name** | **str** |  | [optional] 
**var_base64** | **str** |  | [optional] 
**html_table** | **str** |  | [optional] 
**missed** | **bool** |  | [optional] 
**text_content** | **str** |  | [optional] 
**from_test_case** | **bool** |  | [optional] 
**storage_key** | **str** |  | [optional] 

## Example

```python
from src.client.generated.models.test_result_attachment_step_dto_all_of_attachment import TestResultAttachmentStepDtoAllOfAttachment

# TODO update the JSON string below
json = "{}"
# create an instance of TestResultAttachmentStepDtoAllOfAttachment from a JSON string
test_result_attachment_step_dto_all_of_attachment_instance = TestResultAttachmentStepDtoAllOfAttachment.from_json(json)
# print the JSON string representation of the object
print(TestResultAttachmentStepDtoAllOfAttachment.to_json())

# convert the object into a dict
test_result_attachment_step_dto_all_of_attachment_dict = test_result_attachment_step_dto_all_of_attachment_instance.to_dict()
# create an instance of TestResultAttachmentStepDtoAllOfAttachment from a dict
test_result_attachment_step_dto_all_of_attachment_from_dict = TestResultAttachmentStepDtoAllOfAttachment.from_dict(test_result_attachment_step_dto_all_of_attachment_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


