# TestSessionResponseDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **int** |  | [optional] 
**job_id** | **int** |  | [optional] 
**job_run_id** | **int** |  | [optional] 
**launch_id** | **int** |  | [optional] 
**project_id** | **int** |  | [optional] 

## Example

```python
from src.client.generated.models.test_session_response_dto import TestSessionResponseDto

# TODO update the JSON string below
json = "{}"
# create an instance of TestSessionResponseDto from a JSON string
test_session_response_dto_instance = TestSessionResponseDto.from_json(json)
# print the JSON string representation of the object
print(TestSessionResponseDto.to_json())

# convert the object into a dict
test_session_response_dto_dict = test_session_response_dto_instance.to_dict()
# create an instance of TestSessionResponseDto from a dict
test_session_response_dto_from_dict = TestSessionResponseDto.from_dict(test_session_response_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


