# IntegrationFieldsFormDtoDefaultProjectFieldsInner


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**depends_on_fields** | **List[str]** |  | [optional] 
**deprecated** | **bool** |  | [optional] 
**name** | **str** |  | [optional] 
**required** | **bool** |  | [optional] 
**type** | **str** |  | 
**default_value** | **str** |  | [optional] 
**label_name** | **str** |  | [optional] 
**description** | **str** |  | [optional] 
**classifier** | **str** |  | [optional] 
**options** | [**List[ExtFormFieldOption]**](ExtFormFieldOption.md) |  | [optional] 
**multi** | **bool** |  | [optional] 
**max** | **float** |  | [optional] 
**min** | **float** |  | [optional] 
**step** | **float** |  | [optional] 
**with_confirmation** | **bool** |  | [optional] 

## Example

```python
from src.client.generated.models.integration_fields_form_dto_default_project_fields_inner import IntegrationFieldsFormDtoDefaultProjectFieldsInner

# TODO update the JSON string below
json = "{}"
# create an instance of IntegrationFieldsFormDtoDefaultProjectFieldsInner from a JSON string
integration_fields_form_dto_default_project_fields_inner_instance = IntegrationFieldsFormDtoDefaultProjectFieldsInner.from_json(json)
# print the JSON string representation of the object
print(IntegrationFieldsFormDtoDefaultProjectFieldsInner.to_json())

# convert the object into a dict
integration_fields_form_dto_default_project_fields_inner_dict = integration_fields_form_dto_default_project_fields_inner_instance.to_dict()
# create an instance of IntegrationFieldsFormDtoDefaultProjectFieldsInner from a dict
integration_fields_form_dto_default_project_fields_inner_from_dict = IntegrationFieldsFormDtoDefaultProjectFieldsInner.from_dict(integration_fields_form_dto_default_project_fields_inner_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


