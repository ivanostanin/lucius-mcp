# PageLaunchDiffRow


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**content** | [**List[LaunchDiffRow]**](LaunchDiffRow.md) |  | [optional] 
**empty** | **bool** |  | [optional] 
**first** | **bool** |  | [optional] 
**last** | **bool** |  | [optional] 
**number** | **int** |  | [optional] 
**number_of_elements** | **int** |  | [optional] 
**pageable** | [**Pageable**](Pageable.md) |  | [optional] 
**size** | **int** |  | [optional] 
**sort** | [**PageAccessGroupDtoSort**](PageAccessGroupDtoSort.md) |  | [optional] 
**total_elements** | **int** |  | [optional] 
**total_pages** | **int** |  | [optional] 

## Example

```python
from src.client.generated.models.page_launch_diff_row import PageLaunchDiffRow

# TODO update the JSON string below
json = "{}"
# create an instance of PageLaunchDiffRow from a JSON string
page_launch_diff_row_instance = PageLaunchDiffRow.from_json(json)
# print the JSON string representation of the object
print(PageLaunchDiffRow.to_json())

# convert the object into a dict
page_launch_diff_row_dict = page_launch_diff_row_instance.to_dict()
# create an instance of PageLaunchDiffRow from a dict
page_launch_diff_row_from_dict = PageLaunchDiffRow.from_dict(page_launch_diff_row_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


