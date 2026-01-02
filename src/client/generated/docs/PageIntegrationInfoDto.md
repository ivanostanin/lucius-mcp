# PageIntegrationInfoDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**content** | [**List[IntegrationInfoDto]**](IntegrationInfoDto.md) |  | [optional] 
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
from src.client.generated.models.page_integration_info_dto import PageIntegrationInfoDto

# TODO update the JSON string below
json = "{}"
# create an instance of PageIntegrationInfoDto from a JSON string
page_integration_info_dto_instance = PageIntegrationInfoDto.from_json(json)
# print the JSON string representation of the object
print(PageIntegrationInfoDto.to_json())

# convert the object into a dict
page_integration_info_dto_dict = page_integration_info_dto_instance.to_dict()
# create an instance of PageIntegrationInfoDto from a dict
page_integration_info_dto_from_dict = PageIntegrationInfoDto.from_dict(page_integration_info_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


