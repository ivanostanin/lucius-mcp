# DashboardPatchDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** |  | [optional] 

## Example

```python
from src.client.generated.models.dashboard_patch_dto import DashboardPatchDto

# TODO update the JSON string below
json = "{}"
# create an instance of DashboardPatchDto from a JSON string
dashboard_patch_dto_instance = DashboardPatchDto.from_json(json)
# print the JSON string representation of the object
print(DashboardPatchDto.to_json())

# convert the object into a dict
dashboard_patch_dto_dict = dashboard_patch_dto_instance.to_dict()
# create an instance of DashboardPatchDto from a dict
dashboard_patch_dto_from_dict = DashboardPatchDto.from_dict(dashboard_patch_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


