# UploadTestFixtureResultDtoStepsInner


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**type** | **str** |  | 
**attachment** | [**UploadAttachmentDto**](UploadAttachmentDto.md) |  | [optional] 
**duration** | **int** |  | [optional] 
**start** | **int** |  | [optional] 
**status** | [**UploadTestStatus**](UploadTestStatus.md) |  | [optional] 
**stop** | **int** |  | [optional] 
**body** | **str** |  | [optional] 
**body_json** | [**DefaultTextMarkupDocument**](DefaultTextMarkupDocument.md) |  | [optional] 
**message** | **str** |  | [optional] 
**parameters** | [**List[UploadParameterDto]**](UploadParameterDto.md) |  | [optional] 
**trace** | **str** |  | [optional] 

## Example

```python
from src.client.generated.models.upload_test_fixture_result_dto_steps_inner import UploadTestFixtureResultDtoStepsInner

# TODO update the JSON string below
json = "{}"
# create an instance of UploadTestFixtureResultDtoStepsInner from a JSON string
upload_test_fixture_result_dto_steps_inner_instance = UploadTestFixtureResultDtoStepsInner.from_json(json)
# print the JSON string representation of the object
print(UploadTestFixtureResultDtoStepsInner.to_json())

# convert the object into a dict
upload_test_fixture_result_dto_steps_inner_dict = upload_test_fixture_result_dto_steps_inner_instance.to_dict()
# create an instance of UploadTestFixtureResultDtoStepsInner from a dict
upload_test_fixture_result_dto_steps_inner_from_dict = UploadTestFixtureResultDtoStepsInner.from_dict(upload_test_fixture_result_dto_steps_inner_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


