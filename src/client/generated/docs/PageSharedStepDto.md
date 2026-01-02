# PageSharedStepDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**content** | [**List[SharedStepDto]**](SharedStepDto.md) |  | [optional] 
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
from src.client.generated.models.page_shared_step_dto import PageSharedStepDto

# TODO update the JSON string below
json = "{}"
# create an instance of PageSharedStepDto from a JSON string
page_shared_step_dto_instance = PageSharedStepDto.from_json(json)
# print the JSON string representation of the object
print(PageSharedStepDto.to_json())

# convert the object into a dict
page_shared_step_dto_dict = page_shared_step_dto_instance.to_dict()
# create an instance of PageSharedStepDto from a dict
page_shared_step_dto_from_dict = PageSharedStepDto.from_dict(page_shared_step_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


