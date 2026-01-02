# ProjectSyncRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**aql** | **str** |  | 
**fields** | **object** |  | 
**integration_id** | **int** |  | 
**project_id** | **int** |  | 
**project_key** | **str** |  | 
**sync_only_existing** | **bool** |  | 
**test_type_id** | **str** |  | 

## Example

```python
from src.client.generated.models.project_sync_request import ProjectSyncRequest

# TODO update the JSON string below
json = "{}"
# create an instance of ProjectSyncRequest from a JSON string
project_sync_request_instance = ProjectSyncRequest.from_json(json)
# print the JSON string representation of the object
print(ProjectSyncRequest.to_json())

# convert the object into a dict
project_sync_request_dict = project_sync_request_instance.to_dict()
# create an instance of ProjectSyncRequest from a dict
project_sync_request_from_dict = ProjectSyncRequest.from_dict(project_sync_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


