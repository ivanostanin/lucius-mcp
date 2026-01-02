# ExtFormFieldText


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**default_value** | **str** |  | [optional] 
**description** | **str** |  | [optional] 
**label_name** | **str** |  | [optional] 
**with_confirmation** | **bool** |  | [optional] 

## Example

```python
from src.client.generated.models.ext_form_field_text import ExtFormFieldText

# TODO update the JSON string below
json = "{}"
# create an instance of ExtFormFieldText from a JSON string
ext_form_field_text_instance = ExtFormFieldText.from_json(json)
# print the JSON string representation of the object
print(ExtFormFieldText.to_json())

# convert the object into a dict
ext_form_field_text_dict = ext_form_field_text_instance.to_dict()
# create an instance of ExtFormFieldText from a dict
ext_form_field_text_from_dict = ExtFormFieldText.from_dict(ext_form_field_text_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


