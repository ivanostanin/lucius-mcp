# DashboardDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**created_date** | **int** |  | [optional] 
**id** | **int** |  | [optional] 
**last_modified_date** | **int** |  | [optional] 
**name** | **str** |  | [optional] 
**project_id** | **int** |  | [optional] 
**sort_order** | **int** |  | [optional] 

## Example

```python
from src.client.generated.models.dashboard_dto import DashboardDto

# TODO update the JSON string below
json = "{}"
# create an instance of DashboardDto from a JSON string
dashboard_dto_instance = DashboardDto.from_json(json)
# print the JSON string representation of the object
print(DashboardDto.to_json())

# convert the object into a dict
dashboard_dto_dict = dashboard_dto_instance.to_dict()
# create an instance of DashboardDto from a dict
dashboard_dto_from_dict = DashboardDto.from_dict(dashboard_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


