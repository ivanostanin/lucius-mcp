# TemplateOverviewDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**created_date** | **int** |  | [optional] 
**id** | **int** |  | [optional] 
**last_modified_date** | **int** |  | [optional] 
**name** | **str** |  | [optional] 
**widgets** | [**List[WidgetDto]**](WidgetDto.md) |  | [optional] 

## Example

```python
from src.client.generated.models.template_overview_dto import TemplateOverviewDto

# TODO update the JSON string below
json = "{}"
# create an instance of TemplateOverviewDto from a JSON string
template_overview_dto_instance = TemplateOverviewDto.from_json(json)
# print the JSON string representation of the object
print(TemplateOverviewDto.to_json())

# convert the object into a dict
template_overview_dto_dict = template_overview_dto_instance.to_dict()
# create an instance of TemplateOverviewDto from a dict
template_overview_dto_from_dict = TemplateOverviewDto.from_dict(template_overview_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


