# DashboardOverviewDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**created_date** | **int** |  | [optional] 
**id** | **int** |  | [optional] 
**last_modified_date** | **int** |  | [optional] 
**name** | **str** |  | [optional] 
**project_id** | **int** |  | [optional] 
**sort_order** | **int** |  | [optional] 
**widgets** | [**List[WidgetDto]**](WidgetDto.md) |  | [optional] 

## Example

```python
from src.client.generated.models.dashboard_overview_dto import DashboardOverviewDto

# TODO update the JSON string below
json = "{}"
# create an instance of DashboardOverviewDto from a JSON string
dashboard_overview_dto_instance = DashboardOverviewDto.from_json(json)
# print the JSON string representation of the object
print(DashboardOverviewDto.to_json())

# convert the object into a dict
dashboard_overview_dto_dict = dashboard_overview_dto_instance.to_dict()
# create an instance of DashboardOverviewDto from a dict
dashboard_overview_dto_from_dict = DashboardOverviewDto.from_dict(dashboard_overview_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


