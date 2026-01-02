# ExtFormFieldFormChoice


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**classifier** | **str** |  | [optional] 
**description** | **str** |  | [optional] 
**label_name** | **str** |  | [optional] 
**options** | [**List[ExtFormFieldFormChoiceOption]**](ExtFormFieldFormChoiceOption.md) |  | [optional] 

## Example

```python
from src.client.generated.models.ext_form_field_form_choice import ExtFormFieldFormChoice

# TODO update the JSON string below
json = "{}"
# create an instance of ExtFormFieldFormChoice from a JSON string
ext_form_field_form_choice_instance = ExtFormFieldFormChoice.from_json(json)
# print the JSON string representation of the object
print(ExtFormFieldFormChoice.to_json())

# convert the object into a dict
ext_form_field_form_choice_dict = ext_form_field_form_choice_instance.to_dict()
# create an instance of ExtFormFieldFormChoice from a dict
ext_form_field_form_choice_from_dict = ExtFormFieldFormChoice.from_dict(ext_form_field_form_choice_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


