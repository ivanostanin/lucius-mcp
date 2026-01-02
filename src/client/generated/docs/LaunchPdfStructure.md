# LaunchPdfStructure


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**structure** | [**List[LaunchPdfPart]**](LaunchPdfPart.md) |  | [optional] 

## Example

```python
from src.client.generated.models.launch_pdf_structure import LaunchPdfStructure

# TODO update the JSON string below
json = "{}"
# create an instance of LaunchPdfStructure from a JSON string
launch_pdf_structure_instance = LaunchPdfStructure.from_json(json)
# print the JSON string representation of the object
print(LaunchPdfStructure.to_json())

# convert the object into a dict
launch_pdf_structure_dict = launch_pdf_structure_instance.to_dict()
# create an instance of LaunchPdfStructure from a dict
launch_pdf_structure_from_dict = LaunchPdfStructure.from_dict(launch_pdf_structure_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


