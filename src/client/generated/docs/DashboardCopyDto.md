# DashboardCopyDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** |  | [optional] 
**preserve_widget_aql** | **bool** |  | 
**project_id** | **int** |  | [optional] 

## Example

```python
from src.client.generated.models.dashboard_copy_dto import DashboardCopyDto

# TODO update the JSON string below
json = "{}"
# create an instance of DashboardCopyDto from a JSON string
dashboard_copy_dto_instance = DashboardCopyDto.from_json(json)
# print the JSON string representation of the object
print(DashboardCopyDto.to_json())

# convert the object into a dict
dashboard_copy_dto_dict = dashboard_copy_dto_instance.to_dict()
# create an instance of DashboardCopyDto from a dict
dashboard_copy_dto_from_dict = DashboardCopyDto.from_dict(dashboard_copy_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


