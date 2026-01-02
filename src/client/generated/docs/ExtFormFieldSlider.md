# ExtFormFieldSlider


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**default_value** | **float** |  | [optional] 
**description** | **str** |  | [optional] 
**label_name** | **str** |  | [optional] 
**max** | **float** |  | [optional] 
**min** | **float** |  | [optional] 
**step** | **float** |  | [optional] 

## Example

```python
from src.client.generated.models.ext_form_field_slider import ExtFormFieldSlider

# TODO update the JSON string below
json = "{}"
# create an instance of ExtFormFieldSlider from a JSON string
ext_form_field_slider_instance = ExtFormFieldSlider.from_json(json)
# print the JSON string representation of the object
print(ExtFormFieldSlider.to_json())

# convert the object into a dict
ext_form_field_slider_dict = ext_form_field_slider_instance.to_dict()
# create an instance of ExtFormFieldSlider from a dict
ext_form_field_slider_from_dict = ExtFormFieldSlider.from_dict(ext_form_field_slider_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


