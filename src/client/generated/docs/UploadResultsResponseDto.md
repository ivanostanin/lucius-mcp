# UploadResultsResponseDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**result_ids** | **List[int]** |  | [optional] 

## Example

```python
from src.client.generated.models.upload_results_response_dto import UploadResultsResponseDto

# TODO update the JSON string below
json = "{}"
# create an instance of UploadResultsResponseDto from a JSON string
upload_results_response_dto_instance = UploadResultsResponseDto.from_json(json)
# print the JSON string representation of the object
print(UploadResultsResponseDto.to_json())

# convert the object into a dict
upload_results_response_dto_dict = upload_results_response_dto_instance.to_dict()
# create an instance of UploadResultsResponseDto from a dict
upload_results_response_dto_from_dict = UploadResultsResponseDto.from_dict(upload_results_response_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


