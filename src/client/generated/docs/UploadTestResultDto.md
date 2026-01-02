# UploadTestResultDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**attachments** | [**List[UploadAttachmentDto]**](UploadAttachmentDto.md) |  | [optional] 
**description** | **str** |  | [optional] 
**description_html** | **str** |  | [optional] 
**duration** | **int** |  | [optional] 
**expected_result** | **str** |  | [optional] 
**expected_result_html** | **str** |  | [optional] 
**flaky** | **bool** |  | [optional] 
**full_name** | **str** |  | [optional] 
**hidden** | **bool** |  | [optional] 
**history_id** | **str** |  | [optional] 
**host_id** | **str** |  | [optional] 
**known** | **bool** |  | [optional] 
**labels** | [**List[UploadLabelDto]**](UploadLabelDto.md) |  | [optional] 
**links** | [**List[UploadLinkDto]**](UploadLinkDto.md) |  | [optional] 
**message** | **str** |  | [optional] 
**muted** | **bool** |  | [optional] 
**name** | **str** |  | [optional] 
**parameters** | [**List[UploadParameterDto]**](UploadParameterDto.md) |  | [optional] 
**precondition** | **str** |  | [optional] 
**precondition_html** | **str** |  | [optional] 
**start** | **int** |  | [optional] 
**status** | [**UploadTestStatus**](UploadTestStatus.md) |  | [optional] 
**steps** | [**List[UploadTestFixtureResultDtoStepsInner]**](UploadTestFixtureResultDtoStepsInner.md) |  | [optional] 
**stop** | **int** |  | [optional] 
**test_case_id** | **str** |  | [optional] 
**thread_id** | **str** |  | [optional] 
**trace** | **str** |  | [optional] 
**uuid** | **str** |  | [optional] 

## Example

```python
from src.client.generated.models.upload_test_result_dto import UploadTestResultDto

# TODO update the JSON string below
json = "{}"
# create an instance of UploadTestResultDto from a JSON string
upload_test_result_dto_instance = UploadTestResultDto.from_json(json)
# print the JSON string representation of the object
print(UploadTestResultDto.to_json())

# convert the object into a dict
upload_test_result_dto_dict = upload_test_result_dto_instance.to_dict()
# create an instance of UploadTestResultDto from a dict
upload_test_result_dto_from_dict = UploadTestResultDto.from_dict(upload_test_result_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


