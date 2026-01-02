# WidgetDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**created_by** | **str** |  | [optional] 
**created_date** | **int** |  | [optional] 
**dashboard_id** | **int** |  | [optional] 
**grid_pos** | [**GridPosDto**](GridPosDto.md) |  | [optional] 
**id** | **int** |  | [optional] 
**last_modified_by** | **str** |  | [optional] 
**last_modified_date** | **int** |  | [optional] 
**name** | **str** |  | [optional] 
**options** | [**WidgetCreateDtoOptions**](WidgetCreateDtoOptions.md) |  | [optional] 
**type** | [**WidgetTypeDto**](WidgetTypeDto.md) |  | [optional] 

## Example

```python
from src.client.generated.models.widget_dto import WidgetDto

# TODO update the JSON string below
json = "{}"
# create an instance of WidgetDto from a JSON string
widget_dto_instance = WidgetDto.from_json(json)
# print the JSON string representation of the object
print(WidgetDto.to_json())

# convert the object into a dict
widget_dto_dict = widget_dto_instance.to_dict()
# create an instance of WidgetDto from a dict
widget_dto_from_dict = WidgetDto.from_dict(widget_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


