### `forum/create_post/`

`POST` 请求，创建一条新帖子。传入格式为

```json
{
  "username": "your_username",
  "title": "your_title",
  "content": "your_content"
}
```

请求参数：

| 参数 | 类型 | 说明 |
| --- | --- | --- |
| username | string | 用户名 |
| title | string | 帖子标题 |
| content | string | 帖子内容 |

响应状态：

| 状态码 | 说明 |
| --- | --- |
| 0 | 创建成功 |
| 1020 | 没有权限 |
| 1021 | 用户不存在 |
| 1022 | 帖子标题过长 |

### `forum/posts/`

`GET` 请求，获取帖子列表。参数为：

| 参数 | 类型 | 说明 |
| --- | --- | --- |
| tag_list | list | 标签列表 |
| keyword | string | 关键词 |
| page | int | 页码 |
| page_size | int | 每页帖子数 |

响应状态：

| 状态码 | 说明 |
| --- | --- |
| 0 | 获取成功 |
| 1023 | 页码超出范围 |

响应数据 (`data` 字段)：

```json
{
  "posts": [
    {
      "post_id": 1,
      "title": "your_title",
      "content": "your_content",
      "created_at": "2025-04-20T10:00:00Z",
      "author": "your_username"
    }
  ],
  "total_pages": 1,
  "total_posts": 1
}
```

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| posts | list | 帖子列表 |
| total_pages | int | 总页数 |
| total_posts | int | 总帖子数 |

其中 `posts` 是一个列表，每个元素是一个帖子，包含以下字段：

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| post_id | int | 帖子ID |
| title | string | 帖子标题 |
| content | string | 帖子内容 |
| created_at | string | 创建时间 |
| author | string | 作者 |

### `forum/delete_post/`

`POST` 请求，删除指定帖子。传入格式为

```json
{
  "username": "your_username",
  "post_id": 1
}
```

请求参数：

| 参数 | 类型 | 说明 |
| --- | --- | --- |
| username | string | 用户名 |
| post_id | int | 帖子ID |

响应状态：

| 状态码 | 说明 |
| --- | --- |
| 0 | 删除成功 |
| 1021 | 用户不存在 |
| 1024 | 帖子不存在 |
| 1020 | 没有权限 |



### `forum/post_detail/`

`GET` 请求，获取单个帖子详情。

请求参数：

| 参数 | 类型 | 说明 |
| --- | --- | --- |
| post_id | int | 帖子ID |

响应状态：

| 状态码 | 说明 |
| --- | --- |
| 0 | 获取成功 |
| 1024 | 帖子不存在 |

响应数据 (`data` 字段)：

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| post_id | int | 帖子ID |
| title | string | 帖子标题 |
| content | string | 帖子内容 |
| created_at | string | 创建时间 |
| author | string | 作者 |

### `forum/create_comment/`

`POST` 请求，创建一条新评论。传入格式为

```json
{
  "username": "your_username",
  "post_id": 1,
  "content": "your_content"
}
```

请求参数：

| 参数 | 类型 | 说明 |
| --- | --- | --- |
| username | string | 用户名 |
| post_id | int | 帖子ID |
| content | string | 评论内容 |

响应状态：

| 状态码 | 说明 |
| --- | --- |
| 0 | 创建成功 |
| 1020 | 没有权限 |
| 1021 | 用户不存在 |
| 1026 | 帖子不存在 |

### `forum/comments/`

`GET` 请求，获取指定帖子的评论列表。传入格式为

请求参数：

| 参数 | 类型 | 说明 |
| --- | --- | --- |
| post_id | int | 帖子ID |
| page | int | 页码 |
| page_size | int | 每页评论数 |

响应状态：

| 状态码 | 说明 |
| --- | --- |
| 0 | 获取成功 |
| 1027 | 帖子不存在 |
| 1023 | 页码超出范围 |

响应数据 (`data` 字段)：

```json
{
  "comments": [
    {
      "comment_id": 1,
      "content": "your_content",
      "created_at": "2025-04-20T10:00:00Z",
      "author": "your_username"
    }
  ],
  "total_pages": 1,
  "total_comments": 1
}
```

其中 `comments` 是一个列表，每个元素是一个评论，包含以下字段：

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| comment_id | int | 评论ID |
| content | string | 评论内容 |
| created_at | string | 创建时间 |
| author | string | 作者 |

### `forum/create_comment_of_object/`

`POST` 请求，创建一条新评论。传入格式为

```json
{
  "username": "your_username",
  "content_type": "Post",
  "object_id": 1,
  "content": "your_content",
  "allow_reply": true
}
```

请求参数：

| 参数 | 类型 | 说明 |
| --- | --- | --- |
| username | string | 用户名 |
| content_type | string | 评论类型 (Post / Comment / Competition) |
| object_id | int | 评论对象ID |
| content | string | 评论内容 |
| allow_reply | bool | 是否允许回复 |

响应状态：

| 状态码 | 说明 |
| --- | --- |
| 0 | 创建成功 |
| 1020 | 没有权限 |
| 1021 | 用户不存在 |
| 1031 | 内容类型错误 |
| 1032 | 对象不存在 |
| 1033 | 对象不允许回复 |

