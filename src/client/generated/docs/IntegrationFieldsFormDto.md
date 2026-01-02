# IntegrationFieldsFormDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**default_project_fields** | [**List[IntegrationFieldsFormDtoDefaultProjectFieldsInner]**](IntegrationFieldsFormDtoDefaultProjectFieldsInner.md) |  | [optional] 
**default_project_fields_values** | **Dict[str, object]** |  | [optional] 
**default_secret_fields** | [**List[IntegrationFieldsFormDtoDefaultProjectFieldsInner]**](IntegrationFieldsFormDtoDefaultProjectFieldsInner.md) |  | [optional] 
**default_secret_specified** | **bool** |  | [optional] 
**global_fields** | [**List[IntegrationFieldsFormDtoDefaultProjectFieldsInner]**](IntegrationFieldsFormDtoDefaultProjectFieldsInner.md) |  | [optional] 
**global_fields_values** | **Dict[str, object]** |  | [optional] 

## Example

```python
from src.client.generated.models.integration_fields_form_dto import IntegrationFieldsFormDto

# TODO update the JSON string below
json = "{}"
# create an instance of IntegrationFieldsFormDto from a JSON string
integration_fields_form_dto_instance = IntegrationFieldsFormDto.from_json(json)
# print the JSON string representation of the object
print(IntegrationFieldsFormDto.to_json())

# convert the object into a dict
integration_fields_form_dto_dict = integration_fields_form_dto_instance.to_dict()
# create an instance of IntegrationFieldsFormDto from a dict
integration_fields_form_dto_from_dict = IntegrationFieldsFormDto.from_dict(integration_fields_form_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


