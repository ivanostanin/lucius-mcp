# TestCaseAttachmentRowDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**var_base64** | **str** |  | [optional] 
**html_table** | **str** |  | [optional] 
**missed** | **bool** |  | [optional] 
**text_content** | **str** |  | [optional] 

## Example

```python
from src.client.generated.models.test_case_attachment_row_dto import TestCaseAttachmentRowDto

# TODO update the JSON string below
json = "{}"
# create an instance of TestCaseAttachmentRowDto from a JSON string
test_case_attachment_row_dto_instance = TestCaseAttachmentRowDto.from_json(json)
# print the JSON string representation of the object
print(TestCaseAttachmentRowDto.to_json())

# convert the object into a dict
test_case_attachment_row_dto_dict = test_case_attachment_row_dto_instance.to_dict()
# create an instance of TestCaseAttachmentRowDto from a dict
test_case_attachment_row_dto_from_dict = TestCaseAttachmentRowDto.from_dict(test_case_attachment_row_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


