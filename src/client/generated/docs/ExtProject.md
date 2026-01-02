# ExtProject


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** |  | [optional] 
**key** | **str** |  | [optional] 
**name** | **str** |  | [optional] 

## Example

```python
from src.client.generated.models.ext_project import ExtProject

# TODO update the JSON string below
json = "{}"
# create an instance of ExtProject from a JSON string
ext_project_instance = ExtProject.from_json(json)
# print the JSON string representation of the object
print(ExtProject.to_json())

# convert the object into a dict
ext_project_dict = ext_project_instance.to_dict()
# create an instance of ExtProject from a dict
ext_project_from_dict = ExtProject.from_dict(ext_project_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


