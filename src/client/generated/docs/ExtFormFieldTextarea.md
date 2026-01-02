# ExtFormFieldTextarea


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**default_value** | **str** |  | [optional] 
**description** | **str** |  | [optional] 
**label_name** | **str** |  | [optional] 

## Example

```python
from src.client.generated.models.ext_form_field_textarea import ExtFormFieldTextarea

# TODO update the JSON string below
json = "{}"
# create an instance of ExtFormFieldTextarea from a JSON string
ext_form_field_textarea_instance = ExtFormFieldTextarea.from_json(json)
# print the JSON string representation of the object
print(ExtFormFieldTextarea.to_json())

# convert the object into a dict
ext_form_field_textarea_dict = ext_form_field_textarea_instance.to_dict()
# create an instance of ExtFormFieldTextarea from a dict
ext_form_field_textarea_from_dict = ExtFormFieldTextarea.from_dict(ext_form_field_textarea_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