### `forum/comments_of_object/`

`GET` 请求，获取指定对象的评论列表。传入格式为

请求参数：

| 参数 | 类型 | 说明 |
| --- | --- | --- |
| content_type | string | 评论类型 (Post / Comment / Competition) |
| object_id | int | 评论对象ID |
| page | int | 页码 |
| page_size | int | 每页评论数 |

响应状态：

| 状态码 | 说明 |
| --- | --- |
| 0 | 获取成功 |
| 1031 | 内容类型错误 |
| 1032 | 对象不存在 |
| 1023 | 页码超出范围 |

响应数据 (`data` 字段)：

```json
{
  "comments": [
    {
      "comment_id": 1,
      "content": "your_content",
      "created_at": "2025-04-20T10:00:00Z",
      "author": "your_username"
    }
  ],
  "total_pages": 1,
  "total_comments": 1
}
```

### `forum/create_post_with_tag/`

`POST` 请求，创建一条新帖子。传入格式为

```json
{
  "username": "your_username",
  "title": "your_title",
  "content": "your_content",
  "tag_ids": [1, 2, 3, 4, 5]
}
```

请求参数：

| 参数 | 类型 | 说明 |
| --- | --- | --- |
| username | string | 用户名 |
| title | string | 帖子标题 |
| content | string | 帖子内容 |
| tag_ids | list | 标签ID列表, 至多5个 |

响应状态：

| 状态码 | 说明 |
| --- | --- |
| 0 | 创建成功 |
| 1020 | 没有权限 |
| 1021 | 用户不存在 |
| 1022 | 标题过长 |
| 1045 | 标签数量超过限制 |
| 1046 | 标签ID错误 |
| 1047 | 标签不是帖子标签 |

### `forum/get_tag_list_by_post_id/`

`GET` 请求，获取指定帖子的标签列表。传入格式为

```json
{
  "post_id": 1
}
```

请求参数：

| 参数 | 类型 | 说明 |
| --- | --- | --- |
| post_id | int | 帖子ID |

响应状态：

| 状态码 | 说明 |
| --- | --- |
| 0 | 获取成功 |
| 1024 | 帖子不存在 |

响应数据 (`data` 字段)：

一个 `list`，每个元素是一个 `dict`，包含以下字段：

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| tag_id | int | 标签ID |
| tag_name | string | 标签名 |
| tag_type | string | 标签类型 |
| is_post_tag | bool | 是否为帖子标签 |
| is_competition_tag | bool | 是否为赛事标签 |


### `forum/add_tag_to_post/`

`POST` 请求，添加标签到帖子。传入格式为

```json
{
  "username": "your_username",
  "post_id": 1,
  "tag_ids": [1, 2, 3, 4, 5]
}
```

请求参数：

| 参数 | 类型 | 说明 |
| --- | --- | --- |
| username | string | 用户名 |
| post_id | int | 帖子ID |
| tag_ids | list | 标签ID列表, 至多5个 |

响应状态：

| 状态码 | 说明 |
| --- | --- |
| 0 | 添加成功 |
| 1021 | 用户不存在 |
| 1024 | 帖子不存在 |
| 1046 | 标签ID错误 |
| 1047 | 标签不是帖子标签 |
| 1020 | 没有权限 |
| 1048 | 没有权限添加精华帖标签 |
| 1045 | 标签数量超过限制 |

### `forum/remove_tag_from_post/`

`POST` 请求，移除标签从帖子。传入格式为

```json
{
  "username": "your_username",
  "post_id": 1,
  "tag_id": 1
}
```

请求参数：

| 参数 | 类型 | 说明 |
| --- | --- | --- |
| username | string | 用户名 |
| post_id | int | 帖子ID |
| tag_id | int | 标签ID |

响应状态：

| 状态码 | 说明 |
| --- | --- |
| 0 | 移除成功 |
| 1021 | 用户不存在 |
| 1024 | 帖子不存在 |
| 1046 | 标签ID错误 |
| 1050 | 标签不在帖子中 |
| 1020 | 没有权限 |

### `forum/get_reply_list_of_comment/`

`GET` 请求，获取指定评论的回复列表。传入格式为

```json
{
  "comment_id": 1
}
```

请求参数：

| 参数 | 类型 | 说明 |
| --- | --- | --- |
| comment_id | int | 评论ID |

响应状态：

| 状态码 | 说明 |
| --- | --- |
| 0 | 获取成功 |
| 1035 | 评论不存在 |

响应数据 (`data` 字段)：

```python
[
  {
      "comment_id": comment.comment_id,
      "content": comment.content,
      "created_at": comment.created_at,
      "author": comment.author.username,
      "father_object_id": comment.object_id
  }
  for comment in reply_list
]
```

### `forum/delete_comment/`

`POST` 请求，删除指定评论。传入格式为

```json
{
  "username": "your_username",
  "comment_id": 1
}
```

请求参数：

| 参数 | 类型 | 说明 |
| --- | --- | --- |
| username | string | 用户名 |
| comment_id | int | 评论ID |

响应状态：

