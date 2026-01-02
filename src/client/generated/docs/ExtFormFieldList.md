# ExtFormFieldList


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**description** | **str** |  | [optional] 
**label_name** | **str** |  | [optional] 

## Example

```python
from src.client.generated.models.ext_form_field_list import ExtFormFieldList

# TODO update the JSON string below
json = "{}"
# create an instance of ExtFormFieldList from a JSON string
ext_form_field_list_instance = ExtFormFieldList.from_json(json)
# print the JSON string representation of the object
print(ExtFormFieldList.to_json())

# convert the object into a dict
ext_form_field_list_dict = ext_form_field_list_instance.to_dict()
# create an instance of ExtFormFieldList from a dict
ext_form_field_list_from_dict = ExtFormFieldList.from_dict(ext_form_field_list_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


