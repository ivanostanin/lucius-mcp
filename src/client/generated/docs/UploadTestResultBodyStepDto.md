# UploadTestResultBodyStepDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**body** | **str** |  | [optional] 
**body_json** | [**DefaultTextMarkupDocument**](DefaultTextMarkupDocument.md) |  | [optional] 
**duration** | **int** |  | [optional] 
**message** | **str** |  | [optional] 
**parameters** | [**List[UploadParameterDto]**](UploadParameterDto.md) |  | [optional] 
**start** | **int** |  | [optional] 
**status** | [**UploadTestStatus**](UploadTestStatus.md) |  | [optional] 
**stop** | **int** |  | [optional] 
**trace** | **str** |  | [optional] 

## Example

```python
from src.client.generated.models.upload_test_result_body_step_dto import UploadTestResultBodyStepDto

# TODO update the JSON string below
json = "{}"
# create an instance of UploadTestResultBodyStepDto from a JSON string
upload_test_result_body_step_dto_instance = UploadTestResultBodyStepDto.from_json(json)
# print the JSON string representation of the object
print(UploadTestResultBodyStepDto.to_json())

# convert the object into a dict
upload_test_result_body_step_dto_dict = upload_test_result_body_step_dto_instance.to_dict()
# create an instance of UploadTestResultBodyStepDto from a dict
upload_test_result_body_step_dto_from_dict = UploadTestResultBodyStepDto.from_dict(upload_test_result_body_step_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


