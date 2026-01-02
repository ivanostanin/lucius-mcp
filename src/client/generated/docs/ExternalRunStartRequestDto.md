# ExternalRunStartRequestDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**ci** | [**Ci**](Ci.md) |  | [optional] 
**job** | [**Job**](Job.md) |  | [optional] 
**job_run** | [**JobRun**](JobRun.md) |  | 
**launch** | [**Launch**](Launch.md) |  | [optional] 
**project_id** | **int** |  | [optional] 

## Example

```python
from src.client.generated.models.external_run_start_request_dto import ExternalRunStartRequestDto

# TODO update the JSON string below
json = "{}"
# create an instance of ExternalRunStartRequestDto from a JSON string
external_run_start_request_dto_instance = ExternalRunStartRequestDto.from_json(json)
# print the JSON string representation of the object
print(ExternalRunStartRequestDto.to_json())

# convert the object into a dict
external_run_start_request_dto_dict = external_run_start_request_dto_instance.to_dict()
# create an instance of ExternalRunStartRequestDto from a dict
external_run_start_request_dto_from_dict = ExternalRunStartRequestDto.from_dict(external_run_start_request_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


