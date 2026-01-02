# ExtFormFieldSelect


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**default_value** | **str** |  | [optional] 
**description** | **str** |  | [optional] 
**label_name** | **str** |  | [optional] 
**multi** | **bool** |  | [optional] 
**options** | [**List[ExtFormFieldOption]**](ExtFormFieldOption.md) |  | [optional] 

## Example

```python
from src.client.generated.models.ext_form_field_select import ExtFormFieldSelect

# TODO update the JSON string below
json = "{}"
# create an instance of ExtFormFieldSelect from a JSON string
ext_form_field_select_instance = ExtFormFieldSelect.from_json(json)
# print the JSON string representation of the object
print(ExtFormFieldSelect.to_json())

# convert the object into a dict
ext_form_field_select_dict = ext_form_field_select_instance.to_dict()
# create an instance of ExtFormFieldSelect from a dict
ext_form_field_select_from_dict = ExtFormFieldSelect.from_dict(ext_form_field_select_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


