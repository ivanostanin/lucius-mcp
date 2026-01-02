# UploadTestResultExpectedBodyStepDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**body** | **str** |  | [optional] 
**body_json** | [**DefaultTextMarkupDocument**](DefaultTextMarkupDocument.md) |  | [optional] 
**duration** | **int** |  | [optional] 
**message** | **str** |  | [optional] 
**start** | **int** |  | [optional] 
**status** | [**UploadTestStatus**](UploadTestStatus.md) |  | [optional] 
**stop** | **int** |  | [optional] 

## Example

```python
from src.client.generated.models.upload_test_result_expected_body_step_dto import UploadTestResultExpectedBodyStepDto

# TODO update the JSON string below
json = "{}"
# create an instance of UploadTestResultExpectedBodyStepDto from a JSON string
upload_test_result_expected_body_step_dto_instance = UploadTestResultExpectedBodyStepDto.from_json(json)
# print the JSON string representation of the object
print(UploadTestResultExpectedBodyStepDto.to_json())

# convert the object into a dict
upload_test_result_expected_body_step_dto_dict = upload_test_result_expected_body_step_dto_instance.to_dict()
# create an instance of UploadTestResultExpectedBodyStepDto from a dict
upload_test_result_expected_body_step_dto_from_dict = UploadTestResultExpectedBodyStepDto.from_dict(upload_test_result_expected_body_step_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


