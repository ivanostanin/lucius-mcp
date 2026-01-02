# LaunchPdfOptions


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**country** | **str** |  | [optional] 
**date_format** | **str** |  | [optional] 
**lang** | **str** |  | [optional] 
**launch_id** | **int** |  | 
**name** | **str** |  | [optional] 
**render_images** | **bool** |  | [optional] 
**render_text** | **bool** |  | [optional] 
**skip_scenario** | **bool** |  | [optional] 
**structure** | [**List[LaunchPdfPart]**](LaunchPdfPart.md) |  | [optional] 
**time_zone** | **str** |  | [optional] 

## Example

```python
from src.client.generated.models.launch_pdf_options import LaunchPdfOptions

# TODO update the JSON string below
json = "{}"
# create an instance of LaunchPdfOptions from a JSON string
launch_pdf_options_instance = LaunchPdfOptions.from_json(json)
# print the JSON string representation of the object
print(LaunchPdfOptions.to_json())

# convert the object into a dict
launch_pdf_options_dict = launch_pdf_options_instance.to_dict()
# create an instance of LaunchPdfOptions from a dict
launch_pdf_options_from_dict = LaunchPdfOptions.from_dict(launch_pdf_options_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


