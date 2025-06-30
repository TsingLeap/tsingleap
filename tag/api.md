### `tag/create_tag/`

`POST` 请求，创建一个新标签。传入格式为

```json
{
  "username": "your_username",
  "name": "your_tag_name",
  "tag_type": "your_tag_type",
  "is_post_tag": true,
  "is_competition_tag": true
}
```

请求参数：

| 参数 | 类型 | 说明 |
| --- | --- | --- |
| username | string | 用户名 |
| name | string | 标签名 |
| tag_type | string | 标签类型, 见 [docs/tag_type名称文档](../docs/tag_type名称文档.md) |
| is_post_tag | bool | 是否为帖子标签 |
| is_competition_tag | bool | 是否为赛事标签 |

响应状态：

| 状态码 | 说明 |
| --- | --- |
| 0 | 创建成功 |
| 1020 | 没有权限 |
| 1040 | 标签类型名称错误 |
| 1041 | 标签已存在 (name 和 tag_type 相同) |

### `tag/delete_tag/`

`POST` 请求，删除一个标签。传入格式为

```json
{
  "username": "your_username",
  "tag_id": 1
}
```

请求参数：

| 参数 | 类型 | 说明 |
| --- | --- | --- |
| username | string | 用户名 |
| tag_id | int | 标签ID |

响应状态：

| 状态码 | 说明 |
| --- | --- |
| 0 | 删除成功 |
| 1020 | 没有权限 |
| 1021 | 用户不存在 |
| 1042 | 标签不存在 |

### `tag/get_tag_list/`

`GET` 请求，获取标签列表。

响应状态：

| 状态码 | 说明 |
| --- | --- |
| 0 | 获取成功 |

响应数据 (`data` 字段)：

一个 `list`，每个元素是一个 `dict`，包含以下字段：

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| id | int | 标签ID |
| name | string | 标签名 |
| tag_type | string | 标签类型 |
| is_post_tag | bool | 是否为帖子标签 |
| is_competition_tag | bool | 是否为赛事标签 |

即：

```python
{
  "code": 0,
  "msg": "Tag list fetched successfully",
  "data": {
      {
          "id": tag.id,
          "name": tag.name,
          "tag_type": tag.tag_type,
          "is_post_tag": tag.is_post_tag,
          "is_competition_tag": tag.is_competition_tag
      }
      for tag in tags
  }
}
```

### `tag/search_tag_by_prefix/`

`GET` 请求，搜索标签。传入格式为

```json
{
  "prefix": "your_prefix",
  "tag_type": "your_tag_type"
}
```

请求参数：

| 参数 | 类型 | 说明 |
| --- | --- | --- |
| prefix | string | 前缀 |
| tag_type | string | 标签类型，见 [docs/tag_type名称文档](../docs/tag_type名称文档.md)，如果不在其中，就搜索所有标签 |

响应状态：

| 状态码 | 说明 |
| --- | --- |
| 0 | 搜索成功 |

### `tag/get_post_list_by_tag/`

`GET` 请求，获取标签对应的帖子列表。传入格式为

```json
{
  "tag_id": 1,
  "page": 1,
  "page_size": 10
}
```

请求参数：

| 参数 | 类型 | 说明 |
| --- | --- | --- |
| tag_id | int | 标签ID |
| page | int | 页码 |
| page_size | int | 每页数量 |

响应状态：

| 状态码 | 说明 |
| --- | --- |
| 0 | 获取成功 |
| 1042 | 标签不存在 |
| 1023 | 页码超出范围 |

响应数据 (`data` 字段)：

```python
"data": {
  "posts": [
      {
          "id": post.post_id,
          "title": post.title,
          "content": post.content,
          "author": post.author.username,
          "created_at": post.created_at,
      }
      for post in page_obj
  ],
  "total_pages": paginator.num_pages,
  "total_posts": paginator.count
}
```