| 状态码 | 说明 |
| --- | --- |
| 0 | 删除成功 |
| 1021 | 用户不存在 |
| 1035 | 评论不存在 |
| 1020 | 没有权限 |

### `forum/search_post_by_keyword/`

`GET` 请求，搜索帖子。传入格式为

```json
{
  "keyword": "your_keyword",
  "page": 1,
  "page_size": 10
}
```

请求参数：

| 参数 | 类型 | 说明 |
| --- | --- | --- |
| keyword | string | 关键词 |
| page | int | 页码 |
| page_size | int | 每页帖子数 |

响应状态：

| 状态码 | 说明 |
| --- | --- |
| 0 | 搜索成功 |
| 1023 | 页码超出范围 |

响应数据 (`data` 字段)：

```json
{
  "posts": [
    {
      "post_id": 1,
      "title": "your_title",
      "content": "your_content",
      "created_at": "2025-04-20T10:00:00Z",
      "author": "your_username"
    }
  ],
  "total_pages": 1,
  "total_posts": 1
```

### `forum/get_comment_detail_by_id/`

`GET` 请求，获取指定评论的详情。传入格式为

```json
{
  "comment_id": 1
}
```

请求参数：

| 参数 | 类型 | 说明 |
| --- | --- | --- |
| comment_id | int | 评论ID |

响应状态：

| 状态码 | 说明 |
| --- | --- |
| 0 | 获取成功 |
| 1035 | 评论不存在 |

响应数据 (`data` 字段)：

```json
{
  "comment_id": 1,
  "content": "your_content",
  "created_at": "2025-04-20T10:00:00Z",
  "author": "your_username",
  "allow_reply": true,
  "object_id": 1,
  "content_type": "Post",
}
```

### `forum/create_report/`

`POST` 请求，创建一条举报。传入格式为

```json
{
  "username": "your_username",
  "content_type": "Post",
  "object_id": 1,
  "reason": "your_reason"
}
```

请求参数：

| 参数 | 类型 | 说明 |
| --- | --- | --- |
| username | string | 用户名 |
| content_type | string | 举报类型 (Post / Comment) |
| object_id | int | 举报对象ID |
| reason | string | 举报原因 |

响应状态：

| 状态码 | 说明 |
| --- | --- |
| 0 | 创建成功 |
| 1021 | 用户不存在 |
| 1031 | 内容类型错误 |
| 1032 | 对象不存在 |

### `forum/modify_report_solved_state/`

`POST` 请求，修改举报状态。传入格式为

```json
{
  "username": "your_username",
  "report_id": 1,
  "solved_state": true
}
```

请求参数：

| 参数 | 类型 | 说明 |
| --- | --- | --- |
| username | string | 处理者用户名 |
| report_id | int | 举报ID |
| solved_state | bool | 举报的处理状态 |

响应状态：

| 状态码 | 说明 |
| --- | --- |
| 0 | 修改成功 |
| 1021 | 用户不存在 |
| 1020 | 没有权限 |
| 1036 | 举报不存在 |

### `forum/get_report_list/`

`GET` 请求，获取举报列表。传入格式为

```json
{
  "solved_state": true, // 可选，默认为 None
  "page": 1,
  "page_size": 10
}
```

请求参数：

| 参数 | 类型 | 说明 |
| --- | --- | --- |
| solved_state | bool | 举报的处理状态 |
| page | int | 页码 |
| page_size | int | 每页举报数 |

响应状态：

| 状态码 | 说明 |
| --- | --- |
| 0 | 获取成功 |
| 1023 | 页码超出范围 |

响应数据 (`data` 字段)：

```json
{
  "report_id": 1,
  "reporter": "your_username",
  "content_type": "Post",
  "object_id": 1,
  "reason": "your_reason",
  "created_at": "2025-04-20T10:00:00Z",
  "solved": true,
  "preview": {
    "author": "reported_user_username",
    "content": "reported_content"
  },
  "object_deleted": false,
  "user_banned": false
}
```

### `forum/delete_reported_object/`

`POST` 请求，删除举报对象。传入格式为

```json
{
  "username": "your_username",
  "report_id": 1
}
```

请求参数：

| 参数 | 类型 | 说明 |
| --- | --- | --- |
| username | string | 用户名 |
| report_id | int | 举报ID |

响应状态：

| 状态码 | 说明 |
| --- | --- |
| 0 | 删除成功 |
| 1021 | 用户不存在 |
| 1020 | 没有权限 |
| 1036 | 举报不存在 |
| 1032 | 对象已删除 (不存在) |

### `forum/ban_reported_user/`

`POST` 请求，封禁被举报者。传入格式为

```json
{
  "username": "your_username",
  "report_id": 1
}
```

请求参数：

| 参数 | 类型 | 说明 |
| --- | --- | --- |
| username | string | 用户名 |
| report_id | int | 举报ID |

响应状态：

| 状态码 | 说明 |
| --- | --- |
| 0 | 封禁成功 |
| 1021 | 用户不存在 |
| 1036 | 举报不存在 |
| 1020 | 没有权限 |
| 1021 | 被举报者权限不存在 |