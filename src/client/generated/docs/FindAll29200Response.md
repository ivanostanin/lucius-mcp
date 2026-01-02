# FindAll29200Response


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**content** | [**List[LaunchDto]**](LaunchDto.md) |  | [optional] 
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
from src.client.generated.models.find_all29200_response import FindAll29200Response

# TODO update the JSON string below
json = "{}"
# create an instance of FindAll29200Response from a JSON string
find_all29200_response_instance = FindAll29200Response.from_json(json)
# print the JSON string representation of the object
print(FindAll29200Response.to_json())

# convert the object into a dict
find_all29200_response_dict = find_all29200_response_instance.to_dict()
# create an instance of FindAll29200Response from a dict
find_all29200_response_from_dict = FindAll29200Response.from_dict(find_all29200_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


