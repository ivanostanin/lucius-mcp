# UploadResultsDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**results** | [**List[UploadTestResultDto]**](UploadTestResultDto.md) |  | [optional] 
**test_session_id** | **int** |  | 

## Example

```python
from src.client.generated.models.upload_results_dto import UploadResultsDto

# TODO update the JSON string below
json = "{}"
# create an instance of UploadResultsDto from a JSON string
upload_results_dto_instance = UploadResultsDto.from_json(json)
# print the JSON string representation of the object
print(UploadResultsDto.to_json())

# convert the object into a dict
upload_results_dto_dict = upload_results_dto_instance.to_dict()
# create an instance of UploadResultsDto from a dict
upload_results_dto_from_dict = UploadResultsDto.from_dict(upload_results_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


