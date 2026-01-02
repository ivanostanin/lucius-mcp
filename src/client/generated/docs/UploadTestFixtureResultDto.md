# UploadTestFixtureResultDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**duration** | **int** |  | [optional] 
**message** | **str** |  | [optional] 
**name** | **str** |  | [optional] 
**start** | **int** |  | [optional] 
**status** | [**UploadTestStatus**](UploadTestStatus.md) |  | [optional] 
**steps** | [**List[UploadTestFixtureResultDtoStepsInner]**](UploadTestFixtureResultDtoStepsInner.md) |  | [optional] 
**stop** | **int** |  | [optional] 
**trace** | **str** |  | [optional] 
**type** | [**UploadTestFixtureType**](UploadTestFixtureType.md) |  | [optional] 

## Example

```python
from src.client.generated.models.upload_test_fixture_result_dto import UploadTestFixtureResultDto

# TODO update the JSON string below
json = "{}"
# create an instance of UploadTestFixtureResultDto from a JSON string
upload_test_fixture_result_dto_instance = UploadTestFixtureResultDto.from_json(json)
# print the JSON string representation of the object
print(UploadTestFixtureResultDto.to_json())

# convert the object into a dict
upload_test_fixture_result_dto_dict = upload_test_fixture_result_dto_instance.to_dict()
# create an instance of UploadTestFixtureResultDto from a dict
upload_test_fixture_result_dto_from_dict = UploadTestFixtureResultDto.from_dict(upload_test_fixture_result_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


