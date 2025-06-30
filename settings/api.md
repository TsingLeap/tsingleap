### `settings/change_password/`

  `POST`请求，修改密码，传入格式为

   ```json
   {
     "username": "your_user_name",
     "password": "your_password",
     "new_password": "your_new_password",
   }
   ```

   请求参数：

   | 参数         | 类型   | 说明   |
   | ------------ | ------ | ------ |
   | username     | string | 用户名 |
   | password     | string | 密码   |
   | new_password | string | 新密码 |

   响应状态：

   | 状态码 | 说明         |
   | ------ | ------------ |
   | 0      | 成功         |
   | 1014   | 密码不正确   |
   | 1021   | 用户名不存在 |
   | 1016   | 新密码过长   |

---

### `settings/change_nickname/`

  `POST`请求，修改昵称，传入格式为

   ```json
   {
     "username": "your_user_name",
     "nickname": "your_nickname",
   }
   ```

   请求参数：

   | 参数 | 类型 | 说明 |
   | --- | --- | --- |
   | username | string | 用户名 |
   | nickname | string | 昵称 |

   响应状态：

   | 状态码 | 说明 |
   | --- | --- |
   | 0 | 成功 |
   | 1021 | 用户名不存在 |

### `settings/get_user_info/`

  `GET`请求，获取用户信息，传入格式为

   ```json
   {
     "username": "your_user_name",
   }
   ```

   请求参数：

   | 参数 | 类型 | 说明 |
   | --- | --- | --- |
   | username | string | 用户名 |

   响应数据 (`data` 字段)：

   | 字段 | 类型 | 说明 |
   | --- | --- | --- |
   | nickname | string | 昵称 |
   | username | string | 用户名 |
   | email | string | 邮箱 |

   响应状态：

   | 状态码 | 说明 |
   | --- | --- |
   | 0 | 成功 |
   | 1021 | 用户名不存在 |
   
### `settings/user_add_permission/`

  `POST`请求，添加权限，传入格式为

   ```json
   {
     "operator": "the_operator_username",
     "username": "your_user_name",
     "permission_name": "your_permission_name",
     "permission_info": "your_permission_info",
   }
   ```

   请求参数：

   | 参数 | 类型 | 说明 |
   | --- | --- | --- |
   | operator | string | 操作员用户名 |
   | username | string | 用户名 |
   | permission_name | string | 权限名 |
   | permission_info | string | 权限信息（比如修改比赛权限中的比赛 id） |

   响应状态：

   | 状态码 | 说明 |
   | --- | --- |
   | 0 | 成功 |
   | 1021 | 用户名不存在 |
   | 1019 | 没有权限 |

### `settings/user_remove_permission/`

  `POST`请求，删除权限，传入格式为

   ```json
   {
     "operator": "the_operator_username",
     "username": "your_user_name",
     "permission_name": "your_permission_name",
     "permission_info": "your_permission_info",
   }
   ```

   请求参数：

   | 参数 | 类型 | 说明 |
   | --- | --- | --- |
   | operator | string | 操作员用户名 |
   | username | string | 用户名 |
   | permission_name | string | 权限名 |
   | permission_info | string | 权限信息（比如修改比赛权限中的比赛 id） |

   响应状态：

   | 状态码 | 说明 |
   | --- | --- |
   | 0 | 成功 |
   | 1021 | 用户名不存在 |
   | 1020 | 没有权限 |
   | 1021 | 权限不存在 |

###  `settings/get_user_permission_info/`

  `GET`请求，获取用户权限信息，传入格式为

   ```json
   {
     "username": "your_user_name",
   }
   ```

   请求参数：

   | 参数 | 类型 | 说明 |
   | --- | --- | --- |
   | username | string | 用户名 |

   响应数据 (`data` 字段)：

   一个 `list`，每个元素是一个 `dict`，包含以下字段：

   | 字段 | 类型 | 说明 |
   | --- | --- | --- |
   | username | string | 用户名 |
   | permission_name | string | 权限名 |
   | permission_info | string | 权限信息（比如修改比赛权限中的比赛 id） |

   响应状态：

   | 状态码 | 说明 |
   | --- | --- |
   | 0 | 成功 |
   | 1021 | 用户名不存在 |

###  `settings/search_username_settings/`

  `GET`请求，搜索用户，进行前缀匹配，传入格式为

  ```json
  {
    "username_prefix": "username_prefix"
  }
  ```

  请求参数：

| 参数            | 类型   | 说明       |
| --------------- | ------ | ---------- |
| username_prefix | string | 用户名前缀 |

  响应数据(`data`字段)：

  `users`键对应一个`list`，表示以`username_prefix`开头的用户（不超过10个），`list`每个元素是一个`dict`，包含以下字段：

  | 字段     | 类型   | 说明   |
  | -------- | ------ | ------ |
  | username | string | 用户名 |
  | nickname | string | 昵称   |

  响应状态：

| 状态码 | 说明                                |
| ------ | ----------------------------------- |
| 0      | 成功                                |
| 1019   | 以username_prefix开头的用户名不存在 |

