# DashboardCreateDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** |  | [optional] 
**project_id** | **int** |  | 
**template_id** | **int** |  | [optional] 

## Example

```python
from src.client.generated.models.dashboard_create_dto import DashboardCreateDto

# TODO update the JSON string below
json = "{}"
# create an instance of DashboardCreateDto from a JSON string
dashboard_create_dto_instance = DashboardCreateDto.from_json(json)
# print the JSON string representation of the object
print(DashboardCreateDto.to_json())

# convert the object into a dict
dashboard_create_dto_dict = dashboard_create_dto_instance.to_dict()
# create an instance of DashboardCreateDto from a dict
dashboard_create_dto_from_dict = DashboardCreateDto.from_dict(dashboard_create_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


