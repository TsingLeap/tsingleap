### `send_verification_code/`

  `POST`请求，向邮箱发送验证码。传入格式为

   ```json
   {
     "email": "your_email"
   }
   ```

   请求参数：

   | 参数 | 类型 | 说明 |
   | --- | --- | --- |
   | email | string | 邮箱 |

   响应状态：

   | 状态码 | 说明 |
   | --- | --- |
   | 0 | 成功 |
   | 1011 | 不是清华邮箱 |
   | 1012 | 邮箱已存在 |
   | 1013 | 1分钟内已发送验证码 |

---

### `register/`

 `POST`请求，注册。传入格式为

   ```json
   {
     "username": "your_username",
     "email": "your_email",
     "password1": "pass_word_1", 
     "password2": "pass_word_2",
     "verification_code": "your_verification_code_from_mail"
   }
   ```

   其中`password1`与`password2`为输入的密码以及再次输入的密码，用于检测两次密码是否相同。

   请求参数：

   | 参数 | 类型 | 说明 |
   | --- | --- | --- |
   | username | string | 用户名 |
   | email | string | 邮箱 |
   | password1 | string | 密码 |
   | password2 | string | 重复密码 |
   | verification_code | string | 验证码 |

   响应状态：

   | 状态码 | 说明 |
   | --- | --- |
   | 0 | 成功 |
   | 1001 | 密码太长 |
   | 1002 | 密码不一致 |
   | 1003 | 用户名已存在 |
   | 1004 | 邮箱已存在 |
   | 1005 | 未使用清华邮箱 |
   | 1006 | 未验证邮箱 |
   | 1007 | 验证码错误 |
   | 1008 | 验证码过期 |

   响应数据：

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| id | int | 用户ID |
| username | string | 用户名 |
| email | string | 邮箱 |

---

### `login/`

  `POST`请求，登录。传入格式为

   ```json
   {
       "username": "your_username",
       "password": "your_password"
   }
   ```

   请求参数：

   | 参数 | 类型 | 说明 |
   | --- | --- | --- |
   | username | string | 用户名 |
   | password | string | 密码 |

   响应状态：

   | 状态码 | 说明 |
   | --- | --- |
   | 0 | 成功 |
   | 1009 | 用户不存在 |
   | 1010 | 密码错误 |

   响应数据：

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| id | int | 用户ID |
| username | string | 用户名 |
| email | string | 邮箱 |

---

### `get_csrf_token/`

  `GET`请求，获得`csrftoken`。无需传入。此后每次`POST`时在`headers`中添加

   ```json
   {
     "Content-Type": "application/json",
     "X-CSRFToken": csrftoken,
   }
   ```

   响应状态：

   | 状态码 | 说明 |
   | --- | --- |
   | 0 | 成功 |

   响应数据：

   | 字段 | 类型 | 说明 |
   | --- | --- | --- |
   | csrfToken | string | CSRF Token |

