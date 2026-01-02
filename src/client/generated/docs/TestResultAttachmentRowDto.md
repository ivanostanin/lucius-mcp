# TestResultAttachmentRowDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**from_test_case** | **bool** |  | [optional] 
**missed** | **bool** |  | [optional] 
**storage_key** | **str** |  | [optional] 

## Example

```python
from src.client.generated.models.test_result_attachment_row_dto import TestResultAttachmentRowDto

# TODO update the JSON string below
json = "{}"
# create an instance of TestResultAttachmentRowDto from a JSON string
test_result_attachment_row_dto_instance = TestResultAttachmentRowDto.from_json(json)
# print the JSON string representation of the object
print(TestResultAttachmentRowDto.to_json())

# convert the object into a dict
test_result_attachment_row_dto_dict = test_result_attachment_row_dto_instance.to_dict()
# create an instance of TestResultAttachmentRowDto from a dict
test_result_attachment_row_dto_from_dict = TestResultAttachmentRowDto.from_dict(test_result_attachment_row_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


