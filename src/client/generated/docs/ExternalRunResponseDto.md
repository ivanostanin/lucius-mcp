# ExternalRunResponseDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**job_id** | **int** |  | [optional] 
**job_run_id** | **int** |  | [optional] 
**launch_id** | **int** |  | [optional] 
**project_id** | **int** |  | [optional] 

## Example

```python
from src.client.generated.models.external_run_response_dto import ExternalRunResponseDto

# TODO update the JSON string below
json = "{}"
# create an instance of ExternalRunResponseDto from a JSON string
external_run_response_dto_instance = ExternalRunResponseDto.from_json(json)
# print the JSON string representation of the object
print(ExternalRunResponseDto.to_json())

# convert the object into a dict
external_run_response_dto_dict = external_run_response_dto_instance.to_dict()
# create an instance of ExternalRunResponseDto from a dict
external_run_response_dto_from_dict = ExternalRunResponseDto.from_dict(external_run_response_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


