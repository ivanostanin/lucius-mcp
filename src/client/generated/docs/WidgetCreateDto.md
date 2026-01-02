# WidgetCreateDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**dashboard_id** | **int** |  | 
**grid_pos** | [**GridPosDto**](GridPosDto.md) |  | [optional] 
**name** | **str** |  | 
**options** | [**WidgetCreateDtoOptions**](WidgetCreateDtoOptions.md) |  | [optional] 
**type** | [**WidgetTypeDto**](WidgetTypeDto.md) |  | 

## Example

```python
from src.client.generated.models.widget_create_dto import WidgetCreateDto

# TODO update the JSON string below
json = "{}"
# create an instance of WidgetCreateDto from a JSON string
widget_create_dto_instance = WidgetCreateDto.from_json(json)
# print the JSON string representation of the object
print(WidgetCreateDto.to_json())

# convert the object into a dict
widget_create_dto_dict = widget_create_dto_instance.to_dict()
# create an instance of WidgetCreateDto from a dict
widget_create_dto_from_dict = WidgetCreateDto.from_dict(widget_create_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


