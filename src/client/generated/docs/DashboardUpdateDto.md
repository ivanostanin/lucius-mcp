# DashboardUpdateDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** |  | [optional] 
**template_id** | **int** |  | [optional] 

## Example

```python
from src.client.generated.models.dashboard_update_dto import DashboardUpdateDto

# TODO update the JSON string below
json = "{}"
# create an instance of DashboardUpdateDto from a JSON string
dashboard_update_dto_instance = DashboardUpdateDto.from_json(json)
# print the JSON string representation of the object
print(DashboardUpdateDto.to_json())

# convert the object into a dict
dashboard_update_dto_dict = dashboard_update_dto_instance.to_dict()
# create an instance of DashboardUpdateDto from a dict
dashboard_update_dto_from_dict = DashboardUpdateDto.from_dict(dashboard_update_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


