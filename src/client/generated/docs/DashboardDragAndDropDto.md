# DashboardDragAndDropDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**after_id** | **int** |  | [optional] 
**before_id** | **int** |  | [optional] 

## Example

```python
from src.client.generated.models.dashboard_drag_and_drop_dto import DashboardDragAndDropDto

# TODO update the JSON string below
json = "{}"
# create an instance of DashboardDragAndDropDto from a JSON string
dashboard_drag_and_drop_dto_instance = DashboardDragAndDropDto.from_json(json)
# print the JSON string representation of the object
print(DashboardDragAndDropDto.to_json())

# convert the object into a dict
dashboard_drag_and_drop_dto_dict = dashboard_drag_and_drop_dto_instance.to_dict()
# create an instance of DashboardDragAndDropDto from a dict
dashboard_drag_and_drop_dto_from_dict = DashboardDragAndDropDto.from_dict(dashboard_drag_and_drop_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


