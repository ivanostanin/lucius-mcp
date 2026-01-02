# LaunchCleanupRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**launch_ids** | **List[int]** |  | 
**statuses** | [**List[TestStatus]**](TestStatus.md) |  | 
**targets** | [**List[CleanerSchemaTargetDto]**](CleanerSchemaTargetDto.md) |  | 

## Example

```python
from src.client.generated.models.launch_cleanup_request import LaunchCleanupRequest

# TODO update the JSON string below
json = "{}"
# create an instance of LaunchCleanupRequest from a JSON string
launch_cleanup_request_instance = LaunchCleanupRequest.from_json(json)
# print the JSON string representation of the object
print(LaunchCleanupRequest.to_json())

# convert the object into a dict
launch_cleanup_request_dict = launch_cleanup_request_instance.to_dict()
# create an instance of LaunchCleanupRequest from a dict
launch_cleanup_request_from_dict = LaunchCleanupRequest.from_dict(launch_cleanup_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


