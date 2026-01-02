# WidgetPatchDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**grid_pos** | [**GridPosDto**](GridPosDto.md) |  | [optional] 
**name** | **str** |  | [optional] 
**options** | [**WidgetCreateDtoOptions**](WidgetCreateDtoOptions.md) |  | [optional] 
**type** | [**WidgetTypeDto**](WidgetTypeDto.md) |  | [optional] 

## Example

```python
from src.client.generated.models.widget_patch_dto import WidgetPatchDto

# TODO update the JSON string below
json = "{}"
# create an instance of WidgetPatchDto from a JSON string
widget_patch_dto_instance = WidgetPatchDto.from_json(json)
# print the JSON string representation of the object
print(WidgetPatchDto.to_json())

# convert the object into a dict
widget_patch_dto_dict = widget_patch_dto_instance.to_dict()
# create an instance of WidgetPatchDto from a dict
widget_patch_dto_from_dict = WidgetPatchDto.from_dict(widget_patch_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


