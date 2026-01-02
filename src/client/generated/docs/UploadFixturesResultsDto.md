# UploadFixturesResultsDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**fixtures** | [**List[UploadTestFixtureResultDto]**](UploadTestFixtureResultDto.md) |  | [optional] 

## Example

```python
from src.client.generated.models.upload_fixtures_results_dto import UploadFixturesResultsDto

# TODO update the JSON string below
json = "{}"
# create an instance of UploadFixturesResultsDto from a JSON string
upload_fixtures_results_dto_instance = UploadFixturesResultsDto.from_json(json)
# print the JSON string representation of the object
print(UploadFixturesResultsDto.to_json())

# convert the object into a dict
upload_fixtures_results_dto_dict = upload_fixtures_results_dto_instance.to_dict()
# create an instance of UploadFixturesResultsDto from a dict
upload_fixtures_results_dto_from_dict = UploadFixturesResultsDto.from_dict(upload_fixtures_results_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


